# RCA: fix reviews blocked `class-open`

Seat: round-11 root-cause. Trigger: the beat's bottleneck line `block-class class-open 33%
(4/12 blocks) vs 30%` over 24 h (`tools/audit/seat/bottleneck_check.py`, threshold
`block-class` 0.30 at 5 or more blocks). This seat fixes nothing. It changes no tracked tooling or
policy, because the tooling freeze is in force. The countermeasure goes to round-end triage as a
proposal.

## The four instances in the window

Each instance's first verdict line is on `verdict/<pr>`:

| PR | blocked head | what the review found open |
|---|---|---|
| #3729 (R11-SEAM-ratchets), round 1 | `5fe13702` | `_LOGGER.log(level=...)`, `logging` rebound by assignment or walrus, `_LOGGER._log` and `.handle`, reflective lookups |
| #3734 (R11-SEAM-inputs-guards) | `40328a85` | `wood_fuel.lighting_window` |
| #3728 (R11-SEAM-kernel-step) | `f6905ea0` | `wood_fuel.py:182` and `:556`: `astimezone` on a naive plan stamp |
| #3729, round 2 | `b950a390` | a sibling module's `_LOGGER` reached as an attribute, `_LOGGER` reached by the string `'_LOGGER'` (`globals()`, `sys.modules[__name__]`), `warnings.warn`, `exec` |

## Measured frequency

Commands: `git fetch origin '+refs/heads/verdict/*:refs/rca/verdict/*'
'+refs/heads/design-verdict/*:refs/rca/dverdict/*'`, then
`git log --since=2026-11-10 --format='%cI|%s'` over those refs, deduplicated on the blocked head.

- From 2026-11-15 to 2026-11-19 10:00Z there are 196 fix-review heads with a verdict: 131
  `merge` and 65 `blocked`, over 116 PRs. Fifteen distinct blocks are `class-open`. That is
  23% of fix-review blocks, 7.7% of reviewed heads, and about 3.4 a day. `class-open` is the
  largest fix-review block class. The next is `mutation-vacuous` at 15 including repeats.
- Two of the fifteen are second rounds on the same PR: #3625 (`still omits`) and #3729.
- Design reviews add 7 `revise ... class-open` verdicts over the same span. They are counted
  in the beat's line but are outside this analysis, which reads the fixer's handoff.
- Cost per occurrence is the wall-clock from a block to the next verdict on the same PR. Over
  all 21 class-open blocks since 2026-11-10 the median is **6.2 h** and the mean 7.8 h. For
  the other 64 blocks the median is 4.5 h. The seat time of the extra fixer round and reviewer
  round was not measured. It is excluded below, which favours building nothing.

## Root cause

### Cause, reproduced

**The class-closure step checks that an enumeration rule was run. It does not check that the
rule's universe contains the class.** `fixer.md` step 8 requires the fixer to "name a rule that
enumerates the class's seams (a command, not a description), run it, and put every seam it
returns in `## Figures` against its disposition". Every blocked body did this. In each case the
rule's universe came from the shape of what the fixer was given, not from the property:

- **#3734: enumerated from one finding file of two.** The body's Figures enumerate "from
  `sweep-P1.json`'s `instance_list`", because the brief's enumerator `enumerate_p1.py` was at
  no fetched ref. `dev/audit/rounds/round11/sweep-P1.md` line 40 hands `wood_fuel.lighting_window`
  to "the fixer's ... same coercion fix". `git show origin/main:dev/audit/rounds/round11/sweep-P1.json
  | grep -c lighting_window` prints 0.
