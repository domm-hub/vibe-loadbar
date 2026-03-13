import os
import time
import sys
import re
import math
from wcwidth import wcswidth

# --- Fallback Imports ---
try:
    from .err import FinishAlreadySet
except (ImportError, ValueError):
    class FinishAlreadySet(Exception): pass

try:
    from .styleOBJ import SmoothStyle, FunStyle, Theme
except (ImportError, ValueError):
    # Dummy classes to prevent NameErrors if styleOBJ is missing
    class SmoothStyle: pass
    class FunStyle: pass
    class Theme:
        def __init__(self, *args): pass
        def __getattr__(self, name): return None

try:
    from .clr import Styler
except (ImportError, ValueError):
    class Styler:
        def txt_style(self, color, text): return text


class SafeDict(dict):
    """Allows string formatting to ignore missing keys."""
    def __missing__(self, key):
        return f"{{{key}}}"


class Loading:
    def __init__(self, iterable=None, style=None, bar_fil="-", end='>', bar_unfil='-',
                 action='CHILLING', comp='Complete', finish=100.0, loading=True,
                 unit='', margin=1, auto_bytes=False,
                 format_str=("{margin} {action} {br1}{bar}{br2} "
                             "{percent} {values} {sep} {elapsed} {com} {eta} {speed}"),
                 print_cli=True, theme=None, wfunc=wcswidth, br1="[", br2="]"):
        
        self.iterable = iterable
        self.finish = float(len(iterable)) if iterable is not None else float(finish)
        self.style = style
        self.interval = 0.04 
        self.past = ""
        self.last_redrawn = 0
        self.start_time = time.perf_counter()
        self.w_func = wfunc
        self.miniters = 1
        self.calls = 0
        
        self.br1 = br1
        self.br2 = br2
        
        self.default_chars = (bar_fil, end, bar_unfil)
        self.action, self.comp, self.unit = action, comp, unit
        self.margin, self.auto_bytes = margin, auto_bytes
        self.format_str = format_str
        self.print_toterminal = print_cli
        
        self.ticks = 0
        self.current_frame_idx = 0
        self.ansi_escape = re.compile(r'\x1b\[[0-9;]*[mK]')
        self.byte_units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
        self.elapsed = 0.0
        
        self.styler = Styler()
        self.theme = theme or Theme('white', 'white', 'white')
        self.loading = loading
        self.i = 0

    def _fmt(self, val, width=6):
        """Forces exactly 2 decimal places to stop layout jumping."""
        return f"{float(val):>{width}.2f}"

    def _t(self, text, color_attr):
        """Applies theme color if available."""
        color = getattr(self.theme, color_attr, None)
        if color is None:
            return str(text)
        return self.styler.txt_style(color, str(text))

    def calculate_width(self, text):
        if not text: return 0
        clean_text = self.ansi_escape.sub('', str(text))
        return self.w_func(clean_text)

    def format_bytes(self, size):
        for unit in self.byte_units:
            if size < 1024.0: 
                return f"{size:>6.2f} {unit}"
            size /= 1024.0
        return f"{size:>6.2f} YB"

    def format_time(self, seconds):
        if seconds < 0 or seconds == float('inf') or math.isnan(seconds): 
            return "--:--"
        m, s = divmod(int(seconds), 60)
        return f"{m:02d}:{s:02d}"

    def _get_style_chars(self):
        b_fil, b_end, b_unfil = self.default_chars
        if not self.style: 
            return b_fil, b_end, b_unfil
            
        if isinstance(self.style, SmoothStyle):
            # Fallbacks in case SmoothStyle is missing attributes
            s_fil = getattr(self.style, 'bar_fil', b_fil)
            s_unfil = getattr(self.style, 'bar_unfil', b_unfil)
            return s_fil, "", s_unfil
            
        if isinstance(self.style, FunStyle):
            p = getattr(self.style, 'elapse_pattern', [1])
            if self.ticks >= p[self.current_frame_idx % len(p)]:
                self.current_frame_idx += 1
                self.ticks = 0
            self.ticks += 1
            idx = self.current_frame_idx
            
            s_fils = getattr(self.style, 'bar_fils', [b_fil])
            s_ends = getattr(self.style, 'ends', [b_end])
            s_unfils = getattr(self.style, 'bar_unfils', [b_unfil])
            
            return (s_fils[idx % max(1, len(s_fils))],
                    s_ends[idx % max(1, len(s_ends))],
                    s_unfils[idx % max(1, len(s_unfils))])
                    
        return getattr(self.style, 'bar_fil', b_fil), getattr(self.style, 'end', b_end), getattr(self.style, 'bar_unfil', b_unfil)

    def update(self, progress, widtha: float=None):
        self.calls += 1
        try: 
            width = os.get_terminal_size().columns - 2
        except OSError: 
            width = 78
        width = int(widtha) if widtha else width
        return self.__display__(float(progress), width)

    def __display__(self, progress: float, width):
        now = time.perf_counter()
        
        # Throttle redraws unless complete
        if now - self.last_redrawn < self.interval and progress < self.finish:
            return self.past

        self.elapsed = now - self.start_time
        
        # --- Metrics Calculation ---
        speed_val = progress / self.elapsed if self.elapsed > 0 else 0.0
        
        if self.finish > 0.0:
            eta_val = (self.finish - progress) / speed_val if speed_val > 0 else 0.0
            percent = (progress / self.finish * 100.0)
            pct_text = f"{self._fmt(percent, 6)} %"
            eta_text = self.format_time(eta_val)
        else:
            pct_text = "  --- %"
            eta_text = "--:--"
        
        if self.auto_bytes:
            val_text = f"({self.format_bytes(progress)}/{self.format_bytes(self.finish) if self.finish > 0 else '?'})"
            speed_text = f" | {self.format_bytes(speed_val)}/s"
        else:
            val_text = f"({self._fmt(progress)}/{self._fmt(self.finish) if self.finish > 0 else '?'})"
            speed_text = f" | {self._fmt(speed_val)}{self.unit}/s"
        
        # --- Action String Truncation ---
        max_act = max(5, int(width * 0.2)) 
        disp_act = self.action if self.calculate_width(self.action) <= max_act else self.action[:max_act-1] + "…"

        b_fil, b_end, b_unfil = self._get_style_chars()
        
        if self.loading:
            # 1. Calculate how much space the metadata takes up
            format_dict_sample = SafeDict(
                margin=' '*self.margin, action=disp_act, bar="", percent=pct_text,
                values=val_text, elapsed=self.format_time(self.elapsed), eta=eta_text,
                speed=speed_text, br1="[", br2="]", com="<", sep="|"
            )
            
            # Use SafeDict so missing keys in user format_str don't crash
            meta_sample = self.format_str.format(**format_dict_sample)
            bar_len = max(1, width - self.calculate_width(meta_sample))
            
            f_w = max(1, self.calculate_width(b_fil))
            e_w = self.calculate_width(b_end)
            u_w = max(1, self.calculate_width(b_unfil))
            
            # 2. Build the Bar
            if self.finish > 0:
                ratio = min(1.0, max(0.0, progress / self.finish))

                if isinstance(self.style, SmoothStyle) and hasattr(self.style, 'frames'):
                    total_filled = bar_len * ratio
                    n_full = int(total_filled / f_w)
                    fill_str = b_fil * n_full
                    
                    remaining_after_full = total_filled - (n_full * f_w)
                    char_idx = int(remaining_after_full * len(self.style.frames))
                    
                    if (n_full * f_w) < bar_len:
                        mid_str = self.style.frames[min(char_idx, len(self.style.frames)-1)]
                    else:
                        mid_str = ""
                        
                    current_w = self.calculate_width(fill_str + mid_str)
                    unfill_count = int(max(0, bar_len - current_w) / u_w)
                    bar_raw = fill_str + mid_str + (b_unfil * unfill_count)
                    
                else:
                    available_for_fill = max(0, bar_len - e_w)
                    num_f = int((available_for_fill * ratio) / f_w)
                    fill_str = b_fil * num_f
                    
                    current_w = self.calculate_width(fill_str)
                    rem_len = max(0, bar_len - current_w - e_w)
                    num_u = int(rem_len / u_w)
                    
                    # Only show the 'end' character if the bar isn't 100% full
                    actual_end = b_end if ratio < 1.0 else (b_fil if e_w == f_w else "")
                    bar_raw = fill_str + actual_end + (b_unfil * num_u)
            else:
                # Indeterminate Ping-Pong Bar
                wing_size = math.floor(max(2, int(bar_len * 0.15)) / f_w)
                wing_visual_width = wing_size * f_w
                available_space = bar_len - wing_visual_width
                
                if available_space > 0:
                    t = now * 2.5 # Speed up the ping-pong slightly
                    ping_pong = (math.sin(t) + 1) / 2
                    pos = int(ping_pong * available_space)
                    bar_raw = (" " * pos) + (b_fil * wing_size) + (" " * (available_space - pos))
                else:
                    bar_raw = b_fil * (bar_len // f_w)

            # Pad raw bar if calculation fell short due to character widths
            final_w = self.calculate_width(bar_raw)
            if final_w < bar_len:
                bar_raw += " " * (bar_len - final_w)
                
            br1 = getattr(self.style, 'br1', self.br1) if self.style else self.br1
            br2 = getattr(self.style, 'br2', self.br2) if self.style else self.br2
        else:
            bar_raw, br1, br2 = "", "", ""

        # --- Final Render ---
        render_dict = SafeDict(
            margin = ' ' * self.margin,
            action = self._t(disp_act, 'ac_clr'),
            bar    = self._t(bar_raw, 'br_clr'),
            percent= self._t(pct_text, 'ex_clr'),
            values = self._t(val_text, 'ex_clr'),
            elapsed= self._t(self.format_time(self.elapsed), 'ex_clr'),
            eta    = self._t(eta_text, 'ex_clr'),
            speed  = self._t(speed_text, 'ex_clr'),
            br1    = self._t(br1, 'br_clr'),
            br2    = self._t(br2, 'br_clr'),
            com    = self._t('<', 'ex_clr'),
            sep    = self._t('|', 'ex_clr')
        )

        res = self.format_str.format(**render_dict)

        # \033[K clears to the end of the line
        self.past = f'\r\033[K{res}'
        
        if self.print_toterminal:
            sys.stdout.write(self.past)
            sys.stdout.flush()
            
        self.last_redrawn = now
        return self.past

    def set_finish(self, val):
        if self.finish != 0: 
            raise FinishAlreadySet("Finish was already set.")
        self.finish = float(val)
    
    def __iter__(self):
        # Hide cursor on iteration start
        if self.print_toterminal:
            sys.stdout.write('\x1b[?25l')
            
        try:
            for i, item in enumerate(self.iterable):
                yield item
                self.update(float(i + 1))
        finally:
            # Ensure cursor comes back even if iteration breaks
            if self.print_toterminal:
                sys.stdout.write('\x1b[?25h')
                sys.stdout.write(f"\n{self.comp} in ({self.format_time(self.elapsed)})\n")

    def __enter__(self):
        if self.print_toterminal:
            sys.stdout.write('\x1b[?25l') # Hide cursor
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.print_toterminal:
            sys.stdout.write('\x1b[?25h') # Show cursor
            if not exc_type:
                sys.stdout.write(f"\n{self.comp} in ({self.format_time(self.elapsed)})\n")