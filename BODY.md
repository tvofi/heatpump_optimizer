Carry 21 repair, round 4: the three survivors of the reviews at b53bbf16 and 2a1a7de0 (verdicts `verdict/3547` 37efc2e08 and 51888e088) are each killed by a self-test arm: P13 by a run of prepr's main flow itself on a hotfix branch, P12 by an `hs` row passing a caller's literal `PREPR_SKIP_CODE=hotfix`, and G6 by a `gate_priority.py --hotfix` arm whose `--ref` roster differs from the local roster ref. No production line changes in this round; the hotfix-scope decision is the one at a81d7f15.

## Review scope

The generated scope-line block is left out of this body: update_pr.sh verifies it against its own merge head, which no body can name in advance (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH); the gate's MODE line at this head is in `## Figures`.

`git diff 2a1a7de05b0c080029817dd4208864c5ef7e9f6a e9ba58d303b8651777a2e9915ac81f4bd8f7f681`, the reviewed head to this one, is one commit and touches self-test code only:

- `tools/pr/gate_priority.py`: `_self_test`'s `cli` helper takes the roster ref, and one arm runs `main(["--hotfix", ..., "--ref", <a roster with no hotfix group>, "--no-fetch"])` for the branch the local roster ref classes a hotfix, expecting `0`; its control in the same check, `is_hotfix(..., ref=None, fetch=False)`, reads the local ref as `True`. Kills G6.
- `tools/pr/prepr.sh` `--self-test`: one `hs` row with `PREPR_SKIP_CODE=hotfix PREPR_SKIP_CLOSURES=x` exported, expecting the receipt line (kills P12); and `rhot`, which runs the whole main flow (`bash tools/pr/prepr.sh <body>`) in the throwaway checkout on branch `fix/r10-hotfix-st` with `tools/pr/gate_priority.py` stubbed there (an `info/exclude`d fixture file at the path `hotfix_class` runs, since prepr `cd`s to the checkout's top level), and reads the `hotfix scope` and `code steps` lines it prints. Classed 1 with no caller skips, the flow prints `ok hotfix scope: ...` and `ok code steps: hotfix scope` (kills P13, whose inline line would print `reused from the receipt at hotfix`); its null control, the same branch with the caller's `PREPR_SKIP_CODE=<sha>` and `PREPR_SKIP_CLOSURES=1`, prints no scope line and `ok code steps: reused from the receipt at 0123456789ab`.

The whole PR, against its merge base 7aac3e7c0, is unchanged from the reviewed heads but for these arms: `tools/pr/prepr.sh`'s `hotfix_class`, `hotfix_scope` and `code_steps_line` and the main flow's two calls to them; `tools/pr/gate_priority.py`'s `_rank`, `is_hotfix` and `--hotfix` CLI; and `dev/programme/delivery/3547.md`.

P9 decision (round 3, kept): the two roster-chosen skip defaults are set unexported. Every reader of the two names is in prepr's own shell: `git grep -n 'PREPR_SKIP_CODE\|PREPR_SKIP_CLOSURES' -- tools tests ':!tools/pr/prepr.sh'` prints only callers setting or logging the value on its way into prepr (`open_pr.sh`, `update_pr.sh`, `handoff_push.sh`, `remerge_main.sh`, `app_push.sh` and its self-test), none a process prepr starts; an exported default would leak a skip the roster chose for this run into the self-test step and any merged-tree command.

Round 1 and 2 survivors (G3, G5, G5b, P7, P8, P9) were killed at b53bbf16, as verdict 37efc2e08 records ("All six of round 1's survivors are now killed at this head"); this round adds no change to the lines they mutate.

## Head

`e9ba58d303b8651777a2e9915ac81f4bd8f7f681`

## Why the same class three times

Cause: `tools/audit/seat/mutant_run.py --diff` draws mutants from added `*.py` lines only (its `git diff ... -- "*.py"` in diff mode), so a fixer's own diff sweep never draws a site in `prepr.sh`; rounds 1 and 2 cleared the survivors the reviewer had hand-built and did not enumerate the shell predicates themselves, so the reviewer's next hand-built set found the next ones. Round 3 then reviewed an unchanged diff: the round-2 repair returned `BLOCKED` (the review packet's carries, wip b88ef35de) and the only move was the merge-main commit 2a1a7de0. Process state (c): the instrument ran, and its draw excludes the language the seam is written in. What this round does instead: a spec-mode run (`mutant_run.py --spec`, which mutates any file) over every added executable line of the seam in `prepr.sh` (`hotfix_class`, `hotfix_scope`, `code_steps_line` and the two main-flow lines), enumerated in `## Mutation proof`, plus the diff-mode run over the `.py` side. Not built here: shell drawing in `mutant_run.py --diff`, which belongs to that instrument's owner, not to a Carry 21 repair.

## Mutation proof

Shell side, `python3 tools/audit/seat/mutant_run.py --spec <spec> --cmd 'bash tools/pr/prepr.sh --self-test' --in-place` at e9ba58d303b8, the spec one entry per added executable line of the seam (the reviewer's P12 and P13 verbatim, from `evidence/P13.diff` and the round-2 verdict):

    NULL (no edit, each of 5 runs)                SURVIVED
    P12-codesteps-drops-scoped-test      KILLED    code_steps_line tests the value alone, not HOTFIX_SCOPED (reviewer)
    P13-main-uses-inline-receipt-line    KILLED    main flow prints the pre-PR inline receipt line (reviewer, evidence/P13.diff)
    P14-codesteps-drops-value-test       KILLED    code_steps_line tests HOTFIX_SCOPED alone, not the value
    P15-scope-flag-dropped               KILLED    hotfix_scope never sets HOTFIX_SCOPED
    P16-early-return-or                  KILLED    the both-set early return fires when either is set
    P17-class-compares-2                 KILLED    hotfix_scope compares the class to 2
    P18-main-scope-call-dropped          KILLED    the main flow never calls hotfix_scope
    P19-classifier-drops-hotfix-flag     KILLED    hotfix_class asks gate_priority for the priority, not --hotfix
    P20-code-default-dropped             KILLED    the PREPR_SKIP_CODE default is not set
    P21-closures-default-dropped         KILLED    the PREPR_SKIP_CLOSURES default is not set
    P22-receipt-branch-dropped           KILLED    code_steps_line never prints the receipt line

All 11 KILLED; 0 SURVIVED besides the NULL. The 11 were run as five spec files in separate detached worktrees at the head, in parallel.

Python side, `python3 tools/audit/seat/mutant_run.py --spec <G6> --cmd 'python3 tools/pr/gate_priority.py --self-test' --in-place`: `SURVIVED NULL`, `KILLED G6-cli-ignores-ref` (the reviewer's `evidence/G6.diff`). Before this round's arm the same mutant reads `gate_priority self-test: 22 checks, 1 failed` only with the arm present; without it, 21 checks, 0 failed (the verdict's `ev/G6.log`).

`python3 tools/audit/seat/mutant_run.py --diff $(git merge-base origin/main HEAD)...HEAD --cmd 'python3 tools/pr/gate_priority.py --self-test' --in-place` (merge base 7aac3e7c0) printed 16 SURVIVED lines and no other non-KILLED line; every one is answered:

- `gate_priority.py:112 RETURN_DEL` (`_rank`'s `if roster_ref is None: return None`): equivalent. Falling through calls `roster_lib.show_roster(repo, None)`, whose `git show None:<path>` fails and raises `RosterNotFound`, which `_rank`'s `except` returns as `None`.
- `:115 GUARD_OFF` and `:116 RETURN_DEL` (`if group is None: return None`): equivalent. `roster_lib.dispatch_rank(roster, None, critical)` returns `RANK_OTHER` for a falsy group, and both callers read `RANK_OTHER` and `None` alike: `derived_priority` maps each to `PRIORITY_NORMAL`, `is_hotfix` compares to `RANK_HOTFIX`.
- `:122 RETURN_DEL` (the `except` arm's `return None`): equivalent; a Python function ending without `return` returns `None`.
- `:264, :268, :281, :287, :302, :309, :311, :313 STMT_DEL` and `:265, :269, :291, :296 CONST_SWAP`: lines of `_self_test` itself (deleting a `check(...)` call, or flipping `fetch` where `ref` is passed and `fetch` is unread, or inside a check's diagnostic `got` argument). A mutant of the test removes or weakens a check; no command can kill it by running that test, and it changes no production behaviour.

`tests/mutation_ledger/survivor_triage/` holds one directory per `custom_components/` module and none for `tools/`, so these answers live here.

## Null control

Every mutant run's automatic NULL (the unedited tree) survived first, so the self-tests do not fail on an unmutated checkout. P13's arm has its own null in the same run: the hotfix branch with the caller's skips set prints the receipt line and no scope line. G6's arm checks in the same assertion that the local roster ref does class the branch a hotfix, so the `0` it reads at `--ref` is the ref's answer and not a branch that is never a hotfix. P12's row sits beside the existing `hs 1` row with no caller value, which prints `code steps=hotfix scope`.

## Carry status

This part builds carry 21 only (the diff above): Carry 21 is built here, in `tools/pr/prepr.sh`'s `hotfix_scope` and `tools/pr/gate_priority.py --hotfix`. Every other dispatched carry's disposition is the one its own text carries in the brief; none is built here:

- Carry 0: dismissed: moved to round 11; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only
- Carry 1: dismissed: moved to round 11; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only
- Carry 2: dismissed: moved to round 11; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only
- Carry 3: dismissed: moved to round 11; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only
- Carry 4: implemented at 6e100ef6980216a81eaa0438bdc215d62b19271f; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only
- Carry 5: moved: R11-INTAKE-R10-RESIDUE; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only
- Carry 6: dismissed in pull request 3479; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only
- Carry 7: dismissed: moved to round 11; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only
- Carry 8: dismissed: superseded by carries 14 to 17; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only
- Carry 9: dismissed: superseded by carries 14 to 17; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only
- Carry 10: dismissed: superseded by carries 14 to 17; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only
- Carry 11: dismissed: superseded by carries 14 to 17; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only
- Carry 12: dismissed: duplicate of carry 20; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only
- Carry 13: dismissed: moved to round 11; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only
- Carry 14: moved: R11-INTAKE-R10-RESIDUE; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only
- Carry 15: moved: R11-INTAKE-R10-RESIDUE; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only
- Carry 16: moved: R11-INTAKE-R10-RESIDUE; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only
- Carry 17: moved: R11-INTAKE-R10-RESIDUE; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only
- Carry 18: dismissed: moved to round 11; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only
- Carry 19: dismissed: roster instruction done; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only
- Carry 20: moved: R11-INTAKE-R10-RESIDUE; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only
- Carry 22: moved: R10-CARRY-AUDIT-P5; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only
- Carry 23: moved: R10-CARRY-AUDIT-P5; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only
- Carry 24: moved: R10-PROCESS-SLIM; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only
- Carry 25: moved: R11-INTAKE-R10-RESIDUE; not built in this part. Carry: dismissed: its disposition is the one its brief text records; this part builds carry 21 only

## Figures

Measured at e9ba58d303b8 over origin/main 50373173d, date -u 2026-11-14 00:03 UTC.

- `bash tools/pr/prepr.sh --self-test`: 553 passed, 0 failed (550 at 2a1a7de0 per the verdict's `ev/P13.log`; the three added rows are the difference).
- `python3 tools/pr/gate_priority.py --self-test`: 22 checks, 0 failed (21 at 2a1a7de0).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED; no budget file touched.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 0 script(s) run, 33 scoped out`.
- `git merge-tree --write-tree origin/main HEAD` at origin/main 50373173d: exit 0, no conflict, so no merge of main in this round.
- `python3 tools/pr/gate_priority.py --hotfix --branch fix/r10-prepr-residue-p2`: 0 (not a hotfix group's branch).

## Red checks

`instrument-self-tests`, prepr.sh `--self-test`, red at becbe652 (round 2) under `update_pr.sh`, which exports `PREPR_SKIP_CLOSURES=1`: assigning an empty value to an exported name keeps it exported, so a `bash -c` row saw it (549 passed, 1 failed; with `PREPR_SKIP_CODE=1` exported, 544 passed, 6 failed). Process state (c): the self-test ran and passed, and assumed an unexported caller. Cheaper detector: the same self-test run once with `PREPR_SKIP_CLOSURES=1` exported before the handoff, about 9 minutes of one background run per handoff touching prepr.sh, against one red update cycle; the entry scrub makes the exported run equal the plain one, so the detector is built into the self-test and no extra run is owed.

## Forward-carry

none

## Friction

none
