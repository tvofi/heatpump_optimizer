# Review packet #3294
head: 131b1358e408954ed0076904bb9a811e5e80fac8
base: 4b5d771bdf8feb1f83d7d9443e5117b771a0ab76

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=128467241362 success
arch-score / arch-score id=128515476918 success
arm id=128466293384 skipped
budget-raise-gate / budget-raise-gate id=128515481890 success
cancel-superseded id=128515480489 success
codeql id=128515454563 skipped
codeql / Analyze (actions) id=128515448632 success
codeql / Analyze (javascript-typescript) id=128515490221 success
codeql / Analyze (python) id=128515448022 success
gate id=128515453754 success
governance id=128515496923 skipped
governance / delivery-status id=128515448155 success
governance / delivery-status-publish id=128515478340 skipped
governance / env-matrix id=128515476794 success
governance / instrument-self-tests id=128515448156 success
governance / policy-docs id=128515489982 success
governance / record id=128515489451 skipped
governance / wave-script id=128515448108 success
hassfest id=128515483417 skipped
hassfest / hassfest id=128515448047 success
kernel-points id=128515486532 skipped
pr-contract id=128515454871 skipped
pr-contract / pr-contract id=128515449967 failure
prelude id=128515485003 success
refresh id=128515454310 success
tests id=128515454531 skipped
tests / arch-instrument id=128515448930 success
tests / briefs id=128515484880 success
tests / browser id=128515449024 success
tests / ci-ratchet id=128515449606 skipped
tests / claims-autofix id=128515449151 skipped
tests / closure-scope id=128515472716 success
tests / closures id=128515449043 success
tests / closures-autofix id=128515449255 skipped
tests / coverage id=128515448807 success
tests / coverage-ratchet id=128515449284 success
tests / fast (3.14) id=128515449090 success
tests / graders-head-copy id=128515449289 success
tests / lane-proofs id=128515449929 success
tests / mutation id=128515448104 success
tests / mutation-autofix id=128515449414 skipped
tests / mutation-pins id=128515449425 skipped
tests / nightly-ha id=128515448662 skipped
tests / nightly-status id=128515447702 failure
tests / replay id=128515449300 skipped
tests / typing id=128515449097 success
validate id=128515454418 skipped
validate / validate-hacs id=128515480790 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 6a07172e: R10-FLY-STANDING-CONTRACTS
NOTE body item 8d488756: R10-FLY-STANDING-CONTRACTS
NOTE body item 88565884: R10-FLY-STANDING-CONTRACTS
NOTE body item 28185cf3: R10-FLY-STANDING-CONTRACTS
NOTE body item 8a9d989c: R10-FLY-STANDING-CONTRACTS
CARRY-AUDIT: 5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/audit/seat/hooks_setup.py --self-test
             `tools/audit/seat/hooks_setup.py` is in the tree at this head
  ok         bash .claude/hooks/pre-bash.sh --self-test
             `.claude/hooks/pre-bash.sh` is in the tree at this head
  ok         python3 -I tools/audit/seat/offline_spy.py tools/audit/seat/hooks_setup.py
             `tools/audit/seat/offline_spy.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/selftest_wiring.py --check
             `tools/audit/seat/selftest_wiring.py` is in the tree at this head
  ok         python3 tests/closure.py select
             `tests/closure.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/tmp_paths.py --check
             `tools/audit/seat/tmp_paths.py` is in the tree at this head
  ok         tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  ok         gh api repos/tvofi/heatpump_optimizer/pulls/<n>/files
             gh api: every long flag accepted

FIGURES: 8 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.claude/hooks/pre-bash.sh b/.claude/hooks/pre-bash.sh
index 1ef88954f..89d0b20d0 100755
--- a/.claude/hooks/pre-bash.sh
+++ b/.claude/hooks/pre-bash.sh
@@ -160,17 +160,86 @@ SELF_TEST=0
 #         sys.exit(1)
 # HPO_PRE_BASH_PY_END
 
