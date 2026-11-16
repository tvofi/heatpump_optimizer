R11-ADVISOR-MEASURES-P2: the advisor harnesses now classify a schedule figure of 0 instead of counting every 0 as a miss (carry 2). Carries 0 and 1 are re-measured at this base: no figure has a wrong sign against a truth that resolves its sign, so no production line or card sentence changes.

**Carry 2 (r11-valve-reference item s2), built.** `r10_advisor_steady_seams.py`'s `fields` arm counted `base is None or base * want <= 0`, so every 0 counted as a miss. On r11-valve-reference's fixed single-zone valve house, the one remaining 0 (`night-1` asked at 21:00) is a correct 0: the room coasts above both night setpoints, so the thermostat draws nothing there. The new `zero_kind` reads `reference_day`'s own second pass (same weather, step clock, comfort bounds and two thermostat passes) on each distinct day of the week, for both schedules:
- `idle`: neither schedule's thermostat draws on any step whose setpoint the ask moves. This is a correct 0.
- `binds`: otherwise, including a thermostat held at the pump's maximum or at the valve's ceiling both ways.

The `fields` arm now prints `missed` as the sum of pair rows, rows against the ask, and 0 rows where the ask binds, plus the correct-0 count beside it. The `weekday` arm (r10) and the `valve` arm (r11_advisor_measures.py) counted 0s apart from misses already. They now also print how many of those 0s are `idle`. No count in either arm changes.

Alternatives considered:
- Keep the old count and annotate the s2 row by hand. Rejected: the count is what later stages read, and an annotation is a figure keyed to one instance.
- Classify a 0 by `live_kwh == sim_kwh`. Rejected: a thermostat saturated both ways also gives equal energies, and that is the defect r11-valve-reference fixed (19 such rows at this base, below).

**Carries 0 and 1, re-measured.** Production moved between #3674's measurement base (e352724335) and this base (c82f014a63): `git diff --stat e352724335 c82f014a63 -- custom_components` shows 10 files. Every `asks`, `valve`, `pv`, `loop` and `pvloop` figure #3674 states reproduces here (Figures). So #3674's dispositions stand, and so does the card text it landed in `docs/dashboard-card.md`:
- the weight and floor scatter by the hour asked;
- the hot-water sentence;
- the valve's near-zero disclosure;
- the panels' lower-end sentence.

Two readings need stating:
- `loop`'s `dhw_setpoint 55 to 50` truth is +23.9 against a half-degree null of −23.1. That is a single-sample null with a margin of 0.8, so the sign is not resolved. The card makes no sign claim for a hot-water setpoint ask.
- The `valve` arm's four Friday 0s on the two-tank valve house are all `wkday+1` (22 → 23 °C) at 01, 03, 05 and 23:00. All four classify `binds`: the valve tops the rooms out at 22.10 and 22.07 (the `holds` line). The card already discloses this case ("reads at or near zero, on either side of it"), and that arm counts no 0 as a miss.

## Head

