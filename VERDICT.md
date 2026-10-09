Fix review: merge 941d42ff04a791e7cbdc1d6d5904c7b3203c0d8f

bus-nonce: c2fe870cb77696f057c901ae31be2641
seat: review-2010b
Evidence: /Users/timmalmstrom/hpo-seats/review-2010b/evidence

This is round 7 by reviewer turns on #2010 (1 blocked `ace05371`, 2 merge `dc4e3f13`,
3 blocked head-moved `d30236a5`, 4 merge `6eafd3a5`, 5 merge `d67d8a44`, 6 merge
`87849cd27`, and this turn). It judges **only the resolution delta `87849cd27..941d42ff0`**
under `fix-review.md` step 12: a main merge whose one conflict,
`tests/golden/claimed_drift.txt`, the `claimnotes` driver refused, so `claim-files.md`
assigns the resolution to the orchestrator, and `orchestrator.md` §2 routes the result
through a reviewer. The author of the delta is the orchestrator, so the delta's own
claims were measured, not read.

## Verdict

**merge.** The claim union is exactly right, every other byte of the delta is main's merged
content, and the head's checks are settled: 38 check-run names, nothing pending, all 17
required contexts present and green, with `mutation`'s own log showing real kills on this
PR's sites at the merged tree (§7). One thing the resolution did is not what the body says
it did — the deleted note, §4 below. It moves no instrument and invalidates no claim, so it
is a record follow-up the orchestrator owes, not a block: the `claims` class in
`.claude/workflows/web-fix-wave.js` is for a dropped, invented, stale or untrue claim, and
none of those holds here. I state it plainly rather than absorb it, and I did not go looking
for a reason to block an orchestrator's own edit — I measured what it wrote.

## 1. The union, re-derived (not taken on faith)

RESULT claim_lines_87849cd27=31 claim_lines_origin/main(d8a4bd36f)=6 claim_lines_941d42ff0=37
RESULT keys_in_common=0 (`comm -12` of the two name sets is empty; 31+6=37, all distinct)
RESULT merged_equals_union_exactly: dropped=0 invented=0 (`union − head` and
`head − union` both empty)
RESULT UX-5_lines_byte_identical=31/31 (head vs `87849cd27`); UX-9_lines_byte_identical=6/6
(head vs `origin/main`) — `diff` of the filtered sets, both empty
RESULT all_37_names_are_real_fixtures=none missing (`tests/golden/<name>.json` exists for each)
RESULT main_touched_0_of_the_31_fixtures: main's side re-recorded only `config_flow.json`
and the five `coord_*.json`; none of the 31 appears in `b2b6acd64..d8a4bd36f` — so the two
claim sets are disjoint in fixture files as well as in names.

Keeping main's six lines is the **rule-preserving** side of the choice, and I checked that
rather than only the arithmetic:
- `tests/env_drift.py:2276 excusing_claims` filters the file through `authored_claims`
  against `fork_point`, and here `merge-base(origin/main, HEAD)` **is** `d8a4bd36f` — the
  main tip — so the six lines are baseline-carried: inert, excusing nothing, going stale
  for nobody. `tests/entities.py` pins each half of that sentence as its own check names:
  "lines a branch inherited excuse no drift and go stale for nobody", "a carried claim
  line does not excuse a moved fixture" (drifted=1 even though the name is in the file),
  and "a claim line the branch wrote excuses its moved fixture".
- The alternative the driver's refusal text suggests ("keep the claims that describe THIS
  branch's diff and delete the rest") would have deleted main's live claims, and at
  merge-back that deletion lands on main — the #608/#633/#635 shape
  (`autofix-erases-claims`), which `claim-files.md`'s "lines `main` carries from earlier
  merges are inert until `stamp.py` empties them" exists to forbid.
