use pyo3::prelude::*;
use crossterm::{
    terminal,
    style::{self, Color, Stylize},
};
use std::io::{self, Write};
use std::time::Instant;
use regex::Regex;
use unicode_width::UnicodeWidthStr;

#[pyclass]
pub struct LoadBar {
    label: String,
    comp_msg: String,
    progress: f64,
    finish: f64,
    format_str: String,
    // Timing & Smoothing (EWMA)
    start_time: Instant,
    last_rendered_time: Instant,
    last_update_time: Instant,
    last_progress: f64,
    current_speed: f64,
    smoothing: f64,
    // Theme Colors
    ac_clr: Color,
    br_clr: Color,
    ex_clr: Color,
}

/// Helper to convert Python string color names to Crossterm Colors
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
        _ => Color::White,
    }
}

#[pymethods]
impl LoadBar {
    #[new]
    // This signature defines the 8 arguments expected by the Python wrapper
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
        Self {
            label: label.to_string(),
            comp_msg: comp_msg.to_string(),
            progress: 0.0,
            finish,
            format_str: format_str.to_string(),
            start_time: now,
            last_rendered_time: now,
            last_update_time: now,
            last_progress: 0.0,
            current_speed: 0.0,
            smoothing,
            ac_clr: str_to_color(ac_clr),
            br_clr: str_to_color(br_clr),
            ex_clr: str_to_color(ex_clr),
        }
    }

    fn update(&mut self, new_prog: f64) {
        let now = Instant::now();
        
        // 1. EWMA Speed Calculation
        let dt = now.duration_since(self.last_update_time).as_secs_f64();
        if dt > 0.0 {
            let dp = new_prog - self.last_progress;
            let inst_speed = dp / dt;
            // S_t = α * instant + (1 - α) * S_{t-1}
            self.current_speed = (self.smoothing * inst_speed) + (1.0 - self.smoothing) * self.current_speed;
        }
        self.last_update_time = now;
        self.last_progress = new_prog;
        self.progress = new_prog;

        // 2. Throttle Render (60 FPS) to prevent terminal flickering
        if now.duration_since(self.last_rendered_time).as_millis() < 16 && new_prog < self.finish {
            return;
        }
        self.last_rendered_time = now;

        // 3. Prepare Template Variables
        let pct = (self.progress / self.finish).min(1.0).max(0.0);
        let elapsed = self.start_time.elapsed().as_secs_f64();
        let eta = if self.current_speed > 0.0 { (self.finish - self.progress) / self.current_speed } else { 0.0 };

        let label_s = self.label.clone().with(self.ac_clr).to_string();
        let pct_s = format!("{:>5.1}%", pct * 100.0).with(self.ex_clr).to_string();
        let speed_s = format!("{:>8.1} it/s", self.current_speed).with(self.ex_clr).to_string();
        let time_s = format!("{:02}:{:02}<{:02}:{:02}", 
            (elapsed / 60.0) as u64, (elapsed % 60.0) as u64, 
            (eta / 60.0) as u64, (eta % 60.0) as u64
        ).with(self.ex_clr).to_string();

        // 4. Render with Color & Template
        let mut output = self.format_str.clone();
        output = output.replace("{action}", &label_s);
        output = output.replace("{percent}", &pct_s);
        output = output.replace("{elapsed}", &time_s);
        output = output.replace("{speed}", &speed_s);
        output = output.replace("{br1}", &"[".with(self.br_clr).to_string());
        output = output.replace("{br2}", &"]".with(self.br_clr).to_string());

        // 5. Dynamic Bar Width Calculation
        let (width, _) = terminal::size().unwrap_or((80, 20));
        let base_for_width = output.replace("{bar}", "");
        let re_ansi = Regex::new(r"\x1b\[[0-9;]*[mK]").unwrap();
        let stripped = re_ansi.replace_all(&base_for_width, "");
        let bar_width = (width as usize).saturating_sub(stripped.width());

        // 6. Build the Bar
        let fill_len = (pct * bar_width as f64) as usize;
        let bar_content = format!(
            "{}{}{}",
            "█".repeat(fill_len.saturating_sub(1)),
            if pct < 1.0 { ">" } else { "█" },
            "░".repeat(bar_width.saturating_sub(fill_len))
        ).with(self.br_clr).to_string();

        output = output.replace("{bar}", &bar_content);

        // Final Write to stdout
        print!("\r\x1b[K{}", output);
        io::stdout().flush().unwrap();
    }

    /// Prints the completion message and a newline
    fn finish(&self) {
        println!("\n{}", self.comp_msg);
    }
}

#[pymodule]
fn vibe_loadbar_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<LoadBar>()?;
    Ok(())
}