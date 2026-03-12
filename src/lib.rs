use pyo3::prelude::*;
use crossterm::{
    terminal,
    style::{Color, Stylize, SetForegroundColor},
};
use std::io::{self, Write};
use std::time::{Instant, Duration};
use std::fmt::Write as FmtWrite; 
use unicode_width::UnicodeWidthStr;

#[derive(Clone)]
enum TemplatePart {
    Literal(String),
    Action,
    Percent,
    Elapsed,
    Speed,
    Bar,
    Br1,
    Br2,
}

#[pyclass]
pub struct LoadBar {
    label: String,
    comp_msg: String,
    finish: f64,
    
    // Time & Math
    start_time: Instant,
    last_update_time: Instant,
    last_render_time: Instant,
    last_progress: f64,
    current_speed: f64,
    smoothing: f64,
    started: bool, // ⚡️ NEW: Lazy start flag
    
    // Rendering
    parts: Vec<TemplatePart>,
    buffer: String,
    
    // Styles
    ac_clr: Color,
    br_clr: Color,
    ex_clr: Color,
    
    // Cache
    label_width: usize,
    
    // Optimization
    n_updates: u64,
    miniters: u64,
    last_size_check: Instant,
    cached_size: (u16, u16),
}

#[pymethods]
impl LoadBar {
    #[new]
    #[pyo3(signature = (label, finish, format_str, ac_clr, br_clr, ex_clr, comp_msg="Complete", smoothing=0.3))]
    fn py_new(
        label: &str, 
        finish: f64, 
        format_str: &str, 
        ac_clr: &str, 
        br_clr: &str, 
        ex_clr: &str, 
        comp_msg: &str, 
        smoothing: f64
    ) -> Self {
        let now = Instant::now();
        
        // Colors
        let ac_c = str_to_color(ac_clr);
        let br_c = str_to_color(br_clr);
        let ex_c = str_to_color(ex_clr);

        // Template Parsing
        let mut parts = Vec::new();
        let tags = [
            ("{action}", TemplatePart::Action),
            ("{percent}", TemplatePart::Percent),
            ("{elapsed}", TemplatePart::Elapsed),
            ("{speed}", TemplatePart::Speed),
            ("{bar}", TemplatePart::Bar),
            ("{br1}", TemplatePart::Br1),
            ("{br2}", TemplatePart::Br2),
        ];

        let mut temp_fmt = format_str.to_string();
        let mut cursor = 0;
        
        while cursor < temp_fmt.len() {
            let mut next_tag_idx = usize::MAX;
            let mut best_tag = None;
            let mut tag_len = 0;
            let remaining = &temp_fmt[cursor..];

            for (key, val) in &tags {
                if let Some(idx) = remaining.find(key) {
                    if idx < next_tag_idx {
                        next_tag_idx = idx;
                        best_tag = Some(val.clone());
                        tag_len = key.len();
                    }
                }
            }

            if next_tag_idx == usize::MAX {
                parts.push(TemplatePart::Literal(remaining.to_string()));
                break;
            } else {
                if next_tag_idx > 0 {
                    parts.push(TemplatePart::Literal(remaining[0..next_tag_idx].to_string()));
                }
                if let Some(tag) = best_tag {
                    parts.push(tag);
                }
                cursor += next_tag_idx + tag_len;
            }
        }

        Self {
            label: label.to_string(),
            comp_msg: comp_msg.to_string(),
            finish,
            start_time: now, 
            last_update_time: now,
            last_render_time: now,
            last_progress: 0.0,
            current_speed: 0.0,
            smoothing,
            started: false, // Wait for first update to start timer
            parts,
            buffer: String::with_capacity(512),
            ac_clr: ac_c,
            br_clr: br_c,
            ex_clr: ex_c,
            label_width: UnicodeWidthStr::width(label),
            n_updates: 0,
            miniters: 1, 
        }
    }

