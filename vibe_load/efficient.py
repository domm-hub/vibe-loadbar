# "Effeciency is key"

import os
import sys
import time

class MinLoad:
    __slots__ = ('iterable', 'finish', 'prefix', 'term_w', 'last_print', 'start_time', 
                 'unit', 'format_b', 'min_iters', 'fil', 'end', 'unfil')

    def __init__(self, iterable=None, finish=None, prefix='Loading..', fr_bytes=False, min_iters=None):
        self.iterable = iterable
        self.finish = finish if finish else (len(iterable) if iterable else 100)
        self.prefix = prefix
        self.format_b = fr_bytes
        self.start_time = 0.0
        self.last_print = 0.0
        
        # ⚡️ OPTIMIZATION 1: Auto-tune update frequency
        # If total is huge (1M+), check every 1000 steps. If small, check every 10.
        if min_iters:
            self.min_iters = min_iters
        else:
            self.min_iters = max(1, self.finish // 200)  # Target ~200 updates total

        try:
            self.term_w = os.get_terminal_size().columns
        except OSError:
            self.term_w = 80
            
        self.fil = '-'
        self.end = '>'
        self.unfil = ' '

    def format_bytes(self, size, auto_f=False):
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        if size <= 0: return "0.00 B" if auto_f else (0.0, 'B')
        for unit in units:
            if size < 1024.0:
                return f"{size:.2f} {unit}" if auto_f else (size, unit)
            size /= 1024.0
        return f"{size:.2f} YB"

    def _render(self, progress, now):
        """Internal render method - only called when we pass the gate."""
        elapsed = now - self.start_time
        
        # Avoid division by zero
        if elapsed > 0:
            rate = progress / elapsed
        else:
            rate = 0
            
        percent = progress / self.finish if self.finish > 0 else 0
        
        # String formatting
        elapsed_str = f"{elapsed:.1f} s"
        pct_str = f"{percent*100:>6.2f}%"
        
        if self.format_b:
            speed_str = self.format_bytes(rate, auto_f=True) + "/s"
            curr_str = self.format_bytes(progress, auto_f=True)
            total_str = self.format_bytes(self.finish, auto_f=True)
        else:
            speed_str = f"{rate:.2f} it/s"
            curr_str = str(progress)
            total_str = str(self.finish)
            
        val_str = f"({curr_str}/{total_str})"
        
        # Bar geometry
        occupied = len(self.prefix) + len(pct_str) + len(val_str) + len(speed_str) + len(elapsed_str) + 7
        bar_w = max(0, self.term_w - occupied)
        
        fill_len = int(bar_w * percent)
        empty_len = bar_w - fill_len
        
        if empty_len > 0:
            bar_content = (self.fil * fill_len) + self.end + (self.unfil * (empty_len - 1))
        else:
            bar_content = (self.fil * fill_len)

        # ⚡️ OPTIMIZATION 3: Single Write
        sys.stdout.write(f'\r{self.prefix} [{bar_content}] {pct_str} {val_str} {speed_str} {elapsed_str}')
        sys.stdout.flush()
        self.last_print = now

    def update(self, progress):
        # ⚡️ OPTIMIZATION 2: Modulo Throttling
        # Only check the clock every `min_iters` iterations.
        # This skips 99% of the math overhead.
        if progress % self.min_iters == 0 or progress == self.finish:
            now = time.time()
            # Double check: Don't print if less than 0.1s has passed (prevents flicker)
            if now - self.last_print > 0.1 or progress == self.finish:
                self._render(progress, now)

    def __iter__(self):
        if not self.iterable: return
        self.start_time = time.time()
        self.last_print = self.start_time
        
        # CACHE LOCAL VARIABLES (Avoids 'self.' lookup cost in the hot loop)
        update_func = self.update
        
        for i, item in enumerate(self.iterable):
            yield item
            update_func(i + 1)
        
        sys.stdout.write('\n')

    def __enter__(self):
        self.start_time = time.time()
        self.last_print = self.start_time
        return self

    def __exit__(self, *args):
        sys.stdout.write('\n')