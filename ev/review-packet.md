# Review packet #2969
head: 3e5b8b7c5b3746230db1920968452931ff5fba1b
base: e5ddba1fad5e6eccfeceaeaaa249bc459963405b

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=123753481863 skipped
cancel-superseded id=123753490763 queued
prelude id=123753491008 queued
refresh id=123753491056 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/audit/seat/r10_stamp_round_mutants.py
             `tools/audit/seat/r10_stamp_round_mutants.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/r10_stamp_round_mutants.py --null e5ddba1fad5e6eccfeceaeaaa249bc459963405b
             `tools/audit/seat/r10_stamp_round_mutants.py` is in the tree at this head
  ok         python3 tools/release/stamp.py --self-test
             `tools/release/stamp.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs --budgets
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         python3 tools/release/stamp.py --bump major --title t --dry-run
             `tools/release/stamp.py` is in the tree at this head

FIGURES: 9 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.github/workflows/governance.yml b/.github/workflows/governance.yml
index b9613b21d..edb801101 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -767,6 +767,16 @@ jobs:
           python3 -I tools/audit/seat/r10_roster_ops_mutants.py --self-test | tee "$RUNNER_TEMP/r10-roster-ops-mutants-self-test.txt"
           grep -Eq '^r10_roster_ops_mutants self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/r10-roster-ops-mutants-self-test.txt"
 
+      # stamp.py's round-close sweep (R10-STAMP-ROUND-MAJOR, decision 0016),
+      # for the same reason: CI pins its plants' preconditions and the null
+      # grid's own detector, never the sweep itself.
+      - name: Show the stamp round-close mutation harness pinning its own plants
+        if: ${{ !cancelled() }}
+        run: |
+          set -o pipefail
+          python3 -I tools/audit/seat/r10_stamp_round_mutants.py --self-test | tee "$RUNNER_TEMP/r10-stamp-round-mutants-self-test.txt"
+          grep -Eq '^r10_stamp_round_mutants self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/r10-stamp-round-mutants-self-test.txt"
+
       # The ledger's mutation sweep (R10-ORCH-LEDGER), for the same reason:
       # CI pins its plants' preconditions, never the sweep itself.
       - name: Show the ledger mutation harness pinning its own plants
