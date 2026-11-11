# R10-RCA-MUTATION-SURVIVOR: a survivor is green on the one job a seat is told to watch (#2840)

The root-cause record for the recurring-friction key `mutation-survivor`
(#2840), run apart from any fix (`dev/governance/roles/root-cause.md`). It
reads `R10-RCA-FRICTION-RESIDUE.md` first and re-derives none of it: #2410's
family subtraction, #2660's `mutation-vacuous` residue and section 7's
`ci-autofix` gaps are that record's, and are cited below only where this cause
reaches them.

**Merge base and window.** Merge base `88c6ad5bbec69bfe157e04597a74d0c9c3e4775c`,
which was `origin/main` when measured (2026-10-29, UTC). Window `v7.0.4..88c6ad5bb`;
`v7.0.4` is dated 2026-10-22T13:48:08Z.

## 1. The count, re-derived

`node tools/policy/policy_lint.mjs --stats --since v7.0.4`, rc=0, 10 m 22 s
(`mutation-survivor/stats_v7.0.4.txt`):

    STATS: 285 merged pull request(s) in v7.0.4..origin/main
         4 / 6     mutation-survivor   <- at or over threshold

The issue's snapshot was 3 / 5; one PR (#2912, 2026-10-28) has entered the key
since. The four PRs and their six entries were enumerated by a second reader,
`mutation-survivor/mutblocks.py` (every `Fix review: blocked <sha> <word>:`
comment on the window's 285 merged PRs whose word is a mutation-family member,
with the `mutation_table.py` site keys — `<file>.py:<line> <KIND>` — that its
Block section cites; output `mutblocks.tsv`, 0 `FETCH-FAILED` rows). Its
`mutation-survivor` rows reproduce the histogram's 4 PRs / 6 entries — #2579
(3 rounds, plus a second-bullet block in its round 1), #2817, #2820, #2912 —
so the two readers agree.

## 2. The brief's premise holds for two of the four

The brief's subject is "survivors that `tests/mutation_table.py --pin-killed`
would have reported before handoff". `--pin-killed` drives only the candidate
sites `mutation_table.py` inventories, which are `custom_components/` code
(`fixer.md` step 2: "its lane mutates `custom_components/` only; a `tools/`
site needs an in-tree mutant harness"). Split by what the Block cites:

| PR | entries | surviving mutant | in `--pin-killed`'s reach |
|---|---|---|---|
| #2579 | 3 | `tools/audit/seat/review_strength.py`: hand mutants against its own self-test (a 600-line cut, a slice, a regex's inner `-`, a nonce slice) | **no** — `tools/` |
| #2820 | 1 | `tools/policy/friction_issues.mjs`: first-write-wins on a shared census key | **no** — `tools/`, JavaScript |
| #2817 | 1 | `coordinator.py:6303 GUARD_OFF`, `coordinator.py:6331 GUARD_OFF` | yes |
| #2912 | 1 | `config_flow.py:3490 RETURN_DEL` (equivalent) | yes |

**#2579 and #2820 are not this subject.** Each is a reviewer's hand mutant on an
instrument's self-test, outside any generated class: #2579's round 5 records
that the fixer's own class sweep of 2333 mutants did not contain the surviving
edit. No mechanical detector in the tree reaches them, and the cheapest one
that did is the adversarial review that found them — `defect-root-cause.md`'s
"does not qualify" case. Recorded, nothing built (section 6).

**#2817 and #2912 share one cause, and it is not in `tests/mutation_table.py`.**
`--pin-killed` reports both correctly; the defect is in what tells a seat it
has to run it.

## 3. Named cause

Both bodies disposed every added `custom_components/` site as "pinned by
`mutation-autofix`" — #2817 all 25, #2912 24 — and in both a site no driver
kills was among them. `mutation-autofix` cannot pin a survivor, and **every path
a survivor takes through it is green**:

- `measurement()` (`tests/mutation_table.py`) returns `measured` when any site
  was killed and `skip-nothing-killed` when none was; the survivors' count,
  which the base program prints in `PIN KILLED: N pinned, M left unpinned`, is
  parsed for N and discarded for M.
- `apply_pins()` returns `changed` once any kill is written, whatever is left.
- `closure.AUTOFIX_QUIET["mutation-autofix"]` holds `changed`,
  `skip-not-allowed`, `skip-not-unpinned`, `skip-nothing-killed` and
  `skip-head-moved`: the job is red only when a measurement failed.

So a survivor leaves `tests / mutation` red indefinitely and `mutation-autofix`
green. `ci-autofix.md`, as it stood at the merge base, told the seat to **wait**
on `tests / mutation` refusing unpinned sites, that the wait "holds only while
the job reports it is repairing", and to run `--pin-killed` "when
`mutation-autofix` goes red". The one trigger the rule names cannot fire for a
survivor; the wait has no end for one. The fact is printed — the
`tests / mutation-pins` log marks each one `-- lives` — but nothing a seat is
told to read says so.

Timelines (check runs, `mutation-survivor/pinsbefore.sh`):

- **#2817.** CI measured head `4fbe4c6a5`: `tests / mutation-pins (1..6)`
  concluded by 16:39:51Z — the reviewer quotes them listing
  `6278 GUARD_OFF -- lives` and `6306 GUARD_OFF -- lives`
  (`ev/ci_mutation_pins_4fbe4c6a5.txt`; the job logs answer 403 to this seat) —
  and `mutation-autofix` concluded **success** at
  16:41:11Z. The reviewed head `3b437b851` and its body ("all 25 pinned by
  mutation-autofix") came at 17:02Z, after the measurement that refuted it.
- **#2912.** The prior verdict merged `cc0510ee` on the condition that
  `tests / mutation` turn green; the bot's `ci: pin killed mutants` head
  `4fc6a4c51` pinned 23 of 24, `tests / mutation` stayed red on the 24th, and the
  reviewer blocked it at 18:54:48Z.
- **#2832** (same cause, filed under `mutation-vacuous`): 8 of 25 added
  `legionella.py` sites `-- lives` in the head's own `mutation-pins` shards,
  `mutation-autofix` **success**, body "every one of the 25 pinned by
  `mutation-autofix`"; blocked 6 minutes after the shards concluded.

## 4. Process state: (c)

The process existed and was obeyed. `fixer.md` step 2 lists "pinned by
`mutation-autofix`" as a disposition; `prepr.sh` step 7d (`unpinned_line`)
checks only that each listed key has a line; `ci-autofix.md` keyed the seat's
own action on `mutation-autofix` going red. Each seat did what the text said,
and the result the text exists for — no survivor reaching review — did not
follow, because the signal the text keys on is quiet by construction for the
case it must catch. It is not (b): no seat skipped a step; the "firmer
instruction" a (b) reading suggests would have told the #2817 fixer to watch a
job that was green. It is not (d): `AUTOFIX_QUIET`'s mutation tuple has held this form since
`dc66cc878` (2026-09-24), before the window, and nothing under it changed.

## 5. How far the class reaches

Rule: `mutblocks.py` over the window's 285 merged PRs, every mutation-family
block whose Block cites a `mutation_table.py` site key. Five PRs:

| PR | word | disposition |
|---|---|---|
| #2817 | `mutation-survivor` | this cause (body: all pinned by `mutation-autofix`) |
| #2912 | `mutation-survivor` | this cause (24 left to `mutation-autofix`, one equivalent survivor) |
| #2832 | `mutation-vacuous` | this cause (8 of 25 live; body: all pinned) — and it is the one post-`662a380` entry `R10-RCA-FRICTION-RESIDUE` section 6 left as #2660's "residue 1" |
| #2632 | `mutation-unpinned` | sibling, recorded by `R10-RCA-FRICTION-RESIDUE` section 7: a killable site whose CI pin run timed out, so no bot pin came |
| — | (not a verdict) | #2834, `R10-RCA-FRICTION-RESIDUE` section 7: ten sites written "pinned by `mutation-autofix`" undriven, two survivors, refused by CI |

Null control on the enumerator: the same regex finds no site key in #2579's or
#2820's blocks (`sites=0`), whose survivors are `tools/` code — so the rule
separates the two populations rather than matching every block. Before the
window, #2379 (2026-10-18, `mutation-untriaged`: "3 added sites survive every
driver after mutation-autofix") is the same shape under a third word.

**The cause spans four class words** (`mutation-survivor`, `mutation-vacuous`,
`mutation-unpinned`, `mutation-untriaged`) and one friction rule id
(`ci-autofix`), which is why no key held it: #2840 filed two of its instances
beside two that are not.

## 6. Cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

**P(recurrence).** Of the window's 285 merged PRs, 28 change
`custom_components/*.py` (`git diff --quiet` over each first-parent merge's
three-dot diff; the same loop over `nonexistent/*.py` counts 0). Four of the 28 —
#2817, #2832, #2912, #2834 — carried a survivor left to `mutation-autofix`
past handoff: **4 / 28 = 14 %** of the PRs that can produce one. #2379 shows it
in the previous window too.

**cost(defect).** Block to the PR's next verdict: #2817 91 min, #2912 161 min,
#2832 496 min (overnight); median 161 min, plus one adversarial review round
each. #2834's owner names its own cost: a CI round and a fixer round.

**Candidates.**

- **A. Run `--pin-killed` before every handoff that adds a site.** Measured at
  #2817's reviewed head against its base `f54f40cc1`, `--jobs 4` on a
  4-core container: stopped at the seat's 30-minute limit with **0 of 29**
  mutants decided — the null control and the baselines alone took 284 s
  (`env_drift.py`), 463 s (`features.py`) and 505 s (`entities.py`)
  (`mutation-survivor/pin2817.txt`). CI's measurement of the same diff at
  `4fbe4c6a5` took six `mutation-pins` shards 30.9 to 77.9 min each,
  **366 runner-minutes**, 78 min wall clock (check-run start and completion
  times). Even the local lower bound, 30 min × 28 PRs = 840 min a window,
  exceeds the whole defect, 4 × 161 min = 644 min, before it is weighted by
  anything. **Refused**: it costs more than it prevents, and repeats a
  measurement the CI shards already make on every push.
- **B. Correct the rule (landed here).** Zero seconds per run. The policy
  corpus does not grow: `ci-autofix.md` stays at its token cap (1469 / 1469),
  paid by wording trims that move no claim.
- **C. Make the survivor loud (carried).** `mutation-autofix` reddens when its
  measurement leaves an added site alive, naming the site in its summary line.
  Zero seconds per run: the same job, reading a number it already parses.
  Owned by `R10-FLY-LEDGER-SAMPLE`, the group holding `tests/mutation_table.py`
  and #2840's own measure-first carry.

## 7. Countermeasure

**B, landed.** `dev/governance/rules/ci-autofix.md` (generated copies by
`node tools/policy/rules_sync.mjs`) gains a fourth "path that ends green
unrepaired":

> **A survivor.** `mutation-autofix` pins kills only, so a site no driver kills
> leaves it green, `tests / mutation` red for good (#2840). `pinned by
> mutation-autofix` is a prediction until a `mutation-pins` log or
> `--pin-killed` kills the site; a `-- lives` line is the seat's.

It addresses state (c) at its unit: the rule's description of what the bot
signals was false for this case, and is now true. It would have changed #2817,
whose reviewed head and body came 22 minutes after the shards printed `-- lives`, and
#2832, whose body's claim was refutable from the head's own shards. Policy
change under the orchestrator's mandate, scope `all` (the brief).

**C, carried** to `R10-FLY-LEDGER-SAMPLE`, with its acceptance: replayed on
#2817's `4fbe4c6a5` measurement (`PIN KILLED: 24 pinned, 2 left unpinned`
shape), the job is red and its summary names `coordinator.py:6278 GUARD_OFF`
and `6306 GUARD_OFF`; on a measurement with `0 left unpinned` it is green
(`changed`); a `skip-head-moved` measurement stays quiet. That carry also
answers the group's #2840 item: the survivors share a cause, and it is the
autofix's status vocabulary, not `--pin-killed`. Survivor *triage* stays manual
(`ci-autofix.md`): C reports, it does not dispose.

**Refused, with the reason recorded:**

- A (section 6).
- A check that a body's "pinned by `mutation-autofix`" row is backed by a
  measurement, in `prepr.sh` step 7d: at a first handoff no measurement exists
  (a handoff ref runs no job), so the arm could only refuse the prediction the
  rule now names as one, or demand A.
- A mechanical detector for #2579's and #2820's shape: no generated class reached
  either surviving edit (#2579 round 5's 2333-mutant sweep), so the cheapest
  detector is the review that ran.

## 8. Carries

- `Carry: R10-FLY-LEDGER-SAMPLE` — countermeasure C and its acceptance, and the
  answer to that group's #2840 carry (section 7).

## Evidence

`dev/audit/rca/mutation-survivor/`:

- `stats_v7.0.4.txt` — the `policy_lint --stats --since v7.0.4` run at
  `88c6ad5bb`.
- `mutblocks.py`, `mutblocks.tsv` — the window's mutation-family blocks with
  their cited site keys (section 5's enumerator).
- `pinsbefore.sh` — per-commit `mutation-pins` completion and `mutation-autofix`
  conclusion for a PR (section 3's timelines).
- `pin2817.txt` — `--pin-killed` at #2817's reviewed head (section 6, A).
