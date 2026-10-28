# Review packet #2937
head: 3d1c405ddbe8d9adefbbb1d26a22ba63871fd995
base: b0b2d7697f8c5baaef2c082d9bf3242b57249e68

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=123126697271 neutral
arch-score / arch-score id=123126201421 in_progress
arm id=123125863531 skipped
budget-raise-gate / budget-raise-gate id=123126201328 success
cancel-superseded id=123125866218 success
codeql / Analyze (actions) id=123126201371 in_progress
codeql / Analyze (javascript-typescript) id=123126201507 queued
codeql / Analyze (python) id=123126201342 in_progress
governance / delivery-status id=123126201402 queued
governance / delivery-status-publish id=123126203960 skipped
governance / env-matrix id=123126201365 in_progress
governance / instrument-self-tests id=123126201662 queued
governance / policy-docs id=123126201413 queued
governance / record id=123126204285 skipped
governance / wave-script id=123126201459 queued
hassfest / hassfest id=123126201329 queued
kernel-points id=123126203673 skipped
prelude id=123125866733 in_progress
refresh id=123125866675 in_progress
tests / arch-instrument id=123126699175 queued
tests / briefs id=123126201563 queued
tests / browser id=123126699141 queued
tests / closure-scope id=123126201391 success
tests / closures id=123126699261 queued
tests / coverage id=123126699340 queued
tests / fast (3.14) id=123126699279 queued
tests / mutation id=123126201390 in_progress
tests / nightly-ha id=123126701087 skipped
tests / nightly-status id=123126201674 queued
tests / replay id=123126700795 skipped
tests / typing id=123126699325 queued
validate / validate-hacs id=123126201327 in_progress

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item fc2c4144: R10-FRICTION-MUTATION-SURVIVOR
NOTE body item ec2ddf28: dismissed:unmeasured, and the fallback is not obviously right for an edit guard; the orchestrator may open it if a measurement shows it.
NOTE body item de3bf417: R10-FLY-SUITE-ENV-FLAKES
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/audit/seat/cloud_dispatch.py --self-test
             `tools/audit/seat/cloud_dispatch.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_flow_dispatch_mutants.py
             `dev/audit/harnesses/r10_flow_dispatch_mutants.py` is in the tree at this head
  unverified git show origin/main:tools/audit/seat/cloud_dispatch.py | grep -cF 'pr=pr, topic=topic, nonce=nonce,'
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         bash .claude/hooks/stop-selfcheck.sh --self-test
             `.claude/hooks/stop-selfcheck.sh` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs --hooks
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         bash tools/audit/seat/ci-watch.sh --self-test
             `tools/audit/seat/ci-watch.sh` is in the tree at this head
  ok         python3 tools/audit/seat/proof_watch.py --self-test
             `tools/audit/seat/proof_watch.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  unverified git grep -nEi "sleep +[0-9]{3}|default=[0-9]{3}\b|(POLL|INTERVAL|WAIT)[A-Z_]*\s*[:=]\s*[0-9]+|five.minute|300 ?s\b" -- tools/audit/seat tools/pr dev/governance .claude
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -niE "read[^.]{0,40}CLAUDE\.md" -- .claude tools dev/governance
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 11 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.claude/hooks/stop-selfcheck.sh b/.claude/hooks/stop-selfcheck.sh
index 36750748d..3cb4cbcbe 100755
--- a/.claude/hooks/stop-selfcheck.sh
+++ b/.claude/hooks/stop-selfcheck.sh
@@ -153,7 +153,23 @@ if [ "${1:-}" = "--self-test" ]; then
     e2e_err 0 "$T" 1 'optimizer.py' "END TO END: a mutation arm is named and the turn still ends"
     git -C "$T" checkout -- custom_components/heatpump_optimizer/optimizer.py >/dev/null 2>&1
     e2e_err 0 "$T" 0 'optimizer.py' "END TO END: and nothing is said once the arm is restored (null control)"
-    rm -rf "$T"
+
+    # THE COMMAND THAT WIRES THIS FILE, read from settings.json and run as the
+    # harness runs it. A session whose project dir is not this repository (an
+    # orchestrator in a scratch workspace) has no hook at "$CLAUDE_PROJECT_DIR";
+    # the command finds the repository's own from its cwd, else does nothing,
+    # and never fails the turn on a path (R10-FLY-CACHE-PROMPTS). The scratch
+    # repository's hook is a stub exiting 3, so "ran it" and "skipped" differ.
+    CMD=$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["hooks"]["Stop"][0]["hooks"][0]["command"])' \
+          "$(dirname -- "$0")/../settings.json")
+    E=$(mktemp -d); mkdir -p "$T/.claude/hooks"; printf 'exit 3\n' >"$T/.claude/hooks/stop-selfcheck.sh"
+    wired() { # want-rc, cwd, project-dir, label
+      (cd "$2" && printf '{}' | CLAUDE_PROJECT_DIR="$3" sh -c "$CMD" >/dev/null 2>&1); st $? "$1" "$4"
+    }
+    wired 3 "$T" "$T" "WIRED: the project dir's hook runs"
+    wired 3 "$T" "$E" "WIRED: a project dir without the hook runs the repository's, found from the cwd"
+    wired 0 "$E" "$E" "WIRED: no hook anywhere exits 0, never a missing-file error"
+    rm -rf "$T" "$E"
   else
     # A box without a working `git init` cannot drive these. Say so rather than
     # counting the end-to-end cases as silent passes: a skipped drive that claims its pins is the
