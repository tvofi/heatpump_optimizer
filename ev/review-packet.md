# Review packet #3012
head: 883e8452fafbef8ecc6c686924e27c054f85bf54
base: a9ba3022e32178c5fb4376b4f333be88544ce94d

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124287875043 neutral
arch-score / arch-score id=124287673740 success
arm id=124289783800 skipped
budget-raise-gate / budget-raise-gate id=124287673701 success
cancel-superseded id=124287534236 success
codeql / Analyze (actions) id=124287673613 success
codeql / Analyze (javascript-typescript) id=124287673612 success
codeql / Analyze (python) id=124287673677 in_progress
governance / delivery-status id=124287673786 success
governance / delivery-status-publish id=124290035646 skipped
governance / env-matrix id=124287673836 success
governance / instrument-self-tests id=124287673780 in_progress
governance / policy-docs id=124287673731 success
governance / record id=124290174860 skipped
governance / wave-script id=124287673751 success
hassfest / hassfest id=124287673569 success
kernel-points id=124289784722 skipped
prelude id=124287534210 success
refresh id=124287533867 success
tests / arch-instrument id=124287876519 success
tests / briefs id=124287673684 success
tests / browser id=124287876527 success
tests / claims-autofix id=124294348307 skipped
tests / closure-scope id=124287673767 success
tests / closures id=124287876686 in_progress
tests / coverage id=124287876583 in_progress
tests / fast (3.14) id=124287876567 success
tests / mutation id=124287673691 success
tests / mutation-autofix id=124290343884 skipped
tests / mutation-pins id=124290268655 skipped
tests / nightly-ha id=124290363720 skipped
tests / nightly-status id=124287673674 success
tests / replay id=124290512026 skipped
tests / typing id=124287876543 success
validate / validate-hacs id=124287673588 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
NOTE body item af6e436a: R10-FLOW-DESIGN-STAGES
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/audit/seat/cloud_dispatch.py --self-test
             `tools/audit/seat/cloud_dispatch.py` is in the tree at this head
  ok         python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         bash tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_flow_dispatch_mutants.py
             `dev/audit/harnesses/r10_flow_dispatch_mutants.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_dispatch-1
             `dev/audit/harnesses/r10_seat_selftests_mutants.py` is in the tree at this head

FIGURES: 6 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_flow_dispatch_mutants.py b/dev/audit/harnesses/r10_flow_dispatch_mutants.py
index 0e17361dc..749fa1894 100644
--- a/dev/audit/harnesses/r10_flow_dispatch_mutants.py
+++ b/dev/audit/harnesses/r10_flow_dispatch_mutants.py
@@ -54,14 +54,15 @@ F = ROOT / REL
 MUTANTS = [
     ("M0", None, None),
     ("tree-skip", "    if tip and _git(repo_dir, \"rev-parse\"", "    if False and _git(repo_dir, \"rev-parse\""),
-    ("brief-drop", 'brief=group.get("brief") or ""', 'brief=""'),
-    ("parent-drop", '*(["-p", tip[0]] if tip else [])', "*[]"),
+    ("brief-drop", 'brief=group_brief(group))', 'brief="")'),
+    ("parent-drop", '*(["-p", tip] if tip else [])', "*[]"),
     ("nonce-altered", "**args, nonce=nonce)\n    except Refusal:", "**args, nonce=nonce + \"0\")\n    except Refusal:"),
     ("topic-to-id", 'ref = dispatch_ref(role, topic, "")', 'ref = dispatch_ref(role, group_id, "")'),
     ("render-host-off", "    m = HOME.search(json.dumps(payload))", "    m = None"),
     ("privacy-off", "    if why:\n        raise Refusal(f\"the dispatch ref", "    if False:\n        raise Refusal(f\"the dispatch ref"),
     ("head-ignored", 'head or _git(repo_dir, "rev-parse", f"{HEAD_REF}', '_git(repo_dir, "rev-parse", f"{HEAD_REF}'),
-    ("prompt-wrong", '"PROMPT.md": prompt}', '"PROMPT.md": ""}'),
+    ("prompt-wrong", '"PAYLOAD.json": json.dumps(payload), "PROMPT.md": prompt}',
+     '"PAYLOAD.json": json.dumps(payload), "PROMPT.md": ""}'),
     ("roster-repo-ignored", 'repo=roster.get("repo") or known["repo"]', 'repo=known["repo"]'),
     ("roster-ref-main", "roster_ref = roster_lib.reader_ref(repo_dir, roster_ref)",
      "roster_ref = roster_ref or roster_lib.MAIN_REF"),
@@ -82,13 +83,15 @@ MUTANTS = [
     ("env-id-forwarded-as-none", '"env_id": "the environment id', '"env_id": None and "the environment id'),
     ("flag-unlisted", '    ap.add_argument("--out")\n', '    ap.add_argument("--out")\n    ap.add_argument("--extra")\n'),
     # R10-FLY-CACHE-PROMPTS: the pointer event, --publish, the wait cap, the role read list.
-    ("pointer-ref-dropped", "at origin ref {ref} (`git fetch origin {ref} && git show",
-     "at origin ref (`git fetch origin && git show"),
-    ("pointer-off", "text = (_pointer(role, repo, pr, head, topic, nonce, publish_ref) if publish_ref",
-     "text = (_pointer(role, repo, pr, head, topic, nonce, publish_ref) if False"),
+    # R10-FLOW-DESIGN-STAGES part 2 re-aimed pointer-ref-dropped at the pinned stub: a
+    # seat told to fetch the moving ref instead of the pinned commit must die.
+    ("pointer-ref-dropped", "of {ref} (`git fetch origin {pin} && \"\n            f\"git show {pin}:PROMPT.md",
+     "of {ref} (`git fetch origin {ref} && \"\n            f\"git show FETCH_HEAD:PROMPT.md"),
+    ("pointer-off", "text = (_pointer(role, repo, pr, head, topic, nonce, publish_ref, pin) if publish_ref",
+     "text = (_pointer(role, repo, pr, head, topic, nonce, publish_ref, pin) if False"),
     ("publish-ignored", "        if args.publish:", "        if False:"),
     ("publish-ref-rev-dropped", 'key = topic or (f"rev-{pr}"', 'key = topic or (f"{pr}"'),
-    ("wait-line-dropped", '"and no timeout. " + WAIT_LINE)', '"and no timeout.")'),
+    ("wait-line-dropped", 'Monitor and no timeout. " + WAIT_LINE)', 'Monitor and no timeout.")'),
     ("claude-md-reread", "roles/fixer.md from main, and follow it exactly",
      "roles/fixer.md and CLAUDE.md from main, and follow them exactly"),
     ("cli-pr-truncated", 'head=args.head or "", pr=args.pr,', "head=args.head or \"\", pr=(args.pr or '')[:1],"),
