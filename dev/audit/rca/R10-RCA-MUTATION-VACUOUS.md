# R10-RCA-MUTATION-VACUOUS: the reviewer's hand mutant survives, in two populations (#2998, #2660, #2942)

The root-cause record for the recurring-friction key `mutation-vacuous` (#2998,
refiled after #2660 closed with `R10-RCA-FRICTION-RESIDUE.md`) and for the
`mutation (family)` refiling #2942 (Carry 3 and Carry 6 of this group). It lands
one tooling change to the family map and records one refusal.

**Merge base and window.** Measured on 2026-11-06 at `origin/main`
`7e8939d38`. Window `v7.0.4..origin/main` (tag `b448d26063cd`), 517 merged PRs,
450 carrying a parsable verdict. The earlier records quote `v7.0.5` and
`92588d581` figures; they are controls here, not sources.

## 1. The count

`node tools/policy/policy_lint.mjs --stats --since v7.0.4`:

- `mutation-vacuous`: **31 PRs / 38 entries**, threshold 3.
- `mutation-survivor`: 9 PRs / 11 entries.
- `mutation (family)`: 1 PR / 2 entries, "of 41; mutation-vacuous,
  mutation-survivor file their own" (the #2410 subtraction working).

The 31 PRs, read from the first line of each `Fix review: blocked <sha>
mutation-vacuous:` comment (search over the window's merge list, then each line
read; equal to the histogram's 31): #2580, #2605, #2645, #2647, #2697, #2709,
#2712, #2832, #2873, #2916, #2919, #2920, #2937, #2968, #2978, #3004, #3016,
#3042, #3047, #3054, #3075, #3078, #3089, #3149, #3164, #3184, #3193, #3217,
#3219, #3221, #3231. Each carries a `git diff --name-only <first parent>
<merge>` over `custom_components/` (below).

Control: `#2660`'s own reading, "held: 7/8 before `662a380`, 1/1 after", does
not hold over this window. Merge dates: 5 PRs merged before `662a380`
(2026-10-25) and **26 after**, so the key did not fall; it came back at a
higher rate. 38 entries on 31 PRs is 7 repeat rounds.

## 2. Two populations, split by what the PR changes

By merge diff (a merge date is an upper bound for "heads pushed after"; the
PR's last head is not re-derived):

| population | PRs | after `662a380` | merged after `42b23e493` (#3059, 2026-11-01) |
|---|---|---|---|
| changes `custom_components/` | #2647, #2712, #2832, #2873, #2919, #2968, #3016, #3047, #3078, #3184, #3193, #3219, #3231 (13) | 12 | 6: #3047, #3078, #3184, #3193, #3219, #3231 |
| changes only `tools/`, `tests/` or docs | the other 18 | 14 | 7: #3054, #3075, #3089, #3149, #3164, #3217, #3221 |

### Population C (`custom_components/`, 13)

The reviewer's surviving mutants are deletions of guards or defaults in the
production code: `_ATTRIBUTE_TARGET_DOMAINS` losing `water_heater` (#3231),
`freq_control.py:228` GUARD_OFF (#3184), `_solve_hubs` default ruling (#3193),
`coordinator.py` `local_tz` (#3016), `diagnostics._over_age` (#2873). This is
the population `mutation-autofix` and `tests/mutation_table.py` cover.
Countermeasure C (`mutation-autofix` reddens on a site left alive, #3059,
`42b23e493`) is in force from that SHA. Six C-population PRs merged after it
still blocked on a survivor, so the autofix going red did not stop the
reviewer finding one the author had not pinned: the two are different
detectors. The autofix pins what a *driver kills*; #3231's mutant survives
every driver, the body's claim ("killed by ...") was wrong or unmeasured
(compare #3184: "survives every suite check, including the one the body names
as its killer"; #2832: "the body names 655 as killed by...").

### Population T (`tools/`, 18)

The mutants are the reviewer's hand mutants of seat tooling's own self-tests:
`ci-watch.sh sleep "$POLL_S"` (#2937), `check_scopes.py main()` exit bypass
(#3149), `prepr.sh` `merged_steps` call (#3221), `confirmGapMerge` guard
(#3217), the `cloud_relay.sh` freeze bypass (#3089). These are outside
`mutation_table.py` (which covers `custom_components/`) and outside
`mutation-autofix`: `R10-RCA-MUTATION-SURVIVOR.md` (#2961) priced them on two
instances and refused. This window has 18.

## 3. Named cause

**C:** the body asserts a pin ("killed by X") the author did not measure on
this head; the autofix's red is a late, per-site detector and the claim is
what the reviewer re-measures. `ci-autofix.md` (this PR) now requires that a
body says `pinned` only when `--pin-killed` ran on this head, which addresses
the claim, not the survivor.

**T:** a self-test for seat tooling is judged by whether it kills the plants
its author wrote, and the reviewer's *next* plant is the finding. The tools
have no mutation measurement at all (the `tests/mutation_budgets.json` and
`mutation_table.py` machinery is `custom_components/`-only), so every
reviewer round on a tool is the only mutation measurement the tool gets.

## 4. Process state

**C: (c).** `#2660`'s countermeasure (`662a380`, `fixer.md` wording) was
obeyed in form and did not produce the result; C's later countermeasure
(`42b23e493`, autofix red on a left-alive site) is a second layer. The key
did not fall after either.

**T: (a).** For tools there is no mutation process to follow or not;
`R10-RCA-MUTATION-SURVIVOR.md` found the same and refused on cost.

## 5. Cost test, re-priced

Defect cost: `R10-RCA-FRICTION-RESIDUE.md` section 2 measured
`mutation-vacuous`'s median time from block to next verdict at **111 min**
(a labelled quote from that record, 8 PRs; not re-measured). The window has
38 entries on 31 PRs; each first entry is a block that costs one fixer round
and one review round, so ~31 x 111 min = 3441 min, of which the repeat rounds
(7) are 777 min.

**T, 18 PRs.** `R10-RCA-MUTATION-SURVIVOR.md` refused a local mutation arm
for tools/ with `840 min/window` standing cost against a `644 min` defect on 2
PRs ("Local --pin-killed refused"). Re-priced at 18 PRs, the defect side is
18 x 111 = **1998 min**, against the same 840 min standing cost *if the
arm's cost scaled the same way* - which it does not know: the 840 min was
priced for `custom_components/` pins and tools have no table to pin. A cost
test needs an arm that exists; none does. The recorded decision is therefore:
**do not build a tools/ mutation arm now**; the cost side is unknown, not
high, and the defect side has moved from 644 to 1998 min. What changes the
answer is a measured cost of a tools/ mutation table, which no seat has
produced.

This is a **refusal that depends on a number nobody has**, so it is not
closed: the owner may want a seat to price a `tools/` mutation table (plants
registered per tool, the shape `r10_*_mutants.py` already has for four
drivers). Waiting on that ruling is stated in the body.

**C, 13 PRs.** 6 merged after #3059. Count for crediting the countermeasure:
entries on heads pushed after `42b23e493`; the merge date is the only data
here and over-counts. It is not credited; #3059 is not shown to have failed
either: its red names an unpinned site the author left alive, the six reviewer
mutants are survivors the author did not know existed.

## 6. #2942, the `mutation (family)` refiling: a new cause, not state (c) of the old one

The question (Carry 3): is the refiling the same cause (then the #2410
countermeasure failed) or a new one?

`#2410`'s countermeasure is the subtraction: the family counts only what no
member files. It still works as built: the family row reads 1 PR / 2 entries
"of 41", with the two filing members subtracted. Control: without the
subtraction the union would be 41.

The refiling comes from a different place, the member list. The reviewer
vocabulary produced three more spellings of the mutation obligation in this
window, none a member, each its own unfiled row:

| spelling | PRs (first-line reads) |
|---|---|
| `mutation-unpinned` | #2632, #2997 |
| `unpinned-site` | #2629, #3143 |
| `mutation-survivors` | #2917 |

None of those five is among the 31 `mutation-vacuous` or 9 `mutation-survivor`
PRs, so the subtraction takes none of them: with the three words declared
members, the family residual goes from **1 to 6 PRs** (5 + the 1 `vacuous-test`
PR it already holds) and fires at the threshold of 3. That is the shape
`R10-RCA-FRICTION-RESIDUE.md` section 4 named for `other`: the declared list
is a closed enumeration, and the spelling moves.

**Process state: (c)** for the list - the family exists, was extended once by
measured synonyms (#2561 section 5), and is obeyed; its unit is a word list
that goes stale as the reviewer coins new words. It is the declared half of
the problem the derived family `other (untaught)` (this PR, #2436) solves for
all untaught words at once; the two words that are *obligation-specific*
(mutation) still belong in the declared family, because the derived family is
one row for every untaught word and the obligation here has a name.

**Countermeasure (landed):** `FRICTION_FAMILIES.mutation` gains
`mutation-unpinned`, `unpinned-site`, `mutation-survivors`. Demonstration, measured
with `--stats --since v7.0.4` before and after: the `mutation (family)` row
1 PR / 2 entries (of 41) -> **6 PRs / 7 entries (of 46)**, over threshold, one
would-open line; controls: every other row prints byte-identically
(`policy_lint.mjs` acceptance: 267 pins, 0 errors), and the family-pinning
fixture windows (`friction-families.json`) carry no new word. It is a
tooling edit to a declared list; per `ratchet-budgets.md` it adds no policy
text.

## 7. #2998 itself

Disposition: the key is real and not `#2660`-held. Population C is reviewed
above (countermeasure in force, not credited, not refuted). Population T is a
recorded refusal that waits on a number (section 5). The family refiling #2942
is a new cause, countermeasure landed (section 6). The T-population refusal
is a recorded result of the cost test, with the number that would reverse it
named (the unpriced cost of a `tools/` mutation table); the owner may order
that pricing, and nothing else here waits on a ruling.

## 8. Not established here

- "Heads pushed after #3059" is not derived; merge dates stand in and
  over-count.
- Median 111 min is quoted from `R10-RCA-FRICTION-RESIDUE.md`; not re-timed.
- The cost of a `tools/` mutation table is unpriced.
