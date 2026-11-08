# Review packet #3294
head: 7359a63866d9f66af019ff543f8d6864268d71b3
base: 5bc009bc82962df5d239cbacc2e570dffd9a9cf9

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=128642513802 neutral
arch-score / arch-score id=128642345616 success
arm id=128641426755 skipped
budget-raise-gate / budget-raise-gate id=128642345606 success
cancel-superseded id=128641431902 success
codeql id=128642346429 skipped
codeql / Analyze (actions) id=128641851117 success
codeql / Analyze (javascript-typescript) id=128641851086 success
codeql / Analyze (python) id=128641851021 in_progress
gate id=128642835260 failure
governance id=128642346871 skipped
governance / delivery-status id=128641851060 success
governance / delivery-status-publish id=128641852132 skipped
governance / env-matrix id=128641851079 success
governance / instrument-self-tests id=128641851069 in_progress
governance / policy-docs id=128641851025 success
governance / record id=128641852201 skipped
governance / wave-script id=128641851112 success
hassfest id=128642346708 skipped
hassfest / hassfest id=128641850953 success
kernel-points id=128642346614 skipped
pr-contract id=128642835720 skipped
prelude id=128641431737 success
refresh id=128641431849 success
tests id=128642346519 skipped
tests / arch-instrument id=128642673420 success
tests / briefs id=128641851022 success
tests / browser id=128642673428 in_progress
tests / closure-scope id=128641851107 success
tests / closures id=128642673557 in_progress
tests / coverage id=128642673347 in_progress
tests / fast (3.14) id=128642673442 in_progress
tests / mutation id=128641851042 success
tests / mutation-autofix id=128642740300 skipped
tests / mutation-pins id=128642739848 skipped
tests / nightly-ha id=128642674574 skipped
tests / nightly-status id=128641851006 success
tests / replay id=128642674583 skipped
tests / typing id=128642673386 success
validate id=128642346481 skipped
validate / validate-hacs id=128641850944 success

## Refusals
required-red: required context `gate` concluded failure at 7359a63866d9f66af019ff543f8d6864268d71b3

## Advisories
none

## carry_audit at the head
NOTE body item 6a07172e: R10-FLY-STANDING-CONTRACTS
NOTE body item 8d488756: R10-FLY-STANDING-CONTRACTS
NOTE body item 88565884: R10-FLY-STANDING-CONTRACTS
NOTE body item ffe275c6: R10-FLY-STANDING-CONTRACTS
NOTE body item e3821077: R10-FLY-STANDING-CONTRACTS
NOTE body item f29a186f: R10-FLY-STANDING-CONTRACTS
NOTE body item 28185cf3: R10-FLY-STANDING-CONTRACTS
NOTE body item 8a9d989c: R10-FLY-STANDING-CONTRACTS
CARRY-AUDIT: 8 finding item(s): 8 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash .claude/hooks/pre-bash.sh --self-test
             `.claude/hooks/pre-bash.sh` is in the tree at this head
  ok         python3 -I tools/audit/seat/hooks_setup.py --self-test
             `tools/audit/seat/hooks_setup.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/r10_bash_kill_hook_drive.py
             `tools/audit/seat/r10_bash_kill_hook_drive.py` is in the tree at this head
  unverified git
             `git` with no subcommand word to resolve
  unverified git -C <orch> pull
             `git pull` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git pull
             `git pull` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified bash -c
             bash runs an inline script rather than a file
  unverified sh -c
             sh runs an inline script rather than a file
  unverified git -C <orch> status
             `git status` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 -I tools/audit/seat/mutant_run.py --diff <merge base>...HEAD --cmd "python3 -I tools/audit/seat/hooks_setup.py --self-test --no-mutants" --max-mutants 0 --report-only
             `tools/audit/seat/mutant_run.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff 131b1358e408954ed0076904bb9a811e5e80fac8 HEAD
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/offline_spy.py tools/audit/seat/hooks_setup.py
             `tools/audit/seat/offline_spy.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/selftest_wiring.py --check
             `tools/audit/seat/selftest_wiring.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/tmp_paths.py --check
             `tools/audit/seat/tmp_paths.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/ref_privacy.py --check
             `tools/audit/seat/ref_privacy.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 11 resolved, 6 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.claude/hooks/pre-bash.sh b/.claude/hooks/pre-bash.sh
