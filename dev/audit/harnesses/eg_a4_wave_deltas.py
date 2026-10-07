"""The report-only wave of the architecture score, re-measured (R9-EG-A4, #1774).

Each EG pull request of the report-only wave is scored with THIS tree's
``tools/audit/archscore`` on both sides: the parent on ``main`` against the
merge commit for a merged one, the merge base against the head for an open one.
One instrument for every row, so the rows compare with each other; a figure a
pull-request body printed was measured with the instrument at that time.

    python3 dev/audit/harnesses/eg_a4_wave_deltas.py [--only 1887,1958]

Prints one line per pull request: group, base and head (8 hex), dS, verdict
and the gate rises; then each changed metric. The review verdict each row is
compared with is the pull request's last ``Fix review:`` comment, read by hand
and written into the R9-EG-A4 body: no script parses a review's reasoning.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools" / "audit"))

from archscore import score, vector  # noqa: E402

# (pull request, group, base ref, head ref). A merged one is ``M^1`` against
# ``M``; an open one names its merge base and head explicitly.
WAVE = (
    (1839, "R9-EG-B2", "492d84011512e1240e45b5cb4cc5d931e0a046d1^1", "492d84011512e1240e45b5cb4cc5d931e0a046d1"),
    (1852, "R9-EG-B3a", "03ba7f70f007147bda32ac0fc5dd83b11499bbaf^1", "03ba7f70f007147bda32ac0fc5dd83b11499bbaf"),
    (1867, "R9-EG-B3b", "12dbd3a5d01f48f44e6c6344bff22d3d015baf9d^1", "12dbd3a5d01f48f44e6c6344bff22d3d015baf9d"),
    (1874, "R9-EG-A2", "697b8c68e7fa9d696ffe298b8f413ab9c503bb79^1", "697b8c68e7fa9d696ffe298b8f413ab9c503bb79"),
    (1887, "R9-EG-B1", "82d1f47f20c0557f6898f843960eaa64bb20cbfd^1", "82d1f47f20c0557f6898f843960eaa64bb20cbfd"),
    (1958, "R9-EG-A3", "b4287c517b910ffe2bca507c76ecf9e7196e00e1^1", "b4287c517b910ffe2bca507c76ecf9e7196e00e1"),
    (1966, "R9-EG-B6", "0aa61e7b72bc6f39fc43a1e74eed5e038d78d9f8^1", "0aa61e7b72bc6f39fc43a1e74eed5e038d78d9f8"),
    (2017, "R9-EG-B7", "b281a4c37e7cf91c79f205906418b2c6696d0e93^1", "b281a4c37e7cf91c79f205906418b2c6696d0e93"),
    (2025, "R9-EG-B11", "c327da7f176afa3d07acd5562b91f6042bb32809", "0dfb63a8c64950f062b047b4a8a49565a1c64f5f"),
)


def sha(ref: str) -> str:
    return subprocess.run(["git", "-C", str(REPO), "rev-parse", ref],
                          capture_output=True, text=True, check=True).stdout.strip()


def measure(ref: str, cache: dict) -> dict:
    key = sha(ref)
    if key not in cache:
        with tempfile.TemporaryDirectory(prefix="eg-a4-wave-") as tmp:
            cache[key] = vector.measure(score.tree_of(key, Path(tmp)))
    return cache[key]


def main(argv: list[str]) -> int:
    only = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
    cache: dict = {}
    for pr, group, base, head in WAVE:
        if only and str(pr) not in only:
            continue
        b, h = measure(base, cache), measure(head, cache)
        d = score.delta(b, h)
        print(f"#{pr} {group:10} {sha(base)[:8]}..{sha(head)[:8]} dS {d['dS']:+.4f} {d['verdict']:8} "
              f"rises: {'; '.join(d['rises']) or 'none'}", flush=True)
        for line in score.report(b, h).splitlines()[1:]:
            print(f"    {line.strip()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
