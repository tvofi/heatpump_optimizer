# Review packet #3242
head: f7e3ed1a8aefc03ccc49bf72cb326bea5f207767
base: 862affd07d2ce3430c200d4f09aa6e16934b5c4d

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=128050040256 success
arch-score / arch-score id=128086484713 success
arm id=128048775051 skipped
budget-raise-gate / budget-raise-gate id=128086565123 success
cancel-superseded id=128086483977 success
codeql id=128086526966 skipped
codeql / Analyze (actions) id=128068507814 success
codeql / Analyze (javascript-typescript) id=128068507088 success
codeql / Analyze (python) id=128068509464 success
gate id=128086483664 success
governance id=128086485216 skipped
governance / delivery-status id=128068507251 success
governance / delivery-status-publish id=128068507252 skipped
governance / env-matrix id=128068506278 success
governance / instrument-self-tests id=128068504029 success
governance / policy-docs id=128068507487 success
governance / record id=128068506015 skipped
governance / wave-script id=128068507368 success
hassfest id=128086485001 skipped
hassfest / hassfest id=128068506822 success
kernel-points id=128086485263 skipped
pr-contract id=128086485633 skipped
pr-contract / pr-contract id=128083535758 success
prelude id=128086484485 success
refresh id=128086531530 success
tests id=128086485575 skipped
tests / arch-instrument id=128068507782 success
tests / briefs id=128068507032 success
tests / browser id=128068507968 success
tests / ci-ratchet id=128068511746 skipped
tests / claims-autofix id=128068511330 skipped
tests / closure-scope id=128068505921 success
tests / closures id=128068508416 success
tests / closures-autofix id=128068512638 skipped
tests / coverage id=128068509364 success
tests / coverage-ratchet id=128068510842 success
tests / fast (3.14) id=128068508681 success
tests / graders-head-copy id=128068511023 success
tests / lane-proofs id=128068511648 success
tests / mutation id=128068505914 success
tests / mutation-autofix id=128068509789 skipped
tests / mutation-pins id=128068509769 skipped
tests / nightly-ha id=128068508839 skipped
tests / nightly-status id=128068507208 success
tests / replay id=128068508539 skipped
tests / typing id=128068508749 success
validate id=128086485089 skipped
validate / validate-hacs id=128068507440 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
NOTE body item c1d09f7c: R10-TRAIN-MERGE-LOOP-2
NOTE body item fca343fb: R10-TRAIN-MERGE-LOOP-2
NOTE body item 6293df3a: R10-TRAIN-MERGE-LOOP-2
NOTE body item 6ac8ab66: R10-TRAIN-MERGE-LOOP-2
NOTE body item 3ed6930b: R10-TRAIN-MERGE-LOOP-2
NOTE body item 3ca63558: R10-TRAIN-MERGE-LOOP-2
NOTE body item 75076207: R10-TRAIN-MERGE-LOOP-2
NOTE body item f353ac9a: dismissed:session plugin outside this repository
CARRY-AUDIT: 8 finding item(s): 8 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub python3 tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  unverified git diff $(git merge-base origin/main HEAD)...HEAD -- dev/audit/harnesses tools/audit/seat | grep -E '^\+.*parents\['
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git diff dc0a170b6...e836876f3dadc368a414ccc2b19126e78507f7d0
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 dev/audit/harnesses/ci_script_seconds.py --selftest
             `dev/audit/harnesses/ci_script_seconds.py` is in the tree at this head
  unverified sh -n critpath_fetch.sh
             `critpath_fetch.sh` does not look like a path in this tree
  ok         python3 tools/audit/seat/merge_train.py --self-test
             `tools/audit/seat/merge_train.py` is in the tree at this head
  ok         bash tools/audit/seat/train.sh --self-test
             `tools/audit/seat/train.sh` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir D
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only origin/main
             `tests/env_drift.py` is in the tree at this head
  ok         tests/closure.py selftest
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  unverified git diff origin/main...HEAD --stat -- tests/golden VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 12 resolved, 4 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.claude/workflows/web-stamp.js b/.claude/workflows/web-stamp.js
index b358ca329..f17641723 100644
--- a/.claude/workflows/web-stamp.js
+++ b/.claude/workflows/web-stamp.js
@@ -138,12 +138,29 @@ reason: <its message>}. Return {stamped: true, version, tag_sha}.`
 const { repo, bump = 'patch', title, wave, session = 'claude-web', merged = [] } = args ?? {}
 if (!repo || !title) throw new Error('args.repo and args.title are required')
 
+// Carry 15 (record PRs ride the stamp): a pull request whose every changed path
+// is a record is HELD-FOR-STAMP by merge_train's queue, add and sweep. This step,
+// before the stamp agent, lands every held record in one train, so the notes and
+// the tag carry them. Not a fragment: only this launcher runs it.
+const recordsPrompt = (repo) => `In ${repo}: if test -f
+~/.zcode/stamp-deploy.key fails, return {landed: false, reason: "no deploy key
+in this runtime; hand the stamp to a local orchestrator"} and change nothing.
+Else run python3 tools/audit/seat/merge_train.py sweep --stamp --repo ${repo}
+from the repository root. Its last line SWEEP HELD or SWEEP REFUSED returns
+{landed: false, reason: <that line>}. On SWEEP DONE with no pull request
+handed to add, return {landed: true, handed: 0}. Otherwise wait for the train
+to close -- the rc file in its state dir (merge_train under $HPO_STATE_DIR,
+else ~/.local/state/hpo) rewritten after the sweep -- and return {landed: rc
+is 0, handed: <n>, reason: <train.log's last line>}.`
+
 phase('Stamp')
 const lastSha = merged.filter((m) => m?.sha).map((m) => m.sha).pop()
 if (lastSha) {
   const gate = await agent(waitMainPrompt(lastSha), { model: 'sonnet', label: 'main gate', phase: 'Stamp', schema: { type: 'object', required: ['green'] } })
   if (!gate?.green) { log(`main is not green at ${lastSha}; not stamping`); return { gate } }
 }
+const records = await agent(recordsPrompt(repo), { model: 'sonnet', label: 'records', phase: 'Stamp', schema: { type: 'object', required: ['landed'] } })
+if (!records?.landed) { log(`held records not landed: ${records?.reason ?? 'records agent returned null'}; not stamping`); return { records } }
 const stamp = await agent(stampPrompt(repo, bump, title), { model: 'opus', effort: 'high', label: 'stamp', phase: 'Stamp', schema: { type: 'object', required: ['stamped'] } })
 if (!stamp?.stamped) log(`not stamped: ${stamp?.reason ?? 'stamp agent returned null'}`)
 
diff --git a/dev/audit/harnesses/ci_script_seconds.py b/dev/audit/harnesses/ci_script_seconds.py
index 973b9cfc4..1b5947c36 100644
--- a/dev/audit/harnesses/ci_script_seconds.py
+++ b/dev/audit/harnesses/ci_script_seconds.py
@@ -39,6 +39,27 @@ def selftest() -> int:
     return 0 if got == want else 1
 
 
+def repo_root(start):
+    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
+    from pathlib import Path
+    here = Path(start).resolve()
+    if here.is_file():
+        here = here.parent
+    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
+    for cand in (here, *here.parents):
+        if (cand / marker).is_file():
+            return cand
+    raise RuntimeError(f"no repository root above {start}")
+
+
+def job_log(repo: str, job_id) -> "str | None":
+    """merge_train.job_log, the one Actions job-log reader (gh's escape flag
+    where gh knows it); None when unreadable."""
+    sys.path.insert(0, str(repo_root(__file__) / "tools" / "audit" / "seat"))
+    import merge_train
+    return merge_train.job_log(None, repo, job_id)
+
+
 def gh(*args: str) -> str:
     return subprocess.run(["gh", *args, "-R", REPO], check=True,
                           capture_output=True, text=True).stdout
@@ -62,7 +83,9 @@ def main() -> int:
             jobs = json.loads(gh("run", "view", str(run["databaseId"]),
                                  "--json", "jobs"))["jobs"]
             fast = next(j for j in jobs if is_fast(j["name"]))
-            log = gh("run", "view", "--job", str(fast["databaseId"]), "--log")
+            log = job_log(REPO, fast["databaseId"])
+            if log is None:
+                raise StopIteration
         except (subprocess.CalledProcessError, StopIteration):
             failed += 1
             print(f"{head} UNREADABLE")
diff --git a/dev/audit/harnesses/r10_ci_layout_p1/critpath_fetch.sh b/dev/audit/harnesses/r10_ci_layout_p1/critpath_fetch.sh
index 914b2f197..a97753ae8 100644
--- a/dev/audit/harnesses/r10_ci_layout_p1/critpath_fetch.sh
+++ b/dev/audit/harnesses/r10_ci_layout_p1/critpath_fetch.sh
@@ -8,6 +8,24 @@
 # other log reader; the CASES format is the contract.
 set -u
 D=$1; C=$2; R=repos/tvofi/heatpump_optimizer
+repo_root() {
+  local d="$1"
+  if [ -f "$d" ]; then
+    d=$(dirname "$d")
+  fi
+  d=$(cd "$d" && pwd) || return 1
+  while [ "$d" != "/" ]; do
+    if [ -f "$d/custom_components/heatpump_optimizer/manifest.json" ]; then
+      printf '%s\n' "$d"
+      return 0
+    fi
+    d=$(dirname "$d")
+  done
+  printf 'no repository root above %s\n' "$1" >&2
+  return 1
+}
+# Job logs are read by merge_train.job_log, the one reader (gh's escape flag where gh knows it).
+SEAT="$(repo_root "$0")/tools/audit/seat" || exit 2
 mkdir -p "$D"; : > "$C"
 for p in 1 2; do
   gh api "$R/actions/workflows/tests.yml/runs?event=pull_request&status=completed&per_page=100&page=$p" \
@@ -31,6 +49,6 @@ print(J["closure-scope"]["id"] if ok else "")
 PY
 )
   [ -n "$jid" ] || continue
-  case_word=$(gh api "$R/actions/jobs/$jid/logs" 2>/dev/null | grep -o -E 'CASE: [A-Z]+' | head -1 | cut -d' ' -f2)
+  case_word=$(python3 "$SEAT/merge_train.py" job-log "$jid" "${R#repos/}" 2>/dev/null | grep -o -E 'CASE: [A-Z]+' | head -1 | cut -d' ' -f2)
   printf '%s\t%s\t%s\n' "$id" "$jid" "${case_word:-UNKNOWN}" >> "$C"
 done < "$D/ids.txt"
diff --git a/dev/audit/harnesses/r10_gate_stale_jobs/scan.py b/dev/audit/harnesses/r10_gate_stale_jobs/scan.py
index 4a3c1dc0e..0824fc709 100644
--- a/dev/audit/harnesses/r10_gate_stale_jobs/scan.py
+++ b/dev/audit/harnesses/r10_gate_stale_jobs/scan.py
@@ -29,7 +29,28 @@ def api(path, *extra):
     if n >= max_calls:
         stop.set()
     p = subprocess.run(["gh", "api", *extra, path], capture_output=True, text=True, errors="replace")
-    return p.returncode, p.stdout
+    return p.returncode, p.stdout if p.returncode == 0 else p.stdout + p.stderr
+
+
+def repo_root(start):
+    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
+    from pathlib import Path
+    here = Path(start).resolve()
+    if here.is_file():
+        here = here.parent
+    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
+    for cand in (here, *here.parents):
+        if (cand / marker).is_file():
+            return cand
+    raise RuntimeError(f"no repository root above {start}")
+
+
+def job_log(job_id) -> "str | None":
+    """A job's log through merge_train.job_log, the one reader (gh's escape flag
+    where gh knows it), each gh call counted by `api`; None when unreadable."""
+    sys.path.insert(0, str(repo_root(__file__) / "tools" / "audit" / "seat"))
+    import merge_train
+    return merge_train.job_log(lambda argv, **_k: api(argv[-1], *argv[2:-1]), R, job_id)
 
 
 def quota():
@@ -78,8 +99,8 @@ def one(row):
     for g in jobs:
         if g["name"] != "gate" or g["conclusion"] != "failure":
             continue
-        rc, log = api(f"repos/{R}/actions/jobs/{g['id']}/logs", "--allow-escape-sequences")
-        if rc:
+        log = job_log(g["id"])
+        if log is None:
             res.append({"run": rid, "job": g["id"], "error": "log read"})
             continue
         at, why = reasons(log)
diff --git a/dev/audit/harnesses/r10_replay_loopnorm.py b/dev/audit/harnesses/r10_replay_loopnorm.py
index 420cfc835..1671e0017 100644
--- a/dev/audit/harnesses/r10_replay_loopnorm.py
+++ b/dev/audit/harnesses/r10_replay_loopnorm.py
@@ -67,6 +67,25 @@ def _gh(*args: str) -> str:
                           check=True).stdout
 
 