index 1ef88954f..bdf61786d 100755
--- a/.claude/hooks/pre-bash.sh
+++ b/.claude/hooks/pre-bash.sh
@@ -14,7 +14,8 @@
 # `|` `&` `(` `$(` a backtick, a newline, and past `sudo`, `xargs`, `env` and
 # the like. The same words inside a quoted argument (`echo "never pkill"`),
 # a comment, a heredoc body or an argument of `grep` do not run and are not read.
-# `bash -c '...'` and `eval` bodies are read, because they do run.
+# `bash -c '...'` and `eval` bodies are read, because they do run. Both arms
+# read the commands this one parser finds (HPO_PRE_BASH_PARSE_PY).
 #
 # KNOWN GAPS, by design: a name held in a variable (`$K x`), a wrapper option
 # that takes a value (`sudo -u root pkill x`) and a pid list built on an earlier
@@ -31,7 +32,9 @@ set -uo pipefail
 SELF_TEST=0
 [ "${1:-}" = "--self-test" ] && SELF_TEST=1
 
-# HPO_PRE_BASH_PY
+# HPO_PRE_BASH_PARSE_PY
+# # THE ONE COMMAND-POSITION PARSER, shared by both arms: `decide` prepends this
+# # block to each arm's block, so neither arm splits a command on its own.
 # import json, re, sys
 # try:
 #     payload = json.loads(sys.argv[1])
@@ -59,36 +62,43 @@ SELF_TEST=0
 #         "nice", "stdbuf", "setsid", "timeout", "builtin", "!"}
 # SHELLS = {"bash", "sh", "zsh", "dash", "ksh"}
 # SEP = " \t\n;&|()"
-# cmds = []                                # (statement id, command word)
+# cmds = []                                # (statement id, command word, argv), in the order run
 # stmt = 0
 #
 # def parse(s, i, close):
-#     """Scan s from i; record every word at command position. Returns the index past `close`."""
+#     """Scan s from i; record every simple command at command position. Returns the index past `close`."""
 #     global stmt
 #     n, at, prev, shellc = len(s), True, None, False
+#     argv, body = None, None              # this scan's open command; the words of an eval
+#     def end():                           # a separator closes the open command
+#         nonlocal argv, body
+#         if body:
+#             parse(" ".join(body), 0, None)   # the body of eval runs
+#         argv = body = None
 #     while i < n:
 #         c = s[i]
 #         if close == ")" and c == ")":
-#             return i + 1
+#             end(); return i + 1
 #         if close == "`" and c == "`":
-#             return i + 1
+#             end(); return i + 1
 #         if c in " \t":
 #             i += 1; continue
 #         if c in ";\n":
-#             stmt += 1; at = True; i += 1; continue
+#             end(); stmt += 1; at = True; i += 1; continue
 #         if c == "&":
-#             i += 2 if s[i:i+2] == "&&" else 1
+#             end(); i += 2 if s[i:i+2] == "&&" else 1
 #             stmt += 1; at = True; continue
 #         if c == "|":
+#             end()
 #             if s[i:i+2] == "||":
 #                 i += 2; stmt += 1
 #             else:
 #                 i += 1
 #             at = True; continue
 #         if c == "(":
-#             at = True; i += 1; continue
+#             end(); at = True; i += 1; continue
 #         if c == ")":
-#             at = True; i += 1; continue
+#             end(); at = True; i += 1; continue
 #         if c == "#":
 #             while i < n and s[i] != "\n":
 #                 i += 1
@@ -126,9 +136,9 @@ SELF_TEST=0
 #                 i = parse(s, i + 1, "`"); quoted_sub = True
 #             else:
 #                 w += ch; i += 1
-#         if shellc or prev == "eval":
+#         if shellc:
 #             shellc = False
-#             parse(w, 0, None)            # the body of bash -c / eval runs
+#             parse(w, 0, None)            # the body of bash -c runs
 #         if at:
 #             base = w.rsplit("/", 1)[-1]
 #             if re.fullmatch(r"\w+=.*", w) or base in WRAP or (w.startswith("-") and prev in WRAP):
@@ -136,20 +146,32 @@ SELF_TEST=0
 #             else:
 #                 at = False
 #                 if base:
-#                     cmds.append((stmt, base))
-#         elif w == "-c" and prev in SHELLS:
-#             shellc = True
+#                     argv = [w]
+#                     cmds.append((stmt, base, argv))
+#                     if base == "eval":
+#                         body = []
+#         else:
+#             if w == "-c" and prev in SHELLS:
+#                 shellc = True
+#             if w and argv is not None:
+#                 argv.append(w)
+#             if w and body is not None:
+#                 body.append(w)
 #         if at or w:
 #             prev = w.rsplit("/", 1)[-1]
