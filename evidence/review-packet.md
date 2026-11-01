# Review packet #3072
head: cae73963448dc1f660a70797a55372fdac19a243
base: 8fec54ee2afb5e37687f34bc5fd3aa7280f64e1f

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=124731037632 success
arch-score / arch-score id=124741325287 success
arm id=124727553510 skipped
budget-raise-gate / budget-raise-gate id=124741325274 success
cancel-superseded id=124727558756 success
codeql id=124741326233 skipped
codeql / Analyze (actions) id=124730686045 success
codeql / Analyze (javascript-typescript) id=124730686088 success
codeql / Analyze (python) id=124730686092 success
gate id=124741685627 success
governance id=124741326509 skipped
governance / delivery-status id=124730686097 success
governance / delivery-status-publish id=124730687286 skipped
governance / env-matrix id=124730686116 success
governance / instrument-self-tests id=124730686160 success
governance / policy-docs id=124730686136 success
governance / record id=124730686963 skipped
governance / wave-script id=124730686248 success
hassfest id=124741326175 skipped
hassfest / hassfest id=124730686030 success
kernel-points id=124741326041 skipped
pr-contract / pr-contract id=124741549270 success
prelude id=124727558640 success
refresh id=124727558819 success
tests id=124741326246 skipped
tests / arch-instrument id=124732664508 success
tests / briefs id=124730686096 success
tests / browser id=124732664530 success
tests / ci-ratchet id=124740980229 skipped
tests / claims-autofix id=124740979757 skipped
tests / closure-scope id=124730686159 success
tests / closures id=124732664478 success
tests / closures-autofix id=124740357305 skipped
tests / coverage id=124732664504 success
tests / coverage-ratchet id=124737920827 success
tests / fast (3.14) id=124732664487 success
tests / graders-head-copy id=124737920821 success
tests / lane-proofs id=124740978914 success
tests / mutation id=124730686091 success
tests / mutation-autofix id=124732550938 skipped
tests / mutation-pins id=124732550753 skipped
tests / nightly-ha id=124732665035 skipped
tests / nightly-status id=124730686110 success
tests / replay id=124732665376 skipped
tests / typing id=124732664447 success
validate id=124741326118 skipped
validate / validate-hacs id=124730686120 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 dev/audit/harnesses/r10_row_head_carry.py --since 2026-10-28 --limit 40 --cache pairs.jsonl
             `dev/audit/harnesses/r10_row_head_carry.py` is in the tree at this head
  unverified git log --no-merges --format='%h %s' 21b4552^1..21b4552^2 | grep -c '^[0-9a-f]* roster_edit '
             `git log` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         bash tools/audit/seat/body_patch.sh --self-test
             `tools/audit/seat/body_patch.sh` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py --base origin/main
             `tools/pr/ci_predict.py` is in the tree at this head
  unverified git diff --stat $(git merge-base origin/main HEAD)...HEAD -- VERSION RELEASE_NOTES.md tests/golden custom_components/heatpump_optimizer/manifest.json
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 5 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.github/workflows/tests.yml b/.github/workflows/tests.yml
index e9a458bc3..60f00ec0a 100644
--- a/.github/workflows/tests.yml
+++ b/.github/workflows/tests.yml
@@ -2310,7 +2310,8 @@ jobs:
           python3 -I tests/ci_ratchet.py --gather --metrics-dir "$M"
       # The window is ci.yml's push runs and, across the cut-over, the
       # pre-umbrella Tests runs, each carrying its jobs: the critical path is
-      # a CI run's span to its last `tests / *` job (U9a). Its reads and its
+      # a run's work to its last `tests / *` job with runner queue removed
+      # (see tests/ci_ratchet.py run_minutes; U9a). Its reads and its
       # refusals are tests/ci_ratchet.py's, self-tested above.
       - name: Fetch the recent push runs' durations
         env:
diff --git a/dev/audit/harnesses/r10_row_head_carry.py b/dev/audit/harnesses/r10_row_head_carry.py
new file mode 100644
index 000000000..fde656823
--- /dev/null
+++ b/dev/audit/harnesses/r10_row_head_carry.py
@@ -0,0 +1,195 @@
+#!/usr/bin/env python3
+"""Would carrying a row-only head's CI results save CI? (R10-FLY-ROW-HEAD-CARRY, arm a)
+
+    python3 dev/audit/harnesses/r10_row_head_carry.py --since 2026-10-28 --limit 40 \\
+        [--cache pairs.jsonl]
+    python3 dev/audit/harnesses/r10_row_head_carry.py --self-test
+
+The carry arm proposed: when a PR's new head R differs from its first parent P
+by exactly `dev/programme/delivery/<N>.md` (open_pr.sh's second push), keep
+P's ci.yml run instead of cancelling it, and let R skip the four code units
+(tests, codeql, hassfest, validate) and reuse P's. GitHub cancels a run, never
+a part of one, so keeping P keeps ALL of P's run.
+
+THE RULES.
+- Row-only: `git diff --name-only R^1 R` is exactly `[dev/programme/delivery/<N>.md]`
+  for the PR's own N (`classify`). The window is every first-parent
+  "Merge pull request #N" commit on origin/main since --since; a PR's commits
+  are `M^1..M^2`. The newest --limit row-only pairs are read from the API.
+- Job-seconds: per ci.yml run at a head, latest attempt, the sum over jobs of
+  `completed_at - started_at`, grouped by the job name's unit (text before
+  ` / `). Job-seconds, not billed minutes.
+- Per pair, from the CODE runs (display_title `CI code ...`):
+  gain = P's job-seconds already spent in the four units (today wasted by the
+  cancel, under the carry kept and reused);
+  loss = R's code-run job-seconds outside the four units (what P's kept run
+  would also spend: prelude, governance, body units, gate) minus what P
+  already spent outside them;
+  net = gain - loss, summed over the pairs (`net`). Negative: the carry costs CI.
+- gap = R's first code run created minus P's (s): the lead time a carry could save.
+
+NULL CONTROL (`--self-test`, offline). The classifier reads a row-only head
+as row-only and refuses each other shape the brief named (the row plus a
+CLAUDE.md byte, another PR's row, a new unclassified .md). `net` reads
+negative on a pair whose P was cancelled at once and POSITIVE on the same pair
+had P run to completion (P's spend equal to R's): had the premise "P is
+cancelled early" been false, the harness would have said the carry pays.
+"""
+from __future__ import annotations
+
+import argparse
+import json
+import re
+import statistics
+import subprocess
+import sys
+from datetime import datetime
+
+REPO = "tvofi/heatpump_optimizer"
+CARRIED = ("tests", "codeql", "hassfest", "validate")
+
+
+def git(*a: str) -> str:
+    return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout
+
+
+def api(path: str) -> dict:
+    return json.loads(subprocess.run(["gh", "api", path], capture_output=True, text=True, check=True).stdout)
+
+
+def classify(pr: str, files: list[str]) -> str:
+    row = f"dev/programme/delivery/{pr}.md"
+    return "row-only" if files == [row] else ("row+other" if row in files else "other")
+
+
+def pairs(since: str) -> tuple[list[tuple[str, str, str]], dict]:
+    """[(pr, P, R)] row-only, newest merge first; and the class counts over every PR commit."""
+    out, counts = [], {}
+    for line in git("log", "--first-parent", "--merges", f"--since={since}", "--format=%H %s", "origin/main").splitlines():
+        m = re.match(r"(\w+) Merge pull request #(\d+) ", line)
+        if not m:
+            continue
+        merge, pr = m.groups()
+        for c in git("rev-list", f"{merge}^1..{merge}^2").split():
+            p = git("rev-parse", f"{c}^1").strip()
+            cls = classify(pr, git("diff", "--name-only", p, c).split())
+            counts[cls] = counts.get(cls, 0) + 1
+            if cls == "row-only":
+                out.append((pr, p, c))
+    return out, counts
+
+
+def _ts(s: str) -> datetime:
+    return datetime.fromisoformat(s.replace("Z", "+00:00"))
+
+
+def runs_at(sha: str) -> list[dict]:
+    out = []
+    for r in api(f"repos/{REPO}/actions/workflows/ci.yml/runs?head_sha={sha}&per_page=100")["workflow_runs"]:
+        units: dict[str, float] = {}
+        for j in api(f"repos/{REPO}/actions/runs/{r['id']}/jobs?filter=latest&per_page=100")["jobs"]:
+            if j["started_at"] and j["completed_at"]:
+                u = j["name"].split(" / ")[0]
+                units[u] = units.get(u, 0) + max((_ts(j["completed_at"]) - _ts(j["started_at"])).total_seconds(), 0)
+        out.append({"id": r["id"], "title": r["display_title"], "conclusion": r["conclusion"] or r["status"],
+                    "created": r["created_at"], "units_s": units})
+    return out
+
+
+def net(p_runs: list[dict], r_runs: list[dict]) -> dict | None:
+    """One pair's figures from its CODE runs; None when either head has none."""
+    pc = [r for r in p_runs if r["title"].startswith("CI code")]
+    rc = [r for r in r_runs if r["title"].startswith("CI code")]
+    if not pc or not rc:
+        return None
+
+    def spent(runs, inside):
+        return sum(v for r in runs for u, v in r["units_s"].items() if (u in CARRIED) == inside)
+    gain = spent(pc, True)
+    loss = spent(rc, False) - spent(pc, False)
+    return {"gap_s": (min(_ts(r["created"]) for r in rc) - min(_ts(r["created"]) for r in pc)).total_seconds(),
+            "p_spent_s": sum(sum(r["units_s"].values()) for r in p_runs), "gain_s": gain, "loss_s": loss,
+            "net_s": gain - loss, "r_carried_s": spent(rc, True),
+            "r_all_s": sum(sum(r["units_s"].values()) for r in r_runs),
+            "p_code": ",".join(r["conclusion"] for r in pc), "r_code": ",".join(r["conclusion"] for r in rc)}
+
+
+def self_test() -> int:
+    n = fails = 0
+
+    def check(name, got, want):
+        nonlocal n, fails
+        n += 1
+        if got != want:
+            fails += 1
+            print(f"FAIL {name}: got {got!r}, want {want!r}")
+    row = "dev/programme/delivery/7.md"
+    check("a row-only head", classify("7", [row]), "row-only")
+    check("null: the row plus a CLAUDE.md byte", classify("7", ["CLAUDE.md", row]), "row+other")
+    check("null: the row plus a new unclassified .md", classify("7", [row, "notes.md"]), "row+other")
+    check("null: another PR's row", classify("7", ["dev/programme/delivery/8.md"]), "other")
+    t0, t1 = "2026-10-31T10:00:00Z", "2026-10-31T10:00:15Z"
+    full = {"tests": 3000.0, "codeql": 300.0, "hassfest": 20.0, "validate": 10.0,
+            "prelude": 30.0, "governance": 900.0, "pr-contract": 600.0, "gate": 700.0}
+    r = [{"title": "CI code pr=7", "conclusion": "success", "created": t1, "units_s": full}]
+    early = [{"title": "CI code pr=7", "conclusion": "cancelled", "created": t0,
+              "units_s": {"prelude": 30.0, "tests": 60.0, "governance": 20.0}}]
+    done = [{"title": "CI code pr=7", "conclusion": "success", "created": t0, "units_s": dict(full)}]
+    e = net(early, r)
+    check("P cancelled at once: the carry costs CI", (e["net_s"] < 0, e["gain_s"], e["loss_s"]), (True, 60.0, 2180.0))
+    d = net(done, r)
+    check("null: P run to completion: the same harness says the carry pays", (d["net_s"] > 0, d["net_s"]),
+          (True, 3330.0))
+    check("the gap", e["gap_s"], 15.0)
+    check("no code run at a head: not a pair", net([], r), None)
+    print(f"r10_row_head_carry self-test: {n} checks, {fails} failed")
+    return 1 if fails else 0
+
+
+def main(argv: list[str]) -> int:
+    ap = argparse.ArgumentParser()
+    ap.add_argument("--since")
+    ap.add_argument("--limit", type=int, default=40)
+    ap.add_argument("--cache", help="JSONL of read pairs: read if present, else written")
+    ap.add_argument("--self-test", action="store_true")
+    a = ap.parse_args(argv)
+    if a.self_test:
+        return self_test()
+    if not a.since:
+        ap.error("--since is required")
+    found, counts = pairs(a.since)
+    print("classes over every PR commit in the window:", json.dumps(counts, sort_keys=True))
+    print(f"PRs with a row-only head: {len({p for p, _, _ in found})}")
+    rows = []
+    try:
+        rows = [json.loads(x) for x in open(a.cache)] if a.cache else []
+    except FileNotFoundError:
+        pass
+    if not rows:
+        for pr, p, r in found[: a.limit]:
+            rows.append({"pr": pr, "P": p, "R": r, "P_runs": runs_at(p), "R_runs": runs_at(r)})
+        if a.cache:
+            with open(a.cache, "w") as fh:
+                fh.writelines(json.dumps(x) + "\n" for x in rows)
+    figs = []
+    for x in rows:
+        f = net(x["P_runs"], x["R_runs"])
+        if f is None:
+            print(x["pr"], "SKIP: no code run at one head")
+            continue
+        figs.append(f)
+        print(x["pr"], *(f"{k}={v:.0f}" if isinstance(v, float) else f"{k}={v}" for k, v in f.items()))
+    if not figs:
+        print("RESULT pairs=0")
+        return 1
+    print(f"pairs={len(figs)} PRs #{rows[-1]['pr']}..#{rows[0]['pr']}")
+    for k in ("gap_s", "p_spent_s", "gain_s", "loss_s", "net_s", "r_carried_s", "r_all_s"):
+        v = [f[k] for f in figs]
+        print(f"{k}: median={statistics.median(v):.0f} sum={sum(v):.0f} max={max(v):.0f}")
+    for k in ("p_code", "r_code"):
+        print(k, json.dumps({c: sum(f[k] == c for f in figs) for c in sorted({f[k] for f in figs})}))
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/dev/programme/delivery/2844.md b/dev/programme/delivery/2844.md
index 6be38ffeb..ef66b07e2 100644
--- a/dev/programme/delivery/2844.md
+++ b/dev/programme/delivery/2844.md
@@ -1 +1 @@
-- [#2844](https://github.com/tvofi/heatpump_optimizer/pull/2844) — **merged `21b4552`**, roster: round-10 batch 16 (5 ops).
+- [#2844](https://github.com/tvofi/heatpump_optimizer/pull/2844) — **merged `21b4552`**, roster: round-10 batch 16 (9 ops).
diff --git a/dev/programme/delivery/2846.md b/dev/programme/delivery/2846.md
index 7883da4a2..1d38257e7 100644
--- a/dev/programme/delivery/2846.md
+++ b/dev/programme/delivery/2846.md
@@ -1 +1 @@
-- [#2846](https://github.com/tvofi/heatpump_optimizer/pull/2846) — **merged `0dfc063`**, triage: batch 32, P191 (V111 record PR swept on a refused merge attempt).
+- [#2846](https://github.com/tvofi/heatpump_optimizer/pull/2846) — **merged `0dfc063`**, triage: batch 32, P184-P191 (V104-V111).
diff --git a/dev/programme/delivery/3072.md b/dev/programme/delivery/3072.md
new file mode 100644
index 000000000..a88bc8c5e
--- /dev/null
+++ b/dev/programme/delivery/3072.md
@@ -0,0 +1 @@
+- [#3072](https://github.com/tvofi/heatpump_optimizer/pull/3072) — **open**, R10-FLY-ROW-HEAD-CARRY: fly row head carry (R10-FLY-ROW-HEAD-CARRY)
diff --git a/tests/closures.json b/tests/closures.json
index 9b305f39c..233301771 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3991,6 +3991,7 @@
    "dev/audit/harnesses/r10_review_strength_mutants.py",
    "dev/audit/harnesses/r10_roster_push_race.sh",
    "dev/audit/harnesses/r10_roster_sync_base.py",
+   "dev/audit/harnesses/r10_row_head_carry.py",
    "dev/audit/harnesses/r10_sav_actuation_phase.py",
    "dev/audit/harnesses/r10_sav_baseline.py",
    "dev/audit/harnesses/r10_sav_baseline_mutants.py",
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index c45039bb1..978698cc5 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -47,7 +47,7 @@ sweep's standing-seat liveness step keep them alive.
 
 - [`features_block.py`](instruments/features_block.py.md) — runs one block of `tests/features.py`
 - [`body_push.sh`](instruments/body_push.sh.md) — publishes a handoff's BODY.md on the orphan ref `handoff-body/<topic>` (plus RESUME.md), parentless first commit, fast-forwards after
-- [`body_patch.sh`](instruments/body_patch.sh.md) — repairs an open pull request's BODY without moving its head
+- [`body_patch.sh`](instruments/body_patch.sh.md) — repairs an open pull request's BODY, or any pull request's TITLE (`--title`), without moving its head
 - [`autofix_statuses.sh`](instruments/autofix_statuses.sh.md) — re-derives what `mutation-autofix` and `closures-autofix` answered on recent pull-request runs
 - [`bus.sh`](instruments/bus.sh.md) — git refs as the programme's message bus
 - [`review_packet.py`](instruments/review_packet.py.md) — the fix reviewer's packet at the frozen head
diff --git a/tools/audit/seat/body_patch.sh b/tools/audit/seat/body_patch.sh
index 33617a480..b3c0012fd 100644
--- a/tools/audit/seat/body_patch.sh
+++ b/tools/audit/seat/body_patch.sh
@@ -1,6 +1,7 @@
 #!/bin/bash
 { set +x; } 2>/dev/null # before anything: a caller's `bash -x` would trace the token
 # body_patch.sh [--dry-run] [--repo <owner/repo>] <pr> <expected-head-sha> <body.md>
+# body_patch.sh [--dry-run] [--repo <owner/repo>] --title <pr> <expected-head-sha> <title>
 # body_patch.sh --self-test
 #
 # Repair an open pull request's BODY without moving its head (Lean flow study
@@ -31,6 +32,15 @@
 # The PATCH sets `body` only: it cannot move the head. `pr-contract` re-runs on
 # the `edited` event and reads the body from the API.
 #
+# --title (R10-FLY-ROW-HEAD-CARRY carry 4) runs the same steps on the TITLE:
+# the PATCH carries {"title"} alone and the read-back compares the title
+# exactly. A title is one line, non-empty and unpadded, refused before any
+# read. The pull request may be open or closed: `record_row.py` derives a
+# merged row's title from the API, so a merged pull request's wrong title is
+# corrected here and the row regenerated from it. An open one's live body is
+# judged by step 3's contract under the NEW title, which pr-contract reads;
+# a closed one runs no contract, because pr-contract never re-runs on it.
+#
 # --dry-run runs steps 1-3, then prints the exact PATCH request and stops
 # before signing anything. Exit 0 = patched and read back; 1 = refused.
 #
@@ -57,31 +67,42 @@ RB_SLEEP=${BODY_PATCH_READBACK_SLEEP:-2}
 
 # One verdict token for a pull request document and the body file:
 #   ok | stale <sha> | body | bad <why>
-verdict() { # head body-file < pr-json
+# The field is `body` (an open pull request only; one trailing newline is
+# GitHub's; the second argument is the body FILE) or `title` (any state;
+# compared exactly; the second argument is the title itself). `body` in the
+# verdict means the FIELD read back differs, whichever field it is.
+verdict() { # head body-file|title [field] < pr-json
   python3 -c '
 import sys, json
 head, f = sys.argv[1], sys.argv[2]
+field = sys.argv[3] if len(sys.argv) > 3 else "body"
 try:
     d = json.loads(sys.stdin.read())
 except ValueError:
     print("bad unparseable response"); sys.exit(0)
-if d.get("state") != "open":
+if field == "body" and d.get("state") != "open":
     print("bad state=%s" % d.get("state")); sys.exit(0)
 live = (d.get("head") or {}).get("sha") or ""
 if live != head:
     print("stale %s" % live); sys.exit(0)
-want = open(f).read(); got = d.get("body") or ""
+want = f if field == "title" else open(f).read(); got = d.get(field) or ""
 def eq1(a, b):
     return a == b or (a.endswith("\n") and a[:-1] == b) or (b.endswith("\n") and b[:-1] == a) # mut:eq1
-print("ok" if eq1(got, want) else "body")' "$1" "$2"
+same = (got == want) if field == "title" else eq1(got, want) # mut:titlereadback
+print("ok" if same else "body")' "$@"
 }
 
 # The contract arm: pr-contract's own policy_lint call, then the carry check.
 # Runs in the current directory (a worktree holding the head's objects).
-contract() { # pr-json base head body -> rc
-  local doc=$1 base=$2 head=$3 body=$4 title author
+contract() { # pr-json base head body|- [title] -> rc   (`-`: the live body the pr-json carries)
+  local doc=$1 base=$2 head=$3 body=$4 title=${5:-} author
   local d; d=$(mktemp -d "${TMPDIR:-/tmp}/body_patch.XXXXXX") || return 1
-  title=$(printf '%s' "$doc" | python3 -c 'import sys, json; print(json.load(sys.stdin).get("title") or "")') || return 1
+  if [ "$body" = - ]; then
+    body=$d/live_body.md
+    printf '%s' "$doc" | python3 -c 'import sys, json; sys.stdout.write(json.load(sys.stdin).get("body") or "")' > "$body" \
+      || { rm -rf "$d"; return 1; }
+  fi
+  [ -n "$title" ] || title=$(printf '%s' "$doc" | python3 -c 'import sys, json; print(json.load(sys.stdin).get("title") or "")') || return 1
   author=$(printf '%s' "$doc" | python3 -c 'import sys, json; print((json.load(sys.stdin).get("user") or {}).get("login") or "")') || return 1
   git diff --no-renames --name-only "$base...$head" > "$d/files" || { rm -rf "$d"; return 1; } # mut:threedot
   git diff --no-renames --name-only --diff-filter=a "$base...$head" > "$d/existing" || { rm -rf "$d"; return 1; } # mut:existing
@@ -105,23 +126,32 @@ patch_body() {
   local dry=0 repo=tvofi/heatpump_optimizer
   [ "${1:-}" = "--dry-run" ] && { dry=1; shift; }
   if [ "${1:-}" = "--repo" ]; then repo=${2:-}; shift 2 2>/dev/null || die "--repo needs a value"; fi
-  [ $# -eq 3 ] || die "usage: body_patch.sh [--dry-run] [--repo <owner/repo>] <pr> <expected-head-sha> <body.md>"
-  local pr=$1 expect=$2 body=$3
+  local field=body
+  [ "${1:-}" = "--title" ] && { field=title; shift; }
+  [ $# -eq 3 ] || die "usage: body_patch.sh [--dry-run] [--repo <owner/repo>] [--title] <pr> <expected-head-sha> <body.md | title>"
+  local pr=$1 expect=$2 body=$3 value
   REPO=$repo
   [[ $repo =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || die "repo '$repo' is not owner/repo"
   [[ $pr =~ ^[0-9]+$ ]] || die "pull request '$pr' is not a number"
   [[ $expect =~ ^[0-9a-f]{40}$ ]] || die "expected head '$expect' is not a 40-hex sha"
-  [ -s "$body" ] || die "no body at $body (missing or empty)"
-  body=$(cd "$(dirname -- "$body")" && printf '%s/%s' "$(pwd)" "$(basename -- "$body")")
+  if [ "$field" = title ]; then
+    [[ -n $body && $body != *$'\n'* && $body != [[:space:]]* && $body != *[[:space:]] ]] || die "the title '$body' is empty, padded or more than one line" # mut:titleshape
+    value=$body
+  else
+    [ -s "$body" ] || die "no body at $body (missing or empty)"
+    body=$(cd "$(dirname -- "$body")" && printf '%s/%s' "$(pwd)" "$(basename -- "$body")")
+  fi
   command -v gh >/dev/null 2>&1 || die "no gh on PATH: the live head cannot be read, so NOTHING was minted or written"
 
   mint_identity # 1
 
+  local want=$body  # the body file, or the title itself
+
   # 2. the live head, read before anything else is done.
   local doc live base v
   doc=$(gh api "repos/$repo/pulls/$pr" 2>/dev/null) \
     || die "pull request #$pr could not be read (gh exited $?); NOTHING was minted or written"
-  v=$(printf '%s' "$doc" | verdict "$expect" "$body")
+  v=$(printf '%s' "$doc" | verdict "$expect" "$want" "$field")
   case "$v" in
     ok|body|stale\ *) ;; # open; the head is judged by the equality below, the body differing is why we are here
     *) die "#$pr did not read back as an open pull request (${v#bad }); NOTHING was minted or written" ;;
@@ -136,11 +166,18 @@ patch_body() {
   git cat-file -e "$expect^{commit}" 2>/dev/null \
     || die "the head $expect is not in this worktree and could not be fetched; the contract cannot run offline, so NOTHING was minted or written"
   git cat-file -e "$base^{commit}" 2>/dev/null || git fetch -q origin "$base" 2>/dev/null
-  contract "$doc" "$base" "$expect" "$body" \
-    || die "the body does not pass the contract at $expect (above): it is NEVER sent; repair it and run this again"
+  local state; state=$(printf '%s' "$doc" | python3 -c 'import sys, json; print(json.load(sys.stdin).get("state") or "")')
+  if [ "$field" = body ]; then
+    contract "$doc" "$base" "$expect" "$body" \
+      || die "the body does not pass the contract at $expect (above): it is NEVER sent; repair it and run this again"
+  elif [ "$state" = open ]; then
+    # The live body, judged under the new title: the pair pr-contract reads next.
+    contract "$doc" "$base" "$expect" - "$value" \
+      || die "the live body does not pass the contract under the title '$value' at $expect (above): it is NEVER sent" # mut:titlecontract
+  fi
 
-  local payload; payload=$(python3 -c 'import sys, json; print(json.dumps({"body": open(sys.argv[1]).read()}))' "$body") \
-    || die "could not write the body payload"
+  local payload; payload=$(python3 -c 'import sys, json; f, v = sys.argv[1:3]; print(json.dumps({f: v if f == "title" else open(v).read()}))' "$field" "$want") \
+    || die "could not write the $field payload"
   if [ "$dry" = 1 ]; then
     printf 'body_patch: DRY-RUN: the contract passed at %s; would PATCH %s/repos/%s/pulls/%s as hpo-author with %s; signed, minted and wrote nothing\n' "$expect" "$API" "$repo" "$pr" "$payload"
     return 0
@@ -155,7 +192,7 @@ patch_body() {
   printf '%s' "$payload" > "$PRIV/pr.json"
   curl -fsS -X PATCH -H @"$PRIV/token.h" -H "$ACCEPT" "$API/repos/$repo/pulls/$pr" \
     --data-binary @"$PRIV/pr.json" >/dev/null \
-    || die "the body PATCH on #$pr was refused; set the body by hand from $body"
+    || die "the $field PATCH on #$pr was refused; set it by hand from $body"
 
   # 5. read it back: body identical, head unmoved.
   # Only a read that says `ok` sets rbok; the OK line is printed past the
@@ -163,10 +200,10 @@ patch_body() {
   local attempt=1 out rbok=0
   while [ "$attempt" -le "$RB_TRIES" ]; do
     if out=$(curl -fsS -H @"$PRIV/token.h" -H "$ACCEPT" "$API/repos/$repo/pulls/$pr" 2>/dev/null); then
-      v=$(printf '%s' "$out" | verdict "$expect" "$body")
+      v=$(printf '%s' "$out" | verdict "$expect" "$want" "$field")
       case "$v" in
         ok) rbok=1; break ;;
-        body) die "#$pr's body read back is not identical to $body modulo one trailing newline" ;; # mut:readback
+        body) die "#$pr's $field read back is not identical to what was sent (a body modulo one trailing newline)" ;; # mut:readback
         stale\ *) die "#$pr's head is now ${v#stale }, not $expect: the head moved around the write" ;; # mut:rbhead
         bad\ state=*) die "#$pr read back as ${v#bad }" ;;
       esac
@@ -175,7 +212,7 @@ patch_body() {
     [ "$attempt" -le "$RB_TRIES" ] && sleep "$RB_SLEEP"
   done
   [ "$rbok" = 1 ] || die "#$pr could not be read back within $RB_TRIES attempts; re-read it by hand" # mut:rbexhaust
-  printf 'body_patch: OK: #%s body patched and read back identical; head %s unmoved\n' "$pr" "$expect"
+  printf 'body_patch: OK: #%s %s patched and read back identical; head %s unmoved\n' "$pr" "$field" "$expect"
 }
 
 if [ "${1:-}" != "--self-test" ]; then
@@ -218,13 +255,16 @@ cat > "$W/prjson.py" <<'PY'
 import json, sys
 # new <file> <head> <base> | get <file> | store <file> <payload>
 v = sys.argv[1:]
-if v[0] == "new":
-    json.dump({"number": 7, "state": "open", "title": "fix: the title", "user": {"login": "hpo-author"},
-               "head": {"sha": v[2]}, "base": {"sha": v[3]}, "body": "the old body, 111"}, open(v[1], "w"))
+if v[0] == "new":   # new <file> <head> <base> [merged]
+    d = {"number": 7, "state": "open", "title": "fix: the title", "user": {"login": "hpo-author"},
+         "head": {"sha": v[2]}, "base": {"sha": v[3], "ref": "main"}, "body": "the old body, 111"}
+    if v[4:] == ["merged"]:
+        d.update(state="closed", merged=True, merge_commit_sha="3f7ed8161234" + "0" * 28)
+    json.dump(d, open(v[1], "w"))
 elif v[0] == "get":
     d = json.load(open(v[1])); d["body"] += "\n"; print(json.dumps(d))   # GitHub appends one newline
-elif v[0] == "store":
-    d = json.load(open(v[1])); d["body"] = json.load(open(v[2]))["body"]; json.dump(d, open(v[1], "w"))
+elif v[0] == "store":   # the PATCH sets the fields it carries, and only those
+    d = json.load(open(v[1])); d.update(json.load(open(v[2]))); json.dump(d, open(v[1], "w"))
 PY
 cat > "$W/bin/gh" <<'STUB'
 #!/bin/bash
@@ -279,6 +319,8 @@ case "$url" in
         python3 "$STUB/../prjson.py" get "$STUB/live.json" | python3 -c 'import sys, json; d = json.load(sys.stdin); d["head"]["sha"] = sys.argv[1]; print(json.dumps(d))' "$(cat "$STUB/../moved.sha")"
       elif [ -f "$STUB/spaces" ] && [ "$n" -ge 2 ]; then
         python3 "$STUB/../prjson.py" get "$STUB/live.json" | python3 -c 'import sys, json; d = json.load(sys.stdin); d["body"] = d["body"] + "  \n"; print(json.dumps(d))'
+      elif [ -f "$STUB/mangle-title" ] && [ "$n" -ge 2 ]; then
+        python3 "$STUB/../prjson.py" get "$STUB/live.json" | python3 -c 'import sys, json; d = json.load(sys.stdin); d["title"] = "retitled by someone else"; print(json.dumps(d))'
       elif [ -f "$STUB/mangle" ] && [ "$n" -ge 2 ]; then
         python3 "$STUB/../prjson.py" get "$STUB/live.json" | python3 -c 'import sys, json; d = json.load(sys.stdin); d["body"] = "edited by someone else\n"; print(json.dumps(d))'
       else
@@ -298,9 +340,9 @@ esac
 STUB
 chmod +x "$W/bin/"*
 
-mkcase() { # name [live-head] -> a stub dir with its own log, TMPDIR and live pull request
+mkcase() { # name [live-head] [merged] -> a stub dir with its own log, TMPDIR and live pull request
   local d="$W/$1"; mkdir -p "$d/tmp"; : > "$d/log"
-  python3 "$W/prjson.py" new "$d/live.json" "${2:-$HEAD}" "$BASE"
+  python3 "$W/prjson.py" new "$d/live.json" "${2:-$HEAD}" "$BASE" ${3:-}
 }
 run() { # name script args... -> rc; out/err captured in the case dir
   local d="$W/$1" sc=$2; shift 2
@@ -312,6 +354,7 @@ calls() { grep -c "^$2" "$W/$1/log"; }
 leftover() { find "$W/$1/tmp" -mindepth 1 | wc -l | tr -d ' '; }
 leaks() { cat "$W/$1/out" "$W/$1/err" | grep -c -e "$TOKEN" -e STUBKEYMATERIAL -e STUBSIGNATURE; }
 livebody() { python3 -c 'import json, sys; sys.stdout.write(json.load(open(sys.argv[1]))["body"])' "$W/$1/live.json"; }
+livetitle() { python3 -c 'import json, sys; sys.stdout.write(json.load(open(sys.argv[1]))["title"])' "$W/$1/live.json"; }
 
 # The healthy run: the arm every refusal below is paired with.
 mkcase ok; printf 'fast (3.14)\nlint\n' > "$W/ok/reds"
@@ -402,6 +445,53 @@ mkcase ghfail; : > "$W/ghfail/gh-fails"
 run ghfail "$BP" --repo o/r 7 "$HEAD" "$W/body.md"; st $? 1 "REFUSE: the live head cannot be read"
 st "$(calls ghfail curl)" 0 "(and nothing minted)"
 
+# --title (R10-FLY-ROW-HEAD-CARRY carry 4): the TITLE alone, on an open or a
+# merged pull request, so a row the record generator derives from it can be
+# corrected without moving a head.
+T2='triage: batch 32, P184-P191 (V104-V111)'
+mkcase tmerged "$HEAD" merged
+run tmerged "$BP" --repo o/r --title 7 "$HEAD" "$T2"; st $? 0 "--title on a MERGED pull request: patched"
+st "$(livetitle tmerged)" "$T2" "the live title is the new title, exactly"
+st "$(livebody tmerged)" "the old body, 111" "and the body is untouched (the PATCH carries the title only)"
+st "$(calls tmerged 'curl PATCH repos/o/r/pulls/7')" 1 "one PATCH"
+st "$(calls tmerged node)$(calls tmerged carry_audit)" 00 "no body contract on a merged pull request: pr-contract never re-runs on one"
+st "$(grep -c '^body_patch: OK: #7 title patched and read back identical; head '"$HEAD"' unmoved$' "$W/tmerged/out")" 1 "the last line is the title OK line"
+# The round trip the carry asks for: the record generator's own row for the
+# patched facts is the corrected row, and the row it made before is refused.
+RT=$(python3 - "$W/tmerged/live.json" "$HERE/record_row.py" <<'PY'
+import json, sys, importlib.util
+fact = json.load(open(sys.argv[1]))
+spec = importlib.util.spec_from_file_location("record_row", sys.argv[2]); rr = importlib.util.module_from_spec(spec)
+spec.loader.exec_module(rr)
+new = rr.row_line(7, fact["title"], fact["merge_commit_sha"], None)
+old = rr.row_line(7, "fix: the title", fact["merge_commit_sha"], None)
+print("%s|%s|%s" % (rr._row_refusal(7, new, 1, fact) == "", rr._row_refusal(7, old, 1, fact) != "", "P184-P191 (V104-V111)." in new))
+PY
+)
+st "$RT" "True|True|True" "round trip: record_row accepts the row regenerated from the patched title, refuses the old one (null control)"
+mkcase topen
+run topen "$BP" --repo o/r --title 7 "$HEAD" "$T2"; st $? 0 "--title on an OPEN pull request: patched"
+st "$(grep -c -- "--title $T2 --author hpo-author" "$W/topen/log")" 1 "an open pull request's live body is judged by the contract with the NEW title"
+st "$(livebody topen)" "the old body, 111" "and its body is untouched"
+mkcase tlint; : > "$W/tlint/lint-fails"
+run tlint "$BP" --repo o/r --title 7 "$HEAD" "$T2"; st $? 1 "REFUSE: the contract refuses the new title on an open pull request"
+st "$(calls tlint curl)" 0 "never sent, never minted"
+mkcase tmangle "$HEAD" merged; : > "$W/tmangle/mangle-title"
+run tmangle "$BP" --repo o/r --title 7 "$HEAD" "$T2"; st $? 1 "REFUSE: the title read back is not the title sent"
+st "$(grep -c '^body_patch: OK' "$W/tmangle/out")" 0 "and no OK line"
+mkcase tmoved "$MOVED" merged
+run tmoved "$BP" --repo o/r --title 7 "$HEAD" "$T2"; st $? 1 "REFUSE: --title at a head other than the expected one"
+st "$(calls tmoved curl)" 0 "(and nothing minted)"
+mkcase tshape "$HEAD" merged
+i=0; for bad in "" " $T2" "$T2 " "$(printf 'two\nlines')"; do
+  i=$((i + 1)); run tshape "$BP" --repo o/r --title 7 "$HEAD" "$bad"; st $? 1 "REFUSE: bad title $i of 4 (empty, leading space, trailing space, two lines)"
+done
+st "$(calls tshape curl)$(calls tshape gh)" 00 "none of those made a call"
+mkcase tdry "$HEAD" merged
+run tdry "$BP" --dry-run --repo o/r --title 7 "$HEAD" "$T2"; st $? 0 "--dry-run --title exits 0"
+st "$(grep -c '^body_patch: DRY-RUN: .* with {"title": "triage: batch 32, P184-P191 (V104-V111)"}; signed, minted and wrote nothing$' "$W/tdry/out")" 1 "and prints the title-only payload"
+st "$(calls tdry curl)$(livetitle tdry)" "0fix: the title" "(null control: nothing minted, the title untouched)"
+
 # Mutants: delete one arm at a time from a copy; its control must stop refusing.
 mutant() { # arm sed-expression -> a copy of the tool with the arm deleted
   mkdir -p "$W/mut-$1/audit/seat" "$W/mut-$1/pr"; cp "$W/tool/pr/app_mint.sh" "$W/mut-$1/pr/"
@@ -419,6 +509,9 @@ mutant eq1    '/# mut:eq1$/s/.*/    return a.strip() == b.strip()/'
 mutant exist  '/# mut:existing$/s/--diff-filter=a //'
 mutant redf   '/# mut:redfilter$/s/select(.*)/select(true)/'
 mutant dot2   '/# mut:threedot$/s/"\$base\.\.\.\$head"/"$base" "$head"/'
+mutant trb    '/# mut:titlereadback$/s/.*/same = True/'
+mutant tshp   '/# mut:titleshape$/s/.*/:/'
+mutant tctr   '/# mut:titlecontract$/s/.*/    :/'
 MBP() { echo "$W/mut-$1/audit/seat/body_patch.sh"; }
 mkcase m1 "$MOVED"; run m1 "$(MBP head)" --repo o/r 7 "$HEAD" "$W/body.md"
 st "$([ "$(calls m1 curl)" -gt 0 ] && echo minted)" minted "MUTANT head check deleted: the moved-head control now MINTS (the pre-write re-read still stops the write), so the control catches it"
@@ -443,6 +536,12 @@ mkcase m10; run m10 "$(MBP dot2)" --repo o/r 7 "$HEAD" "$W/body.md"
 st "$(cat "$W/m10/paths")" "$(printf 'a.txt\nb.txt\nd.txt')" "MUTANT two-dot diff: the paths now hold the base's own d.txt (the ok-run assertion catches it)"
 mkcase m11; printf 'gate\npr-contract / pr-contract\nlint\n' > "$W/m11/reds"; run m11 "$(MBP redf)" --repo o/r 7 "$HEAD" "$W/body.md"
 st "$(grep -c -e "--red gate" "$W/m11/log")" 1 "MUTANT red filter deleted: the body is now asked to answer gate and its own contract (the own-names control catches it)"
+mkcase m12 "$HEAD" merged; : > "$W/m12/mangle-title"; run m12 "$(MBP trb)" --repo o/r --title 7 "$HEAD" "$T2"; rc=$?
+st "$rc$(grep -c '^body_patch: OK' "$W/m12/out")" 01 "MUTANT title read-back deleted: a title someone else changed now reads OK"
+mkcase m13 "$HEAD" merged; run m13 "$(MBP tshp)" --repo o/r --title 7 "$HEAD" "$(printf 'two\nlines')"
+st "$(calls m13 'curl PATCH')" 1 "MUTANT title shape check deleted: a multi-line title is now SENT"
+mkcase m14; : > "$W/m14/lint-fails"; run m14 "$(MBP tctr)" --repo o/r --title 7 "$HEAD" "$T2"
+st "$(calls m14 'curl PATCH')" 1 "MUTANT open-PR title contract deleted: a title the contract refuses is now SENT"
 
 echo "body_patch self-test: $N checks, $FAILS failed"
 [ "$FAILS" -eq 0 ]
diff --git a/tools/audit/seat/instruments/body_patch.sh.md b/tools/audit/seat/instruments/body_patch.sh.md
index 1ce30865d..351933cce 100644
--- a/tools/audit/seat/instruments/body_patch.sh.md
+++ b/tools/audit/seat/instruments/body_patch.sh.md
@@ -14,3 +14,12 @@
   three tries refuses, never reports OK. The offline contract runs the
   caller's checkout, so it can differ from pr-contract's (the script header
   says how). One `--once` unit: its last line is `body_patch: OK|REFUSE ...`.
+- `body_patch.sh --title` — the same steps on the TITLE alone:
+  `body_patch.sh [--dry-run] [--repo O/R] --title <pr> <expected-head-sha>
+  <title>`. PATCHes `{"title"}` and nothing else, and reads the title back
+  exactly, on an open or a closed pull request. When: a title the row
+  generator (`record_row.py`) derives a row from is wrong, so the row is
+  regenerated from the corrected title (R10-FLY-ROW-HEAD-CARRY carry 4).
+  Refusal: an empty, padded or multi-line title, before any read; an open
+  pull request whose live body the contract refuses under the new title;
+  the same head, read-back and retry refusals as the body path.