diff --git a/.claude/settings.json b/.claude/settings.json
index fc8384b85..13e604aa5 100644
--- a/.claude/settings.json
+++ b/.claude/settings.json
@@ -22,7 +22,7 @@
     "Stop": [
       {
         "hooks": [
-          { "type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/stop-selfcheck.sh\"" }
+          { "type": "command", "command": "f=\"$CLAUDE_PROJECT_DIR/.claude/hooks/stop-selfcheck.sh\"; [ -f \"$f\" ] || f=\"$(git rev-parse --show-toplevel 2>/dev/null)/.claude/hooks/stop-selfcheck.sh\"; [ -f \"$f\" ] || exit 0; exec bash \"$f\"" }
         ]
       }
     ]
diff --git a/dev/audit/harnesses/r10_flow_dispatch_mutants.py b/dev/audit/harnesses/r10_flow_dispatch_mutants.py
index 51dc32a03..0e17361dc 100644
--- a/dev/audit/harnesses/r10_flow_dispatch_mutants.py
+++ b/dev/audit/harnesses/r10_flow_dispatch_mutants.py
@@ -8,7 +8,10 @@ cli-head-dropped, cli-roster-ref-dropped, fetch-skipped); round 4 added
 the three the round-3 review found (cli-role-fixed, cli-pr-dropped,
 cli-nonce-dropped) and the rest of the --group call's inputs (cli-group-fixed,
 cli-model-fixed, cli-overlay-dropped); round 5 added the flag table's arms
-(group-refusal-off, env-id-forwarded-as-none, flag-unlisted) and cli-pr-truncated. Each
+(group-refusal-off, env-id-forwarded-as-none, flag-unlisted) and cli-pr-truncated;
+R10-FLY-CACHE-PROMPTS re-aimed nonce-altered, topic-to-id, prompt-wrong and
+flag-unlisted at the publish_seat path and added the pointer, --publish, wait-cap
+and read-list arms (pointer-ref-dropped .. claude-md-reread). Each
 mutant is a one-occurrence replacement in tools/audit/seat/cloud_dispatch.py;
 it is applied alone, `cloud_dispatch.py --self-test` run, and the file
 restored byte for byte. The drive refuses a dirty file and aborts on a
