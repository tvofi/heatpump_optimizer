#!/usr/bin/env python3
"""record_batch_measure.py -- the record beat's batch and pitch, measured from
main's first-parent history (R10-FLOW-RECORD-PITCH).

    python3 dev/audit/harnesses/record_batch_measure.py SINCE [TIP]
    python3 dev/audit/harnesses/record_batch_measure.py db71fe47a origin/main

SINCE..TIP is read with `git log --first-parent`, so it needs a full clone.
A merge is a two-parent first-parent commit; a record merge is one whose
subject is `Merge pull request #N from <owner>/record/autofix` (the git rule
`--grep='from tvofi/record/autofix'` names). Prints:

  * per UTC day: merges (one row each) and record merges -- the after-merge
    comparison runs this over a day before and a day after the change;
  * per record merge, summarised (min / median / p90 / max):
      rows    -- row files in its three-dot diff (`git diff M^1...M^2`);
      wait_c  -- first-parent commits main gained between the record head's
                 merge base and its merge: the commits the batch margin
                 under STALE_AFTER_COMMITS must cover;
      wait_s  -- seconds from the record head's commit to its merge;
      age     -- first-parent commits between its oldest rowed merge and it;
  * chain -- record merges that rowed the previous record merge (the record
    chain: each record merge owing the next a row);
  * conflicts -- record merges with a row file main also changed while open;
  * moved -- record merges the next merged non-record head did not contain
    (a record merge that moved main under an open head).

Null control: an empty range (SINCE=TIP) prints zero merges and no record
merges, so a count above zero comes from the range, not the rule.
"""
from __future__ import annotations

import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
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
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "tools/audit/seat")]
from delivery_status import subject_number  # noqa: E402  the merge-subject reader
from record_row import RECORD_BRANCH, ROW_PATH  # noqa: E402  the record branch and row path


def record_merge(subject: str) -> bool:
    """Whether a first-parent subject is a merge of the record branch."""
    return subject.startswith("Merge pull request #") and subject.endswith("/" + RECORD_BRANCH)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def summary(name: str, values: list) -> str:
    v = sorted(values)
    if not v:
        return f"{name}: n=0"
    return (f"{name}: n={len(v)} min={v[0]} median={statistics.median(v)} "
            f"p90={v[int(0.9 * (len(v) - 1))]} max={v[-1]}")


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    since, tip = argv[0], argv[1] if len(argv) > 1 else "origin/main"
    log = [ln.split("\x1f") for ln in git(
        "log", "--first-parent", "--reverse", "--format=%H\x1f%P\x1f%cI\x1f%s",
        f"{since}..{tip}").splitlines() if ln]
    merged_at, record_ix = {}, []
    day: dict = defaultdict(Counter)
    for i, (sha, parents, when, subject) in enumerate(log):
        n = subject_number(subject)
        if len(parents.split()) != 2:
            continue
        d = datetime.fromisoformat(when).astimezone(timezone.utc).strftime("%F")
        day[d]["merges"] += 1
        if n is not None:
            merged_at[n] = i
            if record_merge(subject):
                day[d]["record"] += 1
                record_ix.append(i)
    print("UTC day, merges (rows owed), record merges")
    for d in sorted(day):
        print(d, day[d]["merges"], day[d]["record"])
    rec = []
    for k, i in enumerate(record_ix):
        sha, parents, when, subject = log[i]
        p1, p2 = parents.split()
        base = git("merge-base", p1, p2).strip()
        files = [f for f in git("diff", "--name-only", f"{p1}...{p2}").split() if f]
        rows = [int(ROW_PATH.match(f).group(1)) for f in files if ROW_PATH.match(f)]
        head_at = datetime.fromisoformat(git("show", "-s", "--format=%cI", p2).strip())
        touched = set(git("diff", "--name-only", base, p1).split()) if base != p1 else set()
        prev = subject_number(log[record_ix[k - 1]][3]) if k else None
        moved = None
        for j in range(i + 1, len(log)):
            if len(log[j][1].split()) == 2 and subject_number(log[j][3]) is not None \
                    and not record_merge(log[j][3]):
                moved = subprocess.run(["git", "merge-base", "--is-ancestor", sha,
                                        log[j][1].split()[1]]).returncode != 0
                break
        ages = [i - merged_at[n] for n in rows if n in merged_at and merged_at[n] < i]
        rec.append({
            "rows": len(rows),
            "wait_c": int(git("rev-list", "--first-parent", "--count", f"{base}..{p1}")),
            "wait_s": int((datetime.fromisoformat(when) - head_at).total_seconds()),
            "age": max(ages) if ages else None,
            "chain": prev is not None and prev in rows,
            "conflict": bool(set(files) & touched),
            "moved": moved,
        })
    print(f"\nrecord merges: {len(rec)}")
    for key in ("rows", "wait_c", "wait_s", "age"):
        print(summary(key, [r[key] for r in rec if r[key] is not None]))
    chained = [r for r in rec[1:]]
    print(f"chain: {sum(r['chain'] for r in chained)}/{len(chained)} record merges "
          "rowed the previous record merge")
    print(f"conflicts: {sum(r['conflict'] for r in rec)}/{len(rec)} record merges with "
          "a row file main also changed while open")
    known = [r for r in rec if r["moved"] is not None]
    print(f"moved: {sum(r['moved'] for r in known)}/{len(known)} record merges the next "
          "merged non-record head did not contain")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
