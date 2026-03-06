import os
import time
import sys
import re
from wcwidth import wcswidth
from .styleOBJ import *

class Loading:
    def __init__(self, iterable=None, style=None, bar_fil="-", end='>', bar_unfil='-',
                 action='CHILLING', comp='Complete', finish=100, loading=True,
                 unit='', margin=1, auto_bytes=False,
                 format_str=("{margin} {action} {br1}{bar}{br2} "
                             "{percent}% {values} {sep} {elapsed} {com} {eta} {speed}"),
                 print_cli=True, theme=None):
        
        self.iterable = iterable
        self.finish = len(iterable) if iterable is not None else finish
        self.style = style
        self.interval = 0.04 
        self.past = ""
        self.last_redrawn = 0
        self.start_time = time.perf_counter()
        
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
        from .clr import Styler
        from .styleOBJ import Theme
        self.styler = Styler()
        self.theme = theme or Theme('white', 'white', 'white')

    def _t(self, text, color_attr):
        """Styles text using the theme colors."""
        color = getattr(self.theme, color_attr)
        return self.styler.txt_style(color, str(text))

    def calculate_width(self, text):
        """Calculates visual width, correctly identifying emoji double-columns."""
        if not text: return 0
        clean_text = self.ansi_escape.sub('', str(text))
        return wcswidth(clean_text)

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

    def update(self, progress):
        try: width = os.get_terminal_size().columns - 2
        except OSError: width = 78
        return self.__display__(progress, width)

    def __display__(self, progress, width):
        now = time.perf_counter()
        if now - self.last_redrawn < self.interval and progress < self.finish:
            return self.past

        # 1. Base Calculations
        elapsed = now - self.start_time
        speed_val = progress / elapsed if elapsed > 0 else 0
        eta_val = (self.finish - progress) / speed_val if speed_val > 0 else 0
        percent = (progress / self.finish * 100) if self.finish > 0 else 0
        
        val_text = f"({self.format_bytes(progress) if self.auto_bytes else progress}/{self.format_bytes(self.finish) if self.auto_bytes else self.finish})"
        speed_text = f" | {self.format_bytes(speed_val)}/s" if self.auto_bytes else f" | {speed_val:>6.1f}{self.unit}/s"
        
        # 2. Dynamic Truncation for Action Text
        max_act = max(5, int(width * 0.2))
        disp_act = self.action if self.calculate_width(self.action) <= max_act else self.action[:max_act-1] + "…"

        # 3. Bar Space Calculation (Using visual width)
        b_fil, b_end, b_unfil = self._get_style_chars()
        meta_sample = self.format_str.format(
            margin=' '*self.margin, action=disp_act, bar="", percent=f"{percent:>6.2f}",
            values=val_text, elapsed=self.format_time(elapsed), eta=self.format_time(eta_val),
            speed=speed_text, br1="[", br2="]", com="<", sep="|"
        )
        bar_len = max(1, width - self.calculate_width(meta_sample))
        
        # 4. Accurate Bar Construction with Character-Width Awareness
        ratio = min(1.0, progress / self.finish if self.finish > 0 else 0)
        f_w = max(1, self.calculate_width(b_fil))   # Filler width
        e_w = self.calculate_width(b_end)          # End width
        u_w = max(1, self.calculate_width(b_unfil)) # Unfiller width

        if isinstance(self.style, SmoothStyle):
            total_filled = bar_len * ratio
            n_full = int(total_filled / f_w)
            
            fill_str = b_fil * n_full
            # Calculate sub-character frame index
            remaining_after_full = total_filled - (n_full * f_w)
            char_idx = int(remaining_after_full * len(self.style.frames))
            mid_str = self.style.frames[min(char_idx, len(self.style.frames)-1)] if (n_full * f_w) < bar_len else ""
            
            current_w = self.calculate_width(fill_str + mid_str)
            unfill_count = int(max(0, bar_len - current_w) / u_w)
            bar_raw = fill_str + mid_str + (b_unfil * unfill_count)
        else:
            # Leave room for the 'end' character
            available_for_fill = max(0, bar_len - e_w)
            num_f = int((available_for_fill * ratio) / f_w)
            
            fill_str = b_fil * num_f
            current_w = self.calculate_width(fill_str)
            
            # Fill remaining space with unfiller
            rem_len = max(0, bar_len - current_w - e_w)
            num_u = int(rem_len / u_w)
            bar_raw = fill_str + b_end + (b_unfil * num_u)

        # Final Padding to ensure the bar fills the exact target width
        final_w = self.calculate_width(bar_raw)
        if final_w < bar_len:
            bar_raw += " " * (bar_len - final_w)

        # 5. Final Render with Theme
        res = self.format_str.format(
            margin = ' ' * self.margin,
            action = self._t(disp_act, 'ac_clr'),
            bar    = self._t(bar_raw, 'br_clr'),
            percent= self._t(f"{percent:>6.2f}", 'ex_clr'),
            values = self._t(val_text, 'ex_clr'),
            elapsed= self._t(self.format_time(elapsed), 'ex_clr'),
            eta    = self._t(self.format_time(eta_val), 'ex_clr'),
            speed  = self._t(speed_text, 'ex_clr'),
            br1    = self._t('[', 'br_clr'),
            br2    = self._t(']', 'br_clr'),
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