@@ -53,12 +56,12 @@ MUTANTS = [
     ("tree-skip", "    if tip and _git(repo_dir, \"rev-parse\"", "    if False and _git(repo_dir, \"rev-parse\""),
     ("brief-drop", 'brief=group.get("brief") or ""', 'brief=""'),
     ("parent-drop", '*(["-p", tip[0]] if tip else [])', "*[]"),
-    ("nonce-altered", "pr=pr, topic=topic, nonce=nonce,", "pr=pr, topic=topic, nonce=nonce + \"0\","),
-    ("topic-to-id", 'ref = f"{DISPATCH_NS}/{role}-{topic}"', 'ref = f"{DISPATCH_NS}/{role}-{group_id}"'),
+    ("nonce-altered", "**args, nonce=nonce)\n    except Refusal:", "**args, nonce=nonce + \"0\")\n    except Refusal:"),
+    ("topic-to-id", 'ref = dispatch_ref(role, topic, "")', 'ref = dispatch_ref(role, group_id, "")'),
     ("render-host-off", "    m = HOME.search(json.dumps(payload))", "    m = None"),
     ("privacy-off", "    if why:\n        raise Refusal(f\"the dispatch ref", "    if False:\n        raise Refusal(f\"the dispatch ref"),
     ("head-ignored", 'head or _git(repo_dir, "rev-parse", f"{HEAD_REF}', '_git(repo_dir, "rev-parse", f"{HEAD_REF}'),
-    ("prompt-wrong", '"PROMPT.md": payload["job_config"]', '"PROMPT.md": "" and payload["job_config"]'),
+    ("prompt-wrong", '"PROMPT.md": prompt}', '"PROMPT.md": ""}'),
     ("roster-repo-ignored", 'repo=roster.get("repo") or known["repo"]', 'repo=known["repo"]'),
     ("roster-ref-main", "roster_ref = roster_lib.reader_ref(repo_dir, roster_ref)",
      "roster_ref = roster_ref or roster_lib.MAIN_REF"),
@@ -77,7 +80,17 @@ MUTANTS = [
     ("cli-overlay-dropped", "nonce=args.nonce, overlay=args.overlay))", "nonce=args.nonce, overlay=None))"),
     ("group-refusal-off", "if why and getattr(args, dest)", "if False and getattr(args, dest)"),
     ("env-id-forwarded-as-none", '"env_id": "the environment id', '"env_id": None and "the environment id'),
-    ("flag-unlisted", '    ap.add_argument("--out")\n    return ap', '    ap.add_argument("--out")\n    ap.add_argument("--extra")\n    return ap'),
+    ("flag-unlisted", '    ap.add_argument("--out")\n', '    ap.add_argument("--out")\n    ap.add_argument("--extra")\n'),
+    # R10-FLY-CACHE-PROMPTS: the pointer event, --publish, the wait cap, the role read list.
+    ("pointer-ref-dropped", "at origin ref {ref} (`git fetch origin {ref} && git show",
+     "at origin ref (`git fetch origin && git show"),
+    ("pointer-off", "text = (_pointer(role, repo, pr, head, topic, nonce, publish_ref) if publish_ref",
+     "text = (_pointer(role, repo, pr, head, topic, nonce, publish_ref) if False"),
+    ("publish-ignored", "        if args.publish:", "        if False:"),
+    ("publish-ref-rev-dropped", 'key = topic or (f"rev-{pr}"', 'key = topic or (f"{pr}"'),
+    ("wait-line-dropped", '"and no timeout. " + WAIT_LINE)', '"and no timeout.")'),
+    ("claude-md-reread", "roles/fixer.md from main, and follow it exactly",
+     "roles/fixer.md and CLAUDE.md from main, and follow them exactly"),
     ("cli-pr-truncated", 'head=args.head or "", pr=args.pr,', "head=args.head or \"\", pr=(args.pr or '')[:1],"),
 ]
 SUMMARY = re.compile(r"cloud_dispatch self-test: (\d+) checks, (\d+) failed")
diff --git a/dev/programme/delivery/2937.md b/dev/programme/delivery/2937.md
new file mode 100644
index 000000000..8f845a739
--- /dev/null
+++ b/dev/programme/delivery/2937.md
@@ -0,0 +1 @@
+- [#2937](https://github.com/tvofi/heatpump_optimizer/pull/2937) — **open**, R10-FLY-CACHE-PROMPTS: cloud seat prompt-cache gaps 1, 4, 6 (R10-FLY-CACHE-PROMPTS)
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index c2a5128fe..229775fbb 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -257,12 +257,16 @@ sweep's standing-seat liveness step keep them alive.
   branch, `roster_lib.default_roster_ref`); the head is `--head`, else
   `origin/main`'s tip, never the roster ref's (a reviewer must pass its PR
   head); the environment is the overlay / `HPO_CLOUD_ENV_ID`; a flag it does
-  not consume (`--topic`, `--brief`, `--repo`, `--env-id`, `--out`) refuses;
-  it renders through the same `render` (the payload is the flag path's byte
-  for byte), publishes PAYLOAD.json and PROMPT.md on origin as
-  `dispatch/<role>-<topic>` (fast-forwarded, an identical tree adds nothing, a
-  render refusal pushes nothing) and prints that ref name, the one line a
-  standing trigger is fired with; `dev/audit/harnesses/r10_flow_dispatch_mutants.py`
+  not consume (`--topic`, `--brief`, `--repo`, `--env-id`, `--out`,
+  `--publish`) refuses; it renders through the same `publish_seat` as the flag
+  path's `--publish` (the payload is that path's byte for byte), publishes
+  PAYLOAD.json and PROMPT.md on origin as `dispatch/<role>-<topic>`
+  (fast-forwarded, an identical tree adds nothing, a render refusal pushes
+  nothing) and prints that ref name, the one line a standing trigger is fired
+  with. A published payload's event is a pointer to PROMPT.md on its ref, not
+  the prompt (the runner echoes the event into the orchestrator); `--publish`
+  on the flag path publishes to `dispatch/<role>-<topic>`, else
+  `dispatch/<role>-rev-<PR>`, the same way; `dev/audit/harnesses/r10_flow_dispatch_mutants.py`
   re-runs its mutants. When: dispatching a seat to the cloud runner;
   paste the printed JSON as the trigger update, or fire the standing trigger
   with the printed ref. The measured shape of a cloud seat:
