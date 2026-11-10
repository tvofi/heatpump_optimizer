# Review packet #3383
head: e8c3fe927bb9a1d070f458d6aed9173d8a8bb192
base: d9af08062a611c507537c7ba2c73872c5b6de8ee

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=129436132229 success
arch-score / arch-score id=129457143198 success
arm id=129435674081 skipped
budget-raise-gate / budget-raise-gate id=129457141925 success
cancel-superseded id=129457140696 success
codeql id=129457141560 skipped
codeql / Analyze (actions) id=129436013251 success
codeql / Analyze (javascript-typescript) id=129436013351 success
codeql / Analyze (python) id=129436013443 success
gate id=129457141302 success
governance id=129457141766 skipped
governance / delivery-status id=129436013509 success
governance / delivery-status-publish id=129436016450 skipped
governance / env-matrix id=129436013513 success
governance / instrument-self-tests id=129436013495 success
governance / policy-docs id=129436013637 success
governance / record id=129436016067 skipped
governance / wave-script id=129436013595 success
hassfest id=129457142217 skipped
hassfest / hassfest id=129436013110 success
kernel-points id=129457141611 skipped
pr-contract id=129457142774 skipped
pr-contract / pr-contract id=129455325717 success
prelude id=129457139970 success
refresh id=129457191961 success
tests id=129457141298 skipped
tests / arch-instrument id=129436318481 success
tests / briefs id=129436013356 success
tests / browser id=129436318484 success
tests / ci-ratchet id=129454825045 skipped
tests / claims-autofix id=129438054917 skipped
tests / closure-scope id=129436013213 success
tests / closures id=129436318569 success
tests / closures-autofix id=129438960889 skipped
tests / coverage id=129436318692 success
tests / coverage-ratchet id=129454820756 success
tests / fast (3.14) id=129436318503 success
tests / graders-head-copy id=129454820674 success
tests / lane-proofs id=129454820721 success
tests / mutation id=129436013298 success
tests / mutation-autofix id=129436504724 skipped
tests / mutation-pins id=129436504741 skipped
tests / nightly-ha id=129436321094 skipped
tests / nightly-status id=129436013255 success
tests / replay id=129436322215 skipped
tests / typing id=129436318945 success
validate id=129457141867 skipped
validate / validate-hacs id=129436013438 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git diff --stat 294a880da...65c333b2f25e03cb0953ec77784cf55933beb9ba
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 0 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3383.md b/dev/programme/delivery/3383.md
new file mode 100644
index 000000000..7eead56c9
--- /dev/null
+++ b/dev/programme/delivery/3383.md
@@ -0,0 +1 @@
+- [#3383](https://github.com/tvofi/heatpump_optimizer/pull/3383) — **open**, triage: s12-batch130  (R10-TRIAGE-S12)
diff --git a/dev/programme/triage/s6-batch130.md b/dev/programme/triage/s6-batch130.md
new file mode 100644
index 000000000..afc994dde
--- /dev/null
+++ b/dev/programme/triage/s6-batch130.md
@@ -0,0 +1,31 @@
+# Proposal triage, session s12, batch 130 (P401)
+
+The rolling batch after batch 129. Facts were read at origin/main `294a880da` and at the roster branch `11940e1dd`, and in the orchestration logs. The logs and the tools worktrees are host-local, so another seat re-runs those commands only on the host that holds them.
+
+## P401: update-pr-tools-root, the freshness check measures the main checkout
+
+Verdict: ACCEPT narrowed. The defect is real and reproduced, but its mechanism is not the one the queue line names, so the fix changes. `pr_tools_fresh` already measures the checkout holding the sourced `pr_args.sh`. It resolves that directory from `${BASH_SOURCE[0]}` when it is called, not when the file is sourced. A seat that runs `bash tools/audit/seat/update_pr.sh` by a relative path sources a relative `pr_args.sh`. `update_pr.sh` then runs `cd "$M"` (line 53, the git-common-dir parent) before `pr_tools_fresh` (line 62), so the relative path resolves inside the main checkout. `open_pr.sh` has the same order, `cd "$M"` at line 42 and `pr_tools_fresh` at line 95. The fix resolves the directory once, when the file is sourced. It does not change what is measured. Destination R10-HANDOFF-PATH (carries-open), which owns `update_pr.sh`, `open_pr.sh` and `pr_args.sh`. This ACCEPT is not taken on the >10 % exemption.
+
+Source: the orchestrator's queue line `s12-update-pr-tools-root`, 2026-11-07.
+
+Instances:
+- **The code:** `git show origin/main:tools/audit/seat/pr_args.sh` lines 168 to 179. `pr_tools_fresh` sets `d=$(cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)` on each call. `update_pr.sh` sources it as `. "$(dirname -- "$0")/pr_args.sh"` (line 34). Its other paths, `SEAT`, `PRT` and `M` (lines 39 and 43), are made absolute before the `cd`. So the run executes the invoking worktree's code and only the freshness check reads the main checkout. No stale code ran; the guard was the only casualty.
+- **Reproduction:** a detached worktree at origin/main `294a880da`, a probe that sources `pr_args.sh` by `$(dirname -- "$0")`, optionally runs `cd` into the main checkout, then calls `pr_tools_fresh`:
+  - relative `$0`, no `cd`: FRESH;
+  - absolute `$0`, `cd` to the main checkout: FRESH;
+  - relative `$0`, `cd` to the main checkout: `REFUSE: STALE CHECKOUT 5a04096d1711 behind origin/main 294a880dae60 by 175 commit(s)`, naming the main checkout's `tools/audit/seat`. That is the defect.
+- **Main checkout lag:** `git -C <main checkout> rev-list --count HEAD..origin/main -- tools/audit/seat tools/pr` gives 175, and 2238 over all paths. HEAD is `5a04096d1`, committed 2026-11-04.
+- **The live seat:** the dispatch seat's update scripts `cd` into its tools worktree `upd-tools-31` and run `bash tools/audit/seat/update_pr.sh` by a relative path. That worktree is at `294a880da`, and `rev-list --count HEAD..origin/main -- tools/audit/seat tools/pr` gives 0. Yet its `upd-3244.out` reads `update_pr: NOTICE: STALE CHECKOUT 5a04096d1711 ... HPO_ALLOW_STALE_TOOLS is set`. 47 of its 47 `run*.sh` scripts export `HPO_ALLOW_STALE_TOOLS=1` (`grep -c`).
+- **The guard is off:** `grep -rhsoE '(update|open)_pr: NOTICE: STALE CHECKOUT [0-9a-f]+'` over the orchestration logs. 77 notices (46 `update_pr`, 31 `open_pr`, in 69 files, 2026-11-04 to 2026-11-07) name `5a04096d1711`, the main checkout's HEAD. Each of those runs went ahead with the check bypassed, so a tools worktree that really was stale would not have been refused either. The check exists for #2664, where a stale checkout wrote a Co-Authored-By delivery row.
+- **What is not the defect:** of the 149 `update_pr: REFUSE: STALE CHECKOUT` lines, 118 name `orch-wt` or `orch-wt2`, both invoked by absolute path. Those trees really were stale, so the check fired correctly. Of the 12 refusals that name the main checkout, the one traced (`s7/push-queue-16.sh`, `cd` to the main checkout itself) was a correct firing. The relay is unaffected: it runs `update_pr.sh` by absolute path from its levelled `relay-tools` tree (P283).
+- **The rule on the instance:** in the same worktree, `pr_args.sh` was patched to set `PR_ARGS_DIR=$(cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)` at source time, and `pr_tools_fresh` was changed to `d=$PR_ARGS_DIR`. That is two lines added and one removed. With the patch, relative `$0` followed by `cd` to the main checkout gives FRESH. As a null control, `PR_ARGS_DIR` was pointed at the main checkout's tools, and the patched function still refuses with `STALE CHECKOUT 5a04096d1711 ... by 175`. The patch was then reverted.
+
+Cost:
+- About 3 changed lines in `pr_args.sh`, plus one self-test arm of about 10 lines in its existing `fresh` block. The arm runs `update_pr.sh` by a relative path from a fresh clone whose common checkout is stale. It must not refuse, and a mutant that restores call-time resolution must refuse. It is an S part inside an existing group: a sonnet fixer and one review.
+- `pr_args.sh` is hot (30 commits on origin/main since 2026-10-24), but the change is confined to one function and one top-level assignment. There is no API call and no standing cost.
+- No `tests/structure_budgets.json` metric reads shell, and neither file is a `policy_lint.mjs --budgets` row.
+- Benefit: the stale-tools guard is restored for every relative invocation, which is the dominant form: 159 relative against 7 absolute `update_pr.sh` and `open_pr.sh` invocations in the orchestration scripts and briefs (`grep -rhsoE`). The standing `HPO_ALLOW_STALE_TOOLS=1` can then come off the dispatch seat's scripts, where it now disables the check in 47 of 47 runs. A check that is bypassed on every run moves no right-first-time; once restored, it again refuses a stale tools tree before it writes.
+
+Binding:
+- Carry text: `From triage batch 130 (triage: dev/programme/triage/s6-batch130.md#P401 at <roster sha>): pr_tools_fresh in tools/audit/seat/pr_args.sh resolves its directory from BASH_SOURCE when called, after update_pr.sh (line 53) and open_pr.sh (line 42) have run cd "$M" to the main checkout. A relative invocation (bash tools/audit/seat/update_pr.sh from a fresh tools worktree) therefore measures the main checkout and refuses, so seats run with HPO_ALLOW_STALE_TOOLS=1 always. Resolve the directory once at source time (an absolute PR_ARGS_DIR beside PR_FRESH_PATHS) and read it in pr_tools_fresh; do not change which checkout is measured. Self-test arm in the existing fresh block: update_pr.sh run by a relative path from a fresh worktree whose common checkout is behind origin/main passes the check; a mutant that restores call-time resolution refuses; the existing stale-tools arms stay green. Afterwards the dispatch seat drops HPO_ALLOW_STALE_TOOLS=1 from its update scripts.`
+- The fixer re-measures the lag and the notice counts at its own base and does not carry them.

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
