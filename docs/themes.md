# `Theme` Documentation

The `Theme` class represents a color configuration for the **Vibe Suite**. It allows you to style the labels, the progress bar itself, and the extra metadata (percentage, ETA, speed, etc.) using ANSI escape codes.

- **Source:** [`vibe_load/styleOBJ.py`](../vibe_load/styleOBJ.py)
- **Predefined Themes:** [`vibe_load/themes.py`](../vibe_load/themes.py)

---

## 🛠 Initialization

```python
from vibe_load import Theme

my_theme = Theme(
    action_clr='blue', 
    bar_clr='green', 
    et_clr='yellow'
)
```

### Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `action_clr` | `str` | `None` | Color for the `action` label. |
| `bar_clr` | `str` | `None` | Color for the progress bar and brackets. |
| `et_clr` | `str` | `None` | Color for extra information (percentage, values, ETA, speed). |

---

## 🔧 Predefined Themes

Vibe Loader comes with a variety of built-in themes for different terminal backgrounds and aesthetics:

### 🌟 Top Picks
- `garden`: Blue label, Green bar, Yellow metadata.
- `cyberpunk`: Magenta label, Cyan bar, Yellow metadata.
- `royal`: Blue label, Magenta bar, White metadata.
- `blueprint`: Blue label, Cyan bar, White metadata.

### 🌓 Dark & Light
- `default`: White label, White bar, White metadata (classic look).
- `winter`: Blue label, Cyan bar, White metadata.

### ⚠️ Status Themes
- `emergency`: Red label, White bar, Black metadata.
- `status_ok`: Green label, Cyan bar, Blue metadata.
- `status_error`: Red label, Yellow bar, White metadata.

---

## 📖 Usage Examples

### 1. Using a Predefined Theme
```python
from vibe_load import Loading, themes
import time

# Use the garden theme
for i in Loading(range(100), theme=themes.garden):
    time.sleep(0.05)
```

### 2. Creating a Custom Theme
```python
from vibe_load import Loading, Theme
import time

# Create your own custom theme
custom = Theme(action_clr="red", bar_clr="magenta", et_clr="cyan")

for i in Loading(range(50), theme=custom):
    time.sleep(0.1)
```

### 3. Using Themes with `RustBar`
```python
from vibe_load import RustBar, themes
import time

# Themes are compatible with Rust-accelerated bars too!
with RustBar(range(1000), theme=themes.cyberpunk) as rb:
    for i in rb:
        time.sleep(0.01)
```

---

## 📐 The Styling Engine (`clr.py`)

The `Theme` class works in conjunction with `vibe_load/clr.py`, which is responsible for applying the ANSI escape codes. It supports basic colors (e.g., `red`, `green`, `blue`) and many more.

### Validation:
When a `Theme` is initialized, it automatically validates that the colors provided are supported by the `Styler` engine. If an invalid color is passed, an exception is raised.

---

## 🎨 Terminal Compatibility

All themes use standard ANSI escape codes, which are supported by most modern terminals (Windows Terminal, iTerm2, Kitty, Alacritty, GNOME Terminal, etc.). If you are using a very old terminal, colors may not display correctly, but the progress bar will still function as expected in plain text.

---
Built with ❤️ by **Adam Hany**. Part of the **Vibe Suite**.