diff --git a/tools/audit/seat/ci-watch.sh b/tools/audit/seat/ci-watch.sh
index 01a6f21a9..6d95b0463 100755
--- a/tools/audit/seat/ci-watch.sh
+++ b/tools/audit/seat/ci-watch.sh
@@ -25,6 +25,10 @@
 R=tvofi/heatpump_optimizer
 S=${CI_WATCH_STATE:-${HPO_STATE_DIR:-$HOME/.local/state/hpo}/ci-watch-state}
 RULESET=main-protect-checks
+# Seconds between cycles: under a waiting seat's 5-minute prompt-cache TTL, so the
+# wake on its exit does not rewrite the seat's whole context (R10-FLY-CACHE-PROMPTS),
+# and never under GitHub's 60 s poll floor.
+POLL_S=240
 
 # --------------------------------------------------------------- self-test
 self_test() {
@@ -223,6 +227,11 @@ EOF
   ck "W12 a gate that did not succeed (skipped; RATE-LIMITED is a failure) alerts RED: gate, never a pass" \
      "$([ $rc = 1 ] && says 'RED: gate' "$O" && echo 1 || echo 0)"
 
+  # The cadence (R10-FLY-CACHE-PROMPTS): under the seat's 5-minute prompt-cache
+  # TTL, never under GitHub's 60 s poll floor.
+  ck "the poll is inside [60 s, 240 s] (POLL_S=${POLL_S:-unset})" \
+     "$([ "${POLL_S:-0}" -ge 60 ] && [ "${POLL_S:-0}" -le 240 ] && echo 1 || echo 0)"
+
   printf 'ci-watch self-test: %d checks, %d failed\n' "$((passed + failed))" "$failed"
   [ "$failed" = 0 ]
   return $?
@@ -287,5 +296,5 @@ while true; do
   done
   if [ -n "$OUT" ]; then echo -e "CI-WATCH ALERT ($(date -u +%H:%MZ)): NEW state(s):$OUT"; exit 1; fi
   [ -n "${CI_WATCH_ONCE:-}" ] && exit 0
-  sleep 300
+  sleep "$POLL_S"
 done
diff --git a/tools/audit/seat/cloud_dispatch.py b/tools/audit/seat/cloud_dispatch.py
index cc1b1e976..a97421109 100644
--- a/tools/audit/seat/cloud_dispatch.py
+++ b/tools/audit/seat/cloud_dispatch.py
@@ -3,7 +3,7 @@
 
     python3 -I tools/audit/seat/cloud_dispatch.py --role reviewer|fixer|probe \
         --head <40-hex> [--pr N] [--topic T] [--nonce N] [--brief FILE] \
-        [--env-id ID] [--model M] [--repo OWNER/NAME] [--overlay FILE] [--out FILE]
+        [--env-id ID] [--model M] [--repo OWNER/NAME] [--overlay FILE] [--out FILE] [--publish]
     python3 -I tools/audit/seat/cloud_dispatch.py --role reviewer|fixer|probe --group G --model M \
         [--roster-ref REF] [--head <40-hex>] [--pr N] [--nonce N] [--overlay FILE]
     python3 -I tools/audit/seat/cloud_dispatch.py --self-test
@@ -16,10 +16,13 @@ never the roster ref's (a seat forks from main, not from the roster branch); a
 reviewer needs --head (the PR head) and takes its nonce from `bus.sh dispatch`, which
 mints one or re-records --nonce; the environment id comes from the overlay /
 $HPO_CLOUD_ENV_ID. The
-payload is rendered by the same `render` as the flag path, so it is the flag
-path's byte for byte, and is published, with its prompt, on origin as
+payload is rendered by the same `publish_seat` as the flag path's --publish, so it
+is that path's byte for byte, and is published, with its prompt, on origin as
 `dispatch/<role>-<topic>` (PAYLOAD.json, PROMPT.md); the one line printed is that
-ref name. A standing trigger whose prompt fetches the ref it is fired with
+ref name. A published payload's event is a pointer to PROMPT.md on the ref, never
+the prompt itself (the runner echoes the event; R10-FLY-CACHE-PROMPTS). --publish
+does the same on the flag path, to `dispatch/<role>-<topic>`, else
+`dispatch/<role>-rev-<PR>`, and prints the payload as without it. A standing trigger whose prompt fetches the ref it is fired with
 needs nothing else. A render refusal (below) pushes nothing.
 
 WHAT IT RENDERS. The whole `job_config.ccr` object a cloud runner's trigger
@@ -100,20 +103,39 @@ FOOTER_BAN = ("Write no Claude Code footer, no Co-Authored-By or Claude-Session
               "with `git log --format=%B` before pushing.")
 
 
+#: A seat's prompt cache lives 5 min: a wait past it rewrites the whole context on
+#: the next turn (R10-FLY-CACHE-PROMPTS). 240 s stays under it; GitHub's 60 s poll
+#: floor stays the lower bound.
+WAIT_LINE = "Never wait in one tool call longer than 240 s; poll again instead."
+
+
 class Refusal(Exception):
     pass
 
 
-def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, brief: str) -> str:
+def _seat_line(role: str, repo: str, pr: str, head: str, topic: str, nonce: str) -> str:
     who = {"reviewer": "CLOUD REVIEWER", "fixer": "CLOUD FIXER", "probe": "CLOUD PROBE"}[role]
     subject = f"PR #{pr} of {repo}, at head {head}" if pr else f"{repo}, topic {topic}, at head {head}"
     first = f"{who} seat for {subject}."
     if nonce:
         first += f" Bus nonce: {nonce}."
