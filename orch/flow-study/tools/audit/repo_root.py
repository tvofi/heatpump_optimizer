"""Repository root for an audit harness.

The root is the directory that holds
``custom_components/heatpump_optimizer/manifest.json``. Each harness inlines
``repo_root``; this module is the copy a test imports, and the two texts match.
"""
from __future__ import annotations

from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


def main() -> int:
    found = repo_root(Path(__file__))
    print(found)
    return 0 if (found / "custom_components/heatpump_optimizer/manifest.json").is_file() else 1


if __name__ == "__main__":
    raise SystemExit(main())
