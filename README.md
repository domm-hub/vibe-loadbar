# Vibe Loader

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
The new `MinLoad` class is faster than `tqdm` in most tasks.

| Candidate | Time (s) | IT/s | Overhead |
| :--- | :--- | :--- | :--- |
| **Baseline** | 0.0022 | 45,207,098 | +0.0% |
| **tqdm** | 0.0474 | 2,109,886 | +2,042.6% |
| **MinLoad** | 0.0377 | 2,651,187 | +1,605.2% |

---

### Links
Check out the repository here: [vibe-loadbar on GitHub](https://www.github.com/domm-hub/vibe-loadbar)