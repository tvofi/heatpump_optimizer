R11-PRE-TOOLCHAIN-PIN part 1 of 2 as dispatched: carries 0-4 of the group, at the approved design `a37706d599ca28414378bda7813068b79fd716d6` (`design-verdict/R11-PRE-TOOLCHAIN-PIN` 72c0fda351, `Design review: approve`). Two instruments change. `tools/audit/seat/open_driver.py` stops charging the branch for the environment's refusal: a `REFUSE: STALE CHECKOUT <head>` result records the tools checkout HEAD it was refused at, sets no backoff and counts toward no stuck, and is retried on the first pass after that HEAD changes (carry 2, P627); `open_driver.py retry <topic> [<sha>]` replaces the hand edit of `fails.json` (carry 1, P678). `tools/pr/cancel_superseded.py` gains a `main` arm, the one sanctioned path for cancelling superseded main push runs: never the newest run of a workflow, never a cancel that leaves more than three consecutive main runs with no concluded one (carry 3, P658). Carries 0 and 4 re-measure as already answered at the base and change no file.

Scope decision, and why: the dispatch line names carries 0-4 and the design's own p1 (the toolchain instrument, the section 3 freshness sites, the main mirror, the prune guard, the beat row) is a different cut. This diff is the dispatch's cut. None of the design's p1 instrument is in it, and carry 2 is built on the design's fallback reading, which holds under the pin too: the HEAD recorded is the driver's own checkout, the one `pr_tools_fresh` judges (design df3267eba7 section 6, "1, 2: p1, as written"), so the rule does not change when that function is repointed at the stable ref.

