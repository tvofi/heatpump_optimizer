# Review packet #3223
head: 81ee61752cff8ba51d41546f540e50ff1c950fac
base: 8b49d50b0a4c3eebee0edeb6ec98aa365e3d004f

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=127450375160 success
arch-score / arch-score id=127557729152 success
arm id=127449589239 skipped
budget-raise-gate / budget-raise-gate id=127557698737 success
cancel-superseded id=127557710239 success
codeql id=127557722344 skipped
codeql / Analyze (actions) id=127557698513 success
codeql / Analyze (javascript-typescript) id=127557699601 success
codeql / Analyze (python) id=127557699806 success
gate id=127558800149 success
governance id=127557732860 skipped
governance / delivery-status id=127557699428 failure
governance / delivery-status-publish id=127557698767 skipped
governance / env-matrix id=127557699515 success
governance / instrument-self-tests id=127557699302 success
governance / policy-docs id=127557698644 success
governance / record id=127557698808 skipped
governance / wave-script id=127557699400 success
hassfest id=127557653660 skipped
hassfest / hassfest id=127557698997 success
kernel-points id=127557736491 skipped
pr-contract / pr-contract id=127558241838 success
prelude id=127557697227 success
refresh id=127557713424 success
tests id=127557652730 skipped
tests / arch-instrument id=127557700791 success
tests / briefs id=127557699355 success
tests / browser id=127557701272 success
tests / ci-ratchet id=127557703444 skipped
tests / claims-autofix id=127557703334 skipped
tests / closure-scope id=127557699045 success
tests / closures id=127557702107 success
tests / closures-autofix id=127557704997 skipped
tests / coverage id=127557701751 success
tests / coverage-ratchet id=127557704000 success
tests / fast (3.14) id=127557701096 success
tests / graders-head-copy id=127557703180 success
tests / lane-proofs id=127557704083 success
tests / mutation id=127557699421 success
tests / mutation-autofix id=127557703348 skipped
tests / mutation-pins id=127557701771 skipped
tests / nightly-ha id=127557701542 skipped
tests / nightly-status id=127557699257 failure
tests / replay id=127557700508 skipped
tests / typing id=127557701845 success
validate id=127557699381 skipped
validate / validate-hacs id=127557698425 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item e70400f3: R10-RAISE-GATE-SHIM
NOTE body item 35c84a90: R10-RAISE-GATE-SHIM
NOTE body item ae76342e: dismissed:the brief scopes the guard to the seat shims and the note calls it a habit guard, not a boundary.
NOTE body item fa55f75b: dismissed:the orchestrator reads the job's duration from the next raise PR's run.
CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/audit/seat/gh_calls.py --self-test
             `tools/audit/seat/gh_calls.py` is in the tree at this head
  ok         python3 tools/audit/seat/queue_pre_flight.py --self-test
             `tools/audit/seat/queue_pre_flight.py` is in the tree at this head
  ok         bash tools/audit/seat/seat_venv.sh --self-test
             `tools/audit/seat/seat_venv.sh` is in the tree at this head
  unverified git diff origin/main...HEAD | grep '^+' | grep -ci 'revok'
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  unverified git diff origin/main...HEAD --quiet -- <file>
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         gh pr comment
             gh pr comment: every long flag accepted
  ok         gh pr comment 201
             gh pr comment: every long flag accepted
  ok         bash tools/audit/seat/cloud-setup.sh --check
             `tools/audit/seat/cloud-setup.sh` is in the tree at this head
  unverified python3 -c 'import numpy,scipy;print(numpy.__version__,scipy.__version__)'
             python3 runs an inline script rather than a file
  ok         tools/pr/prepr.sh <body>
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 10 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3223.md b/dev/programme/delivery/3223.md
new file mode 100644
index 000000000..10de0725d
--- /dev/null
+++ b/dev/programme/delivery/3223.md
@@ -0,0 +1 @@
+- [#3223](https://github.com/tvofi/heatpump_optimizer/pull/3223) — **open**, R10-RAISE-GATE-SHIM: raise gate shim (R10-RAISE-GATE-SHIM)
diff --git a/tools/audit/seat/gh_calls.py b/tools/audit/seat/gh_calls.py
index 289c7c553..13a9b2bbb 100644
--- a/tools/audit/seat/gh_calls.py
+++ b/tools/audit/seat/gh_calls.py
@@ -25,6 +25,7 @@ urllib read are not counted.
 """
 from __future__ import annotations
 
+import importlib.util
 import os
 import re
 import shutil
@@ -157,9 +158,12 @@ def self_test():
         stub.write_text('#!/bin/sh\nprintf "STUB %s\\n" "$*"; cat; printf "ERR\\n" >&2; exit 7\n')
         stub.chmod(0o700)
 
+        gcs = w / "gh_comment.py"  # stands for the tree's tools/pr/gh_comment.py: the installer bakes its path in
+        gcs.write_text("import subprocess, sys\nsys.exit(subprocess.run(['gh', *sys.argv[1:]]).returncode)\n")
+
         def install(src_text):
             dst = w / "own" / "gh"
-            dst.write_text(src_text)
+            dst.write_text(src_text.replace("gcpy=@HPO_GH_COMMENT@\n", f"gcpy={gcs}\n"))
             dst.chmod(0o700)
 
         # Hermetic PATH: the shim and the stub, plus a dir of symlinks to the few
@@ -446,10 +450,181 @@ def self_test():
             check(f"mutant killed: {name}", ok and tripped)
             install(good)
 
-        killed("no --input skip", "--input|", "", "input")
+        killed("no --input skip", "--raw-field|--input) skip", "--raw-field) skip", "input")
         killed("clean() is cat", "tr -c 'A-Za-z0-9_./:-' '?'", "cat", "clean")
         killed("no mkdir of the state dir", '  mkdir -p "$state"\n', "", "mkdir")
 
+        # The #201 comment guard (R10-RAISE-GATE-SHIM): a comment write on the tracking issue
+        # reaches the real gh only through gh_comment.py. The stub exits 7, a refusal exits 1.
+        # the kill word is built from fragments at runtime, never written whole in a file
+        # (the guard's own pattern is the stem of these two); the id is the fixture's
+        fixture_id = "fixture-mandate-0000"
+        kill = "".join(("Re", "vo", "ked"))
+        kill_body = f"{kill} mandate {fixture_id}"
+        planted = ["api", "-X", "POST", "repos/o/r/issues/201/comments", "-f", f"body={kill_body}"]
+        raw = run(planted)
+        check("planted: a raw `gh api` post of a revocation to #201 is refused, the real gh never run",
+              raw.returncode == 1 and b"gh_comment.py" in raw.stderr and b"STUB" not in raw.stdout)
+        via_ok = run([], via=f"{py} -I {gcs} " + " ".join(planted[:5]) + " -f body=ok")
+        check("control: the same post made by a python running gh_comment.py reaches the real gh",
+              via_ok.returncode == 7 and b"STUB api -X POST" in via_ok.stdout)
+        via_close = run([], via=f"{py} -I {gcs} issue close 201 --comment x")
+        check("control: the known poster's own `issue close 201 --comment` reaches the real gh",
+              via_close.returncode == 7 and b"STUB issue close" in via_close.stdout)
+        spoof = run([], via=f"{py} -c 'pass' gh_comment.py; gh api repos/o/r/issues/201/comments -f body=x")
+        check("a shell that merely names gh_comment.py is not gh_comment.py", spoof.returncode == 1)
+        other = w / "other"
+        other.mkdir()
+        (other / "gh_comment.py").write_text(gcs.read_text())
+        post = "import subprocess, sys; sys.exit(subprocess.run(['gh', 'api', '-X', 'POST', 'repos/o/r/issues/201/comments', '-f', 'body=x']).returncode)"
+        (other / "lnk.py").symlink_to(gcs)
+        W = "api -X POST repos/o/r/issues/201/comments -f body=x"
+        for label, via, want_rc in (
+                ("python -X taking gh_comment.py as its value, then -c code", f"{py} -X gh_comment.py -c \"{post}\"", 1),
+                ("another file of the basename gh_comment.py", f"{py} {other / 'gh_comment.py'} {W}", 1),
+                ("a symlink named for another file to the tree's script", f"{py} {other / 'lnk.py'} {W}", 1),
+                ("python -c code naming gh_comment.py in its text", f"{py} -c \"{post}\" gh_comment.py", 1),
+                ("null control: -X dev -W ignore -I before the tree's script", f"{py} -X dev -W ignore -I {gcs} api -X POST repos/o/r/issues/201/comments -f body=x", 7),
+                ("null control: the tree's script by a relative path", f"cd {w} && {py} gh_comment.py api -X POST repos/o/r/issues/201/comments -f body=x", 7),
+                ("null control: -Wignore attached before the script", f"{py} -Wignore -B {gcs} api -X POST repos/o/r/issues/201/comments -f body=x", 7)):
+            check(f"parent check: {label}", run([], via=via).returncode == want_rc)
+        for label, args in (("a GET of #201's comments", ["api", "repos/o/r/issues/201/comments"]),
+                            ("a post to another issue", ["api", "repos/o/r/issues/202/comments", "-f", "body=x"]),
+                            ("a post to another issue with upper-case segments", ["api", "repos/o/r/ISSUES/202/COMMENTS", "-f", "body=x"]),
+                            ("a post to a comment of a longer number", ["api", "repos/o/r/issues/2011/comments", "-f", "body=x"]),
+                            ("a post to dot segments that resolve to another issue", ["api", "repos/o/r/issues/201/../202/comments", "-f", "body=x"]),
+                            ("a post to a percent-encoded other issue", ["api", "repos/o/r/issues/%32%30%32/comments", "-f", "body=x"]),
+                            ("a gh issue comment on another issue", ["issue", "comment", "202", "-b", "x"]),
+                            ("a gh issue comment --body on another issue, number first", ["issue", "comment", "202", "--body", "201"]),
+                            ("a gh issue comment --body-file on another issue", ["issue", "comment", "--body-file", "201", "202"]),
+                            ("a gh issue comment on a #202 URL with a trailing slash", ["issue", "comment", "https://github.com/o/r/issues/202/", "-b", "x"]),
+                            ("a gh issue comment on a percent-encoded #202", ["issue", "comment", "%32%30%32", "-b", "x"]),
+                            ("a gh issue view of #201", ["issue", "view", "201"]),
+                            ("a gh issue list", ["issue", "list", "-R", "o/r", "--state", "all"]),
+                            ("a gh issue close with a comment on another issue", ["issue", "close", "202", "--comment", "x"]),
+                            ("a gh issue close -c on another issue", ["issue", "close", "-c", "x", "202"]),
+                            ("a gh issue reopen with a comment on another issue", ["issue", "reopen", "202", "-c", "x"]),
+                            ("a gh issue close of #202 with no comment", ["issue", "close", "202"]),
+                            ("a gh pr view", ["pr", "view", "5", "--json", "state"]),
+                            ("a gh pr merge of another number", ["pr", "merge", "5", "--squash"]),
+                            ("a graphql read query", ["api", "graphql", "-f", "query=query{viewer{login}}", "-F", "n=1"]),
+                            ("an api GET with an Accept header", ["api", "-H", "Accept: application/vnd.github.raw", "repos/o/r/contents/x"]),
+                            ("an api write at a non-issue path", ["api", "-X", "POST", "repos/o/r/git/refs", "-f", "ref=x"]),
+                            ("a post to a pull request's review comments", ["api", "repos/o/r/pulls/5/comments", "-f", "body=x"]),
+                            ("a workflow run", ["workflow", "run", "ci.yml"]),
+                            ("a gh run list", ["run", "list"]),
+                            ("a version query", ["--version"])):
+            check(f"null control: {label} reaches the real gh", run(args).returncode == 7)
+        refused = (
+            ("gh issue comment 201", ["issue", "comment", "201", "-b", f"{kill.lower()} {fixture_id}"]),
+            ("gh issue comment on a #201 URL", ["issue", "comment", "https://github.com/o/r/issues/201", "-b", "x"]),
+            ("gh issue comment on a #201 URL with a trailing slash", ["issue", "comment", "https://github.com/o/r/issues/201/", "-b", "x"]),
+            ("gh issue comment on a #201 URL with an anchor", ["issue", "comment", "https://github.com/o/r/issues/201#issuecomment-1", "-b", "x"]),
+            ("gh issue comment --body x 201", ["issue", "comment", "--body", "x", "201"]),
+            ("gh issue comment --body=x 201", ["issue", "comment", "--body=x", "201"]),
+            ("gh issue comment -bx 201", ["issue", "comment", "-bx", "201"]),
+            ("gh issue comment --body-file f 201", ["issue", "comment", "--body-file", "f", "201"]),
+            ("gh issue comment -F f 201", ["issue", "comment", "-F", "f", "201"]),
+            ("gh issue comment -R o/r -b x 201", ["issue", "comment", "-R", "o/r", "-b", "x", "201"]),
+            ("gh issue comment --repo o/r --body x 201", ["issue", "comment", "--repo", "o/r", "--body", "x", "201"]),
+            ("gh issue comment 0201", ["issue", "comment", "0201", "-b", "x"]),
+            ("gh issue comment #201", ["issue", "comment", "#201", "-b", "x"]),
+            ("gh issue comment %32%30%31", ["issue", "comment", "%32%30%31", "-b", "x"]),
+            ("gh issue comment with no target (unreadable, fail closed)", ["issue", "comment", "-b", "x"]),
+            ("gh issue comment on a branch word (unreadable, fail closed)", ["issue", "comment", "main", "-b", "x"]),
+            ("gh api --method=POST", ["api", "--method=POST", "repos/o/r/issues/201/comments"]),
+            ("gh api -XPOST", ["api", "-XPOST", "repos/o/r/issues/201/comments"]),
+            ("gh api --input", ["api", "repos/o/r/issues/201/comments", "--input", "f.json"]),
+            ("gh api an upper-cased issues segment", ["api", "repos/o/r/ISSUES/201/comments", "-f", "body=x"]),
+            ("gh api an upper-cased comments segment", ["api", "repos/o/r/issues/201/COMMENTS", "-f", "body=x"]),
+            ("gh api a trailing slash", ["api", "repos/o/r/issues/201/comments/", "-f", "body=x"]),
+            ("gh api a leading zero", ["api", "repos/o/r/issues/0201/comments", "-f", "body=x"]),
+            ("gh api a percent-encoded number", ["api", "repos/o/r/issues/%32%30%31/comments", "-f", "body=x"]),
+            ("gh api a percent-encoded slash", ["api", "repos/o/r/issues%2F201/comments", "-f", "body=x"]),
+            ("gh api an unresolved percent-escape (fail closed)", ["api", "repos/o/r/issues/201/comments%252F", "-f", "body=x"]),
+            ("gh api dot segments resolving to #201", ["api", "repos/o/r/issues/202/../201/comments", "-f", "body=x"]),
+            ("gh api doubled slashes", ["api", "repos//o/r/issues//201/comments", "-f", "body=x"]),
+            ("gh api a full URL", ["api", "https://api.github.com/repos/o/r/issues/201/comments", "-f", "body=x"]),
+            ("gh api a query string", ["api", "repos/o/r/issues/201/comments?per_page=1", "-f", "body=x"]),
+            ("gh api an anchor", ["api", "repos/o/r/issues/201/comments#x", "-f", "body=x"]),
+            # deny by default: the rule refuses each of these, no arm is named for any
+            ("gh issue close 201 --comment", ["issue", "close", "201", "--comment", "x"]),
+            ("gh issue close 201 -c", ["issue", "close", "201", "-c", "x"]),
+            ("gh issue close 201 -cx", ["issue", "close", "201", "-cx"]),
+            ("gh issue close 201 --comment=x", ["issue", "close", "201", "--comment=x"]),
+            ("gh issue reopen 201 --comment", ["issue", "reopen", "201", "--comment", "x"]),
+            ("gh issue close with no comment on #201", ["issue", "close", "201"]),
+            ("gh issue edit 201", ["issue", "edit", "201", "--title", "x"]),
+            ("a gh alias word", ["c201", "-b", "x"]),
+            ("a gh issue verb that is not known", ["issue", "frobnicate", "202"]),
+            ("an unknown flag on gh issue close", ["issue", "close", "--zzz", "x", "202"]),
+            ("an unknown flag before a #201 target", ["issue", "comment", "--zzz", "201", "-b", "x"]),
+            ("a short-flag cluster on gh issue close", ["issue", "close", "-wc", "x", "201"]),
+            ("two targets on gh issue close", ["issue", "close", "202", "201"]),
+            ("gh issue close with no target", ["issue", "close", "-c", "x"]),
+            ("a flag before the subcommand", ["-R", "o/r", "issue", "comment", "201"]),
+            ("gh pr comment 201", ["pr", "comment", "201", "-b", "x"]),
+            ("gh pr close 201 --comment", ["pr", "close", "201", "--comment", "x"]),
+            ("a PATCH of a comment by id", ["api", "-X", "PATCH", "repos/o/r/issues/comments/9", "-f", "body=x"]),
+            ("a DELETE of a comment by id", ["api", "-X", "DELETE", "repos/o/r/issues/comments/9"]),
+            ("a graphql mutation", ["api", "graphql", "-f", "query=mutation{addComment(input:{})}"]),
+            ("a graphql query read from a file", ["api", "graphql", "-F", "query=@q.graphql"]),
+            ("a graphql call with --input", ["api", "graphql", "--input", "q.json"]),
+            ("an api call with an unknown flag", ["api", "--zzz", "repos/o/r/issues/201/comments", "-f", "body=x"]),
+            ("an api call with a non-Accept header", ["api", "-H", "X-HTTP-Method-Override: POST", "repos/o/r/issues/201/comments"]),
+            ("gh extension exec", ["extension", "exec", "x"]))
+        for label, args in refused:
+            check(f"{label} is refused", run(args).returncode == 1)
+        mut = good.replace("tracker=201", "tracker=0")
+        check("mutant: the guard's issue number changed lets the planted post through",
+              mut != good and run(planted, shim_text=mut).returncode == 7)
+        install(good)
+
+        # mutants of each rule of the guard: each lets one refused spelling (or spoof) through
+        def guard_mutant(name, old, new_, args=None, via=None, rc=7):
+            m = good.replace(old, new_)
+            r_ = run(args, shim_text=m) if via is None else run([], via=via, shim_text=m)
+            check(f"mutant killed: {name}", m != good and r_.returncode == rc)
+            install(good)
+        guard_mutant("--body not read as taking a value (a #202 comment with a body word is refused)",
+                     "ISSUE_VAL='-b --body ", "ISSUE_VAL='-b ",
+                     ["issue", "comment", "202", "--body", "201"], rc=1)
+        guard_mutant("leading zeros kept", 'n=${n#"${n%%[!0]*}"}', ":", ["issue", "comment", "0201", "-b", "x"])
+        guard_mutant("no percent-decoding", "*%*) w=$(printf '%b' \"${w//%/\\\\x}\"); case $w in *[%#?\\\\]*) printf '?'; return ;; esac ;; esac\n  while",
+                     "*%*) ;; esac\n  while", ["issue", "comment", "%32%30%32", "-b", "x"], rc=1)
+        guard_mutant("trailing slash kept on the target", 'while [ "${w%/}" != "$w" ]; do w=${w%/}; done', ":",
+                     ["issue", "comment", "https://github.com/o/r/issues/202/", "-b", "x"], rc=1)
+        guard_mutant("an unreadable target passes", "t=$(num \"${pos[1]}\"); [ \"$t\" != '?' ] && [ \"$t\" != \"$tracker\" ]", 't=$(num "${pos[1]}"); [ "$t" != "$tracker" ]',
+                     ["issue", "comment", "main", "-b", "x"])
+        guard_mutant("dot segments kept", "      ''|.) ;;\n      ..) [", "      ''|.) ;;\n      zz) [", ["api", "repos/o/r/issues/202/../201/comments", "-f", "body=x"])
+        guard_mutant("empty path segments kept", "      ''|.) ;;\n", "      .) ;;\n",
+                     ["api", "repos//o/r/issues//201/comments", "-f", "body=x"])
+        guard_mutant("the deny-by-default arm passes an unknown subcommand", "    *) return 1 ;;\n  esac\n}\ngate", "    *) return 0 ;;\n  esac\n}\ngate",
+                     ["c201", "-b", "x"])
+        guard_mutant("an unknown flag on issue close is let through", "--*|-?) if has \"$ISSUE_VAL\" \"$a\"; then skip=1; elif ! has \"$ISSUE_BOOL\" \"$a\"; then bad=1; fi ;;",
+                     "--*|-?) if has \"$ISSUE_VAL\" \"$a\"; then skip=1; fi ;;", ["issue", "close", "--zzz", "202"])
+        guard_mutant("graphql mutations let through", "case $low in *mutation*|*subscription*) return 1 ;; esac", ":",
+                     ["api", "graphql", "-f", "query=mutation{addComment(input:{})}"])
+        guard_mutant("path segments not lower-cased", "  w=$(printf '%s' \"$w\" | tr 'A-Z' 'a-z')\n", "",
+                     ["api", "repos/o/r/ISSUES/201/comments", "-f", "body=x"])
+        guard_mutant("path segments not lower-cased (comments segment)", "  w=$(printf '%s' \"$w\" | tr 'A-Z' 'a-z')\n", "",
+                     ["api", "repos/o/r/issues/201/COMMENTS", "-f", "body=x"])
+        guard_mutant("a comment by id let through", '[ "$nxt" = comments ] && return 1', ":",
+                     ["api", "-X", "PATCH", "repos/o/r/issues/comments/9", "-f", "body=x"])
+        guard_mutant("issue close -c value not skipped (target read as the value)", "ISSUE_VAL='-b --body -F --body-file -R --repo -c --comment ", "ISSUE_VAL='-b --body -F --body-file -R --repo ",
+                     ["issue", "close", "202", "--comment", "201"], rc=1)
+        guard_mutant("python -W/-X value read as the script", "[WX]) [", "[W]) [",
+                     None, via=f"{py} -X dev -W ignore -I {gcs} {W}", rc=1)
+        guard_mutant("the script matched by basename", 'a=$(rp "$script") && b=$(rp "$gcpy") && [ "$a" = "$b" ] && ok=1',
+                     '[ "${script##*/}" = gh_comment.py ] && ok=1', None, via=f"{py} {other / 'gh_comment.py'}")
+        try:
+            spec = importlib.util.spec_from_file_location("budget_raise_gate", SHIM.parents[3] / "policy" / "budget_raise_gate.py")
+            g = importlib.util.module_from_spec(spec)
+            spec.loader.exec_module(g)
+            check("the shim's tracker number is budget_raise_gate.MANDATE_ISSUE", f"tracker={g.MANDATE_ISSUE}\n" in good)
+        except (OSError, ImportError, AttributeError):
+            check("the shim's tracker number is budget_raise_gate.MANDATE_ISSUE (gate readable)", False)
+
         # a shim is never its own real gh. The PATH is hermetic: no real gh on any host.
         (w / "real" / "gh").unlink()
         no_gh_path = f"{w / 'own'}:{tools}"
diff --git a/tools/audit/seat/instruments/shims_seat-gh.md b/tools/audit/seat/instruments/shims_seat-gh.md
index 19cddb16c..c9e3bc44e 100644
--- a/tools/audit/seat/instruments/shims_seat-gh.md
+++ b/tools/audit/seat/instruments/shims_seat-gh.md
@@ -11,3 +11,19 @@
   Refusal: no real gh, `gh shim: no real gh on PATH`, rc 127. When: the shared
   token's core bucket is spent and no host log names the caller (P284). Tested by
   `gh_calls.py --self-test`.
+  Comment guard (R10-RAISE-GATE-SHIM), deny by default: any call that could write a comment on #201
+  is refused unless the caller is python running the tree's own `tools/pr/gh_comment.py`, resolved by
+  real path (the installer bakes the path into the copy). Let through without it: a call on an explicit
+  list of calls that cannot. `issue` view/list/status/create; `issue` comment/close/reopen/edit/delete/
+  lock/unlock/pin/unpin/transfer/develop only with one target read as a plain number other than 201,
+  under gh's own flag table (an unknown flag, a short-flag cluster or a second target is refused, so
+  `close`/`reopen` `--comment`/`-c` are covered by the rule, not by name); `pr` unless a word reads as
+  201; `api` as a read (no field, no `--input`, GET, only an Accept header) or as a write that is not at
+  `issues/201/comments`, not at an unreadable path, not at `issues/comments/<id>` and not graphql unless
+  the document holds no `mutation`/`subscription` and is not read from a file; gh command groups with no
+  issue-comment surface; everything else (an unknown subcommand, an alias, an extension, a leading flag
+  but `--version`/`--help`) is refused. The number is read after dropping leading zeros, trailing
+  slashes, query, anchor, one %-decoding, dot segments and upper-case letters (path segments are matched in lower case).
+  Residual, by design (Carry: R10-RAISE-GATE-SHIM): the caller test reads `ps` args, which a caller
+  writes, so `exec -a 'python3 <tree>/tools/pr/gh_comment.py' ...` passes as the poster. That is
+  deliberate evasion, not a seat's habit, and has no fix in a ps-based parent check.
diff --git a/tools/audit/seat/merge_train.py b/tools/audit/seat/merge_train.py
index 4370f22e5..f3044585e 100644
--- a/tools/audit/seat/merge_train.py
+++ b/tools/audit/seat/merge_train.py
@@ -1668,6 +1668,12 @@ class Train:
             raise Stop("approve", "the body could not be read for the raise justification: " + o.strip()[-160:])
         return o
 
+    def _measured_score(self, g, h: str) -> str:
+        """score.py's report line for <h> against origin/main, the gate's own
+        measured_score: the figure a mandated raise's body must name, judged at
+        the merge as the budget-raise-gate check judges it at the head."""
+        return g.measured_score("origin/main", h)
+
     def raise_hold(self, pr: int, h: str, files: "list[str]") -> "tuple[list[str], bool, str]":
         """(raises, held, why) for <pr> at <h>: the train's ONE reading of a
         budget raise, shared by `approve` and queue_pre_flight.py.
@@ -1725,7 +1731,7 @@ class Train:
         try:
             ok, why = g.approval(self._reviews(pr, "the owner's approval"), h, self._mandate_read,
                                  lambda _r, cid, c, t: g.mandate_state(cid, c, t, now, at, "merge"),
-                                 justify=lambda: g.justification(self._body(pr)))
+                                 justify=lambda: g.justified(self._body(pr), lambda: self._measured_score(g, h)))
         except Stop:
             raise
         except Exception as e:  # fail closed: an unread approval is none
