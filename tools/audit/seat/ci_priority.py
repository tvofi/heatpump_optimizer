#!/usr/bin/env python3
"""The CI-priority tier rule: one function says which tier a pull request is in.

    python3 tools/audit/seat/ci_priority.py --self-test

Owner rulings (tvofi 2026-10-28, P267/P268; 2026-11-11, P652): the account's
runner limit is shared by one order, main push > critical path or hotfix or
outside > production or major-saving > instrument, and no pull request of the
first two tiers waits in the CI queue behind a lower one. Three instruments
read the order and none keeps its own: the merge train's pause (`ci_pause.py`),
the beat's cancel sweep (`tools/pr/cancel_superseded.py`) and the tick's owed
lines (`orchestrator_tick.py`).

`dev/audit/config/ci_priority.json` holds the tier order and the knobs ONLY. The
group-to-tier mapping is read from the roster through `roster_lib` (`is_hotfix`,
`is_outside`, `savings_h`, `group_class`) in `tier()`, the one class rule: a
setting file that keys data by group is refused naming the key.

Floor refusals (`check_setting`): the order names exactly the four tiers, the
pause and cancel guards keep their structural members (a setting that dropped
`main-push` or `cp-hotfix` from `never_cancel` would let the sweep cancel the
runs the rule exists to protect), and every knob has its type.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import roster_lib as rl  # noqa: E402

CONFIG = ROOT / "dev" / "audit" / "config" / "ci_priority.json"
TIERS = ("main-push", "cp-hotfix", "tier1", "instrument")
GUARDS = ("train-head",)  # structural: a train head is never paused whatever its tier
TIEBREAKS = ("cp-rank", "savings-desc", "train-position", "age")
KEYS = {"_comment": str, "order": list, "major_savings_h": (int, float), "tiebreak": list,
        "never_pause": list, "never_cancel": list, "pause_queued_min": (int, float),
        "pause_gap_min": (int, float), "priority_cancel": bool}
FLOOR_PAUSE = ("main-push", "cp-hotfix", "train-head")
FLOOR_CANCEL = ("main-push", "cp-hotfix")


class SettingError(ValueError):
    """The setting file is not one the rule can run on; the message names the key."""


def check_setting(s) -> dict:
    """The setting, or SettingError naming the key that refused it."""
    if not isinstance(s, dict):
        raise SettingError("setting is not an object")
    for k, v in s.items():
        if k not in KEYS:
            raise SettingError(f"{k}: not a knob (group-keyed data belongs in the roster, read "
                               "through roster_lib)" + (" -- a map" if isinstance(v, dict) else ""))
        if (isinstance(v, bool) and KEYS[k] is not bool) or not isinstance(v, KEYS[k]):
            raise SettingError(f"{k}: wrong type {type(v).__name__}")
        if isinstance(v, dict):
            raise SettingError(f"{k}: a map is refused")
    for k in KEYS:
        if k != "_comment" and k not in s:
            raise SettingError(f"{k}: missing")
    if sorted(s["order"]) != sorted(TIERS):
        raise SettingError(f"order: must name exactly {list(TIERS)}")
    if s["order"][0] != "main-push":
        raise SettingError("order: main-push must lead")
    if sorted(s["tiebreak"]) != sorted(TIEBREAKS):
        raise SettingError(f"tiebreak: must name exactly {list(TIEBREAKS)}")
    for key, floor in (("never_pause", FLOOR_PAUSE), ("never_cancel", FLOOR_CANCEL)):
        missing = [x for x in floor if x not in s[key]]
        if missing:
            raise SettingError(f"{key}: floor members {missing} may not be dropped")
        unknown = [x for x in s[key] if x not in TIERS + GUARDS]
        if unknown:
            raise SettingError(f"{key}: unknown tier {unknown}")
    if s["major_savings_h"] <= 0:
        raise SettingError("major_savings_h: must be positive")
    return s


def load_setting(path: "Path | str | None" = None) -> dict:
    p = Path(path) if path else CONFIG
    try:
        return check_setting(json.loads(p.read_text()))
    except (OSError, ValueError) as e:
        if isinstance(e, SettingError):
            raise
        raise SettingError(f"{p}: unreadable: {e}") from e


def _group(roster: dict, group) -> "dict | None":
    if not group:
        return None
    return next((x for x in (roster or {}).get("groups", []) if x.get("group") == group), None)


def tier(group, crit, roster: dict, setting: dict, *, touches_production: bool = False) -> str:
    """The tier of the group `group` (a roster group id, or None for a pull request
    that maps to no group). `crit` is a set of `roster_lib.norm_group` ids.

    cp-hotfix = on the critical path, a hotfix, or an accepted outside group (owner
    rulings tvofi 2026-11-07/-08: outside ranks with the critical path);
    tier1 = group_class production or savings_h at or above the setting's
    major_savings_h; instrument = the rest. A group-less pull request is tier1
    when its three-dot diff touches custom_components/ (`touches_production`),
    else instrument."""
    g = _group(roster, group)
    if g is None:
        return "tier1" if touches_production else "instrument"
    if rl.norm_group(str(group)) in (crit or ()) or rl.is_hotfix(g) or rl.is_outside(g):
        return "cp-hotfix"
    sv = rl.savings_h(g)
    if rl.group_class(g) == "production" or (sv is not None and sv >= setting["major_savings_h"]):
        return "tier1"
    return "instrument"


def rank(group, crit, roster: dict, setting: dict, *, touches_production: bool = False,
         position: int = 0, age_s: float = 0.0) -> tuple:
    """Sort key, best first: the tier's place in the setting's order, then the
    setting's tiebreaks in order (cp-rank, savings descending, train position,
    older first)."""
    t = tier(group, crit, roster, setting, touches_production=touches_production)
    g = _group(roster, group)
    # cp-rank: a hotfix first, then the critical path and outside groups unordered between
    # them (owner rulings tvofi 2026-11-07/-08), then the rest.
    cp = (0 if g is not None and rl.is_hotfix(g) else
          1 if (g is not None and rl.is_outside(g)) or rl.norm_group(str(group or "")) in (crit or ()) else 2)
    parts = {"cp-rank": cp,
             "savings-desc": -(rl.savings_h(g) or 0) if g else 0,
             "train-position": position, "age": -age_s}
    return (setting["order"].index(t),) + tuple(parts[k] for k in setting["tiebreak"])


def is_priority(t: str, setting: dict) -> bool:
    """A tier whose queued runs are never cancelled or held (`never_cancel`)."""
    return t in setting["never_cancel"]


def may_pause(t: str, setting: dict, *, train_head: bool = False) -> bool:
    """False for any `never_pause` tier and for the train head, a structural guard."""
    return not (t in setting["never_pause"] or (train_head and "train-head" in setting["never_pause"]))


def _self_test() -> int:
    n = bad = 0

    def check(label, ok):
        nonlocal n, bad
        n += 1
        bad += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")
    S = load_setting()
    R = {"groups": [
        {"group": "CP", "class": "instrument"}, {"group": "HF", "hotfix": True},
        {"group": "R10-HOTFIX-X"}, {"group": "OUT", "source": "outside"},
        {"group": "PROD", "class": "production"}, {"group": "BIG", "class": "instrument", "savings": 14},
        {"group": "SMALL", "class": "instrument", "savings": 3}, {"group": "INSTR", "class": "instrument"}]}
    crit = {rl.norm_group("CP")}
    t = lambda g, **k: tier(g, crit, R, S, **k)  # noqa: E731
    check("default setting loads", S["order"] == list(TIERS))
    check("critical path, hotfix flag, HOTFIX name and outside are cp-hotfix",
          [t(g) for g in ("CP", "HF", "R10-HOTFIX-X", "OUT")] == ["cp-hotfix"] * 4)
    check("production and a 14 h instrument are tier1; a 3 h and a plain instrument are not",
          [t(g) for g in ("PROD", "BIG", "SMALL", "INSTR")] == ["tier1", "tier1", "instrument", "instrument"])
    check("a group-less PR is tier1 only when it touches custom_components/",
          (t(None, touches_production=True), t(None), t("NOPE")) == ("tier1", "instrument", "instrument"))
    order = sorted(["INSTR", "SMALL", "BIG", "PROD", "OUT", "CP"],
                   key=lambda g: rank(g, crit, R, S))
    check("null: the default setting orders cp/outside, then savings, then the rest",
          order[0] in ("CP", "OUT") and order.index("BIG") < order.index("SMALL")
          and order.index("PROD") < order.index("INSTR"))
    check("a 14 h instrument ranks with a production PR and above a 3 h one",
          rank("BIG", crit, R, S)[0] == rank("PROD", crit, R, S)[0] < rank("SMALL", crit, R, S)[0])
    check("never_cancel covers cp-hotfix, not tier1", (is_priority("cp-hotfix", S), is_priority("tier1", S)) == (True, False))
    check("train head and cp-hotfix may not be paused; an instrument may",
          (may_pause("instrument", S), may_pause("instrument", S, train_head=True), may_pause("cp-hotfix", S)) == (True, False, False))

    def refused(mut, key):
        try:
            check_setting({**S, **mut})
        except SettingError as e:
            return key in str(e)
        return False
    check("a group-keyed map is refused naming the key", refused({"savings_h": {"R10-X": 14}}, "savings_h"))
    check("a dropped never_cancel floor member is refused", refused({"never_cancel": ["main-push"]}, "never_cancel"))
    check("a dropped never_pause floor member is refused", refused({"never_pause": ["main-push", "cp-hotfix"]}, "never_pause"))
    check("a reordered order that demotes main-push is refused", refused({"order": ["cp-hotfix", "main-push", "tier1", "instrument"]}, "order"))
    print(f"ci_priority self-test: {n} checks, {bad} failed")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    if argv[1:] == ["--self-test"]:
        return _self_test()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
