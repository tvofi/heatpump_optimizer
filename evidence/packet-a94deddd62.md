# Review packet #3808
head: a94deddd62ca54f9c81bc1a558c398887d67ddf7
base: 99436a082c67ad5dbb4afc293506af010d6ee8df

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=135546521147 success
arch-score / arch-score id=135656811715 success
arm id=135545059696 skipped
budget-raise-gate / budget-raise-gate id=135656813569 success
cancel-superseded id=135656900819 success
codeql id=135586100945 skipped
codeql / Analyze (actions) id=135656812432 success
codeql / Analyze (javascript-typescript) id=135656812589 success
codeql / Analyze (python) id=135656814813 success
gate id=135683847947 success
governance id=135586100331 skipped
governance / env-matrix id=135656809464 success
governance / instrument-self-tests id=135656813284 success
governance / policy-docs id=135656813945 success
governance / record id=135656814135 skipped
governance / wave-script id=135656812833 success
hassfest id=135586100273 skipped
hassfest / hassfest id=135656812199 success
kernel-points id=135656811383 skipped
pr-contract id=135586101847 skipped
pr-contract / pr-contract id=135668840021 success
prelude id=135656810221 success
refresh id=135656808342 success
sweep-self id=135692749269 skipped
tests id=135586100422 skipped
tests / arch-instrument id=135656818948 success
tests / briefs id=135656813198 success
tests / browser id=135656817283 success
tests / ci-ratchet id=135656820921 skipped
tests / claims-autofix id=135656819810 skipped
tests / closure-scope id=135656813227 success
tests / closures id=135656818933 success
tests / closures-autofix id=135656819974 skipped
tests / coverage id=135656817755 skipped
tests / coverage-ratchet id=135656819137 skipped
tests / fast (3.14) id=135656817696 success
tests / graders-head-copy id=135656820151 success
tests / lane-proofs id=135656820630 success
tests / mutation id=135656812526 success
tests / mutation-autofix id=135656820788 skipped
tests / mutation-pins id=135656818118 skipped
tests / nightly-ha (2025.2.0) id=135656816559 success
tests / nightly-ha (stable) id=135656818079 success
tests / nightly-status id=135656812762 success
tests / replay id=135656818092 skipped
tests / typing id=135656816872 success
validate id=135586100561 skipped
validate / validate-hacs id=135656813446 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: FULL -- every test script runs, nothing is scoped out.
             no segment of this names a program this check knows
  unverified git archive origin/plan/r11 dev/audit/rounds/round11/D5/s7 dev/audit/rounds/round11/D5/s8 dev/audit/rounds/round11/D5/s9
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/comment_ratchet.py
             `tests/comment_ratchet.py` is in the tree at this head
  ok         python3 tests/comment_ratchet.py --self-test
             `tests/comment_ratchet.py` is in the tree at this head
  ok         python3 tests/comment_ratchet.py --text-only 1723f9fdc9d8a6e6987190d2887686297a621dd4
             `tests/comment_ratchet.py` is in the tree at this head
  unverified PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D5/s9/comments.py --repo . --ref 1723f9fdc9d8a6e6987190d2887686297a621dd4 --show
             the path `$EXPORT/dev/audit/rounds/round11/D5/s9/comments.py` is a template or an expansion, not a literal
  unverified PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D5/s9/stale_paths.py --repo . --ref 1723f9fdc9d8a6e6987190d2887686297a621dd4
             the path `$EXPORT/dev/audit/rounds/round11/D5/s9/stale_paths.py` is a template or an expansion, not a literal
  ok         python3 tools/audit/seat/moved_paths.py tests/throwaway_git.sh $(git ls-files tests/hastub)
             `tools/audit/seat/moved_paths.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r11_comments_ratchet_reconcile.py $EXPORT
             `dev/audit/harnesses/r11_comments_ratchet_reconcile.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff 1723f9fdc9d8a6e6987190d2887686297a621dd4
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/closure.py selftest
             `tests/closure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:tests:custom_components python3 tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/layout.py
             `tests/layout.py` is in the tree at this head
  ok         python3 tests/env_drift.py --claims-only origin/main
             `tests/env_drift.py` is in the tree at this head
  ok         tests/closure.py changes the gate itself
             `tests/closure.py` is in the tree at this head

FIGURES: 13 resolved, 4 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: delta (later round over the reviewed head bdcca2fb9f21edbeace79cfc108f38c38f4b1f46)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at bdcca2fb9f21edbeace79cfc108f38c38f4b1f46
Fix review: merge bdcca2fb9f21edbeace79cfc108f38c38f4b1f46
bus-nonce: 9a2d2c5fec354887f54bd2d04690f3bd

Round 1, full scope: three-dot diff `99436a082c...bdcca2fb9f` (23 files), from a detached worktree at the head. `fix-review.md` at the merge base equals main's (`git diff <mb>...origin/main -- dev/governance/roles/` empty).

## Evidence

- Step 1, mutation: the fixer's `r11_comments_ratchet_mutants.py` re-run at the head: `RESULT baseline_rc=0`, `RESULT killed=9 survived=0`, every kill a named arm. My own five mutants on predicates the PR does not name (`ev/rev_mutants.py`): `_split_trailing`, `_is_heading`, `_is_code`, `_is_break` killed by their named arms; `_is_rule -> False` survives the self-test (see the notes).
- Step 1, wiring end to end: `doc_claims.py` at the head, clean tree `ALL 441 checks PASSED` (both ratchet rows ok); with a 41-word comment planted in `tests/edge.py`, `1 of 441 checks FAILED` on the ratchet row, `REFUSE tests/edge.py: long units 0 -> 1`, rc 1; plant removed after (`ev/doc_claims_clean.txt`, `ev/doc_claims_plant.txt`).
- Step 2, the finder's harness (`plan/r11` `D5/s9/comments.py`, exported, not the fixer's): at the merge base 99436a082c `RESULT C5-long=824`, 15 of them in p1 files (`tests/hastub/**`, `tests/throwaway_git.sh`); at the head `RESULT C5-long=809`, 0 in p1 files. The harness's `--perturb` arm moves at the head (`perturb_C5 ... long 1->0`, `perturb_C2 ... 18->0`). `C2-path=3`, `C2-moved=15` flat at both ends.
- Step 3, null control: outside p1 the harness reads 824 - 15 = 809 at both ends, so no other file moved. The ratchet at the head against the merge base: `RESULT base=99436a082c67 files=96 long_units_base=1642 long_units_head=1618`, `comment_ratchet: OK`; `--self-test` OK.
- `--text-only 99436a082c`: `RESULT code_changed_files=5 line_shifted_hunks=9`; CODE lines name only `comment_ratchet.py`, `doc_claims.py`, `entities.py`, `run.sh` and the new file; no `tests/hastub/` file or `throwaway_git.sh` changes a code token or a line count. The 14 text files read as sentence splits that keep each claim.
- Step 4/5: `VERSION`, the manifest, `RELEASE_NOTES.md`, both claim files and both budget files are byte-identical to the merge base.
- Step 6, the class: the rule is the ratchet over SCOPE; every in-scope tracked `tests/` file but `tests/closure.py` is in `doc_claims.py`'s recorded closure (95 of 96), and a `closure.py` edit forces FULL, so no in-scope edit escapes the arm. CI runs `run.sh` with `fetch-depth: 0` and `GOLDEN_REF` set, so the ratchet base resolves there.
- Step 13: `git merge-tree --write-tree origin/main bdcca2fb9f` exit 0.
- Step 14: the `closures.json` growth (doc_claims closure + 54 entries, seconds 11.4 -> 31.0) and the three INERT removals are the reads `comment_ratchet.gate` makes; removing the arm removes them. `closure.py selftest`: `ALL 118 closure shrink pins PASSED`.
- Step 15: the design note at a2823ffea0 (Notes for the fixer) permits the ratchet as an arm of an existing gate script when the script-run budgets bind, so the `doc_claims.py` route is inside the design, not a departure.
- Step 7/12: PR head is bdcca2fb9f at review time, the body names it, author `hpo-author[bot]` (the packet's open point that the author shows as tvofi does not hold).
- Step 11, checks at the head: the one red, `gate` (run 44484273149, `pull_request` edit run), prints `FAIL run(s) [44484251682] at this head are still being judged; their gate decides`: a pending-sequencing red that the code run's own gate will re-decide, not a code finding. The code run's `tests/*` lanes were still queued when I read them; this verdict cites CI for the suite and asserts nothing about it.

## Notes (non-blocking)

- Note: carry-missing: the body's three hand-off notes (harness-only units classed by the reconcile harness; how comments-production consumes `comment_ratchet.in_scope` through `check_comment_length` and re-records with `--single`; the design-section-6 reconcile) are not in either group's `brief` on `plan/r11` `.claude/workflows/wave-r11-groups.json` (no keyword of them present in R11-SEAM-comments-tests or R11-SEAM-comments-production at 50a932de3b); a PR body does not propagate them. Neither group id is a token `carry_audit.py` accepts (upper-case only), which is P-R11-84. Carry: dismissed: no parseable destination exists until P-R11-84; the orchestrator lands the three texts in those two roster briefs on plan/r11
- Note: test-gap: `_is_rule` replaced by `False` survives `--self-test`, because `_is_heading` also catches dash, equals, hash and tilde rules; only an underscore or asterisk rule line would join the next sentence, and the effect is a false refusal (fail-closed). On the head tree the mutant changes no count: 1618 long units both ways (`ev/is_rule_tree.txt`). Carry: dismissed: fail-closed predicate with zero effect on the measured tree
- Note: stale-figure: the body prices the arm at `doc_claims.py` "11 s"; the closure this PR records reads `"seconds": 31.0`. Carry: dismissed: body figure only, the recorded closure carries the measured value

## Delta diff: git diff bdcca2fb9f21edbeace79cfc108f38c38f4b1f46 a94deddd62ca54f9c81bc1a558c398887d67ddf7
diff --git a/tests/closures.json b/tests/closures.json
index f87533d2aa..64f4b642b0 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -1817,6 +1817,7 @@
    "tests/ci_budgets.json",
    "tests/ci_ratchet.py",
    "tests/closures.json",
+   "tests/comment_ratchet.py",
    "tests/config_flow_steps.py",
    "tests/coverage_budgets.json",
    "tests/coverage_ratchet.py",
@@ -2106,6 +2107,7 @@
    "tools/audit/seat/state_docs.py",
    "tools/audit/seat/tmp_paths.py",
    "tools/audit/seat/topic_grammar.py",
+   "tools/audit/text_ledger.py",
    "tools/ci/alert_list.py",
    "tools/ci/codescan_wait.py",
    "tools/ci/gate.py",
@@ -5875,7 +5877,7 @@
   },
   "tests/edge.py": {
    "rc": 0,
-   "seconds": 21.5
+   "seconds": 60.2
   },
   "tests/entities.py": {
    "rc": 0,
@@ -5891,7 +5893,7 @@
   },
   "tests/finite_boundary.py": {
    "rc": 0,
-   "seconds": 90.4
+   "seconds": 193.8
   },
   "tests/frontend.py": {
    "rc": 0,
@@ -5943,7 +5945,7 @@
   },
   "tests/stress.py": {
    "rc": 0,
-   "seconds": 463.0
+   "seconds": 928.7
   },
   "tests/structure.py": {
    "rc": 0,
@@ -5951,7 +5953,7 @@
   },
   "tests/typing_ruler.py": {
    "rc": 0,
-   "seconds": 20.8
+   "seconds": 0.6
   },
   "tests/validate.py": {
    "rc": 0,

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
