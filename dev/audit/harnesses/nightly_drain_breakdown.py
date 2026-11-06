#!/usr/bin/env python3
"""Where a nightly's mutation-ledger draw went, per shard, from its job logs.

    python3 dev/audit/harnesses/nightly_drain_breakdown.py SHARD.log... \
        [--prior OTHER_RUN_SHARD.log...]

Each SHARD.log is one `mutation-ledger (K)` job log, as
`gh api repos/<owner>/<repo>/actions/jobs/<id>/logs` returns it. The rule,
per shard, reads only the lines `tests/mutation_table.py --drain` prints
between its `DRAIN SHARD` header and its `DRAIN:` summary:

* drawn      -- the header's `N of M unpinned site(s)`;
* killed     -- `pinned <site> -- killed by <script>` rows;
* lives      -- `UNPINNED <site> -- lives` rows (owed a human verdict);
* split      -- `UNPINNED <site> -- killed by ..., but its anchor also
  covers a site no run killed` rows: killed, but unpinnable, since a
  disposition covers the whole anchor;
* timed out  -- `UNPINNED <site> -- skip-timed-out in ...` rows;
* not run    -- `NOT RUN <site> -- not started: ... --budget-minutes` rows;
* slack      -- minutes between the `DRAIN:` line and the --budget-minutes
  deadline, the deadline taken as the header's timestamp plus the budget
  read from the job's own echoed command (the drive's deadline is set a few
  seconds before the header, so this overstates the slack by those seconds).

Every drawn site lands in exactly one class or the shard reports `UNCLASSED`,
the rule's own null control. `--prior` names the job logs of a run that
pushed before this one: a kill it also recorded lands no new pin, so
`killed new` is the count the push could record.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timedelta

_STAMP = re.compile(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)\.\d+Z (.*)$")
_HEAD = re.compile(r"DRAIN SHARD (\d+)/(\d+) -- (\d+) of (\d+) unpinned")
_BUDGET = re.compile(r"--budget-minutes (\d+)")
_ROW = re.compile(r"^  (pinned|UNPINNED|NOT RUN) +(\S+ [A-Z_]+) -- (.*)$")


def _lines(path: str):
    with open(path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            raw = raw.lstrip("\ufeff").rstrip("\n")
            m = _STAMP.match(raw)
            if m:
                yield datetime.fromisoformat(m.group(1)), m.group(2)


def shard(path: str) -> dict:
    """One shard's classes, read by the module docstring's rule."""
    out = {"path": path, "killed": [], "lives": 0, "split": 0, "timed out": 0,
           "not run": 0, "unclassed": []}
    budget = start = end = None
    inside = False
    for when, text in _lines(path):
        if budget is None and (b := _BUDGET.search(text)):
            budget = int(b.group(1))
        if (h := _HEAD.search(text)):
            inside, start = True, when
            out["shard"], out["drawn"] = f"{h.group(1)}/{h.group(2)}", int(h.group(3))
            continue
        if not inside:
            continue
        if text.startswith("DRAIN: "):
            end = when
            break
        row = _ROW.match(text)
        if not row:
            continue
        kind, site, why = row.groups()
        if kind == "pinned" and why.startswith("killed by "):
            out["killed"].append(site)
        elif kind == "UNPINNED" and why == "lives":
            out["lives"] += 1
        elif kind == "UNPINNED" and "but its anchor also covers" in why:
            out["split"] += 1
        elif kind == "UNPINNED" and why.startswith("skip-timed-out"):
            out["timed out"] += 1
        elif kind == "NOT RUN" and "--budget-minutes" in why:
            out["not run"] += 1
        elif kind == "UNPINNED" and why == "skip-budget":
            continue  # the NOT RUN row names the same mutant
        else:
            out["unclassed"].append(text.strip())
    if start and end and budget:
        out["slack_min"] = round(
            (start + timedelta(minutes=budget) - end).total_seconds() / 60)
    out["budget"] = budget
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("logs", nargs="+")
    ap.add_argument("--prior", nargs="*", default=[])
    args = ap.parse_args(argv)
    prior = {s for p in args.prior for s in shard(p)["killed"]}
    totals: dict[str, int] = {}
    bad = 0
    for path in args.logs:
        s = shard(path)
        if "drawn" not in s:
            print(f"{path}: no DRAIN SHARD header, not a shard log; skipped")
            continue
        new = [k for k in s["killed"] if k not in prior]
        row = {"drawn": s.get("drawn", 0), "killed": len(s["killed"]),
               "killed new": len(new), "lives": s["lives"], "split": s["split"],
               "timed out": s["timed out"], "not run": s["not run"]}
        summed = (row["killed"] + row["lives"] + row["split"]
                  + row["timed out"] + row["not run"])
        for k, v in row.items():
            totals[k] = totals.get(k, 0) + v
        print(f"shard {s.get('shard', '?')}: " + ", ".join(
            f"{k} {v}" for k, v in row.items())
            + f"; slack {s.get('slack_min', '?')} min of --budget-minutes "
              f"{s['budget']}")
        if summed != row["drawn"] or s["unclassed"]:
            bad = 1
            print(f"  UNCLASSED: classes sum to {summed} of {row['drawn']} "
                  f"drawn; {len(s['unclassed'])} row(s) no rule reads: "
                  + "; ".join(s["unclassed"][:3]))
    print("total: " + ", ".join(f"{k} {v}" for k, v in totals.items()))
    return bad


if __name__ == "__main__":
    sys.exit(main())
