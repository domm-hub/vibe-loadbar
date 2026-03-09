import os
import time
import sys
import re
from wcwidth import wcswidth

try:
    from .styleOBJ import SmoothStyle, FunStyle, Theme
    from .clr import Styler
except ImportError:
    from styleOBJ import SmoothStyle, FunStyle, Theme
    from clr import Styler

class Loading:
    __slots__ = [
        'finish', 'interval', 'past', 'last_redrawn', 'start_time',
        'action', 'comp', 'unit', 'margin', 'auto_bytes', 
        'ticks', 'current_frame_idx', 'byte_units', 
        'theme', 'miniters', 'n_updates', '_write',
        # Optimization Caches
        '_width_func', '_cached_prefix', '_cached_width', '_cached_prefix_len', 
        '_last_term_check', '_term_width',
        '_c_ac', '_c_br', '_c_ex', '_c_rst',
        '_bar_fil', '_bar_end', '_bar_unfil', '_style_frames', '_style_pattern'
    ]

    def __init__(self, iterable=None, style=None, bar_fil="-", end='>', bar_unfil='-',
                 action='CHILLING', comp='Complete', finish=100, loading=True,
                 unit='', margin=1, auto_bytes=False,
                 print_cli=True, theme=None):
        
        self.finish = float(len(iterable)) if iterable is not None else float(finish)
        self.interval = 0.05
        self.past = ""
        self.last_redrawn = 0
        self.start_time = time.perf_counter()
        
        self.action = action
        self.comp = comp
        self.unit = unit
        self.margin = " " * margin
        self.auto_bytes = auto_bytes
        
        if print_cli:
            self._write = sys.stdout.write
        else:
            self._write = lambda x: None

        self.ticks = 0
        self.current_frame_idx = 0
        self.byte_units = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
        
        _styler = Styler()
        self.theme = theme or Theme('white', 'white', 'white')

        # 1. CACHE COLORS
        self._c_ac = _styler.txt_style(self.theme.ac_clr, "").replace("\x1b[0m", "")
        self._c_br = _styler.txt_style(self.theme.br_clr, "").replace("\x1b[0m", "")
        self._c_ex = _styler.txt_style(self.theme.ex_clr, "").replace("\x1b[0m", "")
        self._c_rst = "\x1b[0m"

        # 2. CACHE STYLE & WIDTH FUNCTION
        check_chars = (bar_fil, end, bar_unfil) 
        if style:
            if isinstance(style, SmoothStyle):
                self._bar_fil = style.bar_fil
                self._bar_end = ""
                self._bar_unfil = style.bar_unfil
                self._style_frames = style.frames
                self._style_pattern = None
                check_chars = (style.bar_fil, style.bar_unfil)
            elif isinstance(style, FunStyle):
                self._bar_fil = None
                self._style_pattern = style.elapse_pattern
                self._style_frames = (style.bar_fils, style.ends, style.bar_unfils)
                self._bar_end = None
                self._bar_unfil = None
                check_chars = (style.bar_fils[0], style.ends[0], style.bar_unfils[0])
            elif isinstance(style, St):
                self._bar_fil = style.bar_fil
                self._bar_end = style.end
                self._bar_unfil = style.bar_unfil
                self._style_frames = None
                self._style_pattern = None
                check_chars = (style.bar_fil, style.end, style.bar_unfil)
        else:
            self._bar_fil = bar_fil
            self._bar_end = end
            self._bar_unfil = bar_unfil
            self._style_frames = None
            self._style_pattern = None
            check_chars = (bar_fil, end, bar_unfil)

        is_ascii = all(ord(c) < 128 for c in check_chars if c)
        self._width_func = len if is_ascii else wcswidth

        # 3. INITIALIZE STATE
        self.n_updates = 0
        self.miniters = 1
        self._last_term_check = 0
        self._term_width = 80
        
        self._cached_width = 0
        self._rebuild_prefix(80)

    def _rebuild_prefix(self, width):
        _act = self.action
        _max_act = int(width * 0.2)
        if _max_act < 5: _max_act = 5
        
        if len(_act) > _max_act:
            if self._width_func(_act) > _max_act:
                _act = _act[:_max_act-1] + "…"
        
        # Pre-bake prefix: "  Action ["
        self._cached_prefix = f"{self.margin}{self._c_ac}{_act}{self._c_rst} {self._c_br}["
        self._cached_width = width
        # Store only the visual length of the prefix so we can calculate bar len dynamically
        # len(margin) + visual_len(action) + 1 space + 1 bracket
        self._cached_prefix_len = len(self.margin) + self._width_func(_act) + 2

    def format_bytes(self, size):
        if size <= 0: return "  0.00 B"
        units = self.byte_units
        i = 0
        while size >= 1024 and i < 8:
            size /= 1024
            i += 1
        return f"{size:>6.2f} {units[i]}"

    def update(self, progress):
        self.n_updates += 1
        if (self.n_updates % self.miniters != 0) and (progress < self.finish):
            return self.past

        now = time.perf_counter()
        
        # Adaptive Throttling
        elapsed_render = now - self.last_redrawn
        if elapsed_render < self.interval:
            if progress < self.finish:
                self.miniters *= 2
                return self.past
        else:
            if elapsed_render > 0.5 and self.miniters > 1:
                self.miniters //= 2

        # Terminal Resize
        if now - self._last_term_check > 2.0:
            try:
                w = os.get_terminal_size().columns - 2
            except (OSError, AttributeError):
                w = 78
            if w != self._cached_width:
                self._rebuild_prefix(w)
            self._last_term_check = now

        # Math
        _finish = self.finish
        _ratio = progress / _finish if _finish > 0 else 0.0
        if _ratio > 1.0: _ratio = 1.0
        elif _ratio < 0.0: _ratio = 0.0

        _elapsed = now - self.start_time
        _speed = progress / _elapsed if _elapsed > 0.001 else 0.0

        # --- STEP 1: CALCULATE STATS FIRST (To know remaining space) ---
        if self.auto_bytes:
            _sz, _fsz = progress, _finish
            _ui, _uf = 0, 0
            while _sz >= 1024 and _ui < 8: _sz /= 1024; _ui += 1
            while _fsz >= 1024 and _uf < 8: _fsz /= 1024; _uf += 1
            _val_text = f"({_sz:>6.2f} {self.byte_units[_ui]}/{_fsz:>6.2f} {self.byte_units[_uf]})"
            
            _spz = _speed
            _us = 0
            while _spz >= 1024 and _us < 8: _spz /= 1024; _us += 1
            _spd_text = f" | {_spz:>6.2f} {self.byte_units[_us]}/s"
        else:
            _val_text = f"({int(progress)}/{int(_finish)})"
            _spd_text = f" | {_speed:>6.1f}{self.unit}/s"

        # Time Calc
        if _speed > 0.001:
            _eta = int((_finish - progress) / _speed)
            _eta_m, _eta_s = _eta // 60, _eta % 60
            _eta_str = f"{_eta_m:02d}:{_eta_s:02d}"
        else:
            _eta_str = "--:--"
            
        _el = int(_elapsed)
        _el_m, _el_s = _el // 60, _el % 60

        # Calculate VISUAL width of the stats (everything after the bar)
        # "] 99.99% (val) | 00:00 < 00:00 | speed"
        # We assume standard ASCII for stats so len() is fast and safe.
        # 2 = "] "
        # 7 = "99.99% "
        # 3 = " | "
        # 16 = "00:00 < 00:00 "
        # Plus the variable lengths of val_text and spd_text
        _stats_len = 2 + 7 + len(_val_text) + 16 + len(_spd_text)
        
        # --- STEP 2: CALCULATE DYNAMIC BAR LENGTH ---
        # Available = Total - Prefix - Stats
        _bar_len = self._cached_width - self._cached_prefix_len - _stats_len
        if _bar_len < 1: _bar_len = 1
        
        _wf = self._width_func

        # --- STEP 3: CONSTRUCT BAR ---
        if self._bar_fil: 
            if self._style_frames: 
                # SmoothStyle
                _total = _bar_len * _ratio
                _n = int(_total)
                _rem = _total - _n
                _fr = self._style_frames
                _mid = _fr[int(_rem * len(_fr))] if _n < _bar_len else ""
                _bar_str = (self._bar_fil * _n) + _mid + (self._bar_unfil * (_bar_len - _n - 1))
            else: 
                # Basic Style
                _avail = _bar_len - _wf(self._bar_end)
                if _avail < 0: _avail = 0
                _n = int(_avail * _ratio)
                _bar_str = (self._bar_fil * _n) + self._bar_end + (self._bar_unfil * int((_avail - _n) / max(1, _wf(self._bar_unfil))))
        else: 
            # Fun Style
            p = self._style_pattern
            self.ticks += 1
            if self.ticks >= p[self.current_frame_idx % len(p)]:
                self.current_frame_idx += 1
                self.ticks = 0
            idx = self.current_frame_idx
            _b_fils, _b_ends, _b_unfils = self._style_frames
            b_f = _b_fils[idx % len(_b_fils)]
            b_e = _b_ends[idx % len(_b_ends)]
            b_u = _b_unfils[idx % len(_b_unfils)]
            
            _avail = _bar_len - _wf(b_e)
            if _avail < 0: _avail = 0
            _n = int((_avail * _ratio) / _wf(b_f))
            _bar_str = (b_f * _n) + b_e + (b_u * int((_avail - (_n*_wf(b_f))) / _wf(b_u)))

        if len(_bar_str) < _bar_len: _bar_str += " " * (_bar_len - len(_bar_str))

        # --- FINAL ASSEMBLY ---
        _res = (
            f"{self._cached_prefix}{_bar_str}{self._c_rst}] "
            f"{self._c_ex}{(_ratio*100):>6.2f}% {_val_text} "
            f"| {_el_m:02d}:{_el_s:02d} < {_eta_str}"
            f"{_spd_text}{self._c_rst}"
        )
        
        self.past = f'\r\x1b[K{_res}'
        self._write(self.past)
        sys.stdout.flush()
        
        self.last_redrawn = now
        return self.past

    def __iter__(self):
        for i, item in enumerate(self.iterable):
            yield item
            self.update(i + 1)
        self._write(f"\n{self.comp}\n")

    def __enter__(self): return self
    def __exit__(self, t, v, tb):
        if not t:
            self._write(f"\n{self.comp}\n")