Fix review: merge 1f9d606dd88ac324320772fe66142574823ac1e4
bus-nonce: c766152af8b8f87a42c3d101a8e26a34

Round 4, seat review-2071r4. This verdict judges the **resolution delta only**
(`7843b7992..1f9d606dd`, one main merge). Rounds 1-3 judged the code; round 3
returned `Fix review: merge 7843b7992…`, and its two kills (the round-1
vacuous selector pin, the round-2 `notifier.py:182 CONST` survivor) were
reproduced there. I re-ran the null controls at the merged head because the
merge touched the two test files that hold them.

## RESULT lines

- RESULT: **0 of 18** files in the branch's three-dot diff have a changed +/-
  payload between `bd59a4af1…7843b7992` and `a9baf164c…1f9d606dd`. **5** differ
  in hunk-header line numbers only — `strings.json`, `translations/en.json`,
  `translations/sv.json`, `tests/entities.py`, `tests/features.py` — the benign
  case. `app_approve.sh --carry` refused for exactly that reason; the per-file
  content test says no content moved.
- RESULT: `1f9d606dd` is a **clean automatic merge**: `--remerge-diff` body is
  0 lines, `git merge-tree --write-tree 7843b7992 a9baf164c` exits 0 with no
  conflict section and no `MERGE-CLAIM` marker, and its tree `679e3c775…` is
  **the same OID** as the commit's tree. 134 commits in the range: 133 are
  main's own lineage, **1** is new on the branch side — the merge itself,
  authored tvofi, 2026-10-09 21:19 +0200. No hand resolution, so nothing
  outside the two parents' content arrived.
- RESULT: the reviewed code is the judged code — `diagnostics.py`, `notifier.py`,
  `setpoint_check.py` and `tools/audit/seat/features_block.py` are
  **byte-identical** blobs at `7843b7992` and at `1f9d606dd`. Main changed none
  of them (`git diff --name-only bd59a4af1 a9baf164c` omits all three).
- RESULT: both claim files are byte-identical to **live** `origin/main`
  (`claimed_drift.txt eda8856b9`, `card_claimed_drift.txt c683379da`); the
  branch's diff touches no `tests/golden/` path, and every `tests/golden/**`
  file at head equals live main. `VERSION`, `hacs.json`, the manifest and
  `RELEASE_NOTES.md` are untouched by the delta.
- RESULT: the four ledger validators are **empty** at the live head —
  `completeness_problems` 0, `ledger_form_problems` 0, `layout_problems` 0,
  `triage_problems` 0 over an inventory of 5906 sites and 1269 dispositions.
- RESULT: all **7 of the branch's `killed_by` pins MATCH** a generated site by
  `(ledger_key, old)` — notifier.py lines 182, 198, 201 (x2), 219 and
  setpoint_check.py 176, 188 — so no line shift retired a pin, and the body's
  site line numbers are still accurate. `tests/mutation_table.py --normalize`
  is a **no-op** here (0 top-level keys changed, 0 retired keys, 1185 killed_by
  keys unchanged), so no re-key is owed.
- RESULT: no `*_budgets.json` moved at all between the branch's base and head
  (coverage/mutation/stress/structure/typing blob OIDs identical) — the branch
  raised nothing. Main's own merges raised `structure_budgets.json`
  `max_class_loc 8817→8818` and `seam_cut_total 760→762`; both sit at their cap
  at head. That is main's payment, not this PR's.
- RESULT: `tests/structure.py` prints byte-identical metric lines at
  `a9baf164c` and at `1f9d606dd` — **no metric moved** across the delta — and
  ends `STRUCTURE RATCHET PASSED`. The body's "every metric is unchanged from
  the merged-in main" re-derives exactly.
- RESULT: `tools/pr/ci_predict.py --base a9baf164c`: "no closures or fast red
  predicted". `tests/closure.py select --diff a9baf164c --workdir .`:
  `MODE: SCOPED -- 22 script(s) run, 11 scoped out` — the body's figure
  re-derives at the new base.
- RESULT: added-lines sweep over the 6 files both sides touched: all of the
  branch's added lines are present at head (0 missing), and none of its 4
  removed lines came back (0 resurrections). Check-count additivity confirms
  the merged tree holds both sides exactly: `tests/entities.py` 1694 (base) + 5
  (branch) = **1699** (head); `tests/features.py` 3507 + 12 = **3519** (old head
  1691 / 3500 over old base 1686 / 3488).
