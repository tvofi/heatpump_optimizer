#!/usr/bin/env python3
"""Reviewer's mutation driver: one predicate replaced, the owning self-test run, RESULT printed.
usage: mutate.py <worktree> <out> <id>...   (ids from MUTANTS)"""
import re, subprocess, sys, pathlib

T = "tools/audit/seat/merge_train.py"
P = "tools/audit/seat/merge_pr.sh"
R = "tools/audit/seat/remerge_main.sh"
ST = {T: ["python3", "-I", T, "--self-test"], P: ["bash", P, "--self-test"],
      R: ["python3", "-I", "tools/audit/seat/remerge_main_selftest.py"]}
# id: (file, old, new)   old must occur exactly once; DEL_LINE deletes the whole line holding old
DEL = object()
MUTANTS = {
 "t01-cross-false": (T, 'cross = facts["head_repo"] != self.repo', 'cross = False'),
 "t02-admit-any-head": (T, ' and f" at {h}: " in str(ln)', ''),
 "t03-rc3-admits": (T, 'ok = rc == 0 and', 'ok = rc in (0, 3) and'),
 "t04-allowlist-old-path": (T, '"dev/governance/config/outside_contributors.json"', '"dev/governance/outside_contributors.json"'),
 "t05-no-fork-post-off": (T, 'if fork is not None:\n            raise Stop("approve", f"{what} is never', 'if False:\n            raise Stop("approve", f"{what} is never'),
 "t06-ok-not-true-off": (T, 'if ok is not True:', 'if False:'),
 "t07-blob-compare-off": (T, 'if c1 or c2 or not is_sha(want.strip()) or want.strip() != have.strip():', 'if False:'),
 "t08-contracted-pop-dropped": (T, 'self.contracted.pop(pr, None)', 'pass'),
 "t09-_approve-contract-guard-off": (T, 'if fork is not None and self.contracted.get(pr) != h:', 'if False:'),
 "t10-approve-contract-call-off": (T, 'if fork is not None:\n            self.log(f"#{pr} outside contract holds', 'if False:\n            self.log(f"#{pr} outside contract holds'),
 "t11-_approve-fork-owner-arm-off": (T, 'if fork is not None:\n            # ONE path', 'if False:\n            # ONE path'),
 "t12-carry-owner-fork-arm-off": (T, 'if self.fork_head(pr) is not None:\n            return no(', 'if False:\n            return no('),
 "t13-policy-due-fork-arm-off": (T, 'if self.fork_head(pr) is not None:\n            # Policy paths are class R', 'if False:\n            # Policy paths are class R'),
 "t14-push-park-off": (T, 'if failed and fork and " at push" in failed:', 'if False:'),
 "t15-outside-prefix-dropped": (T, 'str(ln).startswith("OUTSIDE: ") and ', ''),
 "t16-fork-name-check-off": (T, 'if not FORK_REPO.fullmatch(name) or name == self.repo or not ref or ref != ref.strip():', 'if False:'),
 "t17-main-fetch-fail-ignored": (T, 'if code:\n            raise Stop("outside", "origin/main could not be fetched', 'if False:\n            raise Stop("outside", "origin/main could not be fetched'),
 "t18-fork-conflict-park-off": (T, 'if "MERGE CONFLICT" in o and fork:', 'if False:'),
 "t19-main-copies-drop-codeowners": (T, '".github/CODEOWNERS", "tools/pr/app_approve.sh"', '"tools/pr/app_approve.sh"'),
 "t20-unread-pull-ours": (T, 'if not isinstance(pull, dict) or not isinstance(pull.get("head"), dict):\n            raise Stop("outside", f"#{pr} could not be read', 'if False:\n            raise Stop("outside", f"#{pr} could not be read'),
 "p01-cross-false": (P, 'cross = facts["head_repo"] != repo', 'cross = False'),
 "r01-first-parent-line": (R, 'rev-list --first-parent origin/main | grep -qx "$p2"', DEL),
 "r02-p1-old": (R, ' && [ "$p1" = "$old" ]', ''),
}

def main():
    wt, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    for mid in sys.argv[3:]:
        f, old, new = MUTANTS[mid]
        p = wt / f
        src = p.read_text()
        n = src.count(old)
        if n != 1:
            print(f"RESULT {mid}: NOT-APPLIED ({n} occurrences of the target)", flush=True)
            continue
        if new is DEL:
            lines = src.split("\n")
            mut = "\n".join(l for l in lines if old not in l)
        else:
            mut = src.replace(old, new)
        p.write_text(mut)
        try:
            r = subprocess.run(ST[f], cwd=wt, capture_output=True, text=True, timeout=900)
            o = r.stdout + r.stderr
        except subprocess.TimeoutExpired as e:
            o, r = "TIMEOUT", None
        finally:
            p.write_text(src)
        (out / f"mut_{mid}.txt").write_text(o[-60000:])
        fails = [l for l in o.splitlines() if re.match(r"^ *FAIL", l)]
        summ = next((l for l in reversed(o.splitlines()) if "checks," in l), "(no summary line)")
        verdict = "KILLED" if fails or (r is not None and r.returncode != 0) else "SURVIVED"
        print(f"RESULT {mid}: {verdict} rc={r.returncode if r else 'timeout'} FAIL-lines={len(fails)} | {summ.strip()}", flush=True)
        for l in fails[:3]:
            print(f"    {l.strip()[:230]}", flush=True)

main()