-    first += " Never send push notifications. " + FOOTER_BAN
+    return first + " Never send push notifications."
+
+
+def _pointer(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, ref: str) -> str:
+    """The event a published seat is fired with: who it is, and where its prompt is.
+    The runner echoes the event into every view of the trigger, so the whole prompt
+    there was paid for several times over; PROMPT.md on the ref is paid once."""
+    return (_seat_line(role, repo, pr, head, topic, nonce) + "\n"
+            f"Your full brief is PROMPT.md at origin ref {ref} (`git fetch origin {ref} && git show "
+            "FETCH_HEAD:PROMPT.md`); read it first and follow it exactly.\n")
+
+
+def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, brief: str) -> str:
+    first = _seat_line(role, repo, pr, head, topic, nonce) + " " + FOOTER_BAN
     setup = ("Setup: `git fetch --unshallow --tags origin`. The toolchain (venv python, node, gh) "
              "is on PATH from the environment. Run anything heavy in the background with Monitor "
-             "and no timeout.")
+             "and no timeout. " + WAIT_LINE)
     if role == "reviewer":
         body = (
             "Role: read dev/governance/roles/fix-review.md and its rules from main, and follow them "
@@ -153,7 +175,7 @@ def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, br
             "That ref is the return signal. Do not post comments, approve or merge.")
     elif role == "fixer":
         body = (
-            "Role: read dev/governance/roles/fixer.md and CLAUDE.md from main, and follow them exactly, "
+            "Role: read dev/governance/roles/fixer.md from main, and follow it exactly, "
             f"in a worktree of your own cut from origin/main. Fetch {head} for the base you were given.\n"
             f"Output: push the code to refs/heads/handoff/{topic}, then write the PR body and run "
             f"`bash tools/audit/seat/body_push.sh {topic} <body.md>`, which pushes "
@@ -176,7 +198,8 @@ def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, br
 
 
 def render(role: str, head: str, *, env_id: str, model: str, repo: str, pr: str = "",
-           topic: str = "", nonce: str = "", brief: str = "") -> dict:
+           topic: str = "", nonce: str = "", brief: str = "", publish_ref: str = "") -> dict:
+    """The payload; with `publish_ref`, its event is the pointer to that ref (`publish_seat`)."""
     if role not in ROLES:
         raise Refusal(f"role must be one of {', '.join(ROLES)}")
     if not is_head(head or ""):
