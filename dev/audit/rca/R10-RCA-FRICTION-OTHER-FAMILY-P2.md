# R10-RCA-FRICTION-OTHER-FAMILY-P2: the owed `red-checks` fold lands; class-open and mutation-vacuous stay with their rulings (#3283, #3313, #3314)

Part 2 of the group whose part 1 merged as #3311 (`R10-RCA-OTHER-UNTAUGHT.md`).
That record named one countermeasure and left it owed: fold `red-checks` into
the `root-cause` family. This record lands it, and re-reads the two sibling
friction issues against their standing records.

**Merge base and window.** `origin/main` `51cd5ec8a42abde3c223f22e9f4a0d5f35f8844a`,
2026-11-08 21:07Z, window `v7.1.5..origin/main`. Dated figures: re-derive with
`node tools/policy/policy_lint.mjs --stats --since v7.1.5`; the per-key entries
come from `--window-cache W.json` then `python3 -I dev/audit/rca/ci-red/entries.py W.json <key>`.

## 1. #3283, `other (untaught) (family)`: countermeasure landed

Cause, state and cost test are #3311's (state (c), spelling dispersion; seven
singletons refused as noise). What was owed is its section 6 item 2. Done:
`red-checks` joins `FRICTION_FAMILIES.root-cause` in `tools/policy/policy_lint.mjs`.
Its one window instance is #3252, two entries, the unanswered `## Red checks` body.

Demonstration (`defect-root-cause.md`): `assertAcceptance` gains a pin
(`rcSpelled`): `red-checks` + `root-cause-detectable` + `root-cause-unrecorded`
on three pull requests must fold to a `root-cause` family of 3, and the same
window without `red-checks` must read 2 (null control). Run before the
one-line change: `--self-test` printed `FIXTURE VACUOUS: the derived ... root-cause
family did not fold as pinned`. After: no `FIXTURE VACUOUS`, `FIXTURE ok`.

Honest limit: at this window the effect is small. `--stats --since v7.1.5` now
prints `root-cause (family)` at 1 PR / 2 entries (below threshold 3) where it
printed no row; `other (untaught) (family)` still reads 6 PRs / 7 entries,
because the derived family does not subtract a declared family's members. The
fold makes the obligation countable beside its siblings; it does not quiet #3283.
Whether the derived family should subtract declared-family members is a distinct
change to the keying rule, not made here.

Policy-adjacent (the classifier decides which issues the cron files): approval
owed under the mandate.

## 2. #3313, `class-open`: standing ruling, no new cause

Window: 7 PRs / 10 entries (#3244 x2, #3274, #3280, #3288, #3290 x3,
#3294, #3296; counted by `entries.py`, which prints `ENTRIES 10 PRS 7`). Each entry is a reviewer naming a further seat of a class the change
left open (an unhandled sibling site, an unpinned `git fetch`, a second parser
reading the same red). That is the mechanism `R10-RCA-CLASS-OPEN.md` recorded at
32 PRs and routed to the owner as a drafted `fixer.md` sentence, "owed a ruling".
No ruling is in the tree, so nothing new is established and nothing is landed.
No countermeasure is built here: the drafted sentence is policy and the standing
record already holds the cost test.

## 3. #3314, `mutation-vacuous`: standing refusal, no new cause

Window: 6 PRs / 11 entries (#3252, #3262 x5, #3264, #3265, #3275 x2, #3301).
Every entry names reviewer mutants on `tools/` lines that survive the self-test;
none is under `custom_components/`. That is population T of
`R10-RCA-MUTATION-VACUOUS.md` section 5, whose recorded decision is "do not
build a `tools/` mutation arm now; the cost side is unknown", waiting on a
priced `tools/` mutation table. #3262 alone holds five of the eleven entries.
The window adds a datum, not a price: it does not change the refusal.

## 4. Dispositions

- #3283: countermeasure landed (section 1); the family noise verdict of #3311
  stands. Closes #3283.
- #3313, #3314: not delivered by #3311 or this part; each is an owner ruling
  already recorded and still open. Neither is closed here; the standing records
  are the disposition and the owner decides whether to rule.

## 5. Not established

Per-key PR lists in sections 2 and 3 are the cache read, not re-read from the
comments. Whether any #3262 round would have been caught by a `tools/` mutation
arm is unmeasured.
