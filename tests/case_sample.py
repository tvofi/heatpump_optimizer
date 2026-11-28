#!/usr/bin/env python3
"""The seeded case sample a scoped pull request adds to its plan (R11-CI-CASE-SELECT P2, #3885).

    pick(ids, seed=<head sha>, fraction=FRACTION) -> the sampled subset of ids

A span is drawn when sha256(seed, id) falls under the fraction, so one head
draws the same spans on every run and every shard, and a new head draws
afresh. `tests/case_select.py` takes the union of the diff's spans and this
draw, then adds the producers each drawn span needs. A draw only adds spans
to a plan, so the fraction prices CI time and never decides soundness.
"""
from __future__ import annotations

import hashlib

# The share of the spans the diff does not reach that a pull request runs
# anyway, design 25fa1f76's 30%. Each head draws a different 30%, so a span
# the recorder under-scoped still runs on about one head in three.
FRACTION = 0.3


def pick(ids, *, seed: str, fraction: float = FRACTION) -> set[str]:
    """The ids whose sha256(seed, id) falls under `fraction`; none without a seed."""
    if not seed or fraction <= 0:
        return set()
    cut = int(fraction * 2 ** 64)
    return {i for i in ids
            if int.from_bytes(hashlib.sha256(f"{seed}\0{i}".encode()).digest()[:8], "big") < cut}