@@ -193,7 +216,8 @@ def render(role: str, head: str, *, env_id: str, model: str, repo: str, pr: str
             raise Refusal(f"no {name}: pass a flag, an overlay entry or its HPO_CLOUD_* variable")
     if not re.fullmatch(r"[\w.-]+/[\w.-]+", repo):
         raise Refusal("repo must be OWNER/NAME")
-    text = _prompt(role, repo, pr, head, topic, nonce, brief)
+    text = (_pointer(role, repo, pr, head, topic, nonce, publish_ref) if publish_ref
+            else _prompt(role, repo, pr, head, topic, nonce, brief))
     payload = {"job_config": {"ccr": {
         "environment_id": env_id,
         "session_context": {
@@ -260,6 +284,24 @@ def _publish(repo_dir: str, ref: str, files: dict[str, str]) -> None:
     _git(repo_dir, "push", "-q", "origin", f"{commit}:refs/heads/{ref}")
 
 
+def dispatch_ref(role: str, topic: str, pr: str) -> str:
+    """`dispatch/<role>-<topic>`, or `dispatch/<role>-rev-<PR>` for a seat with no topic."""
+    key = topic or (f"rev-{pr}" if pr.isdigit() else "")
+    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", key):
+        raise Refusal("a published seat needs a topic (letters, digits, . _ -) or a --pr")
+    return f"{DISPATCH_NS}/{role}-{key}"
+
+
+def publish_seat(repo_dir: str, ref: str, role: str, head: str, **args) -> dict:
+    """Publish the seat's whole prompt as PROMPT.md, with the payload firing it, on `ref`;
+    return that payload, whose event is the pointer to the ref. Both render first, so
+    every `render` refusal pushes nothing."""
+    prompt = render(role, head, **args)["job_config"]["ccr"]["events"][0]["data"]["message"]["content"]
+    payload = render(role, head, **args, publish_ref=ref)
+    _publish(repo_dir, ref, {"PAYLOAD.json": json.dumps(payload), "PROMPT.md": prompt})
+    return payload
+
+
 def dispatch_group(role: str, group_id: str, model: str, *, repo_dir: str = ".",
                    roster_ref: str | None = None, head: str = "", pr: str = "", nonce: str = "",
                    overlay: str | None = None, environ=None) -> str:
@@ -292,12 +334,9 @@ def dispatch_group(role: str, group_id: str, model: str, *, repo_dir: str = ".",
     if role == "reviewer":
         render(role, head, **args, nonce=BUS_PROBE_NONCE)  # every other refusal, before the bus records
         nonce = _bus_dispatch(repo_dir, pr, head, model, nonce, environ)
-    payload = render(role, head, **args, nonce=nonce)
-    ref = f"{DISPATCH_NS}/{role}-{topic}"
+    ref = dispatch_ref(role, topic, "")
     try:
-        _publish(repo_dir, ref, {
-            "PAYLOAD.json": json.dumps(payload),
-            "PROMPT.md": payload["job_config"]["ccr"]["events"][0]["data"]["message"]["content"]})
+        publish_seat(repo_dir, ref, role, head, **args, nonce=nonce)
     except Refusal:
         if role == "reviewer":  # the bus closed reviewer-fire for a seat that was never fired
             subprocess.run([sys.executable, "-I", str(HERE / "ledger.py"), *_ledger_log(environ), "open",
@@ -410,14 +449,23 @@ def _group_checks(check) -> None:
               line == "dispatch/fixer-r10-x" and "\n" not in line and " " not in line)
         brief = work / "brief.txt"
         brief.write_text(grp["brief"])
-        old = io.StringIO()
-        with contextlib.redirect_stdout(old):
-            rc = main(["--role", "fixer", "--head", tip, "--topic", "r10-x", "--brief", str(brief),
-                       "--env-id", "env_x", "--model", "m-1", "--repo", "owner/name"])
-        check("the printed line round-trips to a payload byte-identical to today's flag path",
+        flags = ["--role", "fixer", "--head", tip, "--topic", "r10-x", "--brief", str(brief),
+                 "--env-id", "env_x", "--model", "m-1", "--repo", "owner/name"]
+        plain, old = io.StringIO(), io.StringIO()
+        with contextlib.redirect_stdout(plain):
+            rc0 = main(flags)
+        with contextlib.chdir(work), contextlib.redirect_stdout(old):
+            rc = main([*flags, "--publish"])
+        check("the printed line round-trips to a payload byte-identical to the flag path's --publish",
               rc == 0 and fetched(line, "PAYLOAD.json") == old.getvalue().rstrip("\n"))
-        msg = json.loads(fetched(line, "PAYLOAD.json"))["job_config"]["ccr"]["events"][0]["data"]["message"]["content"]
-        check("the ref carries the prompt the payload carries", fetched(line, "PROMPT.md") == msg)
+        content = lambda text: json.loads(text)["job_config"]["ccr"]["events"][0]["data"]["message"]["content"]
+        msg = fetched(line, "PROMPT.md")
+        ptr = content(fetched(line, "PAYLOAD.json"))
+        check("the published payload's event is the pointer to the ref, under 600 chars; PROMPT.md is the prompt",
+              len(ptr) < 600 and f"origin ref {line} (`git fetch origin {line} && git show FETCH_HEAD:PROMPT.md`)"
+              in ptr and tip in ptr and msg.startswith("CLOUD FIXER") and msg not in ptr)
+        check("without --publish the flag path is unchanged: the whole prompt in its event, nothing published",
+              rc0 == 0 and content(plain.getvalue()) == msg)
         check("the roster brief is inlined and the roster tip is the head",
               "Fix the thing in tools/x.py." in msg and tip in msg)
         check("a re-dispatch of the same brief moves no ref", dispatch() == line
@@ -516,6 +564,17 @@ def _group_checks(check) -> None:
             published = False
         check("_publish itself refuses a ref that would publish the host, and pushes nothing",
               not published and "someone" not in git(work, "ls-remote", str(origin)))
+        out = io.StringIO()
+        with contextlib.chdir(work), contextlib.redirect_stdout(out):
+            rc = main(["--role", "reviewer", "--head", rhead, "--pr", "7", "--nonce", "abc123", "--publish",
+                       "--env-id", "env_x", "--model", "m-1", "--repo", "owner/name"])
+        try:
+            msg = fetched("dispatch/reviewer-rev-7", "PROMPT.md")
+        except subprocess.CalledProcessError:
+            msg = ""
+        check("a reviewer's flag-path --publish publishes to dispatch/reviewer-rev-<PR> and points there",
+              rc == 0 and "git fetch origin dispatch/reviewer-rev-7 " in content(out.getvalue())
+              and msg.startswith("CLOUD REVIEWER") and "Bus nonce: abc123." in msg)
         # Two sources, never one: the roster from the round's roster branch
         # (O17), the head from main. The branch is one commit ahead of main
         # with its own brief, so either swap shows.
@@ -603,6 +662,7 @@ def _flag_checks(check) -> None:
     import contextlib
     import io
     dests = {a.dest for a in _parser()._actions if a.dest != "help"}
+    switches = {a.dest for a in _parser()._actions if a.nargs == 0 and a.dest != "help"}
     check("every flag the parser accepts has a --group disposition in GROUP_FLAGS, and no other",
           dests == set(GROUP_FLAGS))
     calls: list = []
@@ -613,6 +673,8 @@ def _flag_checks(check) -> None:
             base = {"role": "fixer", "group": "G-BASE", "model": "m-base"}
             value = "probe" if dest == "role" else f"value-of-{dest}"
             argv = [x for k, v in {**base, dest: value}.items() for x in ("--" + k.replace("_", "-"), v)]
+            if dest in switches:  # a switch takes no value
+                argv = argv[:-1]
             calls.clear()
             with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                 rc = main(argv)
@@ -682,6 +744,22 @@ def self_test() -> int:
           all(sum(FOOTER_BAN in line for line in t.splitlines()) == 1 for t in prompts.values()))
     check("and no rendered prompt carries the attribution it bans (ref_privacy's classes: the null control)",
           all(ref_privacy.attribution(t) == [] for t in prompts.values()))
+    check("every role's prompt caps one tool call's wait under the 5-minute prompt-cache TTL (R10-FLY-CACHE-PROMPTS)",
+          all(WAIT_LINE in t and "240 s" in WAIT_LINE for t in prompts.values()))
+    check("the fixer reads its role file, not CLAUDE.md, which the harness already loaded",
+          "dev/governance/roles/fixer.md" in prompts["fixer"] and "CLAUDE.md" not in prompts["fixer"])
+    for role, ref in (("fixer", "dispatch/fixer-t-1"), ("reviewer", "dispatch/reviewer-rev-7")):
+        a = dict(pr="7" if role == "reviewer" else "", topic="" if role == "reviewer" else "t-1",
+                 nonce="abc123" if role == "reviewer" else "")
+        check(f"the {role}'s publish ref is {ref}", dispatch_ref(role, a["topic"], a["pr"]) == ref)
+        ptr = render(role, head, **base, **a, publish_ref=ref)["job_config"]["ccr"]["events"][0]["data"][
+            "message"]["content"]
+        check(f"a published {role}'s event is a pointer: under 600 chars, names the ref, the head and PROMPT.md",
+              len(ptr) < 600 and f"git fetch origin {ref} && git show FETCH_HEAD:PROMPT.md" in ptr
+              and head in ptr and FOOTER_BAN not in ptr and len(ptr) < len(prompts[role]))
+    check("a reviewer's pointer carries its nonce", "abc123" in render(
+        "reviewer", head, **base, pr="7", nonce="abc123", publish_ref="dispatch/reviewer-rev-7")[
+        "job_config"]["ccr"]["events"][0]["data"]["message"]["content"])
     check("a 39-hex head is refused", refused(h=head[:-1]))
     check("a 41-hex head is refused", refused(h=head + "0"))
     check("an upper-case head is refused", refused(h=head.upper()))
@@ -723,6 +801,7 @@ GROUP_FLAGS = {
     "repo": "the roster gives the repository",
     "env_id": "the environment id comes from the overlay or $HPO_CLOUD_ENV_ID",
     "out": "--group publishes the payload to its ref and prints the ref name",
+    "publish": "--group always publishes",
 }
 
 
@@ -742,6 +821,8 @@ def _parser() -> argparse.ArgumentParser:
     ap.add_argument("--repo")
     ap.add_argument("--overlay")
     ap.add_argument("--out")
+    ap.add_argument("--publish", action="store_true", help="publish PROMPT.md to dispatch/<role>-<topic or "
+                    "rev-PR> and fire the seat with a pointer to it")
     return ap
 
 
@@ -768,8 +849,12 @@ def main(argv: list[str]) -> int:
                 brief = Path(args.brief).read_text()
             except OSError as e:
                 raise Refusal(f"unreadable brief: {e.__class__.__name__}")
-        payload = render(args.role, args.head, pr=args.pr, topic=args.topic, nonce=args.nonce,
-                         brief=brief, **_config(args))
+        known = dict(pr=args.pr, topic=args.topic, nonce=args.nonce, brief=brief, **_config(args))
+        if args.publish:
+            payload = publish_seat(".", dispatch_ref(args.role, args.topic, args.pr), args.role, args.head,
+                                   **known)
+        else:
+            payload = render(args.role, args.head, **known)
     except Refusal as e:
         print(f"cloud_dispatch: refused: {e}", file=sys.stderr)
         return 2
diff --git a/tools/audit/seat/proof_watch.py b/tools/audit/seat/proof_watch.py
index 5378b9a1d..e43748235 100644
--- a/tools/audit/seat/proof_watch.py
+++ b/tools/audit/seat/proof_watch.py
@@ -138,11 +138,18 @@ def _train():
     return merge_train
 
 
+#: Seconds between polls: under a waiting seat's 5-minute prompt-cache TTL, so
+#: the wake that follows a poll does not rewrite its whole context
+#: (R10-FLY-CACHE-PROMPTS), and never under GitHub's 60 s floor (main refuses it).
+POLL_S = 240.0
+POLL_FLOOR_S = 60.0
+
+
 class Watcher:
     """One watch: one pull request, one pinned head, one named check-run."""
 
     def __init__(self, repo: str, pr: int, sha: str, check: str,
-                 poll: float = 300.0, budget_h: float = 6.0,
+                 poll: float = POLL_S, budget_h: float = 6.0,
                  dry: bool = False, mode: str = "app", state: Path = DEFAULT_STATE,
                  merge_script: Path | None = None, approve_script: Path | None = None,
                  run=None, sleep=time.sleep, clock=time.monotonic, say=print,
@@ -375,7 +382,7 @@ def main(argv: list[str] | None = None) -> int:
     ap.add_argument("--head", help="the pinned 40-hex head SHA; never followed")
     ap.add_argument("--check", help="the name of the check-run to wait for")
     ap.add_argument("--repo", default=DEFAULT_REPO, help="owner/repo (default %(default)s)")
-    ap.add_argument("--poll", type=float, default=300.0, help="seconds between polls (default %(default)s)")
+    ap.add_argument("--poll", type=float, default=POLL_S, help="seconds between polls (default %(default)s)")
     ap.add_argument("--budget", type=float, default=6.0, help="hours before aborting (default %(default)s)")
     ap.add_argument("--mode", choices=("app", "owner"), default="app",
                     help="the merge identity merge_pr.sh is handed (default %(default)s)")
@@ -389,6 +396,10 @@ def main(argv: list[str] | None = None) -> int:
         if v is None:
             print(f"proof_watch: REFUSE: {flag} is required (or --self-test)", file=sys.stderr)
             return 2
+    if a.poll < POLL_FLOOR_S:
+        print(f"proof_watch: REFUSE: --poll under GitHub's {POLL_FLOOR_S:.0f} s floor, got {a.poll}",
+              file=sys.stderr)
+        return 2
     if not (len(a.head) == 40 and set(a.head) <= HEX):
         print(f"proof_watch: REFUSE: --head must be the full 40-hex SHA, got '{a.head}'", file=sys.stderr)
         return 2
@@ -412,6 +423,7 @@ def main(argv: list[str] | None = None) -> int:
 # pairs, and the dry-run arm asserts the tree it was given is untouched.
 
 def self_test() -> int:
+    import io
     import shutil
     import tempfile
 
@@ -435,6 +447,17 @@ def self_test() -> int:
             print(f"FAIL {why} (got {got!r}, want {want!r})")
             fails += 1
 
+    # The cadence (R10-FLY-CACHE-PROMPTS): under the seat's 5-minute prompt-cache
+    # TTL, never under GitHub's 60 s poll floor. The --poll 60 case is the null
+    # control: it passes the poll guard and is refused at --head instead.
+    st(60.0 <= POLL_S <= 240.0, True, "the default poll is inside [60 s, 240 s]")
+    for poll, flag in (("59", "--poll"), ("60", "--head")):
+        err = io.StringIO()
+        with contextlib.redirect_stderr(err):
+            rc = main(["--pr", "7", "--head", "short", "--check", "x", "--poll", poll])
+        st((rc, flag in err.getvalue().split("REFUSE: ", 1)[-1][:8]), (2, True),
+           f"--poll {poll} is refused at {flag}")
+
     class Fixture:
         def __init__(self):
             self.root = W / f"case{len(cases)}"

