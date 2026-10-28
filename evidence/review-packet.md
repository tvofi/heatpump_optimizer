# Review packet #2935
head: 89b04b74feaef1c0696fca1f353c9532c6792374
base: b0b2d7697f8c5baaef2c082d9bf3242b57249e68

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=123118659247 neutral
arch-score / arch-score id=123118369121 success
arm id=123118266925 skipped
budget-raise-gate / budget-raise-gate id=123118369244 success
cancel-superseded id=123118189674 success
codeql / Analyze (actions) id=123118369098 success
codeql / Analyze (javascript-typescript) id=123118369023 success
codeql / Analyze (python) id=123118369085 in_progress
governance / delivery-status id=123118369025 success
governance / delivery-status-publish id=123118370831 skipped
governance / env-matrix id=123118369160 in_progress
governance / instrument-self-tests id=123118369448 in_progress
governance / policy-docs id=123118369208 success
governance / record id=123118370916 skipped
governance / wave-script id=123118369172 success
hassfest / hassfest id=123118368905 success
kernel-points id=123118370319 skipped
prelude id=123118189548 success
refresh id=123118189434 success
tests / arch-instrument id=123118551238 success
tests / briefs id=123118368970 success
tests / browser id=123118551048 in_progress
tests / closure-scope id=123118368817 success
tests / closures id=123118551321 in_progress
tests / coverage id=123118551094 in_progress
tests / fast (3.14) id=123118551109 in_progress
tests / mutation id=123118369308 success
tests / mutation-autofix id=123118746834 skipped
tests / mutation-pins id=123118745868 skipped
tests / nightly-ha id=123118553565 skipped
tests / nightly-status id=123118368869 success
tests / replay id=123118554201 skipped
tests / typing id=123118551044 success
validate / validate-hacs id=123118369034 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/audit/seat/sweep_render.py --self-test
             `tools/audit/seat/sweep_render.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tests/closure.py select
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 5 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/2935.md b/dev/programme/delivery/2935.md
new file mode 100644
index 000000000..6274203ca
--- /dev/null
+++ b/dev/programme/delivery/2935.md
@@ -0,0 +1 @@
+- [#2935](https://github.com/tvofi/heatpump_optimizer/pull/2935) — **open**, R10-FLY-SWEEP-DEFAULTS: the orchestrator's sweep additions become template defaults (R10-FLY-SWEEP-DEFAULTS)
diff --git a/tests/closures.json b/tests/closures.json
index 6063b8d8c..824f360b5 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3614,6 +3614,7 @@
    "tools/audit/seat/selftest_wiring.py",
    "tools/audit/seat/sweep_driver.py",
    "tools/audit/seat/sweep_driver_selftest.py",
+   "tools/audit/seat/sweep_render.py",
    "tools/audit/seat/tmp_paths.py",
    "tools/policy/budget_raise_gate.py",
    "tools/policy/figure_lint.mjs",
diff --git a/tools/audit/seat/sweep_render.py b/tools/audit/seat/sweep_render.py
index f941cd629..1fe34ea35 100644
--- a/tools/audit/seat/sweep_render.py
+++ b/tools/audit/seat/sweep_render.py
@@ -62,6 +62,17 @@ PLACEHOLDER = re.compile(r"\{\{([A-Za-z0-9_]*)\}\}")
 TABLE_ROW = re.compile(r"^\|\s*`([A-Za-z0-9_]+)`\s*\|")
 CITED = re.compile(r"`((?:tools|tests|dev|\.github)/[^`\s{}<>*]+|CLAUDE\.md)[^`]*`")
 HOST = re.compile(HOME_DIR)
+#: What every rendered sweep carries by default (tvofi, 2026-10-28: round 10's
+#: session additions became the template's defaults). One fragment per default
+#: the self-test pins; the template is still the one owner of the wording.
+DEFAULTS = {
+    "record beat: the replan": "tools/plan/replan.py --out",
+    "record beat: the plan page": "tools/audit/seat/plan_page.py --plan",
+    "tick board read unfiltered": "REVIEW OWED",
+    "tick board: owner flags": "OWNER FLAG:",
+    "tick board: design builds": "DESIGN-BUILD:",
+    "train flags": "--overlap --approval-carry --skip-bad --free-holders --bot-prs --pre-flight",
+}
 
 
 class Refused(Exception):
@@ -96,6 +107,11 @@ def citations(text: str, root: Path) -> list[str]:
     return sorted({m.group(1) for m in CITED.finditer(text) if not (root / m.group(1)).exists()})
 
 
+def defaults_missing(sweep: str) -> list[str]:
+    """The DEFAULTS a sweep body lacks, by name."""
+    return [name for name, frag in DEFAULTS.items() if frag not in sweep]
+
+
 def value_text(name: str, v) -> str:
     if isinstance(v, bool) or not isinstance(v, (str, int)):
         raise Refused(f"unfilled: `{name}` is a {type(v).__name__}, not a string or an integer")
@@ -163,16 +179,24 @@ def self_test() -> int:
     tracked = TEMPLATE.read_text(encoding="utf-8")
     names = declared(tracked)
     full = {n: f"<{n}>" for n in names}
-    full["local_seat_cap"] = 8
+    full["plan_slots"] = 10
     try:
         text = render(tracked, full)
-        ok = all(f"<{n}>" in text for n in names if n != "local_seat_cap") and "{{" not in text
+        ok = all(f"<{n}>" in text for n in names if n != "plan_slots") and "{{" not in text
     except Refused as e:
         print(f"    {e}")
         ok = False
     check("the tracked template renders from a complete overlay, every placeholder filled (null control)", ok)
     check("the tracked template cites only paths that exist", citations(tracked, ROOT) == [])
     check("the tracked template's sweep names no host", not HOST.search(body(tracked)))
+    missing = defaults_missing(body(tracked))
+    if missing:
+        print("    missing: " + ", ".join(missing))
+    check("the tracked template's sweep carries every round-10 default", not missing)
+    every = "\n".join(DEFAULTS.values())
+    check("a sweep carrying every default fragment misses none (null control)", defaults_missing(every) == [])
+    check("a sweep without the train flags is reported missing exactly them",
+          defaults_missing(every.replace(DEFAULTS["train flags"], "")) == ["train flags"])
 
     mini = "## Placeholders\n\n| `a` | x |\n| `b` | y |\n\n## Other\n\n" + BEGIN + "\nrun {{a}} then {{b}}\n" + END + "\n"
     check("a minimal template renders (null control for the refusals below)",
diff --git a/tools/audit/seat/sweep_template.md b/tools/audit/seat/sweep_template.md
index 6341b938d..450b1c35b 100644
--- a/tools/audit/seat/sweep_template.md
+++ b/tools/audit/seat/sweep_template.md
@@ -33,10 +33,10 @@ rendered text that no overlay value supplied.
 | `orch_scratch` | the orchestration scratch directory (not a worktree) |
 | `orch_checkout` | the orchestrator's own checkout, fetched before every re-read |
 | `seat_ledger` | the session's seat ledger file, updated every sweep |
-| `local_seat_cap` | the most local seats the session runs at once |
-| `cloud_above_cap` | whether cloud seats count above that cap (`yes` or `no`) |
-| `plan_generator` | the command that regenerates the plan artifact |
-| `plan_artifact` | the plan artifact's path, republished at the same path |
+| `plan_slots` | `replan.py --slots`: concurrent fixer slots the plan schedules (10 unless the owner set another) |
+| `plan_seats` | `replan.py --seats`: seats the plan may use (99 unless the owner set another) |
+| `plan_json` | the plan JSON `replan.py --out` writes and `plan_page.py --plan` reads |
+| `plan_page` | the plan page `plan_page.py --html` writes, republished at the same path |
 | `state_mirror` | the directory `state_docs.py --mirror` writes |
 | `tick_alive` | the tick seat's liveness file, touched every pass |
 | `tick_log` | the tick seat's log |
@@ -50,19 +50,27 @@ rendered text that no overlay value supplied.
 <!-- sweep:begin -->
 ORCHESTRATOR SWEEP, round {{round}}, repository {{repo}}. Read {{seat_ledger}} first. Run each instrument from its path in the tree, from {{orch_checkout}}, with `tools/audit/seat/shims` first on PATH. Then, briefly:
 
-(0) Policy re-read. Run `python3 -I tools/audit/seat/policy_reread_check.py --transcript {{transcript}} --stamp {{policy_stamp}}`. On OWED: `git -C {{orch_checkout}} fetch origin`, then read `CLAUDE.md`, every policy file its index names, and `tools/audit/seat/INSTRUMENTS.md` with `git -C {{orch_checkout}} show origin/main:<path>`; act on any delta against current practice; then `python3 -I tools/audit/seat/policy_reread_check.py --stamp {{policy_stamp}} --write-stamp`, and log the re-read in {{seat_ledger}}.
+(0) Policy re-read. Run `python3 -I tools/audit/seat/policy_reread_check.py --transcript {{transcript}} --stamp {{policy_stamp}}`. On OWED: `git -C {{orch_checkout}} fetch origin`, then read `CLAUDE.md`, every policy file its index names, and `tools/audit/seat/INSTRUMENTS.md` with `git -C {{orch_checkout}} show origin/main:<path>`; act on any delta against current practice; then `python3 -I tools/audit/seat/policy_reread_check.py --stamp {{policy_stamp}} --write-stamp`, and log the re-read in {{seat_ledger}}. While the check prints OWED (exit 1), that is, until `--write-stamp` ran after the newest compaction, this sweep is not clean, whatever the rest of the board says.
 
-(1) Seats. Run at most {{local_seat_cap}} local seats; cloud seats count above that cap: {{cloud_above_cap}}. Below the cap, resume the next queued seat from {{seat_ledger}}. Seat worktrees live under {{seat_root}}, each named absolute in its brief (`dev/governance/roles/orchestrator.md` section 5). A handed-off seat is not resumed and an unblocked roster group gets a fixer (`dev/governance/roles/nudge.md` steps 14 and 16).
+(1) Seats. Cloud seats are uncapped. A fixer for a NEW roster group is dispatched only while fewer than 3 handoffs wait without a pull request and 6 to 10 pull requests are open (owner ruling, 2026-10-28; `tools/audit/seat/pr_cap.py` `dispatch-gate` measures its WIP arm); reviews, repairs and openers are never capped, and a ready critical-path group dispatches past every cap (`dev/governance/roles/orchestrator.md` section 5). Resume the next queued seat from {{seat_ledger}}. Dispatch a record pull request's reviewer (triage, roster batches) on sonnet, and a design, code or architecture pull request's reviewer on opus. Seat worktrees live under {{seat_root}}, each named absolute in its brief (`dev/governance/roles/orchestrator.md` section 5). A handed-off seat is not resumed and an unblocked roster group gets a fixer (`dev/governance/roles/nudge.md` steps 14 and 16).
 
 (1b) Standing-seat liveness. The four standing seats are `dev/governance/roles/standing-tick.md`, `dev/governance/roles/standing-merge.md`, `dev/governance/roles/standing-dispatch.md` and `dev/governance/roles/standing-roster.md`. Run `python3 -I tools/audit/seat/pulse.py --repo {{repo}} {{seat_queues}}`; a seat that is absent from {{seat_ledger}}, that finished with work still owed, or that a `PULSE` line reports `STOPPED seat <name>:` is restarted in this sweep on its contract with its queue, and the restart is logged in {{seat_ledger}}. Routine work goes to these seats as queue lines, never inline (`dev/governance/roles/orchestrator.md` section 5).
 
 (2) Handoffs. Compare `git ls-remote --heads origin 'handoff/r{{round}}-*'` with the open pull-request heads, and run `tools/audit/seat/bus.sh orphans`. A handoff with no pull request gets `tools/audit/seat/open_pr.sh`; one ahead of its pull request gets `tools/audit/seat/update_pr.sh`; each runs detached under `tools/audit/seat/daemonize.py`, then `tools/pr/approve_held_runs.sh` on that branch, then `tools/audit/seat/bus.sh dispatch` and a reviewer seat at the printed head (`dev/governance/roles/orchestrator.md` section 5b; `dev/governance/roles/nudge.md` steps 1, 2 and 8).
 
-(3) Merges. Verdicted pull requests go to one train on the hourly pitch: `tools/audit/seat/merge_train.py sweep --state-dir {{orch_scratch}} --mandate {{mandate}}` (detached under `tools/audit/seat/daemonize.py`; `tools/audit/seat/tick_loop.sh --sweep` runs it from the tick loop) builds the queue from the verdict bus and `add`s each verdicted head, starting `tools/audit/seat/train.sh --bot-prs --approval-carry --pre-flight` when no train is running and otherwise loading that train's next batch, never a second live train (`dev/governance/roles/nudge.md` step 3; `dev/governance/roles/orchestrator.md` section 11). The open record or autofix pull request merges inside that train through `--bot-prs`, not between pitches. A budget-file or policy head goes the batch's serial route, where `--pre-flight` parks a budget raise or a policy head the owner has not approved at that head under an open mandate (`Train.raise_hold`, `Train.policy_gate`); a parked one merges directly under mandate {{mandate}} (`dev/governance/roles/nudge.md` steps 5 and 7; `CLAUDE.md` rule 2). Between pitches, a record or autofix pull request merges by hand only behind `tools/audit/seat/record_row.py --automerge-check` (`dev/governance/roles/nudge.md` step 6).
+(3) Merges. Verdicted pull requests go to one train on the hourly pitch: `tools/audit/seat/merge_train.py sweep --state-dir {{orch_scratch}} --mandate {{mandate}}` (detached under `tools/audit/seat/daemonize.py`; `tools/audit/seat/tick_loop.sh --sweep` runs it from the tick loop) builds the queue from the verdict bus and `add`s each verdicted head, starting `tools/audit/seat/train.sh` with `--overlap --approval-carry --skip-bad --free-holders --bot-prs --pre-flight --mandate {{mandate}}`, the recommended default (`dev/governance/roles/standing-merge.md`), when no train is running and otherwise loading that train's next batch, never a second live train (`dev/governance/roles/nudge.md` step 3; `dev/governance/roles/orchestrator.md` section 11). The open record or autofix pull request merges inside that train through `--bot-prs`, not between pitches. A budget-file or policy head goes the batch's serial route, where `--pre-flight` parks a budget raise or a policy head the owner has not approved at that head under an open mandate (`Train.raise_hold`, `Train.policy_gate`); a parked one merges directly under mandate {{mandate}} (`dev/governance/roles/nudge.md` steps 5 and 7; `CLAUDE.md` rule 2). Between pitches, a record or autofix pull request merges by hand only behind `tools/audit/seat/record_row.py --automerge-check` (`dev/governance/roles/nudge.md` step 6).
 
-(4) After each merge (`dev/governance/roles/nudge.md` steps 12 and 18): `tools/audit/seat/roster_edit.py set-stage` for a roster group, one #201 comment through `tools/pr/gh_comment.py` with its read-back, `tools/audit/worktree_gc.sh {{repo}}`, the issues the merge commit closed read back (`dev/governance/roles/orchestrator.md` section 4), the finished seat's worktrees under {{seat_root}} and its scratch removed, `tools/audit/seat/state_docs.py --push --mirror {{state_mirror}}`, and the plan artifact regenerated with `{{plan_generator}}` and republished at {{plan_artifact}}.
+(4) After each merge (`dev/governance/roles/nudge.md` steps 12 and 18): `tools/audit/seat/roster_edit.py set-stage` for a roster group, one #201 comment through `tools/pr/gh_comment.py` with its read-back, `tools/audit/worktree_gc.sh {{repo}}`, the issues the merge commit closed read back (`dev/governance/roles/orchestrator.md` section 4), and the finished seat's worktrees under {{seat_root}} and its scratch removed.
 
-(5) Tick watcher. If {{tick_alive}} is missing or older than {{tick_stale_min}} minutes, the tick seat has died: start a new one in the background on `dev/governance/roles/standing-tick.md`, whose prompt is the contents of {{tick_brief}}; it runs `tools/audit/seat/orchestrator_tick.py`. Log the restart in {{seat_ledger}}. Act on the newest actionable lines of {{tick_log}}; the tick only lists, the sweep acts (`tools/audit/seat/INSTRUMENTS.md`, `orchestrator_tick.py`). The `pulse.py` lines step (1b) printed name each consumer whose owed input is waiting on it (opener, verdict router or train, state beat, a standing seat's queue): drive that consumer before the rest of the sweep, and log it in {{seat_ledger}}; `UNREADABLE` is not a clean board.
+(4b) Record beat, every sweep, merge or none: `tools/audit/seat/state_docs.py --push --mirror {{state_mirror}}`, then `python3 tools/plan/replan.py --out {{plan_json}} --slots {{plan_slots}} --seats {{plan_seats}}`, then `python3 tools/audit/seat/plan_page.py --plan {{plan_json}} --html {{plan_page}}`, republished at the same path.
+
+(4c) Open pull requests. Reconcile every open pull request to one bucket, with its reason: in train, review out, fixer out, CI wait, or owner-held; none waits without one; critical path first.
+
+(4d) Queue priority, for the train, review, fixer and CI queues alike: a push to main; then critical path and hotfix; then production pull requests with instrument pull requests saving 12 h or more; then other instruments by savings. A group's critical-path standing is the roster's `critical` list (`tools/audit/seat/roster_lib.py` `critical_path`); the gate order is `tools/pr/gate_priority.py`'s.
+
+(4e) CI capacity. Cancel each superseded workflow run, one whose head is no longer its pull request's head: read `gh run list --json databaseId,headSha,headBranch,status,event` against each open pull request's `headRefOid`, and `gh run cancel` the stale ones. Never cancel a run on main or on a critical-path or hotfix pull request's live head. `tools/pr/cancel_superseded.py` does the same from inside one workflow run.
+
+(5) Tick watcher. If {{tick_alive}} is missing or older than {{tick_stale_min}} minutes, the tick seat has died: start a new one in the background on `dev/governance/roles/standing-tick.md`, whose prompt is the contents of {{tick_brief}}; it runs `tools/audit/seat/orchestrator_tick.py`. Log the restart in {{seat_ledger}}. Read {{tick_log}}'s newest pass unfiltered: every `OWED`, `REVIEW OWED`, `DISPATCH:`, `OWNER FLAG:` and `DESIGN-BUILD:` line, none truncated, and give each an action this sweep (`dev/governance/roles/standing-tick.md`); the tick only lists, the sweep acts (`tools/audit/seat/INSTRUMENTS.md`, `orchestrator_tick.py`). The `pulse.py` lines step (1b) printed name each consumer whose owed input is waiting on it (opener, verdict router or train, state beat, a standing seat's queue): drive that consumer before the rest of the sweep, and log it in {{seat_ledger}}; `UNREADABLE` is not a clean board.
 
 (6) Verdicts and CI. Read any moved `review/*` or `probe/*` refs and the cloud runs; confirm each verdict at its exact head with `tools/audit/seat/bus.sh confirm` (`dev/governance/roles/nudge.md` step 1). A red required check at an open head goes back to its fixer with the line `tools/audit/seat/failure_logs.sh` prints (`dev/governance/roles/nudge.md` steps 4 and 15).
 

