# `RustBar` Class Documentation

The `RustBar` class is a hybrid progress bar that uses a Rust backend to handle heavy progress calculation and formatting, while providing a clean, Pythonic API. It's the ultimate compromise between high-performance and rich visual aesthetics.

- **Python Source (Wrapper):** [`vibe_load/rust_wrapper.py`](../vibe_load/rust_wrapper.py)
- **Rust Source (Core):** [`src/lib.rs`](../src/lib.rs)

---

## 🏗 Rust Backend Engine

The core engine is implemented in Rust using standard libraries for high performance and minimal memory footprint. It manages the internal state of the progress bar, including time calculation, speed estimation, and bar rendering.

### `LoadBar` Struct (Rust)
The Rust engine maintains:
- `label`: String prefix.
- `finish`: Total items (as a float).
- `format_str`: The layout template.
- `ac_clr`, `br_clr`, `ex_clr`: ANSI color codes.
- `comp`: Completion message.
- `min_redraw`: Minimum time between redraws (defaulting to 0.1s or 0.3s).

---

## 🛠 Initialization

```python
from vibe_load import RustBar

pbar = RustBar(
    iterable=None, 
    label="STYLISH", 
    finish=None, 
    theme=None, 
    comp="Complete"
)
```

### Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `iterable` | `Iterable` | `None` | The object to iterate over. |
| `label` | `str` | `'STYLISH'` | The action text shown at the beginning. |
| `finish` | `int/float`| `None` | The total value for 100% completion. Derived from `len(iterable)` if possible. |
| `theme` | `Theme` | `None` | A `Theme` object for coloring. Defaults to white if `None`. |
| `comp` | `str` | `'Complete'` | Text printed when the progress is finished. |

---

## ⚡️ Performance & Gatekeeping

While the engine is written in Rust, calling into Rust from Python still has a small overhead. `RustBar` uses a **Gatekeeper** mechanism to ensure that the Python-to-Rust bridge is only crossed when necessary.

- **The Gate:** By default, `RustBar` only calls the Rust engine approximately **1000 times** throughout the entire lifecycle of the bar.
- **Throttling:** If you have 1,000,000 iterations, the bridge will only be crossed every 1,000 iterations.

---

## 🔧 Core Methods

### `update(n: float)`
Updates the internal progress. The gatekeeper decides whether to pass this value to the Rust backend.
- `n`: Current progress value.

### `finish()`
Manually triggers the completion message and final state synchronization with the Rust engine.

### `__iter__()`
Standard Python iterator support. Automatically handles `update` and `finish` calls.

---

## 📖 Usage Examples

### 1. Simple Iterator
```python
from vibe_load import RustBar
import time

for i in RustBar(range(1000), label="PROCESSING"):
    time.sleep(0.01)
```

### 2. Context Manager
```python
from vibe_load import RustBar
from vibe_load.themes import garden
import time

with RustBar(finish=5000, label="GARDENING", theme=garden) as rb:
    for i in range(5001):
        rb.update(i)
        time.sleep(0.001)
```

---

## 🛠 Building the Rust Engine

The `RustBar` requires the compiled Rust extension (`vibe_loadbar_rs`). If you are working on the source code, you can build it using `maturin`:

```sh
# Install maturin
pip install maturin

# Build and install locally
maturin develop
```

The extension exposes the `LoadBar` class to Python, which is then wrapped by the `RustBar` class in `vibe_load/rust_wrapper.py`.

---
Built with ❤️ by **Adam Hany**. Part of the **Vibe Suite**.
