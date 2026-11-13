"""Reviewer's hand mutants over tools/pr/outside.py production and command-line lines
(the reviewer's instrument, not the finder's). usage: hand_mutants.py <worktree>"""
import subprocess, sys, pathlib
wt = pathlib.Path(sys.argv[1]); f = wt / "tools/pr/outside.py"; src = f.read_text()
cut_a, cut_b = src.index("\ndef self_test"), src.index("\ndef main(")
M = [
 ("NULL", None, None, 0),
 ("owner_read: latest not APPROVED", 'if last.get("state") != "APPROVED":', 'if False:', 0),
 ("read_allowlist: not JSON", 'raise Refuse(f"{ALLOWLIST} at {ref} is not JSON") from None', 'data = {"contributors": []}', 0),
 ("read_allowlist: no list", ' or not isinstance(data.get("contributors"), list):', ':', 0),
 ("pull_facts: other number", ' or p.get("number") != pr:', ':', 0),
 ("shape: no 40-hex head", 'if not isinstance(f["head"], str) or not SHA40.fullmatch(f["head"]):', 'if False:', 0),
 ("other_pulls: commits pages", "/pulls?per_page=100\", pages=True)", "/pulls?per_page=100\", pages=False)", 0),
 ("other_pulls: branch pages", "&per_page=100\", pages=True)", "&per_page=100\", pages=False)", 0),
 ("check: fetch dropped", 'git("fetch", "-q", "--no-tags", "origin", f"+refs/pull/{pr}/head:refs/hpo-outside/{pr}")', 'pass', 0),
 ("check: moved-head refusal", 'if git("rev-parse", f"refs/hpo-outside/{pr}").strip() != head:', 'if False:', 0),
 ("check: reviews pages", 'owner_read(api(f"repos/{repo}/pulls/{pr}/reviews?per_page=100", pages=True)', 'owner_read(api(f"repos/{repo}/pulls/{pr}/reviews?per_page=100", pages=False)', 0),
 ("manifest_version: unparsed is ok", "return False, None\n\n\ndef changed", "return True, None\n\n\ndef changed", 0),
 ("approve: no mandate", "if mandate is None:", "if False:", 0),
 ("approve: fetch dropped", 'git("fetch", "-q", "--no-tags", "origin", f"+refs/pull/{pr}/head:refs/hpo-outside/{pr}")', 'pass', 1),
 ("approve: reviews pages (pre-post)", 'reviews = api(f"repos/{repo}/pulls/{pr}/reviews?per_page=100", pages=True)', 'reviews = api(f"repos/{repo}/pulls/{pr}/reviews?per_page=100", pages=False)', 0),
 ("approve: body file kept", "os.unlink(t.name)", "pass", 0),
 ("approve: post refusal", "        if rc:\n            return 1, [f\"REFUSE: the review was refused", "        if False:\n            return 1, [f\"REFUSE: the review was refused", 0),
 ("approve: read-back pages", 'back = api(f"repos/{repo}/pulls/{pr}/reviews?per_page=100", pages=True)', 'back = api(f"repos/{repo}/pulls/{pr}/reviews?per_page=100", pages=False)', 0),
 ("approve: owner_read after post", "        if not ok:\n            return 1, [f\"REFUSE: the approval landed", "        if False:\n            return 1, [f\"REFUSE: the approval landed", 0),
 ("approve: body read-back guard", "if cited != {mandate} or not gate.AGENT_DECLARED.search(body) or READ_LINE.findall(body) != [head]:", "if False:", 0),
 ("main: check --no-fetch ignored", "fetch=not args.no_fetch, early=args.early", "fetch=True, early=args.early", 0),
 ("main: check --comment dropped", "comment=args.comment, pull=pull", "comment=None, pull=pull", 0),
 ("main: check --ref ignored", "check(args.repo, args.pr, args.ref,", 'check(args.repo, args.pr, "origin/main",', 0),
 ("main: --pull-json falls back", 'print(f"REFUSE: {args.pull_json} is not a readable JSON file"); return 1', "pull = None", 0),
 ("main: approve --head shape", "if not SHA40.fullmatch(args.head):", "if False:", 0),
 ("main: approve --role ignored", "args.ref, args.role, fetch=not args.no_fetch", 'args.ref, "the class-O read seat", fetch=not args.no_fetch', 0),
 ("main: approve --mandate required-less default", 'a.add_argument("--mandate", type=int)', 'a.add_argument("--mandate", type=int, default=4242)', 0),
 ("main: cross rc", "        print(line)\n        return rc", "        print(line)\n        return 0", 0),
]
surv = 0
try:
    for name, old, new, k in M:
        if old is None:
            f.write_text(src)
        else:
            pos, start = -1, 0
            for _ in range(k + 1):
                pos = src.find(old, start); start = pos + 1
                if pos < 0: break
            if pos < 0 or (cut_a < pos < cut_b):
                print(f"NOSITE   {name}"); continue
            f.write_text(src[:pos] + new + src[pos + len(old):])
        r = subprocess.run([sys.executable, "-I", "tools/pr/outside.py", "--self-test"], cwd=wt, capture_output=True, text=True)
        tail = (r.stdout.strip().splitlines() or ["<no output>"])[-1]
        fails = [l.strip()[:150] for l in r.stdout.splitlines() if "FAIL" in l]
        ok_line = __import__("re").fullmatch(r"outside self-test: [1-9][0-9]* checks, 0 failed", tail) is not None
        alive = r.returncode == 0 and ok_line
        surv += alive and old is not None
        print(f"{'SURVIVED' if alive else 'KILLED  '} {name} | rc {r.returncode} | {tail}" + "".join(f"\n      {x}" for x in fails[:3]))
finally:
    f.write_text(src)
print(f"RESULT hand mutants at {subprocess.run(['git','rev-parse','HEAD'],cwd=wt,capture_output=True,text=True).stdout.strip()}: {surv} survivor(s) of {len(M)-1} (NULL apart)")
