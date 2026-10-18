"""The migration's null control: the set of EXECUTED steps of one or more runs,
before versus after, compared as sets.

    python3 -I stepset.py RAW_DIR --before ID[,ID..] --after ID[,ID..] [--map MAP.json]

Each ID names a saved `jobs_<ID>.json` (GET actions/runs/<ID>/jobs?filter=latest)
under RAW_DIR. Several IDs on one side are unioned: the after side of a nightly is
the Tests schedule run PLUS the Nightly run. A step counts when its conclusion is
success or failure (skipped/cancelled steps did not execute). Key: (job, step);
a matrix suffix is kept, because `fast (3.14)` is the required context.
MAP.json is {"renames": {"old job|old step": "new job|new step"}, "dropped":
["job|step", ...]}: the design's closed list of intended moves. Exit 0 only when
before, mapped, equals after exactly. Anything else is printed and exits 1.
"""
import argparse, json, re, sys
from pathlib import Path

RUNNER = {"Set up job", "Complete job"}  # runner bookkeeping, not repository steps
# An unnamed `run:` step is displayed as its first line, which can embed a
# commit SHA (closure-scope's `BASE="<sha>"`): normalised, or every pair of heads differs.
SHA = re.compile(r"\b[0-9a-f]{40}\b")


def steps(raw: Path, ids: str) -> set[tuple[str, str]]:
    out = set()
    for i in ids.split(","):
        for j in json.loads((raw / f"jobs_{i}.json").read_text())["jobs"]:
            for s in j.get("steps") or []:
                if s["conclusion"] in ("success", "failure") and s["name"] not in RUNNER \
                        and not s["name"].startswith("Post "):
                    out.add((j["name"], SHA.sub("<sha>", s["name"])))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("raw", type=Path)
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--map", type=Path)
    a = ap.parse_args()
    m = json.loads(a.map.read_text()) if a.map else {"renames": {}, "dropped": []}
    ren = {tuple(k.split("|", 1)): tuple(v.split("|", 1)) for k, v in m["renames"].items()}
    drop = {tuple(d.split("|", 1)) for d in m["dropped"]}
    before = {ren.get(k, k) for k in steps(a.raw, a.before) if k not in drop}
    after = steps(a.raw, a.after)
    lost, gained = sorted(before - after), sorted(after - before)
    for k in lost:
        print("LOST    ", " | ".join(k))
    for k in gained:
        print("GAINED  ", " | ".join(k))
    print(f"STEPSET: before {len(before)} after {len(after)} lost {len(lost)} gained {len(gained)}")
    return 1 if lost or gained else 0


if __name__ == "__main__":
    sys.exit(main())