- `claim-files.md` (current text at this head, not the reference checkout's — see §6)
  routes the hand case to the orchestrator; `tools/pr/merge_main_bot.py:121` returns
  `skip-driver-refused` when a driver refuses, and `ci-autofix.md` (current) says only
  `merge-main.yml` pushes a resolution. So a hand resolution here was the taught path,
  not a shortcut.

## 2. Every claim is true on the merged tree

RESULT claims_for_equals_VERSION: `# claims-for: 6.7.17` at `87849cd27`, at `origin/main`
(d8a4bd36f) and at the head; `VERSION` is 6.7.17 at the merge base, at main and at the
head — no stamp moved under the branch.
RESULT env_drift --claims-only origin/main at the merged head: exit 0, prints
`claims hygiene: origin/main ok` (re-derived by me, in a detached worktree at
`941d42ff0`, CI venv Python 3.14.7).
RESULT no_fixture_both_claimed_and_may-drift: 37 claim names ∩ 19 may-drift names = ∅;
`may_drift_error(...)` → None (list usable), `may_drift_coverage_error(...)` → None.
RESULT may-drift_lines_unchanged_by_the_merge: the 19 `# may-drift:` entries are
byte-identical at `87849cd27`, `origin/main` and the head (`merge_claim_defect`'s one
comment-level obligation, "a may-drift line was lost", holds).
RESULT card_claim_file_untouched_by_the_delta: `git show 87849cd27:...card_claimed_drift.txt`
== head's, byte-identical (main changed neither; the two card claims are the branch's own,
unchanged since round 6's `merge`).
RESULT the stamp caveat, for the merge queue: `claims-for:` equals `VERSION` only while
main stays at 6.7.17. If a stamp lands before this PR merges, the same file conflicts again
and the same rule decides it — union of the claim lines, both notes kept, and §4's follow-up
should be done in that resolution rather than in a later edit.
RESULT env_drift_--all_at_merged_head exit 0 (it prints the two success lines only on its
`return 0` path, tests/env_drift.py:2712-2717), one run, my detached worktree, CI venv
Python 3.14.7, `PYTHONPATH=tests/hastub`, ref `origin/main` (= d8a4bd36f, also the head's
second parent and the fork point): baseline cache MISS, 56 scenarios captured from branch
and 56 from baseline, and it printed
`NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main` /
`NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`, with
`19 MAY-DRIFT SCENARIO(S) MOVED, plan only` (reported, never failed). Log:
`evidence/envdrift_all.log`.

## 3. Per-diff: is any scenario claimed whose cause is in neither side?

No, for the file the resolution wrote. The six UX-9 lines name drift caused by main's
merged work (`#2024`/`#2016`), which is now in the tree's baseline, so they describe a
diff that is not this branch's and are inert by `excusing_claims` — the mechanism, not a
hope: the drift verdict is computed over the filtered map only, and the 31 UX-5 names are
excused by this branch's `optimizer.py`/`payload.py`/`coordinator.py` reason-publishing.
The 31 name no fixture main touched, and main's 6 name no fixture this branch touched (§1).

What I checked, concretely: the three name sets (`evidence/claims_*.bare.txt`), the
per-side byte identity, the fixture-file sets on each side, `MAY_DRIFT_ALLOWED`, the
`# may-drift:` lines, and `excusing_claims`/`authored_claims` run against the fork point
in `tests/entities.py:21015-21070`.

And then I made the merged tree answer it. In the `--all` run:

RESULT claimed_scenarios=31_of_31 — every UX-5 name printed
`CLAIMED <name>: N leaves moved (R9-UX-5: idle sub-codes, reasons only)`; 4184 leaves
across 31 scenarios; the set of `CLAIMED` names equals the set of the branch's 31 claims
exactly (`comm` both ways empty).
RESULT the_six_carried_names_are_inert_not_stale: `config_flow` and the five `coord_*`
print `ok <name> is byte-identical to origin/main here`, never `STALE claim for …`; the
log contains **no** `STALE claim`, no `unjudged claim`, no `NOT EVALUATED` line. So the
carried lines neither excuse drift (nothing unclaimed was hidden) nor are judged against
this branch (no false staleness) — the exact behavior `entities.py` pins, observed.

One carried-over-text observation that is **not** of this delta: the two card claims
(`shared_steps_hover`, `tooltip_hover`) each state their reason as
`R9-SW-3: stylesheet (quiet series tokens and .wi-quiet rules); R9-UX-5: …`. `.wi-quiet`
is already on main (24 occurrences at `origin/main`), so SW-3's half of that reason names
a change this branch no longer causes; the *names* are still earned by UX-5's own card
change, which is why `card_drift.mjs` honours them. It came in at `f6d28bb7`, was in the
tree round 6 approved, and the merge did not touch it.

## 4. The one thing that is not as the resolution was described

`git show --remerge-diff 941d42ff0` prints the driver's refusal and then exactly **one**
path, `tests/golden/claimed_drift.txt`. In that diff the resolution keeps "ours" whole
(note + 31 lines), keeps "theirs" claim lines whole, and **deletes "theirs" note block** —
main's six comment lines:

    # R9-UX-9 (#1956, #2016): this diff claims config_flow and the five coordinator
    # captures and NOTHING ELSE. The direction is ADD-ONLY: every moved leaf is a
    # key absent on the baseline (feedback_gaps, measured_heat_output_kw,
    # flow_meter_entity). No plan, schedule or solver leaf moves. These names are
    # not may-drift.

- The resolution was reported to this review as a **rewrite** of main's clause, to read
  "this set only, beside R9-UX-5's reasons-only set below". **That text is nowhere in the
  tree** — `grep 'UX-9'` at the head returns only the six claim lines, and no `beside`
  clause exists anywhere in the file. The body's `## Head` says "correcting main's clause
  that claimed a single set", which is a deletion described as a correction. Either
  account, checked against the tree, is inaccurate; the tree is the measurement.
- The instrument's own house resolution for a hand case keeps both notes: `env_drift.py`
  `_union_comments` — "Comment lines assert nothing … so keeping both sides is always
  sound. `theirs` leads so main's accumulated notes stay in their order and this branch's
  note lands last, **which is the resolution every seat here wrote by hand**."
- The file's own conventions show the "NOTHING ELSE" phrasing was never a statement about
  the whole file: `#1495` and `#1588` notes both say "claims the config_flow fixture and
  nothing else" and coexist in this same file. So the clause did not have to go; it had to
  be scoped (the wording my brief describes).
- Consequence, stated precisely and without inflation: no gate moves (no instrument reads
  prose; the six claims stay true and inert), and the six lines self-document — their own
  reason text carries R9-UX-9, the three added keys, and "no value moved". What main loses
  when this PR merges is the two issue numbers, the explicit "not may-drift" negation, and
  the note that made those claims auditable as a set. That is a content loss of another
  lane's authored text, in the one file whose whole design is to prevent exactly that.

**Owed, by the orchestrator, in the record PR that follows this merge (not a new head for
this PR):** restore main's R9-UX-9 note above its six lines, scoped as "this set only,
beside R9-UX-5's reasons-only set", and make `## Head` say "kept both claim sets; deleted
main's note" — a deletion, not a correction.

## 5. Nothing else moved (step 4 of the brief)

RESULT delta_paths=60 and all 60 are main's (`diff --name-only b2b6acd64..d8a4bd36f` ==
`diff --name-only 87849cd27..941d42ff0` as sets, both `comm` arms empty;
`tests/golden/claimed_drift.txt` is in both because main also rewrote it).
RESULT head_tree_equals_auto_merge_except_the_claim_file: `git merge-tree --write-tree
origin/main 87849cd27` → tree `0eeb3c070`; `git diff --name-only 0eeb3c070 941d42ff0` →
exactly `tests/golden/claimed_drift.txt`. Zero changes to any production or test file of
this branch's own — the strongest form of "the reviewed code is unchanged".
RESULT closures.json_is_the_driver's_own_blob: head's `tests/closures.json` == the
merge-tree blob `097bbaf025` (same object id), and its
`inert_reads["tests/harness_headers.py"]` has **538** entries — the count the
`LEDGER-MERGE: resolved` marker printed — with both sides' entries present
(`ux5_idle_codes_sites.py`, `ux5_idle_codes.py`).
RESULT delta_first_parent_commits=1 (`941d42ff0 Merge origin/main into fix/r9-ux-actions`);
the 24 `--no-merges` commits in the range are all main's, reachable only through parent 2.
RESULT structure_budgets_moved_only_via_main, and upward by main's own raise
(`max_class_loc 8817→8818`, `seam_cut_total 760→762`), not by this PR: the branch touches
no `*_budgets.json` on its own side, `mutation_budgets.json` is not in the delta,
`python3 tests/structure.py` at the head prints `STRUCTURE RATCHET PASSED`
(`seam_cut_total 762 <= 762`), and both `budget-raise-gate` runs at the head are green.