diff --git a/dev/audit/harnesses/r10_seat_selftests_mutants.py b/dev/audit/harnesses/r10_seat_selftests_mutants.py
index 207b354f3..b7a463a43 100644
--- a/dev/audit/harnesses/r10_seat_selftests_mutants.py
+++ b/dev/audit/harnesses/r10_seat_selftests_mutants.py
@@ -65,6 +65,47 @@ MUTANTS = [
     ("ci-watch-2", "ci-watch.sh", '($2 == "completed" && $3 != "success")', '($3 == "failure")'),
     ("S02", "cloud_dispatch.py", "return len(head) == 40 and set(head) <= LOWER_HEX",
      "return len(head) != 40 and set(head) <= LOWER_HEX"),
+    # r10-flow-design-stages-p2 A: the stub pins PROMPT.md's commit, keeps the footer ban,
+    # re-dispatches without moving, and refuses a stub with no pin.
+    ("cloud_dispatch-1", "cloud_dispatch.py", "pin=_snapshot(repo_dir, ref, prompt))",
+     'pin=_tip(repo_dir, ref) or "0" * 40)'),
+    ("cloud_dispatch-2", "cloud_dispatch.py", 'nonce) + " " + FOOTER_BAN + "\\n"\n            f"Your full brief',
+     'nonce) + "\\n"\n            f"Your full brief'),
+    ("cloud_dispatch-3", "cloud_dispatch.py", "            return parent[0]\n", "            pass\n"),
+    ("cloud_dispatch-4", "cloud_dispatch.py", "if publish_ref and not is_head(pin):", "if False:"),
+    # r10-flow-design-stages-p2 B: a group's carries reach its PROMPT.md.
+    ("cloud_dispatch-5", "cloud_dispatch.py",
+     '    parts += [f"Carry {i}: {c}" for i, c in enumerate(group.get("carry") or [])]\n', ""),
+    # r10-flow-design-stages-p2 C: the fixer's step ref, its delete, the pre-handoff merge, the identity pin.
+    ("cloud_dispatch-6", "cloud_dispatch.py", 'fast-forward only, to refs/heads/{WIP_NS}/{topic} before',
+     'fast-forward only, to refs/heads/handoff/{topic} before'),
+    ("cloud_dispatch-7", "cloud_dispatch.py", 'delete the step ref: `git push origin :refs/heads/{WIP_NS}/{topic}`. ', ""),
+    ("cloud_dispatch-8", "cloud_dispatch.py", "run, `git merge origin/main`, rerun", "run, rerun"),
+    ("cloud_dispatch-9", "cloud_dispatch.py", 'if role in COMMITTING_ROLES else ""', 'if False else ""'),
+    # r10-flow-design-stages-p2 D: the reviewer's one CI waiter that ends.
+    ("cloud_dispatch-10", "cloud_dispatch.py",
+     "Wait for CI on this head only by re-running \"\n            f\"`python3 tools/audit/seat/merge_train.py classify {head}`",
+     "Wait for CI on this head \"\n            f\"somehow"),
+    # r10-flow-design-stages-p2 E: the setup line's toolchain check.
+    ("cloud_dispatch-11", "cloud_dispatch.py",
+     'f"`{SETUP_CHECK}`, and on REFUSE stop: report its line as your result and start no work. "', '""'),
+    # r10-flow-design-stages-p2 F: the roster's model ruling, enforced at the dispatch.
+    ("cloud_dispatch-12", "cloud_dispatch.py", "if not ruled or _family(model) == _family(ruled):", "if True:"),
+    ("cloud_dispatch-13", "cloud_dispatch.py", "if not ruled or _family(model) == _family(ruled):", "if not ruled:"),
+    # r10-flow-design-stages-p2 I: the design arms #2994 merged (decision 0014), one predicate each.
+    ("cloud_dispatch-14", "cloud_dispatch.py",
+     'if role == "fixer" and roster_lib.needs_design(group) and not design_exempt.strip():',
+     'if role == "fixer" and roster_lib.needs_design(group):'),
+    ("cloud_dispatch-15", "cloud_dispatch.py", "if not design_approved(repo_dir, group_id):", "if False:"),
+    ("cloud_dispatch-16", "cloud_dispatch.py", 'return first == f"Design review: approve {tip}"',
+     'return first.startswith("Design review: approve ")'),
+    ("cloud_dispatch-17", "cloud_dispatch.py", "if role in DESIGN_ROLES and not roster_lib.needs_design(group):",
+     "if False:"),
+    ("cloud_dispatch-18", "cloud_dispatch.py", "        if not design:\n", "        if False:\n"),
+    ("cloud_dispatch-19", "cloud_dispatch.py", 'if role == "design-reviewer" and not is_head(design or ""):',
+     "if False:"),
+    ("cloud_dispatch-20", "cloud_dispatch.py", "topic = group_id if role in DESIGN_ROLES else _topic_of(group)",
+     "topic = _topic_of(group)"),
     ("S03", "cloud_relay.sh", 'if [ -f "$led" ] && grep -qxF "$ref $sha" "$led"; then',
      'if [ -f "$led" ] && ! grep -qxF "$ref $sha" "$led"; then'),
     ("S04", "daemonize.py", '"-u" not in run_argv[1:2]:', '"-u" in run_argv[1:2]:'),
diff --git a/dev/programme/delivery/3012.md b/dev/programme/delivery/3012.md
new file mode 100644
index 000000000..b6f94c5ad
--- /dev/null
+++ b/dev/programme/delivery/3012.md
@@ -0,0 +1 @@
+- [#3012](https://github.com/tvofi/heatpump_optimizer/pull/3012) — **open**, R10-FLOW-DESIGN-STAGES part 2: payload stub and carries in the dispatch (R10-FLOW-DESIGN-STAGES)
diff --git a/tools/audit/seat/cloud_dispatch.py b/tools/audit/seat/cloud_dispatch.py
index 1c4b5fa99..5346afba2 100644
--- a/tools/audit/seat/cloud_dispatch.py
+++ b/tools/audit/seat/cloud_dispatch.py
@@ -10,8 +10,8 @@
 
 THE GROUP PATH (`--group`, or `dispatch_group()` for a caller that hosts it) takes
 a role, a roster group and a model. The roster at REF (default: the round's
-roster branch, roster_lib.default_roster_ref) gives the brief, the topic (the
-group's branch) and the repository; the head is --head, else origin/main's tip,
+roster branch, roster_lib.default_roster_ref) gives the brief (`group_brief`: its
+brief, `After:` and carries), the topic (the group's branch) and the repository; the head is --head, else origin/main's tip,
 never the roster ref's (a seat forks from main, not from the roster branch); a
 reviewer needs --head (the PR head) and takes its nonce from `bus.sh dispatch`, which
 mints one or re-records --nonce; the environment id comes from the overlay /
@@ -19,8 +19,11 @@ $HPO_CLOUD_ENV_ID. The
 payload is rendered by the same `publish_seat` as the flag path's --publish, so it
 is that path's byte for byte, and is published, with its prompt, on origin as
 `dispatch/<role>-<topic>` (PAYLOAD.json, PROMPT.md); the one line printed is that
-ref name. A published payload's event is a pointer to PROMPT.md on the ref, never
-the prompt itself (the runner echoes the event; R10-FLY-CACHE-PROMPTS). --publish
+ref name. A published payload's event is a stub, never the prompt itself (the
+runner echoes the event; R10-FLY-CACHE-PROMPTS): the seat line, the footer ban,
+and the commit holding PROMPT.md, pinned by SHA, never by the moving ref. The
+prompt is committed first, alone, and PAYLOAD.json on top of it, since a commit
+cannot name its own SHA. --publish
 does the same on the flag path, to `dispatch/<role>-<topic>`, else
 `dispatch/<role>-rev-<PR>`, and prints the payload as without it. A standing trigger whose prompt fetches the ref it is fired with
 needs nothing else. A render refusal (below) pushes nothing.
@@ -38,8 +41,9 @@ $HPO_CLOUD_OVERLAY, a JSON object with `environment_id`, `model`, `repo`), else
 $HPO_CLOUD_ENV_ID / $HPO_CLOUD_MODEL / $HPO_CLOUD_REPO. One of the three is
 required: a missing value is a refusal, not a default that goes stale.
 
-THE BRIEF is read and INLINED at render time, because the runner snapshots the
-message at `run`: a brief edited afterwards reaches no running seat.
+THE BRIEF is read and INLINED at render time, into the event or, published, into
+PROMPT.md at the pinned commit: either way a brief edited afterwards reaches no
+running seat, since a re-dispatch only moves the ref past that commit.
 
 WHAT IT REFUSES (exit 2, nothing printed on stdout):
   * a head that is not exactly 40 lowercase hex digits;
@@ -51,7 +55,8 @@ WHAT IT REFUSES (exit 2, nothing printed on stdout):
     host-path grammar): the payload is published to the runner, and a seat's
     prompt may not name the machine it was written on;
   * an unreadable brief;
