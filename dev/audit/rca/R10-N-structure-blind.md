# RCA: the N-structure-blind barrier leaks through a count it printed and never gated

Seat: round-10 root-cause, class `N-structure-blind` (#2235). The ledger trigger is met on
three arms: per_round, cross_round and barriered_any. The class is `barriered` by
`tests/structure.py`, so this round's instances say that barrier leaked. Round-10 baseline
`554e2ecfa`; analysis tree `origin/main` at `f1b21daab`. This seat fixes no instance: the
five fix PRs below own those. It builds the countermeasure in section 5.
Every figure is in section 7 with its command.

## 1. The instances, and who delivered them

| id | instrument and seam | proxy that stood in for the property | delivered by |
|---|---|---|---|
| D7-s1-01 | `structure.py` `max_class_loc` | `max()` over the class table: only the largest class is priced | #2340 (`class_excess_loc`) |
| D7-s3-01 | `structure.py` `dead_members` name-kept | an untyped `x.name` load keeps alive every member of that name | #2340 (`ReceiverTypes`) |
| D7-s3-02 | `www/heatpump-optimizer-card.js` | no dead-code metric reads anything but `*.py` | #2373, stacked under #2401; open |
| D7-s3-51 | archscore `untyped_payload_keys` `Flow.returned_keys` | census seeded from coordinator attributes only | #2293 (C14) |
| D7-s3-52 | archscore `untyped_payload_keys` `is_any` | string match on the unparsed annotation | #2293 (C1b) |
| D7-s1-83 | archscore hub role engine | aliases through readers and rebinds not followed | #2311 (catch-up judge, #2251) |

The ledger counts six R10 instances (`per_round.R10 = 6`). D7-s1-83 joined the class
through the catch-up judgment (`dev/audit/rounds/round10/CATCHUP-JUDGE.md`), and #2311
delivered it.

## 2. Cause, reproduced

Every structural instrument here decides a semantic property from a syntactic proxy. The
properties are liveness, class growth and payload typing. The R9 class RCA
(`RCA-BULK-2.md` §2.2) named this, and its countermeasure (§2.5) had three parts:

1. reachability liveness;
2. a planted-shape self-check;
3. *"Declared blind shapes are counted as `RESULT unmeasured_shapes=<n>`, never left to
   prose."*

F10.4 landed the barrier in #1838 (`ca718836`, `16e8fef9`; merged in `2b6c5b87`, first
tag `v6.7.14`). Part 3 landed as a printed line,
`unmeasured: N live member(s) kept only by an untyped x.name load`. That line went into
the report, not into `measure()`'s `metrics`, so `ratchet` never compared it with a
budget. The ledger's own `barrier` field at the baseline says so: *"Not reached: a member
kept alive only by an untyped load of a name another class defines (printed,
unmeasured)"*.

The printed count grew on every release while the gate stayed green (F1):

| tag | `unmeasured` |
|---|---|
| v6.7.14 | 124 |
| v6.7.15 | 132 |
| v6.7.16 | 132 |
| v6.7.17 | 141 |
| v7.0.0 | 152 |
| `origin/main` after #2340 | 38 |

D7-s3-01 is six members drawn from those 152, and #2340 found and deleted four of them
dead. #2340 narrowed the shape and kept it printed. It did not gate it.

**Reproduced at `origin/main`, after the fix (F2).** The harness
`dev/audit/harnesses/r10_rca_name_kept_plant.py` plants a live class in `diagnostics.py`,
a module Home Assistant loads. The class has a dead `as_dict`, whose only load is the
untyped `x.as_dict()`.

- Main's own `tests/structure.py` and budgets read `plant_refused=0`, with
  `plant_name_kept=39`: the dead member passes.
- The control, the same member under a unique name, reads `null_refused=1` on
  `dead_methods`.
- The architecture score on the same plant reads `dS 0`, `rises []`, `NULL` (F3).

Neither required check refuses a dead production method.

**The other three ways the barrier's unit missed an instance:**

- **One metric at a time.** #374 (2026-09-03) fixed the max-only shape for methods with
  `max_method_loc`, and `methods_over_150/200` later priced every offender. `max_class_loc`
  kept the max-only form until D7-s1-01. The self-check plants one example per past
  *instance* (#364, #1395, #1538, #1539, #1686). It does not plant one per shape across
  sibling metrics.
- **One instrument at a time.** The ledger barrier names `tests/structure.py`. The
  architecture score landed eleven hours after F10.4: #1851 (`399098f6`, merged in
  `16551007`, first tag `v6.7.15`). It came with its own calibration corpus, and that
  corpus planted the spellings known when the score was written. Three of the six R10
  instances are in it. No step adds a new instrument of a barriered class to that class's
  barrier. `archscore.dead_members` reuses structure's
  `dead_methods + dead_top_level_symbols` (`tools/audit/archscore/vector.py`
  `structure_rows`), so it inherits the name-kept blindness. F3 shows that.