-decide() { # $1 the raw payload; stdout: a refusal message, or nothing
-  # Prefilter: no `kill` anywhere in the payload means nothing here can match,
-  # and a bash `case` costs about 3 ms where a python start costs about 26.
-  case "$1" in *kill*) ;; *) return 0 ;; esac
-  sed -n '/^# HPO_PRE_BASH_PY$/,/^# HPO_PRE_BASH_PY_END$/{
-    /^# HPO_PRE_BASH_PY$/d
-    /^# HPO_PRE_BASH_PY_END$/d
+# HPO_PRE_BASH_GUARD_PY
+# import json, os, re, shlex, subprocess, sys
+# # Second arm: the orchestrator's checkout is what beatd, tick_loop.sh and
+# # cloud_relay.sh run their scripts from, and bash reads a script
+# # incrementally, so a command that moves its HEAD or working tree corrupts
+# # them (2026-10-31, gap 4 of R10-FLY-STANDING-CONTRACTS). INERT unless
+# # $HPO_STATE_DIR/orch-checkout names a directory; fails open on anything odd.
+# MOVERS = {"checkout", "switch", "reset", "pull", "merge", "rebase", "stash", "clean", "restore"}
+# try:
+#     state = os.environ.get("HPO_STATE_DIR", "")
+#     marker = open(os.path.join(state, "orch-checkout")).read().strip() if state else ""
+#     if not marker or not os.path.isdir(marker):
+#         sys.exit(0)
+#     payload = json.loads(sys.argv[1])
+#     cmd = payload["tool_input"]["command"]
+#     cwd = payload.get("cwd") or os.getcwd()
+#     guarded = os.path.realpath(marker)
+#     if not isinstance(cmd, str):
+#         sys.exit(0)
+#     def toplevel(d):
+#         r = subprocess.run(["git", "-C", d, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
+#         return os.path.realpath(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else ""
+#     cur = cwd
+#     for stmt in re.split(r"\n|;|&&|\|\||\||&", cmd):
+#         try:
+#             w = shlex.split(stmt, comments=True)
+#         except ValueError:
+#             continue
+#         while w and (re.fullmatch(r"\w+=.*", w[0]) or w[0] in ("sudo", "env", "command", "time", "nohup", "exec")):
+#             w = w[1:]
+#         if not w:
+#             continue
+#         if w[0] == "cd" and len(w) > 1:
+#             cur = os.path.realpath(os.path.join(cur, os.path.expanduser(w[1])))
+#             continue
+#         if w[0] != "git":
+#             continue
+#         d, i = cur, 1
+#         while i < len(w) and w[i].startswith("-"):
+#             if w[i] == "-C" and i + 1 < len(w):
+#                 d = os.path.realpath(os.path.join(d, os.path.expanduser(w[i + 1]))); i += 2
+#             elif w[i] in ("-c", "--git-dir", "--work-tree", "--namespace") and i + 1 < len(w):
+#                 i += 2
+#             else:
+#                 i += 1
+#         sub = w[i] if i < len(w) else ""
+#         if sub in MOVERS and os.path.isdir(d) and toplevel(d) == guarded:
+#             print(f"`git {sub}` would move HEAD or the working tree of the orchestrator checkout "
+#                   "($HPO_STATE_DIR/orch-checkout), which beatd, tick_loop.sh and cloud_relay.sh run their "
+#                   "scripts from; bash reads a script incrementally, so the move corrupts them. Read main with "
+#                   "`git -C <checkout> show origin/main:<path>` or work in a worktree of your own.")
+#             sys.exit(1)
+# except SystemExit:
+#     raise
+# except Exception:
+#     sys.exit(0)                          # anything unforeseen -- fail open
+# HPO_PRE_BASH_GUARD_PY_END
+
+extract() { # $1 the marker name; stdout: that block as a python program
+  sed -n "/^# $1\$/,/^# $1_END\$/{
+    /^# $1\$/d
+    /^# $1_END\$/d
     s/^# //
-    s/^#$//
+    s/^#\$//
     p
-  }' "$0" | python3 - "$1"
+  }" "$0"
+}
+
+decide() { # $1 the raw payload; stdout: a refusal message, or nothing
+  # Prefilter: no `kill` anywhere in the payload means the first arm cannot
+  # match, and a bash `case` costs about 3 ms where a python start costs about
+  # 26. The second arm needs `git` in the payload AND a marker file.
+  case "$1" in
+    *kill*) extract HPO_PRE_BASH_PY | python3 - "$1" ;;
+  esac
+  case "$1" in
+    *git*) [ -n "${HPO_STATE_DIR:-}" ] && [ -f "$HPO_STATE_DIR/orch-checkout" ] \
+             && extract HPO_PRE_BASH_GUARD_PY | python3 - "$1" ;;
+  esac
+  return 0
 }
 
 if [ "$SELF_TEST" = 1 ]; then
@@ -208,6 +277,31 @@ pkill -f x
 EOF'                                               "a heredoc body holding pkill is allowed (null control)"
   st allow  'echo hi # pkill x'                    "pkill in a comment is allowed (null control)"
   st allow  'git status'                           "a command without the substring kill takes the prefilter path"
