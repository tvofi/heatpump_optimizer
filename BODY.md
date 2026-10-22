Group: R10-FLOW-YIELD-PROBE

Pinned pack file: `dev/programme/flow-study/roster/groups/R10-FLOW-YIELD-PROBE.json` at pack commit 78117030 on branch `claude/dazzling-gauss-7l3u2b`.

R10-FLOW-YIELD-PROBE (owner ruling R13) explains why real-catch blocks per reviewed PR fell from 0.52 to 0.15. The record is `dev/audit/rounds/round10/D13/yield-probe.md`, and every figure in it comes from `tools/audit/seat/review_strength.py`, which reads the verdict bus over git only. No production code, budget, `VERSION`, manifest or claim file is touched.

Round 6 follows the orchestrator's split decision (O-3) on the round-5 block:

- **The guardrail is split out.** The record's threshold, arms and back-test, and the tool's `--guardrail` path with `ALPHA` and `binom_cdf`, are removed. They are R10-ORCH-MACHINERY's carry (item b8b28b28). The record now answers only why the rate fell. Its one binomial figure is stated as a formula: (1 − 0.28)^20 = 0.0014.
- **H1 and H9 are killed by fixtures.** PR 18's delivery row names `R10-FLOW-YIELD-PROBE`. PR 16 adds `tests/t16.py` and `tools/t16.py`, which are top-level directories outside the product, and keeps its 150 lines.
- **The sweep's literal class drops each single character of a regex literal** (the pattern argument of an `re.` call), one mutant per inner position. Its first run found 9 undisposed survivors. Eight are killed by fixtures:
  - group `R1-555` puts a digit inside each range of GROUP_RE;
  - PR 21 pins the class word up to its own colon;
  - PRs 22 and 23 carry a nonce and a confirmation with no space after the colon;
  - `--fetch` with `--by origin` and no `--roster` is refused before the fetch.

  The ninth, the drop of GROUP_RE's first `]`, is disposed as equivalent on the bus's inputs. All 150 roster groups hold two or more characters after the dash. A one-character group such as `R1-X` separates the tool from the mutant.
- **Committer time is pinned.** PR 20's verdict was authored a month before it was committed, and the window reads it by its committer time.
- **The `--fetch` fixture's push is registered** in `ref_privacy.py`'s `PUSHERS` as `fixture`.
- **DISPOSED entries (a) and (c)** now say "equivalent on the bus's inputs" and name the input that separates each one. Entry (b), `cdf < ALPHA`, left with the guardrail.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_011FQcopbARzxDhthavMrv7v

## Head

Code head `218b0af4c3176a671207a2253ada97ca248a726d`. It merges `origin/main` at `cd4aaed44` (v7.0.3) into the reviewed head `6ad8089c14b50de2f6408ef6948a7d86ca4c52c2`, and adds three commits on top. The sweep ran at `29110ab18`. Its last commit drops the one DISPOSED entry that run reported stale, and nothing else changes: `cmp list_before.txt list_after.txt && echo MUTANT-LIST-IDENTICAL` over the harness's `--list` prints `MUTANT-LIST-IDENTICAL`.

## Mutation proof

The class rule is the command `python3 dev/audit/harnesses/r10_review_strength_mutants.py --jobs 4`. Its header states the classes and BOUNDS. At `29110ab18` it prints `RESULT mutants=2350 killed=2306 survived=44 disposed=44 undisposed=0 stale=1`. The stale entry is `cls`'s `or ''` arm, which PR 21's no-class block now kills, so the head drops it. Each survivor is keyed and reasoned in the harness's `DISPOSED`.

The verdict's hand mutants were applied in a scratch root at the head. Each fails exactly one check:

- H1 (`[A-Z0-9-]*` → `[A-Z0-9]*` in GROUP_RE): `FAIL: group regex: a group's inner dashes are part of it (18 R10-FLOW-YIELD-PROBE, not R10-FLOW)`.
- H9 (`"tests/"` added to the product prefixes): `FAIL: product: tests/, tools/, custom_components.md and blueprints.md are not under the product prefixes (16)`.
- H5 (`%cI` → `%aI`): `FAIL: a verdict counts at its committer time, not its author time (20: in 10-05T09:46..09:48)`.

## Null control

- **M0.** The unmutated emission passes (`review_strength self-test: 87 checks, 0 failed`) before any mutant runs.
- **No figure moves.** The study bundle (the record's command) was printed by the `6ad8089c` tool and by the code head's tool over the same fetched bus. `diff old.txt new.txt && echo BUNDLE-IDENTICAL` prints `BUNDLE-IDENTICAL` (2026-10-22T11:51Z, 403 verdicts on the bus, `facts as of 2026-10-21T15:15Z: tree e7c664856776 roster 2c76c3128bf6`).

## Figures

- `python3 -I tools/audit/seat/review_strength.py --self-test` prints `review_strength self-test: 87 checks, 0 failed`.
- `python3 dev/audit/harnesses/r10_review_strength_mutants.py --jobs 4` prints `RESULT mutants=2350 killed=2306 survived=44 disposed=44 undisposed=0 stale=1` at `29110ab18`. The stale entry is removed at the head (see Head).
- `python3 -I tools/audit/seat/ref_privacy.py --check` prints `0 refused`.
- The finder's harness is the tool on the real bus after `--fetch`, with both ends at the brief's quoted rates:
  - `python3 tools/audit/seat/review_strength.py --window A=2026-10-15T12:37Z..2026-10-21T11:00Z` prints `PRs 112 verdicts 257 real 58 (0.52/PR)`.
  - The record's bundle prints `all L PRs 47 verdicts 84 real 7 (0.15/PR)`.
  - Every window closes by 2026-10-21T15:15Z.

## Red checks

- **`instrument-self-tests`** was red at `6ad8089c`: `ref_privacy: REFUSE tools/audit/seat/review_strength.py:854`. It is fixed by the `PUSHERS` entry. The cheaper detector is `python3 -I tools/audit/seat/ref_privacy.py --check`, which takes seconds and was not run before the push. It now prints 0 refused.
- **`pr-contract`** was red at 10:12Z on `6ad8089c`: `check instrument-self-tests is red and ## Red checks does not name it`. It follows from the red above, because the body was written before that check concluded. The cheaper detector is `policy_lint.mjs --pr-body <body> --red <name>`, run once every check on the head has concluded. This body names the red.
- **`nightly-status`** grades main's scheduled run, not this diff, which touches nothing it reads. Carry: dismissed: grades main, not this diff
- **Local**, with `PYTHONPATH=tests/hastub` and `PREPR_SKIP_CLOSURES=1`: `tests/closure.py select` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out`. Both pass at the code head (3.13): `ALL 2388 ENTITY CHECKS PASSED` and `ALL 109 HARNESS HEADER CHECKS PASSED`. `tests/structure.py` prints `STRUCTURE RATCHET PASSED`, and `tmp_paths.py --check` prints 0 refused.

## Forward-carry

- The guardrail (threshold, arms, back-test, planted-defect calibration and the tool's `--guardrail` path) is split out of this PR. The owner group gets two corrected points. First, P(X ≤ 4 | 30, 0.28) = 0.0495, so the 30-PR arm trips at 4 or fewer, not 3. Second, the round-5 finding that `ALPHA` is unpinned between 0.05 and 0.0526 is moot here, but the seat-family arm's k = 2 of 20 gives P = 0.0526, so any `ALPHA` the guardrail adopts needs a check at that P. Destination: `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-ORCH-MACHINERY (item b8b28b28)

## Friction

none