@@ -3500,6 +3506,10 @@ def _self_test() -> int:
     passed = failed = 0
     H0, H1, H2, V = "a" * 40, "b" * 40, "9" * 39 + "a", "c" * 40
     BOT_SUBJ = "ci: pin killed mutants"
+    # The figure a mandated raise's body must name is the gate's measured_score (a
+    # scorer run on a worktree); the world below answers with one fixed line.
+    MEASURED = ["Architecture score: dS +0.4000 IMPROVES"]
+    Train._measured_score = lambda self, g, h: MEASURED[0]
 
     def check(name: str, cond: bool) -> None:
         nonlocal passed, failed
@@ -4226,6 +4236,14 @@ def _self_test() -> int:
     check("#2209's shape MUTATION (the mandate re-read at the merge): a re-anchored approval "
           "under an expired mandate stops exactly as today",
           rc == 1 and "a raise is the owner's" in lines[-1] and not merged(calls))
+    # The value, not only the shape (#3045 round 1: dS +0.0012 claimed, +0.0000 true).
+    planted_ds = JUST.replace("dS +0.4 IMPROVES", "dS +0.0012 IMPROVES")
+    rc, lines, calls = go(carry_world(reviews=[dict(owner_review(H1, NOW), id=RID)], mandate=mandate(NOW),
+                                      pr_body=planted_ds), mandate=CB, approval_carry=True)
+    check("a mandated raise whose body quotes a dS the scorer did not measure stops, as budget-raise-gate "
+          "refuses it (the train reads budget_raise_gate.justified, its measured figure)",
+          rc == 1 and "a raise is the owner's" in lines[-1] and "measures dS +0.4000 IMPROVES" in lines[-1]
+          and not merged(calls) and not approved(calls))
     rc, lines, calls = go(carry_world(reviews=[dict(owner_review(H1, NOW), id=RID)], mandate=mandate(NOW),
                                       pr_body=JUST.replace("Payments tried", "Paid")), mandate=CB, approval_carry=True)
     check("#2209's shape MUTATION (the gate's own justification): a mandated approval at the head "
diff --git a/tools/audit/seat/queue_pre_flight.py b/tools/audit/seat/queue_pre_flight.py
index d31a835b3..b448a7b6b 100644
--- a/tools/audit/seat/queue_pre_flight.py
+++ b/tools/audit/seat/queue_pre_flight.py
@@ -452,6 +452,9 @@ def _self_test() -> int:
     check("a policy head whose mandate was revoked PARKS, named as revoked",
           go({**POL, "reviews": [owner_review(H0, NOW)], "mandate": mandate(NOW),
               "thread": [revoke()]})[:2] == ("PARK", "policy"))
+    # The train judges a mandated raise's body against the gate's measured score (a scorer
+    # run on a worktree); the world here answers with the one line JUSTIFIED_BODY names.
+    mt.Train._measured_score = lambda self, g, h: "Architecture score: dS +0.4000 IMPROVES"
     BUD = {"files": ["tests/structure_budgets.json", ROW], "budgets": mt.RAISE_FIXTURE,
            "pr_body": mt.JUSTIFIED_BODY}
     check("a budget raise whose owner approval cites an in-force mandate, its body justified, passes",
diff --git a/tools/audit/seat/seat_venv.sh b/tools/audit/seat/seat_venv.sh
index b7b06f7f5..210735596 100755
--- a/tools/audit/seat/seat_venv.sh
+++ b/tools/audit/seat/seat_venv.sh
@@ -268,6 +268,18 @@ STUB
     "$ROOT/tools/audit/seat/cloud-setup.sh"
   expect "cloud-setup.sh is still the oracle for that pins call" $?
 
+  # --install-shims bakes the tree's gh_comment.py path into the installed gh shim's
+  # `gcpy=` line; without it every sanctioned post to the tracker is refused. The source
+  # shim carries the placeholder (null control); the installed copy carries the path and
+  # no placeholder. The installer's own trailing interpreter probe may fail here: only
+  # the written copy is read.
+  grep -qxF 'gcpy=@HPO_GH_COMMENT@' "$ROOT/tools/audit/seat/shims/seat-gh"
+  expect "the source gh shim carries the gcpy placeholder (null control)" $?
+  HPO_STATE_DIR=$W bash "$ROOT/tools/audit/seat/seat_venv.sh" --install-shims "$W/inst" >/dev/null 2>&1
+  grep -qxF "gcpy=$(printf '%q' "$ROOT/tools/pr/gh_comment.py")" "$W/inst/gh" \
+    && ! grep -qF '@HPO_GH_COMMENT@' "$W/inst/gh"
+  expect "--install-shims bakes the tree's gh_comment.py path into the installed gh shim" $?
+
   rm -rf "$W"
   printf 'seat_venv self-test: %s checks, %s failed\n' "$((pass + fail))" "$fail"
   [ "$fail" = 0 ]
@@ -284,7 +296,13 @@ case ${1:-} in
     done
     # The gh shim (P284) is installed as `gh`; it logs the call, then execs the
     # real gh found further along PATH. Read the log with gh_calls.py --top.
-    cp "$ROOT/tools/audit/seat/shims/seat-gh" "$dest/gh" && chmod 755 "$dest/gh"
+    # The comment guard names the tree's gh_comment.py by real path: bake it into the copy.
+    gcpy=$ROOT/tools/pr/gh_comment.py
+    [ -f "$gcpy" ] || die "no $gcpy for the gh shim's comment guard"
+    while IFS= read -r l; do
+      [ "$l" = 'gcpy=@HPO_GH_COMMENT@' ] && l="gcpy=$(printf '%q' "$gcpy")"
+      printf '%s\n' "$l"
+    done < "$ROOT/tools/audit/seat/shims/seat-gh" > "$dest/gh" && chmod 755 "$dest/gh"
     printf 'seat_venv: shims installed in %s; they run %s/bin/python3\n' "$dest" "$VENV"
     "$dest/python3" -c 'import sys; print("seat_venv: shim resolves to", sys.executable)' \
       || die "the installed shim does not start; build the venv first"
diff --git a/tools/audit/seat/shims/seat-gh b/tools/audit/seat/shims/seat-gh
index 1d1364b40..94781a751 100755
--- a/tools/audit/seat/shims/seat-gh
+++ b/tools/audit/seat/shims/seat-gh
@@ -39,13 +39,16 @@ done
 IFS=$ifs
 [ -n "$real" ] || { echo "gh shim: no real gh on PATH" >&2; exit 127; }
 
-sub=; verb=; skip=0
+sub=; verb=; third=; skip=0
 for a in "$@"; do
-  if [ $skip = 1 ]; then skip=0; continue; fi
+  if [ $skip = 1 ]; then
+    skip=0; continue
+  fi
   case $a in
-    -X|-H|-f|-F|-q|-t|-p|-R|-B|-b|--method|--header|--field|--raw-field|--input|--jq|--template|--hostname|--cache|--preview|--repo) skip=1 ;;
+    -f|-F|--field|--raw-field|--input) skip=1 ;;
+    -X|--method|-H|-q|-t|-p|-R|-B|-b|--body|--body-file|--header|--jq|--template|--hostname|--cache|--preview|--repo) skip=1 ;;
     -*) ;;