+def _job_log(job: str) -> str:
+    """A job's log through merge_train.job_log, the one reader (gh's escape flag
+    where gh knows it); an unread log raises CalledProcessError with gh's stderr,
+    as `_gh` does, so a 404 still reads as no reading."""
+    sys.path.insert(0, str(ROOT / "tools" / "audit" / "seat"))
+    import merge_train
+    err: list[str] = []
+
+    def run(argv, **_k):
+        p = subprocess.run(argv, capture_output=True, text=True)
+        if p.returncode:
+            err.append(p.stderr)
+        return p.returncode, p.stdout if p.returncode == 0 else p.stdout + p.stderr
+    log = merge_train.job_log(run, REPO, job)
+    if log is None:
+        raise subprocess.CalledProcessError(1, "merge_train.job_log", stderr=err[-1] if err else "")
+    return log
+
+
 def nightly_rows() -> list[dict]:
     """One row per timed slow lane's clean cost line (tests.yml, then nightly.yml), on main.
 
@@ -103,8 +122,7 @@ def nightly_rows() -> list[dict]:
                 if not job:      # a run with no slow lane: not a read failure
                     no_job += 1
                     continue
-                log = _gh("api", "--allow-escape-sequences",
-                          f"repos/{REPO}/actions/jobs/{job}/logs")
+                log = _job_log(job)
             except subprocess.CalledProcessError as err:
                 # A cancelled or superseded job has no log: the API answers
                 # 404. That is a run with no reading, not a failed read.
diff --git a/dev/audit/harnesses/r10_seat_selftests_mutants.py b/dev/audit/harnesses/r10_seat_selftests_mutants.py
index e63e3c1fd..4358ab46e 100644
--- a/dev/audit/harnesses/r10_seat_selftests_mutants.py
+++ b/dev/audit/harnesses/r10_seat_selftests_mutants.py
@@ -272,8 +272,47 @@ MUTANTS = [
      'key=lambda e: (not crit(e), not (e.get("priority") or e.get("front"))))'),
     # Round 3: train_add's start path orders a stopped train's spool plus the entry by drain_order.
     ("merge_train-42", "merge_train.py",
-     "queue = t.drain_order([entry] + spooled if front else spooled + [entry])  # mut:start",
-     "queue = [entry] + spooled if front else spooled + [entry]  # mut:start"),
+     "queue = t.drain_order([entry] + spooled + others if front else spooled + [entry] + others)  # mut:start",
+     "queue = [entry] + spooled + others if front else spooled + [entry] + others  # mut:start"),
+    ("merge_train-43", "merge_train.py", "return bool(tree) and tree == self.tree(tip)", "return bool(tree)"),
+    ("merge_train-44", "merge_train.py", "                status, step, pf_why = t.preflight_entry(item)\n",
+     '                status, step, pf_why = "PASS", "", ""\n'),
+    # r10-train-merge-loop round 2: the one job-log reader (carry 2), the
+    # same-tree fetch (R5), carry 19's drain, carries 14 and 15.
+    ("merge_train-45", "merge_train.py",
+     'logs = {j.get("id"): job_log(self.run, self.repo, j.get("id")) for j in failed}',
+     'logs = {j.get("id"): (lambda c: None if c[0] else c[1])(self.run(["gh", "api", '
+     'f"repos/{self.repo}/actions/jobs/{j.get(\'id\')}/logs"])) for j in failed}'),
+    ("merge_train-46", "merge_train.py",
+     '    if code and f"unknown flag: {ESCAPES_FLAG}" in text:\n',
+     '    if False:\n'),
+    ("merge_train-47", "merge_train.py",
+     '        if self.run(["git", "fetch", "-q", "origin", f"verdict/{n}"])[0]:\n',
+     '        if False:\n'),
+    ("merge_train-48", "merge_train.py",
+     "READMIT_SAME_VERDICT = (HOLDER, BRANCH_POLICY, PREFLIGHT_PARK)",
+     "READMIT_SAME_VERDICT = (HOLDER, BRANCH_POLICY)"),
+    ("merge_train-49", "merge_train.py",
+     '        others = t.ready_batch(ready, {int(e["pr"]) for e in spooled} | {entry["pr"]})\n',
+     '        others = []\n'),
+    ("merge_train-50", "merge_train.py",
+     "            if not self.stamp and record_pr([f.get(\"path\", \"\") for f in pr.get(\"files\") or ()]):\n",
+     "            if False:\n"),
+    ("merge_train-51", "merge_train.py",
+     "        return HELD_FOR_STAMP if code == 0 and record_pr(o.split()) else None\n",
+     "        return None\n"),
+    ("merge_train-52", "merge_train.py",
+     "all(stamp.record_class_paths([p]) or PROGRAMME_RECORD.match(p) for p in paths)",
+     "all(stamp.record_class_paths([p]) for p in paths)"),
+    ("merge_train-53", "merge_train.py",
+     "        if self.stamp:\n            return None\n        code, o = self.run([\"gh\", \"pr\", \"view\"",
+     "        code, o = self.run([\"gh\", \"pr\", \"view\""),
+    ("merge_train-54", "merge_train.py",
+     '        log = job_log(train.run, train.repo, c.get("id"))\n',
+     '        log = train.run(["gh", "api", f"repos/{train.repo}/actions/jobs/{c.get(\'id\')}/logs"])[1]\n'),
+    ("merge_train-55", "merge_train.py",
+     'scripts |= set(FAILED_SCRIPT.findall(job_log(self.run, self.repo, c["id"]) or ""))',
+     'scripts |= set(FAILED_SCRIPT.findall(self.run(["gh", "api", f"repos/{self.repo}/actions/jobs/{c[\'id\']}/logs"])[1]))'),
     # r10-ci-layout-p2-u9a: the merge-main bot's pin chain under ci.yml's names.
     ("merge_main_bot-1", "tools/pr/merge_main_bot.py", 'PIN_CHAIN = re.compile(r"^tests / (?:',
      'PIN_CHAIN = re.compile(r"^(?:'),
diff --git a/dev/programme/delivery/3242.md b/dev/programme/delivery/3242.md
new file mode 100644
index 000000000..dfb6b1b6a
--- /dev/null
+++ b/dev/programme/delivery/3242.md
@@ -0,0 +1 @@
+- [#3242](https://github.com/tvofi/heatpump_optimizer/pull/3242) — **open**, R10-TRAIN-MERGE-LOOP: train merge loop (R10-TRAIN-MERGE-LOOP)
diff --git a/tools/audit/seat/autofix_statuses.sh b/tools/audit/seat/autofix_statuses.sh
index cb99316ca..927f86ccd 100755
--- a/tools/audit/seat/autofix_statuses.sh
+++ b/tools/audit/seat/autofix_statuses.sh
@@ -20,6 +20,9 @@ set -uo pipefail
 OUT=${1:?usage: autofix_statuses.sh <out-dir> [pages]}
 PAGES=${2:-3}
 R=tvofi/heatpump_optimizer
+# Job logs are read by merge_train.job_log (`job-log`), the one reader.
+SEAT=$(cd "$(dirname "$0")" && pwd)
+joblog() { sleep 1; python3 "$SEAT/merge_train.py" job-log "$1" "$R"; }
 api() { sleep 1; gh api "$@"; }
 mkdir -p "$OUT/logs" "$OUT/jobs"
 cd "$OUT" || exit 2
@@ -50,15 +53,14 @@ lf=0
 : > status.tsv
 while IFS=$'\t' read -r run br sha jid name concl; do
   f=logs/$jid.log
-  [ -s "$f" ] || api --allow-escape-sequences "repos/$R/actions/jobs/$jid/logs" > "$f" 2>/dev/null \
+  [ -s "$f" ] || joblog "$jid" > "$f" 2>/dev/null \
     || { lf=$((lf + 1)); rm -f "$f"; continue; }
   st=$(grep -m1 -oE 'AUTOFIX: [a-z-]+' "$f" | cut -d' ' -f2)
   why=-
   if [ "$name" = "tests / closures-autofix" ] && [ "${st:-}" != changed ]; then
     cj=$(jq -r '.jobs[] | select(.name == "tests / closures") | .id' "jobs/$run.json")
     c=logs/closures-$cj.log
-    if [ -n "$cj" ] && { [ -s "$c" ] || api --allow-escape-sequences \
-        "repos/$R/actions/jobs/$cj/logs" > "$c" 2>/dev/null; }; then
+    if [ -n "$cj" ] && { [ -s "$c" ] || joblog "$cj" > "$c" 2>/dev/null; }; then
       why=$(grep -oE '(UNDER-SCOPED|INERT READS UNDER-APPROXIMATED|PHANTOM|NOT A FILE):' "$c" \
         | sort -u | tr -d ':' | paste -sd, -)
     else
diff --git a/tools/audit/seat/failure_logs.sh b/tools/audit/seat/failure_logs.sh
index bf8c5f01a..9cc361a1a 100755
--- a/tools/audit/seat/failure_logs.sh
+++ b/tools/audit/seat/failure_logs.sh
@@ -39,6 +39,8 @@ set -uo pipefail
 R=${FAILURE_LOGS_REPO:-tvofi/heatpump_optimizer}
 PACE=${FAILURE_LOGS_PACE:-1}
 api() { sleep "$PACE"; gh api "$@"; }
+# Job logs are read by merge_train.job_log (`job-log`), the one reader.
+joblog() { sleep "$PACE"; python3 "$(dirname "$0")/merge_train.py" job-log "$1" "$R"; }
 
 self_test() {
   passed=0; failed=0
@@ -146,7 +148,7 @@ while IFS=$'\t' read -r name concl crid url; do
   safe=$(printf '%s' "$name" | sed 's# / #-#g' | tr -c 'A-Za-z0-9._-' '-')
   f="$OUT/$safe-$jid.log"
   if [ ! -s "$f" ]; then
-    api --allow-escape-sequences "repos/$R/actions/jobs/$jid/logs" > "$f" 2>/dev/null \
+    joblog "$jid" > "$f" 2>/dev/null \
       || { rm -f "$f"; printf '%s\t%s\t%s\tNO-LOG\tjob %s (log not served)\n' \
              "$name" "$crid" "$concl" "$jid"; continue; }
   fi
diff --git a/tools/audit/seat/instruments/merge_train.py.md b/tools/audit/seat/instruments/merge_train.py.md
index f1b9cafcd..eb750a3af 100644
--- a/tools/audit/seat/instruments/merge_train.py.md
+++ b/tools/audit/seat/instruments/merge_train.py.md
@@ -30,6 +30,16 @@
   `verdict/<pr>`'s posted tip and is `merge` at its head or carries to it
   (`app_approve.sh --carry`), oldest first, one `QUEUE`/`LEFT` line each;
   budget and policy heads are queued for the batch's own serial route.
+  A record pull request (`record_pr`: every changed path a delivery row,
+  carry, plan, triage batch, the handover or a roster) is logged
+  `HELD-FOR-STAMP` and queued for nobody, by `queue`, `add` and `sweep`
+  alike; under `--stamp` they are admitted, so the stamp step of
+  `.claude/workflows/web-stamp.js` runs `sweep --stamp` before the tag and
+  one train merges every held record in one batch (tvofi 2026-11-01). The record/autofix branch stays `--bot-prs`'s.
+  An `add` that starts a train starts it over every ready pull request
+  (`Train.ready_batch`: the sweep's queue, else `build_queue`), one batch;
+  a train over one pull request starts only when it is the one ready
+  (tvofi 2026-11-01, batch by default).
   `add`'s admission (`Train.admit_add`) reads the same posted verdict
   first, as its `verdict` rule, and fills an absent comment id from it.
   bus.sh's post loads the train the moment it posts a merge verdict
@@ -37,8 +47,14 @@
   `sweep` is the slow backstop (`tick_loop.sh --sweep`, every 1800 s by
   default): unless the ledger holds an open train-stop, it `add`s each head
   `queue` admits that no sweep added at that head, into the live train's
-  next batch or a `train.sh --bot-prs --approval-carry --pre-flight` it
-  starts when none is live, never a second.
+  next batch or a bare `train.sh` launch it starts when none is live, never
+  a second.
+  A train launched through `train.sh` runs the recommended flags by default:
+  `RECOMMENDED` in this file is their one definition (`--overlap`,
+  `--approval-carry`, `--skip-bad`, `--free-holders`, `--bot-prs`,
+  `--pre-flight`), each off with `train.sh --no-<flag>`. The flags this page
+  names say what each does; a caller launching through `train.sh` passes none
+  of them by hand.
   `batch` merges the queue without re-merging main: the entries' merges are
   proved together on `batch/<tag>-<n>` (B), a lone entry merges unproved (D),
   and workflow, claim, grader, budget or conflicting entries go serial. When:
diff --git a/tools/audit/seat/instruments/train.sh.md b/tools/audit/seat/instruments/train.sh.md
index 1c6b320b9..87e557ed3 100644
--- a/tools/audit/seat/instruments/train.sh.md
+++ b/tools/audit/seat/instruments/train.sh.md
@@ -25,7 +25,10 @@
   launch without `--checkout`, and a bare launch's argv carrying no flag.
   `train.sh add <pr> <verdict> --repo R --state-dir D [--verdict-comment ID]
   [flags]` loads one pull request into that state dir's live train (its next
-  batch) or, with none live, starts one with those flags. When: whenever a
+  batch) or, with none live, starts one with those flags over every ready
+  pull request (`merge_train.py queue`'s, carry 14); a record pull request is
+  `HELD-FOR-STAMP`, rc 0 (the stamp seat loads them in one batch: `merge_train.py sweep
+  --stamp`, the stamp step of `.claude/workflows/web-stamp.js`). When: whenever a
   merge verdict is confirmed. Refusal: `ADD REFUSED #<pr> <rule>: <why>` from
   `Train.admit_add` (shape, open, base, carry, row, budget-raise, policy),
   and `one-train` beside a train.sh still closing; a pull request already
diff --git a/tools/audit/seat/merge_train.py b/tools/audit/seat/merge_train.py
index f3044585e..3361fce26 100644
--- a/tools/audit/seat/merge_train.py
+++ b/tools/audit/seat/merge_train.py
@@ -496,20 +496,41 @@ def approval_owed(train: "Train", pr: int, head: str, runs, required) -> "str |
 RAISE_REASON = re.compile(rf"^{re.escape(RAISE_GATE)}: failure \((?:this run|run \d+)\)$")
 
 
+#: The flag gh needs to pass an Actions log's terminal escapes (measured on the
+#: R9-RO-12 proof), and gh 2.89's refusal of it as an unknown flag (measured on
+#: the #3242 review seat, which reads the same log without it).
+ESCAPES_FLAG = "--allow-escape-sequences"
+
+
+def job_log(run, repo: str, job_id) -> "str | None":
+    """The one reader of an Actions job's log (a check run's id is its job's
+    id): `gh api <ESCAPES_FLAG>`, and on a gh that does not know the flag the
+    same read without it. None when the read fails, so no caller judges an
+    unread log. `run` None is the train's own subprocess runner; a shell
+    caller reads it as `merge_train.py job-log <job id> <owner/repo>`. Every
+    Actions job-log read in the tree goes through here (`git grep -nE
+    'actions/jobs/[^ ]*/logs' -- '*.py' '*.sh'` names this module, fixtures
+    and the mutant harness alone)."""
+    run = run or Train._run
+    path = f"repos/{repo}/actions/jobs/{job_id}/logs"
+    code, text = run(["gh", "api", ESCAPES_FLAG, path])
+    if code and f"unknown flag: {ESCAPES_FLAG}" in text:
+        code, text = run(["gh", "api", path])
+    return None if code else text
+
+
 def gate_raise_only(train: "Train", runs) -> bool:
     """True when at least one gate suite is red, none is still running, and
     every red one's log (`gate_outcome`, gate.py's own FAIL reasons) lists
     RAISE_REASON alone. An unread log, a gate step that never ran or a
