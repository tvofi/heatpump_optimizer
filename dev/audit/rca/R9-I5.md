# RCA — class I5 (docs, comments or a compliance checklist drift stale against the code)

Round 9, RCA seat for I5 (N = 19 judged, 0 sweep instances at S2). Started beside F8.1; barrier
lands in F10.4 (doc_claims arms) and F11.3 (policy_lint pass), see Plan fold.
Baseline `1936d5ca` (v6.7.1); main `db878b29`. Prototype: branch `handoff/r9-rca-i5` @ `c6ba6036`
(cut from `db878b29`). Evidence files beside this one in `audit-r9/rca/i5/`.

## Root cause

### Cause

**A fact the code owns (an entity count, a state set, a schema's fields, a form label, a member
name, a unit glyph, a printed line) is restated by hand in reader prose, a comment, a translation
or a policy file, with no derivation link back to the code. The PR that moves the fact edits the
copies its author remembers; nothing reads the rest.** Which side moved, by `git log -S`:

| instance | the fact moved in | the prose |
|---|---|---|
| D6-s2-01 (`All 74 entities`, configuration.md) | #1497 (`3df1be62`, mold-floor binary sensor, 74 -> 75) | #1497 updated README.md and architecture.md, not configuration.md:196 |
| D6-s1-01 (Heat Pump Action states) | #571 added `idle`/`system_identification` | #1555 (`333b10fb`) rewrote that exact row, added `hot_water`, still omitted both |
| D6-s1-03 (disabled census) | hot-water gate | #1572 (`ca79a473`) rewrote the census rows and left six sensors out |
| D6-s2-05 (+2 new seams below) | #489, #735, #746 added schema fields | Services paragraphs never updated |
| D6-s2-04 (`two starting points`) | #455, #657, #1293 grew the multi-start | how-it-works.md unchanged since #69 |
| D11-s2-04 (CLAUDE.md mode line) | closure.py prints `MODE: SCOPED -- ...` since #84 | written wrong at #391, never drift |

