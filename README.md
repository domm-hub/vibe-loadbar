# Vibe Loader

![Vibe Demo](demos.gif)

**Vibe Loader** is a lightweight alternative to TQDM, written in less than 250 lines of code. It uses an event-based function called `update` to refresh values dynamically.

## Features
- **100+ Styles:** Passed directly into the `Loading` object.
- **Zero Dependencies:** No foreign packages required.
- **MARGIN Support:** Optimized for small terminals to prevent layout breaking.
- **Dynamic Resizing:** Automatically adjusts to terminal width.
- **Stream Support:** Compatible with request streams.
- **Context Manager:** Supports `with` statements for easy lifecycle management.
- **Developer Friendly:** All variables are public and changeable, plus support for custom styles.

## Performance
**The new minload is faster than tqdm.**
| Library | Overhead Cost (Lower is Better) | Speed Factor | Efficiency |
| :--- | :--- | :--- | :--- |
| **`vibe-loadbar` (MinLoad)** | **0.0995s**  | **1.76x Faster** | **High** |
| `tqdm` (Standard) | 0.1930s | 1.00x (Baseline) | Moderate |



[![MinLoad Speed](https://img.shields.io/badge/MinLoad-1.76x_Faster_than_tqdm-brightgreen?style=for-the-badge&logo=python)](https://github.com/domm-hub/vibe-loadbar)
> *Test Conditions: Measured as pure overhead (Total Time - Raw Loop Time) on a standard Python loop.*

`MinLoad()` is better than `Loading()` in speed, `Loading()` is better for aesthetics.

---


## Installation from PyPi.
```sh
pip install vibe-loadbar
```

## Installation from Github. **(For latest updates.)**
### Note: Cutting Edge updates might have errors or be unstable.
```sh
pip install -e git+https://github.com/domm-hub/vibe-loadbar
```


### Example Usage for Loading:
~~~python
from vibe_load import Loading, SmoothStyle
import time

for i in Loading(range(100), style=SmoothStyle()):
    time.sleep(0.1)

with Loading(range(100), style=SmoothStyle()) as pbar:
    for i in pbar:
        time.sleep(0.1)
    
#These loops should take ~10 seconds
~~~


### Example Usage for MinLoad:
~~~python
from vibe_load import MinLoad
import time

for i in MinLoad(range(100)):
    time.sleep(0.01)

with MinLoad(range(100)) as pbar:
    for i in pbar:
        time.sleep(0.1)
~~~

### Links
Check out the repository here: [vibe-loadbar on GitHub](https://www.github.com/domm-hub/vibe-loadbar)