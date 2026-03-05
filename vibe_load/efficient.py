import os
import sys
import time

class MinLoad:
    __slots__ = ('iterable', 'finish', 'width', 'prefix', 'fil', 'end', 'unfil', 'rc', 'term_w', 'p', 'past_prog', 'unit', 'format_b', 'start_time')

    def __init__(self, iterable=None, finish=100, recalculate_width=False, prefix='Loading..', fr_bytes=False):
        self.iterable = iterable  
        self.finish = len(iterable) if iterable else finish
        self.prefix = prefix
        self.rc = recalculate_width
        self.p = time.time() 
        self.format_b = fr_bytes
        self.start_time = time.time()
    
        
        try:
            self.term_w = os.get_terminal_size().columns
        except OSError:
            self.term_w = 80
            
        self.width = self.term_w - 1
        self.fil = '-'
        self.end = '>'
        self.unfil = ' '
        self.past_prog = 0
        self.unit = 'it'
        
    def format_bytes(self, size, auto_f=False):
        """Returns a formatted string if auto_f=True, otherwise returns (value, unit) tuple."""
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
        # Handle zero or negative size
        if size <= 0:
            return "0.00 B" if auto_f else (0.0, 'B')
            
        for unit in units:
            if size < 1024.0:
                if auto_f:
                    return f"{size:.2f} {unit}"
                return size, unit
            size /= 1024.0
        
        final_unit = 'YB'
        return f"{size:.2f} {final_unit}" if auto_f else (size, final_unit)
        
    def update(self, progress):
        elapsed_fs = round(time.time() - self.start_time,  1)
        elapsed_str = f"{elapsed_fs} s"
        now = time.time()
        # Throttling to 25 FPS (0.04s) helps avoid terminal flicker
        if now - self.p < 0.04 and progress < self.finish:
            return

        dif_t = now - self.p
        dif_p = progress - self.past_prog
        
        # FIX: Speed = Progress / Time (e.g., Bytes per second)
        items_p_sec = (dif_p / dif_t) if dif_t > 0 else 0

        # Logic for speed readout
        if self.format_b:
            speed_str = self.format_bytes(items_p_sec, auto_f=True) + "/s"
        else:
            speed_str = f"{items_p_sec:.2f} it/s"
        
        # Logic for progress readout
        if self.format_b:
            curr_str = self.format_bytes(progress, auto_f=True)
            total_str = self.format_bytes(self.finish, auto_f=True)
        else:
            curr_str = str(progress)
            total_str = str(self.finish)
            
        val_str = f"({curr_str}/{total_str})"
        
        # 4. Math for percentage
        percent = progress / self.finish if self.finish > 0 else 0
        pct_str = f"{percent*100:>6.2f}%"
        
        # Update trackers
        self.p = now
        self.past_prog = progress
        
        if progress > self.finish:
            return

        # Width calculation for responsiveness
        if self.rc:
            try:
                self.term_w = os.get_terminal_size().columns
            except OSError:
                pass
        
        # 5. Bar Geometry
        # prefix + " [] " + pct + val + speed + extra spaces
        occupied = len(self.prefix) + len(pct_str) + len(val_str) + len(speed_str) + len(elapsed_str) + 7
        bar_w = max(0, self.term_w - occupied) 
        
        fill_len = int(bar_w * percent)
        empty_len = bar_w - fill_len
        
        if empty_len > 0:
            # The '>' arrow takes 1 space from the empty section
            bar_content = (self.fil * fill_len) + self.end + (self.unfil * (empty_len - 1))
        else:
            bar_content = (self.fil * fill_len)

        # 6. Direct Output
        sys.stdout.write(f'\r{self.prefix} [{bar_content}] {pct_str} {val_str} {speed_str} {elapsed_str}')
        sys.stdout.flush()

    def __iter__(self):
        if not self.iterable:
            return
            
        for i, item in enumerate(self.iterable):
            yield item
            self.update(i + 1)
        sys.stdout.write('\n')
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout.write('\n')