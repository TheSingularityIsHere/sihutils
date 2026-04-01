# sihutils

Utility helpers for SIH workflows.

## Installation

**Update to the latest commit:**
```python
!pip install --upgrade "sihutils @ git+https://github.com/TheSingularityIsHere/sihutils.git"
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
from etils.lazy_imports import *
import sihutils

# monitor GPU 0
if 'rows' not in globals(): rows = []
rows = sihutils.monitoring.loop(rows, gpu_index=0)
sihutils.monitoring.export(rows)

# render a script
sihutils.comfy.render_script(
    script='20260331_205938.json',
)
```

---

## License

[Apache 2.0](LICENSE)
