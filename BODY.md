Carry 21 repair, round 3: the six survivors of the review at a81d7f15 (verdict `review/3547` 9e69261ad2) are pinned by self-test arms on the hotfix-scope seam, prepr's `hotfix_class` through `gate_priority.py --hotfix` to the printed answer. The hotfix-scope decision is the one at a81d7f15. One behaviour changes: the two roster-chosen skip defaults are no longer exported (P9, below).

## Review scope

The generated scope-line block is left out of this body: update_pr.sh verifies it against its own merge head, which no body can name in advance (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH); the gate's MODE line at this head is in `## Figures`.

`git diff a81d7f15293fc2101f42e48ade37ef7022c35517 b53bbf1604a3720aeb665a3b51219eb54df1fe6a`, the review's head to this one: `tools/pr/gate_priority.py` (self-test arms only), `tools/pr/prepr.sh` (the arms, `code_steps_line`, the export removal, the self-test's caller-env scrub), and the `tests/closures.json` re-record of `tests/harness_headers.py` that prepr asked for (rc field 1 to 0, membership unchanged). b53bbf16 is the merge of handoff 16c571f7 into the PR head; its tree equals 16c571f7's (`git diff 16c571f7 b53bbf16` is empty).

- `tools/pr/gate_priority.py`: arms that drive `main(["--hotfix", ...])` and read its stdout per direction (hotfix group 1; outside, critical-path and unmapped 0); an arm that stubs `roster_lib.show_roster` to raise, so `_rank`'s `except` arm runs, and asserts `is_hotfix` False, `derived_priority` 0 and `--hotfix` printing `0`; its null, the restored read, `(True, 2, '1')`; and the fetched default. No change to `_rank`, `is_hotfix`, `derived_priority` or the CLI.
- `tools/pr/prepr.sh`: the hotfix-scope self-test runs the real `hotfix_class` end to end against a fixture roster (no stub); the main flow's code-steps message moves into `code_steps_line`, which the self-test drives, so a hotfix-scoped run's line names the hotfix scope and makes no receipt claim; the skip defaults are set unexported, and an arm checks a child process sees both unset; `--self-test` unsets `PREPR_SKIP_CODE`/`PREPR_SKIP_CLOSURES` at entry, so an exporting caller (`update_pr.sh`) no longer turns its rows red.

P9 decision: delete the export, not pin it. Every reader of the two names is in prepr's own shell: `git grep -n 'PREPR_SKIP_CODE\|PREPR_SKIP_CLOSURES' -- tools tests ':!tools/pr/prepr.sh'` at this head prints 12 lines, every one a caller setting or logging the value on its way into prepr (`open_pr.sh`, `update_pr.sh`, `handoff_push.sh`, `remerge_main.sh`, `app_push.sh` and its self-test) and none a process prepr starts; a reader prepr spawned would have printed there; an exported default would leak a skip the roster chose for this run into the self-test step and any merged-tree command.

## Head

`b53bbf1604a3720aeb665a3b51219eb54df1fe6a`

## Mutation proof

The reviewer's driver (`evidence/driver.py` on `review/3547`) re-run at this head, HEAD set to b53bbf16, with one added mutant P9b (the inverse of P9: re-insert `export PREPR_SKIP_CODE PREPR_SKIP_CLOSURES` after the closures default). Each mutant: a fresh detached worktree, one exact replacement asserted to match once, then the named self-test (`python3 tools/pr/gate_priority.py --self-test` for G*, `bash tools/pr/prepr.sh --self-test` for G5b and P*). KILLED is rc non-zero or a failed count above 0.

    G1-is_hotfix-eq-inverted         KILLED rc=1 failed=6
    G2-unmapped-fails-open           KILLED rc=1 failed=4
    G3-except-fails-open             KILLED rc=1 failed=1
    G4-derived-drops-top             KILLED rc=1 failed=6
    G5-cli-hotfix-inverted           KILLED rc=1 failed=3
    G5b-cli-hotfix-inverted-prepr    KILLED rc=2 failed=2
    P1-class-pred-inverted           KILLED rc=2 failed=4
    P2-code-unset-test-dropped       KILLED rc=2 failed=1
    P3-closures-unset-test-dropped   KILLED rc=2 failed=1
    P4-bothset-return-dropped        KILLED rc=2 failed=1
    P5-scope-line-dropped            KILLED rc=2 failed=3
    P6-main-call-dropped             KILLED rc=2 failed=1
    P7-HOTFIX_SCOPED-dropped         KILLED rc=2 failed=2
    P8-classifier-asks-priority      KILLED rc=2 failed=1
    P9-export-dropped                NOT-APPLIED (matches=0: the export line is deleted at this head)
    P9b-export-readded               KILLED rc=2 failed=3
    NULL-comment-only                SURVIVED rc=0 failed=0

The six survivors of the review (G3, G5, G5b, P7, P8, P9) are all killed or, for P9, gone with the line it deleted, its inverse P9b killed; P1-P6, G1, G2 and G4 stay killed; the NULL survives.

## Null control

The NULL mutant (a comment-only edit in prepr.sh) survives, so the driver does not kill on any edit. For the scope: the `(hotfix) null control: a non-hotfix branch prints nothing and sets neither skip` arm passes, so a non-hotfix topic runs the full prepr as at the merge base. End to end, the fixture's lease priorities are 2 (hotfix) and 1 (outside), and `hotfix_class` reads 1 and 0, so the arms pin the class and not the priority (P8's kill). For the fail-closed arm, the null is the unbroken read restored: `(True, 2, '1')` for the hotfix branch.

## Figures

- `python3 tools/pr/gate_priority.py --self-test`: 21 checks, 0 failed at this head (17 at a81d7f15).
- `bash tools/pr/prepr.sh --self-test`: 550 passed, 0 failed at this head (the driver's NULL-comment-only run, a comment-only tree; 548 at a81d7f15, 542 at the merge base 7eadd75f per the review's logs).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED; no budget file touched.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 1 script(s) run` (tests/entities.py, which needs `homeassistant`, absent from this cloud venv; left to CI).
- `git merge-tree --write-tree origin/main HEAD` at origin/main e23124ff6e45 (2026-11-13 UTC): exit 0, no conflict.
- `python3 tools/pr/gate_priority.py --hotfix --branch fix/r10-prepr-residue-p2`: 0 (this branch is not a hotfix group's, so its own prepr runs full).

## Red checks

`instrument-self-tests`, prepr.sh `--self-test`, red at becbe652 (round 2) under `update_pr.sh`, which exports `PREPR_SKIP_CLOSURES=1`: assigning an empty value to an exported name keeps it exported, so a `bash -c` row saw it (549 passed, 1 failed; with `PREPR_SKIP_CODE=1` exported, 544 passed, 6 failed). Process state (c): the self-test ran and passed, and assumed an unexported caller. Cheaper detector: the same self-test run once with `PREPR_SKIP_CLOSURES=1` exported before the handoff, about 9 minutes of one background run per handoff touching prepr.sh, against one red update cycle; the entry scrub makes the exported run equal the plain one, so the detector is built into the self-test and no extra run is owed.

## Forward-carry

none

## Friction

none