-  * with --group: a group the roster does not name, a roster that cannot be read,
+  * with --group: a model outside the family the roster rules for the role
+    (`model_refusal`), a group the roster does not name, a roster that cannot be read,
     a reviewer without --head, a ref name that would publish the host
     (ref_privacy.refusal), and any flag the group path does not consume
     (--topic, --brief, --repo, --env-id, --out; GROUP_FLAGS gives each its reason).
@@ -106,6 +111,21 @@ FOOTER_BAN = ("Write no Claude Code footer, no Co-Authored-By or Claude-Session
               "with `git log --format=%B` before pushing.")
 
 
+#: The identity a dispatch commit and a writing seat's own commits carry: a noreply
+#: address, which ref_privacy's host-email class passes, never the host's default.
+SEAT_NAME, SEAT_EMAIL = "seat", "seat@users.noreply.github.com"
+#: The roles that commit in their own checkout, and so pin that identity first.
+COMMITTING_ROLES = ("fixer", "probe")
+#: Where a cloud fixer pushes each verified step (`<WIP_NS>/<topic>`), so an idle
+#: container holds no unpushed work. Neither cloud_relay.sh's handoff arm nor
+#: `bus.sh orphans` lists the prefix, so a step push moves no pull request.
+WIP_NS = "handoff-wip"
+
+
+#: The toolchain check a seat runs before any work (#2709): REFUSE stops the seat.
+SETUP_CHECK = "bash tools/audit/seat/cloud-setup.sh --check"
+
+
 #: A seat's prompt cache lives 5 min: a wait past it rewrites the whole context on
 #: the next turn (R10-FLY-CACHE-PROMPTS). 240 s stays under it; GitHub's 60 s poll
 #: floor stays the lower bound.
@@ -116,6 +136,30 @@ class Refusal(Exception):
     pass
 
 
+#: The roster key a role's model is ruled under: the group's `model` table, else its
+#: `<key>Model` field (roster_lib's shape). The values are the roster's, routed by
+#: judgement per group (tvofi 2026-10-24 card 9); this table only names the key. A
+#: role with no key (the probe, the design steps) has no ruling to enforce.
+MODEL_KEY = {"fixer": "fixer", "reviewer": "reviewer"}
+
+
+def _family(model: str) -> str:
+    """`claude-sonnet-5-5` and `sonnet` are one model family; an unknown name is itself."""
+    m = re.search(r"haiku|sonnet|opus|fable", model.lower())
+    return m.group(0) if m else model.lower()
+
+
+def model_refusal(role: str, group: dict, model: str) -> str | None:
+    """Why `model` may not run `role` for `group`, in one line, or None when the roster
+    rules no model for it or the model is of the family it rules."""
+    key = MODEL_KEY.get(role)
+    table = group.get("model") if isinstance(group.get("model"), dict) else {}
+    ruled = key and (table.get(key) or group.get(f"{key}Model"))
+    if not ruled or _family(model) == _family(ruled):
+        return None
+    return f"{group.get('group')} rules {ruled} for its {role} (roster model.{key}); --model {model} is not {ruled}"
+
+
 def _seat_line(role: str, repo: str, pr: str, head: str, topic: str, nonce: str) -> str:
     who = {"reviewer": "CLOUD REVIEWER", "fixer": "CLOUD FIXER", "probe": "CLOUD PROBE",
            "designer": "CLOUD DESIGNER", "design-reviewer": "CLOUD DESIGN REVIEWER"}[role]
@@ -126,21 +170,27 @@ def _seat_line(role: str, repo: str, pr: str, head: str, topic: str, nonce: str)
     return first + " Never send push notifications."
 
 
-def _pointer(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, ref: str) -> str:
-    """The event a published seat is fired with: who it is, and where its prompt is.
-    The runner echoes the event into every view of the trigger, so the whole prompt
-    there was paid for several times over; PROMPT.md on the ref is paid once."""
-    return (_seat_line(role, repo, pr, head, topic, nonce) + "\n"
-            f"Your full brief is PROMPT.md at origin ref {ref} (`git fetch origin {ref} && git show "
-            "FETCH_HEAD:PROMPT.md`); read it first and follow it exactly.\n")
+def _pointer(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, ref: str, pin: str) -> str:
+    """The event a published seat is fired with: who it is, the footer ban, and the
+    commit its prompt is at. The runner echoes the event into every view of the
+    trigger, so the whole prompt there was paid for several times over; PROMPT.md is
+    paid once. `pin` is a SHA, never `ref`: a re-dispatch moves the ref, and a
+    running seat's brief may not move with it."""
+    return (_seat_line(role, repo, pr, head, topic, nonce) + " " + FOOTER_BAN + "\n"
+            f"Your full brief is PROMPT.md at commit {pin} of {ref} (`git fetch origin {pin} && "
+            f"git show {pin}:PROMPT.md`); read it first and follow it exactly.\n")
 
 
 def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, brief: str,
             design: str = "") -> str:
     first = _seat_line(role, repo, pr, head, topic, nonce) + " " + FOOTER_BAN