## 6. The class, opened (steps 6 and 13)

Files both sides touched — the population a clean merge can falsify — is 13, from
`(b2b6acd64..87849cd27) ∩ (b2b6acd64..d8a4bd36f)`:
`coordinator.py`, `payload.py`, `strings.json`, `translations/en.json`, `translations/sv.json`,
`www/heatpump-optimizer-card.js`, `docs/configuration.md`, `docs/dashboard-card.md`,
`tests/card.mjs`, `tests/closures.json`, `tests/entities.py`, `tests/features.py`,
`tests/golden/claimed_drift.txt`. Twelve auto-merged; only the claim file conflicted
(`merge-tree` exit 1, `MERGE-CLAIM: refused`, no other `CONFLICT`). The three files the
class bit today (`tests/features.py`, `tests/deployment_shape.py`,
`dev/audit/rounds/round4/D6/claims.py`) split here: `features.py` is in the shared set and
was checked; `deployment_shape.py` and `claims.py` are **main-only** in this merge (absent
from the branch's side), so their content equals main's, and `deployment_shape.py` carries
no census count to falsify (no `RESULT`/expected numbers in it).

What closes each, measured rather than assumed:
- `tests/features.py`: the branch's own assertions survived — 45 `UX-5` markers at
  `87849cd27` and 45 at the head; main's merge appends its #1956 advisor block and shifts
  lines, which is harmless because the file's checks are name-keyed. The run at the head:
  `1 of 3921 FEATURE CHECKS FAILED` (`evidence/features.out`), and the one failure is
  `R9-F2.1 P3: the shipped storage plan is no worse on its own objective than the
  half-price floor's plan refined under it [shipped 110.4366, seeded … 110.1297]` — not a
  UX-5 check, not a check this delta touched, and its own null arms all pass. This PR's own
  earlier review round recorded the same shape: "`R9-F2.1 P3` inside `tests/features.py` —
  red on this Mac at this head **and at origin/main**. It comes from the Mac BLAS solve, not
  from this diff" (`/Users/timmalmstrom/hpo-seats/review-2010/body.md:94`, with the same
  statement at `:28` and `:76`). CI's `fast (3.14)` at this head, which runs
  `tests/features.py`, is **success**, which is the authority per step 11; I did not run the
  25-minute main-side control locally because a green CI at the head says more than a Mac
  control would.