-    *) if [ -z "$sub" ]; then sub=$a; else verb=$a; break; fi ;;
+    *) if [ -z "$sub" ]; then sub=$a; elif [ -z "$verb" ]; then verb=$a; else third=$a; break; fi ;;
   esac
 done
 case $sub in
@@ -117,4 +120,223 @@ esac
   chmod 600 "$log"
 ) 2>/dev/null || true
 
+# The #201 comment guard (R10-RAISE-GATE-SHIM; tools/pr/gh_comment.py's mandate_guard
+# lives in that script alone, so a raw post bypassed it). DENY BY DEFAULT: a call that could
+# write a comment on the tracking issue is refused unless the caller is python running the
+# tree's own gh_comment.py (by real path); it is let through only when it is on an explicit
+# list of calls that cannot. The list is gh's own command table, not a list of spellings:
+#   - no subcommand, or --version/--help alone: pass; any other leading flag: refused;
+#   - `issue`: view/list/status/create pass; comment, close, reopen, edit, delete, lock,
+#     unlock, pin, unpin, transfer and develop pass only with exactly one target that reads as
+#     a plain number other than the tracker, under gh's own flag table (an unknown flag, or a
+#     short-flag cluster, is refused: it could be a value that moves the target); any other
+#     verb is refused;
+#   - `pr`: refused when any word reads as the tracker's number (a PR cannot be the issue,
+#     so this is belt and braces); otherwise passes;
+#   - `api`: a call with no body field, no --input, no method but GET and no header but
+#     Accept is a read and passes (flags read by gh api's own table, an unknown one refused);
+#     a write is refused at issues/<tracker>/comments, at an unreadable path, at
+#     issues/comments/<id> (a comment by id names no issue), and at graphql unless the
+#     document has no `mutation` or `subscription` and is not read from a file or --input;
+#   - the command groups with no issue-comment surface (workflow, release, run, repo, label,
+#     auth, secret, variable, cache, config, gist, ssh-key, gpg-key, codespace, project,
+#     ruleset, org, search, browse, status, completion, help, version, attestation) pass;
+#   - everything else is refused: an unknown subcommand, a gh alias, an extension.
+# The number is read after dropping leading zeros, a trailing slash, a query or anchor, one
+# %-decoding and `.`/`..`/empty path segments, matched in lower case. Residual, by design: the caller test reads
+# `ps` args, which a caller writes (`exec -a`), so a deliberate spoof of the parent passes
+# (Carry: R10-RAISE-GATE-SHIM); the shim is a guard against a seat's habit, not an adversary.
+tracker=201
+# gh_comment.py's own path: seat_venv.sh --install-shims bakes the tree's into the next
+# line; a shim run from its place in the tree derives it; anywhere else it stays empty,
+# and then no caller passes.
+gcpy=@HPO_GH_COMMENT@
+case $gcpy in @*) case $0 in */tools/audit/seat/shims/*) gcpy=${0%/tools/audit/seat/shims/*}/tools/pr/gh_comment.py ;; *) gcpy= ;; esac ;; esac
+
+# num <word>: the decimal number a word names, leading zeros dropped, or ? when it is not
+# one plain number (a URL counts only as .../issues/<n> or .../pull/<n>)
+num() {
+  local w=$1 n p
+  case $w in *\\*) printf '?'; return ;; esac
+  w=${w%%[#?]*}; w=${w#\#}
+  case $w in *%*) w=$(printf '%b' "${w//%/\\x}"); case $w in *[%#?\\]*) printf '?'; return ;; esac ;; esac
+  while [ "${w%/}" != "$w" ]; do w=${w%/}; done
+  case $w in
+    */*) n=${w##*/}; p=${w%/*}; case ${p##*/} in issues|pull) ;; *) printf '?'; return ;; esac ;;
+    *) n=$w ;;
+  esac
+  case $n in ''|*[!0-9]*) printf '?'; return ;; esac
+  n=${n#"${n%%[!0]*}"}
+  printf '%s' "${n:-0}"
+}
+# norm <path>: the path's segments after %-decoding, dropping a URL's scheme and host, a query
+# or anchor, and `.`/`..`/empty segments, and lower-casing every letter (a path segment is
+# matched in lower case: `ISSUES/201/COMMENTS` is the tracker's), into NSEG; 1 when it cannot be read
+norm() {
+  local w=$1 IFS=/ seg
+  local -a segs
+  NSEG=()
+  case $w in *\\*|*$'\n'*) return 1 ;; esac
+  w=${w%%[#?]*}
+  case $w in *%*) w=$(printf '%b' "${w//%/\\x}"); case $w in *[%#?\\]*|*$'\n'*) return 1 ;; esac ;; esac
+  case $w in *://*) w=${w#*://}; w=${w#*/} ;; esac
+  w=$(printf '%s' "$w" | tr 'A-Z' 'a-z')
+  set -f; read -r -a segs <<< "$w"; set +f
+  for seg in "${segs[@]}"; do
+    case $seg in
+      ''|.) ;;
+      ..) [ "${#NSEG[@]}" -gt 0 ] && NSEG=("${NSEG[@]:0:$((${#NSEG[@]} - 1))}") ;;
+      *) NSEG+=("$seg") ;;
+    esac
+  done
+  return 0
+}
+# has <list> <word>: 0 when the space-separated list holds the word
+has() { case " $1 " in *" $2 "*) return 0 ;; esac; return 1; }
+# rp <file>: the physical path of an existing regular file that is not a symlink, else nothing
+rp() {
+  local p=$1 d
+  case $p in /*) ;; *) p=$PWD/$p ;; esac
+  { [ -f "$p" ] && [ ! -L "$p" ]; } || return 1
+  d=$(cd "${p%/*}" 2>/dev/null && pwd -P) || return 1
+  printf '%s/%s' "$d" "${p##*/}"
+}
+
+ISSUE_VAL='-b --body -F --body-file -R --repo -c --comment -r --reason -t --title -a --assignee --add-assignee --remove-assignee -l --label --add-label --remove-label -m --milestone -p --project --add-project --remove-project -T --template -d --duplicate-of'
+ISSUE_BOOL='-w --web -e --editor --edit-last --create-if-none --delete-last --yes --remove-milestone -h --help'
+issue_gate() {
+  local a skip=0 t verb bad=
+  local -a pos=()
+  shift
+  for a in "$@"; do
+    if [ $skip = 1 ]; then skip=0; continue; fi
+    case $a in
+      --) bad=1 ;;
+      --*=*) has "$ISSUE_VAL" "${a%%=*}" || bad=1 ;;
+      --*|-?) if has "$ISSUE_VAL" "$a"; then skip=1; elif ! has "$ISSUE_BOOL" "$a"; then bad=1; fi ;;
+      -*) has "$ISSUE_VAL" "${a:0:2}" || bad=1 ;;
+      *) pos+=("$a") ;;
+    esac
+  done
+  verb=${pos[0]:-}
+  case $verb in
+    ''|view|list|status|create) return 0 ;;
+    comment|close|reopen|edit|delete|lock|unlock|pin|unpin|transfer|develop)
+      [ -z "$bad" ] && [ "${#pos[@]}" -eq 2 ] || return 1
+      t=$(num "${pos[1]}"); [ "$t" != '?' ] && [ "$t" != "$tracker" ] ;;
+    *) return 1 ;;
+  esac
+}
+pr_gate() {
+  local a
+  shift
+  for a in "$@"; do
+    case $a in -*) ;; *) [ "$(num "$a")" = "$tracker" ] && return 1 ;; esac
+  done
+  return 0
+}
+API_VAL='-q --jq -t --template -p --preview --hostname --cache'
+API_BOOL='--paginate --slurp -i --include --silent --verbose -h --help'
+api_gate() {
+  local a skip= path= meth= write= fields= unread= k t nxt low
+  local -a pos=()
+  shift
+  for a in "$@"; do
+    if [ -n "$skip" ]; then
+      case $skip in
+        m) meth=$a ;;
+        f) write=1; fields="$fields $a"; case $a in *=@*) unread=1 ;; esac ;;
+        i) write=1; unread=1 ;;
+        h) case $a in [Aa]ccept:*) ;; *) write=1 ;; esac ;;
+      esac
+      skip=; continue
+    fi
+    case $a in
+      -X|--method) skip=m ;;
+      -X?*) meth=${a#-X} ;;
+      --method=*) meth=${a#*=} ;;
+      -f|-F|--field|--raw-field) skip=f ;;
+      -f?*|-F?*) a=${a#-?}; write=1; fields="$fields $a"; case $a in *=@*) unread=1 ;; esac ;;
+      --field=*|--raw-field=*) a=${a#*=}; write=1; fields="$fields $a"; case $a in *=@*) unread=1 ;; esac ;;
+      --input) skip=i ;;
+      --input=*) write=1; unread=1 ;;
+      -H|--header) skip=h ;;
+      --header=*) case ${a#*=} in [Aa]ccept:*) ;; *) write=1 ;; esac ;;
+      -H?*) case ${a#-H} in [Aa]ccept:*) ;; *) write=1 ;; esac ;;
+      --*=*) has "$API_VAL" "${a%%=*}" || return 1 ;;
+      --*|-?) if has "$API_VAL" "$a"; then skip=v; elif ! has "$API_BOOL" "$a"; then return 1; fi ;;
+      -*) has "$API_VAL" "${a:0:2}" || return 1 ;;
+      *) pos+=("$a") ;;
+    esac
+  done
+  [ "${#pos[@]}" -le 1 ] || return 1
+  path=${pos[0]:-}
+  if [ -z "$write" ]; then
+    case ${meth:-GET} in GET|get) return 0 ;; esac
+  fi
+  norm "$path" || return 1
+  low=$(printf '%s' "$fields" | tr 'A-Z' 'a-z')
+  k=0
+  while [ "$k" -lt "${#NSEG[@]}" ]; do
+    case ${NSEG[$k]} in
+      graphql)
+        [ -z "$unread" ] || return 1
+        case $low in *mutation*|*subscription*) return 1 ;; esac ;;
+      issues)
+        nxt=${NSEG[$((k + 1))]:-}
+        [ "$nxt" = comments ] && return 1
+        if [ "${NSEG[$((k + 2))]:-}" = comments ]; then
+          t=$(num "$nxt"); { [ "$t" != '?' ] && [ "$t" != "$tracker" ]; } || return 1
+        fi ;;
+    esac
+    k=$((k + 1))
+  done
+  return 0
+}
+gate() {
+  case ${1-} in
+    '') return 0 ;;
+    --version|--help|-h) [ $# -eq 1 ] ;;
+    -*) return 1 ;;
+    api) api_gate "$@" ;;
+    issue) issue_gate "$@" ;;
+    pr) pr_gate "$@" ;;
+    workflow|release|run|repo|label|auth|secret|variable|cache|config|gist|ssh-key|gpg-key|codespace|project|ruleset|org|search|browse|status|completion|help|version|attestation) return 0 ;;
+    *) return 1 ;;
+  esac
+}
+gate "$@" || hit=1
+if [ -n "${hit:-}" ]; then
+  gcp=$(ps -o args= -p "$PPID" </dev/null 2>/dev/null | tr -c '[:print:]' ' ')
+  set -f; read -r -a gw <<< "$gcp"; set +f
+  ok=
+  # python's own option table (as the parent field above reads it): the script is the first
+  # word that is not an option nor an option's value; -c, -m and any option unknown end it
+  case ${gw[0]##*/} in python|python[0-9]*)
+    i=1 script=
+    while [ "$i" -lt "${#gw[@]}" ]; do
+      w=${gw[$i]}
+      case $w in
+        --*) break ;;
+        -?*)
+          j=1
+          while [ "$j" -lt "${#w}" ]; do
+            case ${w:$j:1} in
+              [bBdEhiIOqPRSuvVx]) ;;
+              [WX]) [ "$((j + 1))" -eq "${#w}" ] && i=$((i + 1)); break ;;
+              *) break 2 ;;
+            esac
+            j=$((j + 1))
+          done ;;
+        *) script=$w; break ;;
+      esac
+      i=$((i + 1))
+    done
+    if [ -n "$script" ] && [ -n "$gcpy" ]; then
+      a=$(rp "$script") && b=$(rp "$gcpy") && [ "$a" = "$b" ] && ok=1
+    fi ;;
+  esac
+  [ -n "$ok" ] || { echo "gh shim: a comment write on #$tracker goes through tools/pr/gh_comment.py (its mandate guard refuses a post that voids a mandate); refused" >&2; exit 1; }
+fi
+
 exec "$real" "$@"
