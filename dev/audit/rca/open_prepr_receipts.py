#!/usr/bin/env python3
"""Receipt reach and open latency, read from git alone (R10-RCA-OPEN-PREPR-SLOW).

`tips`: every handoff-body tip (origin/handoff-body/* and archive/handoff-body/*
tags) committed in [--since, --until) is classed as a result body (no `Code:`),
a code body whose tip carries a `Prepr:` trailer, or a code body without one.
A body without one is split by the newest earlier body on the same history that
carried a trailer: `same` (that trailer's sha is the tip's code), `merge-only`
(an ancestor of the code, every commit on the ancestry path between them a
merge), `non-merge` (an ancestor, a non-merge commit on that path), `not-ancestor`, or `never`. For
`merge-only` and `non-merge` rows `tree_equal` says whether
`git merge-tree --write-tree <receipt> <base>` equals the code's tree but for
delivery rows, the test app_push.sh's reuse_verdict applies; `<base>` is the
newest commit on --main's first-parent chain the code contains, which, unlike
merge-base, stays the main the code merged after the code lands on main. A code object absent
from this clone is `missing`.

`opens`: for every `record: the delivery row for #N` commit committed in the
window, the latency is its committer time less the committer time of the newest
handoff-body commit, made before it, whose `Code:` is the row's parent or one of
that parent's parents (open_pr.sh merges main first). The row is graded
`receipt` when that body commit carries a `Prepr:` trailer, else `full`. A proxy
for an open's duration: it also holds the relay's wait before the open starts.

Exit 0; exit 2 on a git failure. --self-test builds a synthetic origin.

  python3 -I dev/audit/rca/open_prepr_receipts.py tips  --since ISO --until ISO [--main REF] [--repo DIR]
  python3 -I dev/audit/rca/open_prepr_receipts.py opens --since ISO --until ISO [--repo DIR]
  python3 -I dev/audit/rca/open_prepr_receipts.py --self-test
"""
import argparse, datetime, os, statistics, subprocess, sys, tempfile

ROW_DIR = "dev/programme/delivery/"
REFS = ("refs/remotes/origin/handoff-body/", "refs/tags/archive/handoff-body/")


def git(repo, *a, ok=(0,)):
    r = subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True)
    if r.returncode not in ok:
        sys.stderr.write(f"git {' '.join(a)}: rc {r.returncode}: {r.stderr.strip()}\n")
        sys.exit(2)
    return r.returncode, r.stdout.strip()


def trailers(msg):
    code = prepr = None
    for line in msg.splitlines():
        if line.startswith("Code: "):
            code = line.split()[1]
        elif line.startswith("Prepr: ") and len(line.split()) == 3:
            prepr = line.split()[1]
    return code, prepr


def history(repo, ref):
    """[(sha, ct, code, prepr)] newest first, along the ref's first parents."""
    _, out = git(repo, "log", "--first-parent", "--format=%H%x00%ct%x00%B%x01", ref)
    rows = []
    for rec in out.split("\x01"):
        rec = rec.strip("\n")
        if not rec:
            continue
        sha, ct, msg = rec.split("\x00", 2)
        rows.append((sha, int(ct), *trailers(msg)))
    return rows


def body_refs(repo):
    seen, refs = set(), []
    for prefix in REFS:
        _, out = git(repo, "for-each-ref", "--format=%(refname) %(objectname)", prefix)
        for line in out.splitlines():
            ref, sha = line.split()
            if sha not in seen:
                seen.add(sha)
                refs.append(ref)
    return refs


def has(repo, sha):
    return git(repo, "cat-file", "-e", f"{sha}^{{commit}}", ok=(0, 1, 128))[0] == 0


def main_base(repo, code, main):
    """The newest commit on `main`'s first-parent chain that `code` contains: the
    main an open of `code` merged, which stays put after `code` itself lands."""
    global _CHAIN
    if _CHAIN is None:
        _CHAIN = git(repo, "rev-list", "--first-parent", main)[1].split()
    anc = set(git(repo, "rev-list", code)[1].split())
    return next((c for c in _CHAIN if c in anc and c != code), None)


_CHAIN = None


