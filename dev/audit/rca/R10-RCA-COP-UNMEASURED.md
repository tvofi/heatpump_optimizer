# R10-RCA-COP-UNMEASURED: the COP health watch graded the model against itself

This is the root-cause seat for R10-HOTFIX-COP-UNMEASURED (PR #3297, branch
`fix/r10-hotfix-cop-unmeasured`). It follows `dev/governance/roles/root-cause.md`
and `dev/governance/rules/defect-root-cause.md`. It ran beside that fixer, never
inside it, and edits nothing under `custom_components/`.

- **Trigger:** 1, the defect reached released versions, v4.0.0 to v7.1.5.
- **Measured at:** `origin/main` `73365699a` on 2026-11-08; the brief's base
  `afc1586a4` differs from it only by #3307.
- **The fix:** read at its head `2d010b091`.
- **Reproduction:** `dev/audit/harnesses/r10_rca_cop_unmeasured.py`.

## Result

- **Cause.** One COP sample serves two different kinds of reader. The
  fold computes it once per interval: the COP scale learns from it, and the
  last measured COP and the health watch record it. The sample does not carry
  where its heat figure came from. With no heat input, `flow_meter.cop_evidence`
  infers the heat from the plan, as the model's COP times the plan's ask. With
  a thermal power entity it reads that entity's value, which may be the
  vendor's own estimate. The learner can take an inference (owner ruling, tvofi
  2026-11-07). The watch and the Health grade cannot, because they compare the
  sample with the same model it came from.
- **Process state: (c).** Three processes looked at this seam and passed it.
  They were the round-10 P5 class sweep, the R10-IDENT study's R10-COP-GATE
  group, and the vetting guards on the sample itself. Each was followed. Each
  judged whether the sample was *clean* (no frost, no immersion, enough duty, a
  draw that follows its ask). None asked where the sample's inputs came from.
- **Cost test.** A provenance step for finders costs about 10 min a round on
  the names a round adds, against an expected 1.2 to 1.5 h a round from the
  defect. It passes. A CI-wide provenance type fails the test.
- **Countermeasure.**
  - Built: the reproduction harness as a hand-run detector. It exits 1 on
    v7.1.5 and on main, 0 at the fix, and 2 on a tree that skips every sample.
  - Proposed to the owner: a method step in `D1.md` (policy, owner-gated, not
    landed here).
  - Recorded refusal: a static provenance check in CI.
- **Audit class.** No class is minted. The shape has one instance on the
  register, and the fix closes it through one decision function. The nearest
  classes are N-unmetered-reference and P11 (see section 4).

## 1. The defect, reproduced

Command: `python3 -I dev/audit/harnesses/r10_rca_cop_unmeasured.py --check <checkout>`.

The harness builds the real coordinator against `tests/hastub` and drives
`_fold_cop_evidence` with three installs:

- **null:** no heat input, and a hot-water interval whose draw (2.0 kW) equals
  its ask.
- **tuya:** both inputs are vendor estimates, with ids
  `sensor.pump_estimated_power_draw` and
  `sensor.pump_estimated_heating_output`, folded at fitted COPs 3.1, 2.4 and
  4.05.
- **metered:** plain ids, 6.0 kW of heat over 2.0 kW of power. This is the
  positive control.

| checkout | null | tuya | metered | rc | wall |
|---|---|---|---|---|---|
| v7.1.5 (`516ad1b6b`) | graded: `{(2, True): [2.5533587538536424, 1]}`, measured COP 2.55 | graded: `{(2, False): [3.1833333333333336, 3]}` | graded: `[3.0, 1]` | 1 | 0.62 s |
| origin/main `73365699a` | graded, same band | graded, same band | graded | 1 | 0.68 s |
| fix head `2d010b091` | withheld: `{}`, `None` | withheld: `{}`, `None` | graded: `[3.0, 1]` | 0 | 0.70 s |
| fix head with `if measured:` turned to `if False:` (skip control) | withheld | withheld | withheld | 2 | |

For the null install the model's COP is `compute_cop_dhw(8, 48)` =
2.5533587538536424. The inferred COP is the same float (`equal = True`), so
the band records the model itself.

The tuya band is the mean of the vendor's three fitted COPs: (3.1 + 2.4 +
4.05) / 3 = 3.1833. It carries no information about the machine.

These figures agree with #3297's own null control, which this seat re-ran
rather than read.

### Which side moved

`git log -L` on `_fold_cop_evidence` and its predecessor `_learn_measured_cop`
shows the order:

- **The inference came first.** `df7db8215` (PR #11, 2026-08-22, v2.8.0)
  wrote `observed_cop = modelled_cop * commanded / self._measured_power` and
  stored it as `_last_measured_cop` (`ATTR_COP_MEASURED = "measured_cop"`). It
  was named measured from its first line. PR #11 merged four minutes after
  opening, with no review.
- **The watch was built onto it.** `a63b576cd` (PR #50, 2026-08-26, v4.0.0)
  added `_observe_cop_health` at the tail of that fold. The comment reads
  "the same vetted sample feeds the weeks-scale health watch — this path is
  already guarded against frost, immersion, freezes and low duty, so the
  baseline inherits every filter for free". Until v7.0.5 the watch had no
  other input: every sample it ever took was an inference.
- **Real heat came later, through the same door.**
  - `f2ea21dfe` (PR #2753, 2026-10-24, v7.0.5) added the thermal power entity.
    It created `cop_evidence`, which takes heat over power when there is a heat
    reading and otherwise "the v4.0.5 inference ... kept bit for bit". Both
    branches flow into the same record call and the same watch call.
  - `7ba0c046a` (PR #2854, v7.0.5) added the heat-counter span along the same
    path.
  - Neither PR gave the thermal entity a way to say "estimate". The owner's
    Tuya install fills that slot with an estimate.

The watch did not degrade. It never had a measured input to begin with. The
class trap of reading the error text instead of the history (`root-cause.md`
section 1) points the other way here: "measured COP" read as a metered value
that the inference had leaked into, but the inference was the original.

## 2. The process state: (c)

**(c) The process was followed and did not produce the intended result.** Three
processes looked at this exact seam.

1. **The audit dimension that names the property.** `D1.md` lines 10 to 11, under
   "What you are hunting": "Ways the integration wedges, leaks, races,
   publishes stale or fabricated data as measured, or turns a corrupt input
   into a permanent failure". The property exists, so this is not (a). D1's
   method steps (lifecycle, store fuzz, staleness, executor, guards, parsers)
   never operationalise "as measured". No dimension brief turns it into a
   step either: `D2.md`'s COP item checks monotonicity, the Carnot band and
   derates, and `D8.md`'s oracle rule covers operating-state entities only.
2. **The round-10 P5 class sweep examined the watch and cleared it.**
   `dev/audit/rounds/round10/sweep-P5.md:37`: "coordinator.py
   `_cop_health_cusum` (2912) | not applicable. It is fed a shortfall against
   an empirical per-bucket, per-curve baseline (lift-normalised), not a model
   residual." The sweep ran, read the seam, and judged it by its container (an
   empirical per-bucket baseline). The samples inside that container are the
   model times ask over draw. That is not a skipped step, so this is not (b).
   The step's unit was wrong.
3. **The study found the defect, and its group carried something else.**
   - STUDY R10-IDENT Q2, recorded on #2262, said: "The sample definition
     assumes the draw follows the plan (owner slope 0.37), so COP is not
     observable without a heat meter."
   - The ruling made R10-COP-GATE "an honest 'COP not measurable here' state
     plus L3 (draw-follows check), not a gate loosening."
   - The group's brief (`dev/programme/rosters/wave-r10-groups.json`,
     R10-COP-GATE) then set the null control: "an install whose draw does
     follow the plan still reaches a COP model."
   - #2917 (`3ea1d8d48`, v7.1.0) implemented the brief as written. "Not
     measurable" became a draw that ignores its ask, and `draw_follows_plan`
     was published as a measurable state. The card says "Read from the power
     draw, which follows the plan" and shows the watch's verdict beside it.
   - The fixer and the fix review answered the brief's controls. Those
     controls asked about the learner ("still reaches a COP model") and never
     about the readers that grade.
   - The study's finding was right. Carrying it into the plan replaced "COP is
     not observable" with "the draw follows the plan", and the check-and-review
     chain then held exactly that.

The same unit passed the second door. `68dfc752a` (`docs/how-it-works.md`
1042-1046, 2026-10-31) records that "The integration cannot tell a revenue meter
from a power figure the heat pump computes for itself", and applies it to the
heat-loss learner. Nothing applied it to the thermal power slot that
`cop_evidence` reads as metered heat.

The tests pinned the inference as the specification:

- `tests/features.py` at main, "and the gap is exactly the model's own DHW law
  at the tank's temperature, not a fudge" (section "v5.3.0 — the COP learner
  uses the curve the mode implies"), asserts that the measured COP equals the
  model ratio on an install with no heat input.
- The restart and latch checks build their measured COP through `_cf_learn`,
  "intervals where the pump drew what it was told". With no heat input, that
  is the model's own COP.
- No check at main asserts that a no-heat or estimated interval stays out of
  `_cop_baseline` or `_measured_cop`.

**Why not (a).** D1 names the property, the P5 sweep read the seam, and the
study stated the defect in so many words.

**Why not (b).** Every process above was followed. A firmer "do not publish
fabricated data as measured" would have been obeyed with the same unit. Every
seat above believed a vetted, plan-following sample was a measurement.

**Why not (d).** No precondition changed under a sound process. The watch took
inferences from its first commit. The vendor-estimate door was born unmarked in
`f2ea21dfe`. It is not a later change in a sound reading.

## 3. How far the class reaches

**The rule.** Take every string literal in `custom_components/heatpump_optimizer/*.py`
whose name carries `measured` or `observed`
(`grep -ohiE '"[a-z_]*(measured|observed)[a-z_]*"'`, 23 unique names). Then
take every reader of the COP sample's three outputs: the record, the watch,
and the envelope. Trace each back to configured entities, and ask whether a
model term or an unmarked vendor estimate is among its inputs.

| seam | inputs without a heat reading | graded or acted on against the same model? | disposition |
|---|---|---|---|
| `_fold_cop_evidence` → `MeasuredCop.record`, `_observe_cop_health` (coordinator.py 5437, 5459) | model × ask / draw | yes: the watch's band and `machine_score` grade it against the model | **this defect**; #3297 gates both on `InstallCapability.cop_measured` |
| `read_heat_output_kw` (flow_meter.py 66-69) feeding `cop_evidence` | a vendor estimate read as metered heat | yes, the same readers | **this defect, second door**; #3297's `heat_pump_thermal_power_source` / `heat_pump_power_source` |
| `_fold_capacity_envelope` (coordinator.py 9379) | `thermal_kw = observed_cop * measured_power` = model × ask, at nameplate commands | yes: the envelope caps the plan with the plan's own intended heat | a learner, default off (`DEFAULT_CAPACITY_CURVE_ENABLED = False`), kept by the owner's 2026-11-07 ruling that no learner is gated; #3297 lists it among the retained learners. Not counted as an instance. |
| `MeasuredCop.residual` → `sample.cop_residual` (accuracy.py 926, coordinator.py 10138) | model × (ask / draw − 1) | no reader grades it: it is stored (`store.py` 289) and nothing in `custom_components/` or the card reads it back | a label, not a grade; #3297's gate also stops the latch it reads from on a no-heat install |
| `ObservedCOPSensor` (sensor.py 1694), its docstring "COP derived from measured electrical input" | the latched COP | published, not graded | #3297 makes it wait for metered inputs; the docstring and two doc claims stay (Carries) |
| `learning_estimated_cop` (sensor.py 673) | the model | labelled an estimate | sound |
| heat-loss and lower-floor learners (`_interval_measured_heat_kw`, coordinator.py 976) | a vendor heat estimate replayed as measured | coupled with `cop_scale` through the same ratio; not a self-comparison | N-confounded-learner's territory, already open with its own RCA |

**Reach.** One self-grading seam with two doors, both closed by the fix. One
self-referential learner, ruled retained by the owner. No other grader of a
model value was found.

**Nearest classes.**

- **N-unmetered-reference** ("a harness measuring the reference against itself
  reads sound") checks a modelled figure against no meter. Here the meter that
  would be needed does not exist on the install.
- **P11** has the oracle as a double the implementer wrote. Here the oracle is
  the model.

A class of one, with its seam closed by one function, is an instance. The next
round's judge may mint the class if the D1 step proposed below turns up a
second grader.

## 4. The cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

**cost(defect), one occurrence.**

| measure | value | how measured |
|---|---|---|
| released exposure | 73 days, v4.0.0 (2026-08-26) to v7.1.5 (2026-11-07), 134 `v*` tags | `git tag --contains a63b576cd -l 'v*'` |
| fix wall-clock, so far | at least 12.0 h: #3297 opened 2026-11-07T17:47Z, last updated 2026-11-08T05:49Z, still open | the PR's `created_at` / `updated_at` |
| fix size | 12 commits, 39 files, +700/−146, two fix-review rounds | the PR's `commits`, `changed_files`, diff and body |
| rework of a merged group | R10-COP-GATE's `draw_follows_plan` is retired by #3297 | #3297 body, item 2 |
| user cost | every metered install re-learns its bands (20 samples each, `COP_BASELINE_MIN_SAMPLES`); the owner's Health tab graded the model for the whole exposure | #3297 body, item 5 |

**P(recurrence).**

- The register holds no measured class frequency for this shape: no class
  carries it, and no `_rca` entry names it.
- The escape record holds one release escape in the programme's life,
  v2.8.0 (2026-08-22) to 2026-11-08, which is 78 days and ten audit rounds
  (rounds 1 to 9 in the register's `_source`, then round 10).
- Estimate: 0.1 per round, or about 0.4 per 30 days. The basis is that one
  escape over that span.
- The expected cost per round is 0.1 × (at least 12 h of fix plus an RCA seat
  of about 1 to 3 h, estimated) = 1.2 to 1.5 h.

**cost(countermeasure, recurring).**

- **Proposed D1 step.** A finder traces only the `measured` / `observed`
  names a round adds over the last round's list, plus any new reader of the
  COP sample. There are 23 names today. The one-off first trace of all 23, at
  an estimated 2 to 3 min each, is about 1 h and does not recur. The recurring
  cost, at an estimated 2 to 3 new names a round, is about 10 min. 10 min is
  less than 1.2 h, so it **passes**.
- **The hand-run detector.** It has no standing cost (0.7 s when run). It
  passes trivially, but it reaches only this seam.
- **A static provenance check in CI.** This would type every reading with its
  provenance and refuse a "measured" output with a modelled input. It changes
  every reader of the power and heat readings. #3297's learner list names
  eight consumers of the power reading alone. The bound in
  `defect-root-cause.md` refuses complexity worth more than the defect, and
  the fix already concentrates the decision in one function. It **fails**, and
  is recorded as refused.

## 5. Countermeasures

### Built: the detector, shown failing and passing

`dev/audit/harnesses/r10_rca_cop_unmeasured.py --check` is the detector:

- It exits 1 on v7.1.5 and on main: the defect.
- It exits 0 at the fix head `2d010b091`: fixed.
- It exits 2 on the fix head with its `if measured:` turned to `if False:`.
  That is the skip control: a tree that grades nothing cannot pass.
- The metered install grades on every tree, so the harness can see a sample.
- **Each door alone.** Two more trees are cut from the fix head:
  - **door N** reopens only the no-heat door: `cop_sample`'s no-heat arm
    returns `True`. It prints `null=graded tuya=withheld`, rc 1.
  - **door T** reopens only the estimate door: `_estimated` returns `False`
    first. It prints `null=withheld tuya=graded`, rc 1.
  So either verdict alone is enough to refuse.

**The verdict follows the named root, not the shell's cwd.** `tests/harness.py`,
at every tree measured, inserts the cwd-relative `tests` and
`custom_components` ahead of the root's own entries, so at `b8fba2c8` the
detector loaded `heatpump_optimizer` from whatever checkout
the shell stood in: from a v7.1.5 cwd the fix head read rc 1, and from the fix
cwd v7.1.5 read rc 0, a false clean. The detector now changes into the root
before importing, and exits 3 (`REFUSED`) if `harness`, `flow_meter` or the
coordinator loaded from outside it. Every rc in this section was re-taken with
the shell's cwd holding a different tree from the one measured: v7.1.5 run from
the fix tree, every other tree run from v7.1.5, and v7.1.5 and the fix head
again from a neutral `/tmp`.

**Mutation proof.** `prepr.sh`'s diff-mutant step generates no mutants here,
because `mutant_run.py` skips `dev/` (`SKIP_PREFIXES`). So the detector was
mutated by hand. The scored command requires every one of these together:

- rc 0 at the fix head;
- rc 1 at v7.1.5;
- rc 2 on the skip tree;
- rc 1 on door N and on door T;

each target run from a cwd holding a different tree (v7.1.5 from the fix tree,
the rest from v7.1.5). Unmutated, the command passes. Each mutant below was applied alone and
restored, and each fails the command, so each is killed (8 of 8):

| mutant | the edit |
|---|---|
| M-a | the verdict line becomes `return 0` |
| M-b | the skip guard becomes `if False:` |
| M-c | the null verdict is forced to `withheld` |
| M-d | the tuya verdict is forced to `withheld` |
| M-e | `null` is dropped from the verdict |
| M-f | the metered verdict is forced to `graded` |
| M-g | the `os.chdir(root)` line is deleted: the provenance refusal fires, rc 3 |
| M-h | M-g with the refusal's `return 3` made `pass`: the cwd-captured detector, v7.1.5 read as rc 0 from the fix cwd |

Before the door trees existed, M-c, M-d and M-e survived. At v7.1.5 both
doors are open, so either verdict alone refuses. The door trees are what kill
them.

It is hand-run evidence under `dev/audit/` and is wired into no gate. The
instance's barrier in CI is #3297's own section in `tests/features.py`. Its
null control is this harness's null install, pinned by value and
mutation-proven there (M1 `if measured:` → `if True:`). A second CI copy would
pin the same line twice.

### Proposed to the owner: a provenance step in D1

This is policy. Dimension briefs are in the owner's words, so it is drafted
here and not landed. It addresses state (c): it changes the unit from "is the
sample clean" to "where do its inputs come from".

> **Measured means measured.** List every value the integration publishes,
> stores or grades under a name that says measured or observed (sensor keys,
> diagnostics fields, store keys, health-watch and score inputs), and every new
> reader of one since the last round. Trace each one's arithmetic back to
> configured entities. A model term, the plan's own ask, or an entity the
> install cannot tell from a vendor estimate among its inputs is a finding. A
> watch or a grade fed by it compares the model with itself; name the model it
> is graded against.

The step belongs in D1, which already hunts "fabricated data as measured" and
has no method step that reaches it.

A planning counterpart goes with it, as worker instruction and again only
with the owner's approval. When a study rules that a quantity "is not
observable", the group brief's controls name every reader of that quantity,
grader and learner alike, rather than the learner alone. R10-COP-GATE's null
control named only the learner.

### Recorded refusal

The static provenance check in CI is refused (section 4).

## 6. Carries

These are findings outside this seat's edit scope, routed by
`finding-propagation.md` rather than filed. Each is for the orchestrator to put
into the owning stage's brief.

- **D6 / docs, after #3297 merges.**
  - `README.md:614` says Observed COP "Needs measured power". At the fix
    head it needs a heat reading over a power reading, neither an estimate.
  - `docs/how-it-works.md:1240` says the watch "compares each measured COP".
    It does, but only since the fix gave "measured" a meaning.
  - The `ObservedCOPSensor` docstring (sensor.py 1694) says "derived from
    measured electrical input".
  - #3297 changes neither doc. Its diff touches `docs/configuration.md` only.
- **The cwd capture, beyond this detector.** Any harness that takes a root
  and imports `tests/harness.py` measures the cwd's tree unless it changes into
  that root first, for the reason above. Enumerator (a superset, not a
  per-file trace): `git grep -l 'from harness import\|import harness' --
  dev/audit/harnesses/ | xargs grep -l 'sys.path'`, less those that
  `git grep -l os.chdir` also returns. Anchoring the two inserts in
  `tests/harness.py` to its own directory was not landed here: a historical
  root brings its own `tests/harness.py`, so a harness measuring v7.1.5 needs
  the change of directory regardless, and the file is imported by the whole
  suite, outside this seat's edit scope. It is the same unit this RCA indicts,
  a detector that never traced its own inputs. For the orchestrator to route
  to the stage owning `dev/audit/harnesses/`.
- **The defect's issue.** `defect-root-cause.md` asks for a short **Root
  cause** section on the defect's own issue. R10-HOTFIX-COP-UNMEASURED is an
  owner-reported hotfix with no issue on record, and this seat's brief forbids
  comments. That section is the orchestrator's to place, if an issue is
  opened: state (c) as in section 2, the cost test in section 4, and this path.

## Reproduce

Run from any cwd; the verdict follows the argument.

    git worktree add --detach /tmp/v715 v7.1.5
    git worktree add --detach /tmp/fix 2d010b091
    python3 -I dev/audit/harnesses/r10_rca_cop_unmeasured.py --check /tmp/v715     # rc 1
    python3 -I dev/audit/harnesses/r10_rca_cop_unmeasured.py --check .             # rc 1 at main until #3297
    python3 -I dev/audit/harnesses/r10_rca_cop_unmeasured.py --check /tmp/fix      # rc 0
    (cd /tmp/fix  && python3 -I "$OLDPWD"/dev/audit/harnesses/r10_rca_cop_unmeasured.py --check /tmp/v715)  # rc 1
    (cd /tmp/v715 && python3 -I "$OLDPWD"/dev/audit/harnesses/r10_rca_cop_unmeasured.py --check /tmp/fix)   # rc 0
