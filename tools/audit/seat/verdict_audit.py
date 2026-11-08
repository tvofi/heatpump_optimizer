#!/usr/bin/env python3
"""Map every open PR to its latest verdict and the holder it is owed, and print UNHELD lines.

    verdict_audit.py --repo O/R [--fired LEDGER] [--train-glob GLOB] [--skip FILE]
    verdict_audit.py --self-test

Owner ruling (tvofi 2026-11-06): the sweep's point is that no PR waits unheld. The beat's
`verdict-audit` row (`tools/audit/seat/beat_jobs.py`) runs this every 30 minutes and writes
each `UNHELD` line to the digest the orchestrator reads.

One `UNHELD` line per PR whose next step nobody visibly holds:
  merge verdict at an older head that the PR head only main-merges onto -> owed to the merge train
  blocked verdict and handoff/<topic> not moved past the blocked sha    -> owed a repair fixer
  blocked verdict and the handoff moved on                              -> owed update_pr then a reviewer
  no verdict ref at all                                                 -> owed a first reviewer
"Held" means: queued in a live train log (modified within 3 h), or a fire line in the
last 12 h naming the PR or its topic. `--skip FILE` lists `#<N> <ruling>` lines: PRs held
by an owner ruling rather than a seat, which are never printed.
Run from a checkout of the repository with origin fetched; reads only (`gh pr list`,
`git ls-remote`, `git fetch`, `git show`).
"""
import argparse, glob, json, os, re, subprocess, sys, time

HELD_H = 12
TRAIN_H = 3
STAMP = re.compile(r"(\d{4}-\d\d-\d\dT\d\d:\d\d)(?::\d\d)?Z")


def recent_lines(lines, now):
    """Fire-ledger lines whose leading UTC stamp is at most HELD_H old."""
    cut = now - HELD_H * 3600
    out = []
    for l in lines:
        m = STAMP.match(l)
        if m and time.mktime(time.strptime(m[1], "%Y-%m-%dT%H:%M")) - time.timezone >= cut:
            out.append(l)
    return "".join(x if x.endswith("\n") else x + "\n" for x in out)


def skip_set(lines):
    return {int(m[1]) for l in lines if (m := re.match(r"#(\d+)\s", l))}


def audit(prs, refs, verdict_first, recent, trains, skip, moved_past):
    """Pure core. prs: dicts number/headRefOid/headRefName/title. refs: ref -> sha.
    verdict_first: sha -> first line of its VERDICT.md. moved_past(handoff, at) -> bool.
    Returns the UNHELD lines."""
    out = []
    for p in prs:
        n, head, br = p["number"], p["headRefOid"], p["headRefName"]
        if n in skip:
            continue
        topic = br.split("/", 1)[-1]
        held = f"#{n}" in recent or topic in recent
        v = refs.get(f"refs/heads/verdict/{n}")
        if not v:
            if not held:
                out.append(f"UNHELD #{n} no verdict ever: owed a first reviewer once the gate is green ({p['title'][:50]})")
            continue
        m = re.match(r"Fix review: (\w+) ([0-9a-f]{40})", verdict_first.get(v, ""))
        if not m:
            continue
        kind, at = m[1], m[2]
        if kind == "merge":
            if re.search(rf"#{n}\b", trains) is None and not held:
                out.append(f"UNHELD #{n} merge verdict at {at[:8]}, head {head[:8]}: owed to the merge train")
        elif kind == "blocked":
            h = refs.get(f"refs/heads/handoff/{topic}")
            moved = bool(h) and h != at and moved_past(h, at)
            if head == at and not moved and not held:
                out.append(f"UNHELD #{n} blocked at {at[:8]}, no repair handoff and no fire in 12 h: owed a repair fixer")
            elif moved and head == at and not held:
                out.append(f"UNHELD #{n} blocked at {at[:8]}, handoff moved to {h[:8]}: owed update_pr then a reviewer")
    return out


def sh(*a):
    return subprocess.run(a, capture_output=True, text=True).stdout


