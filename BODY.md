D13-s2-01 (#2225, class N-gate-yield) found that `root-cause-unanswered` blocked 37 of the 124 fix-review verdicts in `v6.7.16..17f1c55f`. That is more than any engineering class (`harness` blocked 23). The judge weakened the finding to hygiene: a share of blocks is a cost, not a defect. What the class lacked was a measurement. One word mixes two different costs, so no D13 round can price it. R9-RCA-1985 measured that mixture.
- A red that a detector cheaper than the gate could have shown before the handoff. That is a process yield.
- A red whose cheapest detector is the gate that went red. That block costs a review round for a missing "none exists" line.

The roster brief asks for the split and forbids loosening the gate. This change splits the class by `defect-root-cause.md`'s own question.

What changes, in `.claude/workflows/web-fix-wave.js`:
- `VERDICT_CLASSES` teaches two more words, `root-cause-detectable` and `root-cause-unrecorded`.
- `ROOT_CAUSE_CLASSES` carries all three root-cause words, so each arm blocks and dispatches the root-cause seat exactly as the unsplit word does. The gate is not loosened.
- The reviewer prompt says when to use each word. The unsplit `root-cause-unanswered` stays taught, for a reviewer who cannot tell and for `fix-review.md` step 11, which still teaches it. Its count is the residue a D13 round reads.
- No new parser. `policy_lint.mjs` `blockClasses()` extracts the same literal, so the `--stats` histogram, the D13 harness and the D14 enumerator key each word as its own row with no code change.

Alternatives considered:
- A cheaper-detector registry keyed by check name, read from the verdict's `<check> went red`. Rejected: it is a judgement table (typing's local ruler is optional, closures cannot be derived off Linux, budget-raise-gate is predicted by prepr). It would go stale with every new check, and it would decide in code what `defect-root-cause.md` asks a person to decide.
- A `detector` field on the root-cause seat's result. Rejected: no script reads `Root cause:` comments, so the split would land where no D13 instrument looks.
- Teaching the split in `fix-review.md` step 11 as well. Not done here: it is policy at zero headroom (140/140 lines, 2451/2451 tokens under `policy_lint --budgets`), outside this group's files, and owner-approved. Carried below.

Part of #201.

Closes #2225.

## Head

`21a4e4a1ded4b117d045ebfac94708ff569a156d`, cut from `origin/main` `5603ee319d73cd464d38a3cbbad90d83d4cf4cdf`. There are two commits: the failing test (`2a0a0f09d`), then the fix.

## Mutation proof

Each mutation was applied to the head, then `node tools/policy/check-wave-script.mjs` was run, then the file was restored with `git checkout`.
- Delete the line `'root-cause-detectable', 'root-cause-unrecorded',` from `VERDICT_CLASSES`. Result: `180 passed, 4 failed`. All four `group 11b` checks fail: `a root-cause-detectable verdict routes as itself, blocks, and dispatches the root-cause seat rather than a repair` (class `other`, calls `repair A`), `the stats histogram keys root-cause-detectable as its own row, the same class the wave routes` (key `root-cause-detectable`, route `other`), and the same two checks for `root-cause-unrecorded`.
- Revert `ROOT_CAUSE_CLASSES` to `['root-cause-unanswered']`. Result: `182 passed, 2 failed`. Both "dispatches the root-cause seat" checks fail: the class routes as itself, but the calls show `repair A` and `re-review A`, so the gate would have sent the verdict to a repair round.
- Failing test first: at `2a0a0f09d` (the test, no fix) the same 4 checks failed, with `180 passed, 4 failed`.
- In both runs, the other failing line is `FAIL (probe, expected) threw: deliberate`. It is a planted probe that prints at every head, the merge base included. It is not counted in the totals.

## Null control

