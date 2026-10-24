Fix review: blocked 07b83e9b28ab3a21e3a1ad8d9b38eea27ee707e0 carry-missing: not carried to R10-HEAT-METER or R10-ARCH-SHAPES
bus-nonce: b1e4aefc16fa189c3da536923ab6e2b4

Review round 1 of #2683 (R10-INPUT-STALENESS, class N-staleness, Closes #2234), at head `07b83e9b28ab3a21e3a1ad8d9b38eea27ee707e0`, merge base `d05a44c63`. Contract currency: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty. Detached worktrees under this seat's scratch directory, `python3.13`. Evidence files are under `evidence/`.

The fix itself measures as claimed. The only blocker is step 10.

## Blocker: forward-carry not in the tree (step 10, finding-propagation.md)

The body's `## Forward-carry` items 1 (R10-HEAT-METER) and 2 (R10-ARCH-SHAPES) are in the PR body only. `origin/handoff/audit-r10-roster` at `ea71518dcf718f7844ed03f8f488ae766eb9c36e` (re-fetched just before posting) contains none of `source_polls`, `INPUT_ON_CHANGE`, `_r10st_same` (count 0). Neither group's brief or `carry` holds the control: a new key in `INPUT_MAX_AGE_MINUTES` owes its on-change decision, the declaration check that refuses an undeclared key, and the rule that a dead-meter test must re-report before going silent. R10-HEAT-METER's existing carry ("Add the new key's max age through R10-INPUT-STALENESS's freshness rule") predates this PR and states neither. No `dev/programme/carries/carry-*.json` holds them either. `carry_audit.py pr 2683` prints `5 routed, 0 unrouted, 0 bad destination(s)`, rc 0. It checks that each marker names a live destination, not that the text is written there.

Repair (orchestrator/roster seat): `roster_edit.py append-carry` both items onto R10-HEAT-METER and R10-ARCH-SHAPES, with their controls. That touches no code at the head. Once the roster SHA carries them, a re-review need only confirm the carry. Every measurement below stands at this head.

## Finder's harness at both ends (step 2)

`PYTHONPATH=tests/hastub python3.13 dev/audit/rounds/round10/D14/s3/staleness_on_change.py` (sha1 6fa091e3…, in tree, identical in both trees). Base is `d05a44c63`, head is `07b83e9b2`.

- RESULT base: polling_stale_cycles=0, heat_pump_power_entity_stale_cycles=39, power newly_unavailable_entity_cycles=78 (measured_power x39, compressor_starts x39), heat_pump_mode_entity_stale_cycles=47, seams=2, perturb_unbounded power=0 mode=0; dhw/indoor/outdoor 0. (evidence/finder-base.out)
- RESULT head: polling_stale_cycles=0, power 0, power newly_unavailable 0, mode 0, seams=0; dhw/indoor/outdoor 0. (evidence/finder-head.out)

This reproduces the judge's 39/47/0 and the body's figures, at the current merge base rather than the body's `c5e1be196`.

Sweep instance probes, `probe.py <KEY>` (sha1 311f0e02…), base and head (evidence/probe.out):

- RESULT power, mode, energy, supply, return, flow: `problem=stale FAIL` at base, `problem=None pass` at head.
- RESULT controls indoor (361 min), defrost (31), wood top (61): stale at both ends, so those keys keep their bound.
- RESULT HUMIDITY: base `limit=120.0 quiet=240 -> FAIL stale`. At head the arm raises AttributeError, because it reads the deleted `coordinator.HUMIDITY_MAX_AGE_MINUTES`. I built my own replacement arm and disclose it as mine (evidence/probe_humidity_head.py). It applies probe.py's method to the head's humidity path, `InputReader.read(CONF_INDOOR_HUMIDITY_ENTITY)`, which `_indoor_humidity_value` now calls. Results: on-change 241 min -> fresh, 359 -> fresh, 361 -> stale; polled 121 -> stale, 119 -> fresh. The finder's 240-min quiet interval clears.

Class enumerator, `enumerate.py` (sha1 2028e757…): RESULT seams=29 flagged=20 at both ends; `--controls` RESULT controls_ok=True at both ends. It reads only the polling table, so it is flat by design (the body says so). I checked the body's 20-row disposition table against the enumerator's 20 flags: power, mode, energy, supply, return, flow, humidity (at head, the new `CONF_INDOOR_HUMIDITY_ENTITY`, flagged as "unknown" QUIET), MODE_LAST_GOOD, 6 pump signals, 4 wood/flue/valve/external probes, solar and PV. No seam is open.

## Failing test first, and the RCA countermeasure demonstrated (defect-root-cause.md)

I applied the head's `tests/features.py` onto the base tree `d05a44c63` (evidence/features-base-headtest.out). The run gave rc=1:
- FAIL declaration ("undeclared [...]": the base has no on-change table).
- FAIL census "all 25 age-limited keys", wrong = flow, energy, mode, power, return, supply: exactly the six InputReader instances.
- FAIL the idle power meter check ("idle stale 0.0 limit 30.0").
- FAIL the P2 stamp-reader check.
- Then AttributeError on `inputs_mod.source_polls`.

