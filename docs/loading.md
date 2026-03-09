# `Loading` Class Documentation

The `Loading` class is the original, flagship progress bar in the **Vibe Suite**. It provides a rich set of features including 100+ style options, dynamic terminal resizing, and support for complex theme objects.

- **Source:** [`vibe_load/main.py`](../vibe_load/main.py)

---

## 🛠 Initialization

```python
from vibe_load import Loading

pbar = Loading(
    iterable=None, 
    style=None, 
    bar_fil="-", 
    end='>', 
    bar_unfil='-',
    action='CHILLING', 
    comp='Complete', 
    finish=100, 
    loading=True,
    unit='', 
    margin=1, 
    auto_bytes=False,
    format_str=("{margin} {action} {br1}{bar}{br2} "
                "{percent}% {values} {sep} {elapsed} {com} {eta} {speed}"),
    print_cli=True, 
    theme=None, 
    wfunc=wcswidth
)
```

### Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `iterable` | `Iterable` | `None` | The object to iterate over. If provided, `finish` is automatically set to `len(iterable)`. |
| `style` | `Style/SmoothStyle/FunStyle` | `None` | A style object from `vibe_load.styles`. Overrides `bar_fil`, `end`, and `bar_unfil`. |
| `bar_fil` | `str` | `"-"` | Character used for the filled part of the bar (if `style` is `None`). |
| `end` | `str` | `">"` | Character used for the "head" or tip of the bar. |
| `bar_unfil` | `str` | `"-"` | Character used for the unfilled part of the bar. |
| `action` | `str` | `'CHILLING'` | The label displayed at the start of the bar. |
| `comp` | `str` | `'Complete'` | Text printed when the progress is finished. |
| `finish` | `int` | `100` | The target value for 100% progress. |
| `loading` | `bool` | `True` | Internal state flag to enable rendering. |
| `unit` | `str` | `''` | Unit label for the speed (e.g., `"/s"`, `"it/s"`). |
| `margin` | `int` | `1` | Leading whitespace before the progress bar. |
| `auto_bytes` | `bool` | `False` | Automatically format progress and speed values into human-readable bytes (KB, MB, etc.). |
| `format_str` | `str` | *(Long)* | Python format string for the entire bar line. Allows reordering of elements. |
| `print_cli` | `bool` | `True` | Set to `False` to suppress printing to `stdout`. |
| `theme` | `Theme` | `None` | A `Theme` object for coloring. See `vibe_load.themes`. |
| `wfunc` | `Callable` | `wcswidth` | Function to calculate visual character width (critical for Unicode/Emojis). |

---

## 🔧 Key Methods

### `update(progress: float, widtha: float = None)`
Manually triggers a progress bar update.
- `progress`: Current completion value.
- `widtha`: Optional manual override for terminal width.

### `write(txt: str)`
Writes text to the terminal above the current progress bar, properly handling line breaks to avoid visual corruption.

### `__iter__()`
Allows the object to be used in a standard `for` loop. The bar updates automatically as you iterate.

---

## 📖 Usage Examples

### 1. Simple Iterator
```python
from vibe_load import Loading
import time

# Automatically calculates length from the list
for i in Loading(range(100), action="SYNCING"):
    time.sleep(0.01)
```

### 2. Context Manager (Manual Control)
Useful for tasks where you don't have a direct iterable, like reading a file or a network stream.
```python
from vibe_load import Loading
import time

with Loading(finish=500, action="UPLOADING", auto_bytes=True) as pbar:
    for i in range(0, 501, 50):
        pbar.update(i)
        time.sleep(0.1)
```

### 3. Custom Styling & Themes
```python
from vibe_load import Loading, styles, themes
import time

for i in Loading(range(50), style=styles.SNAKE, theme=themes.cyberpunk):
    time.sleep(0.1)
```

---

## 🎨 Layout Formatting

The `format_str` parameter allows you to completely redesign the output line. Available placeholders:
- `{margin}`: Leading spaces.
- `{action}`: The label text.
- `{br1}` / `{br2}`: Brackets surrounding the bar.
- `{bar}`: The visual progress bar itself.
- `{percent}`: Percentage string (e.g., ` 45.00%`).
- `{values}`: Current/Total (e.g., `(45/100)`).
- `{sep}`: Separator character.
- `{elapsed}`: Time elapsed.
- `{eta}`: Estimated time of arrival.
- `{speed}`: Iterations or bytes per second.

---
Built with ❤️ by **Adam Hany**. Part of the **Vibe Suite**.

---
[« Back to Home](./README.md)
