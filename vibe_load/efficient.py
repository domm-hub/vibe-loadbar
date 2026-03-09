import os
import sys
import time
import math 

class MinLoad:
    __slots__ = ('iterable', 'finish', 'prefix', 'term_w', 'last_print', 'start_time', 
                 'unit', 'format_b', 'min_iters', 'fil', 'end', 'unfil', 'byte_units')

    def __init__(self, iterable=None, finish=None, prefix='Loading..', fr_bytes=False, min_iters=None):
        self.iterable = iterable
        self.finish = finish if finish else (len(iterable) if iterable else 100)
        self.prefix = prefix
        self.format_b = fr_bytes
        self.start_time = 0.0
        self.last_print = 0.0
        self.byte_units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        
        # ⚡️ OPTIMIZATION 1: Auto-tune update frequency
        if min_iters:
            self.min_iters = min_iters
        else:
            # math.ceil is faster than manual logic for rounding up
            self.min_iters = max(1, math.ceil(self.finish / 200))

        try:
            self.term_w = os.get_terminal_size().columns
        except (OSError, AttributeError):
            self.term_w = 80
            
        self.fil, self.end, self.unfil = '-', '>', ' '

    def format_bytes(self, size):
        """Logarithmic byte conversion - much faster than a loop."""
        if size <= 0: return "0.00 B"
        # math.log(size, 1024) tells us exactly which unit index to use
        i = min(math.floor(math.log(size, 1024)), 5)
        p = math.pow(1024, i)
        return f"{size/p:.2f} {self.byte_units[i]}"

    def _render(self, progress, now):
        elapsed = now - self.start_time
        _finish = self.finish
        
        # Use math.isclose to avoid zero-division errors safely
        rate = progress / elapsed if elapsed > 1e-6 else 0.0
        percent = progress / _finish if _finish > 0 else 0.0
        
        # ⚡️ OPTIMIZATION: f-strings are ~20% faster than .format()
        pct_str = f"{percent*100:>6.2f}%"
        
        if self.format_b:
            speed_str = f"{self.format_bytes(rate)}/s"
            curr_str = self.format_bytes(progress)
            total_str = self.format_bytes(_finish)
        else:
            speed_str = f"{rate:.2f} it/s"
            curr_str, total_str = str(progress), str(_finish)
            
        val_str = f"({curr_str}/{total_str})"
        
        # Bar geometry using math.floor for pixel-perfect alignment
        occupied = len(self.prefix) + len(pct_str) + len(val_str) + len(speed_str) + 12
        bar_w = max(0, self.term_w - occupied)
        
        fill_len = math.floor(bar_w * percent)
        empty_len = bar_w - fill_len
        
        if empty_len > 0:
            bar_content = f"{self.fil * fill_len}{self.end}{self.unfil * (empty_len - 1)}"
        else:
            bar_content = self.fil * fill_len

        # ⚡️ OPTIMIZATION: f-string write reduces buffer calls
        sys.stdout.write(f'\r{self.prefix} [{bar_content}] {pct_str} {val_str} {speed_str} {elapsed:.1f}s')
        sys.stdout.flush()
        self.last_print = now

    def update(self, progress):
        # ⚡️ OPTIMIZATION: Check modulo FIRST (The Gatekeeper)
        if progress % self.min_iters == 0 or progress == self.finish:
            now = time.time()
            # Double check: 0.1s throttle (60Hz visual vibe)
            if now - self.last_print > 0.1 or progress == self.finish:
                self._render(progress, now)

    def __iter__(self):
        if self.iterable is None: return
        self.start_time = time.time()
        self.last_print = self.start_time
        
        # HOISTING: Local variable access is faster than 'self.'
        _update = self.update
        _finish = self.finish
        
        for i, item in enumerate(self.iterable, 1):
            yield item
            _update(i)
        
        sys.stdout.write('\n')

    def __enter__(self):
        self.start_time = time.time()
        self.last_print = self.start_time
        return self

    def __exit__(self, *args):
        sys.stdout.write('\n')