diff --git a/tools/policy/budget_raise_gate.py b/tools/policy/budget_raise_gate.py
index c6da73c01..c022032cf 100644
--- a/tools/policy/budget_raise_gate.py
+++ b/tools/policy/budget_raise_gate.py
@@ -522,14 +522,18 @@ def justified(body, score_fn=None) -> tuple[bool, str]:
     return ok, why
 
 
-def check_body(body, raises: list[str] | None = None) -> tuple[bool, str]:
+def check_body(body, raises: list[str] | None = None, score_fn=None) -> tuple[bool, str]:
     """(ok, why) for `--check-body`: what a mandated approval of this body
     would meet at merge. `raises` is raises_between's reading of the diff, or
     None when no diff was named. A section present is judged by justification()
     whatever the diff; with none, a diff that raises a cap is refused (the
-    train refuses it identically) and one that raises nothing owes nothing."""
+    train refuses it identically) and one that raises nothing owes nothing.
+    A diff that raises a cap and a section that is well formed are also judged
+    against `score_fn() -> report line` (justified), the figure the gate and the
+    train read at merge; a diff that raises nothing is never mandated, so its
+    section is shape-checked alone."""
     if raises is None or _heading_at(str(body or "").splitlines()):
-        return justification(body)
+        return justified(body, score_fn) if raises else justification(body)
     if raises:
         return False, (f"the diff raises {len(raises)} cap(s) ({'; '.join(raises)}) and the body has no "
                        f"`{JUSTIFICATION_HEADING}` section, which a mandated raise owes")
@@ -1536,6 +1540,7 @@ def _end_to_end() -> list[tuple[str, object, object]]:
                 f.write(text)
             return run(head, argv=["--check-body", bodyf, "--base", base_, "--head", head])
         bare = "## Summary\n\nx\n"
+        planted_body = just["body"].replace("+0.0000 NULL", "+0.0012 IMPROVES")
         rc_, text, calls = check_body_run(raise_, bare)
         out.append(("e2e: --check-body: a raise whose body has no section exits 1, names the raise, asks nothing",
                     (rc_, "cut_views: 110 -> 111" in text, JUSTIFICATION_HEADING in text, calls), (1, True, True, [])))
@@ -1543,6 +1548,14 @@ def _end_to_end() -> list[tuple[str, object, object]]:
         out.append(("e2e: --check-body: ... a routine edit with no section exits 0 (null control)", rc_, 0))
         rc_, _, _ = check_body_run(raise_, just["body"])
         out.append(("e2e: --check-body: ... a raise with a well-formed section exits 0", rc_, 0))
+        # The value, not only the shape (#3045 round 1): the stub scorer measures
+        # dS +0.0000 NULL, so a body quoting +0.0012 IMPROVES is refused on a raise
+        # and a body quoting the measured figure is not (just["body"], above).
+        rc_, text, _ = check_body_run(raise_, planted_body)
+        out.append(("e2e: --check-body: a raise whose body quotes a dS the scorer did not measure exits 1 and says so",
+                    (rc_, "measures dS +0.0000 NULL" in text), (1, True)))
+        rc_, _, _ = check_body_run(routine, planted_body)
+        out.append(("e2e: --check-body: ... the same body on a diff that raises nothing is shape-checked alone (null control)", rc_, 0))
         rc_, text, _ = check_body_run(routine, just["body"].replace(" NULL", ""))
         out.append(("e2e: --check-body: a malformed section is refused on a diff that raises nothing",
                     (rc_, "Architecture score" in text), (1, True)))
@@ -1585,7 +1598,12 @@ def main(argv: list[str]) -> int:
                 print(f"the diff {rest['--base'][:12]}...{rest['--head'][:12]} could not be read "
                       f"({(e.stderr or '').strip()[:120] or f'git exited {e.returncode}'})")
                 return 2
-        ok, why = check_body(body, raises)
+        try:
+            ok, why = check_body(body, raises, (lambda: measured_score(rest["--base"], rest["--head"])) if rest else None)
+        except (RuntimeError, subprocess.CalledProcessError, OSError) as e:
+            print(f"the architecture score could not be measured ({str(e).splitlines()[0][:160] if str(e) else type(e).__name__}), "
+                  "and an unread figure supports no claim")
+            return 2
         print(why)
         return 0 if ok else 1
     args = dict(zip(argv[::2], argv[1::2]))

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
