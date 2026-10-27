"""R10-ARCH-SHAPES census: which golden scenarios put a plan step in the D8-s1-01 band, per last-ulp nudge.

D8-s1-01's classifier arm makes a channel idle on a step where its own draw is
above ``optimizer.CHANNEL_ACTIVE_KW`` and the step's whole ask (space plus
DHW) is not above ``thermal_model.MIN_RUNNING_DRAW_KW``: "the band". A golden
fixture moves under that arm only if its solve emits a band step, and whether
it does is a property of the solve's basin, not of the diff. This harness
measures that by #996's R4-RC-01 technique: it nudges one price (index n//3)
by a relative ``eps`` and counts band steps per scenario per ``eps``. ``eps``
0 is the unperturbed control, whose non-may-drift band set must equal this
host's own ``env_drift.py --all`` movers for the classifier arm.

A scenario with a band step under ANY nudge is "susceptible": some host can
see it move. The union is a lower bound on the hosts' union, not a closed set
(a scenario a runner moved can read 0 at every nudge here).

The power series are read off ``classify_space_steps``'s own inputs, so the
counts are the same at a tree with or without the arm: the solve is unchanged.

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_band_census.py [scenario ...]

Prints one line per scenario, then ``RESULT scenarios=.. susceptible=..
failures=..`` and a ``SUSCEPTIBLE`` name list. Cost: about 25 min for every
scenario on an Apple M-class laptop (four captures each).
"""
from __future__ import annotations

import sys
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


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))

import numpy as np  # noqa: E402

import golden  # noqa: E402
from heatpump_optimizer import optimizer as opt  # noqa: E402
from heatpump_optimizer import thermal_model as tm  # noqa: E402

EPS = (0.0, 1e-15, 1e-12, 1e-9)
_make = golden.make
_classify = opt.classify_space_steps
_state: dict = {"eps": 0.0, "calls": []}


def _nudged_make(**kw):
    built = _make(**kw)
    prices = np.array(built["prices"], dtype=float)
    k = len(prices) // 3
    prices[k] = prices[k] * (1.0 + _state["eps"]) if prices[k] else _state["eps"]
    built["prices"] = prices
    return built


def _spy(power, *args, **kwargs):
    other = kwargs.get("other")
    _state["calls"].append(
        (np.array(power, float), None if other is None else np.array(other, float))
    )
    return _classify(power, *args, **kwargs)


def band_steps(space: np.ndarray, dhw: np.ndarray | None) -> int:
    """Channel steps over the channel line on a step the plan calls off."""
    if dhw is None or len(dhw) == 0:
        dhw = np.zeros_like(space)
    dhw = np.resize(dhw, space.shape)
    off = (space + dhw) <= tm.MIN_RUNNING_DRAW_KW
    line = opt.CHANNEL_ACTIVE_KW
    return int(np.sum(off & (space > line)) + np.sum(off & (dhw > line)))


def main(names: list[str]) -> int:
    golden.make = _nudged_make
    opt.classify_space_steps = _spy
    union: list[str] = []
    failures = 0
    for name in names:
        counts: list = []
        for eps in EPS:
            _state["eps"], _state["calls"] = eps, []
            try:
                golden.capture(name, golden.SCENARIOS[name])
                counts.append(sum(band_steps(s, d) for s, d in _state["calls"]))
            except Exception as exc:  # a failed capture is counted, never a zero
                failures += 1
                counts.append(f"ERR:{type(exc).__name__}")
        hit = any(isinstance(c, int) and c > 0 for c in counts)
        if hit:
            union.append(name)
        print(f"{name}: band_steps_per_eps={dict(zip(EPS, counts))} susceptible={hit}", flush=True)
    print(f"RESULT scenarios={len(names)} susceptible={len(union)} failures={failures}")
    print("SUSCEPTIBLE " + " ".join(union))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or sorted(golden.SCENARIOS)))