- **One language.** `textWidth` lost its last caller in #1817 (`fdf0639c`, merged in
  `fee38809`, first tag `v6.7.13`), one release before the barrier. No dead-code metric
  read `.js`, and nothing ever named that as a shape the barrier left uncovered.

## 3. Class search

At `origin/main`, outside the findings' own deliveries:

1. **`structure.py` name-kept, ungated.** 38 members are printed and unmeasured (F1). This is
   the residual countermeasure 5.1 gates.
2. **The finder's D7-s3-01 harness is hint-keyed.**
   `dev/audit/rounds/round10/D7/s3/namekept_receivers.py` counts a "typed hit" when the
   receiver's *text* contains a hard-coded hint. It reads `candidates_with_zero_typed_hits=6`
   at both the baseline and main (F4). #2340's body records it as keyed to the instance, not
   the property.
3. **The D14 sweep enumerator hard-codes its dispositions.**
   `dev/audit/rounds/round10/D14/sweep-N-structure-blind/enumerate.py` reads
   `RESULT instances=5` at `554e2ecfa` and at `origin/main` (F5).
   - Rules B, C and E return the literal `"instance"`, and rule D sets `is_any` to
     `"instance"` by name.
   - Rule A matches sibling keys by AST name, so it misses #2340's `class_excess_loc`, which
     is bound through `excess`.
   - It does not move under the fixes, so it is not a barrier candidate.
4. **#2293 left its residual in prose.** Spellings outside `annotation_members`'s grammar (a
   generic `X[T]`, a `TypeVar` bound, a `Protocol`) are *"a residual the companion does not
   drive"*. That residual is not counted. The ledger's barrier now names it under
   "Not reached".
5. **The card metrics after #2373 are priced, not blind.** `card_dead_definitions` is an
   arch-score metric. A rise on the required `arch-score` check passes only if the body
   explains it (`tools/audit/archscore/ABOUT.md`). That is a seam, not an instance.

Items 2 and 3 are the class's mechanism inside audit instruments, not production gates. The
R10 sweep counted `beyond_finding 0`, and this seat does not refold them (section 8).

## 4. Process state: (c) followed and did not produce the intended result

The barrier existed and ran. `tests/structure.py`, with its counting-rule self-check, ran
green on every PR from `v6.7.14` to `v7.0.0`. The archscore calibration ran on every PR
that touched it. F10.4 did carry out RCA-BULK-2 §2.5 item 3: the unmeasured shape is
counted and printed. The result was not what the item was for. A count outside `metrics` is
not refused, so it grew by 28 across four releases.

The unit is wrong in three ways, and all three are (c):

- the unmeasured count is printed, not ratcheted;
- the plants are one per past instance, not one per shape across sibling metrics;
- the barrier's scope is one file in one language, not the class's mechanism.

The other states were considered and rejected:

- **Not (a).** A barrier existed, and the contract says an instance of a barriered class is
  not (a).
- **Not (b).** Each fix did what its brief asked. #2340 documented the residual it left.
- **Not (d).** The archscore arrival looks like a changed precondition. But the card's dead
  function predates the barrier, and the archscore carried its own calibration step, which
  was followed. The unit error, not a changed precondition, is the one cause across all six.

R9's RCA made the same (c) call (§2.3): *"each fix widens the proxy for the shape just
reported"*. R10's fixes repeat it. #2293 closed the listed spellings and left the rest in
prose. #2340 narrowed name-kept and left 38 printed.

## 5. Countermeasure, by arm

### 5.1 Built: `name_kept_members`, a ratchet row

`tests/structure.py`'s `measure()` returns `name_kept_members`, the length of the name-kept
table, and `tests/structure_budgets.json` records it at 38. A rise now refuses
(`FAIL name_kept_members 39 > 38`). The honest ways out are:

- type the receiver, so the load reaches the member and it is live or measured dead;
- delete the member.

A new budget key is not a raise: `tools/policy/budget_raise_gate.py`'s schema reads
`tests/structure_budgets.json` keys as `MAX`, and a new `MAX` leaf is not refused. The row
was added by hand, not by `--record`, and `recorded_at` is unchanged, because only this one
row is new.

The acceptance test is the harness's four arms on this head (F2):

