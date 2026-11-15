# Review packet #3626
head: f475901cacf05fc6b106610d90db01cff7e08a07
base: ebe83a1b8265b56bde009b70185585e736dbdb82

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=132977777390 success
arch-score / arch-score id=132985378467 success
arm id=132977549583 skipped
budget-raise-gate / budget-raise-gate id=132985407479 success
cancel-superseded id=132985401908 success
codeql id=132985377696 skipped
codeql / Analyze (actions) id=132977718751 success
codeql / Analyze (javascript-typescript) id=132977718767 success
codeql / Analyze (python) id=132977718885 success
gate id=132985362062 success
governance id=132985362858 skipped
governance / env-matrix id=132977718691 success
governance / instrument-self-tests id=132977718713 success
governance / policy-docs id=132977718696 success
governance / record id=132977720127 skipped
governance / wave-script id=132977718728 success
hassfest id=132985392133 skipped
hassfest / hassfest id=132977718667 success
kernel-points id=132985362910 skipped
pr-contract id=132985362989 skipped
pr-contract / pr-contract id=132984763687 success
prelude id=132985362090 success
refresh id=132985393787 success
sweep-self id=132985609452 skipped
tests id=132985392476 skipped
tests / arch-instrument id=132977978477 success
tests / briefs id=132977718718 success
tests / browser id=132977978442 success
tests / ci-ratchet id=132983713279 skipped
tests / claims-autofix id=132982495505 skipped
tests / closure-scope id=132977718725 success
tests / closures id=132977978542 success
tests / closures-autofix id=132982754595 skipped
tests / coverage id=132977978500 success
tests / coverage-ratchet id=132983711474 success
tests / fast (3.14) id=132977978493 success
tests / graders-head-copy id=132983711415 success
tests / lane-proofs id=132983711504 success
tests / mutation id=132977718746 success
tests / mutation-autofix id=132977989929 skipped
tests / mutation-pins id=132977989817 skipped
tests / nightly-ha id=132977979871 skipped
tests / nightly-status id=132977718747 success
tests / replay id=132977979513 skipped
tests / typing id=132977978468 success
validate id=132985394026 skipped
validate / validate-hacs id=132977718655 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 4b4249e2: R11-INTAKE-R10-RESIDUE
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         node tools/policy/policy_lint.mjs --budgets
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         python3 tools/audit/seat/hooks_setup.py --self-test
             `tools/audit/seat/hooks_setup.py` is in the tree at this head
  ok         python3 -I tools/audit/check_scopes.py --self-test --repo .
             `tools/audit/check_scopes.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         node tools/policy/rules_sync.mjs --check
             `tools/policy/rules_sync.mjs` is in the tree at this head

FIGURES: 6 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/CLAUDE.md b/CLAUDE.md
index 937834a848..e770524eba 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -77,8 +77,8 @@ rewrite looks like a correction from the inside; if the honest description is
 `node tools/policy/rules_sync.mjs`; never edit it — `--check` refuses drift
 and an orphan `.mdc`.
 
-`AGENTS.md` is the entry point for a harness auto-loading that name (ZCode,
-Codex); it states no policy and binds the seat to this file.
+`AGENTS.md` binds a harness that auto-loads that name (ZCode, Codex) to this
+file.
 
 | rule | what it binds |
 |---|---|
@@ -97,8 +97,7 @@ Codex); it states no policy and binds the seat to this file.
 
 `.claude/skills/steward/SKILL.md` — read before acting on a CI failure or a
 review comment; only where this repository differs from a session's default, and
-nothing in it loosens a rule stated here. No `babysit/` counterpart: a session
-prefers `steward/`, so a second would bind nobody.
+nothing in it loosens a rule stated here.
 `.claude/workflows/web-fragments.md` — the MCP mapping for a seat with no `gh`
 binary, the one file allowed to name those commands.
 `.github/PULL_REQUEST_TEMPLATE.md` — the headings `checkPrBody` requires;
@@ -164,10 +163,12 @@ architecture score in `tools/audit/archscore/`, per-group harnesses in
 any merge, push, body, gate or watch loop; new reusable instruments land here,
 never only in /tmp (decision 0013).
 
-### The suite, the register, the handover
+### The suite, the register, the rulings, the handover
 
 - `tests/README.md` — what each script pins, how the scoped gate selects, why a
   test that re-implements a production formula pins nothing.
+- `dev/programme/RULINGS.md` — the owner's rulings, verbatim and dated: they bind
+  every seat, though the file is not policy.
 - `dev/audit/README.md` — how a round is run and where its evidence lands.
 - `dev/programme/HANDOVER.md` — the one durable handover, ruled by
   `writing-for-agents.md`; `tests/entities.py` refuses a second under `docs/`.
@@ -202,12 +203,11 @@ is recorded as `pending owner confirmation`, quoting the rule it would change;
 the seat neither acts on that half nor writes it as direction until the owner or
 the contract moves.
 
-## Root-cause remediation
+## What the repository may carry
 
-A qualifying defect owes its cause and the **process** that let the cause get
-that far, established in its own seat beside the fix and never inside it. The
-two triggers, the four process states, the cost test, when recording that no
-countermeasure is worth building is a legitimate result, and the demonstration a
-check-shaped countermeasure owes are in `defect-root-cause.md` and
-`root-cause.md`. The fixer answers a red check in the pull-request body; an
-unanswered one is a reviewer's note resolved at merge (card C5).
+Opinions are private data (tvofi, 2026-11-15). Nothing pushed states or implies
+an opinion of the owner, a contributor or an agent on anything but the code, the
+product and how they work. A decision is described by what it
+does; an owner ruling is quoted only for what it decides. Findings of the
+security-and-privacy audit dimension go to the owner directly, never to an issue
+or anything else on origin.
diff --git a/dev/audit/config/scopes.json b/dev/audit/config/scopes.json
index 2f08deea70..567ca24c3b 100644
--- a/dev/audit/config/scopes.json
+++ b/dev/audit/config/scopes.json
@@ -498,6 +498,7 @@
    "dev/README.md",
    "dev/governance/{dimensions,roles,rules}/*.md",
    "dev/programme/HANDOVER.md",
+   "dev/programme/RULINGS.md",
    "dev/programme/plan-*.md",
    "dev/audit/README.md",
    "tests/README.md",
@@ -600,6 +601,7 @@
       "dev/README.md",
       "dev/governance/rules/*.md",
       "dev/programme/HANDOVER.md",
+      "dev/programme/RULINGS.md",
       "dev/audit/README.md",
       "tests/README.md",
       "tools/{audit,pr}/**.md",
diff --git a/dev/governance/config/corpus_excluded.json b/dev/governance/config/corpus_excluded.json
index 57a1196bbd..4b5f152afb 100644
--- a/dev/governance/config/corpus_excluded.json
+++ b/dev/governance/config/corpus_excluded.json
@@ -1,8 +1,9 @@
 {
- "_comment": "Round-evidence exclusions for the named-docs check, in the shape .claude/workflows/cfr_exclusions.json takes (a top-level object of keyed entries beside a _comment). policy_lint.mjs merges `excluded` into its CORPUS_EXCLUDED set at load, so each entry here is a named document the corpus cites -- COMMON.md's report-shape line names REPORT.md, fixer.md's baseline line names BASELINE.md -- that holds a finder report, a round baseline or other data a later seat reads rather than policy prose -- or, for `docs/index.html` (the product page D6.md names), a user-facing page, on the ground policy_lint.mjs's own CORPUS_EXCLUDED holds README.md and DISCLAIMER.md as `user-facing`. A `.md` is never excused by location, so they are excluded one by one rather than by prefix. Or, for `tools/audit/seat/beatd_shims/git`, an executable and not a document: the beat jobs' git shim, which must be named `git` to be found on PATH, so the bare-name pass resolves every policy sentence's word `git` to it. Or, for `dev/README.md`, the developer onboarding: it states no policy and binds the reader to CLAUDE.md, while it names the tree's tools and contracts by bare name throughout; excluded by 7ae69419e (R10-ARCH-DOCS-FIRST), and dropped when policy_lint.mjs's resolveCited canon lookup lands.",
+ "_comment": "Round-evidence exclusions for the named-docs check, in the shape .claude/workflows/cfr_exclusions.json takes (a top-level object of keyed entries beside a _comment). policy_lint.mjs merges `excluded` into its CORPUS_EXCLUDED set at load, so each entry here is a named document the corpus cites -- COMMON.md's report-shape line names REPORT.md, fixer.md's baseline line names BASELINE.md -- that holds a finder report, a round baseline or other data a later seat reads rather than policy prose -- or, for `docs/index.html` (the product page D6.md names), a user-facing page, on the ground policy_lint.mjs's own CORPUS_EXCLUDED holds README.md and DISCLAIMER.md as `user-facing`. A `.md` is never excused by location, so they are excluded one by one rather than by prefix. Or, for `tools/audit/seat/beatd_shims/git`, an executable and not a document: the beat jobs' git shim, which must be named `git` to be found on PATH, so the bare-name pass resolves every policy sentence's word `git` to it. Or, for `dev/README.md`, the developer onboarding: it states no policy and binds the reader to CLAUDE.md, while it names the tree's tools and contracts by bare name throughout; excluded by 7ae69419e (R10-ARCH-DOCS-FIRST), and dropped when policy_lint.mjs's resolveCited canon lookup lands. Or, for `dev/programme/RULINGS.md`, the owner's standing rulings, excluded by tvofi's own ruling of 2026-11-15: \"This file should be excluded by the corpus but still needs to be re-read on changes, just like instruments.md\" -- the liveness hook re-reads it by change after a compaction, as it does the instrument pages.",
  "_why_data_not_source": "These entries must be DATA and not a hardcoded block inside .claude/workflows/policy_lint.mjs. The `policy-docs` job's 'Restore the check source from the base commit' step (#1403) rewrites `.claude/workflows/*.mjs` and `*.py` from the base commit before grading, so a round that ships its evidence files and their exclusions in one branch would have the exclusions erased on CI and fail named-docs; pre-registering them first is refused as FIXTURE VACUOUS, because an exclusion that names no tracked file yet is a destination waiting to be used. This file is outside that pathspec, so it arrives with the branch that adds the evidence it excludes -- the same shape the #1403 fix's own comment names for policy_budgets.json, policy_known_bad.json and cfr_exclusions.json: a grader's criteria are data, and a fixture's expected outcome has to be the data under test.",
  "_fail_closed": "A missing or unparseable file, or a non-array `excluded`, makes policy_lint.mjs merge nothing, and the cited-but-unexcluded evidence files then re-arm named-docs on the production run -- so this list cannot silently drop an entry; the check that consumes it notices.",
  "excluded": [
+  "dev/programme/RULINGS.md",
   "dev/archive/README.md",
   "docs/index.html",
   "dev/audit/rounds/round10/D0/s1/REPORT.md",
diff --git a/dev/governance/roles/fixer.md b/dev/governance/roles/fixer.md
index b8bcb5c9c0..233e6c18dd 100644
--- a/dev/governance/roles/fixer.md
+++ b/dev/governance/roles/fixer.md
@@ -2,7 +2,8 @@
 
 You own one PR group: one subsystem, at most five findings, at most about 400
 production lines. You work in your own worktree branched from `origin/main`.
-Read only your roster group (`jq`). Run a job outliving your turn as a
+Read only your roster group (`jq`). The owner's rulings in
+`dev/programme/RULINGS.md` bind you. Run a job outliving your turn as a
 background task, whose exit wakes you; never end a turn on a detached one.
 Wait on CI through one `seat/ci-watch.sh` or `seat/proof_watch.py` (the 60 s
 API floor is theirs), woken by its exit, never polling;
@@ -72,11 +73,11 @@ fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M), ~300 k (L,
    run it on a `GRID_SURFACE` diff (recipe: `web-fragments.md`; #2841).
 
    **Running locally does not discharge CI.** What `scope.run` names is green,
-   every red `prepr.sh` step 6d predicts is repaired before the handoff
-   (`ci-autofix.md`'s wait starts at the PR), and the body passes
-   `tools/pr/prepr.sh`, run on a committed tree (step 6f reads `HEAD`; 7e is
-   the carry check); the orchestrator opens
-   the PR (`docs/decisions/0011-app-authored-identity.md`).
+   every red `prepr.sh` step 6d predicts is repaired before the handoff, and
+   the body passes `tools/pr/prepr.sh`, run on a committed tree. **Prepr runs scoped** (tvofi, 2026-11-15):
+   `PREPR_SKIP_CLOSURES=1`, plus `PREPR_SKIP_CODE=1` for a text-only delta
+   since the last clean run; a full run only where the change reaches what
+   only it measures, the reason in the body.
 
    **`ci_predict.py` printing `BOOTSTRAP`** (the base's copy of the changed
    grader refuses, the head's passes in `prepr.sh`) is not `BLOCKED`: register
@@ -84,8 +85,6 @@ fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M), ~300 k (L,
    p1 the grader hunks alone, p2 the rest, a WIP handoff until p1 is on main
    (decision 0013, Consequences).
 
-   **`run.sh` takes the gate lease itself, around `tests/stress.py` alone**
-   (`gate-scoping.md`).
    A mutation proof leaves `stress.py` to CI's required mutation check: never
    run it locally per mutant.
 
@@ -98,7 +97,8 @@ fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M), ~300 k (L,
    false the moment `main` moves; stamp it with that tip and `date -u`. The code
    head goes to `handoff/<topic>`, the body to the orphan `handoff-body/<topic>`
    by `seat/body_push.sh`, whose offline `review_packet.py handoff` refusals you
-   answer first. That push is the handoff; `handoff_push.sh` opens the PR.
+   answer first. That push is the handoff; `handoff_push.sh` opens
+   the PR (`docs/decisions/0011-app-authored-identity.md`).
 
    **The handoff freezes the branch.** Until then, merge `origin/main` (never
    rebase) only when `git merge-tree --write-tree origin/main HEAD` reports a
@@ -212,7 +212,7 @@ fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M), ~300 k (L,
     its remaining share, not a close.
 
 16. **An age computed from a stamp ahead of the reading clock is unknowable,
-    never 0** (#775's refusal; #1532 pinned the technique #775 had refused).
+    never 0** (#775, #1532).
 17. **Take the fix that yields the better code; it is architecturally sound**
     (tvofi, 2026-10-08). Where one fix satisfies the check and another removes
     the cause or simplifies the design, take the second; the body names the
diff --git a/dev/governance/roles/orchestrator.md b/dev/governance/roles/orchestrator.md
index f18f72f2f4..fafed23280 100644
--- a/dev/governance/roles/orchestrator.md
+++ b/dev/governance/roles/orchestrator.md
@@ -14,12 +14,14 @@ comments, dispatch briefs, roster edits, and what you tell the owner.
 every role contract here are instructions you follow, not relay. Where a rule
 names "the fixer" or "a seat", read yourself into it whenever you are the one
 acting — and you are acting whenever you write text another agent or the owner
-will treat as established.
+will treat as established. The owner's rulings in `dev/programme/RULINGS.md`
+bind you and whoever you brief, though that file is not policy. **After each compaction** read `CLAUDE.md`, this
+contract and the rules in full, and the instrument pages and
+`dev/programme/RULINGS.md` the liveness hook's `policy-corpus.txt` carries as changed, then run its
+`PROOF` line (tvofi, 2026-11-13, P6 and R3; 2026-11-15).
 
 ## 1. Verify before claiming
 
-**`fixer.md` step 8: a quoted number states its rule, not just its value.**
-
 **Nothing is asserted that has not been measured, and the measurement is the
 command, not the impression it left.** Before writing a claim, ask what exactly
 ran, and what its output would have looked like had the claim been false. If you
@@ -27,10 +29,8 @@ cannot answer the second, you have not measured — you have expected.
 
 - Describing an artifact without opening it is the same defect. A wrong claim
   is corrected under `fixer.md` step 9.
-- **Never print a conclusion beside a command** (`fixer.md` step 3).
 - **Never chain past a check with `;`.** `check; publish` publishes whether or
-  not the check refused. Use `check && publish` — and for the body and the
-  push, that `&&` is already wired as `tools/pr/push.sh` (#678).
+  not the check refused. Use `check && publish`.
 
 ## 2. Delegate what a seat can do; do only what only you can do
 
@@ -64,14 +64,12 @@ target or the critical chain would feel goes back to the owner first.
 ## 3. Repeated errors go to the root-cause seat, not into another issue
 
 `CLAUDE.md`'s *recurring error* rule binds you as it binds a seat, and an
-instance by you counts toward the third. The product, the four
-process states and the demonstration a check owes are `root-cause.md`'s and
-`defect-root-cause.md`'s; it runs in **its own seat**, never inside the fix (section 2).
+instance by you counts toward the third. It runs in **its own seat**
+(`root-cause.md`), never inside the fix (section 2).
 
 ## 4. The merge message is a second closing surface
 
-A pull request's closing references describe its **body**, and no GitHub
-tool method here exposes them. The merge message is a separate artifact, written by you at merge
+A pull request's closing references describe its **body**. The merge message is a separate artifact, written by you at merge
 time, and GitHub parses it too; since `main` took to merge commits (`docs/decisions/0010-merge-commits-on-main.md`) its default body is the pull request's **title**, so a keyword in a title reaches `main` too. A pull request can show `[]` forever while its
 merge commit shuts an issue. **GitHub discards the negation**; only the keyword
 and the number matter.
@@ -85,9 +83,8 @@ whenever you merge.
 ## 5. Before dispatching a seat
 
 - **The soft cap gates only dispatching a new roster group** (tvofi,
-  2026-10-20): `pr_cap.py dispatch-gate` counts roster `in-progress` groups and
-  refuses at `HPO_WIP_CAP` (default 6) unless `--over-cap "<reason>"` says why.
-  Opening or updating a pull request for an owed handoff is never refused by it.
+  2026-10-20; its value is in `dev/programme/RULINGS.md`): opening or updating a
+  pull request for an owed handoff is never refused by it.
 - **A ready critical-path group starts regardless of every cap** (tvofi,
   2026-10-22): a group in the current plan's
   `critical_path` whose `after` groups are all done, and whose design verdict
@@ -120,9 +117,11 @@ whenever you merge.
   stage, the numbers it must re-measure, and the destination its carry must reach.
 - **Name the null control you expect**, where one is knowable. A seat told what
   must *not* fire returns better evidence than one told only what must.
-- **Every brief names the identity** (decisions 0011, 0013): seats push refs (`tools/audit/seat/bus.sh`), never a pull request; every GitHub write is yours (`CLAUDE.md`, Identity). Verdicts post only on `bus.sh confirm`, signed by `hpo-approver`'s key; code-owned paths still need tvofi. The retired account makes no GitHub write: its writes vanish retroactively.
+- **Every brief names the identity** (decisions 0011, 0013): seats push refs (`tools/audit/seat/bus.sh`), never a pull request; every GitHub write is yours (`CLAUDE.md`, Identity). Verdicts post only on `bus.sh confirm`, signed by `hpo-approver`'s key; code-owned paths still need tvofi. The retired account never writes: its writes vanish retroactively.
 - **Brief a seat its own roster group** (`jq`), and give a judgement-free turn
-  (a relay, a delivery row) the cheapest model that does it.
+  (a relay, a delivery row) the cheapest model that does it. A fixer is a local
+  seat only where SendMessage steering is likely, else cloud (tvofi,
+  2026-11-15).
 - **Concurrent fixes sharing a concern push only after an architect note**
   you dispatch into each group's roster brief (owning module, each fix's
   shape); it binds them (`fixer.md` 17). A serial chain orders groups whose
@@ -191,7 +190,8 @@ established fact, with nothing gating it. A real finding you must not touch goes
 no per-PR row from you (card C5); a verdict's paperwork notes are yours to resolve at that merge.
 **The handover is one file and it is not optional** (`writing-for-agents.md`).
 **Rotate** at a ledger-clean point, never mid-task, as `dev/audit/README.md`
-sets.
+sets. **A round closes only with its objective record** under
+`dev/audit/yardstick/` (tvofi, 2026-11-15, E11-N-OBJECTIVE-RECORD).
 
 Failure shapes already produced, all yours:
 
@@ -209,8 +209,6 @@ Failure shapes already produced, all yours:
 `finding-propagation.mdc` binds the producing pull request, and you too: you
 write the rosters and order the merges.
 
-- **A comment is not propagation** — including yours on #3394.
-- **The destination must exist**, and creating it is part of the carry.
 - **Land the roster on main only when the tree needs it** (tvofi, 2026-10-18):
   a carry a PR names, a `Closes` needing a `fixes` edit (`pr-contract` reads
   it), each stamp, and before branch cleanup, which keeps the roster
@@ -241,7 +239,9 @@ Through the `roster-drain` queue; `roster_edit.py`'s lint gate binds.
   review on a code-owned path; then merge with `--match-head-commit <sha>`.
 - Then `main` is green after it. If a merge reddens main: a behaviour change in
   the merged diff → revert first and diagnose after; a failure the diff cannot
-  reach → establish that, and it is its own issue. Never `--allow-red`.
+  reach → establish that, and it is its own issue. `--allow-red` only when the
+  red's cause is established as not the pull request's and commented on it or recorded; never over a
+  concluded red whose cause is unknown (tvofi, 2026-11-05, 2026-11-11).
 - After each merge: run `tools/audit/worktree_gc.sh <owner/repo>` — its worktree, branch and seat scratch go now, cited evidence kept.
 
 ## 12. The gate lease
diff --git a/dev/governance/roles/proposal-triage.md b/dev/governance/roles/proposal-triage.md
index 62eabf1f24..1470557de9 100644
--- a/dev/governance/roles/proposal-triage.md
+++ b/dev/governance/roles/proposal-triage.md
@@ -5,9 +5,8 @@ passes this gate before building (decision 0015); a required countermeasure
 (root cause, red-check carry, finding fix) keeps its route. **Once per round**
 (tvofi, 2026-11-14: "keep it in the once per round shape"): the round's
 proposals are consolidated and triaged together at round end by one opus seat,
-medium effort; an ACCEPT is built at the start of the next round. A fix to an
-instrument a running seat depends on stays local and in-round, ruled by no one.
-Check rulings against code.
+medium effort; an ACCEPT is built at the start of the next round. Check
+rulings against code; the owner's, in `dev/programme/RULINGS.md`, bind this triage.
 
 **Bar:** measured benefit clearly outweighs cost: critical-path wall-clock/seat
 time; tokens (model x effort x runs); API calls; standing CPU
@@ -19,10 +18,9 @@ ACCEPT. Blocking no production merge: LOG, bar the exemption in
 
 **Machinery.** A planned machinery group, or a non-production CI lane or
 seat, stays only on a measured gain of at least 10% on them. Repair of such
-code (outside `custom_components/`) with roster `severity` `low` or `normal`
-meets both (over 20% to add); `medium`, `high`, `major`, `critical`,
-root-cause countermeasure, closeout, owner directive skip them; unset is
-classified first, never assumed major.
+code (outside `custom_components/`) meets both (over 20% to add) at any
+severity; a red required check on `main`, a blocked production pull request, a
+root-cause countermeasure, closeout or an owner directive skips them (tvofi, 2026-11-13, card P2).
 
 **Verdicts:** ACCEPT names a destination (a next-round roster group and carry,
 or new group, brief); DEFER, what would change it or the owning group; REJECT,
diff --git a/dev/programme/RULINGS.md b/dev/programme/RULINGS.md
new file mode 100644
index 0000000000..3d0a3a7d31
--- /dev/null
+++ b/dev/programme/RULINGS.md
@@ -0,0 +1,421 @@
+# The owner's standing rulings
+
+Purpose (the orchestrator's wording, confirmed by tvofi on 2026-11-15: "This is
+exactly how I see it"): this file is a holding area below policy, not a second
+rulebook. (1) An entry policy already states is dropped. (2) An entry that should
+bind every session permanently graduates into policy, or into a decision record
+when it is structural and its reasoning must be kept, and then leaves this file.
+(3) What remains is operational or temporary: the current mandate,
+round-specific direction, and preferences too fine-grained for policy. (4) The
+file should stay small and shrink over time; a growing file is a signal that
+rulings are not being promoted.
+
+Every ruling of tvofi's still in force, with its date. Quoted text is his words
+verbatim, typos kept; "as recorded" marks a ruling whose words were not kept,
+and "orchestrator's reading" marks an interpretation, never his. A ruling given
+to an orchestrator lands here in its next pull request; one superseded moves to
+the closing list, naming its successor. An entry belongs here only while no
+policy file states it (tvofi, 2026-11-15: "Also screen the rulings for overlap
+with policy, if both policy and rulings mandates something, policy is the right
+place"; "The point with this is that policy files and policy related files
+should follow good data integrity practice, no duplication, that creats risks of
+divergence"). Re-read on change after every compaction
+(`dev/governance/roles/orchestrator.md` section 0).
+
+## Authority and the mandate
+
+- **Current mandate:** comment 6893738184 on #3394, scope all, until
+  2026-12-15T12:00Z. 2026-11-15: "I hereby extend your mandate until 2026-12-15
+  12:00Z, post a new mandate in canonical form on the tracking issue for me."
+  Cite it in every approval posted as tvofi; ask him for an extension at the
+  time, never assume one (2026-11-14: "I will extend the mandate when needed").
+- 2026-11-08: "it can still be done by you under the mandate. The mandate means
+  you may act as me in any way necessary without asking?" The orchestrator posts
+  that review itself and never sends it back to him (what such a review must
+  carry is decision 0013's).
+- 2026-10-23: "The raise is ok, but you can rule such cases under your mandate".
+  A seat's denial is never laundered through the mandate (the raise itself is
+  `CLAUDE.md` rule 2 and decision 0013's).
+- 2026-11-15: "The owners own words can also be you under the mandate." Wording
+  the owner owns (dimension briefs) may be written under the mandate, declared
+  with its id.
+- 2026-10-25: "You can toggle a ruleset under the mandate as you have done
+  multiple times before." Narrow it, restore it, read it back, log it.
+- 2026-11-13: "Remember you have GitHub admin rights under the mandate."
+  2026-11-09: "Yes delete it, you are free to make that call under the mandate"
+  (removing a stuck CI run that holds the programme).
+- 2026-09-17: "I have given you a standing approval, but importantly, it applies
+  to this session ONLY", and "Such exceptional session approvals can never be
+  overstated or uncontrollably extended again." Record a grant in his words with
+  its scope; a session grant dies with the session.
+- 2026-11-13, card X1: "No, mandate stays as is" (actuator-write pull requests
+  stay approvable under it).
+
+## Decisions put to him
+
+- 2026-11-15: "For any decisions, if i don't answer within 5 minutes, go with
+  what you recommend and log it".
+- 2026-11-15: "Dont default to bring me cards when I have not been active the
+  last hour. When I am active, try the 5 minute wait first. Not cards that pause
+  your turn".
+- 2026-11-13: "Describe all the audits findings and han anything to me as
+  decision cards before applying", for audit findings he asks to see (narrowed
+  by the 2026-11-15 card rule above).
+- 2026-11-07: "Remember to not act on anything before I have decided on the
+  verified findings though" (verified is not decided).
+- 2026-11-12: "It has already been decided that that should be dropped." Read a
+  group's roster stage and note before asking; a settled ruling is not re-asked.
+- 2026-10-21 (as recorded): seat questions are decided by the orchestrator under
+  the mandate, never surfaced to him in a seat's final text.
+- 2026-11-15: "Send judgement-heavy rulings to a seat for a recommendation first
+  (an Opus reviewer, or Fable when it is truly architectural), then decide. The
+  contract already asks for this on architectural calls." (the orchestrator's
+  proposal, accepted in these words; `orchestrator.md` section 5's architect
+  note covers concurrent fixes only, so the whole rule stays here).
+- 2026-11-15: "Raise effort for a single turn when a ruling warrants it, not for
+  the session.".
+- 2026-10-29: "there is never a scenario where I would not want to" (fix every
+  slip found; never ask).
+- 2026-11-12: "Stop replying to no-op notifications to be a bit more token
+  effective."
+- 2026-11-14: "If they never use it, ship them without it" (cloud seats are
+  created with no connectors; never repeat the connector notice).
+
+## Round scope and the objective
+
+- 2026-11-13: "Also verify that the other dimensions also covers the full
+  codebase in their contracts, I want future rounds to always check everything
+  in their dimension, not only small samples". 2026-11-13: "I would like the
+  scope of d5 and d6 to always cover that full scope". Where `D3.md` and `D11.md`
+  still sample, the change is owned by R11-PRE-BRIEFS-TEXT part 2.
+- 2026-11-15: "As soon as everything that is critical to land before the finder
+  phase, the finding phase can start in parallel with the remaining groups";
+  "Only the finder critical are required for finder start"; "i meant cutover as
+  when the finders are finished, so that such groups can move in parallel with
+  the finders." What is still open when the finders finish goes to the architect
+  and planner phase. "Token Ledger not critical to land before finders."
+- 2026-11-15: "Remember that any still open round 10 groups need to be moved to
+  round 11 before or at cutover, round 10 no longer is active".
+- 2026-11-13: "Make sure the future rounds can use the audit playbook even with
+  the addition of the objective function and the improved audit dimension. It
+  should also make the round orchestrator pick up the carries and pre-finder
+  carries from the previous round."
+- 2026-11-13: "outside and owner filed findings and requests should always fold
+  into the ongoing round if not explicitly deferred by the owner or outsider".
+
+## The instrument freeze, proposals and root cause
+
+- Card P11 (verbatim in the card list below) sets the freeze's exceptions.
+  2026-11-13: "This should be the shape for instrument fixes, prototype
+  local fixes in-round, file proposal permanent fixes for consolidation and
+  cost/benefit that is carried to the start of next round". (The local in-round
+  fix and the round-end triage are `orchestrator.md` section 5's and
+  `proposal-triage.md`'s.)
+- 2026-11-01: "On any deadlock, you fix it by hand while waiting on the
+  permanent fix." 2026-11-13: "For the relay, this repos shape is fix it
+  locally, file permanent fix as a proposal".
+- 2026-11-14: "limiter first, write that in" (R11-PRE-MACHINERY-LIMITER before
+  the other pre-finder instrument groups).
+- 2026-11-14, loop-study cards: "L1 loop ledger: Yes · L2 countermeasure order:
+  Yes · L3 unread not red: Yes · L4 price induced work: Yes · L5 triage by
+  instrument: Yes · L6 probation revert first: All three parts · L7 kill
+  criterion: Yes, at 0.8 spawn ratio or 15% hotfix share · L8 machinery rca
+  timing: Once per family at round end · L9 generate after merge: Yes · Build
+  timing: At round 11 start, per the freeze".
+- 2026-09-16: "deploy the rca, it should be done immediately and not deferred as
+  owed" (product and release defects and outages; tooling friction is counted by
+  family and analysed at round end, L8). The trigger and the separate seat are
+  `CLAUDE.md`'s and `defect-root-cause.md`'s.
+- 2026-10-24: "each operation or shape that is not clearly a one shot and could
+  be mechanical should be mechanical and wired into the machinery. This means
+  reusable instrument before policy, only policy if no robust script could be
+  built at a reasonable cost (tokens, time, complexity)".
+- 2026-11-13: "you may have a fixer have more carries based on their kind,
+  locally for now and filed as a permanent proposal" (operational until the
+  round-end proposal triage rules PC-1113-08).
+- 2026-11-01: never propose or triage CI-capacity widening: runners, paid plan,
+  second account (as recorded). 2026-11-13: "No" to raising the Actions
+  concurrency limit; never ask again. 2026-11-12: "You know you can run seats
+  locally if needed right?" (a macOS-only check runs on a local seat).
+
+## Process changes ruled 2026-11-13 and 2026-11-14
+
+- Cards, verbatim: "P1: Yes · P2: Declining cap, one in one out, severity route
+  narrowed · P3: Yes · P4: Yes, local and cloud · P5: Keep and do the rest · P6:
+  Yes · P7: Yes, fold in · P8: Yes · P9: Yes, design first in round 11 · P10:
+  Yes · P11: Freeze, except production defects, owner orders and red main · P12:
+  Yes, during round 11 · P13: Yes · P14: Yes · R1: Yes, keep one exception seat
+  · R2: Yes, render on change · R3: "Full for CLAUDE.md, orchestrator contract
+  and rulings; changes only for instrument pages" · X1: No, mandate stays as is
+  · X2: Yes, trial". On P9, P10, P12, P14, R1, R2: "They should be fixed in the
+  beginning of round 11 before the finders run".
+- 2026-11-15, relayed by the orchestrator: "This file should be excluded by the
+  corpus but still needs to be re-read on changes, just like instruments.md". It
+  is listed in `corpus_excluded.json`, outside the policy caps; the reading rule
+  is `orchestrator.md` section 0's.
+- 2026-11-14: "Day 1 plus shadow" (the shadow runs beside round 11 as a
+  measurement; the switch to an integration branch is his decision after it);
+  "Yes." to "small shadow first; driver only if the replay passes"; "If cloud
+  seats for speculative gating is feasible, they should run haiku";
+  "remerge_main.sh definitely needs to be scoped down aggressively" (merging
+  main only on a conflict is `fixer.md` step 6's).
+- 2026-11-14: "Keep them open" (never close a re-routed pull request to cut the
+  branch count).
+- 2026-11-11, study review: "I agree with all the recommendations" (as recorded:
+  `tests / ci-ratchet` advisory on a push to main; D11 and D13 name the
+  convergence scorecard). 2026-11-12: "2. Round 11" (the product-only required
+  check set).
+
+## Priority, caps and the critical path
+
+- 2026-11-09: "Your absolute, critical top priority is to never let the critical
+  path or outside PRs slip, ever."; "This should under no circumstances never,
+  ever be allowed to slip since it is outside request"; "These types of
+  worksrounds is definitely warranted for landing critical path an outside
+  request PRs as well."
+- 2026-11-07: "all accepted outside issues or contributions should be
+  prioritized higher than audit or owner submitted ones unless i call the owner
+  one a hotfix".
+- 2026-10-28 (as recorded): a hotfix is a production bug the owner or a user
+  reports, a feature he calls a hotfix, a critical bug found while fixing, a red
+  required check on main, or a machinery bug deadlocking all merges. 2026-10-29:
+  "critical-path PRs jump the record step too" (card, 2026-11-15: "Keep both
+  parts").
+- 2026-11-13: "All production groups now goes above the cap" (orchestrator's
+  context: the soft cap of 20 open pull requests before starting new groups,
+  2026-11-11).
+- 2026-11-11: "Do it, it is already decided and should be built in, no critical
+  path, outside or hotfix PR should wait in CI queue"; "Dont do A" (no merging
+  on a combined proof with the required-check rule narrowed).
+- 2026-11-08: "every item must always have someone on it" for every open pull
+  request, ready handoff and unblocked group (as recorded).
+- 2026-10-28: "no pr should wait without reason, in particular not CP prs";
+  2026-10-18: "act on work waiting on you, you should never ignore it";
+  2026-11-06: "Anything ”owed” means by definition you should act in the same
+  round"; 2026-11-14: "Act on everything that is owed in the same turn always".
+- 2026-11-08: "Raise the coordinator cap to 3" (ordering by owning seam, not
+  shared file, is `orchestrator.md` section 5's).
+- 2026-11-05: "The point with the roster and plan is to avoid such file
+  conflicts" (compare open pull requests' files before queueing).
+- 2026-10-25 (as recorded): new work goes to an existing open group; a new group
+  only when nothing is in common.
+- 2026-11-07: "The dependsncy is backwards, user docs verify need to be after
+  every user facing change. Verify no other seams are backwards".
+- 2026-11-01: "Each time the plan html is updated, compare the real state
+  against the gantt, mechanically if possible, and have slips surfaced to you to
+  act on, defer or accept."
+- 2026-10-30: "dark mode should absolutely not be scoped out. you have your
+  mandate". User-visible quality is never scoped out for cost or ownership.
+
+## Merges, CI and reds
+
+- When a merge train is run, it runs in batch mode with combined proof and with
+  overlap, and it pauses while a stamp runs: 2026-11-01: "batch mode should be
+  the default mode but the merge seats keep dropping that info"; 2026-11-07: "I
+  meant the batch mode with combined proof that the train supports"; 2026-10-22:
+  "It is recommended to run the train with --overlap as long as ci of the prs
+  are run"; 2026-10-24: "have the merge seat run with batch where possible, and
+  always overlap"; 2026-11-08: "The train should pause while a stamp is running
+  the next time." These bind nothing while merges are single (card, 2026-11-15:
+  "Keep, scoped to train runs (Recommended)").
+- 2026-11-04: "keep records such as triage and roster edits on separate
+  branches, and merge them with main only around the stamp and in batches";
+  "records should not drown out production PRs. Merge the record PRs together
+  with stamps". 2026-11-15, card "Hold delivery rows for the stamp too": the
+  automatic delivery-rows pull request (record/autofix) also waits and merges
+  with the stamp batch, never on its own guard between stamps. 2026-10-28: "we
+  should keep them, but that kind of reviews are for sonnet seats" (record pull
+  request reviews).
+- 2026-11-04: "DONT CLOSE THEM. JUST CANCEL THEIR CI RUNS".
+- 2026-11-04: "You don't have to pause merges due to CI ratchets red, since it
+  was not caused by any PR".
+- 2026-10-28 (as recorded): cancel superseded runs every sweep, CP and hotfix
+  heads included ("keep cancelling them, yes"); never a live head or main.
+  2026-11-13: "2. Yes" (cancelling superseded main runs while Actions is
+  healthy); 2026-11-11 (as recorded): never while Actions is degraded.
+- 2026-10-21: "A pr still needs valid evidence" (fix an over-firing check's
+  classification, never the requirement).
+- 2026-11-04 (as recorded): a heavy pre-PR script runs once per code; a fixer's
+  run is not repeated at the opening (scoped prepr is `fixer.md` step 5's).
+- 2026-11-11: "4. Go with what you recommend" (a finished merge verdict may post
+  before CI is green; the train still gates CI).
+
+## Reviews
+
+- 2026-10-04: "in general, blocked review verdicts go back to the original
+  fixer."
+- 2026-11-11: "the reviewer has to be fable under the reviewer >= fixer model
+  rule" (a reviewer's model is at least the strongest author's; orchestrator's
+  reading since 2026-11-15: a Fable reviewer only where the reviewed work is
+  itself of that class).
+- 2026-11-07: "Remember that a significant new feature should have a design and
+  design reviews, especially outside ones. Post on the outside PR that the
+  feature is being planned with the design choices made, then post again with a
+  link to the plan html as soon as the public page has landed" (whatever its
+  size; design first for L and XL is `orchestrator.md` section 5's).
+
+## Outside contributions
+
+- 2026-11-06: "the plan html for an ongoing round should be made publically
+  available from a suitable place in the developer documentation on the repo.
+  [...] When the plan html is done, and any outside submission is on the roster,
+  the plan HTML should be linked in an answer to the outside submission." (Each
+  outside submission's disposition is `orchestrator.md` section 5's.)
+- Fallback, for an outside pull request decision 0017 does not admit (order by
+  card, 2026-11-15: "I3 first, I2 as fallback (Recommended)"): 2026-11-06:
+  "R10-PR-CONTRACT-OUTSIDE should be cancelled, drop that path"; "With our
+  additions in mind, change the strategy to mergeing our version, but thank the
+  outside cotributor in the PR description".
+- 2026-11-06, for every outside pull request either way: "For outside PRs, the
+  reviewer needs to take extra care on code security".
+
+## Seats and models
+
+- 2026-09-17: "the orchestrator should route to sonnet and haiku models where
+  reasonable"; 2026-09-24: "only start your opus 5.5 fixers with medium effort".
+- 2026-11-15: "From now on, reserve fable for the most complex, architectural
+  work, both for fixers, finders and reviewers". 2026-11-11: "S and M groups may
+  go to Opus when no oracle exists or if the groups requires judgement";
+  2026-11-12: "Budget is fine for important work".
+- 2026-10-25: "the triage seat should be opus, since it requires judgement";
+  2026-11-15: "product-feature triage can run on opus".
+- 2026-10-21: "try to keep heavy runs on cloud runners to keep the box load
+  under control"; 2026-10-25: "dont forget cloud seats are uncapped" (where a
+  fixer runs is `orchestrator.md` section 5's).
+- 2026-11-08: "Don't forget that you have a cap of 7 local seat that you can use
+  for fixers and reviewers as well, best used for work that might need
+  sendmessage communication"; "Repeated failures of cloud seats on the same
+  prompt could warrant running it on a local seat instead that has sendmessage."
+- 2026-11-11: "When you re-fire any seats, have them pick up from the work the
+  previous seat left"; "when you schedule seats, you can schedule them in just a
+  couple of minutes".
+- 2026-10-21: "I get these notifications to approve the cloud seats, there is a
+  documented dispatch that uses scheduled tasks, use that".
+- 2026-11-04 (as recorded): cloud seats get generous windows, and their liveness
+  and output are checked every sweep.
+- 2026-10-22: "You are free to restart seats or start entirely new seats as you
+  see fit"; 2026-11-01: "You would not need my go ahead for something like
+  that."
+- 2026-11-09: "Drop it, the seats should use cheaper sub seats when the frugal
+  guard says so"; 2026-10-21: "The frugal guard should be on but it should allow
+  you to read the policy that binds you". No seat edits `.claude/settings.json`.
+- 2026-11-04 (as recorded): every local seat type can message the orchestrator.
+
+## Record, handover and identity
+
+- 2026-11-14: "The resume prompt is generated mechanically".
+- 2026-10-28: "sweep should also include the record beat"; "mechanically replan
+  and generate the plan html". 2026-11-08: "I would like the public plan page to
+  refresh on every update to it without needing a stamp"; "Have a cheap seat
+  read it next time".
+- 2026-11-13: "5. Leave." (duplicate record lines on #3394 stay).
+- 2026-09-24 (as recorded): the owner is named only "tvofi" (card, 2026-11-15:
+  "Keep the naming rule only"; who approves what is `CLAUDE.md`'s Identity).
+- 2026-10-22: "please have your seats not post claude code footers, especially
+  not with direct links to sessions".
+- 2026-11-12: "ok, correct any references to that script or remove it entirely"
+  (`nudge.md`, which binds Cursor orchestrators only).
+- 2026-10-28: "no, you keep working while waiting on background jobs";
+  2026-11-07: "NEVER run long scripts inline. Daemonize or background, or use a
+  seat".
+- 2026-11-01: "Fix this and dont let it slip again" (the wake loop is re-armed
+  after every exit and compaction).
+- After a compaction, check running seat briefs and pending steps against the
+  instrument pages that changed (card, 2026-11-15: "Retire K11, K12 on parity
+  (Recommended)").
+- 2026-11-09: "Yes, keep the local one, but propose an update to the live one to
+  cover the gaps". The local liveness hook is retired once the tracked hook is
+  installed and shown to cover it (same card).
+
+## Releases
+
+- 2026-11-01: "to not stall the programme when waiting for ci on main when you
+  stamp, admin stamp to keep the merges flowing with overlap"; 2026-11-12: "You
+  may stamp without waiting for main"; 2026-11-08: "Stamp manually without
+  waiting for main." (When `--allow-red` may be used is `orchestrator.md`
+  section 11's.)
+- 2026-11-09: "You should have at least one new feature in custom_components or
+  3-5 bug fix PRs touching that path between the stamps, if I don't tell you
+  otherwise".
+- 2026-11-13: "Every release requiring extra steps should either be shipped with
+  an automated migration script or very clearly describe the human action needed
+  at the beginning of the release notes."; "the incorrect config flow text and
+  the release notes omission are defects in themselves".
+
+## Superseded, spent or expired
+
+- 2026-11-15, tvofi on the orchestrator's list: "Retire your candidates". Each
+  line below is dated 2026-11-15.
+- Default to the recommendation (2026-10-21, 2026-10-31): folded into the
+  5-minute rule.
+- Text verification split between rounds 10 and 11, "before round 11" changes,
+  and "you are round 10" (2026-11-13): spent with round 10's closure; full-scope
+  dimensions stand above, the two new dimensions are roster groups.
+- Every proposal triaged before implementation (2026-10-22): superseded by
+  once-per-round triage.
+- The production-share exemption (2026-11-01): superseded by the 20%/10% bar;
+  the exemption itself is policy in `ratchet-budgets.md`.
+- Queue order of 2026-10-28: superseded by outside first (2026-11-07); its
+  hotfix definition stays above.
+- The 20-PR soft cap entry (2026-11-11): retired; the cap is named where the
+  production-above-cap ruling cites it.
+- No merge outside the train (2026-10-26) and the orchestrator never runs
+  `train.sh` (2026-10-29): retired; round 11 merges single pull requests through
+  `merge_pr.sh` without a standing merge seat.
+- GitHub poll cadence (2026-10-07, 2026-10-19, 2026-11-08): retired.
+- R10-DRAW-MAP-EVIDENCE rulings (2026-11-14) and the R10-COMBI-TANK waiver
+  (2026-11-06): retired here; they live on those groups' roster entries.
+- Reviewers owed as soon as a pull request opens (2026-10-20): superseded by the
+  delta-review timing of 2026-11-09 (early only for critical path and outside,
+  otherwise once CI is green); card "Retire H3 (Recommended)".
+- Standing seats with multi-hour windows and their recycling (2026-10-28,
+  2026-10-31, 2026-11-01): retired, round 11 has no standing seats; tick and
+  roster work are beat jobs (card "Retire J10").
+- A main-red hotfix merging before its review (2026-10-24): retired, a merge
+  verdict precedes every merge (card "Retire G14 (Recommended)").
+- Only policy and budget-raise pull requests need his approval (2026-09-24):
+  dropped, `CLAUDE.md`'s Identity section states who approves what (card "Keep
+  the naming rule only").
+- Fable for L and XL architectural groups (2026-11-11: "Replace L and XL
+  architectural groups that are now routed to opus to fable 5.2, use cheaper
+  seats for easier work") and "L and XL seats only" (2026-11-12): superseded by
+  "reserve fable for the most complex, architectural work" (2026-11-15).
+- "Have the triage seat as fable when triaging new product features"
+  (2026-11-11): superseded by "product-feature triage can run on opus"
+  (2026-11-15).
+- Decision cards as the default ("Normal decision cards please", 2026-11-13; "I
+  want Normal decision cards as before" and cards through the question tool on
+  Remote Control, 2026-11-15): superseded by "Dont default to bring me cards
+  when I have not been active the last hour" (2026-11-15).
+- "architectural calls take a suitable reviewer's recommendation first"
+  (2026-10-21): merged into "Send judgement-heavy rulings to a seat for a
+  recommendation first" (2026-11-15).
+- Reviewer timing, "only fire reviewers before ci is finished for prs on the cr
+  watch" (2026-11-09): superseded by `orchestrator.md` section 5's dispatch at
+  the fixer's push, with `bus.sh dispatch` refusing a red head (2026-11-15).
+- Mandate 6715477401: superseded by 6893738184 (2026-11-15).
+- R3's reading of this file in full (2026-11-13) and the card answer "Count it,
+  raise the cap (Recommended)" (2026-11-15): superseded by "excluded by the
+  corpus but still needs to be re-read on changes" (2026-11-15).
+- Durable policy memory, the full corpus re-read after every compaction
+  (2026-10-24, 2026-10-25, 2026-11-09) and the session-start corpus hook
+  (2026-10-21): superseded by R3 (2026-11-13), "Rules in full" and the 2026-11-15
+  reading rules (card "Retire K11, K12 on parity (Recommended)").
+- Non-critical outside and self-fed work goes to round 11 if it moves closure
+  (2026-11-12): superseded by the 2026-11-13 fold rule.
+- Severity exemption stays (2026-11-11, item 1): narrowed by card P2.
+- Every-sweep slip proposals and continuous triage (2026-10, 2026-11):
+  superseded by the freeze shape and once-per-round triage (2026-11-13,
+  2026-11-14).
+- Triage bar 10% / keep 5% (before 2026-11-08): superseded by 20% / 10%.
+- Spent with round 10's closure (v10.0.0, 2026-11-15): "Nothing is to be moved
+  to round 11" (2026-11-01); the closure definition and gating list (2026-11-07,
+  2026-11-13); "catalog PR goes after v10.0.0 stamp" (2026-11-04); the 15/11
+  date, its workarounds and bypass authority (2026-11-13, 2026-11-14); "Only
+  land gating PRs as long as CI capacity is full" and the two top non-gating
+  groups (2026-11-14); the soak before v10.0.0 (2026-11-11, 2026-11-12,
+  2026-11-14); part D's round-10 condition (2026-11-13); the round-11 session
+  start (2026-11-14); the overnight run and its Fable fallback (2026-11-14); the
+  2026-11-08 top set and zero-slip directive (2026-10-24); the 2026-11-12
+  catalog, learner and Pages answers; the 2026-11-11 above-cap starts (items 2,
+  3, 8); the 2026-11-13 handoff archive (item 4).
diff --git a/dev/programme/delivery/3626.md b/dev/programme/delivery/3626.md
new file mode 100644
index 0000000000..fa28a2474c
--- /dev/null
+++ b/dev/programme/delivery/3626.md
@@ -0,0 +1 @@
+- [#3626](https://github.com/tvofi/heatpump_optimizer/pull/3626) — **open**, R11-PRE-RULINGS-FILE: r11 pre rulings file (R11-PRE-RULINGS-FILE)
diff --git a/tests/layout.json b/tests/layout.json
index 497917b883..39abcadc04 100644
--- a/tests/layout.json
+++ b/tests/layout.json
@@ -67,9 +67,10 @@
   },
   {
    "name": "dev/programme",
-   "why": "the fix programme record: the living handover, the plan of record, delivery rows, live carries, rosters, the register, proposal-triage rulings",
+   "why": "the fix programme record: the living handover, the owner's standing rulings, the plan of record, delivery rows, live carries, rosters, the register, proposal-triage rulings",
    "globs": [
     "dev/programme/HANDOVER.md",
+    "dev/programme/RULINGS.md",
     "dev/programme/plan-*.md",
     "dev/programme/delivery/*.md",
     "dev/programme/carries/carry-*.json",
diff --git a/tools/audit/seat/hooks/liveness.py b/tools/audit/seat/hooks/liveness.py
index e92bbc6e89..cc22f3cc1e 100644
--- a/tools/audit/seat/hooks/liveness.py
+++ b/tools/audit/seat/hooks/liveness.py
@@ -26,8 +26,12 @@ This hook runs at both events and prints, on stdout (which the session reads):
                  runs inside tick_loop.sh's pass, so no standalone process is sought;
   MISSING        a checkout the state names (orch-checkout and the *checkout* keys
                  of sweep-overlay.json) that is not a directory;
-  READ-PROOF     the policy corpus at origin/main is written to policy-corpus.txt,
-                 its last line a `--prove <sha256>` command; a compact-owed marker
+  READ-PROOF     the owed corpus at origin/main is written to policy-corpus.txt:
+                 CLAUDE.md, orchestrator.md and every .claude/rules/ file in full,
+                 and of the instrument pages and dev/programme/RULINGS.md only those
+                 changed since the last accepted proof (its manifest,
+                 policy-proven.json); its last line a
+                 `--prove <sha256>` command; a compact-owed marker
                  stands, and the UserPromptSubmit event re-raises the obligation
                  every prompt until `liveness.py --state S --prove <sha256>` clears it;
   the digest     digest/digest.txt, verbatim;
@@ -65,7 +69,15 @@ def _env_min(name: str, default: float) -> float:
         return default
 
 
-CORPUS = ("CLAUDE.md", "dev/governance/roles/orchestrator.md", "tools/audit/seat/INSTRUMENTS.md")
+# Owner rulings 2026-11-13 (cards P6 and R3) and 2026-11-15 ("Rules in full"; the
+# rulings file re-read "on changes, just like instruments.md"): the core and the
+# rules are read in full after every compaction; the instrument pages and the
+# rulings file only where they changed since the last accepted proof. A missing
+# rulings file is a removed page, not a missing core file.
+CORE = ("CLAUDE.md", "dev/governance/roles/orchestrator.md")
+FULL = (".claude/rules/",)
+BY_CHANGE = ("tools/audit/seat/INSTRUMENTS.md", "tools/audit/seat/instruments/", "dev/programme/RULINGS.md")
+PENDING, PROVEN = "policy-corpus.json", "policy-proven.json"
 
 
 def _git(repo: str, *args: str) -> str | None:
@@ -73,20 +85,45 @@ def _git(repo: str, *args: str) -> str | None:
     return r.stdout if r.returncode == 0 else None
 
 
+def _blobs(repo: str, paths: tuple[str, ...]) -> dict[str, str] | None:
+    """{path: blob sha} of every file under `paths` at origin/main, or None."""
+    out = _git(repo, "ls-tree", "-r", "origin/main", "--", *paths)
+    if out is None:
+        return None
+    blobs = {}
+    for ln in out.splitlines():
+        meta, _, name = ln.partition("\t")
+        f = meta.split()
+        if len(f) == 3 and f[1] == "blob":
+            blobs[name] = f[2]
+    return blobs
+
+
 def write_corpus(state: Path, repo: str) -> str | None:
-    """The policy corpus at origin/main in one file; returns the sha256 of its body, or None."""
-    names = list(CORPUS)
-    rules = _git(repo, "ls-tree", "-r", "--name-only", "origin/main", ".claude/rules/")
-    if rules is None:
+    """The owed corpus at origin/main in one file; returns the sha256 of its body, or None.
+
+    Every CORE file and every file under FULL in full; of BY_CHANGE, only the files whose blob differs from the
+    last accepted proof's manifest (all of them when no manifest reads), and the names
+    of those gone since. A missing CORE file writes nothing: the read is not owed short."""
+    core, full, rest = _blobs(repo, CORE), _blobs(repo, FULL), _blobs(repo, BY_CHANGE)
+    if core is None or full is None or rest is None:
         return None
-    names += rules.split()
+    try:
+        proven = json.loads((state / PROVEN).read_text())
+        assert isinstance(proven, dict)
+    except (OSError, ValueError, AssertionError):
+        proven = {}
+    changed = sorted(n for n, b in rest.items() if proven.get(n) != b)
+    gone = sorted(n for n in proven if n not in rest and n not in core and n not in full)
     body = ""
-    for n in names:
+    for n in [*CORE, *sorted(full), *changed]:
         t = _git(repo, "show", f"origin/main:{n}")
         if t is None:
             return None
         body += f"=== {n} ===\n{t}\n"
+    body += f"=== unchanged since the last proof: {len(rest) - len(changed)} page(s); removed: {', '.join(gone) or 'none'} ===\n"
     sha = hashlib.sha256(body.encode()).hexdigest()
+    (state / PENDING).write_text(json.dumps({**core, **full, **rest}, sort_keys=True) + "\n")
     (state / "policy-corpus.txt").write_text(
         body + f"PROOF: python3 -I {Path(__file__).resolve()} --state {state} --prove {sha}\n")
     (state / "compact-owed").write_text(sha + "\n")
@@ -102,6 +139,10 @@ def prove(state: Path, sha: str) -> int:
     if sha.strip() != want:
         print("READ-PROOF refused: the sha256 is not the corpus file's; read policy-corpus.txt to its last line")
         return 1
+    try:
+        (state / PENDING).replace(state / PROVEN)
+    except OSError:
+        (state / PROVEN).unlink(missing_ok=True)  # no manifest: the next corpus carries every page
     (state / "compact-owed").unlink()
     print("read-proof accepted")
     return 0
@@ -141,8 +182,8 @@ def report(state: Path, event: str, transcript: str, now: float) -> list[str]:
     py = sys.executable
     stamp = state / "policy-reread.stamp"
     if event == "PostCompact":
-        out.append("POLICY-REREAD owed: this session was compacted; re-read CLAUDE.md, the rules and the role "
-                   f"contracts from fresh origin/main, then python3 -I tools/audit/seat/policy_reread_check.py --stamp {stamp} --write-stamp")
+        out.append("POLICY-REREAD owed: this session was compacted; read policy-corpus.txt (the core and the rules in full, "
+                   f"the instrument pages and rulings changed since the last proof), then python3 -I tools/audit/seat/policy_reread_check.py --stamp {stamp} --write-stamp")
     else:
         cmd = [py, "-I", str(SEAT / "policy_reread_check.py"), "--stamp", str(stamp),
                "--transcript", transcript or os.devnull + ".none"]  # no transcript: unreadable, so OWED
@@ -150,11 +191,14 @@ def report(state: Path, event: str, transcript: str, now: float) -> list[str]:
         if r.returncode == 2:
             out.append(f"UNREADABLE policy_reread_check: {(r.stderr or r.stdout).strip()[-80:]}")
         elif r.returncode != 0 or not r.stdout.strip().startswith("OK"):
-            out.append("POLICY-REREAD owed: re-read CLAUDE.md, the rules and the role contracts from fresh origin/main, "
-                       f"then policy_reread_check.py --stamp {stamp} --write-stamp")
+            out.append("POLICY-REREAD owed: read policy-corpus.txt (the core and the rules in full, the instrument "
+                       f"pages and rulings changed since the last proof), then policy_reread_check.py --stamp {stamp} --write-stamp")
     owed = event == "PostCompact" or any(ln.startswith("POLICY-REREAD") for ln in out)
-    if owed and write_corpus(state, repo):
-        out.append(f"READ-PROOF owed: read {state / 'policy-corpus.txt'} to its last line and run the PROOF command there")
+    if owed:
+        if write_corpus(state, repo):
+            out.append(f"READ-PROOF owed: read {state / 'policy-corpus.txt'} to its last line and run the PROOF command there")
+        else:  # no partial corpus: the whole read is owed from the tree
+            out.append(f"POLICY-CORPUS unwritten at origin/main: read {', '.join(CORE + FULL + BY_CHANGE)} in full instead")
     b = subprocess.run([py, "-I", str(SEAT / "beatd.py"), "status", "--state", str(state), "--repo", repo],
                        capture_output=True, text=True)
     if b.returncode == 2 or not b.stdout.strip():
diff --git a/tools/audit/seat/hooks_setup.py b/tools/audit/seat/hooks_setup.py
index 0aa1805946..8470ab9ca4 100644
--- a/tools/audit/seat/hooks_setup.py
+++ b/tools/audit/seat/hooks_setup.py
@@ -325,7 +325,10 @@ def cases() -> dict[str, bool]:
                            check=True, capture_output=True)
         s, fd = _fixture_state(tmp / "readproof")
         repo = Path((s / "orch-checkout").read_text().strip())
-        for n in ("CLAUDE.md", "dev/governance/roles/orchestrator.md", "tools/audit/seat/INSTRUMENTS.md", ".claude/rules/r.md"):
+        for n in ("CLAUDE.md", "dev/governance/roles/orchestrator.md", "dev/programme/RULINGS.md",
+                  "tools/audit/seat/INSTRUMENTS.md", ".claude/rules/r.md", ".claude/rules/gone.md",
+                  "tools/audit/seat/instruments/a.md",
+                  "tools/audit/seat/instruments/b.md"):
             (repo / n).parent.mkdir(parents=True, exist_ok=True)
             (repo / n).write_text(f"policy {n}\n")
         git(repo, "add", "-A")
@@ -337,7 +340,8 @@ def cases() -> dict[str, bool]:
         sha = proof.rpartition("--prove ")[2]
         res["read-proof: PostCompact writes the corpus with a sha256 proof last line and a compact-owed marker"] = (
             "READ-PROOF owed" in out and proof.startswith("PROOF: ") and len(sha) == 64 and (s / "compact-owed").is_file()
-            and "policy CLAUDE.md" in corpus and "policy .claude/rules/r.md" in corpus)
+            and "policy CLAUDE.md" in corpus and "policy .claude/rules/r.md" in corpus
+            and "policy dev/programme/RULINGS.md" in corpus and "policy tools/audit/seat/instruments/b.md" in corpus)
         res["read-proof: a UserPromptSubmit re-raises the obligation every prompt until the proof clears it"] = (
             all("READ-PROOF owed" in _run_hook("liveness.py", s, {"hook_event_name": "UserPromptSubmit"}) for _ in range(2)))
         res["read-proof: a wrong sha256 is refused and the marker stands"] = (
@@ -350,6 +354,54 @@ def cases() -> dict[str, bool]:
             and "session" not in proof)
         res["read-proof: a healthy SessionStart with a fresh stamp writes no marker (null control)"] = (
             (_run_hook("liveness.py", s), not (s / "compact-owed").exists())[1])
+        # owner rulings 2026-11-13 (R3) and 2026-11-15: the core and the rules in full,
+        # the instrument pages and the rulings file by change since the last proof
+        _run_hook("liveness.py", s, {"hook_event_name": "PostCompact"})
+        same = (s / "policy-corpus.txt").read_text()
+        res["read-proof: nothing changed since the proof reads the core and the rules only (null control)"] = (
+            "policy CLAUDE.md" in same and "policy dev/governance/roles/orchestrator.md" in same
+            and "policy .claude/rules/r.md" in same and "RULINGS.md ===" not in same
+            and "instruments/a.md ===" not in same and "instruments/b.md ===" not in same
+            and "INSTRUMENTS.md ===" not in same
+            and "unchanged since the last proof: 4 page(s); removed: none" in same)
+        prove_last = lambda: _run_hook("liveness.py", s, args=[  # noqa: E731
+            "--state", str(s), "--prove", (s / "policy-corpus.txt").read_text().splitlines()[-1].rpartition("--prove ")[2]])
+        prove_last()
+        (repo / "tools/audit/seat/instruments/a.md").write_text("policy a.md changed\n")
+        (repo / "dev/programme/RULINGS.md").write_text("policy rulings changed\n")
+        (repo / ".claude/rules/gone.md").unlink()
+        git(repo, "add", "-A")
+        git(repo, "commit", "-qm", "change")
+        git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
+        _run_hook("liveness.py", s, {"hook_event_name": "PostCompact"})
+        again = (s / "policy-corpus.txt").read_text()
+        res["read-proof: after a proof the core and an unchanged rule are in full, changed pages and rulings are in, an unchanged page is out"] = (
+            "policy CLAUDE.md" in again and "policy dev/governance/roles/orchestrator.md" in again
+            and "policy .claude/rules/r.md" in again and "policy rulings changed" in again
+            and "policy a.md changed" in again
+            and "instruments/b.md" not in again and "INSTRUMENTS.md ===" not in again
+            and "removed: .claude/rules/gone.md" in again)
+        (s / "policy-proven.json").unlink()
+        _run_hook("liveness.py", s, {"hook_event_name": "PostCompact"})
+        res["read-proof: with no proof manifest every page is in (null control for by-change)"] = (
+            "policy tools/audit/seat/instruments/b.md" in (s / "policy-corpus.txt").read_text())
+        prove_last()
+        (repo / "dev/programme/RULINGS.md").unlink()
+        git(repo, "add", "-A")
+        git(repo, "commit", "-qm", "no rulings")
+        git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
+        out = _run_hook("liveness.py", s, {"hook_event_name": "PostCompact"})
+        res["read-proof: a rulings file gone from origin/main is a removed page, and the corpus is still written"] = (
+            "READ-PROOF owed" in out and (s / "compact-owed").is_file()
+            and "removed: dev/programme/RULINGS.md" in (s / "policy-corpus.txt").read_text())
+        (repo / "dev/governance/roles/orchestrator.md").unlink()
+        git(repo, "add", "-A")
+        git(repo, "commit", "-qm", "no contract")
+        git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
+        (s / "compact-owed").unlink(missing_ok=True)
+        out = _run_hook("liveness.py", s, {"hook_event_name": "PostCompact"})
+        res["read-proof: a core file missing at origin/main writes no short corpus and says so"] = (
+            "POLICY-CORPUS unwritten" in out and not (s / "compact-owed").exists())
         os.close(fd)
         # checkout presence, from the state overlay
         s, fd = _fixture_state(tmp / "checkouts")
@@ -443,6 +495,15 @@ MUTANTS = [  # (label, old text, new text): each must turn at least one case red
     ("the relay is never judged by its log", "    if age is not None and age > _env_min(\"HPO_RELAY_STALE_MIN\", 15):", "    if False:"),
     ("a missing checkout is never reported", "sorted(names.items()) if not Path(v).is_dir()]", "sorted(names.items()) if False]"),
     ("the read-proof accepts any sha256", "    if sha.strip() != want:", "    if False:"),
+    ("the corpus carries every page, changed or not", "if proven.get(n) != b)", "if True)"),
+    ("the proof never records its manifest", "        (state / PENDING).replace(state / PROVEN)\n", "        pass\n"),
+    ("the corpus carries no changed page", "    for n in [*CORE, *sorted(full), *changed]:", "    for n in [*CORE, *sorted(full)]:"),
+    ("the corpus drops the rules", "    for n in [*CORE, *sorted(full), *changed]:", "    for n in [*CORE, *changed]:"),
+    ("the rulings file is read in full", "CORE = (\"CLAUDE.md\", \"dev/governance/roles/orchestrator.md\")",
+     "CORE = (\"CLAUDE.md\", \"dev/governance/roles/orchestrator.md\", \"dev/programme/RULINGS.md\")"),
+    ("a changed rulings file is dropped", ", \"dev/programme/RULINGS.md\")\n", ")\n"),
+    ("the rules are read by change", "FULL = (\".claude/rules/\",)\nBY_CHANGE = (", "FULL = ()\nBY_CHANGE = (\".claude/rules/\", "),
+    ("a missing core file still writes a corpus", "        if t is None:\n            return None\n        body +=", "        if t is None:\n            continue\n        body +="),
     ("the prompt arm never re-raises the proof", "        if (state / \"compact-owed\").exists():", "        if False:"),
     ("beatd run never refuses an interpreter under the floor", "    if sys.version_info < FLOOR:\n", "    if False:\n"),
     ("beatd run records no launch", "(d / \"launch.json\").write_text(", "(d / \"launch.jsonX\").write_text("),
diff --git a/tools/audit/seat/instruments/hooks_setup.py.md b/tools/audit/seat/instruments/hooks_setup.py.md
index 6ca6e2b8b7..fe9756cc40 100644
--- a/tools/audit/seat/instruments/hooks_setup.py.md
+++ b/tools/audit/seat/instruments/hooks_setup.py.md
@@ -4,7 +4,7 @@
 
 | hook | event | script | does | why it exists |
 |---|---|---|---|---|
-| liveness | SessionStart, PostCompact, UserPromptSubmit | `hooks/liveness.py` | demands a fresh policy re-read (`policy_reread_check.py`; always on PostCompact); prints `DEAD`/`ALARM` per late beat job and for a free `beatd.lock` (`beatd.py status`, so the loop list is the job table), `STALE` for an alive file under `$HPO_STATE_DIR/alive/` and for a digest whose `digest.txt` and beat journal both stood still, `DEAD beatd` is relaunched (`RESTARTED`/`auto-restart FAILED`) from `beatd/launch.json` under the seat venv's PATH, beatd only; `DEAD relay` when `cloud-relay.log` is stale; `MISSING` for an absent checkout in the state overlay; on PostCompact it writes `policy-corpus.txt` and a `compact-owed` marker that every UserPromptSubmit re-raises until `--prove <sha256>` clears it; then the digest, then one `ARM:` line | after a compaction nobody re-armed the wake loop and owed lines stood unread for hours (2026-11-01) |
+| liveness | SessionStart, PostCompact, UserPromptSubmit | `hooks/liveness.py` | demands a fresh policy re-read (`policy_reread_check.py`; always on PostCompact); prints `DEAD`/`ALARM` per late beat job and for a free `beatd.lock` (`beatd.py status`, so the loop list is the job table), `STALE` for an alive file under `$HPO_STATE_DIR/alive/` and for a digest whose `digest.txt` and beat journal both stood still, `DEAD beatd` is relaunched (`RESTARTED`/`auto-restart FAILED`) from `beatd/launch.json` under the seat venv's PATH, beatd only; `DEAD relay` when `cloud-relay.log` is stale; `MISSING` for an absent checkout in the state overlay; on PostCompact it writes `policy-corpus.txt` (`CLAUDE.md`, `orchestrator.md` and `.claude/rules/` in full; of `INSTRUMENTS.md`, `instruments/` and `dev/programme/RULINGS.md` only the files whose blob differs from the last accepted proof's manifest `policy-proven.json`, every one when none reads; a missing core file writes none and prints `POLICY-CORPUS unwritten`, a missing rulings file is listed as removed) and a `compact-owed` marker that every UserPromptSubmit re-raises until `--prove <sha256>` clears it; then the digest, then one `ARM:` line | after a compaction nobody re-armed the wake loop and owed lines stood unread for hours (2026-11-01) |
 | seat-interpreter | SessionStart | `hooks/seat_interpreter.py` | runs `seat_venv.sh --check`; one `SEAT-INTERPRETER` line when it refuses | a temp cleanup deleted the seat venv unnoticed (2026-10-03) |
 | git-identity | SessionStart | `hooks/git_identity.py` | sets the orchestrator checkout's local `user.name`/`user.email` from `$HPO_STATE_DIR/git-identity` when they differ | a commit under the host's default identity is refused only after the push (decision 0011) |
 | Bash guard | PreToolUse, project-level | `.claude/hooks/pre-bash.sh`, second arm | exit 2 for `git checkout/switch/reset/pull/merge/rebase/stash/clean/restore` whose cwd, `cd` or `-C` resolves to the checkout named in `$HPO_STATE_DIR/orch-checkout`, read through the hook's one command-position parser (`HPO_PRE_BASH_PARSE_PY`), so `bash -c`, `eval`, `( )` and `$( )` bodies count | `beatd`, `tick_loop.sh` and `cloud_relay.sh` run from that checkout and bash reads a script incrementally |
diff --git a/tools/audit/seat/sweep_template.md b/tools/audit/seat/sweep_template.md
index ae12f0623d..0afbebb310 100644
--- a/tools/audit/seat/sweep_template.md
+++ b/tools/audit/seat/sweep_template.md
@@ -60,7 +60,7 @@ rendered text that no overlay value supplied.
 <!-- sweep:begin -->
 ORCHESTRATOR SWEEP, round {{round}}, repository {{repo}}. Read {{seat_ledger}} first. Run each instrument from its path in the tree, from {{orch_checkout}}, with `tools/audit/seat/shims` first on PATH. Then, briefly:
 
-(0) Policy re-read. Run `python3 -I tools/audit/seat/policy_reread_check.py --transcript {{transcript}} --stamp {{policy_stamp}}`. On OWED: `git -C {{orch_checkout}} fetch origin`, then read `CLAUDE.md`, every policy file its index names, and `tools/audit/seat/INSTRUMENTS.md` with `git -C {{orch_checkout}} show origin/main:<path>`; act on any delta against current practice; then `python3 -I tools/audit/seat/policy_reread_check.py --stamp {{policy_stamp}} --write-stamp`, and log the re-read in {{seat_ledger}}. Before the first dispatch of a session run `python3 -I tools/audit/seat/seat_gen.py lock` and stop if it prints REFUSED. While the check prints OWED (exit 1), that is, until `--write-stamp` ran after the newest compaction, this sweep is not clean, whatever the rest of the board says.
+(0) Policy re-read. Run `python3 -I tools/audit/seat/policy_reread_check.py --transcript {{transcript}} --stamp {{policy_stamp}}`. On OWED: `git -C {{orch_checkout}} fetch origin`, then read `CLAUDE.md`, `dev/governance/roles/orchestrator.md` and every `.claude/rules/` file in full, and of the instrument pages and `dev/programme/RULINGS.md` only those the liveness hook's `policy-corpus.txt` carries as changed since the last proof (owner rulings 2026-11-13, card R3, and 2026-11-15), each with `git -C {{orch_checkout}} show origin/main:<path>`; act on any delta against current practice; then `python3 -I tools/audit/seat/policy_reread_check.py --stamp {{policy_stamp}} --write-stamp`, and log the re-read in {{seat_ledger}}. Before the first dispatch of a session run `python3 -I tools/audit/seat/seat_gen.py lock` and stop if it prints REFUSED. While the check prints OWED (exit 1), that is, until `--write-stamp` ran after the newest compaction, this sweep is not clean, whatever the rest of the board says.
 
 (1) Seats. Cloud seats are uncapped. A fixer for a NEW roster group is dispatched only while fewer than 3 handoffs wait without a pull request and 6 to 10 pull requests are open (owner ruling, 2026-10-28; `tools/audit/seat/pr_cap.py` `dispatch-gate` measures its WIP arm); reviews, repairs and openers are never capped, and a ready critical-path group dispatches past every cap (`dev/governance/roles/orchestrator.md` section 5). Resume the next queued seat from {{seat_ledger}}. Dispatch a record pull request's reviewer (triage, roster batches) on sonnet, and a design, code or architecture pull request's reviewer on opus. Seat worktrees live under {{seat_root}}, each named absolute in its brief (`dev/governance/roles/orchestrator.md` section 5). A handed-off seat is not resumed and an unblocked roster group gets a fixer (`dev/governance/roles/nudge.md` steps 14 and 16).
 

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