diff --git a/dev/governance/decisions/0016-a-major-version-is-a-closed-audit-round.md b/dev/governance/decisions/0016-a-major-version-is-a-closed-audit-round.md
new file mode 100644
index 000000000..7dd33b7e9
--- /dev/null
+++ b/dev/governance/decisions/0016-a-major-version-is-a-closed-audit-round.md
@@ -0,0 +1,51 @@
+# 0016 — A major version is a closed audit round
+
+Status: recorded 2026-10-29 from the repository owner's ruling of that day.
+Lands as roster group R10-STAMP-ROUND-MAJOR, under the mandate in force with
+scope all (#201 comment 6329234399), and merges before round 10's closeout
+stamp.
+
+## Context
+
+`tools/release/stamp.py` took `--bump patch|minor|major` and nothing tied a
+major to anything, so a version number said nothing about which audit round a
+release has passed.
+
+## Decision
+
+The owner, verbatim (tvofi, 2026-10-29): *"I am also changing the versioning,
+each full audit round means a new major version, and it should match the round
+number on closeout, so the programme closeout release will be v10.0.0"*.
+
+1. **The closeout stamp of audit round N is N.0.0**, whatever the current
+   major: round 10's programme closeout is v10.0.0.
+2. **Between closeouts a stamp is `--bump minor` or `--bump patch`**, as
+   before; the next stamp, for the Marketplace work, is v7.1.0 by
+   `--bump minor`.
+3. **No other major exists.** A plain major bump is refused, so no stamp can
+   reach a major without closing a round.
+
+## How stamp.py enforces it
+
+`stamp.py --round-close N` sets the version through `next_version`, which
+refuses, before anything is fetched or written:
+
+- an N not above the current major (a round closes once, upward);
+- an N that is not the round of the newest roster, read through
+  `roster_lib.roster_path` and `roster_round`, and a checkout with no roster;
+- an N given beside `--bump`.
+
+`--bump major` stays a parseable choice and refuses with a pointer to
+`--round-close`; `bump()` itself has no major arm, so a caller cannot skip
+`next_version`. Rule 3's tag checks then apply to N.0.0 as to any version.
+`stamp.py --self-test` drives each refusal, and a null control over patch and
+minor.
+
+## Consequences
+
+- Versions jump at a closeout (7.x to 10.0.0): the gap is the rule, not a
+  missing release.
+- Rule 4 of `CLAUDE.md` is unchanged: versions are still assigned after the
+  merge, by `stamp.py`, and never in a branch.
+- `dev/governance/` is `@tvofi`'s in `.github/CODEOWNERS`: this record merges
+  on the owner's approving review, or under a mandate in force with scope all.
diff --git a/dev/programme/delivery/2969.md b/dev/programme/delivery/2969.md
new file mode 100644
index 000000000..d4b7452b2
--- /dev/null
+++ b/dev/programme/delivery/2969.md
@@ -0,0 +1 @@
+- [#2969](https://github.com/tvofi/heatpump_optimizer/pull/2969) — **open**, R10-STAMP-ROUND-MAJOR: stamp the round closeout as a major version (R10-STAMP-ROUND-MAJOR)
diff --git a/tests/closures.json b/tests/closures.json
index 8b3f2f339..76e4815b7 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3608,6 +3608,7 @@
    "tools/audit/seat/r10_ledger_mutants.py",
    "tools/audit/seat/r10_roster_ops_mutants.py",
    "tools/audit/seat/r10_roster_sync_mutants.py",
+   "tools/audit/seat/r10_stamp_round_mutants.py",
    "tools/audit/seat/record_row.py",
    "tools/audit/seat/review_carry.py",
    "tools/audit/seat/review_packet.py",
diff --git a/tools/audit/seat/r10_stamp_round_mutants.py b/tools/audit/seat/r10_stamp_round_mutants.py
new file mode 100755
index 000000000..1c79b3e84
--- /dev/null
+++ b/tools/audit/seat/r10_stamp_round_mutants.py
@@ -0,0 +1,157 @@
+#!/usr/bin/env python3
+"""R10-STAMP-ROUND-MAJOR: every plant stamp.py's self-test must refuse.
+
+Metric, one line per plant: `RESULT mutant=<name> rc=<rc> fails=<n>`, then the
+failing check names. Each plant is one exact one-occurrence replacement in
+tools/release/stamp.py; the driver applies it, runs `stamp.py --self-test`, and
+restores the file byte for byte. It refuses to start when the file differs from
+HEAD, so a restore cannot overwrite work. Expected: every plant rc=1 with
+fails>=1 -- a FAIL line, not a crash (a crash is rc=1 with fails=0 and prints
+its tail).
+
+Plants, one per predicate of decision 0016's `next_version` and its wiring:
+  R1  a round close stamps N.1.0 instead of N.0.0.
+  R2  a round equal to the current major is let through (`<=` to `<`).
+  R3  the roster's round is never compared (also passes an unreadable roster).
+  R4  --round-close beside --bump is let through.
+  R5  --bump major is let through to bump(), which has no major arm.
+  R6  main() drops --round-close before next_version.
+
+    python3 tools/audit/seat/r10_stamp_round_mutants.py [plant ...]
+    python3 tools/audit/seat/r10_stamp_round_mutants.py --null [<base rev>]
+    python3 tools/audit/seat/r10_stamp_round_mutants.py --self-test
+
+Null control: `--null` runs the self-test with no plant, which must print
+rc=0 fails=0; given a base revision it also prints every patch and minor bump
+over a version grid from that revision's stamp.py and from the tree's, through
+`next_version` where it exists, and reports `RESULT null grid=<n> differ=<d>`:
+d=0 is patch and minor behaving exactly as before. `--self-test` does not run
+the plants and pins the preconditions instead: every anchor occurs exactly
+once in the target, and the grid comparison counts a planted difference.
+"""
+import importlib.util
+import subprocess
+import sys
+import tempfile
+from pathlib import Path
+
+ROOT = Path(__file__).resolve().parents[3]
+TARGET = "tools/release/stamp.py"
+
+PLANTS = {
+    "R1": ('return f"{round_close}.0.0", None', 'return f"{round_close}.1.0", None'),
+    "R2": ("if round_close <= major:", "if round_close < major:"),
+    "R3": ("if round_close != roster_round:", "if False:"),
+    "R4": ('        if part is not None:\n            return None, "--round-close',
+           '        if False:\n            return None, "--round-close'),
+    "R5": ('if part == "major":\n        return None', 'if False:\n        return None'),
+    "R6": ("nxt, why = next_version(current, args.bump, args.round_close,",
+           "nxt, why = next_version(current, args.bump, None,"),
+}
+
+GRID = [f"{a}.{b}.{c}" for a in range(12) for b in (0, 1, 9, 10, 99)
+        for c in (0, 1, 5, 9, 10, 99)]
+
+
+def target_self_test():
+    r = subprocess.run([sys.executable, TARGET, "--self-test"], cwd=ROOT,
+                       capture_output=True, text=True)
+    fails = [ln.strip() for ln in r.stdout.splitlines() if ln.startswith("  FAIL")]
+    return r.returncode, fails, (r.stdout + r.stderr).strip().splitlines()[-3:]
+
+
+def report(name, rc, fails, tail):
+    print(f"RESULT mutant={name} rc={rc} fails={len(fails)}")
+    for f in fails:
+        print(f"    {f}")
+    if rc and not fails:
+        print("    crash tail:")
+        for ln in tail:
+            print(f"      {ln}")
+
+
+def grid_rows(path):
+    """`version part next` for every patch and minor bump over GRID, read from
+    the stamp.py at `path`: through next_version when it has one, else bump."""
+    spec = importlib.util.spec_from_file_location("stamp_under_test", path)
+    mod = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(mod)
+    nv = getattr(mod, "next_version", None)
+    return [f"{v} {p} {nv(v, p, None, None)[0] if nv else mod.bump(v, p)}"
+            for v in GRID for p in ("patch", "minor")]
+
+
+def differ(a, b):
+    return sum(x != y for x, y in zip(a, b)) + abs(len(a) - len(b))
+
+
+def null(base):
+    rc, fails, tail = target_self_test()
+    report("null", rc, fails, tail)
+    if base is None:
+        return 1 if rc or fails else 0
+    src = subprocess.run(["git", "show", f"{base}:{TARGET}"], cwd=ROOT,
+                         capture_output=True, text=True, check=True).stdout
+    with tempfile.TemporaryDirectory() as d:
+        old = Path(d) / "stamp_base.py"
+        old.write_text(src)
+        before, after = grid_rows(old), grid_rows(ROOT / TARGET)
+    d = differ(before, after)
+    print(f"RESULT null grid={len(after)} differ={d}")
+    return 1 if rc or fails or d else 0
+
+
+def self_test():
+    passed = failed = 0
+
+    def ck(name, ok):
+        nonlocal passed, failed
+        passed, failed = passed + bool(ok), failed + (not ok)
+        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
+
+    text = (ROOT / TARGET).read_text()
+    for name, (old, new) in PLANTS.items():
+        ck(f"{name}: its anchor occurs exactly once", text.count(old) == 1)
+        compile(text.replace(old, new), TARGET, "exec")
+    rows = grid_rows(ROOT / TARGET)
+    ck("the grid covers patch and minor for every version", len(rows) == 2 * len(GRID))
+    planted = rows[:]
+    planted[0] = planted[0] + "x"
+    ck("the grid comparison counts a planted difference, and none without one",
+       differ(rows, planted) == 1 and differ(rows, rows) == 0)
+    print(f"r10_stamp_round_mutants self-test: {passed + failed} checks, {failed} failed")
+    return 1 if failed else 0
+
+
+def main(argv):
+    path = ROOT / TARGET
+    if argv == ["--self-test"]:
+        return self_test()
+    if subprocess.run(["git", "diff", "--quiet", "HEAD", "--", TARGET], cwd=ROOT).returncode:
+        print(f"refused: {TARGET} differs from HEAD; a restore would overwrite it")
+        return 2
+    if argv[:1] == ["--null"]:
+        return null(argv[1] if len(argv) > 1 else None)
+    names = argv or list(PLANTS)
+    unknown = [n for n in names if n not in PLANTS]
+    if unknown:
+        print(f"refused: unknown plant(s) {unknown}; known: {list(PLANTS)}")
+        return 2
+    original = path.read_bytes()
+    survivors = []
+    try:
+        for name in names:
+            old, new = PLANTS[name]
+            path.write_text(original.decode().replace(old, new))
+            rc, fails, tail = target_self_test()
+            report(name, rc, fails, tail)
+            if not fails:
+                survivors.append(name)
+    finally:
+        path.write_bytes(original)
+    print(f"plants: {len(names)}, without a FAIL line: {survivors or 'none'}")
+    return 1 if survivors else 0
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/tools/release/stamp.py b/tools/release/stamp.py
index aad551429..cd99f3abe 100755
--- a/tools/release/stamp.py
+++ b/tools/release/stamp.py
@@ -2,8 +2,16 @@
 """Stamp a release on main. This is the only way a version number is assigned.
 
     python tools/release/stamp.py --bump patch|minor --title "<what shipped>" [--push] [--dry-run]
+    python tools/release/stamp.py --round-close N --title "<what shipped>" [--push] [--dry-run]
     python tools/release/stamp.py --self-test
 
+A major version is a closed audit round (decision 0016, tvofi 2026-10-29): the
+programme closeout of round N stamps N.0.0 through --round-close N, which
+refuses an N not above the current major, an N that is not the round of the
+newest roster (`roster_lib`), and an N given beside --bump. Between closeouts a
+stamp is --bump minor or --bump patch; --bump major refuses, naming
+--round-close, so no major skips the rule (`next_version`).
+
 Versions are assigned at merge time, never in a branch: four branches each
 picking "the next version" once cost real cycles, and a stamp that skipped a
 claim file turned main red. So every rule below is a refusal, not a warning:
@@ -24,7 +32,8 @@ claim file turned main red. So every rule below is a refusal, not a warning:
      with its reason, never an exception: rule 2 is a refusal, and a
      refusal that crashes instead cannot be overridden.
   3. The next version is greater than VERSION and than every existing tag, and
-     its tag exists neither locally nor on origin.
+     its tag exists neither locally nor on origin; a round close's version is
+     `next_version`'s, refused as above before the tags are read.
   4. RELEASE_NOTES.md opens with a '## v<next>' section whose body mentions
      every PR merged since the last tag -- a stamp covers everything
      unstamped, whoever merged it. The merges are read off main's own
@@ -288,16 +297,56 @@ def refresh_origin(runner=None) -> str | None:
 # --- pure pieces (covered by --self-test) -----------------------------------
 
 def bump(version: str, part: str) -> str:
+    """patch or minor. There is no major arm: a major is a closed audit round
+    (decision 0016), assigned by `next_version` from --round-close alone."""
     major, minor, patch = (int(x) for x in version.strip().split("."))
     if part == "patch":
         return f"{major}.{minor}.{patch + 1}"
     if part == "minor":
         return f"{major}.{minor + 1}.0"
-    if part == "major":
-        return f"{major + 1}.0.0"
     raise ValueError(part)
 
 
+def next_version(current: str, part: str | None, round_close: int | None,
+                 roster_round: int | None) -> tuple[str | None, str | None]:
+    """The version this stamp assigns, or why it refuses: `(next, None)` or
+    `(None, why)`. Decision 0016 (tvofi, 2026-10-29): each full audit round
+    is a major version equal to the round number at its closeout, so
+    `--round-close N` stamps N.0.0 and refuses an N that is not above the
+    current major, an N the roster's round contradicts (`roster_round` None,
+    an unreadable roster, refuses too), and an N given beside --bump. A
+    plain `--bump major` refuses, so no major skips the rule."""
+    if round_close is not None:
+        if part is not None:
+            return None, "--round-close sets the whole version; it takes no --bump"
+        major = version_tuple(current)[0]
+        if round_close <= major:
+            return None, (f"round {round_close} is not above the current major {major} "
+                          f"(VERSION {current.strip()}); a round closes once, upward")
+        if round_close != roster_round:
+            seen = "no readable roster" if roster_round is None else f"the roster's round {roster_round}"
+            return None, (f"--round-close {round_close} disagrees with {seen}; "
+                          "the major is the round being closed")
+        return f"{round_close}.0.0", None
+    if part == "major":
+        return None, ("a major version is a closed audit round (decision 0016): "
+                      "use --round-close <round>, not --bump major")
+    if part is None:
+        return None, "one of --bump patch|minor or --round-close <round> is required"
+    return bump(current, part), None
+
+
+def roster_round_at(root: Path) -> int | None:
+    """The round of the newest roster in the checkout at `root`, through
+    roster_lib's own `roster_path` and `roster_round`; None when there is none."""
+    sys.path.insert(0, str(ROOT / "tools" / "audit" / "seat"))
+    import roster_lib
+    try:
+        return roster_lib.roster_round(roster_lib.roster_path(str(root)))
+    except roster_lib.RosterNotFound:
+        return None
+
+
 def version_tuple(v: str) -> tuple[int, int, int]:
     a, b, c = (int(x) for x in v.strip().lstrip("v").split("."))
     return a, b, c
@@ -721,7 +770,53 @@ def self_test() -> int:
 
     check("bump patch", bump("6.2.12", "patch") == "6.2.13")
     check("bump minor", bump("6.2.12", "minor") == "6.3.0")
-    check("bump major", bump("6.2.12", "major") == "7.0.0")
+    # Decision 0016: a major is a closed audit round, never a bump. A plain
+    # `--bump major` refuses with a pointer to --round-close, which takes the
+    # round and refuses a number the roster or VERSION contradicts.
+    check("round close: 7.1.0 closing round 10 stamps 10.0.0",
+          next_version("7.1.0", None, 10, 10) == ("10.0.0", None))
+    check("round close: a round not above the current major refuses",
+          next_version("7.1.0", None, 7, 7)[0] is None
+          and next_version("10.0.0", None, 10, 10)[0] is None
+          and next_version("9.3.1", None, 10, 10)[0] == "10.0.0")
+    check("round close: a round the roster disagrees with refuses",
+          next_version("7.1.0", None, 9, 10)[0] is None
+          and "roster" in (next_version("7.1.0", None, 9, 10)[1] or ""))
+    check("round close: a roster that cannot be read refuses, never defaults",
+          next_version("7.1.0", None, 10, None)[0] is None)
+    check("round close: combined with --bump refuses",
+          next_version("7.1.0", "minor", 10, 10)[0] is None
+          and next_version("7.1.0", "patch", 10, 10)[0] is None)
+    try:
+        _major = next_version("7.0.5", "major", None, None)
+    except ValueError as _e:
+        _major = ("raised", str(_e))
+    check("bump major refuses, naming --round-close",
+          _major[0] is None and "--round-close" in (_major[1] or ""))
+    _bumped_major = False
+    try:
+        bump("7.0.5", "major")
+        _bumped_major = True
+    except ValueError:
+        pass
+    check("bump() itself has no major arm, so no caller can skip next_version", not _bumped_major)
+    check("bump minor on 7.0.5 gives 7.1.0, patch 7.0.6, through next_version",
+          next_version("7.0.5", "minor", None, None) == ("7.1.0", None)
+          and next_version("7.0.5", "patch", None, None) == ("7.0.6", None))
+    check("neither flag refuses", next_version("7.0.5", None, None, None)[0] is None)
+    with tempfile.TemporaryDirectory() as _rd:
+        _rdir = Path(_rd) / "dev" / "programme" / "rosters"
+        _rdir.mkdir(parents=True)
+        for _n in ("wave-r9-groups.json", "wave-r10-groups.json", "critical-path.json"):
+            (_rdir / _n).write_text("{}")
+        _r10 = roster_round_at(Path(_rd))
+        (_rdir / "wave-r10-groups.json").unlink()
+        _r9 = roster_round_at(Path(_rd))
+        for _n in ("wave-r9-groups.json",):
+            (_rdir / _n).unlink()
+        _none = roster_round_at(Path(_rd))
+    check("roster round: the newest roster's round, read through roster_lib, None when absent",
+          (_r10, _r9, _none) == (10, 9, None))
     check("tag order", version_tuple("v6.2.12") > version_tuple("v6.2.9"))
     notes = "# Notes\n\n## v6.2.13\n\n### T\n\nB (#170) and (#171).\n\n## v6.2.12\n\nold\n"
     check("notes: first section found", notes_section(notes, "6.2.13") == "### T\n\nB (#170) and (#171).")
@@ -1121,7 +1216,6 @@ def self_test() -> int:
     check("push: a failed refresh is reported, not raised",
           "could not refresh" in (refresh_origin(runner=_refused) or ""))
 
-    import tempfile
     with tempfile.TemporaryDirectory() as _d:
         _key, _hosts = Path(_d) / "stamp.key", Path(_d) / "hosts"
         _key.write_text("k")
@@ -1714,6 +1808,9 @@ def self_test() -> int:
           and wait_gate("new5678", gate=lambda h: (False, "ci.yml push run's gate for HEAD "
                                                           "concluded ['failure']"),
                         sleep=lambda s: 1 / 0, clock=lambda: 0)[0] is False)