+#     end()
 #     return i
 #
 # try:
 #     parse(text, 0, None)
 # except Exception:
 #     sys.exit(0)                          # anything unforeseen -- fail open
-#
-# feeds = {s for s, b in cmds if b == "pgrep"}
-# for s, b in cmds:
+# HPO_PRE_BASH_PARSE_PY_END
+
+# HPO_PRE_BASH_PY
+# # First arm: a kill by name, over the parse block's `cmds`.
+# feeds = {s for s, b, _ in cmds if b == "pgrep"}
+# for s, b, _ in cmds:
 #     if b in ("pkill", "killall") or (b == "kill" and s in feeds):
 #         what = "kill fed by pgrep" if b == "kill" else b
 #         print(f"`{what}` kills processes by name or pattern, and on a shared host "
@@ -160,17 +182,84 @@ SELF_TEST=0
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
+# import os, subprocess
+# # Second arm: the orchestrator's checkout is what beatd, tick_loop.sh and
+# # cloud_relay.sh run their scripts from, and bash reads a script
+# # incrementally, so a command that moves its HEAD or working tree corrupts
+# # them (2026-10-31, gap 4 of R10-FLY-STANDING-CONTRACTS). It reads the parse
+# # block's `cmds` -- so `bash -c`, `eval`, `( )` and `$( )` bodies are seen --
+# # following `cd` in the order the commands appear (a `cd` inside a subshell is
+# # carried past its close, which can only refuse more). INERT unless
+# # $HPO_STATE_DIR/orch-checkout names a directory; fails open on anything odd.
+# MOVERS = {"checkout", "switch", "reset", "pull", "merge", "rebase", "stash", "clean", "restore"}
+# try:
+#     state = os.environ.get("HPO_STATE_DIR", "")
+#     marker = open(os.path.join(state, "orch-checkout")).read().strip() if state else ""
+#     if not marker or not os.path.isdir(marker):
+#         sys.exit(0)
+#     guarded = os.path.realpath(marker)
+#     def toplevel(d):
+#         r = subprocess.run(["git", "-C", d, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
+#         return os.path.realpath(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else ""
+#     def under(d, p):
+#         return os.path.realpath(os.path.join(d, os.path.expandvars(os.path.expanduser(p))))
+#     cur = payload.get("cwd") or os.getcwd()
+#     for _, b, w in cmds:
+#         if b == "cd":
+#             to = [a for a in w[1:] if not a.startswith("-")]
+#             if to:
+#                 cur = under(cur, to[0])
+#             continue
+#         if b != "git":
+#             continue
+#         d, i = cur, 1
+#         while i < len(w) and w[i].startswith("-"):
+#             if w[i] == "-C" and i + 1 < len(w):
+#                 d = under(d, w[i + 1]); i += 2
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
+arm() { # $1 an arm's marker, $2 the payload: the shared parser, then that arm
+  { extract HPO_PRE_BASH_PARSE_PY; extract "$1"; } | python3 - "$2"
+}
+
+decide() { # $1 the raw payload; stdout: a refusal message, or nothing
+  # Prefilter: no `kill` anywhere in the payload means the first arm cannot
+  # match, and a bash `case` costs about 3 ms where a python start costs about
+  # 26. The second arm needs `git` in the payload AND a marker file.
+  case "$1" in
+    *kill*) arm HPO_PRE_BASH_PY "$1" ;;
+  esac
+  case "$1" in
+    *git*) [ -n "${HPO_STATE_DIR:-}" ] && [ -f "$HPO_STATE_DIR/orch-checkout" ] \
+             && arm HPO_PRE_BASH_GUARD_PY "$1" ;;
+  esac
+  return 0
 }
 
 if [ "$SELF_TEST" = 1 ]; then
