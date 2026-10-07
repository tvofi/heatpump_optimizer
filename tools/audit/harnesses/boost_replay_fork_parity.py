"""tests/boost_drift_replay.py's shared pre-boost prefix equals the unshared replay.

The replay solves the cycles before the first boost window once and continues
every arm from a deep copy of that state (``replay``'s default fork). This
harness replays a shortened schedule both ways -- ``fork=0``, every arm from
its own fresh start, against the default fork -- and requires each arm's
summary to be identical: the daily scale rows, the fold counts, the final
scale, and every accuracy sample's stored form (actual and predicted
temperature per cycle, so the true house's trajectory is in the comparison).

Its null control breaks the precondition the fork rests on: the first window
opens one cycle before the forced fork, so the channel and mode arms lose
their first boosting cycle to the shared surface-free prefix. That arm must
report DIFFERS; if it reads PARITY the comparison is blind.

    PYTHONPATH=tests/hastub:tests:custom_components \\
        python3 tools/audit/harnesses/boost_replay_fork_parity.py

About seventy production solves; it is a harness, not a gate script.
"""
from __future__ import annotations

import sys

import boost_drift_replay as bdr

ARMS = {"null_no_boost": "none", "channel_boost": "channel",
        "mode_boost": "mode"}


def comparable(out: dict) -> dict:
    return {
        k: ([s.as_dict() for s in v] if k in ("tagged", "untagged") else v)
        for k, v in out.items()
    }


def compare(label: str, fork: int | None) -> bool:
    plain = bdr.replay(ARMS, fork=0)
    shared = bdr.replay(ARMS, fork=fork)
    same = all(comparable(plain[a]) == comparable(shared[a]) for a in ARMS)
    for a in ARMS:
        print(f"  {label} {a}: tagged={len(plain[a]['tagged'])} "
              f"untagged={len(plain[a]['untagged'])} "
              f"folds_outside={plain[a]['folds_outside']} "
              f"{'equal' if comparable(plain[a]) == comparable(shared[a]) else 'DIFFERENT'}")
    print(f"{label}: {'PARITY' if same else 'DIFFERS'} "
          f"(fork={bdr.fork_cycle() if fork is None else fork})")
    return same


def main() -> int:
    # Eight half-hour cycles from midnight on day 0: one window opening at
    # 00:30, so the default fork is cycle 1 and the window spans cycles 1-4.
    bdr.DAYS = 8 * bdr.DT_MIN / (24 * 60)
    bdr.BOOST_DAYS = (0,)
    bdr.BOOST_STARTS = (0.5,)
    real = compare("fork", None)
    # Null control: force the fork past the first boosting cycle.
    control = compare("control", bdr.fork_cycle() + 1)
    ok = real and not control
    print("BOOST REPLAY FORK PARITY " + ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
