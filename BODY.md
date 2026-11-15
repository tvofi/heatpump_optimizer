R11-PRE-ROUND-METRICS, part 1 of the group (topic r11-pre-round-metrics-p1): decision 0018 section 5's two held-out instruments, planted-defect recall and the two-finder overlap estimate, on the path to the round-11 finder start (tvofi, 2026-11-15, card E11-N-P744-SCOPE).

`tools/audit/seat/plant_recall.py` plants a held-out seat's objective bugs into the baseline export and counts recall after the judge; `tools/audit/seat/finder_overlap.py` seats a twin finder on one scopes.json seat's universe and estimates the bugs there from the judged-real overlap, reported with both seats' models. Each is self-tested in `instrument-self-tests` (steps `plant-recall`, `finder-overlap`, read sets recorded by `selftest_scope.py record`), code-owned in `.github/CODEOWNERS` (carry 0), and its run commands, before the Finders phase and after the judge, are in its `tools/audit/seat/instruments/*.py.md` page (the documented command the orchestrator runs; `audit-find.js` is not edited). The plants themselves are not written here.

Carry 0: both instruments are added to `.github/CODEOWNERS` in this pull request and built to 0018's definitions; the ones they cannot meet are the cards below. Carry 3: this part builds its two held-out instruments, recall counted after the judge (a plant lost at the verifier or the judge is a miss) with plants refused unless spread over both the natural universe and the configuration space and refused from a finder, orchestrator or evaluator planter, and the overlap reported with the two seats' models; carry 3's section-2 and section-5 reads (`product_green` over the window with `gate`'s check count, the `lead_time` clock from the roster commit, runner seconds per merge) stay with the group's later parts, as this part's brief scopes them out.

## Cards

Definitions of 0018 that cannot be met as written, returned rather than bent:

- **C1 isolated dimensions take no plant.** Section 5 plants into "the baseline export"; `audit-find.js` runs D0, D3, D9, D11, D13, D14 and D15 in `git worktree`s, where `git diff` shows every plant to the finder. `plant` refuses a tree holding `.git`, so recall is read over the export's dimensions only and the seven isolated ones have no recall. Owner choice: accept that, or plant those worktrees as a commit the wall hides (not built).
- **C2 when a finding "finds" a plant.** 0018 defines recall as found / planted and names no matching rule. Built: a judged finding names a plant when its `files` hold the plant's file and the plant's `symbol` is a whole word of its `instrumented_symbol`, `title` or `claim`; every match is printed with the finding ids so the rule can be audited per plant.
- **C3 the overlap is counted after the judge.** Section 5 says "finding n1 and n2 with m shared" without a stage. Built as recall is (section 4 item 3): a seat's finding counts when its canonical finding is judged `verified` or `weakened`, and m is the bugs the judge's dedup merged across the two seats.
- **C4 the models are declared, not recorded.** No round record holds a seat's model (`finding.schema`, `JUDGE.json`, `reports-<box>.json`); the pair record carries the models the orchestrator dispatches with, which nothing re-reads.

## Head

ebd654c3bae14515bea4fd6536d95c98b4904289, measured at origin/main 26dbf7c43ec3742101398b098dbdcc61bbee8f19, 2026-11-15T13:04:51Z.

## Mutation proof

Each self-test edits a copy of its own production code above its self-test marker, one mutant per predicate, and fails unless the named case fails: `python3 -I tools/audit/seat/plant_recall.py --self-test` prints `mutant killed` for 20 predicates (planter ban and its normalisation, unnamed planter, `.git` tree, list inside the tree, both spaces, config cell, old text once, a plant changing nothing, empty list, the real verdicts and weakened among them, the file and the whole-word arms of a finding naming a plant, LOST against MISSED, the merge chain and its text spelling, and the three unread guards); `python3 -I tools/audit/seat/finder_overlap.py --self-test` for 10 (seat in scopes, both models, the box key, shared, the estimator, unseen, one model, the three unread guards; the verdict and merge rules it reads are `plant_recall.resolve`'s, the one reader of the judge's merge grammar, mutated in that file's run). Run alone, the `old once` mutant (`if n != 1:` to `if n < 1:`) turns `FAIL plant: an old text twice in the file is refused`.

## Null control

Each instrument's null control is an empty input printing `unread (<why>)` and no digit: `plant_recall.py recall` over an empty directory prints `recall  unread (no plant list, or an empty one)`, and `finder_overlap.py estimate` over one prints `overlap unread (no pair record)`; both are self-test cases with a mutant each. A sound plant list over both spaces is refused nothing, and a scopes seat with two models is seated (self-test cases).

## Figures

<!-- figure-block: scope-line mb=26dbf7c43ec3742101398b098dbdcc61bbee8f19 head=ebd654c3bae14515bea4fd6536d95c98b4904289 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->
- Self-tests, at the head: `python3 -I tools/audit/seat/plant_recall.py --self-test` ends `plant_recall self-test: ok (with mutants)`; `python3 -I tools/audit/seat/finder_overlap.py --self-test` ends `finder_overlap self-test: ok (with mutants)`.
- End to end on real data, illustrative plants (not round-11 plants): a two-plant list (P01 natural in `currency.py:money_scale`, P02 config cell `price_shape=flat` in `optimizer.py:_multi_start_minimize`) planted into a `git archive HEAD custom_components` copy by `python3 -I tools/audit/seat/plant_recall.py plant --plants <list> --tree <copy> --population <check_scopes.py --population output> --not orchestrator --not evaluator` prints two `PLANTED` lines; a second run refuses both (old text 0 times); `--not Demo_Planter` against planter `demo-planter` refuses. `python3 -I tools/audit/seat/plant_recall.py recall --plants <list> --judge-input dev/audit/rounds/round10/JUDGE-INPUT.json --judge dev/audit/rounds/round10/JUDGE.json` prints recall 1/2: P02 FOUND by D0-s1-01 and D0-s2-01 (judged weakened and verified), P01 MISSED. Control: no round-10 finding touches `money_scale`, so P01 must read MISSED, and it does.
- `python3 -I tools/audit/seat/finder_overlap.py estimate` over round 10's D0-s1 (`reports-B1.json`) and D0-s2 (`reports-B2.json`) as a stand-in pair (two universes, so an illustration of the count, not an estimate) and `dev/audit/rounds/round10/JUDGE.json` prints n1=1 n2=1 m=0, estimate 3.0, 1.0 unseen; checked by hand from the two reports' ids and their verdicts (D0-s1-01 weakened, D0-s2-01 verified, no merge between them): (1+1)(1+1)/(0+1) - 1 = 3. The same with the twin's report absent prints `overlap unread (a seat's report is missing ...)`; `seat --seat D0-s9` refuses (no such seat).
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: FULL` (`tools/ci/selftest_closures.json` is a gate file), left to CI; `python3 -I tools/ci/selftest_scope.py select --base origin/main` prints `MODE: FULL` (`governance.yml` changed). `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Red checks

none

## Forward-carry

none

## Friction

none