+  # SECOND ARM: the orchestrator-checkout guard, over a throwaway repository
+  # and state directory (HPO_STATE_DIR/orch-checkout names the repository).
+  gtmp=$(mktemp -d); mkdir -p "$gtmp/state" "$gtmp/orch" "$gtmp/other"
+  . "$(dirname "$0")/../../tests/throwaway_git.sh"
+  throwaway_git_init "$gtmp/orch" -q; throwaway_git_init "$gtmp/other" -q
+  printf '%s\n' "$gtmp/orch" > "$gtmp/state/orch-checkout"
+  gst() { # want(refuse|allow), command, cwd, label, [state dir]
+    local payload out got
+    payload=$(python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","cwd":sys.argv[2],"tool_input":{"command":sys.argv[1]}}))' "$2" "$3")
+    out=$(HPO_STATE_DIR="${5-$gtmp/state}" decide "$payload")
+    got=allow; [ -n "$out" ] && got=refuse
+    if [ "$got" = "$1" ]; then pass=$((pass+1)); printf '  ok   %s\n' "$4"
+    else fail=$((fail+1)); printf '  FAIL %s (got %s, wanted %s)\n' "$4" "$got" "$1"; fi
+  }
+  gst refuse 'git pull'                         "$gtmp/orch"  "guard: git pull in the orchestrator checkout is refused"
+  gst refuse "git -C $gtmp/orch checkout main"  "$gtmp/other" "guard: git -C into the checkout is refused"
+  gst refuse "cd $gtmp/orch && git reset --hard" "$gtmp/other" "guard: cd then reset is refused"
+  gst refuse 'git -c x=y merge origin/main'     "$gtmp/orch"  "guard: git -c before the subcommand is read past"
+  gst allow  'git status'                       "$gtmp/orch"  "guard: a read-only git command is allowed (null control)"
+  gst allow  "git -C $gtmp/orch show origin/main:README.md" "$gtmp/other" "guard: show of main is allowed (null control)"
+  gst allow  'git pull'                         "$gtmp/other" "guard: pull in another repository is allowed (null control)"
+  gst allow  'git pull'                         "$gtmp/orch"  "guard: inert without HPO_STATE_DIR (null control)" ""
+  rm -f "$gtmp/state/orch-checkout"
+  gst allow  'git pull'                         "$gtmp/orch"  "guard: inert without the marker file (null control)"
+  rm -rf "$gtmp"
   # AND THE SCRIPT ITSELF, end to end over its real stdin: every case above
   # drives `decide`, none of them the wrapper that reads the payload and turns a
   # message into an exit status -- where pre-edit.sh was inert once.
diff --git a/.github/workflows/governance.yml b/.github/workflows/governance.yml
index 759ec575e..3a22e649c 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -970,6 +970,13 @@ jobs:
           grep -Eq '^delivery_row self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/update-pr-self-test.txt"
           grep -Eq '^pr_args self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/update-pr-self-test.txt"
 
+      - name: Show the hook installer refusing its own fixtures
+        if: ${{ !cancelled() }}
+        run: |
+          set -o pipefail
+          python3 -I tools/audit/seat/hooks_setup.py --self-test | tee "$RUNNER_TEMP/hooks-setup-self-test.txt"
+          grep -Eq '^hooks_setup self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/hooks-setup-self-test.txt"
+
       - name: Show the offline spy refusing its own fixtures
         if: ${{ !cancelled() }}
         run: |
diff --git a/dev/programme/delivery/3294.md b/dev/programme/delivery/3294.md
new file mode 100644
index 000000000..29c75324b
--- /dev/null
+++ b/dev/programme/delivery/3294.md
@@ -0,0 +1 @@
+- [#3294](https://github.com/tvofi/heatpump_optimizer/pull/3294) — **open**, R10-FLY-STANDING-CONTRACTS: standing contracts, part 2 (R10-FLY-STANDING-CONTRACTS)
diff --git a/tests/closures.json b/tests/closures.json
index e0693316d..fcc289561 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3870,6 +3870,7 @@
    "tools/audit/seat/features_block.py",
    "tools/audit/seat/flow_metrics.py",
    "tools/audit/seat/gh_calls.py",
+   "tools/audit/seat/hooks_setup.py",
    "tools/audit/seat/ledger.py",
    "tools/audit/seat/merge_train.py",
    "tools/audit/seat/moved_paths.py",
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index 57fcb0697..2c89b57c6 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -123,3 +123,4 @@ sweep's standing-seat liveness step keep them alive.
 - [`shims/seat-python`, `shims/seat-python3`](instruments/shims_seat-python.md) — the seat interpreter
 - [`shims/seat-gh`](instruments/shims_seat-gh.md) — the seat's `gh`: one log line per call (caller, subcommand, api path, no values), then the real gh
 - [`gh_calls.py`](instruments/gh_calls.py.md) — reads that log: `--top` ranks callers and endpoints, `--coverage` names the processes whose PATH misses the shim
+- [`hooks_setup.py`](instruments/hooks_setup.py.md) — reports and installs the user-level hooks (liveness, seat interpreter, git identity) and reports the project-level checkout guard, from `tools/audit/seat/hooks/`
diff --git a/tools/audit/seat/hooks/git_identity.py b/tools/audit/seat/hooks/git_identity.py
new file mode 100644
index 000000000..95a5f30a2
--- /dev/null
+++ b/tools/audit/seat/hooks/git_identity.py
@@ -0,0 +1,55 @@
+#!/usr/bin/env python3
+"""SessionStart hook: pin the orchestrator checkout's git identity from a state file.
+
+    python3 -I tools/audit/seat/hooks/git_identity.py [--state DIR]
+
+WHY. A commit made from the orchestrator's checkout under the host's default
+identity is refused by the identity contract (decision 0011) only after it is
+pushed. $HPO_STATE_DIR/git-identity holds two lines, the name then the email;
+this hook sets them as the checkout's LOCAL config when they differ, and prints
+one `GIT-IDENTITY set` line saying so. Silent when they already match, and
+INERT without orch-checkout or without the identity file: it never invents an
+identity. It touches local config only, never the working tree or HEAD.
+"""
+from __future__ import annotations
+
+import os
+import subprocess
+import sys
+from pathlib import Path
+
+
+def _git(repo: str, *a: str) -> subprocess.CompletedProcess:
+    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True)
+
+
+def report(state: Path) -> list[str]:
+    try:
+        repo = (state / "orch-checkout").read_text().strip()
+        ident = (state / "git-identity").read_text().splitlines()
+    except OSError:
+        return []
+    if not repo or len(ident) < 2 or not ident[0].strip() or not ident[1].strip():
+        return []
+    out = []
+    for key, want in (("user.name", ident[0].strip()), ("user.email", ident[1].strip())):
+        have = _git(repo, "config", "--local", "--get", key)
+        if have.returncode == 0 and have.stdout.strip() == want:
+            continue
+        r = _git(repo, "config", "--local", key, want)
+        out.append(f"GIT-IDENTITY set {key}" if r.returncode == 0 else f"UNREADABLE git-identity {key}")
+    return out
+
+
+def main(argv: list[str]) -> int:
+    state = os.environ.get("HPO_STATE_DIR", "")
+    if argv[:1] == ["--state"] and len(argv) > 1:
+        state = argv[1]
+    if state:
+        for ln in report(Path(state)):
+            print(ln)
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/tools/audit/seat/hooks/liveness.py b/tools/audit/seat/hooks/liveness.py
new file mode 100644
index 000000000..a9f6b0ce7
--- /dev/null
+++ b/tools/audit/seat/hooks/liveness.py
@@ -0,0 +1,136 @@
+#!/usr/bin/env python3
+"""SessionStart and PostCompact hook: say what the orchestrator must restart or re-read.
+
+    python3 -I tools/audit/seat/hooks/liveness.py [--state DIR]      (payload JSON on stdin)
+
+WHY. After a compaction or a resume nobody re-armed the wake loop, and owed lines
+stood unread for hours while every instrument had flagged them (2026-11-01).
+This hook runs at both events and prints, on stdout (which the session reads):
+  POLICY-REREAD  the session owes a fresh read of the policy corpus from
+                 origin/main (policy_reread_check.py says OWED, or the event is
+                 PostCompact, which has just replaced the corpus with a summary);
+  DEAD / ALARM   one line per beat job that is late, per beatd alarm, and for
+                 beatd itself when its lock is free -- beatd.py status over the
+                 job table, so a new row is checked the day it lands;
+  STALE          an alive file under $HPO_STATE_DIR/alive/ older than
+                 HPO_ALIVE_STALE_MIN (default 120) minutes, and the digest when
+                 neither digest/digest.txt nor beatd/journal.log moved within
+                 HPO_DIGEST_STALE_MIN (default 30): digest.txt is rewritten only on
+                 a change, so a quiet board is judged by the beat's own journal;
+  the digest     digest/digest.txt, verbatim;
+  ARM            the one instruction line: restart what is reported dead, check the
+                 standing seats, re-arm the wake loop (exit on a new
+                 digest/new.stamp or digest/events.txt line) this turn.
+INERT unless $HPO_STATE_DIR/orch-checkout names a directory: on any other host
+it prints nothing and exits 0, so it can sit in a user's settings everywhere.
+It never fails the session: an unreadable input prints UNREADABLE for that part.
+"""
+from __future__ import annotations
+
+import json
+import os
+import subprocess
+import sys
+import time
+from pathlib import Path
+
+SEAT = Path(__file__).resolve().parents[1]
+
+
+def _age_min(p: Path, now: float) -> float | None:
+    try:
+        return (now - p.stat().st_mtime) / 60
+    except OSError:
+        return None
+
+
+def _env_min(name: str, default: float) -> float:
+    try:
+        return float(os.environ.get(name, default))
+    except ValueError:
+        return default
+
+
+def report(state: Path, event: str, transcript: str, now: float) -> list[str]:
+    marker = state / "orch-checkout"
+    try:
+        repo = marker.read_text().strip()
+    except OSError:
+        return []
+    if not repo or not Path(repo).is_dir():
+        return []
+    out: list[str] = []
+    py = sys.executable
+    stamp = state / "policy-reread.stamp"
+    if event == "PostCompact":
+        out.append("POLICY-REREAD owed: this session was compacted; re-read CLAUDE.md, the rules and the role "
+                   f"contracts from fresh origin/main, then python3 -I tools/audit/seat/policy_reread_check.py --stamp {stamp} --write-stamp")
+    else:
+        cmd = [py, "-I", str(SEAT / "policy_reread_check.py"), "--stamp", str(stamp),
+               "--transcript", transcript or os.devnull + ".none"]  # no transcript: unreadable, so OWED
+        r = subprocess.run(cmd, capture_output=True, text=True)
+        if r.returncode == 2:
+            out.append(f"UNREADABLE policy_reread_check: {(r.stderr or r.stdout).strip()[-80:]}")
+        elif r.returncode != 0 or not r.stdout.strip().startswith("OK"):
+            out.append("POLICY-REREAD owed: re-read CLAUDE.md, the rules and the role contracts from fresh origin/main, "
+                       f"then policy_reread_check.py --stamp {stamp} --write-stamp")
+    b = subprocess.run([py, "-I", str(SEAT / "beatd.py"), "status", "--state", str(state), "--repo", repo],
+                       capture_output=True, text=True)
+    if b.returncode == 2 or not b.stdout.strip():
+        out.append(f"UNREADABLE beatd status: {(b.stderr or b.stdout).strip()[-80:]}")
+    for ln in b.stdout.splitlines():
+        f = ln.split()
+        if ln.startswith("JOB ") and len(f) > 2:
+            if f[2] == "late":
+                out.append(f"DEAD loop {f[1]} {' '.join(f[3:])}")
+            elif f[2] not in ("ok", "running", "idle"):
+                out.append(f"ALARM job {f[1]} {f[2]}")
+        elif ln.startswith(("DOWN ", "ALERT ", "STALE-CODE", "UNREADABLE")):
+            out.append(("DEAD beatd " + ln[5:]) if ln.startswith("DOWN ") else f"ALARM {ln}")
+    alive_stale = _env_min("HPO_ALIVE_STALE_MIN", 120)
+    ad = state / "alive"
+    for p in sorted(ad.iterdir()) if ad.is_dir() else []:
+        if p.is_file():
+            age = _age_min(p, now)
+            if age is None or age > alive_stale:
+                out.append(f"STALE alive {p.name} age_min={'?' if age is None else int(age)}")
+    dig = state / "digest" / "digest.txt"
+    ages = [a for a in (_age_min(dig, now), _age_min(state / "beatd" / "journal.log", now)) if a is not None]
+    if not ages or min(ages) > _env_min("HPO_DIGEST_STALE_MIN", 30):
+        out.append("STALE digest: neither digest.txt nor the beat journal moved in time")
+    try:
+        text = dig.read_text()
+    except OSError:
+        text = ""
+    out += [ln for ln in text.splitlines() if ln.strip()]
+    out.append("ARM: restart any loop reported dead above, check the standing seats, and re-arm the wake loop this turn "
+               "(it exits on a new digest/new.stamp or digest/events.txt line)")
+    return out
+
+
+def main(argv: list[str]) -> int:
+    state = os.environ.get("HPO_STATE_DIR", "")
+    if argv[:1] == ["--state"] and len(argv) > 1:
+        state = argv[1]
+    if not state:
+        return 0
+    event, transcript = "", ""
+    try:
+        if not sys.stdin.isatty():
+            p = json.loads(sys.stdin.read() or "{}")
+            if isinstance(p, dict):
+                event = str(p.get("hook_event_name") or "")
+                transcript = str(p.get("transcript_path") or "")
+    except (ValueError, OSError):
+        pass
+    try:
+        lines = report(Path(state), event, transcript, time.time())
+    except Exception as e:  # a hook never fails the session
+        lines = [f"UNREADABLE liveness hook: {type(e).__name__}"]
+    if lines:
+        print("\n".join(lines))
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/tools/audit/seat/hooks/seat_interpreter.py b/tools/audit/seat/hooks/seat_interpreter.py
new file mode 100644
index 000000000..dffa49da9
--- /dev/null
+++ b/tools/audit/seat/hooks/seat_interpreter.py
@@ -0,0 +1,45 @@
+#!/usr/bin/env python3
+"""SessionStart hook: say when the seat interpreter is not the one seat_venv.sh builds.
+
+    python3 -I tools/audit/seat/hooks/seat_interpreter.py [--state DIR]
+
+WHY. A temp cleanup once deleted the seat venv and every seat ran the system
+python3 without anyone noticing (2026-10-03, seat_venv.sh). This hook runs
+`seat_venv.sh --check` -- the recipe's own report of what the venv must hold --
+and prints one `SEAT-INTERPRETER` line, with the rebuild command, when it
+refuses. Silent when it passes. INERT unless $HPO_STATE_DIR/orch-checkout
+exists, as liveness.py is, so it binds only a seat host.
+"""
+from __future__ import annotations
+
+import os
+import subprocess
+import sys
+from pathlib import Path
+
+SEAT = Path(__file__).resolve().parents[1]
+
+
+def report(state: Path) -> list[str]:
+    if not (state / "orch-checkout").is_file():
+        return []
+    r = subprocess.run(["bash", str(SEAT / "seat_venv.sh"), "--check"],
+                       capture_output=True, text=True, env=dict(os.environ, HPO_STATE_DIR=str(state)))
+    if r.returncode == 0:
+        return []
+    why = (r.stderr or r.stdout).strip().splitlines()[-1:] or ["no output"]
+    return [f"SEAT-INTERPRETER refused: {why[0][:160]}; rebuild with tools/audit/seat/seat_venv.sh"]
+
+
+def main(argv: list[str]) -> int:
+    state = os.environ.get("HPO_STATE_DIR", "")
+    if argv[:1] == ["--state"] and len(argv) > 1:
+        state = argv[1]
+    if state:
+        for ln in report(Path(state)):
+            print(ln)
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/tools/audit/seat/hooks_setup.py b/tools/audit/seat/hooks_setup.py
new file mode 100644
index 000000000..1cae049c5
--- /dev/null
+++ b/tools/audit/seat/hooks_setup.py
@@ -0,0 +1,330 @@
+#!/usr/bin/env python3
+"""Report and install the user-level Claude Code hooks the orchestrator's host depends on.
+
+    python3 -I tools/audit/seat/hooks_setup.py --check   [--settings FILE]
+    python3 -I tools/audit/seat/hooks_setup.py --install [--settings FILE]
+    python3 -I tools/audit/seat/hooks_setup.py --self-test
+
+WHY THIS EXISTS. The orchestrator's sessions leaned on four hooks that lived
+only in one user's settings, with no description and no way to rebuild them on
+a new host (R10-FLY-STANDING-CONTRACTS, carry 19 part 2). The scripts are
+tracked under tools/audit/seat/hooks/ and described in
+instruments/hooks_setup.py.md; this is the one installer, and a later group's
+user-level hook adds a row to HOOKS here rather than shipping its own.
+
+USER LEVEL, per hook (project-level hooks bind every session through
+.claude/settings.json and need no installer):
+  liveness          SessionStart, PostCompact   hooks/liveness.py
+  seat-interpreter  SessionStart                hooks/seat_interpreter.py
+  git-identity      SessionStart                hooks/git_identity.py
+PROJECT LEVEL, reported by --check and never installed: the Bash PreToolUse
+guard of the orchestrator's checkout, the second arm of .claude/hooks/pre-bash.sh.
+
+--check changes nothing and prints one line per hook and event: `ok`,
+`missing` or `differs` (an entry for the script whose command is not the
+one this tree would write). Exit 0 when none is missing or differing, else 1.
+--install adds a missing entry and corrects a differing command in place, prints
+each change, and backs the settings file up first (settings.json.bak-<ns>), only
+when it changes something; a second run changes nothing and writes no byte. It
+never touches an entry of another script, and keeps every unrelated key.
+Settings default to $HOME/.claude/settings.json.
+"""
+from __future__ import annotations
+
+import json
+import os
+import shutil
+import subprocess
+import sys
+import tempfile
+import time
+from pathlib import Path
+
+SEAT = Path(__file__).resolve().parent
+ROOT = SEAT.parents[2]
+HOOKS = [  # (id, script, events)
+    ("liveness", "liveness.py", ("SessionStart", "PostCompact")),
+    ("seat-interpreter", "seat_interpreter.py", ("SessionStart",)),
+    ("git-identity", "git_identity.py", ("SessionStart",)),
+]
+PROJECT_GUARD = ("pre-bash guard", ".claude/hooks/pre-bash.sh", "HPO_PRE_BASH_GUARD_PY")
+
+
+def expected(script: str, root: Path = ROOT) -> str:
+    return f'python3 -I "{root}/tools/audit/seat/hooks/{script}"'
+
+
+def find(settings: dict, event: str, script: str) -> list[dict]:
+    """Every command entry under `event` whose command names this script."""
+    out = []
+    groups = (settings.get("hooks") or {}).get(event) or []
+    for g in groups if isinstance(groups, list) else []:
+        for h in (g.get("hooks") or []) if isinstance(g, dict) else []:
+            if isinstance(h, dict) and f"hooks/{script}" in str(h.get("command", "")):
+                out.append(h)
+    return out
+
+
+def state_of(settings: dict, event: str, script: str, root: Path = ROOT) -> str:
+    hs = find(settings, event, script)
+    if not hs:
+        return "missing"
+    return "ok" if all(h.get("command") == expected(script, root) for h in hs) else "differs"
+
+
+def check(settings: dict, root: Path = ROOT) -> tuple[int, list[str]]:
+    out, bad = [], 0
+    for hid, script, events in HOOKS:
+        for ev in events:
+            st = state_of(settings, ev, script, root)
+            bad += st != "ok"
+            out.append(f"{st} {hid} {ev}")
+    name, rel, marker = PROJECT_GUARD
+    try:
+        proj = json.loads((root / ".claude/settings.json").read_text())
+        wired = any("pre-bash.sh" in h.get("command", "")
+                    for g in proj["hooks"]["PreToolUse"] if g.get("matcher") == "Bash" for h in g["hooks"])
+        armed = marker in (root / rel).read_text()
+    except (OSError, ValueError, KeyError, TypeError):
+        wired = armed = False
+    st = "ok" if wired and armed else "missing"
+    bad += st != "ok"
+    out.append(f"{st} {name} PreToolUse project-level (tree: .claude/settings.json, installs nothing)")
+    return (1 if bad else 0), out
+
+
+def install(settings: dict, root: Path = ROOT) -> list[str]:
+    """Mutate `settings` in place; return one line per change."""
+    changes = []
+    hooks = settings.setdefault("hooks", {})
+    for hid, script, events in HOOKS:
+        for ev in events:
+            st = state_of(settings, ev, script, root)
+            if st == "ok":
+                continue
+            if st == "differs":
+                for h in find(settings, ev, script):
+                    h["command"] = expected(script, root)
+            else:
+                hooks.setdefault(ev, []).append(
+                    {"hooks": [{"type": "command", "command": expected(script, root)}]})
+            changes.append(f"{'corrected' if st == 'differs' else 'added'} {hid} {ev}")
+    return changes
+
+
+def load(path: Path) -> dict:
+    if not path.exists():
+        return {}
+    data = json.loads(path.read_text())
+    if not isinstance(data, dict):
+        raise ValueError(f"{path} is not a JSON object")
+    return data
+
+
+def cmd_install(path: Path, root: Path = ROOT) -> int:
+    settings = load(path)
+    changes = install(settings, root)
+    if not changes:
+        print("hooks_setup: nothing to change")
+        return 0
+    if path.exists():
+        bak = path.with_name(f"{path.name}.bak-{time.time_ns()}")
+        shutil.copy2(path, bak)
+        print(f"hooks_setup: backed up to {bak.name}")
+    path.parent.mkdir(parents=True, exist_ok=True)
+    path.write_text(json.dumps(settings, indent=2) + "\n")
+    for c in changes:
+        print(f"hooks_setup: {c}")
+    return 0
+
+
+# ---------------------------------------------------------------- self-test
+
+def _fixture_state(base: Path, *, dead: bool = False, stale: bool = False):
+    """A healthy beat state under `base` (lock held by the caller), or one planted fault."""
+    import fcntl
+    s = base / "state"
+    (s / "beatd").mkdir(parents=True)
+    (s / "digest").mkdir()
+    (s / "alive").mkdir()
+    repo = base / "orch"
+    sys.path.insert(0, str(ROOT / "tests"))
+    from throwaway_git import throwaway_git_init
+    throwaway_git_init(repo, "-q")
+    (s / "orch-checkout").write_text(f"{repo}\n")
+    now = time.time()
+    stamp = lambda t: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))  # noqa: E731
+    rows = json.loads((SEAT / "beatd.jobs.json").read_text())["jobs"]
+    lines = [f"START {stamp(now - 100000)} beatd pid=1 code=unknown supervisor=none"]
+    for j in rows:
+        if j["kind"] == "watch" or (dead and j["name"] == "pulse"):
+            continue
+        lines.append(f"PASS {stamp(now - 30)} {j['name']} start={stamp(now - 31)} dur=1 rc=0 outcome=ok")
+    (s / "beatd" / "journal.log").write_text("\n".join(lines) + "\n")
+    (s / "digest" / "digest.txt").write_text("OWED reviewer-fire 1\n")
+    (s / "alive" / "merge").write_text("")
+    (base / "transcript.jsonl").write_text("")
+    subprocess.run([sys.executable, "-I", str(SEAT / "policy_reread_check.py"), "--stamp",
+                    str(s / "policy-reread.stamp"), "--write-stamp"], check=True, capture_output=True)
+    if stale:
+        old = now - 86400
+        for p in (s / "digest" / "digest.txt", s / "beatd" / "journal.log", s / "alive" / "merge"):
+            os.utime(p, (old, old))
+    fd = os.open(s / "beatd" / "beatd.lock", os.O_RDWR | os.O_CREAT, 0o600)
+    fcntl.flock(fd, fcntl.LOCK_EX)
+    os.write(fd, b"1\n")
+    return s, fd
+
+
+def _run_hook(script: str, state: Path, payload: dict | None = None) -> str:
+    tr = state.parent / "transcript.jsonl"
+    payload = dict({"hook_event_name": "SessionStart", "transcript_path": str(tr)}, **(payload or {}))
+    r = subprocess.run([sys.executable, "-I", str(SEAT / "hooks" / script), "--state", str(state)],
+                       input=json.dumps(payload),
+                       capture_output=True, text=True)
+    return r.stdout
+
+
+def cases() -> dict[str, bool]:
+    res: dict[str, bool] = {}
+    tmp = Path(tempfile.mkdtemp(prefix="hooks-setup-"))
+    try:
+        home = tmp / "home"
+        sf = home / ".claude" / "settings.json"
+        # --check on a fresh HOME lists every user-level hook as missing
+        rc, out = check({})
+        res["fresh settings: every user-level hook is missing"] = (
+            rc == 1 and sum(ln.startswith("missing") and "project-level" not in ln for ln in out)
+            == sum(len(e) for _, _, e in HOOKS))
+        res["the project-level guard is reported present in the tree"] = any(
+            ln.startswith("ok pre-bash guard") for ln in out)
+        # --install, then --check lists none; a second --install writes no byte
+        unrelated = {"permissions": {"allow": ["Read"]}, "hooks": {"Stop": [{"hooks": [
+            {"type": "command", "command": "echo mine"}]}], "SessionStart": [{"hooks": [
+                {"type": "command", "command": "echo other"}]}]}}
+        sf.parent.mkdir(parents=True)
+        sf.write_text(json.dumps(unrelated, indent=2) + "\n")
+        cmd_install(sf)
+        got = load(sf)
+        res["install then check lists none missing"] = check(got)[0] == 0
+        res["install keeps unrelated entries"] = (
+            got["permissions"] == unrelated["permissions"] and got["hooks"]["Stop"] == unrelated["hooks"]["Stop"]
+            and got["hooks"]["SessionStart"][0] == unrelated["hooks"]["SessionStart"][0])
+        baks = list(sf.parent.glob("settings.json.bak-*"))
+        res["install backs the file up first, holding the old bytes"] = (
+            len(baks) == 1 and json.loads(baks[0].read_text()) == unrelated)
+        before = sf.read_bytes()
+        cmd_install(sf)
+        res["a second install changes nothing (byte-identical, no new backup)"] = (
+            sf.read_bytes() == before and len(list(sf.parent.glob("settings.json.bak-*"))) == 1)
+        # a differing command is corrected in place, nothing else is
+        got["hooks"]["SessionStart"][1]["hooks"][0]["command"] = "python3 old.py hooks/liveness.py"
+        sf.write_text(json.dumps(got))
+        res["a differing command is reported differs"] = "differs liveness SessionStart" in check(load(sf))[1]
+        cmd_install(sf)
+        res["install corrects the differing command only"] = (
+            check(load(sf))[0] == 0 and load(sf)["hooks"]["Stop"] == unrelated["hooks"]["Stop"])
+        # the hooks themselves
+        s, fd = _fixture_state(tmp / "healthy")
+        out = _run_hook("liveness.py", s)
+        res["liveness: a healthy table prints nothing actionable"] = (
+            not any(w in out for w in ("DEAD", "STALE", "ALARM", "UNREADABLE")) and "ARM:" in out
+            and "OWED reviewer-fire 1" in out)
+        res["liveness: PostCompact demands the policy re-read"] = (
+            "POLICY-REREAD" in _run_hook("liveness.py", s, {"hook_event_name": "PostCompact"}))
+        os.close(fd)
+        s, fd = _fixture_state(tmp / "dead", dead=True)
+        res["liveness: a planted dead loop prints DEAD"] = "DEAD loop pulse" in _run_hook("liveness.py", s)
+        os.close(fd)
+        s, fd = _fixture_state(tmp / "stale", stale=True)
+        out = _run_hook("liveness.py", s)
+        res["liveness: a planted stale digest and alive file print STALE"] = (
+            "STALE digest" in out and "STALE alive merge" in out)
+        os.close(fd)
+        quiet = tmp / "quiet"
+        quiet.mkdir()
+        res["liveness, seat-interpreter and git-identity are inert without orch-checkout"] = all(
+            _run_hook(h, quiet) == "" for h in ("liveness.py", "seat_interpreter.py", "git_identity.py"))
+        s, fd = _fixture_state(tmp / "ident")
+        os.close(fd)
+        (s / "git-identity").write_text("Seat Name\nseat@example.invalid\n")
+        first = _run_hook("git_identity.py", s)
+        repo = (s / "orch-checkout").read_text().strip()
+        have = subprocess.run(["git", "-C", repo, "config", "--local", "user.email"],
+                              capture_output=True, text=True).stdout.strip()
+        res["git-identity: sets a differing identity, then prints nothing"] = (
+            "GIT-IDENTITY set user.email" in first and have == "seat@example.invalid"
+            and _run_hook("git_identity.py", s) == "")
+    finally:
+        shutil.rmtree(tmp, ignore_errors=True)
+    return res
+
+
+MUTANTS = [  # (label, old text, new text): each must turn at least one case red
+    ("install skips the backup", "        shutil.copy2(path, bak)\n", "        pass\n"),
+    ("install rewrites an unrelated entry",
+     "    hooks = settings.setdefault(\"hooks\", {})\n",
+     "    hooks = settings.setdefault(\"hooks\", {})\n    hooks[\"Stop\"] = []\n"),
+    ("install is not idempotent", "            if st == \"ok\":\n                continue\n", ""),
+    ("liveness reads no dead loop", "            if f[2] == \"late\":", "            if False:"),
+    ("liveness reads no stale digest", "if not ages or min(ages) > _env_min(", "if False and min(ages) > _env_min("),
+]
+
+
+def self_test(run_mutants: bool = True) -> int:
+    res = cases()
+    fails = [k for k, v in res.items() if not v]
+    n = len(res)
+    for k in fails:
+        print(f"  FAIL {k}")
+    if run_mutants and not fails and not os.environ.get("HPO_HOOKS_MUTANT"):
+        for label, old, new in MUTANTS:
+            tgt = Path(tempfile.mkdtemp(prefix="hooks-mutant-"))
+            try:
+                shutil.copytree(SEAT, tgt / "tools/audit/seat", ignore=shutil.ignore_patterns("__pycache__", "fixtures"))
+                (tgt / "tests").mkdir()
+                shutil.copy2(ROOT / "tests" / "throwaway_git.py", tgt / "tests" / "throwaway_git.py")
+                for f in ("hooks_setup.py", "hooks/liveness.py"):
+                    p = tgt / "tools/audit/seat" / f
+                    text = p.read_text()
+                    if old in text:
+                        p.write_text(text.replace(old, new, 1))
+                        break
+                else:
+                    print(f"  FAIL mutant '{label}': its target text is gone")
+                    fails.append(label)
+                    continue
+                r = subprocess.run([sys.executable, "-I", str(tgt / "tools/audit/seat/hooks_setup.py"), "--self-test"],
+                                   capture_output=True, text=True, env=dict(os.environ, HPO_HOOKS_MUTANT="1"))
+                n += 1
+                if r.returncode == 0:
+                    print(f"  FAIL mutant '{label}' survived")
+                    fails.append(label)
+            finally:
+                shutil.rmtree(tgt, ignore_errors=True)
+    print(f"hooks_setup self-test: {n} checks, {len(fails)} failed")
+    return 1 if fails else 0
+
+
+def main(argv: list[str]) -> int:
+    path = Path(os.environ.get("HOME", "~")).expanduser() / ".claude" / "settings.json"
+    if "--settings" in argv:
+        path = Path(argv[argv.index("--settings") + 1])
+    try:
+        if "--self-test" in argv:
+            return self_test("--no-mutants" not in argv)
+        if "--check" in argv:
+            rc, out = check(load(path))
+            print("\n".join(out))
+            return rc
+        if "--install" in argv:
+            return cmd_install(path)
+    except (ValueError, OSError) as e:
+        print(f"hooks_setup: REFUSE {e}", file=sys.stderr)
+        return 2
+    print(__doc__)
+    return 2
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/tools/audit/seat/instruments/hooks_setup.py.md b/tools/audit/seat/instruments/hooks_setup.py.md
new file mode 100644
index 000000000..3c9df2455
--- /dev/null
+++ b/tools/audit/seat/instruments/hooks_setup.py.md
@@ -0,0 +1,12 @@
+# `hooks_setup.py`
+
+- `hooks_setup.py` — reports (`--check`) and installs (`--install`) the user-level Claude Code hooks the orchestrator's host depends on, from the tracked scripts under `tools/audit/seat/hooks/`; `--self-test` drives it against a throwaway `HOME`. When: setting up a host, or after a hook is added to its `HOOKS` table. Refusal: an unreadable settings file refuses (rc 2) and changes nothing; `--install` backs the file up first, only when it changes something, and a second run writes no byte.
+
+| hook | event | script | does | why it exists |
+|---|---|---|---|---|
+| liveness | SessionStart, PostCompact | `hooks/liveness.py` | demands a fresh policy re-read (`policy_reread_check.py`; always on PostCompact); prints `DEAD`/`ALARM` per late beat job and for a free `beatd.lock` (`beatd.py status`, so the loop list is the job table), `STALE` for an alive file under `$HPO_STATE_DIR/alive/` and for a digest whose `digest.txt` and beat journal both stood still, then the digest, then one `ARM:` line | after a compaction nobody re-armed the wake loop and owed lines stood unread for hours (2026-11-01) |
+| seat-interpreter | SessionStart | `hooks/seat_interpreter.py` | runs `seat_venv.sh --check`; one `SEAT-INTERPRETER` line when it refuses | a temp cleanup deleted the seat venv unnoticed (2026-10-03) |
+| git-identity | SessionStart | `hooks/git_identity.py` | sets the orchestrator checkout's local `user.name`/`user.email` from `$HPO_STATE_DIR/git-identity` when they differ | a commit under the host's default identity is refused only after the push (decision 0011) |
+| Bash guard | PreToolUse, project-level | `.claude/hooks/pre-bash.sh`, second arm | exit 2 for `git checkout/switch/reset/pull/merge/rebase/stash/clean/restore` whose cwd, `cd` or `-C` resolves to the checkout named in `$HPO_STATE_DIR/orch-checkout` | `beatd`, `tick_loop.sh` and `cloud_relay.sh` run from that checkout and bash reads a script incrementally |
+
+The three user-level hooks are inert (print nothing, exit 0) unless `$HPO_STATE_DIR/orch-checkout` names a directory; the guard is inert without `HPO_STATE_DIR` or that file, and fails open on an unparseable payload. `--check` reports the guard as present in the tree and installs nothing for it. Thresholds: `HPO_ALIVE_STALE_MIN` (120), `HPO_DIGEST_STALE_MIN` (30).

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