prepr: passed rc=0 at c03ab4b85fd9a08ce6ecc072670a223018a808db (scoped: `PREPR_SKIP_CLOSURES=1`, the diff selects no script; `PREPR_SKIP_CODE=1` on the final run, a body-only delta since the first full run, whose only refusals were the body's).

`c03ab4b85fd9a08ce6ecc072670a223018a808db`, merge base `c82f014a639954b0f8930f29cf30fed3f0b20a6a` (the base the brief gave). origin/main was at `5854e4f69e361d841d7590ae0f868eea6758655f` at 2026-11-16T23:34Z, and `git merge-tree --write-tree origin/main HEAD` reports no conflict. The head changes only two harness files, so every base figure below holds at the head except the counting lines this diff changes. Those were run at the head.

## Mutation proof

n/a for `prepr.sh`'s draw: the diff adds no production line, and both changed files are under `dev/audit/harnesses/`, which the draw excludes. The classifier's predicate is mutated by hand instead. The probe calls `zero_kind` for `night-1` at 21:00 on the single-zone valve house, on a scratch tree of this head's harness over c82f014a63 merged with r11-valve-reference's head c60b23450f. Each mutant is applied by `sed`, the probe is run, and the file is restored (`cmp` confirmed):
- Unmutated: `figure 0.0 zero_kind idle`.
- M1, the moved-step mask dropped (`np.asarray(power)[moved] > IDLE_KW` → `np.asarray(power) > IDLE_KW`): `binds`. Killed.
- M2, every step counted as moved (`moved = targets[0] != targets[1]` → `targets[0] == targets[0]`): `binds`. Killed.
- M3, only the live side's thermostat read (`zip(sides, comforts)` → `[:1]`): `idle`. **Survives on this row**, because both sides are idle there. M3 would misread only a 0 where one schedule heats on a moved step and the other draws nothing, with equal day energies. No fixture measured here produces such a row, so the both-sides read is not pinned by a value.

## Null control

- Saturated thermostat, where a 0 is a miss: the single-zone house with `max_electrical_power` 0.05 kW, `day-1` and `day+1` asked at 09:00, reads `figure 0.0 zero_kind binds` for both. The default house reads −56.61 and +68.16, also `binds`.
- c82f014a63 itself, before r11-valve-reference fixes the single-zone valve reference: `fields valve, one tank` reads `missed 24` at the head against `at 0 or against the ask 24` at the base. The 24 split as 5 against the ask and 19 zeros that bind, with no `idle` zeros. So the classifier does not excuse the 0s the reference defect produced.
- Output this diff does not touch: the `largest move of the figure by start` column of every `fields` line, the `valve` arm's per-day rows and its `holds` lines. `diff` of those lines between base and head printed `LARGEST-MOVE COLUMNS IDENTICAL`, `VR LARGEST-MOVE COLUMNS IDENTICAL` and `VALVE PER-DAY ROWS AND HOLDS IDENTICAL`.

## Figures

All runs from the tree root with `PYTHONPATH=tests/hastub:tests:custom_components`. Each money figure is a month's money in the fixture's price unit, printed by the arm named.

- Carry 2, `python3 dev/audit/harnesses/r10_advisor_steady_seams.py fields`, on c82f014a63 merged with c60b23450f:
  - before this diff: `valve, one tank` rows 72, `at 0 or against the ask 1`;
  - after: `missed 0 (reading the pair 0, against the ask 0, at 0 where the ask binds 0)`, `a correct zero 1`, the `idle` row being `night-1 21:00`.
  - The other three fixtures read 0 before and `missed 0`, with no zeros, after.
- Same arm at c82f014a63 (base) and at the head: `valve, one tank` `at 0 or against the ask 24` at the base. At the head it reads `missed 24 (… against the ask 5, at 0 where the ask binds 19)` with no `idle` zero. The other three fixtures read 0 at both ends.
- `python3 dev/audit/harnesses/r10_advisor_steady_seams.py weekday` at base and head: Friday rows 96, against 0, rounding to 0.00 0 at both ends.
- `python3 dev/audit/harnesses/r11_advisor_measures.py valve` at base and head: with weekend comfort set, days against the ask 7 and days at 0.00 0. Friday: rows 96, against 8, at 0.00 4, of them idle 0 (head). Rooms held at a 23.0 setting: 22.10 and 22.07.
- Carry 0, `python3 dev/audit/harnesses/r11_advisor_measures.py asks` at c82f014a63: rows against the ask out of 18 are
  - hot-water setpoint 55 → 50: 8;
  - 55 → 60: 10;
  - hot-water minimum 45 → 50: 0 (+58.0..+102.0);
  - weight 5 → 2.5: 6;
  - weight 5 → 10: 5;
  - floor 17 → 16: 8;
  - floor 17 → 18: 3;
  - half-degree null range −11.2..+7.1.
- Carry 0, `python3 dev/audit/harnesses/r11_advisor_measures.py loop` at c82f014a63, closed-loop truths:
  - hot-water minimum +99.8;
  - setpoint 55 → 50 +23.9 and 55 → 60 −0.8;
  - weight −17.3 and +7.9;
  - floor +3.8 and +10.9;
  - null −23.1.
- Carry 1, `python3 dev/audit/harnesses/r11_advisor_measures.py pv pvloop` at c82f014a63:
  - `pv`: the thermostat priced at each step's surplus-aware price lies outside the estimate's range in all 8 rows.
  - `pvloop` with surplus, day−1: truth −25.2, ends −63.2 and −8.0. Day+1: truth −10.5, ends +73.6 and +9.3.
  - `pvloop` null, day−1: truth −24.9, ends −63.2 and −26.8. Day+1: truth +19.2, ends +73.6 and +31.0.
  - The own-price end is the closer one in all four rows.
- Structure ratchet: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.

<!-- figure-block: scope-line mb=c82f014a639954b0f8930f29cf30fed3f0b20a6a head=c03ab4b85fd9a08ce6ecc072670a223018a808db -->
~~~text
MODE: SCOPED -- 0 script(s) run, 33 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none

## Forward-carry

- R11-VALVE-REFERENCE's body states the `fields` arm's `valve, one tank` count as "24 of 72 rows at 0 or against the ask … 1 of 72". Once this merges, that arm prints `missed` and `a correct zero` in place of that phrase. At the valve-reference head the line reads `missed 0`, with `night-1 21:00` as the one correct zero, so a re-run of its figure command no longer prints the phrase its body quotes. Control: the `fields` before/after pair in Figures. Re-measure at its own merge base. Lands in R11-VALVE-REFERENCE's brief, in the round-11 roster under `dev/programme/rosters/` on `handoff/audit-r10-roster` (not on main yet); the count it changes is printed by `dev/audit/harnesses/r10_advisor_steady_seams.py`. Carry: R11-VALVE-REFERENCE

## Friction

none
