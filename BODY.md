R10-STAMP-ROUND-MAJOR. Owner directive (tvofi, 2026-10-29, verbatim): "I am also changing the versioning, each full audit round means a new major version, and it should match the round number on closeout, so the programme closeout release will be v10.0.0".

- **Decision 0016** (`dev/governance/decisions/0016-a-major-version-is-a-closed-audit-round.md`) records the rule, the owner's words, and how `stamp.py` enforces it. Policy, merged under the mandate in force with scope all (#201 comment 6329234399).
- **`tools/release/stamp.py --round-close N`** stamps N.0.0 through the new pure `next_version`. It refuses an N that is not above the current major, an N that differs from the newest roster's round (read through `roster_lib.roster_path`/`roster_round`; no roster refuses too), and an N given beside `--bump`. `--bump major` stays a parseable choice and refuses with a pointer to `--round-close`. `bump()` loses its major arm, so no caller can skip `next_version`. The version is decided before the fetch, so a flag-only refusal costs no network or gate read; rule 1 then proves the checkout it read is origin/main.
- **Docs:** the `stamp.py` docstring (usage, the rule, rule 3) and `--help`. `orchestrator.md` names no bump kind, so it does not describe versioning, and its token cap has zero headroom at the merge base (`policy_lint.mjs --budgets`: 4251 of 4251), so it is unchanged. `CLAUDE.md` rule 4 does not state a bump rule, so it is unchanged. No instrument note for `stamp.py` exists in the tree (`tools/release/` holds only `stamp.py`, and `INSTRUMENTS.md` does not name it), so there was none to update.
- **In-tree mutant driver** `tools/audit/seat/r10_stamp_round_mutants.py`, its self-test wired into `governance.yml`'s instrument-self-tests beside its siblings. Classified as an INERT READ of `tests/entities.py` by `ci_predict.py --apply-inert`.
- Removed a redundant function-local `import tempfile` inside `self_test()`. It shadowed the module import, so the new arms raised `UnboundLocalError` when they used it earlier in the function.

Alternatives considered (fixer step 17): (a) a refusal in `main()` alone, with `bump()` still returning N+1.0.0 for major. Rejected: any other caller of `bump` would skip the rule, and the refusal would not be drivable without `main`. (b) A separate `roster_round` check in `main`. Rejected: one pure function owning every refusal is what the self-test drives, and `main` only wires it.

**The closeout stamp:** The round-10 closeout stamp must run `stamp.py --round-close 10`, and this diff itself makes that the only way: `web-stamp.js` passes `--bump ${bump}` through, and `bump: 'major'` now refuses with `use --round-close <round>, not --bump major`. Decision 0016 states the rule.

VERSION, the manifest version and the RELEASE_NOTES headings are untouched.

**Seat notes for the orchestrator** (unrouted, since a friction line needs a roster destination this seat cannot write): the brief names `tools/audit/prepr.sh`, but the script is `tools/pr/prepr.sh`. The brief also says the toolchain is on PATH, but this seat's Bash did not read `/etc/profile.d/hpo-toolchain.sh` (as `cloud-setup.sh`'s header warns), so `python3` was 3.11 without `voluptuous` until that file was sourced.

## Head

e1913fbfca2dab4bcb5fd61ca7a576c2964f9297, forked from origin/main e5ddba1fad5e6eccfeceaeaaa249bc459963405b.

## Mutation proof

Failing test first: with the arms added and no implementation, `python3 tools/release/stamp.py --self-test` died with `NameError: name 'next_version' is not defined`.

`python3 -I tools/audit/seat/r10_stamp_round_mutants.py` runs one plant per predicate. Each plant is applied, `stamp.py --self-test` runs, and the file is restored byte for byte:

- R1 (N.1.0 instead of N.0.0): rc=1, `FAIL round close: 7.1.0 closing round 10 stamps 10.0.0`, `FAIL round close: a round not above the current major refuses`
- R2 (`<=` to `<`): rc=1, `FAIL round close: a round not above the current major refuses`
- R3 (roster round never compared): rc=1, `FAIL round close: a round the roster disagrees with refuses`, `FAIL round close: a roster that cannot be read refuses, never defaults`
- R4 (`--round-close` beside `--bump` let through): rc=1, `FAIL round close: combined with --bump refuses`
- R5 (`--bump major` let through): rc=1, `FAIL bump major refuses, naming --round-close`
- R6 (`main` drops `--round-close`): rc=1, `FAIL round close: main takes the version from next_version, the round from the roster`

`plants: 6, without a FAIL line: none`. A first sweep found a vacuous branch: a separate `roster_round is None` check survived its plant, because `!=` already refuses `None`. That branch was folded into the disagreement predicate, which R3 now kills on both arms. R5 first died by traceback (`ValueError: major`), not by a FAIL line, so the arm now catches the error and names itself.

## Null control

`python3 -I tools/audit/seat/r10_stamp_round_mutants.py --null e5ddba1fad5e6eccfeceaeaaa249bc459963405b` printed `RESULT mutant=null rc=0 fails=0` (the self-test with no plant) and `RESULT null grid=720 differ=0`. That is every patch and minor bump over 12x5x6 versions, read from the base's `bump()` and from the head's `next_version`, identical. The driver's self-test plants one altered row and asserts the comparison counts exactly 1, so a differ=0 that could not have been anything else would refuse.

## Figures

- 6 plants, 6 killed by a FAIL line: `python3 -I tools/audit/seat/r10_stamp_round_mutants.py`
- 720 grid rows, 0 differ: `python3 -I tools/audit/seat/r10_stamp_round_mutants.py --null e5ddba1fad5e6eccfeceaeaaa249bc459963405b`
- `stamp_self_test=pass`: `python3 tools/release/stamp.py --self-test`
- scoped gate `MODE: SCOPED`, `tests/doc_claims.py` and `tests/entities.py` run, both green: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`
- structure ratchet passed: `python3 tests/structure.py`
- `tools/audit/briefs/orchestrator.md` at 4251 of a 4251-token cap at the merge base and at the head: `node tools/policy/policy_lint.mjs --budgets`
- CLI refusals at the live tree (VERSION 7.0.5, roster round 10), each `stamp refused (rule 3)` before any fetch: `python3 tools/release/stamp.py --bump major --title t --dry-run`, likewise `--round-close 7`, `--round-close 9`, and `--round-close 10 --bump minor`

## Red checks

none. `prepr.sh`'s CI predictor named two predicted reds before the handoff (`governance / instrument-self-tests` UNWIRED, `tests / closures` INERT READS), both caused by this branch's new driver. Both are repaired in this diff: the self-test is wired, and `--apply-inert` wrote the entry. The predictor is the cheaper detector, and it caught them. Locally, `policy_lint`'s budget lane also refused an intermediate head that added a sentence to `orchestrator.md` past its token cap. That sentence was reverted, and the cap reads as at the merge base.

## Forward-carry

none

## Friction

none
