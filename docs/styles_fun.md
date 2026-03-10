# `FunStyle` (Animated) Documentation

`FunStyle` represents an animated progress bar with rhythmic timing. Unlike static styles, `FunStyle` cycles through different character sets over time, creating a "pulsing" or "moving" effect in the terminal.

- **Source:** [`vibe_load/styleOBJ.py`](../vibe_load/styleOBJ.py)
- **Predefined Styles:** [`vibe_load/styles.py`](../vibe_load/styles.py)

---

## 🛠 Initialization

```python
from vibe_load import FunStyle

my_fun_style = FunStyle(
    bar_fils=['❤', '💖', '💗', '💓'],
    ends=[' ', '·', ' ', '·'],
    bar_unfils=[' '],
    elapse_pattern=[2.5, 5, 2.5, 25]
)
```

### Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `bar_fils` | `list[str]` | `None` | A list of characters for the filled part of the bar. The engine cycles through these. |
| `ends` | `list[str]` | `None` | A list of characters for the "head" or tip of the bar. |
| `bar_unfils` | `list[str]` | `None` | A list of characters for the unfilled part of the bar. |
| `elapse_pattern`| `list[float]`| `[1]` | A list of durations (in ticks) for each frame in the animation cycle. |
| `br1` | `str` | `"("` | Bracket one for the bar.
| `br2` | `str` | `")"` | Bracket two for the bar.

---

## 🔧 Predefined Fun Styles

Vibe Loader comes with several unique animated styles:

### 💓 `HEARTBEAT`
A pulsing heart animation.
- **Fils:** `['❤', '💖', '💗', '💓']`
- **Pattern:** Quick pulse followed by a long pause.

### 📡 `PULSE`
A scanning dot animation.
- **Ends:** `['.', '..', '...', '..', '.']`
- **Pattern:** Smooth expansion and contraction of the "head" character.

### 🐱 `SPIN_CAT` (Abstract)
A floating cat moving through the void.
- **Ends:** `['🐱']`
- **Unfils:** `[' ']`

---

## 📖 Usage Examples

### 1. Using a Predefined Style
```python
from vibe_load import Loading, styles
import time

# Use the HEARTBEAT style
for i in Loading(range(100), style=styles.HEARTBEAT):
    time.sleep(0.05)
```

### 2. Creating a Custom Animation
```python
from vibe_load import Loading, FunStyle
import time

# Create a custom "loading" animation
custom_anim = FunStyle(
    bar_fils=["|", "/", "-", "\\"],
    ends=[">"],
    bar_unfils=["."],
    elapse_pattern=[2, 2, 2, 2]
)

for i in Loading(range(50), style=custom_anim):
    time.sleep(0.1)
```

---

## 📐 The Animation Engine

The `Loading` class maintains internal state for `FunStyle` animations:
- `ticks`: Incremented on every render call.
- `current_frame_idx`: Incremented when `ticks` reaches the value defined in `elapse_pattern`.

### Timing Logic:
```python
if self.ticks >= p[self.current_frame_idx % len(p)]:
    self.current_frame_idx += 1
    self.ticks = 0
self.ticks += 1
```

This logic allows for non-uniform animation speeds. For example, a "glitch" effect might have some frames that last only 1 tick and others that last 50 ticks.

---
Built with ❤️ by **Adam Hany**. Part of the **Vibe Suite**.

---
[« Back to Home](./README.md)