def tips(repo, since, until, main):
    rows = []
    for ref in body_refs(repo):
        h = history(repo, ref)
        sha, ct, code, prepr = h[0]
        if not since <= ct < until:
            continue
        name = ref.split("handoff-body/", 1)[1]
        if code is None:
            rows.append((name, sha[:9], "result", "")); continue
        if prepr is not None:
            rows.append((name, sha[:9], "trailer", "")); continue
        earlier = next((r for r in h[1:] if r[3] is not None), None)
        if earlier is None:
            rows.append((name, sha[:9], "never", "")); continue
        rec = earlier[3]
        if rec == code:
            rows.append((name, sha[:9], "same", "")); continue
        if not (has(repo, rec) and has(repo, code)):
            rows.append((name, sha[:9], "missing", "")); continue
        if git(repo, "merge-base", "--is-ancestor", rec, code, ok=(0, 1))[0] != 0:
            rows.append((name, sha[:9], "not-ancestor", "")); continue
        _, nm = git(repo, "rev-list", "--ancestry-path", "--no-merges", f"{rec}..{code}")
        kind = "non-merge" if nm else "merge-only"
        base = main_base(repo, code, main)
        tree_equal = "no-base"
        if base:
            rc, out = git(repo, "merge-tree", "--write-tree", rec, base, ok=(0, 1))
            tree_equal = "conflict"
            if rc == 0:
                _, d = git(repo, "diff", "--name-only", out.split()[0], f"{code}^{{tree}}")
                rest = [f for f in d.splitlines() if not f.startswith(ROW_DIR)]
                tree_equal = "no" if rest else "yes"
        rows.append((name, sha[:9], kind, tree_equal))
    return rows


def opens(repo, since, until):
    index = {}
    for ref in body_refs(repo):
        for sha, ct, code, prepr in history(repo, ref):
            if code:
                index.setdefault(code, set()).add((ct, prepr is not None))
    _, out = git(repo, "log", "--all", "--format=%H %ct %P%x00%s",
                 "--grep=^record: the delivery row for #")
    rows = []
    for line in out.splitlines():
        head, subj = line.split("\x00", 1)
        sha, ct, *parents = head.split()
        ct = int(ct)
        if not since <= ct < until or not parents:
            continue
        cands = [parents[0]]
        _, pp = git(repo, "rev-list", "--parents", "-n1", parents[0])
        cands += pp.split()[1:]
        bodies = [b for c in cands for b in index.get(c, ()) if b[0] <= ct]
        if not bodies:
            rows.append((subj.rsplit("#", 1)[-1], sha[:9], "unmatched", "")); continue
        bct, receipt = max(bodies)
        rows.append((subj.rsplit("#", 1)[-1], sha[:9], "receipt" if receipt else "full",
                     f"{(ct - bct) / 60:.1f}"))
    return rows


def summary_tips(rows):
    from collections import Counter
    c = Counter(r[2] for r in rows)
    code = len(rows) - c["result"]
    none = code - c["trailer"]
    print(f"RESULT tips={len(rows)} result={c['result']} code={code} trailer={c['trailer']} no_trailer={none}")
    print("RESULT split " + " ".join(f"{k}={c[k]}" for k in
          ("same", "merge-only", "non-merge", "not-ancestor", "never", "missing")))
    anc = [r for r in rows if r[2] in ("merge-only", "non-merge")]
    print(f"RESULT tree_equal={sum(r[3] == 'yes' for r in anc)} of={len(anc)}")


def summary_opens(rows):
    for kind in ("full", "receipt"):
        m = sorted(float(r[3]) for r in rows if r[2] == kind)
        if m:
            q = statistics.quantiles(m, n=4) if len(m) > 1 else [m[0]] * 3
            print(f"RESULT {kind} n={len(m)} median_min={statistics.median(m):.1f} p75_min={q[2]:.1f}")
        else:
            print(f"RESULT {kind} n=0")
    print(f"RESULT unmatched={sum(r[2] == 'unmatched' for r in rows)}")


def iso(s):
    return int(datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())