-    RATE-LIMITED gate is False. A check run's id is its Actions job's id; gh
-    refuses an Actions log unless told to pass its terminal escapes."""
+    RATE-LIMITED gate is False. The logs are read by `job_log`."""
     suites = gate_suites(runs)
     if not suites or any(run_state(c) == "pending" for c in suites):
         return False
     reds = [c for c in suites if run_state(c) == "red"]
     for c in reds:
-        code, log = train.run(["gh", "api", "--allow-escape-sequences",
-                               f"repos/{train.repo}/actions/jobs/{c.get('id')}/logs"])
-        out = gate_outcome(log) if code == 0 else None
+        log = job_log(train.run, train.repo, c.get("id"))
+        out = gate_outcome(log) if log is not None else None
         if not out or out[0] != "fail" or not out[1] or not all(RAISE_REASON.match(x) for x in out[1]):
             return False
     return bool(reds)
@@ -770,7 +791,29 @@ POLICY_RED = ("FAILURE", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED", "STARTUP_F
 # A skip of these classes is the environment's, not the entry's: the train's own
 # worktree holder (P189) or GitHub's branch policy at the last merge attempt
 # (P291). Re-added at the SAME verdict head, such an entry is admitted again.
-READMIT_SAME_VERDICT = (HOLDER, BRANCH_POLICY)
+#: A pre-flight park (`Train.preflight`) of any step other than the holder's. A body
+#: patch moves no head, so the park's cause can be cured at the same verdict;
+#: `train_add` re-runs the pre-flight at the add (`Train.preflight_entry`) and
+#: refuses while the cause holds, the drain's batch pre-flight does the same.
+PREFLIGHT_PARK = "PRE-FLIGHT"
+
+#: Carry 15 (tvofi 2026-11-01, production-share ruling): a record pull request
+#: merges only in a stamp's batch, never singly. Record = every changed path is
+#: stamp.py's record class (`record_class_paths`: delivery rows, carries, plans)
+#: or one of the programme's own records below (triage batches, the handover,
+#: the round's rosters). The record/autofix branch is not judged here: it stays
+#: `--bot-prs`'s, behind record_row.py's guard.
+PROGRAMME_RECORD = re.compile(r"^dev/programme/(?:triage/[^/]+\.md|HANDOVER\.md|rosters/[^/]+\.json)$")
+HELD_FOR_STAMP = "a record pull request (every changed path is a record) merges only in a stamp's batch"
+
+
+def record_pr(paths: "list[str]") -> bool:
+    """True when there is at least one path and every one is a record (carry 15)."""
+    sys.path.insert(0, str(ROOT / "tools/release"))
+    import stamp
+    paths = [p for p in paths if p]
+    return bool(paths) and all(stamp.record_class_paths([p]) or PROGRAMME_RECORD.match(p) for p in paths)
+READMIT_SAME_VERDICT = (HOLDER, BRANCH_POLICY, PREFLIGHT_PARK)
 
 
 class MainMoved(Stop):
@@ -1089,7 +1132,7 @@ def launch_detached(argv: "list[str]", state: Path) -> "tuple[int, str]":
 
 
 def train_add(t: "Train", item: dict, train_argv: "list[str]", launch=launch_detached,
-              settle: float = ADD_SETTLE_SECONDS, front: bool = False) -> int:
+              settle: float = ADD_SETTLE_SECONDS, front: bool = False, ready: "list[dict] | None" = None) -> int:
     """`add`: load one verdicted pull request into the state dir's live train,
     or start that train. Under QUEUE_LOCK, in order: a pull request already in
     the live train's running or later batches, or already spooled, is a no-op
@@ -1104,8 +1147,15 @@ def train_add(t: "Train", item: dict, train_argv: "list[str]", launch=launch_det
     waited out, never raced: one train per state dir. rc 2: no train could start.
     <front> (`add --front`, P112): the entry goes FIRST in the next batch -- a
     spooled one is moved there (`spool_edit`), a new one is spooled or queued
-    first -- and the spool order is printed read back."""
+    first -- and the spool order is printed read back.
+    Carry 15: a record pull request outside a `--stamp` add is HELD-FOR-STAMP,
+    rc 0, nothing added. Carry 14: a started train's first batch is every
+    ready pull request (`Train.ready_batch`; <ready>, the sweep's queue)."""
     pr = item.get("pr")
+    stamp_why = t.held_for_stamp(int(pr)) if str(pr).isdigit() else None
+    if stamp_why:
+        t.log(f"HELD-FOR-STAMP #{pr}: {stamp_why}; nothing added")
+        return 0
     with queue_lock(t.state):
         live = read_pid(t.state / QUEUE_OPEN)
         live = live if pid_alive(live) else None
@@ -1118,6 +1168,13 @@ def train_add(t: "Train", item: dict, train_argv: "list[str]", launch=launch_det
             t.log(f"ALREADY #{pr}: {held} ({'live train pid %d' % live if live else 'no live train'}); nothing added")
             return 0
         why = t.admit_add(item)
+        if not why and live and str(pr).isdigit():
+            rec = queue_seen_read(t.state).get(str(pr)) or {}
+            if (rec.get("state") == "skipped" and rec.get("class") == PREFLIGHT_PARK
+                    and str(item.get("verdict") or "") == str(rec.get("verdict") or "")):
+                status, step, pf_why = t.preflight_entry(item)
+                if status != "PASS":
+                    why = f"{step}: {pf_why} (the pre-flight park at this verdict still holds)"
         if why:
             t.log(f"ADD REFUSED #{pr} {why}")
             return 1
@@ -1143,7 +1200,8 @@ def train_add(t: "Train", item: dict, train_argv: "list[str]", launch=launch_det
             return 2
         # P312 here too: the first batch is the leftovers plus the entry in drain_order,
         # the order queue_take drains a live spool in; a fronted entry leads its tier.
-        queue = t.drain_order([entry] + spooled if front else spooled + [entry])  # mut:start
+        others = t.ready_batch(ready, {int(e["pr"]) for e in spooled} | {entry["pr"]})
+        queue = t.drain_order([entry] + spooled + others if front else spooled + [entry] + others)  # mut:start
         qf = t.state / f"add-queue-{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}-{pr}.json"
         qf.write_text(json.dumps(queue, indent=2) + "\n")
         (t.state / QUEUE_SPOOL).unlink(missing_ok=True)
@@ -1168,7 +1226,7 @@ class Train:
                  approval_carry: bool = False, main_moved_tries: int = 0,
                  bot_prs: bool = False, pre_flight: bool = False,
                  free_holders: bool = False, critical=None,
-                 clock: "callable" = time.monotonic, wall: "callable" = time.time) -> None:
+                 clock: "callable" = time.monotonic, wall: "callable" = time.time, stamp: bool = False) -> None:
         self.repo, self.state, self.mandate, self.role = repo, state, mandate, role
         if base != "main" and not base.startswith("batch/"):
             raise ValueError(f"--base {base}: main, or a batch/ rehearsal base")
@@ -1176,6 +1234,9 @@ class Train:
         # there reaches main, so the verdict, row, policy and approval reads --
         # which grade a merge into main -- are not made (`batch`).
         self.base, self.real = base, base == "main"
+        # Carry 15: a stamp's queue (`--stamp`) admits the record pull requests
+        # every other queue holds HELD-FOR-STAMP.
+        self.stamp = stamp
         self.ignore, self.min_runs, self.polls, self.merge_tries = ignore, min_runs, polls, merge_tries
         self.run = run or self._run
         self.sleep, self.log, self.clock = sleep, log, clock
@@ -2418,6 +2479,19 @@ class Train:
         self.log("TRAIN DONE")
         return 1 if self.skipped else 0
 
+    def pre_flight_reader(self):
+        """The one PreFlight construction `preflight` and `preflight_entry` share."""
+        sys.modules.setdefault("merge_train", sys.modules[__name__])  # one Stop class, not two
+        if str(Path(__file__).resolve().parent) not in sys.path:
+            sys.path.insert(0, str(Path(__file__).resolve().parent))
+        import queue_pre_flight
+        return queue_pre_flight.PreFlight(self.repo, train=self, checkout=ROOT, bot_cured=True,
+                                          free_holders=self.free_holders)
+
+    def preflight_entry(self, item: dict) -> "tuple[str, str, str]":
+        """(status, step, why) of one entry under the same construction `preflight` uses."""
+        return self.pre_flight_reader().entry(item)
+
     def preflight(self, queue: list[dict]) -> list[dict]:
         """`--pre-flight`: queue_pre_flight.py's admission reads over the whole
         queue before anything waits or merges; a PARK or FAIL entry is logged
@@ -2428,12 +2502,7 @@ class Train:
         --free-holders, a holder `freeable` clears. A rehearsal reads none."""
         if not (self.pre_flight and self.real):
             return list(queue)
-        sys.modules.setdefault("merge_train", sys.modules[__name__])  # one Stop class, not two
-        if str(Path(__file__).resolve().parent) not in sys.path:
-            sys.path.insert(0, str(Path(__file__).resolve().parent))
-        import queue_pre_flight
-        pf = queue_pre_flight.PreFlight(self.repo, train=self, checkout=ROOT, bot_cured=True,
-                                        free_holders=self.free_holders)
+        pf = self.pre_flight_reader()
         keep = []
         for item in queue:
             status, step, why = pf.entry(item)
@@ -2445,9 +2514,8 @@ class Train:
                    "verdict": item.get("verdict")}
             # PreFlight parks at `recarry` for one cause, the worktree holder
             # (`worktree_holder`): the environment's, so P189's exception reaches it.
