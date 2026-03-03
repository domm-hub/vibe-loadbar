import os
import time
import sys
import re
import math
from wcwidth import wcswidth

# --- Style Definitions ---

class Style:
    def __init__(self, bar_fil, end, bar_unfil):
        self.bar_fil, self.end, self.bar_unfil = bar_fil, end, bar_unfil

class FunStyle:
    def __init__(self, bar_fils, ends, bar_unfils, elapse_pattern=None):
        self.bar_fils, self.ends, self.bar_unfils = bar_fils, ends, bar_unfils
        self.elapse_pattern = elapse_pattern or [1]

class SmoothStyle:
    def __init__(self, bar_fil='█', bar_unfil=' ', frames=[' ', '▏', '▎', '▍', '▌', '▋', '▊', '▉']):
        self.bar_fil, self.bar_unfil = bar_fil, bar_unfil
        self.frames = frames

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
        self.format_str, self.carriage_char, self.print_toterminal = format_str, carriage_char, print_cli
        self.ansi_escape = re.compile(r'\x1b\[[0-9;]*[mK]')
        self.byte_units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
        self.finished = False

    def format_bytes(self, size):
        """Scales bytes and returns (value, unit_string)."""
        for unit in self.byte_units:
            if size < 1024.0: return size, unit
            size /= 1024.0
        return size, 'YB'

    def format_time(self, seconds):
        if seconds < 0: return "--:--"
        if seconds == float('inf') or seconds > 1e300: return "∞"
        
        # 1. Scientific for anything over a century
        SEC_PER_YEAR = 31536000
        if seconds > (SEC_PER_YEAR * 100):
            return f"{seconds / SEC_PER_YEAR:.2e} yr"

        # 2. Human readable breakdown
        intervals = (('dec', 315360000), ('yr', 31536000), ('mo', 2592000), 
                     ('d', 86400), ('h', 3600), ('m', 60))
        for name, count in intervals:
            value = seconds // count
            if value: return f"{int(value)}{name}"
        
        m, s = divmod(int(seconds), 60)
        return f"{m:02d}:{s:02d}"

    def get_val_str(self, val):
        if not self.auto_bytes:
            return f"{val:.2e}" if val > 1_000_000 else str(val)
        v, u = self.format_bytes(val)
        # If it's over 1000 YB or huge scaled, use scientific
        if (u == 'YB' and v >= 1000) or v > 1e12:
            return f"{v:.2e} {u}"
        return f"{v:>6.2f} {u}"

    def update(self, progress, width=None, finished=False):
        if width is None:
            try: width = os.get_terminal_size().columns - 2
            except OSError: width = 78
        self.finished = finished
        return self.__display__(progress, self.finish, width)

    def __display__(self, progress, finish, width):
        now = time.perf_counter()
        if now - self.last_redrawn < self.interval and progress < finish:
            return self.past

        # 1. Style Setup
        if isinstance(self.style, SmoothStyle):
            b_fil, b_unfil = self.style.bar_fil, self.style.bar_unfil
        elif isinstance(self.style, FunStyle):
            p = self.style.elapse_pattern
            if self.ticks >= p[self.current_frame_idx % len(p)]:
                self.current_frame_idx += 1; self.ticks = 0
            self.ticks += 1
            idx = self.current_frame_idx
            b_fil, b_end, b_unfil = self.style.bar_fils[idx % len(self.style.bar_fils)], \
                                    self.style.ends[idx % len(self.style.ends)], \
                                    self.style.bar_unfils[idx % len(self.style.bar_unfils)]
        elif isinstance(self.style, Style):
            b_fil, b_end, b_unfil = self.style.bar_fil, self.style.end, self.style.bar_unfil
        else:
            b_fil, b_end, b_unfil = self.default_bar_fil, self.default_end, self.default_bar_unfil

        # 2. Meta-Data & Scaling
        safe_progress = min(progress, finish)
        percent = (progress / finish * 100) if finish > 0 else 0
        elapsed = now - self.start_time
        speed_val = progress / elapsed if elapsed > 0 else 0
        eta = self.format_time((finish - progress) / speed_val) if self.loading and speed_val > 0 else "--:--"

        # Adaptive formatting for Progress and Speed
        val_text = f"({self.get_val_str(progress)}/{self.get_val_str(finish)})"
        
        s_val, s_unit = self.format_bytes(speed_val)
        if self.auto_bytes:
            speed_text = f" | {s_val:.2e} {s_unit}/s" if (s_unit == 'YB' and s_val >= 1000) else f" | {s_val:>6.1f} {s_unit}/s"
        else:
            speed_text = f" | {speed_val:>6.1f}{self.unit}/s"
        
        action = self.action if len(self.action) <= 25 else f"{self.action[:21]}..."

        # 3. Dynamic Bar Calculation
        temp_meta = self.ansi_escape.sub('', self.format_str).format(
            margin=' '*self.margin, action=action, bar="", 
            percent=f"{percent:>6.2f}", values=val_text, elapsed=self.format_time(elapsed), 
            eta=eta, speed=speed_text
        )
        bar_length = max(10, width - len(temp_meta) - 2)

        # 4. Bar Construction
        bar_str = ""
        if isinstance(self.style, SmoothStyle):
            ratio = safe_progress / finish if finish > 0 else 0
            total_filled = bar_length * ratio
            n_full = int(total_filled)
            char_idx = int((total_filled - n_full) * len(self.style.frames))
            bar_str = (b_fil * n_full)
            if n_full < bar_length:
                bar_str += self.style.frames[min(char_idx, len(self.style.frames)-1)]
            bar_str += (b_unfil * max(0, bar_length - wcswidth(bar_str)))
        else:
            f_w = max(1, wcswidth(b_fil))
            num_fill = int(bar_length * (safe_progress / finish)) // f_w if finish > 0 else 0
            curr_end = b_end if 'b_end' in locals() else self.default_end
            rem_len = bar_length - (num_fill * f_w) - wcswidth(curr_end)
            bar_str = (b_fil * num_fill) + curr_end + (b_unfil * max(0, rem_len))

        # 5. Render
        p_str = "100.00" if progress >= finish else f"{percent:>6.2f}"
        res = self.format_str.format(
            margin=' '*self.margin, action=action, bar=bar_str,
            percent=p_str, values=val_text,
            elapsed=self.format_time(elapsed), eta=eta, speed=speed_text
        )

        self.past = f'{self.carriage_char}\033[K{res}'
        if self.print_toterminal:
            sys.stdout.write(self.past); sys.stdout.flush()
        
        self.last_redrawn = now
        return self.past

    def __iter__(self):
        for i, item in enumerate(self.iterable):
            yield item
            self.update(i + 1)
        if self.print_toterminal and self.finished: sys.stdout.write(f"\n{self.comp}\n")

    def __enter__(self): return self
    def __exit__(self, t, v, tb): 
        if self.print_toterminal: sys.stdout.write(f"\n{self.comp}\n")