-    setup = ("Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line "
+    pin = (f"Before any commit, pin the seat identity: `git config user.name {SEAT_NAME} && git config "
+           f"user.email {SEAT_EMAIL}`. ") if role in COMMITTING_ROLES else ""
+    setup = ("Setup: `git fetch --unshallow --tags origin`. " + pin + "The session-start `toolchain:` line "
              "says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with "
-             "`eval \"$(bash .claude/hooks/session-start.sh --env-lines)\"`. Run anything heavy in "
+             "`eval \"$(bash .claude/hooks/session-start.sh --env-lines)\"`. Then run "
+             f"`{SETUP_CHECK}`, and on REFUSE stop: report its line as your result and start no work. "
+             "Run anything heavy in "
              "the background with Monitor and no timeout. " + WAIT_LINE)
     if role == "reviewer":
         body = (
@@ -153,7 +203,12 @@ def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, br
             "written unless the signal is `host-path`; re-read the live checks either way. "
             "Verify each claim adversarially: mutate the fix and check the tests fail, and check "
             "every figure in the body at this head. Check that it merges with origin/main "
-            "(`git merge-tree --write-tree`) and read CI on this head from the check-runs API.\n"
+            "(`git merge-tree --write-tree`). Wait for CI on this head only by re-running "
+            f"`python3 tools/audit/seat/merge_train.py classify {head}` in the background, at least 60 s "
+            "between runs, until it exits 0 (GREEN), 1 (RED) or 2 (unreadable: say so in the verdict); "
+            "3 is WAIT, so run it again. Never wait with `pgrep` or `pkill`, whose `-f` pattern matches "
+            "the waiter's own command line, nor on a context the ruleset does not require, such as "
+            "`prelude`.\n"
             f"Output: in a fresh directory of your own (`W=$(mktemp -d)`), write verdict.md, whose first line is "
             f"exactly `Fix review: merge {head}` or `Fix review: blocked {head} <class>: <reason>` (no brackets; "
             f"the class is lower-case letters and dashes), in the format the role file gives, "
@@ -175,17 +230,24 @@ def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, br
             f"parentless commit with a private index and touches no branch of your checkout: "
             f"`R=$(git rev-parse --show-toplevel); G=$(git rev-parse --absolute-git-dir); mkdir -p $W/pr && "
             f"cp -r $W/verdict.md $W/ev $W/pr/ && cd $W/pr && T=$(GIT_DIR=$G GIT_INDEX_FILE=$W/idx GIT_WORK_TREE=$W/pr "
-            f"sh -c 'git add -A -f . && git write-tree') && C=$(GIT_DIR=$G git -c user.name=seat "
-            f"-c user.email=seat@users.noreply.github.com commit-tree $T -m \"verdict {pr} {head}\") && "
+            f"sh -c 'git add -A -f . && git write-tree') && C=$(GIT_DIR=$G git -c user.name={SEAT_NAME} "
+            f"-c user.email={SEAT_EMAIL} commit-tree $T -m \"verdict {pr} {head}\") && "
             f"git -C $R push -q origin $C:refs/heads/probe/rev-{pr}-{nonce.strip()[:8]}`. "
             "That ref is the return signal. Do not post comments, approve or merge.")
     elif role == "fixer":
         body = (
             "Role: read dev/governance/roles/fixer.md from main, and follow it exactly, "
             f"in a worktree of your own cut from origin/main. Fetch {head} for the base you were given.\n"
-            f"Output: push the code to refs/heads/handoff/{topic}, then write the PR body and run "
+            f"Output: push each verified step, fast-forward only, to refs/heads/{WIP_NS}/{topic} before "
+            f"any wait on a background run, so an idle container loses nothing; never step-push to "
+            f"handoff/{topic}, whose move updates the pull request. Before the handoff, when origin/main "
+            "has moved since your last `tools/pr/prepr.sh` run, `git merge origin/main`, rerun "
+            "`tools/pr/prepr.sh` (the body check included) and fix what it refuses; hand off only on a "
+            "clean run (an unmoved main needs no second run: say so in the body). Then push the code to "
+            f"refs/heads/handoff/{topic}, then write the PR body and run "
             f"`bash tools/audit/seat/body_push.sh {topic} <body.md>`, which pushes "
-            f"refs/heads/handoff-body/{topic}; that second push is the return signal. Push nothing "
+            f"refs/heads/handoff-body/{topic}; that second push is the return signal. Once it succeeds, "
+            f"delete the step ref: `git push origin :refs/heads/{WIP_NS}/{topic}`. Push nothing "
             "else, open no pull request and write no delivery row. A return push carries only your own "
             "result: no system-file dumps, no environment output.")
     elif role == "designer":
@@ -216,7 +278,8 @@ def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, br
             f"Output: write your result as a body file and run `bash tools/audit/seat/body_push.sh "
             f"{topic} <result.md>`, which pushes refs/heads/handoff-body/{topic}; that push is the "
             "return signal. A return push carries only your own result tokens.")
-    tail = ("Never write to any branch except your return refs. Never work around a hook or a refusal; "
+    refs = f"your return refs and refs/heads/{WIP_NS}/{topic}" if role == "fixer" else "your return refs"
+    tail = (f"Never write to any branch except {refs}. Never work around a hook or a refusal; "
             "report it in your result instead.")
     text = "\n".join([first, setup, body, tail]) + "\n"
     if brief:
@@ -226,8 +289,9 @@ def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, br
 
 def render(role: str, head: str, *, env_id: str, model: str, repo: str, pr: str = "",
            topic: str = "", nonce: str = "", brief: str = "", publish_ref: str = "",
-           design: str = "") -> dict:
-    """The payload; with `publish_ref`, its event is the pointer to that ref (`publish_seat`)."""
+           design: str = "", pin: str = "") -> dict:
+    """The payload; with `publish_ref`, its event is the stub naming PROMPT.md at commit
+    `pin` of that ref (`publish_seat`)."""
     if role not in ROLES:
         raise Refusal(f"role must be one of {', '.join(ROLES)}")
     if not is_head(head or ""):
