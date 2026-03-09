# `Style` (Basic) Documentation

The `Style` class represents a basic, character-based progress bar. It's the most widely used style in the **Vibe Suite** and provides a classic terminal look.

- **Source:** [`vibe_load/styleOBJ.py`](../vibe_load/styleOBJ.py)
- **Predefined Styles:** [`vibe_load/styles.py`](../vibe_load/styles.py)

---

## 🛠 Initialization

```python
from vibe_load import Style

my_style = Style(
    bar_fil='=', 
    end='>', 
    bar_unfil='-'
)
```

### Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `bar_fil` | `str` | `None` | Character used for the filled part of the bar. |
| `end` | `str` | `None` | Character used for the "head" or tip of the bar. |
| `bar_unfil` | `str` | `None` | Character used for the unfilled part of the bar. |

---

## 🔧 Predefined Basic Styles

Vibe Loader comes with 100+ predefined styles. Here are some of the most popular ones grouped by category:

### 🐍 The Snake Pit
- `SNAKE`: `~` for fill, `>` for end, `-` for unfill.
- `ANACONDA`: `=` for fill, `O` for end, ` ` for unfill.
- `PYTHON`: `s` for fill, `S` for end, `.` for unfill.
- `NEON_SNAKE`: `━` for fill, `>` for end, ` ` for unfill.

### 🏛 The Classics
- `BLOCK`: `█` for fill, `█` for end, `░` for unfill.
- `HASH`: `#` for fill, `#` for end, `.` for unfill.
- `PIPE`: `┃` for fill, `┃` for end, `│` for unfill.
- `BRICK`: `■` for fill, `■` for end, `□` for unfill.

### 🎮 Gamer & Tech
- `RETRO`: `▰` for fill, `▰` for end, `▱` for unfill.
- `CYBER`: `⚡` for fill, `⚡` for end, `─` for unfill.
- `ROCKET`: `━` for fill, `🚀` for end, ` ` for unfill.
- `GHOST`: `👻` for fill, `👻` for end, ` ` for unfill.

---

## 📖 Usage Examples

### 1. Using a Predefined Style
```python
from vibe_load import Loading, styles
import time

# Use the SNAKE style
for i in Loading(range(100), style=styles.SNAKE):
    time.sleep(0.05)
```

### 2. Creating a Custom Style
```python
from vibe_load import Loading, Style
import time

# Create your own custom style
custom = Style(bar_fil="*", end="!", bar_unfil=".")

for i in Loading(range(50), style=custom):
    time.sleep(0.1)
```

---

## 📐 How it Works

The `Loading` class uses these characters to construct the progress bar line by line. It calculates the terminal width and allocates space for the label, percentage, and metadata first. The remaining space is filled by the progress bar using a combination of `bar_fil`, `end`, and `bar_unfil`.

1.  **Fill String:** Repeated `bar_fil` characters based on completion ratio.
2.  **End Character:** Placed immediately after the filled portion.
3.  **Unfill String:** Repeated `bar_unfil` characters to fill the rest of the available bar space.

---
Built with ❤️ by **Adam Hany**. Part of the **Vibe Suite**.

---
[« Back to Home](./README.md)