At the head: RESULT `ALL 4345 FEATURE CHECKS PASSED`, rc=0 (evidence/features-head-M0.out).

I also planted the class at the head, one plant per tree:
- P1, a new key appended to `INPUT_MAX_AGE_MINUTES` after the on-change table: RESULT 1 of 4345 FAILED, declaration "undeclared ['planted_on_change_entity']".
- P2, `CONF_POWER_ENTITY` on-change limit set back to 30.0 (the defect reinstated in the table): RESULT 3 of 4345 FAILED (declaration "equal unnamed ['heat_pump_power_entity']", the census, idle power).

The countermeasure detects the defect and a new undeclared key.

## Mutation proof (step 1), re-run by this seat, one mutant per tree, full `tests/features.py`

| mutant | result |
|---|---|
| M1 delete the `age_limit_for` wiring in `InputReader._begin` | 3 of 4345 FAILED (census, idle power, humidity) |
| M2 `reported > updated` -> `>=` | 4 of 4345 FAILED (the body's three plus `source_polls with no owner`) |
| M3 `known.add(entity_id)` -> `pass` | 18 of 4345 FAILED (matches the body's 18) |
| M4 delete the `CONF_POWER_ENTITY: math.inf` row | 3 of 4345 FAILED (declaration, census, idle power) |

CI's `tests / mutation` was still `in_progress` on this head when this was posted. Its result is not cited.

## Null control (brief carry 2)

The brief requires that a polling source still goes stale on today's bound. The census's polled arm (re-report, then silent past the polling limit) and its remembered arm (polling evidence, then a changing write) are stale on every key at the head. M3 and M2 break that arm and are killed. The finder's `perturb_unbounded` arm is 0/0 at the base, re-run above.

## Metrics earned (step 14)

`tests/structure.py` at head: STRUCTURE RATCHET PASSED. I restored only the old `_indoor_humidity_value` body at the head: RESULT `FAIL class_excess_loc 18233 > 18225 (+8)` and `FAIL max_class_loc 8479 > 8471 (+8)`. The recorded −8 is earned by the deleted humidity read. CI `arch-score` and `budget-raise-gate` are success (no raise). Mutation-ledger pins (11 files): CI `mutation` is still running, so the pins' kill counts are the fixer's. I re-derived M1–M4 only.

## Other steps

- Step 4 claims: the diff touches no `tests/golden/` file. CI `tests / fast (3.14)` (runs `env_drift.py --all`) is success at the head. I did not re-run it on Darwin.
- Step 5: `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched.
- Step 7: the body names `07b83e9b2`, which is the measured head and still the head at posting.
- Step 11: no check run on any commit `d05a44c63..07b83e9b2` concluded failure. `a23179207`'s runs are `cancelled` (superseded). At the head, `tests / mutation` and `prelude` (CI edit run 40051485860, which carries pr-contract) were still in progress. The body's `## Red checks` answers the locally predicted `mutation` (prepr 6d, the cheaper detector, repaired before handoff).
- Step 13: `git merge-tree --write-tree origin/main(15f0b5924) HEAD` rc=0. `LEDGER-MERGE: resolved tests/structure_budgets.json` (class_excess_loc 18209, max_class_loc 8449). After the merge, the gate owning that file must be re-run, as the driver prints.
- Brief carry 3 (I5-DOCS): `git grep -n ATTR_MIN_TEMP custom_components` is empty at the head.
- Step 15: the hunks stay in the owning seam (max-age tables, `InputReader`'s limit choice, the humidity freshness read). `_POLLING_SOURCES` keyed on `hass` follows `log_latch._HELD_CONDITIONS`, which already keys a WeakKeyDictionary on the input reader's `hass` in production.
- Closes #2234: delivered in code. All seven listed instances pass the finder's probes at the head (humidity by my disclosed arm).

## Non-blocking notes

- The body says the countermeasure "is the RCA's countermeasure … a declared quantity a check compares, not a comment". It departs from `dev/audit/rca/R10-N-staleness.md`'s proposed form, which declared a numeric `INPUT_QUIET_MINUTES` and refused limit < quiet. The shipped check forces a per-key on-change decision. For the 19 keys kept equal (26 − 7 overrides), the decision rests on a reason string in `_r10st_same`, with no quiet number compared. The RCA's non-vacuity clause (count includes the module `*_MAX_AGE_MINUTES` constants: DHW inlet, MODE_LAST_GOOD) is not covered. The detector is demonstrated (P1, P2, base run), so this is a wording correction for the body, owed at its next take. Carry: dismissed: body wording only; the next body take states the departure; no later stage's work changes
- Unmeasured observation: a report-on-change source with a periodic heartbeat (re-report interval longer than the key's polling limit) is classed polling after its first repeat and keeps today's limit. That is unchanged from the base and outside the finder's harness parameters. Carry: dismissed: unmeasured, and finding-propagation.md carries only a measured finding
