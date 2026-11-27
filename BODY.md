R11-OWNER-AUTO-CARRY (owner order, tvofi 2026-11-27). A merge verdict whose PR head then moves by a bot commit or a clean main merge used to lose its holder. `bus.sh confirm` graded card C8 at the verdict's head, so a red that the moved-to commit cured (the mutation lane before its `ci: pin killed mutants` pin) refused the post. `verdict/<pr>` then sat ahead of the newest posted comment, and `merge_train.py add` refused with "the newest posted verdict ... is not verdict/<n>'s tip". This was observed on #3925: verdict at 129cc121, head d50ab75e.

The carry is applied by the instrument that owns C8: `post_verdict` in `tools/audit/seat/bus.sh`. A new `carry_head` reads the PR's live head (`gh api repos/<repo>/pulls/<n> --jq .head.sha`) and asks `review_carry.py <verdict head> <live head> --verdict-only`. Only CARRY (rc 0) makes C8 grade the live head. FRESH-REVIEW, an undecidable range, an unreadable head or an unmoved head all grade the verdict's head, as before. A head still red takes no merge verdict: a carried head that is RED is refused and named (`whose head <live>, carried to, has a concluded red`). The merge path needs no second change. The posted verdict is now the bus tip, and `merge_train.py add`'s `admit_add` already accepts verdict != head when `app_approve.sh --carry` says `CARRY: yes`, which is the same predicate `review_carry.py` asks. FRESH-REVIEW keeps today's route: a delta reviewer through `bus.sh dispatch --reviewed-head`.

The record: each carried post prints `BUS carried <pr> <verdict> -> <head>` and appends `<pr> <verdict> <head> <utc>` to `$HPO_BUS_STATE/carried`. `orchestrator_tick.py verdict_levels` prints `CARRIED: #N <head8> from <verdict8>` (unflagged) while the PR's newest carry record names its current head. The beat reads the tick log, so the holder shows on the board.

Alternatives that lost:
- Carrying in `merge_train.py add`. It already carries a verdict to the head. What refuses is the post, so a train-side change leaves C8 refusing and the comment unposted.
- Re-posting the verdict at the new head. That mints a verdict no reviewer issued, and it moves the bus tip again.

No policy file changes. `fix-review.md`'s "`bus.sh post` refuses `merge` at a red (C8)" still holds of the head that merges.

## Head

55e2f0d8bbb5c93996a458cbcde3c6b66264528a on base ef797d794017c98f7fb2d8a168d7de63d435ef3b (origin/main at the cut).

Disclosed self-correction: the branch's first commit (72d1774e) carried the `str(n) in carried` tick mutant. The mutation run's restore copied the first mutant back in place of the original. `tests/entities.py`'s `orchestrator_tick.py --self-test passes` check caught it (2 failed). 55e2f0d8 restores the predicate. `bus.sh` is byte-identical between the two commits (`git diff 72d1774e 55e2f0d8 -- tools/audit/seat/bus.sh` is empty), so its self-test figure holds. The tick self-test, `tests/entities.py` and the architecture score were re-taken at 55e2f0d8.

## Mutation proof

The mutants were run on copies of the head tree with `bash tools/audit/seat/bus.sh --self-test`:
- `carry_head`'s `if [ "$rc" = 0 ]` (`# mut:autocarry`) replaced by `if false` (never carry): 2 of 249 failed, `automatic carry: a carried head still red takes no merge verdict ...` and `automatic carry: a mutation-pin commit carries the verdict ...`.
- `rc=$?` after `review_carry.py` replaced by `rc=0` (always carry): 4 of 249 failed, the two above plus `null control (automatic carry): a commit editing the PR's own file is FRESH-REVIEW ...` and `null control (automatic carry): a main merge whose conflict in reviewed code is resolved by hand is FRESH-REVIEW ...`.

The mutants were run in place with `python3 tools/audit/seat/orchestrator_tick.py --self-test`, then the file was restored:
- `# mut:carriedline` predicate replaced by `str(n) in carried` (any record): 2 of 395 failed, `automatic carry line: a carry recorded at the current head prints CARRIED ...` and `automatic carry line: null control: a carry recorded at an older head prints none`.
- The predicate replaced by `False`: 1 of 395 failed, `automatic carry line: a carry recorded at the current head prints CARRIED ...`.

## Null control

The self-test fixtures run the real `review_carry.py` (no stub) in the throwaway repository, with the verdict at h1 RED:
- `acpin`, a `github-actions[bot]` `ci: pin killed mutants` commit inside `tests/mutation_ledger`: CARRY, so C8 is graded at `acpin` (GREEN). It posts, prints `BUS carried`, and records the carry.
- `acown`, a commit editing the PR's own file: FRESH-REVIEW. It is graded at h1 and refused, and nothing is recorded.
- `acconf`, a main merge whose add/add conflict in the PR's file is resolved by hand: FRESH-REVIEW. It is graded at h1 and refused, and nothing is recorded.
- `acpin` with `acpin` itself RED: refused, naming the carried head, and nothing is recorded.

The unmodified tree's existing C8 arms (`card C8: a merge verdict at a head classify calls RED is refused ...`) pass unchanged. Their gh stub prints no sha, so they grade the verdict head (the unreadable-head arm).

The finder's instance, re-run on the real range: `python3 -I tools/audit/seat/review_carry.py 129cc1217e8cae19b4c43d821e535d3018727d34 d50ab75eebbf85dd1a28a0032c2b7629d0ff6d3f` prints `review_carry: CARRY` (1 branch-only commit, `ci: pin killed mutants` by `github-actions[bot]`). At the base, `post_verdict` classifies 129cc121. At the head, `carry_head` selects d50ab75e for C8. The live `gh`/`classify` end was not run here: this seat has no `gh` binary.

## Figures

- `bash tools/audit/seat/bus.sh --self-test`: 249 checks, 0 failed at the head.
- `python3 tools/audit/seat/orchestrator_tick.py --self-test`: 395 checks, 0 failed at the head.
- `python3 tests/closure.py select --diff ef797d794017c98f7fb2d8a168d7de63d435ef3b`: `MODE: SCOPED -- 2 script(s) run`, which are `tests/doc_claims.py` and `tests/entities.py`, both run green with `PYTHONPATH=tests/hastub`.
- `python3 tools/audit/archscore/score.py --diff ef797d794017c98f7fb2d8a168d7de63d435ef3b HEAD`: `Architecture score: dS +0.0000 NULL`.

## Red checks

none

## Forward-carry

none

## Friction

none