@@ -208,6 +297,38 @@ pkill -f x
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
+  # the fix review's five probes (verdict/3294): bodies the shared parser reads
+  gst refuse "bash -c 'git pull'"               "$gtmp/orch"  "guard: a bash -c body is read"
+  gst refuse 'eval git pull'                    "$gtmp/orch"  "guard: an eval body is read"
+  gst refuse "(cd $gtmp/orch && git pull)"      "$gtmp/other" "guard: a subshell's cd is followed"
+  gst refuse "echo x \$(git -C $gtmp/orch checkout main)" "$gtmp/other" "guard: a \$( ) substitution is read"
+  gst refuse "sh -c 'cd $gtmp/orch; git reset --hard'" "$gtmp/other" "guard: a cd inside sh -c is followed"
+  gst allow  "echo 'git pull' > notes.txt"      "$gtmp/orch"  "guard: git pull as quoted echo text is allowed (null control)"
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
index 59acc1dcf..c0d6e2912 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -1010,6 +1010,13 @@ jobs:
           python3 -I tools/audit/seat/beat_jobs.py --self-test | tee "$RUNNER_TEMP/beat-jobs-self-test.txt"
           grep -Eq '^beat_jobs self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/beat-jobs-self-test.txt"
 
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
index 0a6011505..db902ea69 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3900,6 +3900,7 @@
    "tools/audit/seat/flow_metrics.py",
    "tools/audit/seat/gantt_drift.py",
    "tools/audit/seat/gh_calls.py",