- **#3728: a shape classifier that cannot see the defect.** The body's D002 rule classes 53
  sites by shape. The body itself states that the group's own defect site
  (`open_meteo._ensure_utc`'s `astimezone`) "reads by shape as an aware conversion, so the
  classifier is not the instrument for it". The review found two more sites of that shape in
  the class the rule had marked guarded.
- **#3729, both rounds: an API-surface universe for a reach property.** The round-2 rule
  "drives every callable of `logging.Logger` ... and every name in `dir(logging)`". That
  universe is the logging API as named in the module's own namespace. The property is that no
  ERROR-level emission escapes the barrier. The reach channels outside that namespace were
  outside the rule: another module's logger, string-keyed namespace lookups, alternate
  emitters and `exec`.

The fifteen blocks since 2026-11-15 fall into two mechanisms. The first is **a missed site**,
where the rule's universe omitted sites: #3614, #3625 twice, #3698, #3728 and #3734, six
blocks. The second is **an unguarded input domain**, where a new guard or refusal was not
driven over its sibling inputs: #3612, #3622, #3662, #3679, #3703, #3714 and #3729 twice,
eight blocks. #3705, pins that match nothing, fits neither.

### Process state: (c)

The process exists and was followed: `fixer.md` step 8 on the fixer's side and
`fix-review.md` step 6 ("Run the enumeration rule the body names and compare its output to the
diff") on the reviewer's. The bodies of #3728, #3729 and #3734 each name and run a rule, so
this is not (b). The step did not produce its result because its unit is "a rule was run", and
no part of it tests the rule against a known member of the class. That is the gap the step's
own text names: a rule "inherited from the finder is keyed to the instance it demonstrated
(#592's root cause)". #3728's body records a recall failure of its own enumerator and hands
off anyway, since nothing in step 8 makes that disqualifying.

Two parts differ:

- #3625 round 2 ("still omits the configured entity slot") is (b) for that round. The named
  seam was not acted on.
- In #3734 the brief named an enumerator that was absent from every fetched ref. That is a
  precondition missing at dispatch, so (d) for that instance. The fallback to the `.json`
  alone is the (c) part.

### How far the class reaches

The six missed-site blocks share the cause above. The eight unguarded-domain blocks are the
same failure applied to a predicate's domain. `fixer.md` step 2's generated-corpus clause
("a guard that classifies text by shape is driven over a generated spelling corpus") binds
text classifiers only. Its unit does not reach the type, path, archive or reach-channel domains
that #3612, #3622, #3679, #3703, #3714 and #3729 left open.

## Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock per reviewed head:

- `cost(defect) x P` for the whole class is 15/196 x 6.2 h = **0.47 h per reviewed head**.

**A. Narrow step 8 with recall at the base, and read every finding file the brief cites.**

The candidate wording: the rule, run at the merge base, returns every instance the finding
demonstrated, in the class the fix closes. A rule that misses one is not the class's rule.
The rule's sources are every finding file the brief cites, not the machine list alone. The
reviewer's step 6 reads the same line.

- It catches #3728 (the body's own admission) and #3734 (the `.md` seam). That is 2 of 15
  measured, and #3625 possibly, which is unverified. Benefit: 2/196 x 6.2 h = **0.063 h, or
  3.8 min, per reviewed head**.
- Standing cost: one extra run of a rule the fixer already runs, plus one body line. Estimated
  at 2 min per head. This is not measured. The rules in the three bodies are grep and AST
  scripts, and #3728's body already reports base counts.
- Verdict: passes, by a margin smaller than the estimate's error. It applies only to heads that
  close a class.

**B. A generic class-closure probe instrument** (finding files plus enumerator output, reporting
unnamed sites).

- Prototype on #3734's finding: extract every backticked `module.function` in
  `sweep-P1.md` that is absent from both `instance_list` and `barriered`. It flags **19
  names, of which 1 is the real open seam**. The PR body names 5 of the other 18. The rest
  belong to other seams, because the sweep hands sites to several groups. Precision is 1/19
  until the probe parses per-seam handovers, and that format is not uniform across finding files.
- Standing cost: seconds of runtime. Dispositioning 18 false hits per finding costs more than
  A's whole benefit.
- Verdict: **refused for now**. Revisit it only if the finding format gains a machine-readable
  per-group handover. A's line is then the instrument's input.

**C. A fixer step requiring an enumerated sibling-shape probe for every guard** (step 2's corpus
extended past text classifiers).

- Benefit ceiling: 8 unguarded-domain blocks of 196, which is 0.25 h per head if every one were
  caught. No generic generator of sibling inputs exists across these domains (type, path,
  archive, timezone, Python reach). The probe would be hand-built per guard, and it is the
  review's step 6 moved earlier.
- Standing cost: estimated 15 to 30 min per guard-adding head. The share of heads that add a
  guard was not measured. At half of the 196 heads, that is 0.13 to 0.25 h per reviewed head,
  against a benefit below 0.25 h once catch rate is under 100%.
- Verdict: **refused**. It is "tell the worker harder" for a (c) state, and it duplicates the
  reviewer's own step at equal or greater cost. A block that the review finds in one round,
  "every one the review found, not one per round", is the barrier working.

## Countermeasure

A only, as a proposal for round-end triage, because the policy changes only with the owner's
approval. It addresses (c) by changing the unit of step 8 from "a rule was run" to "a rule
that recalls the known instances was run". Its rung is narrowing an existing step; it adds no
refusal. Shadow measurement: the `class-open` share of fix-review blocks over the round after
it lands, against this round's 23% and 7.7% of heads. If the missed-site share does not fall,
withdraw the clause.

The #3734 instance also carries a dispatch-side miss: the brief named an enumerator present
at no fetched ref. That is a dispatch precondition (a brief's named instrument exists at a
fetched ref), not a fixer step, and it is not priced here.
