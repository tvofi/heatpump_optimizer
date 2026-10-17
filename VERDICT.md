Fix review: merge dd3e87c60c89c5f60e05b990647a224f56a0bde9
bus-nonce: 5e822b0f02722375e0616afdccba9dbc

Round 10, first pass (no re-cut owed). Reviewed adversarially from a fresh
detached worktree at dd3e87c60c89c5f60e05b990647a224f56a0bde9, against merge
base fbd99a3d9e3738499bc1981e49188c0689589061. `git diff $(merge-base)...origin/main
-- dev/governance/roles/` is empty, so this contract is current.

The fix is a floor re-validation backstop at the end of
`tools/coverage/coverage_tree.sh` (re-grade the combined JSON with the pinned
`tests/coverage_ratchet.py`; when a reused measurement grades below floor,
re-measure every script without reuse) plus the RCA doc
`dev/audit/rca/R10-RCA-coverage-base-reuse.md`. I measured with the pinned
grader itself over the real CI payloads, not any fixer-built harness.

RESULT mutation-proof (backstop deleted): python3 tests/coverage_ratchet.py over
  #2342's reused coverage-json (artifact 12096042211) prints
  "FAIL package coverage 95.61 % >= 96.0 % (20611/21558 statements)" and
  "FAIL every module >= 95.0 %  (4 below)" (early_cutoff.py 81.53 %,
  coordinator.py 84.14 %, sysid.py 91.28 %, price_model.py 94.77 %),
  "COVERAGE RATCHET BREACHED", rc=1.
RESULT mutation-proof (backstop restored): python3 tests/coverage_ratchet.py over
  #2341's fresh coverage-json (artifact 12079121316) prints
  "ok package coverage 98.61 %" and "ok every module >= 95.0 % (0 below)",
  "COVERAGE RATCHET PASSED", rc=0. Production statement count identical in both
  (21558 statements, 77 files); early_cutoff.py 128/157 reused vs 157/157 fresh,
  matching the RCA's quoted figures exactly.
RESULT null control: detection predicate
  `grep -qE "FAIL (package coverage|every module|config_flow\.py coverage)"`
  fires (rc 0) on the reused payload and is silent (rc 1) on the fresh payload,
  so the re-measure arm enters only on the red and not on a healthy tree.
RESULT metric-gamed (step 14): the backstop re-measures rather than
  short-circuits; it never touches coverage_budgets.json and never writes a
  forged verdict. Planted a genuine drop (early_cutoff.py 157->120 covered in a
  copy of the fresh payload); the grader still prints "FAIL every module >=
  95.0 % (1 below)" and rc=1, so a real regression survives the re-measure and
  reddens. Deleting the re-measure's `run_plan` would leave per/ empty and the
  grader refuses (zero statements), not green -- no skip-to-green path exists.
RESULT bash -n tools/coverage/coverage_tree.sh: clean. Deleting the backstop
  block (lines 282-306) yields a still-valid script (bash -n clean) whose output
  is the un-re-measured reused JSON -- the sole re-measure mechanism is the block.
RESULT python3 tests/closure.py selftest: "ALL 115 closure shrink pins PASSED".
RESULT python3 tests/entities.py: "ALL 2343 ENTITY CHECKS PASSED" -- the RCA doc
  is classified (INERT prefix "dev/audit/" in tests/closure.py:319); the delivery
  row is under the "dev/programme/" INERT prefix.
RESULT python3 tests/structure.py: "STRUCTURE RATCHET PASSED".
RESULT VERSION 7.0.0, manifest 7.0.0, RELEASE_NOTES.md heading untouched; the
  diff touches only coverage_tree.sh, the RCA doc and delivery/2349.md.
RESULT merge-tree --write-tree origin/main head: rc 0, no conflict on any path.

Red-check answer (step 11): the head's check-runs show coverage-ratchet success,
coverage success, fast (3.14) success, mutation success, nightly-status success;
no gate check is red on this PR. The body's "## Red checks" names coverage-ratchet
(the #2320/#2342/#2343/#2348/main recurrence) and answers with the cheaper
detector and its standing cost (8 s re-grade on every run; ~50 runner-minutes
re-measure only when a reused measurement grades below floor), satisfying the
defect-root-cause second trigger. Forward-carry "none" is correct: the
countermeasure is self-healing inside the instrument and imposes no new
precondition on a later stage.

Caveat (informational, non-blocking): the composed-proof job was still
in_progress at review time; it is not red and is a heavy job I do not re-run
(fix-review.md: cite CI's heavy runs). I did not re-run the ~50-minute full
re-measure; the fresh arm of the mutation proof is #2341's own CI payload, the
same measurement the backstop triggers.