- The unmodified tree (`5603ee319`) routes both new words to `other`, which the same check shows above. The histogram key alone is not a control, because it keys an untaught word raw too. That is why the assertion requires the key to equal the wave's route.
- An invented class word still routes to `other` at the head: `group 13`'s `a blocked verdict with an untaught class word parses and routes to other` passes. Teaching two words did not open the vocabulary.
- The unsplit `root-cause-unanswered` still dispatches the root-cause seat at the head: `group 11`'s checks pass.

## Figures

The finder's harnesses, run from the finder's window payload `window.json` (sha1 `8c4de8e205f9ec8cdc2916cbe011a94a2d4156b8`, 185 PRs in `v6.7.16..17f1c55fad1b`, `api_failures` 0). Each was run in a detached worktree at `5603ee319` and in this branch's worktree at the head.
- `node dev/audit/rounds/round10/D14/sweep-N-gate-yield/enumerate.mjs window.json`. The base and the head both print `SEAM root-cause-unanswered count=37 engineering_max=23 INSTANCE` and `RESULT seams=13 instances=1 engineering_max=23`. The harness is flat at both ends, as it should be: the fix changes the vocabulary for verdicts still to be written, not the window's history.
- Companion that reads the change: the same payload plus one planted verdict for each new word (`window_planted.json`). The base prints `SEAM untaught:root-cause-detectable count=1` and `SEAM untaught:root-cause-unrecorded count=1`. The head prints `SEAM root-cause-detectable count=1` and `SEAM root-cause-unrecorded count=1`. Both print `RESULT seams=15 instances=1`.
- `HPO_PLANDATA=$(mktemp -d) node dev/audit/rounds/round10/D13/s2/blocks_friction.mjs window.json`. The base and the head both print `RESULT blocked_verdicts=124`, `RESULT block_class[root-cause-unanswered]=37` and `RESULT blocked_outside_grammar=0`. On the planted payload, the base prints `block_class[untaught:root-cause-detectable]=1` and `block_class[untaught:root-cause-unrecorded]=1`. The head prints `block_class[root-cause-detectable]=1`, `block_class[root-cause-unrecorded]=1`, `PROD verdict_row[root-cause-detectable] prs=1 entries=1` and `PROD verdict_row[root-cause-unrecorded] prs=1 entries=1`.
- `node tools/policy/check-wave-script.mjs` at the head: `184 passed, 0 failed`.
- Scoped gate: `python3 tests/closure.py select --diff 5603ee319...` printed `MODE: SCOPED -- 1 script(s) run, 32 scoped out` (`tests/entities.py`). `PYTHONPATH=tests/hastub python3 tests/entities.py` (seat venv python 3.14) printed `ALL 2318 ENTITY CHECKS PASSED` at the head. The load average was about 61 (`uptime`).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Seams: `git grep -n "root-cause-unanswered" -- .claude tools tests dev/governance` lists every reader of the word.
  - `web-fix-wave.js`: changed here.
  - `tools/policy/check-wave-script.mjs`: extended here.
  - `tools/policy/policy_lint.mjs`: reads the literal through `blockClasses()`, so it needs no change.
  - `tests/entities.py`: reads the literal, so it needs no change, and it passes.
  - `tools/policy/friction_issues.mjs` fixture: a recorded window line, a record not an instruction, left as written.
  - `tools/pr/prepr.sh`: comments that recount history, left as written.
  - `fix-review.md` and `orchestrator.md`: teach the unsplit word, which stays taught. Carried below.

## Red checks

none

## Forward-carry

Two later stages must change how they work. Both destinations are policy or a later round's brief outside this group's files, so they went to the orchestrator for the roster group R10-BRIEFS-FOLD.
- `dev/governance/roles/fix-review.md` step 11 should teach `root-cause-detectable` and `root-cause-unrecorded`. Hand-run reviews read that contract, not this prompt. Until it changes, the split is recorded only by web waves. Control: the planted companion above. Re-measure with the round's own window.
- The next D13 round's M3 bucketing and the D14 `N-gate-yield` enumerator's `ENG` set must place both new words. Otherwise `blocks_friction.mjs` puts them in its default `orchestration` bucket, which is how the planted head run above reads.

## Friction

none