def self_test():
    """Synthetic origin: one tip per class, two opens; each assertion has the case that would fail it."""
    fails = 0
    def check(name, cond):
        nonlocal fails
        print(("ok   " if cond else "FAIL ") + name)
        fails += not cond
    with tempfile.TemporaryDirectory() as d:
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                   GIT_COMMITTER_EMAIL="t@t")
        def run(*a, t=None):
            e = dict(env)
            if t is not None:
                e["GIT_COMMITTER_DATE"] = e["GIT_AUTHOR_DATE"] = f"@{t} +0000"
            return subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, env=e,
                                  check=True).stdout.strip()
        def commit(msg, t, parents=(), tree=None):
            tree = tree or run("write-tree")
            args = ["commit-tree", tree, "-m", msg]
            for p in parents:
                args += ["-p", p]
            return run(*args, t=t)
        run("init", "-q")
        def blob_tree(content):
            b = subprocess.run(["git", "-C", d, "hash-object", "-w", "--stdin"], input=content,
                               capture_output=True, text=True, check=True).stdout.strip()
            return subprocess.run(["git", "-C", d, "mktree"], input=f"100644 blob {b}\tf\n",
                                  capture_output=True, text=True, check=True).stdout.strip()
        def tree2(a, b):
            ba, bb = (subprocess.run(["git", "-C", d, "hash-object", "-w", "--stdin"], input=x,
                      capture_output=True, text=True, check=True).stdout.strip() for x in (a, b))
            return subprocess.run(["git", "-C", d, "mktree"],
                                  input=f"100644 blob {ba}\tf\n100644 blob {bb}\tg\n",
                                  capture_output=True, text=True, check=True).stdout.strip()
        T = 1_000_000
        root = commit("root", T, tree=blob_tree("0\n"))
        main = commit("main", T + 10, [root], tree=tree2("0\n", "m\n"))
        code = commit("code", T + 20, [root], tree=blob_tree("1\n"))
        merged = commit("merge", T + 30, [code, main], tree=tree2("1\n", "m\n"))
        moved = commit("work", T + 40, [code], tree=blob_tree("2\n"))
        other = commit("other", T + 50, [root], tree=blob_tree("3\n"))
        run("update-ref", "refs/remotes/origin/main", main)
        empty = blob_tree("")
        def body(name, msgs):
            p = ()
            for i, m in enumerate(msgs):
                c = commit(m, T + 100 + i, p, tree=empty)
                p = (c,)
            run("update-ref", f"refs/remotes/origin/handoff-body/{name}", p[0])
        rc = f"Prepr: {code} {run('rev-parse', code + '^{tree}')}"
        body("result", ["verdict"])
        body("trailer", [f"b\n\nCode: {code}\n{rc}"])
        body("same", [f"b\n\nCode: {code}\n{rc}", f"b\n\nCode: {code}"])
        body("mergeonly", [f"b\n\nCode: {code}\n{rc}", f"b\n\nCode: {merged}"])
        body("nonmerge", [f"b\n\nCode: {code}\n{rc}", f"b\n\nCode: {moved}"])
        body("notanc", [f"b\n\nCode: {code}\n{rc}", f"b\n\nCode: {other}"])
        body("never", [f"b\n\nCode: {other}"])
        got = {r[0]: (r[2], r[3]) for r in tips(d, T, T + 1000, "refs/remotes/origin/main")}
        for name, want in (("result", "result"), ("trailer", "trailer"), ("same", "same"),
                           ("mergeonly", "merge-only"), ("nonmerge", "non-merge"),
                           ("notanc", "not-ancestor"), ("never", "never")):
            check(f"{name} classed {want} (got {got.get(name)})", got.get(name, ("",))[0] == want)
        check("merge-only receipt passes the tree test", got["mergeonly"][1] == "yes")
        check("null control: a non-merge commit past the receipt fails it", got["nonmerge"][1] == "no")
        check("window: no tip outside [since, until) is read",
              tips(d, T + 1000, T + 2000, "refs/remotes/origin/main") == [])
        row1 = commit("record: the delivery row for #1", T + 100 + 60, [merged], tree=empty)
        row2 = commit("record: the delivery row for #2", T + 100 + 600, [other], tree=empty)
        run("update-ref", "refs/remotes/origin/fix/a", row1)
        run("update-ref", "refs/remotes/origin/fix/b", row2)
        got = {r[0]: r for r in opens(d, T, T + 2000)}
        check(f"open on a merged code matches its body by the code parent ({got.get('1')})",
              got.get("1", ("",) * 4)[2:] == ("full", "1.0"))
        check(f"open on the never body is full ({got.get('2')})", got.get("2", ("",) * 4)[2] == "full")
    print(f"{'PASS' if not fails else 'FAIL'} self-test, {fails} failed")
    return 1 if fails else 0


def main():
    if "--self-test" in sys.argv:
        return self_test()
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=("tips", "opens"))
    p.add_argument("--since", required=True)
    p.add_argument("--until", required=True)
    p.add_argument("--main", default="refs/remotes/origin/main")
    p.add_argument("--repo", default=".")
    a = p.parse_args()
    if a.mode == "tips":
        rows = tips(a.repo, iso(a.since), iso(a.until), a.main)
        for r in sorted(rows):
            print("\t".join(r))
        summary_tips(rows)
    else:
        rows = opens(a.repo, iso(a.since), iso(a.until))
        for r in sorted(rows):
            print("\t".join(r))
        summary_opens(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
