import os
import time
import sys
import re
from wcwidth import wcswidth
import os
try:
    from .styleOBJ import *
except ImportError:
    from styleOBJ import *

class Loading:
    def __init__(self, iterable=None, style=None, bar_fil="-", end='>', bar_unfil='-',
                 action='CHILLING', comp='Complete', finish=100, loading=True,
                 unit='', margin=1, auto_bytes=False,
                 format_str=("{margin} {action} {br1}{bar}{br2} "
                             "{percent} {values} {sep} {elapsed} {com} {eta} {speed}"),
                 print_cli=True, theme=None, wfunc=wcswidth):
        
        self.iterable = iterable
        self.finish = len(iterable) if iterable is not None else finish
        self.style = style
        self.interval = 0.04 
        self.past = ""
        self.last_redrawn = 0
        self.start_time = time.perf_counter()
        self.w_func = wfunc
        self.miniters = 1
        self.calls = 0
        
        # Style defaults
        self.default_chars = (bar_fil, end, bar_unfil)
        self.action, self.comp, self.unit = action, comp, unit
        self.margin, self.auto_bytes = margin, auto_bytes
        self.format_str = format_str
        self.print_toterminal = print_cli
        
        # State trackers for FunStyle
        self.ticks = 0
        self.current_frame_idx = 0
        
        # Regex and Byte constants
        self.ansi_escape = re.compile(r'\x1b\[[0-9;]*[mK]')
        self.byte_units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
        
        # Theme setup
        try:
            from .clr import Styler
            from .styleOBJ import Theme
        except:
            from clr import Styler
            from styleOBJ import Theme
        self.styler = Styler()
        self.theme = theme or Theme('white', 'white', 'white')
        self.loading = loading
        self.i = 0

    def _t(self, text, color_attr):
        """Styles text using the theme colors."""
        color = getattr(self.theme, color_attr)
        return self.styler.txt_style(color, str(text))

    def calculate_width(self, text):
        """Calculates visual width, correctly identifying emoji double-columns."""
        if not text: return 0
        clean_text = self.ansi_escape.sub('', str(text))
        return self.w_func(clean_text)

    def format_bytes(self, size):
        """Converts raw numbers to human-readable byte strings."""
        for unit in self.byte_units:
            if size < 1024.0: return f"{size:>6.2f} {unit}"
            size /= 1024.0
        return f"{size:>6.2f} YB"

    def format_time(self, seconds):
        if seconds < 0 or seconds == float('inf'): return "--:--"
        m, s = divmod(int(seconds), 60)
        return f"{m:02d}:{s:02d}"

    def _get_style_chars(self):
        """Retrieves the correct characters for the current style frame."""
        b_fil, b_end, b_unfil = self.default_chars
        if not self.style: return b_fil, b_end, b_unfil

        if isinstance(self.style, SmoothStyle):
            return self.style.bar_fil, "", self.style.bar_unfil
        
        if isinstance(self.style, FunStyle):
            p = self.style.elapse_pattern
            if self.ticks >= p[self.current_frame_idx % len(p)]:
                self.current_frame_idx += 1
                self.ticks = 0
            self.ticks += 1
            idx = self.current_frame_idx
            return (self.style.bar_fils[idx % len(self.style.bar_fils)],
                    self.style.ends[idx % len(self.style.ends)],
                    self.style.bar_unfils[idx % len(self.style.bar_unfils)])
        
        return self.style.bar_fil, self.style.end, self.style.bar_unfil

    def write(self, txt):
        sys.stdout.write(txt + '\n')
    
    def update(self, progress, widtha: float=None):
        
        self.calls += 1

        try: 
            width = os.get_terminal_size().columns - 2
        except OSError: 
            width = 78
            
        width = widtha if widtha else width
        return self.__display__(progress, width)

    def __display__(self, progress, width):
        now = time.perf_counter()
        if now - self.last_redrawn < self.interval and progress < self.finish:
            return self.past

        # 1. Base Calculations
        elapsed = now - self.start_time
        if self.finish > 0:
            speed_val = progress / elapsed if elapsed > 0 else 0
            eta_val = (self.finish - progress) / speed_val if speed_val > 0 else 0
            percent = (progress / self.finish * 100)
            pct_text = f"{percent:>6.2f}%"
            eta_text = self.format_time(eta_val)
        else:
            speed_val = progress / elapsed if elapsed > 0 else 0
            pct_text = "  --- %"
            eta_text = "--:--"
        
        val_text = f"({self.format_bytes(progress) if self.auto_bytes else progress}/{self.format_bytes(self.finish) if self.auto_bytes else self.finish})"
        speed_text = f" | {self.format_bytes(speed_val)}/s" if self.auto_bytes else f" | {speed_val:>6.1f}{self.unit}/s"
        
        # 2. Dynamic Truncation for Action Text
        max_act = max(5, int(width * 0.2))
        disp_act = self.action if self.calculate_width(self.action) <= max_act else self.action[:max_act-1] + "…"

        # 3. Bar Space Calculation (Using visual width)
        b_fil, b_end, b_unfil = self._get_style_chars()
        
        if self.loading:
            meta_sample = self.format_str.format(
                margin=' '*self.margin, action=disp_act, bar="", percent=pct_text,
                values=val_text, elapsed=self.format_time(elapsed), eta=eta_text,
                speed=speed_text, br1="[", br2="]", com="<", sep="|"
            )
            bar_len = max(1, width - self.calculate_width(meta_sample))
            
            # 4. Accurate Bar Construction
            if self.finish > 0:
                ratio = min(1.0, progress / self.finish)
                f_w = max(1, self.calculate_width(b_fil))   # Filler width
                e_w = self.calculate_width(b_end)          # End width
                u_w = max(1, self.calculate_width(b_unfil)) # Unfiller width

                if isinstance(self.style, SmoothStyle):
                    total_filled = bar_len * ratio
                    n_full = int(total_filled / f_w)
                    
                    fill_str = b_fil * n_full
                    remaining_after_full = total_filled - (n_full * f_w)
                    char_idx = int(remaining_after_full * len(self.style.frames))
                    mid_str = self.style.frames[min(char_idx, len(self.style.frames)-1)] if (n_full * f_w) < bar_len else ""
                    
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
                    bar_raw = fill_str + b_end + (b_unfil * num_u)
            else:
                # 🎾 BOUNCE MODE (Indeterminate)
                import math
                wing_size = max(2, int(bar_len * 0.05))
                available_space = bar_len - wing_size
                if available_space > 0:
                    t = now * 1 # Speed of bounce
                    ping_pong = (math.sin(t) + 1) / 2
                    pos = int(ping_pong * available_space)
                    bar_raw = (" " * pos) + (b_fil * wing_size) + (" " * (available_space - pos))
                else:
                    bar_raw = b_fil * bar_len

            final_w = self.calculate_width(bar_raw)
            if final_w < bar_len:
                bar_raw += " " * (bar_len - final_w)
            
            br1, br2 = '[', ']'
        else:
            bar_raw = ""
            br1, br2 = "", ""

        # 5. Final Render with Theme
        res = self.format_str.format(
            margin = ' ' * self.margin,
            action = self._t(disp_act, 'ac_clr'),
            bar    = self._t(bar_raw, 'br_clr'),
            percent= self._t(pct_text, 'ex_clr'),
            values = self._t(val_text, 'ex_clr'),
            elapsed= self._t(self.format_time(elapsed), 'ex_clr'),
            eta    = self._t(eta_text, 'ex_clr'),
            speed  = self._t(speed_text, 'ex_clr'),
            br1    = self._t(br1, 'br_clr'),
            br2    = self._t(br2, 'br_clr'),
            com    = self._t('<', 'ex_clr'),
            sep    = self._t('|', 'ex_clr')
        )

        self.past = f'\r\033[K{res}'
        if self.print_toterminal:
            sys.stdout.write(self.past)
            sys.stdout.flush()
        
        self.last_redrawn = now
        return self.past

    def __iter__(self):
        for i, item in enumerate(self.iterable):
            yield item
            self.update(i + 1)
        if self.print_toterminal: sys.stdout.write(f"\n{self.comp}\n")

    def __enter__(self): return self
    def __exit__(self, t, v, tb):
        if self.print_toterminal and not t:
            sys.stdout.write(f"\n{self.comp}\n")