So the reported cause "drift" is right in direction for most instances (code moved, prose did not)
and wrong for D11-s2-04 (written wrong). Three of the instances were last touched **by fix PRs of
rounds 7 and 8** (#1497, #1555, #1572): the fix programme itself writes and re-writes these copies.

Reproduction at `1936d5ca`: the S2 enumerator reproduces all 19 (`enum-base.out`, the counts S2
recorded). At the round-8 baseline `cdf82daa`, 12 of the 19 are already present (`enum-r8-cdf82daa.out`;
two harnesses crash there and print 0, see below). The in-window introduction is measured by running
the prototype arms at each merge's first parent and at the merge (`check_entity_prose` et al.):

| merge | count check | state-list check | census check |
|---|---|---|---|
| #1497 `bd04289c` | pass -> **FAIL** | FAIL -> FAIL | FAIL -> FAIL |
| #1555 `233a36bd` | pass | FAIL -> FAIL | FAIL -> FAIL |
| #1572 `4b2a7d8c` | pass | FAIL -> FAIL | FAIL -> FAIL |

Measured: **1 new instance** introduced in the 88 merges `cdf82daa..1936d5ca`, and **2 merges that
edited an already-stale sentence and left it stale**. The rest of the class is backlog that escaped
earlier rounds.

### Class search (beyond the sweep)

The prototype arms scan whole corpora, not the finders' sentences, and at `1936d5ca` they return
seams S2 did not:

- **2 new seams of D6-s2-05's shape** (configuration.md Services omits accepted schema fields):
  `assign_entity.manual_setpoint` (added #746) and `apply_topology.dhw`, `.wood` (added #735).
  Probe: `check_service_fields`. S2's `services_claims.py` checks the simulate_plan prose list only.
- **A 9th bare-unit leaf per language** in D4-s2-09's shape:
  `config.step.user_sensors.data_description.solar_radiation_entity` in strings.json, en.json and
  sv.json. The finder's rule scores only rendered fields, so it counts 8 per language.
- Checked and **not** seams: the card harness's own Python control arm prints 3 unresolved names
  (`_async_configure`, `_CERT_BARS`, `_draftRuns`); each resolves outside the package (HA core, a
  test module, a v3.2.0 history reference). The prototype's card arm reads the card only.

**Correction to the record.** S2's SWEEP.md and the issue draft say "I5 has no prior round entry —
this is the class's first round". `tools/audit/bugclasses.json` at `1936d5ca` carries I5 with
`rounds [1..7]`, **60 instances** (R1 10, R2 15, R3 10, R4 7, R5 9, R6 6, R7 3), `detector: null`,
`barrier: null`. Round 8 fixed more (`0a3075e8`, group R8-I5b, #1534–#1537).

### Process state: **(c)** — the process was followed and did not produce the intended result

The class already had a barrier, and it ran and passed:

- `tests/doc_claims.py` (#1413, round 6; extended in round 8) states its own design: *"Neither side
  is a hand-maintained enumeration: a new sentence of the same shape enters the check the moment it
  lands."* At `1936d5ca` it prints `ALL 30 checks PASSED` with all 19 instances present. Each arm is
  one **shape**; every round-9 instance is in a shape it does not have.
- `policy_lint.mjs`'s `citations` class resolves backticked symbols in policy prose and prints
  `TOTAL: 0 error(s) across 40 policy file(s)` on main (`policy_lint-main.out` shows the prototype's
  one new error). Its symbol pass skips every span holding a space
  (`if (/[\s/]/.test(inner)) continue`), which is exactly D11-s2-04's span.
- The process that grows the barrier was also followed: round 8's I5 commit `0a3075e8` records
  *"Process state (a): no barrier existed for the requirements-claim shape"* and adds *"a fourth
  arm"*. Each round recorded (a) for one shape and added one arm. At the class level that is (c)
  recorded as (a): the barrier existed, was obeyed, and its unit — one arm per shape found — cannot
  reach the next shape.

The countermeasure for (c) is therefore not a firmer instruction but a change of the barrier's unit:
**one arm per fact family, reading the whole corpus**, so the next sentence of any shape that
restates that fact is checked the day it lands.

### Why not the sweep's proposal (a nightly lane of the 19 finder harnesses)

Measured against the same bound:

1. **It fails open.** `enumerator.py` sums a missing `RESULT` as 0 and continues past a crash. With
   an interpreter lacking the venv's packages it exits 0 with 11 of the 14 counted instance rows at
   `flagged=0` and no `ERROR` line (`enum-base-broken-interpreter.out`); at `cdf82daa` two harnesses
   crash (`claims_false None`, `behaviour_claims_false None`) and are summed as 0.
2. **Most of it is state (c) again.** By their own headers, 9 of its 19 harnesses enumerate listed sentences by hand
   (howitworks, behaviour, claims.py's 82-claim table, card_version, quick_setup, setup_section,
   setup, architecture, dataflow): regression pins for those sentences, not detectors of the class.
3. **Nightly detects after merge.** Every detection then costs a follow-up PR; see the cost test.
4. It needs ~3,000 lines of off-tree harness tracked and classified, plus code-owned workflow and
   `nightly_status.py` changes.

The finders' sentence harnesses still have a job: each instance fix PR carries its own as the
failing test (`fixer.md` step 1). That is regression, and it costs nothing extra.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, per the round-8 -> round-9 window
(88 merges `cdf82daa..1936d5ca`, releases v6.6.11–v6.7.1).

Standing cost, upper bounds:

| part | runs in window | seconds per run | window cost |
|---|---|---|---|
| doc_claims arms | 390 branch commits in the 24 merges whose diff meets the widened closure, + 88 forced-full main runs = 478 | 1.05–1.33 s CPU (7- and 5-run medians); 2.51 s wall at load 10–14 on 4 CPUs | 636 s CPU (10.6 min); 1,200 s wall (20 min) |
| policy_lint quoted-line pass | 750 branch commits + 88 main = 838 (governance runs unscoped) | 0.29 s (205 files, 10.3 MB read + 4 regexes) | 243 s (4.1 min) |
| **total** | | | **14.7 min CPU, 24.1 min loaded wall** |

The closure widens only slightly: merges selecting `tests/doc_claims.py` go from 22 to 24 of 88.
Commits upper-bound pushes, so both rows overstate the cost.

Defect cost per instance, lower bound: **17.5 min** = the median elapsed time of 8 past docs-fix PRs
(#1033, #1114, #1252, #1264, #1278, #1344, #1418, #1423: 71.5 min) divided by the 5-finding cap,
plus 3.2 min per finding for the judge's re-run (RESUME.md: 23 rows in 73 min). Finder, verifier,
sweep, review and RCA seats are unmeasured and left out. So is user exposure: every instance shipped
in at least one release.

P(recurrence): I5 is in **every audited round** (R1–R7 ledger, R8 fix commits, R9) with a mean of
**9.9 instances per round** (79 over the 8 rounds that have a count). The prototype's arms cover
7 of the 19 round-9 findings fully and 1 partly: 37 %.

- On the measured class frequency, which the policy prescribes: 0.37 x 9.9 = **3.6 covered instances
  per round** x 17.5 min = **64 min** against 14.7–24.1 min. **Passes, by 2.6x to 4.3x.**
- On the in-window introductions alone (1 measured): 17.5 min against 14.7 min CPU passes; against
  24.1 min loaded wall it does not. That basis leaves out the two in-window PRs the barrier would
  have forced to finish the job, and every regression of this round's fixes.

**Nightly or per-PR.** A nightly run of the same arms would cost about 1.3 s per night, but each
detection would still cost a follow-up PR (lower bound 14.3 min per instance). It would save only
the audit's share, 3.2 min per instance: 3.6 x 3.2 = 11.5 min per round. Per-PR saves the whole
64 min at a standing 14.7–24.1 min. **Per-PR is chosen**, in scripts that already run per PR. No new
file, no new CI job, and no code-owned path.

### The barrier (prototype on `handoff/r9-rca-i5` @ `c6ba6036`)

Five arms in `tests/doc_claims.py`. Each derives its fact from executed production code and scans a
whole corpus (README, reader docs, blueprints, catalogs or the card), and each has an anchor:

| arm | fact from code | claims scanned | round-9 findings it covers |
|---|---|---|---|
| `check_entity_prose` | platforms' real `async_setup_entry` for a hot-water entry and a bare entry | every `<N> entities` in the corpus; README `### <platform> (N total)`; every README row listing an enum entity's states; every bare-entry disabled entity documented as disabled | D6-s2-01, D6-s1-01, D6-s1-03, the count part of D5-s1-01 |
| `check_private_mentions` | card code outside backticked spans, plus package .py/.json/.yaml tokens | every backticked `_name` in the card | D5-s2-01 |
| `check_unit_typography` | house style of the selectors (°C, m²) | every leaf of strings.json, en.json, sv.json | D4-s2-09 (+ the 9th leaf) |
| `check_service_fields` | the voluptuous schemas `async_register_services` registers | every `**\`service\`**` paragraph that lists or counts fields | D6-s2-05 (+ 2 new seams) |
| `check_option_labels` | options-form labels in en.json, by menu page | every options-page `Setting` table row and italic field name in the corpus | D5-s1-05 |

Plus one pass in `.claude/workflows/policy_lint.mjs` `citations`: a backticked `TAG: text` span in
policy prose must match a literal in the tracked sources (`<placeholder>` or a number matches an
interpolation). It is pinned in `REQUIRED_ROT` with a fixture line, so it cannot be deleted in
silence. Covers D11-s2-04's quoted span.

Demonstrations (commands from the repository root, `PYTHONPATH=tests/hastub:tests:custom_components`):

- **Fails on the defect.** `tests/doc_claims.py` at `db878b29` + prototype: `7 of 47 checks FAILED`,
  exactly the round-9 instances plus the three new seams (`doc_claims-main.out`); at `1936d5ca`, the
  same 7 (`doc_claims-baseline.out`). `policy_lint.mjs` at main + prototype: 1 error, CLAUDE.md's
  `MODE: SCOPED — 0 script(s) run`.
- **Passes once fixed.** A scratch copy with the instances fixed (docs, card comments, catalogs,
  CLAUDE.md): `ALL 47 checks PASSED` (`doc_claims-fixed.out`). The CLAUDE.md span rewritten to
  `MODE: SCOPED -- 0 script(s) run` gives `TOTAL: 0 error(s)`, with `FIXTURE ok` and 194 pins.
- **Null control and perturbation.** On the fixed copy, each one-line re-introduction fails exactly
  its own check and nothing else: README 75 -> 76, Buttons total +1, a state dropped from a row, a
  name dropped from the census, a ghost `_member` in a card comment, `45 C` in sv.json, a service
  field dropped, `All 28 fields` -> 27, a renamed options row, an italic ghost label, and an
  unprinted `MODE: PARTIAL` line in a rule (`perturb-fixed.out`, `perturb-extra.out`; the policy_lint
  perturbation was run in the branch worktree).
- **Cannot go green by skipping.** Removing the corpus subject fails the anchor: no `<N> entities`
  left, no `Disabled by default:` list, no `Setting` tables. Production that fails to import exits 1
  (`heatpump_optimizer.coordinator` poisoned). Disabling the policy_lint pass prints
  `FIXTURE VACUOUS: check 'citations' produced no error saying "no tracked tool prints it"`.
- **Ratchet.** `tests/structure.py`: `STRUCTURE RATCHET PASSED`. No production line changed, and
  no `*_budgets.json` is touched.

Known limits, stated so nobody reads them as coverage: the options-label arm reads options-page
tables only, not config-flow tables. The quoted-line pass skips spans that wrap a line. The census
arm reads README only.

### Residual: 11 findings no mechanical arm reaches within the bound — **to tvofi**

D5-s1-02 (quick-setup promise), D5-s1-03 (card-version model), D5-s2-02 and D5-s2-03 (numeric
comments), D5-s2-51 (data-flow comments), D6-s1-02 (options-page placement), D6-s2-02 (flowchart
menu), D6-s2-03 (curve-bias rate), D6-s2-04 (multi-start count), D8-s3-02 (translation meaning), and
the flow-description part of D5-s1-01. Each states **behaviour** in prose. The code has no fact
table to derive it from without hand-listing the sentence, which is the design this RCA finds to be
state (c). The cheapest detector that found them is the D5/D6 audit. The class owes a barrier, so
I do not record a refusal. tvofi's choice:

1. **Accept the residual.** The sentence pins ride the instance PRs as regression tests, and D5/D6
   stay the detector for new behaviour prose. Cost 0; recurrence as now.
2. **A reader-docs writing rule**: a count, list or number the code owns is not restated. The docs
   link to the entity table or to a section a check derives. This is policy on `README.md` and
   `docs/`, which `writing-for-agents.md` scopes out. It addresses (c) by removing copies, not by
   checking them. Needs your ruling.
3. **Drop D6-s1-02 and the D6-s2-04 count from the residual** by extending the arms: a
   config-flow menu-page census, and the multi-start candidate count read from
   `optimizer._multi_start_minimize`. That adds about 60 test lines and has no prototype here.

## Plan fold

- **The barrier is split across two PRs; both are already in the plan and both already own the
  file.**
  - `tests/doc_claims.py` arms -> **F10.4**, as planned. F10.4 already lists the file under Edits,
    and it already waits, directly or through its chain, on every I5 instance PR.
  - The `policy_lint.mjs` quoted-line pass, its fixture line and the `REQUIRED_ROT` pin -> **F11.3**,
    not F10.4. F11.3 already edits `policy_lint.mjs` and fixes the only instance of that sub-shape
    (D11-s2-04 in CLAUDE.md), so it can merge green. No new `after` edge.
- **Files and ownership.** `tests/doc_claims.py`: not code-owned, not policy.
  `.claude/workflows/policy_lint.mjs` and `.claude/workflows/fixtures/policy-rot/citations.md`: not
  code-owned and not in CLAUDE.md's policy list. F11.3 is tvofi's anyway. No new tracked file, so
  nothing needs classifying. `doc_claims.py`'s recorded closure will read UNDER-SCOPED (it now reads
  the card and more package files). CI's `closures-autofix` records it, so do not `--single` it.
- **Line estimate.** Production 0. Tests: doc_claims.py +231 as prototyped (about 290 with option 3
  above); policy_lint.mjs +36/-1 and the fixture +1. No budget raise.
- **Findings that constrain the instance PRs.** These must be carried into each lane's brief before
  F8.1 merges (`finding-propagation.md`); I write only here, so the orchestrator carries them:
  - **F5.1 (D4-s2-09):** fix the 9th leaf, `config.step.user_sensors.data_description.solar_radiation_entity`,
    in all three catalogs, or delete it if unrendered. Otherwise F10.4's unit arm is red.
  - **F8.1 (D6-s2-05):** `assign_entity`'s `manual_setpoint` and `apply_topology`'s `dhw`, `wood`
    are open seams of D6-s2-05's shape. F8.1 is at five findings, so the orchestrator either treats
    them as D6-s2-05 sibling seams in F8.1 (same paragraph set, same fix) or routes them to F8.3,
    which has one slot. Probe: `check_service_fields`.
  - **F8.2 (D6-s1-01, D6-s1-03, D5-s1-05):** every state in the sensor's options is named in its row
    (`unknown` excepted). Every entity a bare entry disables is named in the list, in its row, or in
    a sentence with "disabled by default". Options labels must match en.json exactly (parentheticals
    ignored).
  - **F6.2 (D5-s2-01):** no backticked `_name` may be left in card comments unless it resolves
    against the card's code outside backticks or against package .py/.json/.yaml.
  - **F11.3 (D11-s2-04):** quote the line `closure.py` prints: `MODE: SCOPED -- <n> script(s) run`.
  - **F10.4:** run the arms at the merge base. Every FAIL line there is an instance PR not yet merged,
    or a seam listed above. Land no allow-list (`fixer.md` step 14).
- **Record changes owed (not policy):** the D14 ledger `tools/audit/bugclasses.json` I5 entry gets
  `detector` = the doc_claims command, and `barrier` / `status: barriered` once F10.4 merges. The S2
  "first round" sentence is corrected in the class issue body at filing.
- **Policy proposal (draft, tvofi's approval; addresses (c) recorded as (a)):** add to
  `tools/audit/briefs/root-cause.md` §2: *"An instance of an audit class that already carries a
  barrier is not state (a) because its shape was new: the barrier existed. Name why its unit did
  not reach the instance; the countermeasure changes the unit, not the arm count."*

## Figures

- `PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/sweep/I5/enumerator.py` at `1936d5ca`
  (sweep commit `38f1230e`): all 19 reproduce, 27.0 s wall (`enum-base.out`). At `cdf82daa`: see
  `enum-r8-cdf82daa.out`. Under an interpreter without the venv: exit 0, 11 of 14 rows 0
  (`enum-base-broken-interpreter.out`).
- Per-harness seconds at `1936d5ca`: 0.05–8.66 s each, about 31 s in total. The largest are
  `dataflow_comments.py` (8.66 s) and `howitworks_claims.py` (7.31 s).
- `git rev-list --first-parent --merges --count cdf82daa..1936d5ca` = 88. The branch commits across
  those merges total 750. Closure selection comes from `tests/closures.json`
  `closures["tests/doc_claims.py"]` against each merge's `git diff --name-only`.
- Docs-fix PR elapsed: `git log --merges --first-parent`, first branch commit to merge, for the
  8 PRs named in the cost test.
- `timing.out`: doc_claims with and without the arms, 7 alternating runs,
  `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=1`.