-            cls = HOLDER if step == "recarry" else None
-            if cls:
-                row["class"] = cls
+            cls = HOLDER if step == "recarry" else PREFLIGHT_PARK
+            row["class"] = cls
             self.skipped.append(row)
             self.seen_mark(item.get("pr"), "skipped", cls)
         (self.state / "skipped.json").write_text(json.dumps(self.skipped, indent=2) + "\n")
@@ -2455,6 +2523,31 @@ class Train:
         return keep
 
     # ------------------------------------------------------ the queue builder
+    def held_for_stamp(self, n: int) -> "str | None":
+        """Carry 15 at `add`: why <n> waits for the stamp (HELD_FOR_STAMP), else
+        None -- under `--stamp`, for a production pull request, and for a file
+        list that could not be read (the fail-open direction: a record merged
+        singly costs one gate run; a production PR held would wait a stamp)."""
+        if self.stamp:
+            return None
+        code, o = self.run(["gh", "pr", "view", str(n), "--repo", self.repo, "--json", "files",
+                            "--jq", ".files[].path"])
+        return HELD_FOR_STAMP if code == 0 and record_pr(o.split()) else None
+
+    def ready_batch(self, ready: "list[dict] | None", have: "set[int]") -> "list[dict]":
+        """Carry 14 (tvofi 2026-11-01: batch by default): when an `add` starts a
+        train, every other ready verdicted pull request (`build_queue`, or the
+        sweep's own <ready>) joins its first batch, so one ready PR alone is the
+        only single-PR start. <have>: the add's entry and the spooled leftovers.
+        An unreadable queue starts over what the add holds, logged BATCH-READ."""
+        if ready is None:
+            try:
+                ready = self.build_queue()
+            except Stop as s:
+                self.log(f"BATCH-READ {s.step}: {s.why}; the train starts over what the add holds")
+                return []
+        return [dict(e) for e in ready if int(e["pr"]) not in have]
+
     def build_queue(self) -> list[dict]:
         """`queue`: the train's queue, written from what is already machine-read
         (R10-FLOW-AUTOTRAIN) instead of assembled by hand in an agent's turn.
@@ -2463,11 +2556,13 @@ class Train:
         <why>`. Files are not read: a budget, policy or workflow head is
         queued like any other and goes to the serial route the batch's own
         admission applies (`file_class`, `raise_hold`, the policy gate), so
-        the builder holds no second copy of those rules. An unreadable pull
+        the builder holds no second copy of those rules. A record pull request
+        (`record_pr`, from the list's own files) is HELD-FOR-STAMP outside a
+        `--stamp` queue (carry 15). An unreadable pull
         request list, approver identity or bus listing stops it: a queue built
         on a read that failed is a queue nobody read."""
         code, o = self.run(["gh", "pr", "list", "--repo", self.repo, "--state", "open", "--limit", "200",
-                            "--json", "number,headRefOid,headRefName"])
+                            "--json", "number,headRefOid,headRefName,files"])
         try:
             prs = json.loads(o) if code == 0 else None
         except ValueError:
