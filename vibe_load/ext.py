from .styleOBJ import *
from . import themes
from . import styles
from .err import *
import difflib

def is_style(obj):
    # Using a tuple of classes makes this a single check
    return isinstance(obj, (FunStyle, SmoothStyle, Style))

def find_style(name: str, silent=False):
    name = name.upper()
    style_map = vars(styles)

    # 1. Direct look-up is O(1) - much faster
    if name in style_map and is_style(style_map[name]):
        return style_map[name]
    
    # 2. Only run the loop/difflib if we actually need to raise an error
    if not silent:
        all_style_names = [k for k, v in style_map.items() if is_style(v)]
        match = difflib.get_close_matches(name, all_style_names, n=1)
        suggestion = f" Did you mean '{match[0]}?'" if match else ""
        raise NotFound(f"Style '{name}' not found.{suggestion}")
    
    return None

def find_theme(name: str, silent=False):
    name = name.lower()
    theme_map = vars(themes)
    
    # 1. Direct look-up (O(1) complexity)
    # Ensure we check if it's actually an instance of 'Theme'
    if name in theme_map and isinstance(theme_map[name], Theme):
        return theme_map[name]

    # 2. Error handling / Suggestions
    if not silent:
        # Filter for actual Theme objects in the module
        all_theme_names = [k for k, v in theme_map.items() if isinstance(v, Theme)]
        match = difflib.get_close_matches(name, all_theme_names, n=1)
        suggestion = f" Did you mean '{match[0]}?'" if match else ""
        raise NotFound(f"Theme '{name}' not found.{suggestion}")
    
    return None