#!/usr/bin/env python3
"""What a round's records say per dimension brief, for decision 0018 section 3's dimension row.

Usage: python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref <graded sha> --round 10 --roster <SHA:PATH>
Per dimension, one line: judged verdicts of the round (JUDGE.json and CATCHUP-JUDGE.json, a verdict id counted once, the later
record winning), how many stand (verified or weakened), how many of those the judge classed `bug`, how many standing findings sit
in a roster group whose stage is done (the removed count, by finding id in the group's `findings`), and the seats' own coverage
rows from reports-B*.json: rows, steps, depth labels, steps no seat ran `deep`, rows carrying an examined/universe key (the
denominator 0018's `coverage` needs) and rows whose evidence states a count as `N of M` or `N/M` in prose. An id with no D<k> prefix is attributed by its prefix (ARCH*: D7) or listed under `other`.
"""
import argparse, collections, glob, json, re, subprocess, sys


def show(repo, spec):
    r = subprocess.run(["git", "-C", repo, "show", spec], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="."); ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--round", type=int, required=True); ap.add_argument("--roster", required=True)
    a = ap.parse_args()
    base = f"dev/audit/rounds/round{a.round}/"
    verdicts = {}
    for f in ("JUDGE.json", "CATCHUP-JUDGE.json"):
        t = show(a.repo, f"{a.ref}:{base}{f}")
        for v in (json.loads(t)["verdicts"] if t else []):
            verdicts[v["id"]] = v
    groups = json.loads(show(a.repo, a.roster))["groups"]
    done_ids, any_ids = set(), set()
    for g in groups:
        for fid in g.get("findings") or []:
            any_ids.add(str(fid))
            if (g.get("resume") or {}).get("stage") == "done":
                done_ids.add(str(fid))
    def dim(i):
        m = re.match(r"D(\d+)-", i)
        return f"D{m.group(1)}" if m else ("D7" if i.startswith("ARCH") else "other")
    tab = collections.defaultdict(collections.Counter)
    for i, v in verdicts.items():
        d = tab[dim(i)]
        d["judged"] += 1
        if v.get("verdict") in ("verified", "weakened"):
            d["stand"] += 1
            d["bug"] += v.get("stop_rule_class") == "bug"
            d["removed"] += i in done_ids
            d["in_no_group"] += i not in any_ids
    files = [l for l in subprocess.run(["git", "-C", a.repo, "ls-tree", "--name-only", a.ref, base], capture_output=True, text=True).stdout.split("\n") if re.search(r"reports-B\d+\.json$", l)]
    cov = collections.defaultdict(lambda: {"rows": 0, "depth": collections.Counter(), "steps": collections.defaultdict(set), "denom": 0, "prose": 0, "seats": 0})
    for f in files:
        for seat, r in json.loads(show(a.repo, f"{a.ref}:{f}"))["reports"].items():
            c = cov[r.get("dimension") or seat.split("-")[0]]
            c["seats"] += 1
            for row in r.get("coverage") or []:
                c["rows"] += 1; c["depth"][str(row.get("depth"))] += 1; c["steps"][str(row.get("step"))].add(str(row.get("depth")))
                c["denom"] += any(k in row for k in ("examined", "universe", "denominator"))
                c["prose"] += bool(re.search(r"\b\d+\s*(?:of|/)\s*\d+\b", str(row.get("evidence", ""))))
    print("dimension\tjudged\tstand\tbug\tremoved\tstand_in_no_group\tseats\tcoverage_rows\tsteps\tdepth\tsteps_not_deep\trows_with_examined_universe\trows_stating_a_count_in_prose")
    for k in sorted(set(tab) | set(cov), key=lambda s: (s == "other", int(s[1:]) if s[1:].isdigit() else 0)):
        d, c = tab[k], cov[k]
        nd = sorted(s for s, ds in c["steps"].items() if "deep" not in ds)
        print(f"{k}\t{d['judged']}\t{d['stand']}\t{d['bug']}\t{d['removed']}\t{d['in_no_group']}\t{c['seats']}\t{c['rows']}\t{len(c['steps'])}\t{dict(c['depth'])}\t{','.join(nd) or '-'}\t{c['denom']}\t{c['prose']}")
    print(f"ROWS {sum(c['rows'] for c in cov.values())} WITH_EXAMINED_UNIVERSE {sum(c['denom'] for c in cov.values())} STATING_A_COUNT_IN_PROSE {sum(c['prose'] for c in cov.values())}")
    print(f"VERDICTS {len(verdicts)} DIMENSIONS_REPORTED {sum(1 for c in cov.values() if c["seats"])}")


if __name__ == "__main__":
    main()
