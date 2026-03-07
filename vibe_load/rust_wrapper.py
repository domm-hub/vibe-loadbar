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
        # FIX: Rename 'self.finish' to 'self.total_items' to avoid name collision
        self.total_items = float(finish or (len(iterable) if iterable else 100))
        t = theme or Theme('white', 'white', 'white')
        
        # ⚡️ Gatekeeper: Only call Rust ~1000 times total
        self.gate = max(1, int(self.total_items // 1000)) 
        
        # Initialize Rust Engine with 8 Arguments
        self.engine = LoadBar(
            label, 
            self.total_items,  # Pass the float here
            "{action} {br1}{bar}{br2} {percent} {elapsed} | {speed}", 
            t.ac_clr, t.br_clr, t.ex_clr,
            str(comp),
            0.3
        )

    def update(self, n=1):
        self.n += n
        # Check gate using self.total_items
        if self.n % self.gate == 0 or self.n >= self.total_items:
            self.engine.update(float(self.n))

    def finish(self):
        """Manually call the Rust finish method."""
        self.engine.finish()

    def __iter__(self):
        if self.iterable is None: return
        for item in self.iterable:
            yield item
            self.update(1)
        self.finish()

    def __enter__(self): return self
    def __exit__(self, *args): self.finish()