+    check("round close: main takes the version from next_version, the round from the roster",
+          "next_version(current, args.bump, args.round_close," in _main_src
+          and "roster_round_at(ROOT)" in _main_src)
     print(f"RESULT stamp_self_test={'pass' if ok else 'fail'}")
     return 0 if ok else 1
 
@@ -2346,7 +2443,11 @@ def stamp_message(nxt: str, title: str) -> str:
 
 def main() -> int:
     ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
-    ap.add_argument("--bump", choices=("patch", "minor", "major"))
+    ap.add_argument("--bump", choices=("patch", "minor", "major"),
+                    help="patch or minor; major refuses, pointing at --round-close (decision 0016)")
+    ap.add_argument("--round-close", type=int, metavar="N",
+                    help="close audit round N: stamp N.0.0; N must be above the current major "
+                         "and equal the roster's round, and takes no --bump")
     ap.add_argument("--title", help="what shipped, for the commit subject and the claim files")
     ap.add_argument("--push", action="store_true", help="push the commit and the tag to origin")
     ap.add_argument("--push-key", metavar="PATH",
@@ -2366,8 +2467,8 @@ def main() -> int:
     args = ap.parse_args()
     if args.self_test:
         return self_test()
-    if not args.bump or not args.title:
-        ap.error("--bump and --title are required (or --self-test)")
+    if not (args.bump or args.round_close is not None) or not args.title:
+        ap.error("--bump or --round-close, and --title, are required (or --self-test)")
     why = title_refusal(args.title)
     if why:
         raise Refuse("title", why + " would publish this host; nothing was written")
@@ -2378,6 +2479,15 @@ def main() -> int:
         if problem:
             raise Refuse("push-key", problem + "; nothing was written, and origin is not a fallback")
 
+    # Rule 3's version, decided before anything is fetched: a --bump major, or a
+    # round the roster or VERSION contradicts, refuses at once (decision 0016).
+    # Rule 1 then proves this checkout -- its VERSION and roster -- is origin/main.
+    current = VERSION_FILE.read_text().strip()
+    nxt, why = next_version(current, args.bump, args.round_close,
+                            roster_round_at(ROOT) if args.round_close is not None else None)
+    if nxt is None:
+        raise Refuse(3, why + "; nothing was written")
+
     # Rule 1: a fetched, clean checkout of origin/main.
     sh("git", "fetch", "origin", "--quiet", "--tags")
     head = sh("git", "rev-parse", "HEAD").strip()
@@ -2397,8 +2507,6 @@ def main() -> int:
         print(f"WARNING: stamping a main whose gate is not green: {why}")
 
     # Rule 3: the next version is new, and above every tag.
-    current = VERSION_FILE.read_text().strip()
-    nxt = bump(current, args.bump)
     tags = [t for t in sh("git", "tag", "--list").split() if TAG_RE.match(t)]
     remote = [t for t in (l.split("refs/tags/")[1] for l in sh("git", "ls-remote", "--tags", "origin").splitlines()
                             if "refs/tags/v" in l and not l.endswith("^{}")) if TAG_RE.match(t)]

