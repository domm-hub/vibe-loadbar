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
        #Local import if needed
        self.styler = Styler()
        self.theme = theme or Theme('white', 'white', 'white')

    def _t(self, text, color_attr):
        """Helper to style text using the theme."""
        color = getattr(self.theme, color_attr)
        return self.styler.txt_style(color, str(text))

    def calculate_width(self, text):
        clean_text = self.ansi_escape.sub('', str(text))
        return wcswidth(clean_text)

    def format_bytes(self, size):
        for unit in self.byte_units:
            if size < 1024.0: return f"{size:>6.2f} {unit}"
            size /= 1024.0
        return f"{size:>6.2f} YB"

    def format_time(self, seconds):
        if seconds < 0 or seconds == float('inf'): return "--:--"
        m, s = divmod(int(seconds), 60)
        return f"{m:02d}:{s:02d}"

    def _get_style_chars(self):
        """Logic extracted from main.py's display method."""
        b_fil, b_end, b_unfil = self.default_chars
        
        if not self.style:
            return b_fil, b_end, b_unfil

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

        # 1. Calculations
        elapsed = now - self.start_time
        speed_val = progress / elapsed if elapsed > 0 else 0
        eta_val = (self.finish - progress) / speed_val if speed_val > 0 else 0
        percent = (progress / self.finish * 100) if self.finish > 0 else 0
        
        # 2. String Prep
        val_text = f"({self.format_bytes(progress) if self.auto_bytes else progress}/{self.format_bytes(self.finish) if self.auto_bytes else self.finish})"
        speed_text = f" | {self.format_bytes(speed_val)}/s" if self.auto_bytes else f" | {speed_val:>6.1f}{self.unit}/s"
        
        # Truncate Action
        max_act = max(5, int(width * 0.2))
        disp_act = self.action if self.calculate_width(self.action) <= max_act else self.action[:max_act-1] + "…"

        # 3. Bar Construction (Uncolored for width math)
        b_fil, b_end, b_unfil = self._get_style_chars()
        
        # Calculate Metadata width to find remaining Bar space
        meta_sample = self.format_str.format(
            margin=' '*self.margin, action=disp_act, bar="", percent=f"{percent:>6.2f}",
            values=val_text, elapsed=self.format_time(elapsed), eta=self.format_time(eta_val),
            speed=speed_text, br1="[", br2="]", com="<", sep="|"
        )
        bar_len = max(1, width - self.calculate_width(meta_sample))
        
        # Build Bar String
        ratio = min(1.0, progress / self.finish if self.finish > 0 else 0)
        if isinstance(self.style, SmoothStyle):
            total_filled = bar_len * ratio
            n_full = int(total_filled)
            char_idx = int((total_filled - n_full) * len(self.style.frames))
            mid = self.style.frames[min(char_idx, len(self.style.frames)-1)] if n_full < bar_len else ""
            bar_raw = (b_fil * n_full) + mid
            bar_raw += b_unfil * (bar_len - self.calculate_width(bar_raw))
        else:
            num_f = int(bar_len * ratio)
            bar_raw = (b_fil * num_f)[:bar_len-self.calculate_width(b_end)] + b_end
            bar_raw += b_unfil * (bar_len - self.calculate_width(bar_raw))

        # 4. Final Render with Theme
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