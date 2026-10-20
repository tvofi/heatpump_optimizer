Fix review: merge 478cc27efd03d59d97899cff0d67f2e912ce7918

bus-nonce: 4162309a01046b05b79c53f3e102f4aa

## Head

Round 2. Measured `478cc27efd03d59d97899cff0d67f2e912ce7918` in a detached worktree at
`/Users/timmalmstrom/hpo-seats/r10s3/rev-2485-r2`; `origin/main` is `76bb45628745` and the merge base
is `origin/main`, so the PR's own diff is the three-dot one. The PR head read from the API at
13:30Z, again at 13:39Z and again immediately before posting at 13:49Z is `478cc27e`. The body was
read from the pull request
(`gh pr view 2485 --json body`, sha256 `b074690674fc…cee4`), not from any file the fixer kept.

## The round-1 block is cleared, and by the checker's own run

`## Forward-carry` in the live body is exactly `none.`; the #2445 stamp-time items moved to the
opening paragraph and to the R10-STAMP roster entry (verified below). Against the live body:

    python3 -I tools/audit/carry_audit.py check --body body-at-head.md
    CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)   [exit 0]

`pr-contract` at this head, read from `/repos/tvofi/heatpump_optimizer/commits/478cc27e/check-runs`
(never `gh pr checks`): the push-time run `39427351196` (13:04:44–13:05:06) failed on the old body;
the body edit at 13:29:44 fired run `39430873112` (created 13:29:48), which concluded **success** at
13:30:17. Its own log states `red checks the body must answer: nightly-status`,
`PR-BODY: 0 error(s) in /tmp/pr-body.md`, `CARRY-AUDIT: 0 finding item(s)` and
`no version edit: origin/main...478cc27e moves none of VERSION, the manifest version or a notes
heading`. A green run over the edited body, not a red hidden behind a tick. All of this head's
workflows had concluded by 13:48:28Z, when `closures` completed success; the Tests run's only
failing job is `nightly-status` (job 118643700213), and the only failing `pr-contract` run is the
push-time one the edited-body run superseded.

## Direction and derivation — re-measured, not inherited

The diff removes `tests/stress_budgets.json`'s `coverage_floor_override` (`floor` 18,
`calls_floor` 6); nothing else in any budget file moved. It is a withdrawal, not a raise:

- `coverage_floors` accepts the override only through `lowers()`, which is one-sided by
  construction (`tests/stress.py`: `isinstance(v, int) and not isinstance(v, bool) and 0 < v < literal`).
  I ran the controls: floor 45 (≥ the literal 40) -> `(40, 15, None)`; floor 0 -> `(40, 15, None)`;
  no `cites` -> `(40, 15, None)`; floor 18 with `calls_floor` 6 -> `(18, 6, cites)`; floor 18 without
  it -> `(18, 7, cites)` (the share rule, rounded up). The override could only ever lower the floors.
- At this head, from the committed function and table: **54 scenarios, 20 families,
  `(40, 15, None)`**. The same table with the override restored returns `(18, 6, cites)`.
- Budget gate at this head (`--base origin/main --head 478cc27e --pr 0`):
  `RESULT budget_raises=0 count` / `PASS: no budget raise; no owner review is owed`.
- The mutation proof, as the gate's own comparison sees it: base = this head's tree, head = the same
  tree with the override re-added (my throwaway commit `caa477d5`) -> two
  `RAISE … coverage_floor_override: override added at N (absent is the strict state)` and
  `RESULT budget_raises=2 count` / `REFUSED`. Against `origin/main` as the base the same mutant shows
  no change, because it is byte-identical to the base — the gate compares base against head, so that
  arm is a null control, not a mutation. The gate self-test separates the directions and passes
  `239 checks, 0 failed`, including `the override withdrawn is routine (the literal is stricter)`.
- Class check: the only budget leaf the gate classifies `OVERRIDE` is `coverage_floor_override`
  (`tests/stress_budgets.json`), and `git grep coverage_floor_override -- '*budgets.json'` at this
  head returns nothing. The class is one seam and this PR closes it; no seam is left unnamed.

## §Response to the round-1 verdict

1. *`## Forward-carry` grammar* — a genuine `none.`; `carry_audit` returns 0 items. Answered in the
   body and confirmed by `pr-contract`'s green run.
2. *`pr-contract` red named and answered* — `## Red checks` names it and gives the cheaper detector
   (`carry_audit.py`, seconds, local, already in `prepr.sh`); the body records that it was not run
   before the push, which is the `defect-root-cause.md` question answered rather than restated.
3. *`## Head` re-pointed* — says `478cc27e`, the measured head.
4. *The block's own paragraph* — the #2445 stamp-time substance is in the opening paragraph and its
   destinations are in the R10-STAMP roster entry; see Forward-carry.

