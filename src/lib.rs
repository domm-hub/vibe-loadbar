use pyo3::prelude::*;
use crossterm::{terminal, style::{Color, Stylize, SetForegroundColor}};
use std::io::{self, Write};
use std::time::{Instant};
use std::fmt::Write as FmtWrite; 
use unicode_width::UnicodeWidthStr;

#[derive(Clone)]
enum TemplatePart {
    Literal(String),
    Action, Percent, Elapsed, Speed, Bar, Br1, Br2,
}

#[pyclass]
pub struct LoadBar {
    label: String, comp_msg: String, finish: f64,
    start_time: Instant, last_update_time: Instant,
    last_render_time: Instant, last_progress: f64,
    current_speed: f64, smoothing: f64, started: bool,
    parts: Vec<TemplatePart>, buffer: String,
    ac_clr: Color, br_clr: Color, ex_clr: Color,
    label_width: usize, n_updates: u64, miniters: u64,
    last_size_check: Instant, cached_size: (u16, u16),
}

#[pymethods]
impl LoadBar {
    #[new]
    #[pyo3(signature = (label, finish, format_str, ac_clr, br_clr, ex_clr, comp_msg="Complete", smoothing=0.3))]
    fn py_new(label: &str, finish: f64, format_str: &str, ac_clr: &str, br_clr: &str, ex_clr: &str, comp_msg: &str, smoothing: f64) -> Self {
        let now = Instant::now();
        let mut parts = Vec::new();
        let tags = [("{action}", TemplatePart::Action), ("{percent}", TemplatePart::Percent), 
                    ("{elapsed}", TemplatePart::Elapsed), ("{speed}", TemplatePart::Speed), 
                    ("{bar}", TemplatePart::Bar), ("{br1}", TemplatePart::Br1), ("{br2}", TemplatePart::Br2)];

        let mut remaining = format_str.to_string();
        while !remaining.is_empty() {
            let mut best = None;
            for (tag, part) in &tags {
                if let Some(idx) = remaining.find(tag) {
                    if best.as_ref().map_or(true, |&(b_idx, _, _)| idx < b_idx) {
                        best = Some((idx, tag.len(), part.clone()));
                    }
                }
            }
            if let Some((idx, len, part)) = best {
                if idx > 0 { parts.push(TemplatePart::Literal(remaining[..idx].to_string())); }
                parts.push(part);
                remaining = remaining[idx + len..].to_string();
            } else {
                parts.push(TemplatePart::Literal(remaining));
                break;
            }
        }

        Self {
            label: label.to_string(), comp_msg: comp_msg.to_string(), finish, start_time: now, 
            last_update_time: now, last_render_time: now, last_progress: 0.0, current_speed: 0.0, 
            smoothing, started: false, parts, buffer: String::with_capacity(512), 
            ac_clr: str_to_color(ac_clr), br_clr: str_to_color(br_clr), ex_clr: str_to_color(ex_clr),
            label_width: UnicodeWidthStr::width(label), n_updates: 0, miniters: 1, 
            last_size_check: now, cached_size: terminal::size().unwrap_or((80, 20)),
        }
    }

    fn update(&mut self, current: f64) {
        let now = Instant::now();
        if !self.started { self.start_time = now; self.started = true; }
        self.n_updates += 1;
        if self.n_updates % self.miniters != 0 && current < self.finish { return; }

        let dt = now.duration_since(self.last_update_time).as_secs_f64();
        if dt > 0.0 {
            let inst_speed = (current - self.last_progress) / dt;
            self.current_speed = if self.current_speed == 0.0 { inst_speed } 
                                 else { (self.smoothing * inst_speed) + (1.0 - self.smoothing) * self.current_speed };
        }
        self.last_update_time = now; self.last_progress = current;

        let pct = (current / self.finish).clamp(0.0, 1.0);
        let total = self.start_time.elapsed().as_secs_f64();
        let eta = if self.current_speed > 0.1 { (self.finish - current) / self.current_speed } else { 0.0 };

        self.buffer.clear();
        let _ = write!(self.buffer, "\r\x1b[K");
        let bar_w = (self.cached_size.0 as usize).saturating_sub(60).max(5);

        for part in &self.parts {
            match part {
                TemplatePart::Literal(s) => { let _ = self.buffer.write_str(s); },
                TemplatePart::Action => { let _ = write!(self.buffer, "{}", self.label.clone().with(self.ac_clr)); },
                TemplatePart::Br1 => { let _ = write!(self.buffer, "{}", "[".with(self.br_clr)); },
                TemplatePart::Br2 => { let _ = write!(self.buffer, "{}", "]".with(self.br_clr)); },
                TemplatePart::Percent => { let _ = write!(self.buffer, "{}", format!("{:>5.1}%", pct * 100.0).with(self.ex_clr)); },
                TemplatePart::Speed => { let _ = write!(self.buffer, "{}", format!("{:>8.1} it/s", self.current_speed).with(self.ex_clr)); },
                TemplatePart::Elapsed => { let _ = write!(self.buffer, "{:02}:{:02}<{:02}:{:02}", (total/60.) as u64, (total%60.) as u64, (eta/60.) as u64, (eta%60.) as u64); },
                TemplatePart::Bar => {
                    let fill = (pct * bar_w as f64) as usize;
                    let _ = write!(self.buffer, "{}", SetForegroundColor(self.br_clr));
                    for i in 0..bar_w { self.buffer.push(if i < fill { '█' } else { '░' }); }
                    let _ = write!(self.buffer, "{}", SetForegroundColor(Color::Reset));
                }
            }
        }
        let _ = io::stdout().write_all(self.buffer.as_bytes());
        let _ = io::stdout().flush();
    }
}

fn str_to_color(s: &str) -> Color {
    match s.to_lowercase().as_str() {
        "red" => Color::Red, "green" => Color::Green, "yellow" => Color::Yellow, 
        "blue" => Color::Blue, "cyan" => Color::Cyan, _ => Color::Reset,
    }
}

#[pymodule]
fn vibe_loadbar_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<LoadBar>()?;
    Ok(())
}