# `SmoothStyle` Documentation

`SmoothStyle` represents a high-resolution progress bar that uses Unicode block elements for sub-character precision. This allows for a much smoother visual transition compared to standard character-based bars.

- **Source:** [`vibe_load/styleOBJ.py`](../vibe_load/styleOBJ.py)
- **Predefined Styles:** [`vibe_load/styles.py`](../vibe_load/styles.py)

---

## 🛠 Initialization

```python
from vibe_load import SmoothStyle

my_smooth_style = SmoothStyle(
    bar_fil='█', 
    bar_unfil=' ', 
    frames=[' ', '▏', '▎', '▍', '▌', '▋', '▊', '▉']
)
```

### Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `bar_fil` | `str` | `'█'` | Character used for the fully filled part of the bar. |
| `bar_unfil` | `str` | `' '` | Character used for the unfilled part of the bar. |
| `frames` | `list` | `[' ', '▏', '▎', '▍', '▌', '▋', '▊', '▉']` | List of Unicode characters for sub-character precision. |

---

## 🔧 Predefined Smooth Styles

Vibe Loader comes with a single predefined smooth style by default:

- `SMOOTH`: `█` for fill, ` ` for unfill, and a full set of 8 Unicode block elements for the sub-character frame.

---

## 📖 Usage Examples

### 1. Using a Predefined Style
```python
from vibe_load import Loading, styles
import time

# Use the SMOOTH style
for i in Loading(range(100), style=styles.SMOOTH):
    time.sleep(0.05)
```

### 2. Creating a Custom Smooth Style
```python
from vibe_load import Loading, SmoothStyle
import time

# Create your own custom smooth style
custom_smooth = SmoothStyle(bar_fil="*", bar_unfil=".", frames=["-", "+"])

for i in Loading(range(50), style=custom_smooth):
    time.sleep(0.1)
```

---

## 📐 How it Works

The `Loading` class uses these characters to construct the progress bar line by line. It calculates the terminal width and allocates space for the label, percentage, and metadata first. The remaining space is filled by the progress bar using a combination of `bar_fil`, `frames`, and `bar_unfil`.

1.  **Full Blocks:** Calculated by multiplying the bar length by the completion ratio.
2.  **Sub-Character Frame:** The decimal part of the completion ratio is mapped to one of the characters in the `frames` list.
3.  **Unfilled Space:** The remaining space is filled with `bar_unfil` characters.

This technique provides a more granular visual feedback, especially useful for slow-moving tasks or high-precision progress tracking.

---
Built with ❤️ by **Adam Hany**. Part of the **Vibe Suite**.

---
[« Back to Home](./README.md)
