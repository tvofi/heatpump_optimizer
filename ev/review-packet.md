# Review packet #3419
head: 245ddf7876bf9662937d4e9077172e1e3cd2275a
base: 30c785330fc727ae26d6a6d2d51b38f1856fe87c

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=129813215977 success
arch-score / arch-score id=129832751614 success
arm id=129812642922 skipped
budget-raise-gate / budget-raise-gate id=129832750819 success
cancel-superseded id=129832817875 success
codeql id=129832750212 skipped
codeql / Analyze (actions) id=129812789276 success
codeql / Analyze (javascript-typescript) id=129812789213 success
codeql / Analyze (python) id=129812789430 success
gate id=129832750060 success
governance id=129832751274 skipped
governance / delivery-status id=129812789309 success
governance / delivery-status-publish id=129812791621 skipped
governance / env-matrix id=129812789267 success
governance / instrument-self-tests id=129812789341 success
governance / policy-docs id=129812789314 success
governance / record id=129812790846 skipped
governance / wave-script id=129812789072 success
hassfest id=129832750657 skipped
hassfest / hassfest id=129812789230 success
kernel-points id=129832803434 skipped
pr-contract id=129832751251 skipped
pr-contract / pr-contract id=129831763255 success
prelude id=129832808295 success
refresh id=129832749567 success
sweep-self id=129833052281 skipped
tests id=129832773683 skipped
tests / arch-instrument id=129813027308 success
tests / briefs id=129812789116 success
tests / browser id=129813027213 success
tests / ci-ratchet id=129829053968 skipped
tests / claims-autofix id=129823577098 skipped
tests / closure-scope id=129812788955 success
tests / closures id=129813027334 success
tests / closures-autofix id=129827344120 skipped
tests / coverage id=129813027302 success
tests / coverage-ratchet id=129829051330 success
tests / fast (3.14) id=129813027176 success
tests / graders-head-copy id=129829051337 success
tests / lane-proofs id=129829051324 success
tests / mutation id=129812789004 success
tests / mutation-autofix id=129813049317 skipped
tests / mutation-pins id=129813048975 skipped
tests / nightly-ha id=129813029936 skipped
tests / nightly-status id=129812789038 success
tests / replay id=129813030179 skipped
tests / typing id=129813027200 success
validate id=129832750582 skipped
validate / validate-hacs id=129812788925 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 30419b8d: dismissed:R10-RCA-MAIN-SELFTESTS-RED is resume.stage done, and the countermeasure lands in this PR
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/ci/selftest_scope.py record --step prepr --out <f>
             `tools/ci/selftest_scope.py` is in the tree at this head
  ok         tests/env_drift.py
             `tests/env_drift.py` is in the tree at this head
  ok         tools/merge/ledger_merge.py
             `tools/merge/ledger_merge.py` is in the tree at this head
  unverified git status
             `git status` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 -I tools/ci/selftest_scope.py --self-test
             `tools/ci/selftest_scope.py` is in the tree at this head
  ok         python3 -I tools/ci/selftest_scope.py settle
             `tools/ci/selftest_scope.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         tools/ci/selftest_scope.py
             `tools/ci/selftest_scope.py` is in the tree at this head

FIGURES: 8 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.github/workflows/governance.yml b/.github/workflows/governance.yml
index cb6507cad..8a2461d89 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -332,10 +332,15 @@ jobs:
           done
           echo "selftests=${SELFTESTS:-all}: $(wc -l < "$RUNNER_TEMP/selftest-scope.txt") of $(wc -w <<< "$known") gated step(s) run"
 
+      # `settle` rewrites the index after the checkout's last second, so no
+      # traced step's first `git status` re-reads the files the checkout wrote
+      # last (R10-HOTFIX-PREPR-READSET: run 42780661829 put those reads in prepr).
       - name: Install strace for the read-set measurement
         id: strace
         if: env.SELFTEST_TRACE != ''
-        run: sudo apt-get update -q && sudo apt-get install -y -q strace
+        run: |
+          sudo apt-get update -q && sudo apt-get install -y -q strace
+          python3 -I tools/ci/selftest_scope.py settle
 
       # THE FIVE SLOWEST SELF-TESTS START HERE AND ARE READ AT THE END
       # (R10-HOTFIX-SELFTEST-TIMEOUT). Run in line they were most of this
diff --git a/dev/programme/delivery/3419.md b/dev/programme/delivery/3419.md
new file mode 100644
index 000000000..a7cf41b0f
--- /dev/null
+++ b/dev/programme/delivery/3419.md
@@ -0,0 +1 @@
+- [#3419](https://github.com/tvofi/heatpump_optimizer/pull/3419) — **open**, R10-HOTFIX-PREPR-READSET: settle the racily clean index before tracing the self-tests (R10-HOTFIX-PREPR-READSET)
diff --git a/tools/ci/selftest_scope.py b/tools/ci/selftest_scope.py
index 99a69b914..96a18fa8e 100644
--- a/tools/ci/selftest_scope.py
+++ b/tools/ci/selftest_scope.py
@@ -6,6 +6,7 @@
     python3 -I tools/ci/selftest_scope.py ids
     python3 -I tools/ci/selftest_scope.py record [--step ID]... [--out PATH]
     python3 -I tools/ci/selftest_scope.py check --traces DIR [--write PATH]
+    python3 -I tools/ci/selftest_scope.py settle
     python3 -I tools/ci/selftest_scope.py --self-test
 
 WHY (R10-CI-SELFTEST-SCOPE, owner lever 3, #201 comment 6707834331).
@@ -48,6 +49,10 @@ entry. Over-approximation (an entry naming a file no longer read) is safe
 and is reported, not refused. `--write` saves the run's own measurement,
 which main uploads as the `selftest-closures` artifact: commit that file, or
 re-record with `record` (Linux, strace).
+THE SETTLED INDEX, `settle`, runs untraced before any step is (CI's strace
+step; `record` itself): a fresh checkout leaves racily clean index entries,
+whose content the first index-refreshing git command re-reads, so without it
+those reads land in whichever traced step refreshes first.
 
 BLIND SPOTS, stated: a path a process named relative to a working directory
 the trace does not decorate (a non-*at syscall after a chdir) is resolved
@@ -621,10 +626,68 @@ def drift(table: dict | None, measured: dict[str, dict], steps: list[Step]) -> t
 # ---------------------------------------------------------------------------
 # recording: the job, replayed through the same wrapper CI uses
 
+def _index_path(root: Path, env: dict | None = None) -> Path:
+    out = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-path", "index"],
+                         cwd=root, env=env, capture_output=True, text=True).stdout.strip()
+    return Path(out) if out else root / ".git" / "index"
+
+
+def racy_entries(root: Path, env: dict | None = None) -> list[str]:
+    """Tracked files whose mtime second is not before the index's own: git
+    cannot vouch for them from stat data, so the next index-refreshing
+    command (`git status`, `git diff`) opens and hashes each one. The second
+    is the coarser of git's two racy tests (with and without USE_NSEC)."""
+    try:
+        stamp = int(_index_path(root, env).stat().st_mtime)
+    except OSError:
+        return []
+    listed = subprocess.run(["git", "ls-files", "-z"], cwd=root, env=env,
+                            capture_output=True, text=True).stdout.split("\0")
+    racy = []
+    for rel in filter(None, listed):
+        with contextlib.suppress(OSError):
+            if int((root / rel).lstat().st_mtime) >= stamp:
+                racy.append(rel)
+    return sorted(racy)
+
+
+def settle_index(root: Path, env: dict | None = None) -> int:
+    """Rewrite the index in a second later than every tracked file's mtime,
+    so no entry is racily clean when a traced step starts. Without it the
+    content reads of a fresh checkout's last-written files fall to whichever
+    traced process first refreshes the index -- a read set that moves with
+    scheduling, not with the tree (R10-HOTFIX-PREPR-READSET)."""
+    racy = racy_entries(root, env)
+    if not racy:
+        return 0
+    newest = max(int((root / r).lstat().st_mtime) for r in racy if (root / r).exists())
+    if newest > time.time() + 5:
+        print(f"selftest_scope: settle: {racy[0]} is stamped in the future, so no index can vouch for it",
+              file=sys.stderr)
+        return 1
+    # File and index stamps come from the kernel's coarse clock, which lags
+    # time.time() by up to a tick: a rewrite just past the second boundary
+    # can still be stamped in the old second, so wait past it and retry.
+    for _ in range(3):
+        while time.time() < newest + 1.1:
+            time.sleep(0.05)
+        subprocess.run(["git", "update-index", "-q", "--really-refresh", "--force-write-index"],
+                       cwd=root, env=env, capture_output=True)
+        left = racy_entries(root, env)
+        if not left:
+            return 0
+        newest = max(int((root / r).lstat().st_mtime) for r in left if (root / r).exists())
+    print(f"selftest_scope: settle left {len(left)} racily clean index entr(ies), e.g. {left[0]}",
+          file=sys.stderr)
+    return 1
+
+
 def record(root: Path, only: list[str] | None, out: Path) -> int:
     if shutil.which("strace") is None:
         print("selftest_scope: record needs strace (Linux)", file=sys.stderr)
         return 2
+    if settle_index(root):
+        return 1
     steps = workflow_steps(root)
     gaps = wiring_gaps(steps)
     if gaps:
@@ -1116,6 +1179,9 @@ def self_test(wrapper: Path = ROOT / WRAPPER) -> int:
         if shutil.which("strace") is None or _traced():
             print("  skip the recorder end to end: no strace here, or this run is itself traced")
         else:
+            ns = _index_path(root).stat().st_mtime_ns
+            os.utime(root / "tools/x/a.py", ns=(ns, ns))
+            racy_before = racy_entries(root)
             out = io.StringIO()
             scratch, tempfile.tempdir = tempfile.tempdir, str(root.parent / f"{root.name}-tmp")
             os.makedirs(tempfile.tempdir)
@@ -1136,6 +1202,8 @@ def self_test(wrapper: Path = ROOT / WRAPPER) -> int:
             ck("record: a detached self-test's reads are its waiter's",
                "tools/x/slow.sh" in slow_e.get("files", ()) and "tools/x/slow.sh" not in a_e.get("files", ()))
             ck("record: it leaves no trace directory behind", left == [])
+            ck("record: it settles a racy index before tracing (racy before, none after)",
+               "tools/x/a.py" in racy_before and racy_entries(root) == [])
             part = root / "part.json"
             part.write_text(json.dumps({"steps": {"slow": {"run_sha": "old", "files": [], "probes": [],
                                                            "dirs": [], "index": False, "objects": False}}}))
@@ -1312,6 +1380,51 @@ def self_test(wrapper: Path = ROOT / WRAPPER) -> int:
         m = re.search(r'^UNTRACED="([^"]*)"$', wrapper.read_text(), re.M)
         ck("wrapper: its UNTRACED list is UNGATED", bool(m) and sorted(m.group(1).split()) == sorted(UNGATED))
 
+    # A racily clean index (R10-HOTFIX-PREPR-READSET): entries whose file
+    # mtime second is not before the index's, which a fresh checkout leaves
+    # for the files it wrote last. The first index-refreshing git command
+    # re-reads each one's content, so those reads land in whichever traced
+    # step runs it first (main run 42780661829: prepr's `git status`).
+    # `settle` clears them before any step is traced; a racy fixture is its
+    # control.
+    with tempfile.TemporaryDirectory() as td, throwaway_git_environ():
+        root = Path(os.path.realpath(td))
+        env = throwaway_git_init(root, "-q")
+        names = [f"docs/f{n}.md" for n in range(3)]
+        for rel in names:
+            (root / rel).parent.mkdir(parents=True, exist_ok=True)
+            (root / rel).write_text(f"{rel}\n")
+        subprocess.run(["git", "add", "-A"], cwd=root, env=env, check=True)
+
+        def make_racy() -> None:   # every file stamped with the index's own mtime
+            ns = _index_path(root, env).stat().st_mtime_ns
+            for rel in names:
+                os.utime(root / rel, ns=(ns, ns))
+        make_racy()
+        ck("racy_entries: files stamped in the index's own second are named (the control)",
+           racy_entries(root, env) == names)
+        traced_status = shutil.which("strace") is not None and not _traced()
+
+        def status_reads() -> set[str]:
+            log = root.parent / f"{root.name}-status.trace"
+            subprocess.run(["strace", "-f", "-q", "-y", "-e", "trace=%file", "-o", str(log),
+                            "git", "status", "--porcelain"], cwd=root, env=env, capture_output=True)
+            got = fold_trace(log.read_text().splitlines(), root, set(names), {"docs"}, *_git_dirs(root))
+            log.unlink()
+            return got["files"]
+        if traced_status:
+            make_racy()
+            ck("a git status over that racy index opens every racy file (the control)",
+               status_reads() == set(names))
+            make_racy()
+        rc = settle_index(root, env)
+        ck(f"settle: no index entry is left racily clean (rc={rc})", rc == 0 and racy_entries(root, env) == [])
+        if traced_status:
+            ck("and a git status after it opens no tracked file", status_reads() == set())
+        else:
+            print("  skip the traced git status over a racy index: no strace here, or this run is itself traced")
+        ck("settle over an index with no racy entry changes nothing (rc 0)", settle_index(root, env) == 0)
+
     # The live table names no landed retired path (tests/layout.py's guard
     # refuses a new reference to one, and a diff re-adding one), and the
     # list it is checked against is not empty (the check's own precondition).
@@ -1343,6 +1456,8 @@ def main(argv: list[str], root: Path = ROOT) -> int:
         return 0
     if argv == ["static"]:
         return static_check(root)
+    if argv == ["settle"]:
+        return settle_index(root)
     if argv[:1] == ["select"] and ("--base" in argv or "--change" in argv):
         steps = workflow_steps(root)
         if "--change" in argv:          # a hypothetical diff: STATUS:PATH ...
diff --git a/tools/ci/selftest_scope_mutants.sh b/tools/ci/selftest_scope_mutants.sh
index 6fdc634ba..8ec9fcfcd 100644
--- a/tools/ci/selftest_scope_mutants.sh
+++ b/tools/ci/selftest_scope_mutants.sh
@@ -39,6 +39,7 @@ scope_mutant "a partial trace read whole" 'return "" if seen["root"] in seen["en
 scope_mutant "a signal death read as partial" '(?:exited with|killed by) ' '(?:exited with) '
 scope_mutant "check drops the trace refusals" 'refuse = broken + refuse' 'refuse = refuse'
 scope_mutant "record passes over a broken trace" 'return 1 if failed or broken else 0' 'return 1 if failed else 0'
+scope_mutant "settle never rewrites the index" '["git", "update-index", "-q", "--really-refresh", "--force-write-index"]' '["true"]'
 wrapper_mutant "only launch untraced (the incident's wrapper)" 'case "$UNTRACED" in *" ${GITHUB_ACTION:-} "*)' 'case " launch " in *" ${GITHUB_ACTION:-} "*)'
 wrapper_mutant "no strace exec'd anyway" 'if ! command -v strace > /dev/null 2>&1; then' 'if false; then'
 wrapper_mutant "exit lines suppressed (-qq)" 'exec strace -f -q -y' 'exec strace -f -qq -y'

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