| arm | `refused` | `name_kept` | `dead_methods` |
|---|---|---|---|
| clean | 0 | 38 | 0 |
| plant (dead `as_dict`, name-kept) | **1** (`name_kept_members`) | 39 | 0 |
| null (dead, uniquely named) | 1 (`dead_methods`), as before | 38 | 1 |
| typed (`x: "PlantedRecord"`) | 0 | 38 | 0 |

On main's `structure.py` and budgets, the plant arm reads `refused=0`.

### 5.2 Built: the rule that a printed residual count must be gated

The smallest enforcing home is the one already enforcing half of it.
`tools/policy/field_coverage.mjs`'s census arm (class N-silent-zero, round 9) runs each
registered count-printing instrument on a copy of the tree. It runs once as the tree is
and once with one planted member, and refuses a count that does not rise by exactly one.

A count that moves is not yet a barrier, so each census now names `gate`, the budget row
that must refuse the planted member. The arm reports:

| condition | report |
|---|---|
| the count rises by one with no `FAIL <gate>` | `BLIND: UNGATED` |
| no gate is named | `REFUSED` |
| the run is already red on the gate unplanted | `REFUSED` |

The three censuses are `dead_methods`, `dead_top_level_symbols` and the new
`name_kept_members`, whose plant is a live `_CensusKept.as_dict` that only an untyped load
reaches.

Demonstration (F6):

| tree | `name_kept_members` census reads |
|---|---|
| head | `read=3`, all three refused on their rows |
| main's `structure.py` and budgets | `REFUSED`: the count line cannot be read, since the residual is not a row |
| head `structure.py` with the row uncapped (9999) | `BLIND: UNGATED, 38 -> 39 … no FAIL on name_kept_members` |

`--self-test` gains three arms: UNGATED, no gate named, already red unplanted. All 4 census
arms pass, and the self-test ends `FIELD COVERAGE SELF-TEST ok` (F7).

The ledger carries the rule as data. The N-structure-blind `barrier` field now names
`name_kept_members` and the census arm. Its "Not reached" list holds only two shapes, each
named with its owner:

- the card `.js`, until #2373 merges;
- #2293's spelling residual.

**Not built, and why.** A registry cannot force an *unregistered* instrument to register.
A `fold_ledger.py check` arm could refuse a `barriered` class whose barrier text says
"printed" or "unmeasured" without naming a census. `fold_ledger.py` is code-owned by tvofi
(`.github/CODEOWNERS`), and the arm would be a text predicate over prose, which is this
class's own mechanism. Refused here; owner: tvofi (section 8, question 3).

### 5.3 The language arm (the card `.js`)

Carry: #2259 item 2, R10-ARCHSCORE-COVERAGE part 4 (#2373, stacked under #2401). It adds
`card_dead_definitions` and `card_clone_copies` to the architecture score
(`tools/audit/archscore/metrics/card.py`), so a new dead card definition is a rise the
required `arch-score` check refuses unless the body explains it. Nothing separate is built
here. Two things are owed when #2373 merges:

- `card_dead_definitions` registers as a `field_coverage.mjs` census, with its plant and
  the arch-score gate as its refusal;
- the ledger's "Not reached" entry for the card is struck.

That belongs to #2259's item-2 group, not to this RCA.

### 5.4 The instrument-coverage arm (archscore arrived with nothing adding it to the class)

**Countermeasure, built as data:** the ledger `barrier` field now names the arch-score
required check, its calibration corpus and #2293/#2311's census holes beside
`tests/structure.py`. The class's barrier unit is the set of instruments, not one file.

