# Vibe Loader

# New! 

### **Rust**
Have the visuals of `Loading()`, with the speed of **TQDM**


![Vibe Demo](demos.gif)

**Vibe Loader** is a lightweight alternative to TQDM, written in **under 800 lines** of `code`. It uses an event-based function called `update` to refresh values dynamically.

## Features
- **100+ Styles:** Passed directly into the `Loading` object.
- **Zero Dependencies:** No foreign packages required.
- **MARGIN Support:** Optimized for small terminals to prevent layout breaking.
- **Dynamic Resizing:** Automatically adjusts to terminal width.
- **Stream Support:** Compatible with request streams.
- **Context Manager:** Supports `with` statements for easy lifecycle management.
- **Developer Friendly:** All variables are public and changeable, plus support for custom styles.

## Performance
**The new `MinLoad` is faster than tqdm.**

| Library | Total Time | Iterations/sec | Speed Factor |
| :--- | :--- | :--- | :--- |
| **MinLoad** | **0.0989s** | **5,063,945 it/s** | **1.45x Faster** |
| `tqdm` | 0.1436s | 4,320,390 it/s | 1.00x (Baseline) |
| `RustBar` (Rust) | 0.1480s | 3,490,749 it/s | 0.97x |
| `Loading` (Legacy) | 0.5197s | 962,297 it/s | 0.28x |

[![MinLoad Speed](https://img.shields.io/badge/MinLoad-1.45x_Faster_than_tqdm-brightgreen?style=for-the-badge&logo=python)](https://github.com/domm-hub/vibe-loadbar)
> *Test Conditions: Measured over 500,000 iterations on a standard Python loop.*

`MinLoad()` is better than `Loading()` in speed, `Loading()` is better for aesthetics.
`RustBar()` (Rust) gives you the best of both worlds: high performance with rich visuals.

---


## Installation from PyPi.
```sh
pip install vibe-loadbar
```

## Installation from `Github`. **(For latest updates.)**
### Note: Cutting Edge updates might have errors or be unstable.
```sh
pip install git+https://github.com/domm-hub/vibe-loadbar
```


### Example Usage for Loading:
~~~python
from vibe_load import Loading, SmoothStyle
from vibe_load.themes import garden
import time

for i in Loading(range(1000), style=SmoothStyle(), theme=garden):
    time.sleep(0.01)

with Loading(range(1000), style=SmoothStyle()) as pbar:
    for i in pbar:
        time.sleep(0.01)
    
#These loops should take ~10 seconds
~~~


### Example Usage for MinLoad:
~~~python
from vibe_load import MinLoad
import time

for i in MinLoad(range(1000)):
    time.sleep(0.01)

with MinLoad(range(1000)) as pbar:
    for i in pbar:
        time.sleep(0.01)
~~~

### Links
Check out the repository here: [vibe-loadbar on GitHub](https://www.github.com/domm-hub/vibe-loadbar)

PyPi Module link: [vibe-loadbar on PyPI](https://pypi.org/project/vibe-loadbar)
---
Built with ❤️ by **Adam Hany**. Part of the **Vibe Suite**.