- `tests/entities.py` at the head: `ALL 2238 ENTITY CHECKS PASSED` (the body's figure at
  `75a6aee4` was 2214; main's merges add checks, so the direction is expected).
- The ledger: `completeness_problems`, `layout_problems`, `ledger_form_problems` and
  `triage_problems` all return no problems at the head (reviewer-owned driver
  `evidence/ledger_validators.py`, disclosed as mine per step 9 — it calls
  mutation_table's own functions, which are the ones `mutation` runs before sampling), on
  an inventory of 5936 sites. `optimizer.py` — where this PR's `idle_codes` pins live — is
  **not** touched by main, so its anchors cannot shift; `coordinator.py`'s branch rows
  (`_fold_away.*`, `_whatif_banded.*`) survive main's edit, which names neither function
  (`git diff b2b6acd64..d8a4bd36f -- coordinator.py` matches no `def` and neither name),
  and the pins are text-hash anchors, not line numbers. Deleted row
  `idle_codes.CMP_BOUND.a87d46e1` stays deleted; the triage row `a02b3552` is present.
- `payload.py`/`coordinator.py`: no duplicate top-level definition introduced by the clean
  merge (AST scan: 75 and 123 names, duplicates none).
- `strings.json`/`en.json`/`sv.json`: no duplicate key in any of the three
  (`object_pairs_hook` scan) and translation parity held — `hassfest` green at the head.
- `docs/configuration.md`, `docs/dashboard-card.md`, `tests/card.mjs`, the card: the
  instruments that would notice a false count are `harness_headers.py` (CI's `fast` runs it
  `run_always`; its rule is "a harness header's EXPECTED RESULT lines must match what it
  prints", and `claims.py`'s census lives in that closure) and `card_drift.mjs` (also
  `run.sh`'s, un-scopable per its own comment line 426). Both at the head: CI's `fast`
  prints `ALL 109 HARNESS HEADER CHECKS PASSED` and
  `ok node tests/card_drift.mjs d8a4bd36f… (4s)` → `ALL CARD CHECKS PASSED`, and
  `browser` is success. `claims.py` and `option_doc_coverage.py` are main-only files in
  this merge, and the doc edits merged under them did not falsify their counts.
- My own local `harness_headers.py` run went red and I am reporting it rather than hiding
  it: **12 of 109 failed** (`evidence/harness_headers.out`), all twelve on one harness,
  `dev/audit/rounds/round4/D7/sysid_estimator_frontier.py` — `exits 0 [rc=124 cpu=157.0s
  stderr=wall limit 900s exceeded]` plus the eleven `RESULT … matches header` lines that
  follow from `printed=None`. That harness is **not** a side of this merge: its blob is
  `ef003fc108` at the merge base, at `origin/main`, at `87849cd27` and at `941d42ff0`
  (identical), it appears in neither side's file list, and it was last touched by
  `de46d8da9` on 2026-10-07. It was starved, not broken: 157 s of CPU in a 900 s wall on a
  machine running three other seats' `features.py` and two other seats' `env_drift`
  captures alongside mine. It is my own load artifact; CI's `fast` at the head is the
  authority for that check.
- `env_drift --all` at the head is the drift verdict over the merged production pair
  itself: `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE: 56`, 31 claims honoured,
  zero stale — so the two sides' production edits (main's `coordinator.py`/`payload.py`
  keys beside this branch's reason publishing) compose without moving any fixture neither
  side claimed.

## 7. Step 11 at the new head

The App push fired the `pull_request` runs (`mergeStateStatus` is BLOCKED, not DIRTY — the
resolution did its job), and I waited for the head's check-runs to settle rather than
reading them at once (300 s polls, `evidence/checkruns_wait.log`).

RESULT required_contexts=17, none ABSENT at `941d42ff0` (ruleset 23698884
`main-protect-checks`: Analyze ×3, briefs, browser, budget-raise-gate, closure-scope,
closures, env-matrix, fast (3.14), hassfest, mutation, policy-docs, pr-contract, typing,
validate-hacs, wave-script — every one has a run at this head).
RESULT governance_contexts_run_at_the_new_head: `briefs`, `budget-raise-gate` (both twins),
`closure-scope`, `instrument-self-tests`, `policy-docs`, `wave-script`, `pr-contract`,
`typing`, `delivery-status`, `nightly-status` all completed success at `941d42ff0`.
RESULT still_running_at_posting: none. The head's check-runs are settled — 38 names, zero
pending, and no name with a conclusion other than success or skipped
(`evidence/checkruns_final_direct.txt`, read at 2026-10-09T17:59Z).
RESULT required_contexts_all_green: all 17 present, **none ABSENT**, none non-success
(`evidence/required_contexts.txt` × the table above).

The `fast (3.14)` lane at this head is **success**, and I read its log, not its tick
(job 113927534382, `evidence/ci_fast_keylines.txt`), because the answer turns on what
inside it ran:

    MODE: SCOPED -- 28 script(s) run, 5 scoped out.   (S3: the mode line, not the count)
    claims hygiene: d8a4bd36f6… ok
    NO UNCLAIMED DRIFT: 56 scenario(s) checked against d8a4bd36f…
    NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes
    19 MAY-DRIFT SCENARIO(S) MOVED, plan only
    ok  node tests/card_drift.mjs d8a4bd36f… (4s)      → ALL CARD CHECKS PASSED
    ALL 3921 FEATURE CHECKS PASSED / ALL 2238 ENTITY CHECKS PASSED
    ALL 109 HARNESS HEADER CHECKS PASSED / ALL DEPLOYMENT SHAPE CHECKS PASSED
    ALL 84 OPTIMALITY, ALL 25 BACKTEST, ALL 106 STRESS, ALL 50 GUARD PIN, ALL 64 DEBUG
    COLLECT, ALL 84 FINITE BOUNDARY, ALL 46 BOOST DRIFT — all PASSED

That is the CI authority saying, at the merged head: the claim file passes hygiene *and*
the drift gate (`--all` runs in this lane because the job sets `GOLDEN_MODE: drift`, so CI
did judge the 56 scenarios here, not only my local run), the two card claims are honoured
against `d8a4bd36f`, `claims.py`'s census still matches its header under
`harness_headers.py`, and `deployment_shape.py` passes. It also independently exonerates
my two local reds (§6: the 12 harness-header failures and the 1 features failure, both
green in CI at this head).

Every red any commit of this branch past the merge base carries is named and answered under
`## Red checks` (`mutation` with its pin history and the `PIN KILLED: 4 pinned, 0 left
unpinned` line, `mutation-autofix` ×2, `closures` ×3, `closures-autofix` ×2, `nightly-ha`
×2, `delivery-status`, `nightly-status`, `env-matrix`, `typing`, `fast (3.14)`, the
cancelled `budget-raise-gate` with its successful twins), each with a cheaper detector or a
recorded "not this pull request's to name" — that enumeration was round 6's object and the
delta adds no authored commit (§5: one first-parent commit, the merge), so no new red can
belong to the branch except one the merge itself caused, which is what the paragraph above
answers. The body's `record`/`skip red-history` arm: the `record` job is **skipped** at
this head, as it was at `87849cd27`, so the range's earlier heads were enumerated by the
body from the API at 2026-10-08T11:15Z rather than by that check; the body says so.
`nightly-status` is green at the head (the body's red it, 113492436544, was main's and is
now answered), and it is not required.

RESULT mutation_at_the_new_head: **success**, and I read the lane's log rather than its tick
(step 11: a green `mutation` can mean "no mutant survived" *or* "none was evaluated"). Job
113927534531 (`evidence/ci_mutation_joblog.txt`) prints
`MUTATION TABLE PASSED`, `0 survivor(s) of 10 evaluated = 0.0%, cap 20.0%`, and
`4621 unpinned site(s) of 5936 … 4622 at the ratchet base d8a4bd36f`, with real kills on
this PR's own sites at the merged tree — `optimizer.py:1039 CLAMP_DROP`,
`optimizer.py:1051 CMP_BOUND`, `optimizer.py:1054 CMP_BOUND`, `coordinator.py:1608 BOOLOP`,
`1620/1627 GUARD_OFF`, `notifier.py:94/97/99`, `services.py:103 GUARD_OFF` — each
`killed by tests/features.py` (or `tests/entities.py`). So main's edits to `coordinator.py`
and `payload.py` did not turn any of this branch's pinned kills into a survivor, which was
the open risk of §6's class-open list. `coverage` also completed success; it is not
required.
RESULT closures_at_the_new_head: **success** — the check that caught this branch's three
earlier `INERT READS UNDER-APPROXIMATED` reds passes on the driver-resolved
`tests/closures.json`, which is the independent confirmation that the `LEDGER-MERGE` output
matched the merged tree (I also compared the blobs directly, §5).

## 8. Two stale-reference traps this review hit, so the next seat does not

- `/private/tmp/r9-main` is checked out at `83f7ca558`, **75 commits behind `origin/main`**,
  and its working copies of `dev/governance/roles/fix-review.md`, `dev/governance/roles/fixer.md`,
  `dev/governance/rules/claim-files.md` and `dev/governance/rules/ci-autofix.md` differ from
  current main (`tests/env_drift.py`, `CLAUDE.md`, `steward/SKILL.md` are identical). Reading
  policy there reads policy that no longer binds: `claim-files.md`'s current text says "The
  merge-main bot (`ci-autofix.md`) merges `main` in where the drivers can; else merge
  locally", and `ci-autofix.md`'s current section is "A driver-file conflict: one bot merges
  it, none autofixes it" — both absent from the copy a seat gets handed. I re-read all three
  at the head (`fix-review.md` is byte-identical between head and main there, so only the
  two rules and `fix-review.md` step 7's carry clause changed). Worth saying to whoever
  prepares reference checkouts for seats: a reference checkout is a stale ref.
- The brief's premise that "the body … says the five governance contexts were absent" is not
  in the body: `## Red checks` says "Settled at the head (`commits/<head>/check-runs`, 40
  check-runs, nothing pending, 2026-10-08T20:31Z)" and the body is the round-4 re-cut. I
  checked it anyway: at `87849cd27` the check-runs API returns 41 entries / 38 names with
  every one success or skipped — nothing absent — and at `941d42ff0` the governance set
  (`briefs`, `budget-raise-gate`, `closure-scope`, `instrument-self-tests`, `policy-docs`,
  `wave-script`, `pr-contract`, `typing`, `delivery-status`, `nightly-status`) all have runs.

## 9. What carries from round 6, and what this turn did not re-do

The delta changes no production line (§5's tree equality), so round 6's measured proofs are
proofs about the same code: step 1's mutation proof (the six `idle_codes` sites, the two
deletions, the probe's B/C sections), step 2's finder harness at both ends
(`ux5_idle_codes.py`: `cases=216223`, `mismatches=0`), step 3's null controls (`differing=0`
against `differing=714`, and the triage control's 1522-vs-0), and the `## Unpinned sites`
dispositions. I did not re-run them, per step 11's "never re-run the gate or the mutation
table"; what I re-took was everything the merge could have invalidated — the ledger
validators, `structure.py`, `entities.py`, the claim semantics — and those are §2 and §6.

RESULT step_14: the delta earns no instrument number of its own. The only two figures that
moved are `tests/structure_budgets.json`'s `max_class_loc` 8817→8818 and `seam_cut_total`
760→762, and both are main's own raise, merged as content (the branch side touches no
`*_budgets.json`, `mutation_budgets.json` is not in the delta, and `structure.py` passes at
the head with `762 <= 762`). The resolution writes no production line, so `changed_lines`
draws no mutant, and the claim file is not a metric.
RESULT step_10 forward-carry: the body's `## Forward-carry` is "none" and the delta adds no
constraint on a later stage. The one thing this turn asks of anyone is a record edit by the
orchestrator itself (§4), named here rather than carried.
RESULT step_12 head: measured at `941d42ff04a791e7cbdc1d6d5904c7b3203c0d8f`; the head the
round-6 verdict carried from is `87849cd27`, the first parent here, so the reviewed code is
the reviewed code. `gh pr view 2010 --json headRefOid,mergeStateStatus` returned
`941d42ff0…` and **BLOCKED** (not DIRTY): the resolution did its job, and the
`pull_request` runs fired at this head, which is what §7 needed.