+   "tools/audit/seat/hooks_setup.py",
    "tools/audit/seat/ledger.py",
    "tools/audit/seat/merge_train.py",
    "tools/audit/seat/moved_paths.py",
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index 73eb1f71b..193ad1537 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -126,3 +126,4 @@ sweep's standing-seat liveness step keep them alive.
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
index 000000000..f12ec91f4
--- /dev/null
+++ b/tools/audit/seat/hooks_setup.py
@@ -0,0 +1,414 @@
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
+def _run_hook(script: str, state: Path, payload: dict | None = None, *, env: dict | None = None,
+              seat: Path = SEAT, args: list[str] | None = None) -> str:
+    """The hook's stdout, plus an `EXIT <rc>` line when it exits non-zero (a hook must not)."""
+    tr = state.parent / "transcript.jsonl"
+    payload = dict({"hook_event_name": "SessionStart", "transcript_path": str(tr)}, **(payload or {}))
+    r = subprocess.run([sys.executable, "-I", str(seat / "hooks" / script),
+                        *(["--state", str(state)] if args is None else args)],
+                       input=json.dumps(payload), env=dict(os.environ, **(env or {})),
+                       capture_output=True, text=True)
+    return r.stdout + (f"EXIT {r.returncode}\n" if r.returncode else "")
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
+        res["liveness: a healthy table with a fresh stamp owes no policy re-read"] = "POLICY-REREAD" not in out
+        res["liveness: PostCompact demands the policy re-read"] = (
+            "POLICY-REREAD" in _run_hook("liveness.py", s, {"hook_event_name": "PostCompact"}))
+        res["liveness: an unparseable HPO_ALIVE_STALE_MIN falls back to its default"] = (
+            "ARM:" in (o := _run_hook("liveness.py", s, env={"HPO_ALIVE_STALE_MIN": "x"})) and "UNREADABLE" not in o)
+        past = time.time() - 120.5 * 60  # half a minute past the 120-minute default
+        os.utime(s / "alive" / "merge", (past, past))
+        res["liveness: an alive file half a minute past HPO_ALIVE_STALE_MIN is STALE"] = (
+            "STALE alive merge age_min=120" in _run_hook("liveness.py", s))
+        (s / "policy-reread.stamp").unlink()
+        res["liveness: SessionStart with no re-read stamp owes the policy re-read"] = (
+            "POLICY-REREAD owed" in _run_hook("liveness.py", s))
+        # a seat copy holding the hook but not policy_reread_check.py: the check cannot run
+        cp = tmp / "seatcopy"
+        (cp / "hooks").mkdir(parents=True)
+        shutil.copy2(SEAT / "hooks" / "liveness.py", cp / "hooks" / "liveness.py")
+        o = _run_hook("liveness.py", s, seat=cp)
+        res["liveness: a policy_reread_check that cannot run is UNREADABLE, not owed"] = (
+            "UNREADABLE policy_reread_check" in o and "POLICY-REREAD" not in o)
+        # the same copy with a stub beatd.py: each status line shape it reads
+        shutil.copy2(SEAT / "policy_reread_check.py", cp / "policy_reread_check.py")
+        (cp / "beatd.py").write_text(
+            "import os, sys\nprint('JOB pulse failed\\nJOB tick ok\\nJOB x\\nDOWN no pid\\nALERT disk\\nSTALE-CODE b')\n"
+            "sys.exit(2 if os.environ.get('STUB_RC') == '2' else 0)\n")
+        o = _run_hook("liveness.py", s, seat=cp)
+        res["liveness: beatd's failed job, DOWN, ALERT and STALE-CODE lines are reported, ok and short lines not"] = (
+            "ALARM job pulse failed" in o and "DEAD beatd no pid" in o and "ALARM ALERT disk" in o
+            and "ALARM STALE-CODE b" in o and "job tick" not in o and "UNREADABLE" not in o)
+        res["liveness: beatd status exiting 2 is UNREADABLE"] = (
+            "UNREADABLE beatd status" in _run_hook("liveness.py", s, seat=cp, env={"STUB_RC": "2"}))
+        res["liveness: a --state with no value, and no HPO_STATE_DIR, is inert"] = (
+            _run_hook("liveness.py", s, args=["--state"], env={"HPO_STATE_DIR": ""}) == ""
+            and _run_hook("liveness.py", s, args=[], env={"HPO_STATE_DIR": ""}) == "")
+        past = time.time() - 30.5 * 60  # half a minute past the 30-minute default
+        for p in (s / "digest" / "digest.txt", s / "beatd" / "journal.log"):
+            os.utime(p, (past, past))
+        res["liveness: a digest and journal half a minute past HPO_DIGEST_STALE_MIN are STALE"] = (
+            "STALE digest" in _run_hook("liveness.py", s))
+        # seat_interpreter against a stub seat_venv.sh: silent when it passes, its last line when not
+        (cp / "hooks" / "seat_interpreter.py").write_bytes((SEAT / "hooks" / "seat_interpreter.py").read_bytes())
+        (cp / "seat_venv.sh").write_text('[ "${STUB_VENV:-}" = ok ] && exit 0\necho first >&2\necho last >&2\nexit 1\n')
+        res["seat-interpreter: a passing seat_venv.sh --check prints nothing"] = (
+            _run_hook("seat_interpreter.py", s, seat=cp, env={"STUB_VENV": "ok"}) == "")
+        res["seat-interpreter: the refusal quotes the check's last line"] = (
+            _run_hook("seat_interpreter.py", s, seat=cp).startswith("SEAT-INTERPRETER refused: last;")
+            and _run_hook("seat_interpreter.py", s, seat=cp, args=["--state"], env={"HPO_STATE_DIR": ""}) == "")
+        os.close(fd)
+        gone = tmp / "gone"
+        gone.mkdir()
+        (gone / "orch-checkout").write_text(f"{tmp / 'no-such-checkout'}\n")
+        res["liveness: an orch-checkout naming no directory is inert"] = _run_hook("liveness.py", gone) == ""
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
+        # the fixture state holds orch-checkout but no venv-ci, so seat_venv.sh --check refuses
+        out = _run_hook("seat_interpreter.py", s)
+        res["seat-interpreter: a refusing seat_venv.sh --check prints SEAT-INTERPRETER refused"] = (
+            out.startswith("SEAT-INTERPRETER refused: seat_venv: no venv at") and "seat_venv.sh" in out)
+        (s / "git-identity").write_text("Seat Name\nseat@example.invalid\n")
+        first = _run_hook("git_identity.py", s)
+        repo = (s / "orch-checkout").read_text().strip()
+        have = subprocess.run(["git", "-C", repo, "config", "--local", "user.email"],
+                              capture_output=True, text=True).stdout.strip()
+        name = subprocess.run(["git", "-C", repo, "config", "--local", "user.name"],
+                              capture_output=True, text=True).stdout.strip()
+        res["git-identity: sets a differing identity, then prints nothing"] = (
+            "GIT-IDENTITY set user.email" in first and have == "seat@example.invalid"
+            and name == "Seat Name" and _run_hook("git_identity.py", s) == "")
+        (s / "git-identity").write_text("Other Name\n")
+        res["git-identity: a one-line identity file is ignored"] = _run_hook("git_identity.py", s) == ""
+        res["git-identity: a --state with no value is ignored"] = _run_hook("git_identity.py", s, args=["--state"]) == ""
+        # the installer's edges and its command line
+        rc, out = check({}, tmp / "bare")
+        res["check reports the project guard missing in a tree without it"] = (
+            rc == 1 and any(ln.startswith("missing pre-bash guard") for ln in out))
+        deep = tmp / "new" / "dir" / "settings.json"
+        res["install creates a settings file under a missing directory, then has nothing to change"] = (
+            cmd_install(deep) == 0 and check(load(deep))[0] == 0 and cmd_install(deep) == 0)
+        bad = tmp / "list.json"
+        bad.write_text("[]\n")
+        cli = lambda *a: subprocess.run([sys.executable, "-I", str(SEAT / "hooks_setup.py"), *a],  # noqa: E731
+                                        capture_output=True, text=True)
+        res["the command line: --check, --install, a non-object file refused, no mode"] = (
+            cli("--check", "--settings", str(deep)).returncode == 0
+            and cli("--install", "--settings", str(tmp / "cli" / "s.json")).returncode == 0
+            and (tmp / "cli" / "s.json").is_file()
+            and "REFUSE" in (r := cli("--check", "--settings", str(bad))).stderr and r.returncode == 2
+            and cli().returncode == 2)
+    finally:
+        shutil.rmtree(tmp, ignore_errors=True)
+    return res
+
+
+COPY_FOR_MUTANTS = (  # what cases() reads outside tools/audit/seat, copied beside each mutant
+    "tests/throwaway_git.py", "tests/typing_budgets.json", ".claude/settings.json", PROJECT_GUARD[1])
+MUTANTS = [  # (label, old text, new text): each must turn at least one case red
+    ("install skips the backup", "        shutil.copy2(path, bak)\n", "        pass\n"),
+    ("install rewrites an unrelated entry",
+     "    hooks = settings.setdefault(\"hooks\", {})\n",
+     "    hooks = settings.setdefault(\"hooks\", {})\n    hooks[\"Stop\"] = []\n"),
+    ("install is not idempotent", "            if st == \"ok\":\n                continue\n", ""),
+    ("liveness reads no dead loop", "            if f[2] == \"late\":", "            if False:"),
+    ("liveness reads no stale digest", "if not ages or min(ages) > _env_min(", "if False and min(ages) > _env_min("),
+    ("seat-interpreter never reports", "    if r.returncode == 0:\n        return []\n", "    if True:\n        return []\n"),
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
+        # the null control first: the copy un-mutated must pass, or every mutant "dies" of the copy
+        for label, old, new in [("null control: the copy un-mutated", None, None), *MUTANTS]:
+            tgt = Path(tempfile.mkdtemp(prefix="hooks-mutant-"))
+            try:
+                shutil.copytree(SEAT, tgt / "tools/audit/seat", ignore=shutil.ignore_patterns("__pycache__", "fixtures"))
+                for rel in COPY_FOR_MUTANTS:
+                    (tgt / rel).parent.mkdir(parents=True, exist_ok=True)
+                    shutil.copy2(ROOT / rel, tgt / rel)
+                # the hooks before this file: an anchor without a newline also matches its own MUTANTS literal here
+                for f in ("hooks/liveness.py", "hooks/seat_interpreter.py", "hooks_setup.py"):
+                    p = tgt / "tools/audit/seat" / f
+                    text = p.read_text()
+                    if old is None or old in text:
+                        p.write_text(text if old is None else text.replace(old, new, 1))
+                        break
+                else:
+                    print(f"  FAIL mutant '{label}': its target text is gone")
+                    fails.append(label)
+                    continue
+                r = subprocess.run([sys.executable, "-I", str(tgt / "tools/audit/seat/hooks_setup.py"), "--self-test"],
+                                   capture_output=True, text=True, env=dict(os.environ, HPO_HOOKS_MUTANT="1"))
+                n += 1
+                if (r.returncode == 0) != (old is None):
+                    print(f"  FAIL mutant '{label}' " + ("is red: " + " | ".join(
+                        ln.strip() for ln in r.stdout.splitlines() if "FAIL" in ln) if old is None else "survived"))
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
index 000000000..f6411c8fa
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
+| Bash guard | PreToolUse, project-level | `.claude/hooks/pre-bash.sh`, second arm | exit 2 for `git checkout/switch/reset/pull/merge/rebase/stash/clean/restore` whose cwd, `cd` or `-C` resolves to the checkout named in `$HPO_STATE_DIR/orch-checkout`, read through the hook's one command-position parser (`HPO_PRE_BASH_PARSE_PY`), so `bash -c`, `eval`, `( )` and `$( )` bodies count | `beatd`, `tick_loop.sh` and `cloud_relay.sh` run from that checkout and bash reads a script incrementally |
+
+The three user-level hooks are inert (print nothing, exit 0) unless `$HPO_STATE_DIR/orch-checkout` names a directory; the guard is inert without `HPO_STATE_DIR` or that file, and fails open on an unparseable payload. `--check` reports the guard as present in the tree and installs nothing for it. Thresholds: `HPO_ALIVE_STALE_MIN` (120), `HPO_DIGEST_STALE_MIN` (30).

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
