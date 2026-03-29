# sihutils

Utility helpers for SIH workflows.

## Installation

**Update to the latest commit:**
```python
!pip install --quiet --upgrade "sihutils @ git+https://github.com/TheSingularityIsHere/sihutils.git"

from etils.lazy_imports import *
import sihutils
```

> **Tip:** To pin to a specific commit or tag, append `@<ref>` to the URL, e.g.:
> ```
> git+https://github.com/TheSingularityIsHere/sihutils.git@v0.1.0
> ```

> **Tip:** Edit files locally with hot-reloading:
> ```
> !ln -s $(dirname {sihutils.__file__}) /workspace/_sihutils
> %load_ext autoreload
> %autoreload 2
> ```

!ln -s $(dirname {sihutils.__file__}) /workspace/sihutils

## Synopsis

```python
if 'rows' not in globals(): rows = []
rows = sihutils.monitoring.loop(rows)
```

---

## License

[Apache 2.0](LICENSE)