@@ -246,7 +310,9 @@ def render(role: str, head: str, *, env_id: str, model: str, repo: str, pr: str
             raise Refusal(f"no {name}: pass a flag, an overlay entry or its HPO_CLOUD_* variable")
     if not re.fullmatch(r"[\w.-]+/[\w.-]+", repo):
         raise Refusal("repo must be OWNER/NAME")
-    text = (_pointer(role, repo, pr, head, topic, nonce, publish_ref) if publish_ref
+    if publish_ref and not is_head(pin):
+        raise Refusal("a published seat's stub needs the 40-hex commit holding its PROMPT.md")
+    text = (_pointer(role, repo, pr, head, topic, nonce, publish_ref, pin) if publish_ref
             else _prompt(role, repo, pr, head, topic, nonce, brief, design))
     payload = {"job_config": {"ccr": {
         "environment_id": env_id,
@@ -276,7 +342,7 @@ DISPATCH_NS = "dispatch"
 #: ref, whose tip is the roster branch a fixer must not fork from.
 HEAD_REF = roster_lib.MAIN_REF
 #: Identity of the commit that carries a dispatch (a constant, never the host's).
-_SEAT = ("-c", "user.name=seat", "-c", "user.email=seat@users.noreply.github.com")
+_SEAT = ("-c", f"user.name={SEAT_NAME}", "-c", f"user.email={SEAT_EMAIL}")
 
 
 def _git(repo_dir: str, *argv: str, stdin: str | None = None) -> str:
@@ -291,27 +357,62 @@ def _topic_of(group: dict) -> str:
     return roster_lib.branch_of(group).removeprefix("handoff/")
 
 
-def _publish(repo_dir: str, ref: str, files: dict[str, str]) -> None:
-    """Append one commit holding `files` to `refs/heads/<ref>` on origin.
-
-    The first commit has no parent; later ones fast-forward, so a re-dispatch
-    needs no force-push. An identical tree adds no commit. A fetch that fails
-    for any reason but a missing ref refuses: a parentless commit would only be
-    refused by the push as a non-fast-forward, never rewritten."""
+def _tip(repo_dir: str, ref: str) -> str:
+    """The tip of `refs/heads/<ref>` on origin, fetched, or "" when there is none.
+    A ref that would publish the host refuses before anything is read or pushed."""
     why = ref_privacy.refusal(ref, (("the dispatch message", f"dispatch: {ref}"),))
     if why:
         raise Refusal(f"the dispatch ref would publish the host: {why}")
     tip = _git(repo_dir, "ls-remote", "origin", f"refs/heads/{ref}").split()[:1]
     if tip:
         _git(repo_dir, "fetch", "-q", "origin", f"refs/heads/{ref}")
+    return tip[0] if tip else ""
+
+
+def _tree(repo_dir: str, files: dict[str, str]) -> str:
     entries = "".join(f"100644 blob {_git(repo_dir, 'hash-object', '-w', '--stdin', stdin=text).strip()}\t{name}\n"
                       for name, text in sorted(files.items()))
-    tree = _git(repo_dir, "mktree", stdin=entries).strip()
-    if tip and _git(repo_dir, "rev-parse", f"{tip[0]}^{{tree}}").strip() == tree:
-        return
-    commit = _git(repo_dir, *_SEAT, "commit-tree", tree, *(["-p", tip[0]] if tip else []),
+    return _git(repo_dir, "mktree", stdin=entries).strip()
+
+
+def _publish(repo_dir: str, ref: str, files: dict[str, str]) -> str:
+    """Append one commit holding `files` to `refs/heads/<ref>` on origin; return the tip.
+
+    The first commit has no parent; later ones fast-forward, so a re-dispatch
+    needs no force-push. An identical tree adds no commit. A fetch that fails
+    for any reason but a missing ref refuses: a parentless commit would only be
+    refused by the push as a non-fast-forward, never rewritten."""
+    tip = _tip(repo_dir, ref)
+    tree = _tree(repo_dir, files)
+    if tip and _git(repo_dir, "rev-parse", f"{tip}^{{tree}}").strip() == tree:
+        return tip
+    commit = _git(repo_dir, *_SEAT, "commit-tree", tree, *(["-p", tip] if tip else []),
                   "-m", f"dispatch: {ref}").strip()
     _git(repo_dir, "push", "-q", "origin", f"{commit}:refs/heads/{ref}")
+    return commit
+
+
+def _snapshot(repo_dir: str, ref: str, prompt: str) -> str:
+    """The commit of `ref` holding PROMPT.md alone, which a stub pins: the tip's parent
+    when the tip already publishes this prompt over it (a re-dispatch moves nothing),
+    else a new commit appended to the ref."""
+    tip = _tip(repo_dir, ref)
+    if tip:
+        parent = _git(repo_dir, "log", "-1", "--format=%P", tip).split()[:1]
+        if parent and _git(repo_dir, "rev-parse", f"{parent[0]}^{{tree}}").strip() == _tree(
+                repo_dir, {"PROMPT.md": prompt}) and _git(repo_dir, "rev-parse", f"{tip}:PROMPT.md") \
+                == _git(repo_dir, "rev-parse", f"{parent[0]}:PROMPT.md"):
+            return parent[0]
+    return _publish(repo_dir, ref, {"PROMPT.md": prompt})
+
+
+def group_brief(group: dict) -> str:
+    """What a group's seat is briefed with: the roster brief, then `After:` the groups it
+    follows, then each carry as `Carry <i>:`, verbatim, `<i>` its 0-based index in the
+    roster's list (the index a brief or a verdict cites a carry by)."""
+    parts = [(group.get("brief") or "").rstrip("\n"), "After: " + (", ".join(group.get("after") or []) or "none")]
+    parts += [f"Carry {i}: {c}" for i, c in enumerate(group.get("carry") or [])]
+    return "\n\n".join(p for p in parts if p) + "\n"
 
 
 def dispatch_ref(role: str, topic: str, pr: str) -> str:
@@ -323,11 +424,13 @@ def dispatch_ref(role: str, topic: str, pr: str) -> str:
 
 
 def publish_seat(repo_dir: str, ref: str, role: str, head: str, **args) -> dict:
-    """Publish the seat's whole prompt as PROMPT.md, with the payload firing it, on `ref`;
-    return that payload, whose event is the pointer to the ref. Both render first, so
-    every `render` refusal pushes nothing."""
+    """Publish the seat's whole prompt as PROMPT.md on `ref`, then the payload firing it
+    on top; return that payload, whose event is the stub pinning the prompt's commit.
+    The prompt renders first, so every `render` refusal, the host-path one on the
+    published PROMPT.md included, pushes nothing; the stub adds only a ref, which
+    `_tip` judges before its first read."""
     prompt = render(role, head, **args)["job_config"]["ccr"]["events"][0]["data"]["message"]["content"]
-    payload = render(role, head, **args, publish_ref=ref)
+    payload = render(role, head, **args, publish_ref=ref, pin=_snapshot(repo_dir, ref, prompt))
     _publish(repo_dir, ref, {"PAYLOAD.json": json.dumps(payload), "PROMPT.md": prompt})
     return payload
 
@@ -375,6 +478,9 @@ def dispatch_group(role: str, group_id: str, model: str, *, repo_dir: str = ".",
     group = roster_lib.groups_of(roster).get(group_id)
     if group is None:
         raise Refusal(f"{group_id} is not a group of the roster at {roster_ref}")
+    why = model_refusal(role, group, model)
+    if why:
+        raise Refusal(why)
     environ = os.environ if environ is None else environ
     known = _config(argparse.Namespace(overlay=overlay, env_id=None, model=model, repo=None), environ)
     topic = group_id if role in DESIGN_ROLES else _topic_of(group)
@@ -393,7 +499,7 @@ def dispatch_group(role: str, group_id: str, model: str, *, repo_dir: str = ".",
         if not design:
             raise Refusal(f"no design/{group_id} on origin to review")
     args = dict(design=design, env_id=known["env_id"], model=model, repo=roster.get("repo") or known["repo"],
-                pr=pr, topic=topic, brief=group.get("brief") or "")
+                pr=pr, topic=topic, brief=group_brief(group))
     head = head or _git(repo_dir, "rev-parse", f"{HEAD_REF}^{{commit}}").strip()
     if role == "reviewer":
         render(role, head, **args, nonce=BUS_PROBE_NONCE)  # every other refusal, before the bus records
@@ -480,20 +586,28 @@ def _group_checks(check) -> None:
         grp = {"group": "R10-X", "brief": "Fix the thing in tools/x.py.\n", "resume": {"branch": "handoff/r10-x"}}
         bad = {"group": "R10-BAD", "brief": "cd " + users + "someone/work"}
         big = {"group": "R10-BIG", "size": "L", "brief": "Redesign tools/y.py.\n"}
-        land([grp, bad, big])
+        two = {"group": "R10-TWO", "brief": "Two things.\n", "after": ["R10-X", "R10-BIG"],
+               "carry": ["First, verbatim.", "Second; tools/z.py."]}
+        cbad = {"group": "R10-CBAD", "brief": "Clean.\n", "carry": ["fine", "cd " + users + "someone/work"]}
+        ruled = {"group": "R10-M", "brief": "Model.\n", "model": {"fixer": "sonnet", "reviewer": "opus"}}
+        legacy = {"group": "R10-L", "brief": "Legacy.\n", "fixerModel": "opus"}
+        land([grp, bad, big, two, cbad, ruled, legacy])
         git(work, "remote", "add", "origin", str(origin))
         tip = git(work, "rev-parse", "origin/main").strip()
 
-        def dispatch(group="R10-X", role="fixer", **kw):
+        def dispatch(group="R10-X", role="fixer", model="m-1", **kw):
             with contextlib.redirect_stderr(io.StringIO()):  # roster_lib's absent-branch note
-                return dispatch_group(role, group, "m-1", repo_dir=str(work), **{"environ": env, **kw})
+                return dispatch_group(role, group, model, repo_dir=str(work), **{"environ": env, **kw})
 
         def refused(*a, **kw):
+            return bool(reason(*a, **kw))
+
+        def reason(*a, **kw) -> str:  # the refusal's text, "" when the dispatch passed
             try:
                 dispatch(*a, **kw)
-            except Refusal:
-                return True
-            return False
+            except Refusal as e:
+                return str(e) or "refused"
+            return ""
 
         @contextlib.contextmanager
         def _env(extra):  # main() reads os.environ, as the orchestrator's shell gives it
@@ -519,7 +633,8 @@ def _group_checks(check) -> None:
               dispatch("R10-BIG", design_exempt="approved prototype on record") == "dispatch/fixer-r10-big")
         check("a designer for an S group is refused (only L and XL take a design)",
               refused("R10-X", "designer") and refused("R10-X", "design-reviewer"))
-        check("a design reviewer with no design/<group> to review is refused", refused("R10-BIG", "design-reviewer"))
+        check("a design reviewer with no design/<group> to review is refused, for that reason",
+              reason("R10-BIG", "design-reviewer") == "no design/R10-BIG on origin to review")
         ref = dispatch("R10-BIG", "designer")
         dtext = fetched(ref, "PROMPT.md")
         check("a designer's ref is dispatch/designer-<group>, pins the base SHA and names its contract",
@@ -545,7 +660,7 @@ def _group_checks(check) -> None:
         check("a fixer is dispatched once the verdict approves the current design tip (null control)",
               dispatch("R10-BIG") == "dispatch/fixer-r10-big")
         brief = work / "brief.txt"
-        brief.write_text(grp["brief"])
+        brief.write_text(group_brief(grp))  # what the group path briefs, so the two payloads can agree
         flags = ["--role", "fixer", "--head", tip, "--topic", "r10-x", "--brief", str(brief),
                  "--env-id", "env_x", "--model", "m-1", "--repo", "owner/name"]
         plain, old = io.StringIO(), io.StringIO()
@@ -558,13 +673,44 @@ def _group_checks(check) -> None:
         content = lambda text: json.loads(text)["job_config"]["ccr"]["events"][0]["data"]["message"]["content"]
         msg = fetched(line, "PROMPT.md")
         ptr = content(fetched(line, "PAYLOAD.json"))
-        check("the published payload's event is the pointer to the ref, under 600 chars; PROMPT.md is the prompt",
-              len(ptr) < 600 and f"origin ref {line} (`git fetch origin {line} && git show FETCH_HEAD:PROMPT.md`)"
-              in ptr and tip in ptr and msg.startswith("CLOUD FIXER") and msg not in ptr)
+        _pin = re.search(r"at commit ([0-9a-f]{40}) of ", ptr)
+        pin = _pin.group(1) if _pin else ""
+        check("the published event is a stub pinning the commit holding PROMPT.md by SHA, never the ref's tip",
+              pin and f"of {line} (`git fetch origin {pin} && git show {pin}:PROMPT.md`)" in ptr
+              and "FETCH_HEAD" not in ptr and git(work, "show", f"{pin}:PROMPT.md") == msg
+              and git(work, "rev-parse", "FETCH_HEAD^").strip() == pin)
+        check("the stub keeps the seat line and the footer ban inline; PROMPT.md is the whole prompt",
+              ptr.startswith("CLOUD FIXER seat for owner/name, topic r10-x, at head " + tip + ".")
+              and FOOTER_BAN in ptr and msg.startswith("CLOUD FIXER") and msg not in ptr)
+        check("the stub payload is far smaller than the prompt: under 1 KB whole, the brief absent, the SHA present",
+              len(fetched(line, "PAYLOAD.json")) < 1024 < len(msg) and "Fix the thing" not in ptr and pin in ptr)
         check("without --publish the flag path is unchanged: the whole prompt in its event, nothing published",
               rc0 == 0 and content(plain.getvalue()) == msg)
         check("the roster brief is inlined and the roster tip is the head",
               "Fix the thing in tools/x.py." in msg and tip in msg)
+        check("a group with no carry renders its brief and `After:` alone (the null control for the carries)",
+              msg.endswith("\nBrief (snapshotted when this payload was rendered):\n"
+                           "Fix the thing in tools/x.py.\n\nAfter: none\n") and "Carry " not in msg)
+        try:
+            dispatch("R10-M", model="claude-opus-5-5")
+            why = ""
+        except Refusal as e:
+            why = str(e)
+        check("a fixer on a model the roster does not rule for the group refuses, in one line naming both",
+              "R10-M rules sonnet for its fixer" in why and "claude-opus-5-5" in why and "\n" not in why
+              and "r10-m" not in git(work, "ls-remote", str(origin)))
+        check("a fixer on the ruled family passes, by full id or alias (null control)",
+              dispatch("R10-M", model="claude-sonnet-5-5") == dispatch("R10-M", model="sonnet") == "dispatch/fixer-r10-m")
+        check("the legacy <role>Model field rules where the model table is absent",
+              refused("R10-L", model="claude-sonnet-5-5") and dispatch("R10-L", model="claude-opus-5-5"))
+        check("a role the roster rules no model for is not checked (a probe on R10-M runs on any model)",
+              dispatch("R10-M", "probe", model="claude-haiku-5-5") == "dispatch/probe-r10-m")
+        twotext = fetched(dispatch("R10-TWO"), "PROMPT.md")
+        check("a group's two carries render numbered by roster index and verbatim, after its brief and `After:`",
+              twotext.endswith("Two things.\n\nAfter: R10-X, R10-BIG\n\nCarry 0: First, verbatim.\n\n"
+                               "Carry 1: Second; tools/z.py.\n"))
+        check("a host path inside a carry refuses as one in the brief does, and pushes nothing",
+              refused("R10-CBAD") and "r10-cbad" not in git(work, "ls-remote", str(origin)))
         check("a re-dispatch of the same brief moves no ref", dispatch() == line
               and git(work, "ls-remote", str(origin), "refs/heads/" + line).split()[0]
               == git(work, "rev-parse", "FETCH_HEAD").strip())
@@ -573,7 +719,12 @@ def _group_checks(check) -> None:
         dispatch()
         git(work, "fetch", "-q", str(origin), "refs/heads/" + line)
         check("a changed brief fast-forwards the ref",
-              git(work, "rev-parse", "FETCH_HEAD^").strip() == first and "Changed." in fetched(line, "PROMPT.md"))
+              git(work, "merge-base", "--is-ancestor", first, "FETCH_HEAD") == ""
+              and git(work, "rev-parse", "FETCH_HEAD").strip() != first and "Changed." in fetched(line, "PROMPT.md"))
+        stale = git(work, "show", f"{pin}:PROMPT.md")
+        check("a seat fired with the first stub still reads the first brief at its pinned commit after the re-dispatch",
+              "Fix the thing in tools/x.py." in stale and "Changed." not in stale
+              and pin not in content(fetched(line, "PAYLOAD.json")))
         check("the dispatch ref is on origin only once the render passed (null control for the refusals)",
               git(work, "ls-remote", str(origin), "refs/heads/dispatch/*").lower().count("r10-big") == 3
               and git(work, "ls-remote", str(origin), "refs/heads/dispatch/*").count("r10-x") == 1)
@@ -615,7 +766,8 @@ def _group_checks(check) -> None:
         registry = lambda: (bus_state / "dispatched").read_text().splitlines() if (bus_state / "dispatched").exists() else []
         check("a reviewer needs its pr, as on the flag path, and records nothing",
               refused(role="reviewer", head=tip) and registry() == [])
-        check("a reviewer needs its PR head", refused(role="reviewer", pr="7"))
+        check("a reviewer needs its PR head, and is refused for that reason",
+              "pass --head" in reason(role="reviewer", pr="7") and registry() == [])
         check("a reviewer dispatch with no nonce mints one through bus.sh dispatch and renders",
               dispatch(role="reviewer", head=rhead, pr="7") == "dispatch/reviewer-r10-x")
         rec = (registry() or [""])[-1].split()
@@ -667,6 +819,28 @@ def _group_checks(check) -> None:
             published = False
         check("_publish itself refuses a ref that would publish the host, and pushes nothing",
               not published and "someone" not in git(work, "ls-remote", str(origin)))
+        # A step push matches no glob the handoff machinery lists, read from its own source.
+        globs = (re.findall(r"'(refs/heads/handoff[^'*]*\*)'", (HERE / "cloud_relay.sh").read_text())
+                 + re.findall(r'"\+(refs/heads/handoff[^:"*]*\*):', (HERE / "bus.sh").read_text()))
+        git(work, "push", "-q", str(origin), f"{tip}:refs/heads/{WIP_NS}/r10-x", f"{tip}:refs/heads/handoff/r10-x")
+        listed = git(work, "ls-remote", str(origin), *globs)
+        check("a handoff-wip push is invisible to cloud_relay.sh's handoff arm and bus.sh orphans; handoff/ is not (null)",
+              len(globs) == 4 and f"refs/heads/{WIP_NS}/" not in listed and "refs/heads/handoff/r10-x" in listed)
+        git(work, "push", "-q", str(origin), f":refs/heads/{WIP_NS}/r10-x", ":refs/heads/handoff/r10-x")
+        # The pinned identity passes ref_privacy --commits; a machine's domain does not (null control).
+        bare_env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_AUTHOR_", "GIT_COMMITTER_"))}
+
+        def judged(email):
+            repo = Path(td) / f"ident-{len(email)}"
+            throwaway_git_init(repo, "-q")
+            subprocess.run(["git", "-C", str(repo), "-c", f"user.name={SEAT_NAME}", "-c", f"user.email={email}",
+                            "commit", "-q", "--allow-empty", "-m", "a step"], env=bare_env, check=True)
+            r = subprocess.run([sys.executable, "-I", str(HERE / "ref_privacy.py"), "guard", "--ref",
+                                f"{WIP_NS}/r10-x", "--commits", "HEAD", "-C", str(repo)],
+                               capture_output=True, text=True, env=bare_env)
+            return r.returncode, git(repo, "log", "-1", "--format=%ae")
+        check("ref_privacy guards a handoff-wip push like any: the pinned identity passes, a .local one refuses (null)",
+              judged(SEAT_EMAIL) == (0, SEAT_EMAIL + "\n") and judged("seat@build.local")[0] == 3)
         out = io.StringIO()
         with contextlib.chdir(work), contextlib.redirect_stdout(out):
             rc = main(["--role", "reviewer", "--head", rhead, "--pr", "7", "--nonce", "abc123", "--publish",
@@ -676,7 +850,7 @@ def _group_checks(check) -> None:
         except subprocess.CalledProcessError:
             msg = ""
         check("a reviewer's flag-path --publish publishes to dispatch/reviewer-rev-<PR> and points there",
-              rc == 0 and "git fetch origin dispatch/reviewer-rev-7 " in content(out.getvalue())
+              rc == 0 and " of dispatch/reviewer-rev-7 (`git fetch origin " in content(out.getvalue())
               and msg.startswith("CLOUD REVIEWER") and "Bus nonce: abc123." in msg)
         # Two sources, never one: the roster from the round's roster branch
         # (O17), the head from main. The branch is one commit ahead of main
@@ -750,7 +924,8 @@ def _group_checks(check) -> None:
             again = None
         git(work, "fetch", "-q", str(origin), "refs/heads/" + line)
         check("a re-dispatch from a second clone fast-forwards the existing ref",
-              again == line and git(work, "rev-parse", "FETCH_HEAD^").strip() == tip_before)
+              again == line and git(work, "rev-parse", "FETCH_HEAD").strip() != tip_before
+              and git(work, "merge-base", "--is-ancestor", tip_before, "FETCH_HEAD") == "")
 
 
 
@@ -851,17 +1026,47 @@ def self_test() -> int:
           all(WAIT_LINE in t and "240 s" in WAIT_LINE for t in prompts.values()))
     check("the fixer reads its role file, not CLAUDE.md, which the harness already loaded",
           "dev/governance/roles/fixer.md" in prompts["fixer"] and "CLAUDE.md" not in prompts["fixer"])
+    check("every role's setup line runs the toolchain check and stops on its REFUSE (#2709)",
+          all(f"`{SETUP_CHECK}`, and on REFUSE stop" in t.splitlines()[1] for t in prompts.values()))
+    rv = prompts["reviewer"]
+    check("the reviewer waits for CI only by re-running merge_train.py classify, 60 s apart, until 0, 1 or 2",
+          f"`python3 tools/audit/seat/merge_train.py classify {head}` in the background, at least 60 s" in rv
+          and "exits 0 (GREEN), 1 (RED) or 2 (unreadable: say so in the verdict)" in rv and "3 is WAIT" in rv)
+    check("the reviewer is forbidden a pgrep or pkill waiter and a context the ruleset does not require",
+          "Never wait with `pgrep` or `pkill`" in rv and "such as\n`prelude`" not in rv and "such as `prelude`" in rv)
+    check("no other role is told to wait on merge_train.py classify (null control)",
+          all("merge_train.py classify" not in t and "pgrep" not in t for r, t in prompts.items() if r != "reviewer"))
+    wip, fx = f"refs/heads/{WIP_NS}/t-1", prompts["fixer"]
+    check("the fixer step-pushes fast-forward to handoff-wip/<topic>, never to handoff/, and the tail allows it",
+          f"push each verified step, fast-forward only, to {wip} before any wait" in fx
+          and "never step-push to\nhandoff/t-1" not in fx and "never step-push to handoff/t-1" in fx
+          and f"except your return refs and {wip}." in fx)
+    check("the fixer deletes the step ref only after body_push.sh succeeds",
+          0 <= fx.find("body_push.sh t-1") < fx.find(f"`git push origin :{wip}`"))
+    check("the fixer merges a moved origin/main and reruns prepr.sh before it pushes the handoff",
+          0 <= fx.find("`git merge origin/main`, rerun `tools/pr/prepr.sh`")
+          < fx.find("push the code to refs/heads/handoff/t-1"))
+    check("no other role is licensed a step ref (null control)",
+          all(WIP_NS not in t for r, t in prompts.items() if r != "fixer"))
+    ident = f"`git config user.name {SEAT_NAME} && git config user.email {SEAT_EMAIL}`"
+    check("the fixer and the probe pin the seat's noreply identity in the setup line, no other role does (null)",
+          all((ident in t.splitlines()[1]) == (r in COMMITTING_ROLES) for r, t in prompts.items())
+          and set(COMMITTING_ROLES) == {"fixer", "probe"})
     for role, ref in (("fixer", "dispatch/fixer-t-1"), ("reviewer", "dispatch/reviewer-rev-7")):
         a = dict(pr="7" if role == "reviewer" else "", topic="" if role == "reviewer" else "t-1",
                  nonce="abc123" if role == "reviewer" else "")
         check(f"the {role}'s publish ref is {ref}", dispatch_ref(role, a["topic"], a["pr"]) == ref)
-        ptr = render(role, head, **base, **a, publish_ref=ref)["job_config"]["ccr"]["events"][0]["data"][
-            "message"]["content"]
-        check(f"a published {role}'s event is a pointer: under 600 chars, names the ref, the head and PROMPT.md",
-              len(ptr) < 600 and f"git fetch origin {ref} && git show FETCH_HEAD:PROMPT.md" in ptr
-              and head in ptr and FOOTER_BAN not in ptr and len(ptr) < len(prompts[role]))
-    check("a reviewer's pointer carries its nonce", "abc123" in render(
-        "reviewer", head, **base, pr="7", nonce="abc123", publish_ref="dispatch/reviewer-rev-7")[
+        pin = "fedcba9876543210" * 2 + "fedcba98"
+        ptr = render(role, head, **base, **a, publish_ref=ref, pin=pin)["job_config"]["ccr"]["events"][0][
+            "data"]["message"]["content"]
+        check(f"a published {role}'s event is a stub: the seat line, the footer ban and PROMPT.md at the pinned SHA",
+              ptr.startswith(_seat_line(role, "owner/name", a["pr"], head, a["topic"], a["nonce"]))
+              and f"git fetch origin {pin} && git show {pin}:PROMPT.md" in ptr and f"of {ref} " in ptr
+              and sum(FOOTER_BAN in x for x in ptr.splitlines()) == 1 and len(ptr) < len(prompts[role]))
+        check(f"a published {role} with no 40-hex pin is refused", refused(role, publish_ref=ref, pin="")
+              and refused(role, publish_ref=ref, pin=ref) and not refused(role, publish_ref=ref, pin=pin))
+    check("a reviewer's stub carries its nonce", "abc123" in render(
+        "reviewer", head, **base, pr="7", nonce="abc123", publish_ref="dispatch/reviewer-rev-7", pin=head)[
         "job_config"]["ccr"]["events"][0]["data"]["message"]["content"])
     check("a 39-hex head is refused", refused(h=head[:-1]))
     check("a 41-hex head is refused", refused(h=head + "0"))
@@ -871,6 +1076,8 @@ def self_test() -> int:
     check("a blank reviewer nonce is refused", refused(nonce="  "))
     check("a reviewer without --pr is refused", refused(pr=""))
     check("a fixer without --topic is refused", refused("fixer", topic=""))
+    check("a design reviewer without the 40-hex design tip is refused on the flag path",
+          refused("design-reviewer", design="") and not refused("design-reviewer", design=head))
     check("a topic with a slash is refused", refused("probe", topic="a/b"))
     check("a missing environment id is refused", refused(env_id=""))
     check("a missing model is refused", refused(model=""))
diff --git a/tools/audit/seat/instruments/cloud_dispatch.py.md b/tools/audit/seat/instruments/cloud_dispatch.py.md
index 68d8c671e..b2b79948f 100644
--- a/tools/audit/seat/instruments/cloud_dispatch.py.md
+++ b/tools/audit/seat/instruments/cloud_dispatch.py.md
@@ -8,36 +8,52 @@
   flag, an overlay JSON (`--overlay` / `$HPO_CLOUD_OVERLAY`) or `HPO_CLOUD_*`,
   never from the tree. `--role R --group G --model M` is the one-call path
   (`dispatch_group()` for a host such as the beat): the brief, topic and
-  repository come from the roster at `--roster-ref` (default the round's roster
+  repository come from the roster at `--roster-ref` (the brief is the group's
+  brief, then `After:` its predecessors, then each carry verbatim as
+  `Carry <i>:`, `<i>` its 0-based roster index; default the round's roster
   branch, `roster_lib.default_roster_ref`); the head is `--head`, else
   `origin/main`'s tip, never the roster ref's (a reviewer must pass its PR
-  head); the environment is the overlay / `HPO_CLOUD_ENV_ID`; a flag it does
+  head); a `--model` outside the family the roster rules for the role (the
+  group's `model.fixer` / `model.reviewer`, else `fixerModel` /
+  `reviewerModel`) refuses in one line, and a role it rules nothing for passes;
+  the environment is the overlay / `HPO_CLOUD_ENV_ID`; a flag it does
   not consume (`--topic`, `--brief`, `--repo`, `--env-id`, `--out`,
   `--publish`) refuses; it renders through the same `publish_seat` as the flag
   path's `--publish` (the payload is that path's byte for byte), publishes
   PAYLOAD.json and PROMPT.md on origin as `dispatch/<role>-<topic>`
   (fast-forwarded, an identical tree adds nothing, a render refusal pushes
   nothing) and prints that ref name, the one line a standing trigger is fired
-  with. A published payload's event is a pointer to PROMPT.md on its ref, not
-  the prompt (the runner echoes the event into the orchestrator); `--publish`
+  with. A published payload's event is a stub, not the prompt (the runner
+  echoes the event into the orchestrator): the seat line and the footer ban
+  inline, and PROMPT.md at the commit that holds it, pinned by SHA and never
+  by the moving ref (PROMPT.md is committed alone, PAYLOAD.json on top);
+  `--publish`
   on the flag path publishes to `dispatch/<role>-<topic>`, else
   `dispatch/<role>-rev-<PR>`, the same way; `dev/audit/harnesses/r10_flow_dispatch_mutants.py`
   re-runs its mutants. When: dispatching a seat to the cloud runner;
   paste the printed JSON as the trigger update, or fire the standing trigger
   with the printed ref. The measured shape of a cloud seat:
   every trigger update resends the full ccr and then `run`s it, never a
-  patch; the brief is snapshotted at `run`, so it is inlined at render time,
-  an edit afterwards reaches no running seat, and overlapping runs are fine;
+  patch; the brief is snapshotted at `run`, so it is inlined at render time
+  (into the event, or into PROMPT.md at the pinned commit), an edit afterwards
+  reaches no running seat, and overlapping runs are fine;
   the toolchain (`PATH` with `/opt/hpo/venv-ci/bin`, `BASH_ENV`,
   `HPO_TYPING_PYTHON`, `OPENBLAS_CORETYPE`) comes from the environment's
   variables, not from a profile the seat sources, so the prompt says only
-  that it is on `PATH`; the seat starts off `main` in a shallow clone
+  that it is on `PATH`, and the setup line runs `cloud-setup.sh --check`
+  and stops the seat on its REFUSE; the seat starts off `main` in a shallow clone
   (`git fetch --unshallow --tags origin` first); the return signal is a
   pushed ref: `probe/rev-<pr>-<nonce first 8>` for a reviewer (see
   `cloud_relay.sh`: a cloud reviewer never runs `bus.sh`, whose dispatch record
   lives on the orchestrator's machine and refuses "unknown nonce" anywhere
   else, and a seat may not write a record it did not mint), `handoff/<topic>`
-  plus `handoff-body/<topic>` for a fixer, `handoff-body/<topic>` for a probe,
+  plus `handoff-body/<topic>` for a fixer (which pushes each verified step,
+  fast-forward only, to `handoff-wip/<topic>`, a prefix neither
+  `cloud_relay.sh`'s handoff arm nor `bus.sh orphans` lists, merges a moved
+  `origin/main` and reruns `prepr.sh` before the handoff, and deletes the step
+  ref once `body_push.sh` succeeds; a seat that dies leaves that one ref),
+  `handoff-body/<topic>` for a probe; a fixer or probe pins the noreply seat
+  identity before its first commit,
   and a return push carries only the seat's own result tokens: a push
   carrying system-file dumps is refused; the session is reachable one way,
   by `SendMessage` to it, and nothing comes back on that channel. Refusal: a
diff --git a/tools/audit/seat/ref_privacy.py b/tools/audit/seat/ref_privacy.py
index 6e138fc6f..a3f68e58c 100644
--- a/tools/audit/seat/ref_privacy.py
+++ b/tools/audit/seat/ref_privacy.py
@@ -411,7 +411,9 @@ PUSHERS = {
     "tools/audit/seat/cloud_dispatch.py": (GUARDED, "the group path publishes dispatch/<role>-<topic> "
                                            "(a roster branch tail), ref_privacy.refusal on the ref and message; "
                                            "its reviewer prompt names probe/rev-<pr>-<nonce8> from a PR number "
-                                           "and 8 hex digits, under a constant seat identity"),
+                                           "and 8 hex digits, under a constant seat identity; its fixer prompt names "
+                                           "handoff-wip/<topic> step pushes, judged by the seat's own guard "
+                                           "like any push"),
     ".claude/workflows/audit-find.js": ("prompt", "an agent prompt naming handoff/audit-r<round>-... "
                                         "refs from round and box numbers"),
     ".claude/workflows/audit-plan.js": ("prompt", "an agent prompt naming the constant plan/r<round> "