**Refused: a process step** ("a new structural instrument is added to the barriered class's
barrier"). Fold that into a brief and it is a rule asking a seat to notice; no check runs
it.

- One such instrument arrived in the 54 releases from 2026-09-03 to 2026-10-14 (F8).
- Its three class instances cost 2.1 + 2.1 + 9.5 = 13.7 h of fix span (F9), so
  13.7 h / 54 = **0.25 h per release**.
- A brief line read by every D7 and D14 seat costs more than that in attention, and it
  would not have caught the archscore's holes. The archscore *had* a calibration corpus.
  What it lacked was a gated count of what the corpus could not plant, and 5.2 now asks
  that of any registered census.

### 5.5 Refused: the sweep enumerator as a CI check

It reads 5 at both ends (F5). It would be a detector that does not detect.

## 6. Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, wall-clock per release.

- **cost(defect):** fix-PR span from first commit to merge (F9).
  - #2293: 6.3 h, 3 findings (2 in class), so 2.1 h each.
  - #2311: 19.0 h, 2 findings, so 9.5 h each.
  - #2340: 35.2 h, 2 findings, so 17.6 h each.

  The mean over the 5 merged class findings is **9.8 h**. That is a lower bound: it excludes
  the finder, verify, judge, sweep and RCA seats. #2373 is open.
- **P(recurrence):** four instances were introduced after the barrier shipped. D7-s3-01's
  shape is in `v6.7.14` itself, and the three archscore instances in `v6.7.15`. That is 4
  over the 5 releases `v6.7.14`..`v7.0.0` (F8), so **0.8 per release**.
- **Expected defect cost:** 0.8 × 9.8 h = **7.8 h per release**.
- **5.1** adds 0 s of CPU, because the count was already computed. Its human cost is the
  reds it raises on honest code. Pre-#2340 growth was 28 over 4 intervals (F1), so 7 per
  release. At an estimated 25 min each, a CI cycle plus typing a receiver, that is ≤ **2.9 h
  per release**. This is an upper bound and an estimate: post-#2340 growth is unmeasured.
- **5.2** adds 2 `structure.py` runs per census when an input changes
  (`governance.yml` runs field coverage only when `tests/structure*` and its other inputs
  move). The census arm read 81.7 s for three censuses, against 65.5 s for two (F6), so
  **+16 s** on such PRs.

Both pass.

## 7. Figures

Each figure was taken at `origin/main` `f1b21daab` or at this branch's head, in a full clone
(`git fetch --unshallow --tags origin`), with `/etc/profile.d/hpo-toolchain.sh` sourced.

- **F1** The unmeasured series. In a detached worktree at each of `v6.7.14 v6.7.15 v6.7.16
  v6.7.17 v7.0.0`, run `PYTHONPATH=tests/hastub python3 tests/structure.py | grep -oE
  "unmeasured: [0-9]+"`. Main: the same command at `f1b21daab`.
- **F2** The four plant arms on the head:
  `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_rca_name_kept_plant.py`. On main:
  add `--structure <main's tests/structure.py> --budgets <main's tests/structure_budgets.json>`,
  each exported with `git show origin/main:<path>`.
- **F3** Arch-score on the plant. With the harness's plant written into `diagnostics.py` in
  a scratch worktree, run `python3 tools/audit/archscore/vector.py .` on the clean tree and
  on the planted one, then `python3 tools/audit/archscore/score.py --delta <clean.json>
  <plant.json>`. It reads `"dS": 0, "rises": [], "verdict": "NULL"`.
- **F4** `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/s3/namekept_receivers.py`,
  at `554e2ecfa` and at main.
- **F5** `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-N-structure-blind/enumerate.py`,
  at `554e2ecfa` and at main.
- **F6** `node tools/policy/field_coverage.mjs --only census`, on the head; then in a
  scratch worktree with main's `tests/structure.py` and budgets; then with the head's
  `tests/structure.py` and `name_kept_members` set to 9999.
- **F7** `node tools/policy/field_coverage.mjs --self-test`.
- **F8** Releases: `git tag -l 'v*' --contains 2b6c5b87 --merged v7.0.0` prints the 5 tags
  from #1838 on; `git tag -l 'v*' --contains 16551007` starts at `v6.7.15`;
  `git tag -l 'v*' --contains fee38809` starts at `v6.7.13`;
  `git for-each-ref --format='%(creatordate:short) %(refname:short)' 'refs/tags/v*' | awk '$1>="2026-09-03" && $1<="2026-10-14"' | wc -l`
  prints 54.
- **F9** Fix spans: for N in 2293 2311 2340,
  `gh api repos/tvofi/heatpump_optimizer/pulls/N/commits --paginate --jq '.[].commit.author.date' | sort | head -1`
  gives the first commit, and
  `gh api repos/tvofi/heatpump_optimizer/pulls/N --jq .merged_at` gives the merge. The
  finding counts are from each PR body.

## 8. Open questions

1. Should class-search items 2 and 3 (the hint-keyed finder harness and the hard-coded
   sweep enumerator) fold as `beyond_finding` seams? Or should they go to the D14 brief by
   `finding-propagation.md`, as a rule that a sweep enumerator's dispositions must be
   computed and shown to move under the fix? That is the orchestrator's call; the brief
   is policy.
2. Should the sentence *"a declared unmeasured shape is a gated count, never a print or
   prose"* go into `fixer.md` or the D7 brief? That is policy and needs tvofi. This PR
   carries it as data (the ledger) and as a check (5.2) only.
3. Is a `fold_ledger.py check` arm wanted, refusing a `barriered` class whose barrier names
   a printed residual and no census? tvofi owns that file.