- RESULT: null controls re-run at the merged head under the CI venv (3.14.7):
  the branch's features block `ALL 14 FEATURES BLOCK PASSED`; round 3's
  reviewer slice (`/Users/timmalmstrom/hpo-seats/review-2071/evidence/entities_slice.py`,
  sha1 `630656715e99a0644772dcc5ecfd96a872feac95`, unmodified — my own
  instrument, disclosed per step 9) `ALL 20 ENTITY SLICE PASSED`;
  `features_block.py --self-test` 1 check 0 failed; `tmp_paths.py --check`
  "0 refused, 0 stale allow entries … ledger lines added since a9baf164c938";
  `tests/deployment_shape.py` `ALL DEPLOYMENT SHAPE CHECKS PASSED`.
- RESULT: the two kills round 3 bought are alive in the merged `features.py`:
  `ninety minutes of silence raises the repair …` (CI's `60 → 120` CONST killer)
  and `another input's failure beside a live floor-return sensor never raises it`
  (the selector killer) both appear in the block's ok-list at this head, and the
  block's text is identical to round 3's (213 lines).
- RESULT: step 11 at this head — **all 17 required contexts of ruleset
  23698884 concluded `success`**, none ABSENT, none red: `fast (3.14)`,
  `browser`, `briefs`, `closure-scope`, `closures`, `typing`, `hassfest`,
  `validate-hacs`, `policy-docs`, `wave-script`, `pr-contract`, `env-matrix`,
  `Analyze (actions)`, `Analyze (javascript-typescript)`, `Analyze (python)`,
  `mutation`, `budget-raise-gate`. `mutation` is green (round 3's kill holds at
  the merged tree) and `fast (3.14)` is green, so nothing there is owed an
  answer. No check ran red across the delta — `red=0` at every one of the seven
  300 s polls from 20:03Z to 20:38Z — so `defect-root-cause.md`'s red-check
  trigger has nothing new to answer at this head. Read from the commit's own
  check-runs API, latest-per-name, never `gh pr checks`.

## Why the carry was refused, and what that proves

The refusal was **context, not content**: main added lines above the branch's
hunks in five files, so every `@@` header moved while no `+`/`-` payload line
did. tvofi's ruling (2026-10-09, #201 comment 6083452844) is right that a
context change is where a semantic collision arrives quietly — so I did not take
the emptiness of the remerge-diff as sufficient. The three independent tests
that the merged tree is exactly both sides' content, added: the identical tree
OID against a fresh `merge-tree`, the byte-identity of the four instruments and
production files the fix owns, and the additive `R.check(` arithmetic. Under
those, the merge introduced no branch-content change and nothing in the fix
needs re-judging.

## False-agreement sweep on the auto-merged files

`tests/entities.py`, `tests/features.py`, `tools/audit/seat/INSTRUMENTS.md` and
`custom_components/heatpump_optimizer/strings.json` auto-merged (plus
`translations/en.json`, `translations/sv.json`).

- `strings.json`/both `translations/*.json`: valid JSON, **no duplicate keys**
  under an `object_pairs_hook` counter, and `floor_return_silent` present in all
  three with `{entity_id}` and `{minutes}` — the two placeholders the finding
  returns. Main's own additions to `strings.json` are config-flow names under a
  different subtree, so nothing overwrote the issue entry. `hassfest` and
  `validate-hacs` are green at this head.
- `INSTRUMENTS.md`: the branch's addition is one five-line entry describing
  `features_block.py`; it asserts no count, and main's edits to the file did not
  disturb it.
- No prose count in the merged tree was left un-checked: the body's "21 reader
  slots" re-derives as **21 distinct `CONF_` slots** at both `bd59a4af1` and
  `1f9d606dd` (the `git grep -n` form prints 23 lines, which is why the census
  is stated as slots, not lines — I measured both, and neither moved),
  `CONF_FLOOR_RETURN_TEMP_ENTITY` is one of them and `CONF_LOWER_FLOOR_TEMP_ENTITY`
  is a separate slot, so the body's no-double-report claim holds at the merged
  tree; the config-merge census still names `__init__.py`, `config_flow.py`,
  `coordinator.py`, `services.py`, and `diagnostics.py` now calls
  `config_view(entry.data, entry.options)` with `entry.data` mentioned only in
  comments; `git grep -n "_set_issue\b"` prints **nothing** at the merged head.

## The body, and what is owed

Nothing is owed on `## Head`: the body at this head **already names
`1f9d606dd…`** and describes the merge correctly ("an automatic merge by the
orchestrator, no resolution. The reviewed code is unchanged"), which I verified
as stated above; `pr-contract` is `success` here. My dispatch's item 7 premise —
that the body still names `7843b7992` — is stale; the re-take landed before this
review.

Two figures in the body were taken at the pre-merge base and I re-took them at
the live base rather than trust them: the scoped-closure line (unchanged at
22/11) and the archscore (`tools/audit/archscore/score.py --diff a9baf164c` →
`dS +0.0000 NULL` at this head). `nightly-status`, red in the body's account at
`86c6daf48`, is now **success** at this head: main's nightly owner landed the
fix, exactly as the body predicted when it declined the cause as not this PR's.
`record`, `recheck-gate` and `slow` are `skipped` at this head, so the
range's earlier heads rest on rounds 1-3's readings of them, not on this run's.

One routing fact, not a block on this head: live `origin/main` has moved twice
more since (`23d354970`), and its newer merges — #2065's 7a diagnostics rework —
rewrite `custom_components/heatpump_optimizer/diagnostics.py`
(`_coordinator_snapshot` into `_never_breaks` + a `_VIEWS` table) in the same
file and close region as this fix's `config_view`. `git merge-tree --write-tree
HEAD origin/main` is clean **right now** (rc=0, no claim-file marker), so the
next merge-main will likely auto-merge over that file. That is precisely the
quiet path the ruling is about: whoever merges it should re-take this delta test
at the new head, and if it auto-merges, read the two hunks together — both
edit the payload assembly in `async_get_config_entry_diagnostics`.

## Measurement I corrected in flight

`closure.py select --workdir .` writes `scope.json/.run/.skip/.txt` into the
workdir and then treats untracked files as changed, so my second run reported
`MODE: FULL` with those four artifacts named. That was my harness, not the tree:
I deleted them, re-ran clean, and the SCOPED 22/11 figure above is the clean
reading. My first `R.check(` tally counted matching lines instead of
occurrences; the additive figures quoted above are the occurrence counts. The
worktree and the session checkout are both `git status` clean after these runs.

## CI at the judged head

Latest-per-name from the commit's own check-runs API at `1f9d606dd` (taken
2026-10-09 20:02Z, 20:34Z and 20:38Z; raw rows in `evidence/ci_final_raw.tsv`,
`evidence/ci_table.md`; the 300 s poll history — seven polls, `red=0` at every
one — in `evidence/ci_wait.log`):

| check | status | conclusion |
|---|---|---|
| Analyze (actions) | completed | success |
| Analyze (javascript-typescript) | completed | success |
| Analyze (python) | completed | success |
| CodeQL | completed | success |
| briefs | completed | success |
| browser | completed | success |
| budget-raise-gate | completed | success |
| claims-autofix | completed | skipped |
| closure-scope | completed | success |
| closures | completed | success |
| closures-autofix | completed | skipped |
| coverage | in_progress | - |
| delivery-status | completed | success |
| delivery-status-publish | completed | skipped |
| env-matrix | completed | success |
| fast (3.14) | completed | success |
| hassfest | completed | success |
| instrument-self-tests | completed | success |
| mutation | completed | success |
| mutation-autofix | completed | skipped |
| mutation-ledger / -push / -nightly / -pin-plan / -pins | completed | skipped |
| nightly-ha | completed | skipped |
| nightly-status | completed | success |
| policy-docs | completed | success |
| pr-contract | completed | success |
| recheck-gate | completed | skipped |
| record | completed | skipped |
| record-autofix | completed | skipped |
| slow | completed | skipped |
| typing | completed | success |
| validate-hacs | completed | success |
| wave-script | completed | success |

`coverage` is the one context still running, and it is **not** among ruleset
23698884's 17 required contexts; every required one is `success`, none is
ABSENT. `closures-autofix`, `claims-autofix` and `mutation-autofix` are all
`skipped`, so no bot commit is owed and none is coming (`ci-autofix.md`).
The head was `1f9d606dd…` when I re-read it immediately before posting (step
12), `mergeable: true`, `mergeStateStatus` not `DIRTY`; `git merge-tree
--write-tree origin/main HEAD` exits 0 with no `MERGE-CLAIM` marker.

seat: review-2071r4
Evidence: /Users/timmalmstrom/hpo-seats/review-2071r4/evidence