def live(args):
    prs = json.loads(sh("gh", "pr", "list", "--repo", args.repo, "--state", "open", "--limit", "100",
                        "--json", "number,headRefOid,headRefName,title"))
    refs = {}
    for line in sh("git", "ls-remote", "origin", "refs/heads/verdict/*", "refs/heads/handoff/*").splitlines():
        sha, ref = line.split("\t")
        refs[ref] = sha
    first = {}
    for p in prs:
        v = refs.get(f"refs/heads/verdict/{p['number']}")
        if v:
            subprocess.run(["git", "fetch", "-q", "origin", v], capture_output=True)
            lines = sh("git", "show", f"{v}:VERDICT.md").splitlines()[:1]
            first[v] = lines[0] if lines else ""
    now = time.time()
    recent = recent_lines(open(args.fired).readlines(), now) if args.fired and os.path.exists(args.fired) else ""
    trains = ""
    for f in glob.glob(args.train_glob) if args.train_glob else []:
        if now - os.path.getmtime(f) < TRAIN_H * 3600:
            trains += open(f, errors="replace").read()
    skip = skip_set(open(args.skip).read().splitlines()) if args.skip and os.path.exists(args.skip) else set()
    def moved_past(h, at):
        return subprocess.run(["git", "merge-base", "--is-ancestor", h, at], capture_output=True).returncode != 0
    return audit(prs, refs, first, recent, trains, skip, moved_past)


def self_test():
    n = 0
    bad = 0

    def check(name, cond):
        nonlocal n, bad
        n += 1
        if not cond:
            bad += 1
            print(f"FAIL {name}")

    A, B, C = "a" * 40, "b" * 40, "c" * 40
    pr = lambda num, head, br: {"number": num, "headRefOid": head, "headRefName": br, "title": f"t{num}"}
    never = lambda h, at: True
    # no verdict ref: unheld, and the null control (a recent fire naming the topic) silences it
    out = audit([pr(1, A, "fix/r10-x")], {}, {}, "", "", set(), never)
    check("no verdict -> first reviewer", len(out) == 1 and "first reviewer" in out[0])
    check("null control: topic fired -> held", audit([pr(1, A, "fix/r10-x")], {}, {}, "FIRED r10-x\n", "", set(), never) == [])
    # merge verdict at an older head
    refs = {"refs/heads/verdict/2": "v2"}
    fv = {"v2": f"Fix review: merge {B}"}
    out = audit([pr(2, A, "fix/r10-y")], refs, fv, "", "", set(), never)
    check("merge verdict not queued -> merge train", len(out) == 1 and "merge train" in out[0])
    check("null control: queued in a train log", audit([pr(2, A, "fix/r10-y")], refs, fv, "", "queued #2 ok\n", set(), never) == [])
    check("#20 in the train log does not hold #2", len(audit([pr(2, A, "fix/r10-y")], refs, fv, "", "#20\n", set(), never)) == 1)
    # blocked verdict at the head, handoff not moved, then moved
    refs = {"refs/heads/verdict/3": "v3", "refs/heads/handoff/r10-z": B}
    fv = {"v3": f"Fix review: blocked {B}"}
    out = audit([pr(3, B, "fix/r10-z")], refs, fv, "", "", set(), lambda h, at: False)
    check("blocked, handoff unmoved -> repair fixer", len(out) == 1 and "repair fixer" in out[0])
    refs2 = dict(refs, **{"refs/heads/handoff/r10-z": C})
    out = audit([pr(3, B, "fix/r10-z")], refs2, fv, "", "", set(), lambda h, at: True)
    check("blocked, handoff moved -> update_pr", len(out) == 1 and "update_pr" in out[0])
    check("null control: a fire in 12 h holds it", audit([pr(3, B, "fix/r10-z")], refs2, fv, "#3\n", "", set(), lambda h, at: True) == [])
    # skip file: owner-ruled PRs are never printed
    check("skip set parses '#N ruling'", skip_set(["#3226 owner ruled", "junk", "#7\tx"]) == {3226, 7})
    check("skipped PR is silent", audit([pr(1, A, "fix/r10-x")], {}, {}, "", "", {1}, never) == [])
    check("null control: not skipped speaks", len(audit([pr(1, A, "fix/r10-x")], {}, {}, "", "", {2}, never)) == 1)
    # 12 h window of the fire ledger
    now = time.mktime(time.strptime("2026-11-06T12:00", "%Y-%m-%dT%H:%M")) - time.timezone
    led = ["2026-11-05T09:00:00Z FIRED #1\n", "2026-11-06T10:00Z FIRED #2\n", "no stamp #3\n"]
    r = recent_lines(led, now)
    check("fire older than 12 h is dropped", "#1" not in r and "#2" in r and "#3" not in r)
    check("null control: 20 h later nothing is recent", recent_lines(led, now + 20 * 3600) == "")
    check("a stale fire leaves the PR unheld", len(audit([pr(1, A, "fix/r10-x")], {}, {}, recent_lines(led[:1], now), "", set(), never)) == 1)
    print(f"verdict_audit self-test: {n} checks, {bad} failed")
    return 1 if bad else 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--fired")
    ap.add_argument("--train-glob")
    ap.add_argument("--skip")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.repo:
        ap.error("--repo is required")
    for line in live(a):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