    fn update(&mut self, current: f64) {
        // ⚡️ LAZY START: Reset timer on very first update
        // This fixes the issue where counting iterations takes 10s before the bar starts
        if !self.started {
            let now = Instant::now();
            self.start_time = now;
            self.last_update_time = now;
            self.last_render_time = now;
            self.started = true;
        }

        self.n_updates += 1;

        if self.n_updates % self.miniters != 0 && current < self.finish {
            return;
        }

        let now = Instant::now();
        if now.duration_since(self.last_size_check).as_millis() > 100 {
            self.cached_size = terminal::size().unwrap_or((80, 20));
            self.last_size_check = now;
        }
        let (term_w, _) = self.cached_size;

        // FPS Control
        if elapsed_render < 0.016 && current < self.finish {
            self.miniters = self.miniters.saturating_mul(2);
            // Force at least one render early on so the user sees *something*
            if self.n_updates > 5 { 
                return; 
            }
        } else if elapsed_render > 0.1 && self.miniters > 1 {
            self.miniters /= 2;
        }

        let dt = now.duration_since(self.last_update_time).as_secs_f64();
        if dt > 0.0001 {
            let inst_speed = (current - self.last_progress) / dt;
            // Handle speed spikes at start
            if self.current_speed == 0.0 {
                self.current_speed = inst_speed;
            } else {
                self.current_speed = (self.smoothing * inst_speed) + (1.0 - self.smoothing) * self.current_speed;
            }
        }
        
        self.last_update_time = now;
        self.last_progress = current;

        let pct = (current / self.finish).clamp(0.0, 1.0);
        let total_elapsed = self.start_time.elapsed().as_secs_f64();
        let eta = if self.current_speed > 0.1 { (self.finish - current) / self.current_speed } else { 0.0 };

        // --- RENDER ---
        self.buffer.clear();
        let _ = write!(self.buffer, "\r\x1b[K");

        let (term_w, _) = terminal::size().unwrap_or((80, 20));
        // ⚡️ WRAP FIX: Subtract 2 to prevent terminal auto-wrap
        let term_w = (term_w as usize).saturating_sub(2); 

        let mut used_width = 0;
        for part in &self.parts {
            match part {
                TemplatePart::Literal(s) => used_width += s.len(),
                TemplatePart::Action => used_width += self.label_width,
                TemplatePart::Br1 | TemplatePart::Br2 => used_width += 1,
                TemplatePart::Percent => used_width += 6,
                TemplatePart::Elapsed => used_width += 11,
                TemplatePart::Speed => used_width += 14, // widened slightly
                TemplatePart::Bar => {}
            }
        }
        
        let bar_width = term_w.saturating_sub(used_width).max(1);

        for part in &self.parts {
            match part {
                TemplatePart::Literal(s) => { let _ = self.buffer.write_str(s); },
                TemplatePart::Action => { let _ = write!(self.buffer, "{}", self.label.clone().with(self.ac_clr)); },
                TemplatePart::Br1 => { let _ = write!(self.buffer, "{}", "[".with(self.br_clr)); },
                TemplatePart::Br2 => { let _ = write!(self.buffer, "{}", "]".with(self.br_clr)); },
                TemplatePart::Percent => { let _ = write!(self.buffer, "{}", format!("{:>5.1}%", pct * 100.0).with(self.ex_clr)); },
                TemplatePart::Speed => { let _ = write!(self.buffer, "{}", format!("{:>8.1} it/s", self.current_speed).with(self.ex_clr)); },
                TemplatePart::Elapsed => {
                     let _ = write!(self.buffer, "{}", format!("{:02}:{:02}<{:02}:{:02}", 
                        (total_elapsed / 60.0) as u64, (total_elapsed % 60.0) as u64, 
                        (eta / 60.0) as u64, (eta % 60.0) as u64
                    ).with(self.ex_clr));
                },
                TemplatePart::Bar => {
                    let fill_len = (pct * bar_width as f64) as usize;
                    let empty_len = bar_width.saturating_sub(fill_len);

                    let _ = write!(self.buffer, "{}", SetForegroundColor(self.br_clr));
                    for _ in 0..fill_len.saturating_sub(1) { self.buffer.push('█'); }
                    if pct < 1.0 && fill_len > 0 { self.buffer.push('>'); }
                    else if fill_len > 0 { self.buffer.push('█'); }
                    for _ in 0..empty_len { self.buffer.push('░'); }
                    let _ = write!(self.buffer, "{}", SetForegroundColor(Color::Reset));
                }
            }
        }

        let stdout = io::stdout();
        let mut handle = stdout.lock();
        let _ = handle.write_all(self.buffer.as_bytes());
        let _ = handle.flush();

        self.last_render_time = now;
    }

    fn finish(&mut self) {
        println!("\n{}", self.comp_msg);
    }
}

fn str_to_color(s: &str) -> Color {
    match s.to_lowercase().as_str() {
        "black" => Color::Black, 
        "red" => Color::Red, 
        "green" => Color::Green,
        "yellow" => Color::Yellow, 
        "blue" => Color::Blue, 
        "magenta" => Color::Magenta,
        "cyan" => Color::Cyan, 
        "white" => Color::White,
        _ => Color::Reset,
    }
}

#[pymodule]
fn vibe_loadbar_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<LoadBar>()?;
    Ok(())
}