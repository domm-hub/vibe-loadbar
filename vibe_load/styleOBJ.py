try:
    from .clr import Styler
except:
    from clr import Styler

class Style:
    """Basic static style (e.g., [===>---])."""
    def __init__(self, bar_fil, end, bar_unfil):
        self.bar_fil = bar_fil
        self.end = end
        self.bar_unfil = bar_unfil

class FunStyle:
    """Animated styles with rhythmic timing (pulsing/moving)."""
    def __init__(self, bar_fils, ends, bar_unfils, elapse_pattern=None):
        self.bar_fils = bar_fils
        self.ends = ends
        self.bar_unfils = bar_unfils
        self.elapse_pattern = elapse_pattern or [1]
        
class SmoothStyle:
    def __init__(self, bar_fil='█', bar_unfil=' ', frames=[' ', '▏', '▎', '▍', '▌', '▋', '▊', '▉']):
        self.bar_fil, self.bar_unfil = bar_fil, bar_unfil
        self.frames = frames
        
class Theme:
    def __init__(self, action_clr, bar_clr, et_clr):
        self.ac_clr = action_clr
        self.br_clr = bar_clr
        self.ex_clr = et_clr
        self.validate()
        
    def validate(self):
        t = 'm'
        for k, v in vars(self).items():
            if callable(v):
                continue
            if Styler().txt_style(v, t) is None:
                raise Exception('Invalid colour')
        