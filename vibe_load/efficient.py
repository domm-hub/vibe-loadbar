import os
import sys
import time

class MinLoad:
    # Added 'iterable' to slots so it can be stored
    __slots__ = ('iterable', 'finish', 'width', 'prefix', 'fil', 'end', 'unfil', 'rc', 'term_w', 'p')

    def __init__(self, iterable=None, finish=100, recalculate_width=False, prefix='Loading..'):
        self.iterable = iterable  # <--- CRITICAL FIX: Storing the data!
        self.finish = len(iterable) if iterable else finish
        self.prefix = prefix
        self.rc = recalculate_width
        self.p = time.time()  # <--- FIX: Initialize with current time, not 1
        
        # Pre-calculate terminal width once
        try:
            self.term_w = os.get_terminal_size().columns
        except OSError:
            self.term_w = 80
            
        self.width = self.term_w - 1
        self.fil = '-'
        self.end = '>'
        self.unfil = ' '

    def update(self, progress):
        # 1. Throttling (Speed Limiter)
        # Only update if 0.04s has passed OR if we are hitting 100%
        # This prevents the terminal from flickering and speeds up the loop
        now = time.time()
        if now - self.p < 0.04 and progress < self.finish:
            return

        self.p = now
        
        # 2. Quick Exit (Safety)
        if progress > self.finish:
            return

        # 3. Width Calculation (Only do syscall if forced)
        if self.rc:
            try:
                self.term_w = os.get_terminal_size().columns
            except OSError:
                pass
        
        # 4. Fast Math
        percent = progress / self.finish
        pct_str = f"{percent*100:>6.2f}%"
        val_str = f"({progress}/{self.finish})"
        
        # 5. Bar Geometry
        # Space taken by non-bar elements: Prefix + " [] " + Percent + Values
        # Len: prefix (N) + 2 (brackets) + 1 (space) + 7 (percent) + 1 (space) + val_str (N)
        occupied = len(self.prefix) + len(pct_str) + len(val_str) + 5
        bar_w = max(0, self.term_w - occupied - 2) 
        
        fill_len = int(bar_w * percent)
        empty_len = bar_w - fill_len
        
        # Handle the arrow tip '>' logic strictly
        if empty_len > 0:
            # We subtract 1 from empty_len because the arrow takes 1 spot
            bar_content = (self.fil * fill_len) + self.end + (self.unfil * (empty_len - 1))
        else:
            # If bar is full, just fill it, no arrow or empty space needed at the very end if exact
            bar_content = (self.fil * fill_len)[:bar_w]

        # 6. Direct Output
        sys.stdout.write(f'\r{self.prefix} [{bar_content}] {pct_str} {val_str}')
        sys.stdout.flush()

    def __iter__(self):
        if not self.iterable:
            return
            
        for i, item in enumerate(self.iterable):
            yield item
            self.update(i + 1)
        sys.stdout.write('\n')