# Vibe Loader Documentation Suite

Welcome to the **Vibe Loader** (vibe-loadbar) documentation hub. This project provides a set of highly customizable and performant progress bars for Python, ranging from feature-rich aesthetic bars to extreme performance-tuned implementations.

Vibe Loader is designed for developers who care about terminal aesthetics without sacrificing execution speed.

## 📦 Core Modules

The library is organized into three primary engines, each optimized for different use cases:

1.  **[Loading (Standard)](./loading.md)**: The original Vibe Loader engine. Features 100+ styles, full RGB/ANSI theme support, and dynamic terminal resizing. Best for user-facing applications where look and feel are paramount.
2.  **[MinLoad (Efficient)](./minload.md)**: A high-performance, minimalist engine. Specifically tuned to have lower overhead than `tqdm`, making it the choice for massive loops (millions of iterations).
3.  **[RustBar (Accelerated)](./rustbar.md)**: A hybrid engine that uses a Rust backend (`src/lib.rs`) to handle the heavy lifting of progress calculation and formatting while maintaining a clean Python API.

---

## 🎨 Styling & Theming

Aesthetics are at the heart of the Vibe Suite. I categorize my styles into three distinct types:

- **[Basic Styles](./styles_basic.md)**: Traditional character-based progress bars (e.g., `[===>---]`).
- **[Smooth Styles](./styles_smooth.md)**: High-resolution progress bars using Unicode block elements for sub-character precision (e.g., `[████▍   ]`).
- **[Fun Styles](./styles_fun.md)**: Animated and rhythmic progress bars that change character sets over time (e.g., pulsing hearts or scanning dots).
- **[Themes](./themes.md)**: Color configuration using the `Theme` class to style the label, the bar itself, and the metadata.

---

## 🛠 Project Architecture

The codebase is split between Python and Rust:

- **Python Source:** Located in [`vibe_load/`](../vibe_load/)
- **Rust Source:** Located in [`src/`](../src/)

### File Map
| File | Description |
| :--- | :--- |
| `vibe_load/main.py` | Implementation of the main `Loading` class. |
| `vibe_load/efficient.py` | Implementation of the `MinLoad` class. |
| `vibe_load/rust_wrapper.py` | Python wrapper for the Rust `LoadBar` engine. |
| `vibe_load/styles.py` | Repository of 100+ predefined style objects. |
| `vibe_load/themes.py` | Repository of predefined color themes. |
| `vibe_load/styleOBJ.py` | Class definitions for `Style`, `SmoothStyle`, `FunStyle`, and `Theme`. |
| `vibe_load/clr.py` | Internal ANSI styling engine. |
| `src/lib.rs` | Rust implementation for high-speed bar rendering. |

---

## 🚀 Quick Start

```python
from vibe_load import Loading, MinLoad, RustBar
import time

# For the looks:
for i in Loading(range(100), action="FETCHING"):
    time.sleep(0.05)

# For the speed:
for i in MinLoad(range(1000000)):
    pass

# For the best of both:
with RustBar(range(1000), label="STYLISH") as rb:
    for i in rb:
        time.sleep(0.01)
```

Check the individual documentation files for detailed API references and advanced configuration options.

---
Built with ❤️ by **Adam Hany**. Part of the **Vibe Suite**.