@@ -2494,6 +2589,9 @@ class Train:
             if isinstance(got, str):
                 self.log(f"LEFT #{pr.get('number')}: {got}")
                 continue
+            if not self.stamp and record_pr([f.get("path", "") for f in pr.get("files") or ()]):
+                self.log(f"HELD-FOR-STAMP #{got['pr']}: {HELD_FOR_STAMP}")
+                continue
             self.log(f"QUEUE #{got['pr']} verdict {got['verdict'][:12]} comment {got['verdict_comment']}"
                      + ("" if got["verdict"] == pr["headRefOid"] else f", carried to {pr['headRefOid'][:12]}"))
             queue.append(got)
@@ -2524,6 +2622,25 @@ class Train:
                     + (o.strip().splitlines() or ["(no output)"])[-1][:160]
         return {"pr": n, "verdict": verdict, "verdict_comment": comment}
 
+    def same_tree_posting(self, n: int, tip: str, body: str) -> bool:
+        """The comment's `bus: verdict/<n> at <sha>,` names a commit that is not the tip
+        but stands for it: bus.sh signs `<pr> <tree>`, so a tree posts once whatever
+        commit carries it. True iff <sha> is an ancestor of <tip> and the two trees are
+        equal (the objects from a fetch of verdict/<n>); a failed fetch or read is False."""
+        m = re.search(rf"^bus: verdict/{n} at ([0-9a-f]{{40}}),", body, re.M)
+        if not m or m.group(1) == tip:
+            return False
+        sha = m.group(1)
+        if self.run(["git", "fetch", "-q", "origin", f"verdict/{n}"])[0]:
+            return False
+        if self.run(["git", "merge-base", "--is-ancestor", sha, tip])[0]:
+            return False
+        try:
+            tree = self.tree(sha)
+            return bool(tree) and tree == self.tree(tip)
+        except Stop:
+            return False
+
     def posted_verdict(self, n: int, tip: "str | None", allow: "tuple[set, int]") -> "tuple[str, str] | str":
         """(the merge verdict's head, its comment id) for pull request <n>, or
         why there is none: a confirmed verdict on the bus (`verdict/<n>`, at
@@ -2550,7 +2667,7 @@ class Train:
             return f"verdict/{n} at {tip} is confirmed and not posted"
         v = max(vs, key=lambda c: (c.get("created_at") or "", c.get("id") or 0))
         body = v.get("body") or ""
-        if f"\nbus: verdict/{n} at {tip}," not in body:
+        if f"\nbus: verdict/{n} at {tip}," not in body and not self.same_tree_posting(n, tip, body):
             return f"the newest posted verdict (comment {v.get('id')}) is not verdict/{n}'s tip {tip}"
         first = body.split("\n", 1)[0].rstrip("\r")
         got = proof_watch.parse_verdict(first)
@@ -2686,11 +2803,7 @@ class Train:
         scripts: set[str] = set()
         for c in runs:
             if c.get("name") in red and c.get("conclusion") not in GREEN:
-                # gh refuses a log carrying terminal escapes -- every Actions log
-                # does -- unless told to pass them (measured on the R9-RO-12 proof).
-                log = self.run(["gh", "api", "--allow-escape-sequences",
-                                f"repos/{self.repo}/actions/jobs/{c['id']}/logs"])[1]
-                scripts |= set(FAILED_SCRIPT.findall(log))
+                scripts |= set(FAILED_SCRIPT.findall(job_log(self.run, self.repo, c["id"]) or ""))
         if not scripts:
             return None
         unit = _fastpath().closure.unit_of
@@ -2953,10 +3066,7 @@ class Train:
                           if j.get("conclusion") == "failure"] if code == 0 else []
             except ValueError:
                 failed = []
-            logs = {}
-            for j in failed:
-                c, text = self.run(["gh", "api", f"repos/{self.repo}/actions/jobs/{j.get('id')}/logs"])
-                logs[j.get("id")] = None if c else text
+            logs = {j.get("id"): job_log(self.run, self.repo, j.get("id")) for j in failed}
             got = infra_due(1, failed, logs)
             if got is None:
                 continue
@@ -3485,7 +3595,7 @@ def sweep(t: Train, train_argv: "list[str]", add=train_add, ledger_log: "str | N
             t.log(f"SWEPT #{pr} at {str(head)[:12]} before; not added again")
             again += 1
             continue
-        rc = add(t, dict(e), train_argv)
+        rc = add(t, dict(e), train_argv, ready=queue)
         if rc == 2:
             t.log(f"SWEEP REFUSED start: #{pr}'s add started no train")
             return 2
@@ -4882,6 +4992,12 @@ def _queue_self_test(check) -> None:
             a = " ".join(argv)
             if argv[:3] == ["gh", "pr", "list"]:
                 return w.get("list", (0, json.dumps(w["prs"])))
+            if argv[:3] == ["git", "fetch", "-q"] and w.get("fetch_fail"):  # same_tree_posting's fetch
+                return 128, f"fatal: couldn't find remote ref {argv[-1]}"
+            if argv[:3] == ["git", "merge-base", "--is-ancestor"]:  # same_tree_posting's reads
+                return (0, "") if (argv[3], argv[4]) in w.get("anc", ()) else (1, "")
+            if argv[:2] == ["git", "rev-parse"] and argv[2].endswith("^{tree}"):
+                return 0, w.get("trees", {}).get(argv[2][:-7], "tree-of-" + argv[2][:-7])
             if argv[:2] == ["git", "ls-remote"]:  # the whole bus, or admit_add's one verdict/<pr>
                 return w.get("ls", (0, "".join(f"{t}\trefs/heads/verdict/{n}\n" for n, t in w["tips"].items()
                                                if argv[-1] in ("refs/heads/verdict/*", f"refs/heads/verdict/{n}"))))
@@ -4926,6 +5042,25 @@ def _queue_self_test(check) -> None:
     check("queue: no verdict/<pr> on the bus is left (#17)", "no confirmed verdict" in left.get(17, ""))
     check("queue: a newest posted verdict that is not the bus tip waits (#18: confirmed, not posted)",
           "not verdict/18's tip" in left.get(18, ""))
+    # Carry 4: bus.sh posts once per `<pr> <tree>`, so a same-tree commit appended after the
+    # posting stands for the posted one; a different tree, or a non-descendant, still waits.
+    def posted_for(tip, **over):
+        wd = world(comments={18: [posted(18, f"Fix review: merge {hx('e')}", tip=hx("7"))]}, **over)
+        tt = Train("o/r", Path(tempfile.mkdtemp(dir=tmp.name)), None, "", (), 1, run=fake(wd)[0], log=lambda m: None)
+        return tt.posted_verdict(18, tip, ({login}, vid))
+    t_new = hx("9")
+    same = posted_for(t_new, anc={(hx("7"), t_new)}, trees={hx("7"): "T1", t_new: "T1"})
+    diff = posted_for(t_new, anc={(hx("7"), t_new)}, trees={hx("7"): "T1", t_new: "T2"})
+    nonanc = posted_for(t_new, anc=set(), trees={hx("7"): "T1", t_new: "T1"})
+    check("queue: a tip one same-tree descendant commit after the commented sha is queued with the same head and comment id",
+          same == (hx("e"), "1018"))
+    check("queue: null controls -- a tip whose tree differs (#18's case), and a same-tree commit that does not descend "
+          "from the commented sha, still wait",
+          isinstance(diff, str) and "not verdict/18's tip" in diff and isinstance(nonanc, str) and "not verdict/18's tip" in nonanc)
+    unfetched = posted_for(t_new, anc={(hx("7"), t_new)}, trees={hx("7"): "T1", t_new: "T1"}, fetch_fail=True)
+    check("queue: null control -- the same same-tree descendant waits when `git fetch origin verdict/<n>` fails "
+          "(the commented sha's objects are not known to be here)",
+          isinstance(unfetched, str) and "not verdict/18's tip" in unfetched)
     check("queue: a merge comment under another login is no verdict, though it carries the App's id (#19)",
           "not posted" in left.get(19, ""))
     check("queue: a merge comment under the App's login and another id is no verdict (#20)",
@@ -4959,8 +5094,9 @@ def _queue_self_test(check) -> None:
         run, calls = fake(w)
         lines, added = [], []
 
-        def add(t, item, argv):
+        def add(t, item, argv, ready=None):
             added.append((item["pr"], argv))
+            w.setdefault("ready_seen", []).append([e["pr"] for e in ready or ()])
             return (rcs or {}).get(item["pr"], 0)
         t = Train("o/r", state, None, "", (), 1, run=run, sleep=lambda s: None, log=lines.append)
         led = state / "ledger"
@@ -4969,8 +5105,122 @@ def _queue_self_test(check) -> None:
             (led / "events.tsv").write_text("".join("\t".join(r) + "\n" for r in events))
         return sweep(t, ["train.sh"], add=add, ledger_log=str(led / "cloud-relay.log")), lines, calls, added
 
+    # Carry 14 (batch by default): an `add` that starts a train starts it over every
+    # ready pull request -- one train, one batch -- and over the entry alone only
+    # when it is the one ready. The sweep hands its own queue in (no second read).
+    def started(ready, pr=12, read=None):
+        with tempfile.TemporaryDirectory() as d:
+            launched, sl = [], []
+
+            def launch(argv, state):
+                launched.append(json.loads(Path(argv[argv.index("--queue") + 1]).read_text()))
+                return 4242, ""
+            ts_ = Train("o/r", Path(d), None, "", (), 1, run=read or (lambda *a, **k: (0, "")), log=sl.append)
+            ts_.admit_add = lambda item: None
+            rc_ = train_add(ts_, {"pr": pr, "verdict": hx(str(pr % 10))}, ["train.sh"], launch=launch, settle=0,
+                            ready=ready)
+            return rc_, [[int(e["pr"]) for e in q] for q in launched], sl
+    three = [{"pr": n, "verdict": hx(str(n % 10)), "verdict_comment": str(1000 + n)} for n in (11, 12, 15)]
+    rc3, launched3, sl3 = started(three)
+    check("carry 14: three ready pull requests and no live train -> `add` starts ONE train whose first batch is "
+          "all three (STARTED over #11 #12 #15)",
+          rc3 == 0 and len(launched3) == 1 and sorted(launched3[0]) == [11, 12, 15]
+          and any(x.startswith("STARTED train.sh pid 4242 over") and all(f"#{n}" in x for n in (11, 12, 15))
+                  for x in sl3))
+    rc1, launched1, _ = started([three[1]])
+    check("carry 14 null: exactly one ready (the add's own) -> a batch of one", rc1 == 0 and launched1 == [[12]])
+    rcr, launchedr, slr = started(None, read=lambda *a, **k: (1, "HTTP 502"))
+    check("carry 14: an unreadable queue at the start still starts the add's entry, logged BATCH-READ",
+          rcr == 0 and launchedr == [[12]] and any(x.startswith("BATCH-READ queue:") for x in slr))
+    rcq, launchedq, _ = started(None, read=fake(world())[0])
+    check("carry 14: with no queue handed in, the add reads build_queue itself (the fixture's #11 #12 #15)",
+          rcq == 0 and len(launchedq) == 1 and sorted(launchedq[0]) == [11, 12, 15])
+
+    # Carry 15 (record PRs ride the stamp): a record pull request is HELD-FOR-STAMP
+    # outside a stamp's queue and add; a production one is not; at the stamp every
+    # held record joins one queue, so one batch.
+    rec_files = [{"path": "dev/programme/delivery/12.md"}, {"path": "dev/programme/triage/s6-batch1.md"}]
+    def recw():
+        wr = world()
+        for p_ in wr["prs"]:
+            p_["files"] = rec_files if p_["number"] in (12, 15) else [{"path": "tools/x.py"}, rec_files[0]]
+        return wr
+    held_lines = build(recw())[1]
+    q_plain = build(recw())[0]
+    run_s, _ = fake(recw())
+    ts_s = Train("o/r", Path(tempfile.mkdtemp(dir=tmp.name)), None, "", (), 1, run=run_s, log=lambda m: None,
+                 stamp=True)
+    q_stamp = ts_s.build_queue()
+    check("carry 15: outside a stamp, the record pull requests (#12, #15: every path a record) are HELD-FOR-STAMP "
+          "and queued for nobody; the production one (#11, a record row beside code) is queued (null control)",
+          [e["pr"] for e in q_plain] == [11]
+          and [x.split(":")[0] for x in held_lines if x.startswith("HELD-FOR-STAMP")]
+          == ["HELD-FOR-STAMP #12", "HELD-FOR-STAMP #15"])
+    check("carry 15: a stamp's queue (--stamp) holds nothing: every held record joins the one queue the stamp's "
+          "train merges as one batch", [e["pr"] for e in q_stamp] == [11, 12, 15])
+
+    def stamp_add(paths, stamp):
+        with tempfile.TemporaryDirectory() as d:
+            sl, launched = [], []
+            tr = Train("o/r", Path(d), None, "", (), 1, log=sl.append, stamp=stamp,
+                       run=lambda argv, cwd=ROOT, stdin=None: (0, "\n".join(paths)) if "files" in argv else (0, ""))
+            tr.admit_add = lambda item: None
+            rc_ = train_add(tr, {"pr": 31, "verdict": hx("3")}, ["train.sh"], settle=0, ready=[],
+                            launch=lambda argv, st: (launched.append(argv), (77, ""))[1])
+            return rc_, sl, len(launched)
+    rec_paths = ["dev/programme/delivery/31.md", "dev/programme/HANDOVER.md"]
+    check("carry 15 at add: a record pull request added between stamps is HELD-FOR-STAMP, rc 0, nothing started; "
+          "a production one starts its train (null); under --stamp the record starts it",
+          stamp_add(rec_paths, False)[::2] == (0, 0)
+          and stamp_add(rec_paths, False)[1][0].startswith("HELD-FOR-STAMP #31:")
+          and stamp_add(["custom_components/x.py", rec_paths[0]], False)[::2] == (0, 1)
+          and stamp_add(rec_paths, True)[::2] == (0, 1))
+    check("carry 15: record_pr is every path a record and at least one; an empty list is not a record",
+          record_pr(rec_paths) and not record_pr([]) and not record_pr(rec_paths + ["tools/x.py"]))
+
+    # Carry 15 at the stamp's launch: the stamp seat's one command (web-stamp.js's
+    # stamp step: `merge_train.py sweep --stamp`) over SEVERAL held records starts
+    # ONE train whose first batch is every one of them; the same sweep without
+    # --stamp starts nothing (null control: the records stay HELD-FOR-STAMP).
+    def stamp_launch(stamp):
+        wr = world()
+        for p_ in wr["prs"]:
+            p_["files"] = rec_files
+        run_l, _ = fake(wr)
+        with tempfile.TemporaryDirectory() as d:
+            launched, sl = [], []
+
+            def launch(argv, state):
+                launched.append(sorted(int(e["pr"]) for e in json.loads(
+                    Path(argv[argv.index("--queue") + 1]).read_text())))
+                (Path(d) / QUEUE_OPEN).write_text(f"{os.getpid()}\n")  # the started train is live
+                return os.getpid(), ""
+            tl = Train("o/r", Path(d), None, "", (), 1, run=run_l, sleep=lambda s: None, log=sl.append,
+                       stamp=stamp)
+            tl.admit_add = lambda item: None
+            led = Path(d) / "ledger"
+            led.mkdir()
+            rc_ = sweep(tl, ["train.sh"], ledger_log=str(led / "cloud-relay.log"),
+                        add=lambda t_, item, argv, ready=None: train_add(t_, item, argv, launch=launch, settle=0,
+                                                                         ready=ready))
+            return rc_, launched, sl
+    rc_sl, launched_sl, sl_sl = stamp_launch(True)
+    rc_nl, launched_nl, sl_nl = stamp_launch(False)
+    check("carry 15 at the stamp: `sweep --stamp` over three held records (#11 #12 #15, every path a record) "
+          "starts ONE train whose first batch is all three; without --stamp it starts none and each is "
+          "HELD-FOR-STAMP (null control)",
+          rc_sl == 0 and launched_sl == [[11, 12, 15]]
+          and rc_nl == 0 and launched_nl == []
+          and sorted(x.split(":")[0] for x in sl_nl if x.startswith("HELD-FOR-STAMP"))
+          == ["HELD-FOR-STAMP #11", "HELD-FOR-STAMP #12", "HELD-FOR-STAMP #15"])
+    if not (rc_sl == 0 and launched_sl == [[11, 12, 15]]):
+        print("    DEBUG", rc_sl, launched_sl, sl_sl[-6:], rc_nl, launched_nl, sl_nl[-6:])
+
     st = Path(tempfile.mkdtemp(dir=tmp.name))
-    rc, lines, calls, added = swept(world(), st)
+    wq = world()
+    rc, lines, calls, added = swept(wq, st)
+    check("carry 14: the sweep hands add its own queue, so a started train batches without a second read",
+          wq.get("ready_seen") == [[11, 12, 15]] * 3)
     check("sweep: every admitted head is handed to add, oldest first, with the started train's argv",
           rc == 0 and [p for p, _ in added] == [11, 12, 15] and all(a == ["train.sh"] for _, a in added)
           and lines[-1] == "SWEEP DONE: 3 admitted, 3 handed to add, 0 swept before at that head, 0 refused by admit_add")
@@ -5015,7 +5265,8 @@ def _queue_self_test(check) -> None:
         run, _ = fake(w)
         lines = []
         t = Train("o/r", state, None, "", (), 1, run=run, sleep=lambda s: None, log=lines.append)
-        return sweep(t, ["train.sh"], add=lambda t, e, argv: train_add(t, e, argv, launch=launch, settle=0.3),
+        return sweep(t, ["train.sh"], add=lambda t, e, argv, ready=None: train_add(t, e, argv, launch=launch, settle=0.3,
+                                                                   ready=ready),
                      ledger_log=str(state / "ledger" / "cloud-relay.log")), lines
     sleepers: list = []
     starts: list = []
@@ -5031,15 +5282,15 @@ def _queue_self_test(check) -> None:
         st = Path(tempfile.mkdtemp(dir=tmp.name))
         rc, lines = live(two, st, launch)
         queued = json.loads(Path(starts[0][starts[0].index("--queue") + 1]).read_text()) if starts else []
-        check("sweep, no train live: ONE train starts over the first missed head, the second joins its next "
-              "batch (spooled) -- never a second train",
-              rc == 0 and len(starts) == 1 and [e["pr"] for e in queued] == [11]
-              and [e["pr"] for e in spool_read(st)[0]] == [12]
+        check("sweep, no train live: ONE train starts over BOTH missed heads in its first batch (carry 14: batch "
+              "by default); the second add finds #12 pending in it, ALREADY -- never a second train",
+              rc == 0 and len(starts) == 1 and [e["pr"] for e in queued] == [11, 12]
+              and spool_read(st)[0] == []
               and any(ln.startswith("STARTED train.sh") for ln in lines)
-              and any(ln.startswith("ADDED #12 to the live train") for ln in lines))
+              and any(ln.startswith("ALREADY #12:") for ln in lines))
         rc, lines = live(two, st, launch)
         check("sweep, a train live: the next pass adds nothing and starts nothing (exactly once)",
-              rc == 0 and len(starts) == 1 and len(spool_read(st)[0]) == 1)
+              rc == 0 and len(starts) == 1 and spool_read(st)[0] == [])
         st = Path(tempfile.mkdtemp(dir=tmp.name))
         busy = subprocess.Popen(["sleep", "60"])
         sleepers.append(busy)
@@ -5609,6 +5860,17 @@ def _state_self_test(check, go, merged, throwaway_git_init) -> None:
           "for a green gate; True for the raise-only suites (the control)",
           gate_raise_only(lt, running) is False and gate_raise_only(lt, [cr(GATE), *shape3045[1:]]) is False
           and gate_raise_only(lt, suites) is True)
+    def lt_gh(behaviour):  # carry 2: gate_raise_only reads through job_log, under either gh
+        def run(argv, **_k):
+            if behaviour == "needs" and ESCAPES_FLAG not in argv:
+                return 1, "the response contains terminal escape sequences"
+            if behaviour == "lacks" and ESCAPES_FLAG in argv:
+                return 1, f"unknown flag: {ESCAPES_FLAG}"
+            return 0, RAISE_LOG
+        return type("lt_gh", (), {"repo": "o/r", "run": staticmethod(run)})
+    check("carry 2: gate_raise_only reads the raise-only suites under a gh that needs the escape flag and under "
+          "one that lacks it (job_log), so both are owed",
+          gate_raise_only(lt_gh("needs"), suites) is True and gate_raise_only(lt_gh("lacks"), suites) is True)
     rc, out = owed_cli(shape3045, BUDGET_F, RAISE_FIXTURE, None, False, "## Summary\n", "--pr", "3045",
                        diff_fail=True)
     check("#3073 O2: a failed three-dot diff read is not approval owed: RED, rc 1",
@@ -5739,12 +6001,19 @@ def _infra_self_test(check) -> None:
     # main_green, in both arms, over a world of that run.
     url = f"https://github.com/o/r/actions/runs/{rid}/job/{gid}"
 
-    def world(attempt="1", glog=logs[gid], clears=False):
+    def world(attempt="1", glog=logs[gid], clears=False, gh=""):
+        """`gh` is the job-log flag behaviour: "needs" refuses a log without
+        --allow-escape-sequences, "lacks" (gh 2.89, measured) refuses the flag
+        as unknown, "" accepts either."""
         w = {"runs": [{"name": GATE, "status": "completed", "conclusion": "failure", "started_at": "1",
                        "id": 5, "details_url": url, "check_suite": {"id": 1}}], "posts": []}
 
         def run(argv, cwd=ROOT, stdin=None):
             a = " ".join(argv)
+            if "/logs" in a and gh == "needs" and "--allow-escape-sequences" not in argv:
+                return 1, "the response contains terminal escape sequences; pass --allow-escape-sequences"
+            if gh == "lacks" and "--allow-escape-sequences" in argv:
+                return 1, "unknown flag: --allow-escape-sequences\n\nUsage:  gh api <endpoint> [flags]"
             if "check-runs" in a:
                 return 0, "\n".join(json.dumps(c) for c in w["runs"])
             if "-X" in argv:
@@ -5791,6 +6060,35 @@ def _infra_self_test(check) -> None:
     lines, stop = act(w, run, ts("23:43"), overlap=False)
     check("V142 blocking: the re-run that clears main lets the wait pass (no stop), one re-run",
           w["posts"] == [rerun] and stop == "")
+    for flag in ("needs", "lacks"):
+        w, run = world(gh=flag)
+        lines, _ = act(w, run, ts("23:43"))
+        check(f"carry 2: infra_rerun reads its job logs through job_log, so a gh that {flag} "
+              "--allow-escape-sequences still re-runs the stamp's run once, logged INFRA-RERUN",
+              w["posts"] == [rerun] and any(x.startswith(f"INFRA-RERUN gate run {rid} attempt 1 (") for x in lines))
+    def gh_logs(behaviour: str, calls: list):
+        def run(argv, cwd=ROOT, stdin=None):
+            calls.append(argv)
+            flagged = ESCAPES_FLAG in argv
+            if behaviour == "lacks" and flagged:
+                return 1, f"unknown flag: {ESCAPES_FLAG}"
+            if behaviour == "needs" and not flagged:
+                return 1, "the response contains terminal escape sequences"
+            if behaviour == "gone":
+                return 1, "HTTP 410: logs expired"
+            return 0, "LOG"
+        return run
+    got = {}
+    for b in ("needs", "lacks", "gone"):
+        calls: list = []
+        got[b] = (job_log(gh_logs(b, calls), "o/r", 7), [ESCAPES_FLAG in c for c in calls])
+    check("carry 2: job_log passes the flag first, reads without it only where gh does not know the flag, and "
+          "returns None for a read that fails otherwise (one call, no retry)",
+          got == {"needs": ("LOG", [True]), "lacks": ("LOG", [True, False]), "gone": (None, [True])})
+    w, run = world(gh="needs", glog=gate_log("tests / fast: failure (this run)", pair[1]))
+    lines, _ = act(w, run, ts("23:43"))
+    check("carry 2 null: through the same reader, a gate red on a non-infra job is never re-run",
+          w["posts"] == [] and not any(x.startswith("INFRA") for x in lines))
     w, run = world(glog=gate_log(pair[0], "tests / browser: SKIPPED (this run)"))
     lines, stop = act(w, run, ts("23:43"), overlap=False)
     check("V142 blocking null: a gate that does not qualify is not re-run and main stops red as today",
@@ -6756,16 +7054,70 @@ def _batch_self_test(check) -> None:
                 sys.modules["queue_pre_flight"] = real_pf
         rec = queue_seen_read(Path(d))
     check("P189 HOLDER arm, pre-flight: a PARK at `recarry` (the worktree holder) is recorded skipped [HOLDER] "
-          "with its verdict, so a same-verdict re-add is admitted; a `carry` PARK is skipped with no class",
+          "with its verdict, so a same-verdict re-add is admitted; a `carry` PARK is skipped [PRE-FLIGHT]",
           kept == [] and rec["7"] == {"verdict": V7, "state": "skipped", "class": HOLDER}
-          and rec["8"] == {"verdict": V7, "state": "skipped"}
-          and already_held(7, V7, rec, set()) is None and bool(already_held(8, V7, rec, set())))
+          and rec["8"] == {"verdict": V7, "state": "skipped", "class": PREFLIGHT_PARK}
+          and already_held(7, V7, rec, set()) is None and already_held(8, V7, rec, set()) is None)
     check("P189 HOLDER arm: an entry skipped [HOLDER] and re-added at the SAME verdict is ADDED by `add` and "
           "by the drain (batch 2), and a ci-skipped one at the same verdict is ALREADY on both sides",
           add_rc == [0, 0] and add_said[0].startswith("ADDED #7") and add_said[1].startswith("ALREADY #8:")
           and more and [int(e["pr"]) for e in bs[-1]] == [7] and "ADDED #7: batch 2 of this train" in drain_said
           and any(ln.startswith("ALREADY #8:") for ln in drain_said))
 
+    # Carries 3/18: a pre-flight park at the SAME verdict rejoins once its cause is
+    # cured (the add re-runs the pre-flight) and is refused, spooling nothing, while it holds.
+    def pf_add(pr, cls, status, step="findings", why="1 unrouted", at=V7, drain=False):
+        """`add` of <pr> at verdict <at> against a live train whose record says it
+        was skipped [<cls>] at V7; the re-run pre-flight answers <status> at
+        <step>. <drain>: the live train then drains its spool (queue_take)."""
+        with tempfile.TemporaryDirectory() as d:
+            st, pl2, pf_calls = Path(d), [], []
+            tq = Train("o/r", st, None, "", (), 1, run=lambda *a, **k: (0, ""), log=pl2.append)
+            tq.admit_add = lambda item: None
+            tq.preflight_entry = lambda item: (pf_calls.append(item["pr"]),
+                                               (status, step, why) if status != "PASS" else ("PASS", "", ""))[1]
+            (st / QUEUE_OPEN).write_text(f"{os.getpid()}\n")
+            tq._seen = {str(pr): {"verdict": V7, "state": "skipped", **({"class": cls} if cls else {})}}
+            queue_seen_write(st, tq._seen)
+            rc = train_add(tq, {"pr": pr, "verdict": at}, ["true"], launch=lambda *a: (0, "no"))
+            spool = spool_read(st)[0]
+            if not drain:
+                return rc, pl2, spool
+            bs = [[{"pr": 1, "verdict": V7}]]
+            tq._queue = {"batches": bs, "next": 1, "closed": False}
+            return rc, pl2, spool, tq.queue_take(bs, 1), bs, pf_calls
+    rc_ok, say_ok, sp_ok = pf_add(7, PREFLIGHT_PARK, "PASS")
+    rc_bad, say_bad, sp_bad = pf_add(7, PREFLIGHT_PARK, "PARK")
+    rc_ci, say_ci, sp_ci = pf_add(8, None, "PASS")
+    check("carries 3/18: a cured pre-flight park rejoins at the same verdict (ADDED, spooled); the uncured one is "
+          "ADD REFUSED rc 1 with no spool line; a ci skip at the same verdict stays ALREADY (null)",
+          rc_ok == 0 and say_ok[0].startswith("ADDED #7") and [e["pr"] for e in sp_ok] == [7]
+          and rc_bad == 1 and say_bad[0].startswith("ADD REFUSED #7 findings: 1 unrouted") and sp_bad == []
+          and rc_ci == 0 and say_ci[0].startswith("ALREADY #8:") and sp_ci == [])
+    # Carry 19's other arms: a `policy` park, the drain, and a park at a new verdict.
+    rc_pol, say_pol, sp_pol = pf_add(9, PREFLIGHT_PARK, "PASS", step="policy")
+    rc_polx, say_polx, sp_polx = pf_add(9, PREFLIGHT_PARK, "PARK", step="policy", why="owner approval missing")
+    check("carry 19: a cured `policy` park rejoins at the same verdict (ADDED, spooled); uncured it is "
+          "ADD REFUSED rc 1 naming the step and why, with no spool line (control)",
+          rc_pol == 0 and say_pol[0].startswith("ADDED #9") and [e["pr"] for e in sp_pol] == [9]
+          and rc_polx == 1 and say_polx[0].startswith("ADD REFUSED #9 policy: owner approval missing")
+          and sp_polx == [])
+    drained_to = {}
+    for step in ("policy", "findings"):
+        rc_d, say_d, _sp, more_d, bs_d, _c = pf_add(9, PREFLIGHT_PARK, "PASS", step=step, drain=True)
+        drained_to[step] = (rc_d, more_d, [int(e["pr"]) for e in bs_d[-1]],
+                            "ADDED #9: batch 2 of this train" in say_d, any(x.startswith("ALREADY #9") for x in say_d))
+    check("carry 19: a cured `policy` park and a cured `findings` park, once added, reach the next batch through "
+          "the drain (queue_take: batch 2, never ALREADY), the add and the drain on the one predicate",
+          drained_to == {k: (0, True, [9], True, False) for k in ("policy", "findings")})
+    V9 = "9" * 40
+    rc_new, say_new, sp_new, more_new, bs_new, calls_new = pf_add(9, PREFLIGHT_PARK, "PARK", at=V9, drain=True)
+    check("carry 19 null: a park re-added at a NEW verdict behaves as today -- admitted with no pre-flight re-read "
+          "at the add, spooled at the new verdict, drained into the next batch",
+          rc_new == 0 and say_new[0].startswith("ADDED #9") and calls_new == []
+          and [(e["pr"], e["verdict"]) for e in sp_new] == [(9, V9)] and more_new
+          and [int(e["pr"]) for e in bs_new[-1]] == [9])
+
     def live_add(w, n):  # the REAL train_add against the live train's state dir, admit_add passed
         al: list[str] = []
         ta = Train("o/r", w["state"], None, "", (), 1, run=stub(w), log=al.append)
@@ -7373,6 +7725,9 @@ def _parser() -> argparse.ArgumentParser:
                        help="write the queue: every open non-record pull request whose newest posted verdict, "
                             "verdict/<pr>'s tip, is merge at its head or carries to it, oldest first")
     q.add_argument("out", help="the queue file to write ('-': stdout)")
+    q.add_argument("--stamp", action="store_true",
+                   help="a stamp's queue: the record pull requests every other queue holds HELD-FOR-STAMP "
+                        "join it, so they merge in one batch before the tag (carry 15)")
     ad = sub.add_parser("add", parents=[common, train_opts],
                         help="load one verdicted pull request into the state dir's live train (its next "
                              "batch), or start that train; the train.sh flags follow `--`")
@@ -7387,6 +7742,8 @@ def _parser() -> argparse.ArgumentParser:
     ad.add_argument("--verdict-comment", help="the verdict comment's id, quoted in a mandate approval")
     ad.add_argument("--priority", action="store_true",
                     help="HOTFIX: the spool's drain puts this entry before critical-path and arrival order (P312)")
+    ad.add_argument("--stamp", action="store_true",
+                    help="a stamp's add: a record pull request is added, not HELD-FOR-STAMP (carry 15)")
     ad.add_argument("--auto", action="store_true",
                     help="a started train is a bare train.sh launch (RECOMMENDED by default) with --mandate, "
                          "as the sweep's is: bus.sh's post calls this")
@@ -7395,6 +7752,7 @@ def _parser() -> argparse.ArgumentParser:
                              "head, unless the ledger holds an open train-stop; a started train is a bare "
                              "train.sh launch, which runs RECOMMENDED")
     sw.add_argument("--mandate", help="passed to the started train; omit to never approve a code-owned head")
+    sw.add_argument("--stamp", action="store_true", help="a stamp's sweep: record pull requests are added too")
     sw.add_argument("--state-dir", default=train_opts.get_default("state_dir"))
     w = sub.add_parser("wait-ci", parents=[common])
     w.add_argument("sha")
@@ -7423,6 +7781,13 @@ def main(argv: list[str]) -> int:
         sys.stdout.reconfigure(line_buffering=True)
     if argv[:1] == ["--self-test"]:
         return _self_test()
+    if argv[:1] == ["job-log"]:  # `job-log <job id> <owner/repo>`: job_log for a shell caller
+        if len(argv) != 3:
+            print("usage: merge_train.py job-log <job id> <owner/repo>", file=sys.stderr)
+            return 2
+        text = job_log(None, argv[2], argv[1])
+        sys.stdout.write(text or "")
+        return 0 if text is not None else 1
     stop_on_signal()
     rest: list[str] = []
     if argv[:1] == ["add"] and "--" in argv:  # the train.sh flags a started train gets
@@ -7432,7 +7797,7 @@ def main(argv: list[str]) -> int:
         if a.auto and rest:
             print("REFUSE add: --auto is the started train's flags; give it or `-- <train.sh flags>`, not both")
             return 2
-        t = Train(a.repo, Path(a.state_dir), a.mandate, a.approver_role, (), a.min_runs)
+        t = Train(a.repo, Path(a.state_dir), a.mandate, a.approver_role, (), a.min_runs, stamp=a.stamp)
         if a.front and a.remove:
             print("REFUSE add: --front and --remove are two edits; give one")
             return 2
@@ -7474,11 +7839,11 @@ def main(argv: list[str]) -> int:
         print(f"{state.upper()} {a.sha} pending: {' '.join(pending) or 'none'} red: {' '.join(red) or 'none'}")
         return {"green": 0, "red": 1, "wait": 3}[state]
     if a.cmd == "sweep":
-        t = Train(a.repo, Path(a.state_dir), a.mandate, "", (), a.min_runs)
+        t = Train(a.repo, Path(a.state_dir), a.mandate, "", (), a.min_runs, stamp=a.stamp)
         return sweep(t, auto_train_argv(a.repo, a.state_dir, a.mandate))
     if a.cmd == "queue":
         to_stdout = a.out == "-"  # the queue alone on stdout, its lines on stderr
-        t = Train(a.repo, Path("."), None, "", (), a.min_runs,
+        t = Train(a.repo, Path("."), None, "", (), a.min_runs, stamp=a.stamp,
                   log=(lambda m: print(m, file=sys.stderr)) if to_stdout else print)
         try:
             queue = t.build_queue()
diff --git a/tools/audit/seat/probe_bridge.py b/tools/audit/seat/probe_bridge.py
index c93938b75..ee5643846 100644
--- a/tools/audit/seat/probe_bridge.py
+++ b/tools/audit/seat/probe_bridge.py
@@ -46,7 +46,6 @@ import argparse
 import json
 import re
 import statistics
-import subprocess
 import sys
 from pathlib import Path
 
@@ -163,11 +162,15 @@ def disagreement(derived: dict, tree: dict) -> list[str]:
             or abs(derived[py] - tree[py]) > ROUNDING]
 
 
-def gh(path: str) -> str:
-    p = subprocess.run(["gh", "api", path], capture_output=True, text=True)
-    if p.returncode:
-        raise SystemExit(f"probe_bridge: gh api {path} failed: {p.stderr.strip()[:300]}")
-    return p.stdout
+def job_log(repo: str, job_id) -> str:
+    """One Actions job's log through merge_train.job_log, the one reader that
+    passes gh's escape-sequence flag where gh knows it."""
+    sys.path.insert(0, str(Path(__file__).resolve().parent))
+    import merge_train
+    text = merge_train.job_log(None, repo, job_id)
+    if text is None:
+        raise SystemExit(f"probe_bridge: the log of job {job_id} could not be read")
+    return text
 
 
 def self_test() -> int:
@@ -253,7 +256,7 @@ def main(argv: list[str]) -> int:
         cr.gather_runs(f, repo=a.repo, window=a.last)
         runs = [r for r in json.loads(f.read_text())["workflow_runs"] if r.get("status") == "completed"]
     ref, unit = references(json.loads((HARNESS / "fast_scripts.json").read_text()))
-    got = bridge(runs, lambda j: log_seconds(gh(f"repos/{a.repo}/actions/jobs/{j['id']}/logs")), ref, unit)
+    got = bridge(runs, lambda j: log_seconds(job_log(a.repo, j["id"])), ref, unit)
     print(f"probe_bridge: {got['runs']} probed fast (3.14) push runs; PROBE_REFERENCE_S implied "
           f"3.14 {got['3.14']} (runs {got['spread'][0]}..{got['spread'][1]}), 3.13 {got.get('3.13')}; "
           f"in the tree {cr.PROBE_REFERENCE_S}")

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
