import os
import time
import sys
import re
from wcwidth import wcswidth
from .styleOBJ import * 
# --- Main Loading Class ---
class Loading:
    def __init__(self, iterable=None, style=None, bar_fil="-", end='>', bar_unfil='-',
                 action='CHILLING', comp='Complete', finish=100, loading=True,
                 unit='', margin=1, auto_bytes=False,
                 format_str=("{margin}\033[0;37m{action}\033[0m \033[1;34m[{bar}]\033[0m "
                             "\033[0;37m{percent}% {values} | {elapsed} < {eta}{speed}\033[0m"),
                 carriage_char='\r', print_cli=True):
        
        self.iterable = iterable
        self.finish = len(iterable) if iterable is not None else finish
        self.style = style
        self.interval = 0.04 
        self.past = ""
        self.last_redrawn = 0
        self.ticks = 0
        self.current_frame_idx = 0
        self.start_time = time.perf_counter()
        
        self.default_bar_fil, self.default_end, self.default_bar_unfil = bar_fil, end, bar_unfil
        self.action, self.comp, self.loading = action, comp, loading
        self.unit, self.margin, self.auto_bytes = unit, margin, auto_bytes
        self.format_str = format_str
        self.carriage_char, self.print_toterminal = carriage_char, print_cli
        self.ansi_escape = re.compile(r'\x1b\[[0-9;]*[mK]')
        self.byte_units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
        self.finished = False

    def format_bytes(self, size):
        for unit in self.byte_units:
            if size < 1024.0: return size, unit
            size /= 1024.0
        return size, 'YB'

    def format_time(self, seconds):
        if seconds < 0: return "--:--"
        m, s = divmod(int(seconds), 60)
        return f"{m:02d}:{s:02d}"

    def get_val_str(self, val):
        if not self.auto_bytes:
            return f"{val:.2e}" if val > 1_000_000 else str(val)
        v, u = self.format_bytes(val)
        return f"{v:>6.2f} {u}"

    def update(self, progress, width=None):
        if width is None:
            try: width = os.get_terminal_size().columns - 2
            except OSError: width = 78
        return self.__display__(progress, self.finish, width)

    def __display__(self, progress, finish, width):
        now = time.perf_counter()
        if now - self.last_redrawn < self.interval and progress < finish:
            return self.past

        # 1. Style Setup
        b_fil, b_end, b_unfil = self.default_bar_fil, self.default_end, self.default_bar_unfil
        
        if isinstance(self.style, SmoothStyle):
            b_fil, b_unfil, b_end = self.style.bar_fil, self.style.bar_unfil, ""
        elif isinstance(self.style, FunStyle):
            p = self.style.elapse_pattern
            if self.ticks >= p[self.current_frame_idx % len(p)]:
                self.current_frame_idx += 1
                self.ticks = 0
            self.ticks += 1
            idx = self.current_frame_idx
            b_fil = self.style.bar_fils[idx % len(self.style.bar_fils)]
            b_end = self.style.ends[idx % len(self.style.ends)]
            b_unfil = self.style.bar_unfils[idx % len(self.style.bar_unfils)]
        elif isinstance(self.style, Style):
            b_fil, b_end, b_unfil = self.style.bar_fil, self.style.end, self.style.bar_unfil

        # 2. Meta-Data Calculations
        safe_progress = min(progress, finish)
        percent = (progress / finish * 100) if finish > 0 else 0
        elapsed = now - self.start_time
        speed_val = progress / elapsed if elapsed > 0 else 0
        eta_val = (finish - progress) / speed_val if speed_val > 0 else 0
        
        val_text = f"({self.get_val_str(progress)}/{self.get_val_str(finish)})"
        s_val, s_unit = self.format_bytes(speed_val)
        speed_text = f" | {s_val:>6.1f} {s_unit}/s" if self.auto_bytes else f" | {speed_val:>6.1f}{self.unit}/s"
        
        # 3. Dynamic Bar Width Calculation
        # We pre-format with an empty bar to see how much space remains
        meta_only = self.ansi_escape.sub('', self.format_str).format(
            margin=' '*self.margin, action=self.action[:20], bar="", 
            percent=f"{percent:>6.2f}", values=val_text, 
            elapsed=self.format_time(elapsed), eta=self.format_time(eta_val), speed=speed_text
        )
        bar_length = max(10, width - len(meta_only) - 2)

        # 4. Bar Construction
        ratio = safe_progress / finish if finish > 0 else 0
        if isinstance(self.style, SmoothStyle):
            total_filled = bar_length * ratio
            n_full = int(total_filled)
            char_idx = int((total_filled - n_full) * len(self.style.frames))
            fill_str = (b_fil * n_full)
            mid_str = self.style.frames[min(char_idx, len(self.style.frames)-1)] if n_full < bar_length else ""
            bar_str = fill_str + mid_str + (b_unfil * (bar_length - wcswidth(fill_str + mid_str)))
        else:
            f_w = max(1, wcswidth(b_fil))
            num_fill = int((bar_length * ratio) / f_w)
            fill_str = b_fil * num_fill
            rem_len = bar_length - wcswidth(fill_str) - wcswidth(b_end)
            bar_str = fill_str + b_end + (b_unfil * max(0, rem_len))

        # 5. Final Render
        res = self.format_str.format(
            margin=' '*self.margin, action=self.action, bar=bar_str,
            percent=f"{percent:>6.2f}", values=val_text,
            elapsed=self.format_time(elapsed), eta=self.format_time(eta_val), speed=speed_text
        )

        self.past = f'{self.carriage_char}\033[K{res}'
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
        if self.print_toterminal: sys.stdout.write(f"\n{self.comp}\n")