Alternatives for carry 2 that lost: a dedicated exit status from `pr_tools_fresh` (changes `pr_refuse`'s one exit path, which `cloud_relay.sh` and `update_pr.sh` also read; the refusal line already carries the HEAD, so the status would add a second channel for one fact); recording `World.tools_head()` at reap time instead of the line's HEAD (a checkout rotated between the refusal and the reap would be recorded as the refused one and the retry lost, the 2026-11-11 shape). For carry 3: one listing of every main run grouped by workflow (a superseded run of a quiet workflow falls outside the newest page, so its row would be guessed); counting an active neighbour as part of a row (refuses the cancels the carry's null control keeps).

## Head

b5df34db8aac1a0bd185cf7f4aa5bce831bf85b0 on origin/main 31117b1029de63938d949e78dcbcd8f9451e5e33 (Sun Nov 15 2026 23:03Z).

## Mutation proof

Predicates mutated, never tails. Each mutant is one exact one-occurrence replacement in a copy; the copy's own self-test must fail.

- `python3 dev/audit/harnesses/r10_open_driver_mutants.py`: the nine plants this diff adds are each `verdict=killed`: `M-stale-env` (every rc 1 read as the environment's: carry 2 (iv), turns the (iii) null-control row red), `M-stale-key` (the HEAD key dropped: turns the (i) rows red), `M-stale-count`, `M-stale-unread`, `M-stale-notice`, `M-retry-nowrite` (the verb writes nothing: carry 1 (iii), turns the (i) row red), `M-retry-refuse`, `M-retry-namesake`, `M-unlisted`. The harness ends `RESULT survived=0`.
- `python3 dev/audit/harnesses/r11_main_cancel_mutants.py`: `M-newest` (the newest-run guard dropped) and `M-row` (the row bound dropped) are the carry's two guards; with `M-bound`, `M-older-side`, `M-newer-side`, `M-planned`, `M-full`, `M-verdicts`, `M-event`, `M-branch`, `M-dry` each is `verdict=killed`, ending `RESULT survived=0`.
- Failing test first: at the merge base with only the new self-test rows applied, `python3 -I tools/audit/seat/open_driver.py --self-test` printed five `FAIL stale ...` rows and then stopped on `AttributeError: module 'open_driver' has no attribute 'stale_head'`; `python3 tools/pr/cancel_superseded.py --self-test` stopped on `NameError: name 'main_plan' is not defined`.

## Null control

- Carry 2 (iii): a merge-conflict rc 1 still backs off 1800 s and counts toward `MAX_TRIES`, whatever the tools HEAD does (row `stale (iii) null`). A `NOTICE: STALE CHECKOUT` line under `HPO_ALLOW_STALE_TOOLS` and the phrase quoted inside another refusal are the branch's failure. The classifier is driven over 480 generated spellings (3 names x 4 levels x 4 phrases x 5 heads x 2 tails) and agrees with `pr_refuse`'s own line on every one.
- Carry 1 (ii): without the verb, the same pass inside the backoff window skips the topic as `backoff`. (iv): a topic with no entry is refused and `fails.json` is byte-identical.
- Carry 3: an older superseded main run with a concluded run inside its last three is cancelled; `run` and `sweep` still select no main run on the same fixture.
- `M0` of both harnesses, nothing mutated, prints `failed=0 verdict=null-ok`.

## Figures

- `python3 -I tools/audit/seat/open_driver.py --self-test`: `open_driver self-test: 114 checks, 0 failed`.
- `python3 tools/pr/cancel_superseded.py --self-test`: `cancel_superseded self-test: 76 checks, 0 failed`.
- `python3 dev/audit/harnesses/r10_open_driver_mutants.py`: `RESULT mutants=33`, `RESULT survived=0`.
- `python3 dev/audit/harnesses/r11_main_cancel_mutants.py`: `RESULT mutants=11`, `RESULT survived=0`.
- Carry 0, re-measured at 31117b1029: `python3 dev/audit/harnesses/r10_open_driver_mutants.py` exited 0 with `RESULT mutants=24`, `RESULT survived=0` and no `ABORT` line; the four plants the carry names resolve in `topic_grammar.py` through the harness's `GRAMMAR` argument.
- Carry 4, re-measured at 31117b1029 from the recorded listing of run 43602217369 that `tests/ci_ratchet.py`'s self-test holds, never from live main: `python3 -I tests/ci_ratchet.py --self-test` prints `ci-ratchet self-test: 72 checks, 0 failed`; with `_cut_at_prelude` forced false it fails `a run cancelled at its prelude, its every tests job skipped, is not in the window (run 43602217369)`; the four `null: a CI push run with no completed tests job ... still refuses` rows are the carry's null control and pass. The advisory half: `python3 -I tools/ci/gate.py --self-test` prints `gate self-test: 106 checks, 0 failed`; with `ci-ratchet` added to `PUSH_ONLY` it fails `B3: push owes coverage-ratchet and no longer ci-ratchet (report-only)` and `a push with ci-ratchet red passes and reports it in the one machinery line`.
- Carry 3's exit measure is `tools/audit/seat/scorecard.py` line `C` (the longest row of cancelled main runs in the last 50). It moves only once the arm is in use after the merge; no baseline was read in this seat, which has no `gh` binary for the scorecard's inputs.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/pr/ci_predict.py --apply-inert`: `CI PREDICT: no closures, fast, governance or instrument red predicted against 31117b1029de`, after it wrote the one `inert_reads` entry for the new harness.
- Gate scope: `python3 tests/closure.py select --diff 31117b1029 --workdir <dir>` prints `MODE: SCOPED -- 1 script(s) run` naming `tests/entities.py`; `PYTHONPATH=tests/hastub python3 tests/entities.py` exits 0.

<!-- figure-block: scope-line mb=31117b1029de63938d949e78dcbcd8f9451e5e33 head=b5df34db8aac1a0bd185cf7f4aa5bce831bf85b0 -->
~~~text
MODE: SCOPED -- 1 script(s) run, 32 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none

## Forward-carry

- Carry 0: dismissed, no ABORT at the base (Figures). Carry: dismissed: the harness exits 0 with survived=0 at 31117b1029
- Carry 1: built (`open_driver.py retry`, acceptance (i)-(iv) in `open_driver_selftest.py`). Carry: R11-PRE-TOOLCHAIN-PIN
- Carry 2: built (acceptance (i)-(v) in `open_driver_selftest.py`; the beat's freshness arm is untouched). Carry: R11-PRE-TOOLCHAIN-PIN
- Carry 3: built (`cancel_superseded.py main`). Carry: R11-PRE-TOOLCHAIN-PIN
- Carry 4: dismissed, both halves are on main at the base: `_cut_at_prelude` (bc85e0900a) and gate.py's push report-only set (`#3500`). Carry: dismissed: built at 31117b1029, measured in Figures
- Design note dr10's aside (2026-11-14: the opener printed no SKIP, NEEDS-TITLE or START line for r10-arch-docs-delta), measured: the new `listing:` row of `open_driver_selftest.py` drives one topic through each branch of a pass and each draws exactly one line; `M-unlisted` turns it red. A `handoff-no-pr` board line cannot go unlisted, so that topic had no such line on the board the driver read. Carry: dismissed: measured, no fixture handoff ref goes unlisted
- The design's p1 other than carries 1 and 2 (the toolchain instrument with promote and behind, the section 3 freshness sites, the `merge_train.py` main mirror with notes dr14-dr18, the prune guard, the beat row) and its p2 are in no part the dispatch has cut: part 2 as dispatched is carries 5-8. The next part's payload must name them, or the group closes with its brief unbuilt. `tools/pr/cancel_superseded.py main` is run by hand; the design names no beat row for it. Carry: R11-PRE-TOOLCHAIN-PIN (item tp1)

## Friction

- fixer.md: contradiction: the dispatch's generated part line cuts a group by carry index ("Part 1 of 2: build carries 0-4") while the approved design cuts it by seam (p1 = toolchain instrument, sites, mirror, carries 1, 2 and 7), and neither names the other; this seat took the dispatch's cut. Carry: R11-PRE-TOOLCHAIN-PIN (item tp1)
