try:
    from .vibe_loadbar_rs import LoadBar
except ImportError:
    from vibe_loadbar_rs import LoadBar
    
try:
    from .styleOBJ import Theme
except ImportError:
    from styleOBJ import Theme

class RustBar:
    def __init__(self, iterable=None, label="STYLISH", finish=None, theme=None, comp="Complete"):
        self.iterable = iterable
        self.n = 0.0
        
        # Calculate total
        if finish is not None:
            self.total_items = float(finish)
        elif iterable is not None:
            self.total_items = float(len(iterable))
        else:
            self.total_items = 100.0

        t = theme or Theme('white', 'white', 'white')
        
        # Initialize Rust Engine
        self.engine = LoadBar(
            label, 
            self.total_items,
            "{action} {br1}{bar}{br2} {percent} {elapsed} | {speed}", 
            t.ac_clr, t.br_clr, t.ex_clr,
            str(comp),
            0.3
        )

    def update(self, n=1.0):
        # 1. Update the cumulative counter
        self.n += n
        if n % 2 < 0:
            return
        # 2. Pass the TOTAL progress to Rust
        # We don't need the gate because Rust handles 'miniters' internally now!
        self.engine.update(float(self.n))

    def finish(self):
        self.engine.finish()

    def __iter__(self):
        if self.iterable is None: return
        for item in self.iterable:
            yield item
            self.update(1.0) # This now correctly increments self.n
        self.finish()

    def __enter__(self): 
        return self
        
    def __exit__(self, *args): 
        self.finish()