Carry 21 repair: pin the hotfix-scope classifier seam that the first review at a81d7f15 found uncovered. The scoped-prepr behaviour is unchanged; this round adds the self-test checks that kill the six surviving mutants the reviewer's driver named, and pins the one fail-closed property (`_rank`'s `except`) the skip now rests on.

## Review scope

`git diff a81d7f15293fc2101f42e48ade37ef7022c35517 becbe652ab6b321a680e5b45b61bfd897f2e0669` -- the two instrument files, plus the `tests/closures.json` re-record of `tests/harness_headers.py` prepr asked for (its rc field 1 to 0; membership unchanged). The hotfix-scope decision is unchanged; the one deliberate behaviour change is the P9 fix (the two skip defaults are no longer `export`ed, since every reader is in prepr's own shell and no child depends on inheriting a roster-chosen skip):

- `tools/pr/gate_priority.py`: new self-test arms that drive `main(["--hotfix", ...])` and read its stdout, and one that makes `roster_lib.show_roster` raise so `_rank`'s `except` arm is exercised and shown fail-closed. No change to `_rank`, `is_hotfix`, `derived_priority` or the CLI.
- `tools/pr/prepr.sh`: the main flow's code-steps line is lifted into `code_steps_line` so the self-test drives the same branch the main flow runs; the hotfix-scope self-test now runs the real `hotfix_class` (through `gate_priority.py --hotfix`) end to end against a fixture roster; the two skip defaults are no longer `export`ed (only this shell reads them, and a child must not inherit a skip chosen for one run). The hotfix-scope decision itself is byte-for-byte the decision at a81d7f15.

## Head

`becbe652ab6b321a680e5b45b61bfd897f2e0669`

## Mutation proof

The block was: the PR's own seven mutants (M1-M7) were killed, but the seam carrying the whole behaviour -- prepr's `hotfix_class` calling `gate_priority.py --hotfix`, and the CLI printing `is_hotfix` -- had no test. The prepr self-test stubbed `hotfix_class`; the gate_priority self-test called `is_hotfix()` directly, never `main(["--hotfix", ...])`. The reviewer's driver (`ev/driver.py` in the verdict evidence) named six survivors. Re-run at this head (driver HEAD set to this branch, plus one added mutant P9b), five of the six are KILLED, P9's target line no longer exists, its inverse P9b is KILLED, and the NULL control survives; P1-P6, G1, G2 and G4 stay KILLED:

    G5-cli-hotfix-inverted        KILLED  (gate_priority main prints int(not is_hotfix(...)))
    G5b-cli-hotfix-inverted-prepr KILLED  (same mutant, against prepr.sh --self-test, via the real hotfix_class)
    P8-classifier-asks-priority   KILLED  (hotfix_class calls --branch without --hotfix: a critical-path branch would scope, a hotfix would not)
    G3-except-fails-open          KILLED  (_rank's except returns RANK_HOTFIX: a failed read must be "not a hotfix", so a full prepr)
    P7-HOTFIX_SCOPED-dropped      KILLED  (HOTFIX_SCOPED=1 deleted: the code-steps line falsely claims a receipt reuse)
    P9-export-dropped             NOT-APPLIED (the export is removed at this head: no reader needs it, every one is in prepr's own shell)
    P9b-export-readded            KILLED  (the driver's added inverse: re-adding the export fails the child-sees-unset arms)
    NULL-comment-only             SURVIVED (the control)

Driver run against 0b407606 (the closures re-record after it changes no driven file). The PR's base seven (M1-M7 = P1-P6, G1) stay killed.

`G3` was no fail-open, only an unpinned fail-closed property the skip rests on; `P9` was a real leak. `_rank`'s `except` already returned `None` (fail-closed) at a81d7f15, but nothing exercised the raise -- the fail-closed self-test arm reached it only through a `fetch=True` path that returns before the `try` body raises; the new arm stubs `show_roster` to raise and asserts `is_hotfix` is False, `derived_priority` 0 and `--hotfix` prints `0`. `P9`'s `export` leaked the roster-chosen skip to any child process (the self-test step, a merged-tree command); the defaults are now set unexported, and a new arm checks a child sees both unset.

`mutant_run.py --diff <merge-base>...HEAD --cmd '<self-test>'` over the added Python reports survivors only in the inline self-test region (STMT_DEL of a `check(...)` call, CONST_SWAP of a redundant `fetch=`/`ref=` keyword in a fixture call) and in `_rank`'s pre-existing `None`-return guards (lines the base PR added, unchanged here); a mutation of an assertion line cannot be killed by the suite asserting it, and the `_rank` guards are equivalent under the fixtures (every fixture resolves a roster ref and a listed group). The behaviour-bearing seam is pinned by the reviewer-driver kills above and the self-test counts below; the residual mutant_run survivors are test-region and equivalent, answered here, not a behavioural gap.

## Null control

The carry's null control is the non-hotfix branch: the `(hotfix) null control: a non-hotfix branch prints nothing and sets neither skip` arm passes, and the full prepr is unchanged for it. End to end, the `(hotfix) null control: the same fixture's lease priority is 2 and 1` arm shows the fixture's gate priorities are 2 (hotfix) and 1 (outside), so `hotfix_class`'s 1 / 0 is the class, not the priority. For the fail-closed fix, the null is the unbroken read, restored: `(True, 2, '1')` for the hotfix branch after `show_roster` is restored.

## Figures

- `python3 tools/pr/gate_priority.py --self-test`: 21 checks, 0 failed at this head (17 at a81d7f15: +4 arms -- the `--hotfix` CLI, the raising read, the restore null, the fetched default).
- `bash tools/pr/prepr.sh --self-test`: 550 passed, 0 failed at this head (548 at a81d7f15, 542 at the merge base 7eadd75f).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED; no budget file touched.
- `python3 tools/audit/seat/bare_array.py --check`: clean.
- `python3 tools/pr/ci_predict.py`: no closures, fast, governance or instrument red predicted.
- `git merge-tree --write-tree origin/main HEAD`: one tree, no conflict.

## Red checks

none

## Forward-carry

none

## Friction

none