Nothing round 1 raised is answered only in a commit message.

## Red checks

- `nightly-status` failure at 13:05:54–13:06:07 — **not this head's**, and exempt: it grades `main`
  and reads Actions run metadata, not this diff (the workflow's own red list agrees: `red checks the
  body must answer: nightly-status` is printed for the body to ignore by the exemption). It is the
  only failing job in this head's Tests run; every other job, `closures` included (13:32:37–13:48:28),
  concluded success.
- The body's `## Red checks` also records its local `tests/stress.py` reds (shoulder economics, and
  the `typical_slab/shoulder` RSS on the after run) with a cheaper-detector answer: CI's
  canonical-environment lane, standing cost a 15–20 minute local duplicate. I did not re-run the
  solver; this head's `fast (3.14)` run passed, and `tests/closures.json` maps
  `tests/stress_budgets.json` to `tests/entities.py`, `tests/harness_headers.py` and
  `tests/stress.py`, so the scoped `fast` lane is the run that settles them at this head.
- `mutation` is green; the diff writes no production line, so no mutant is drawn — the PR's mutation
  evidence is the budget gate's two directions above, which I re-ran.
- `closures` at this head concluded success at 13:48:28Z; the Tests run's only failing job is
  `nightly-status`.

## Forward-carry

`## Forward-carry` is `none.`; the branch owes no new carry. The stamp-time items the opening
paragraph names are in the head tree's R10-STAMP roster entry
(`dev/programme/rosters/wave-r10-groups.json`, the group's `carry` array, lines 4053 and 4056–4058):
the #2368 override withdrawal this PR performs, the flat-price control ruling to record in the
release notes, the Pi `process_time` after the stamp, and the invariant-not-a-count instruction —
each stated as owed at/after the stamp, i.e. as a precondition, not an opportunity.

## Usual

- Claim files byte-identical to the merge base; `env_drift.py --claims-only origin/main` ->
  `claims hygiene: origin/main ok`. Suspension notes at this head: 0 in both claim files, with the
  positive control on `daca95c5d^` reading 19.
- `VERSION`, the manifest version and the `RELEASE_NOTES.md` heading are untouched (my three-dot diff
  shows only the three files below; `pr-contract`'s own version step agrees).
- `structure.py` -> `STRUCTURE RATCHET PASSED`; `fold_ledger.py check` -> 0 violations;
  `tests/closure.py selftest` -> `ALL 124 closure shrink pins PASSED`; `tests/layout.py` ->
  `layout self-test: ok`; `git merge-tree --write-tree origin/main HEAD` -> rc 0, no conflict.
- Diff is three files against the merge base: the override removal, the `landed: "ecdeb42c (#2441)"`
  ledger field (that commit is `Merge pull request #2441 …`, on main, and `fold_ledger` accepts it),
  and the PR's own delivery row. The delta from round 1's head `22ed5ed7` to this head is #2465's
  file set only — production files, `tests/features.py`, `tests/closures.json`, the mutation ledger
  and `delivery/2465.md` — and does not touch this PR's three files, so round 1's substantive
  findings carry unchanged.
- Figures I could not re-derive and did not adopt as verified: the two whole-run stress CPU medians
  (0.928x / 0.985x), the RSS figures, and the fix-head scoped-gate counts (`3 script(s) run`, the
  2358 entity checks). They are local runs, not cheap to repeat, and CI's lanes at this head are the
  authority for the suite.

## RESULT

    RESULT pr-contract: push run 39427351196 failed 13:05:06; edited-body run 39430873112 succeeded 13:30:17
    RESULT carry_audit check --body (live body) = 0 finding item(s), 0 unrouted, 0 bad destination(s)
    RESULT budget gate at 478cc27e: budget_raises=0, PASS; mutant (override added) = 2 RAISEs, REFUSED
    RESULT floors at 478cc27e: 54 scenarios, 20 families, (40, 15, None); mutant (18, 6, cites)
    RESULT lowers() one-sided: floor>=40, floor=0 and missing cites all fall back to (40, 15)
    RESULT claim files byte-identical; suspension notes 0 (control 19); VERSION/manifest/notes untouched
    RESULT structure PASS; fold_ledger 0 violations; closure selftest 124 pins; layout ok; merge-tree rc 0
    RESULT nightly-status red but exempt; no other red at this head; closures succeeded 13:48:28
    RESULT head re-read at 13:49:34Z: still 478cc27e; live body sha256 unchanged (b0746906…)
    RESULT delta 22ed5ed7..478cc27e = #2465 only, does not touch this PR's three files

Not re-run locally and left to CI at this head: `tests/stress.py`, `tests/harness_headers.py`,
`tests/entities.py` (the scoped set), and the full gate.
