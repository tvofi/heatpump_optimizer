# Review packet #3568
head: 3fa750ea3861bf623ea3ff58e8e514321c511b52
base: e23124ff6e45bac1d48b4a775dad555a37965355

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=132239921870 success
arch-score / arch-score id=132239704522 success
arm id=132239344476 skipped
budget-raise-gate / budget-raise-gate id=132239704661 success
cancel-superseded id=132239304555 success
codeql id=132239706875 skipped
codeql / Analyze (actions) id=132239693897 success
codeql / Analyze (javascript-typescript) id=132239693986 success
codeql / Analyze (python) id=132239694017 success
gate id=132240621821 failure
governance id=132239706376 skipped
governance / delivery-status id=132239694041 success
governance / delivery-status-publish id=132239696155 skipped
governance / env-matrix id=132239694026 success
governance / instrument-self-tests id=132239693941 success
governance / policy-docs id=132239693968 success
governance / record id=132239695831 skipped
governance / wave-script id=132239693975 success
hassfest id=132239706000 skipped
hassfest / hassfest id=132239693827 success
kernel-points id=132239705765 skipped
pr-contract id=132240623017 skipped
prelude id=132239304559 success
refresh id=132239304234 success
sweep-self id=132241221235 skipped
tests id=132239706251 skipped
tests / arch-instrument id=132240349081 success
tests / briefs id=132239693855 success
tests / browser id=132240349009 success
tests / claims-autofix id=132245389964 skipped
tests / closure-scope id=132239694209 success
tests / closures id=132240349152 success
tests / closures-autofix id=132246355740 skipped
tests / coverage id=132240348970 in_progress
tests / fast (3.14) id=132240348985 success
tests / mutation id=132239694120 success
tests / mutation-autofix id=132240313809 skipped
tests / mutation-pins id=132240313242 skipped
tests / nightly-ha id=132240352035 skipped
tests / nightly-status id=132239693881 success
tests / replay id=132240350853 skipped
tests / typing id=132240349038 success
validate id=132239707069 skipped
validate / validate-hacs id=132239693828 success

## Refusals
none

## Advisories
required-wait: required context `gate` reads concluded failure at 3fa750ea3861bf623ea3ff58e8e514321c511b52 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
NOTE stale tree: 3fa750ea3861bf623ea3ff58e8e514321c511b52 lacks origin/main 50373173d486faf394b24637c177ab38b691b394; roster read at origin/main
NOTE body item dc8ba668: dismissed:nothing changes a later stage
NOTE body item 1e64f68a: dismissed:no friction recorded
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: SCOPED -- 6 script(s) run, 27 scoped out.
             no segment of this names a program this check knows
  ok         python3 tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         python3 tests/doc_claims.py --markers --user
             `tests/doc_claims.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py
             `dev/audit/rounds/round4/D6/claims.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head

FIGURES: 5 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: delta (later round over the reviewed head 6295f868a4314316f5e12c72fa2d16ead4895d35)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at 6295f868a4314316f5e12c72fa2d16ead4895d35
Fix review: blocked 6295f868a4314316f5e12c72fa2d16ead4895d35 doc-claim-false: two added user-doc sentences are false against executable code (lost heat is charged only hot-water-to-heating; the cold-tank exception needs a step that heats the tank) and the body's null control prints nothing for docs/how-it-works.md

bus-nonce: fd9c4779b03c45c5897554d16b10dca6

## Block

Round 1. Measured at head 6295f868a4314316f5e12c72fa2d16ead4895d35 (handoff tip; the body's `## Head` names the same SHA). Every item below is evidenced by an executable line, not by a comment or docstring (owner ruling 2026-11-13).

1. **docs/configuration.md (Pump duty control, "A switch that stops the compressor is priced") and docs/how-it-works.md (cycling-cost section) state the off time is charged as heat not delivered for any latched direction.** The configuration bullet says "Once a direction has stopped the compressor ... the plan ... expects the median measured off time as heat not delivered in the step that follows"; how-it-works says the optimizer learns "per direction" and "counts the off time as heat not delivered". Executable code charges lost heat for one direction only: `duty_legs.lost_share` returns `min(1.0, stop_probability[0] * off_seconds[0] / (step_minutes * 60.0))` (custom_components/heatpump_optimizer/duty_legs.py:161), index 0 being `dhw_space` (`duty_switch.DIRECTIONS = ("dhw_space", "space_dhw")`, read in that order by `planner_pairs`). A latched heating-to-hot-water direction is priced in `switch_weights_batch` but never reduces availability. Fix: name the direction (hot water to heating) in both sentences.

2. **docs/configuration.md, Heat pump on/off switch row: "a run the plan would end within 10 minutes is not started unless the tank needs heat now (below its minimum, or a disinfection hold)".** `supply_hold._ends_soon` (supply_hold.py:156) exempts the start only when `step_duty(inp.plan, now) in ("dhw", "both") and tank_reason(inp)`: a cold tank or disinfection hold on a space-only step is still held. The page states the tank condition alone. Fix: "unless the step heats the tank and the tank needs heat now".

3. **The body's `## Null control` does not re-derive.** It claims the `git grep -c -E ...` command prints "one or more lines per page at the head"; at the head it prints README.md:1 and docs/configuration.md:3 and nothing for docs/how-it-works.md (none of the four patterns appears in the added how-it-works paragraph). Origin/main side prints nothing, as claimed. ev/checks.txt. Fix: add a pattern that occurs in the how-it-works paragraph (e.g. `min\(a, b\) / p_max`) or correct the sentence.

## Findings

none

## Evidence

- No pull request exists yet: no review packet, no CI runs to read, so no red check is owed an answer (step 11 has nothing to read). `merge_train.py owed-reds` set recorded in ev/checks.txt.
- Merge: `git merge-tree --write-tree origin/main 6295f868a4` rc=0, tree b797a2d8a3; origin/main is e23124ff6e, the head's merge base (head not behind). ev/checks.txt.
- Role contract current: `git diff <mb>...origin/main -- dev/governance/roles/` empty.
- VERSION, manifest.json, RELEASE_NOTES.md untouched; both claim files untouched; no golden fixture in the diff (docs-only), so `env_drift.py --all` has nothing to compare.
- Mutation proof: n/a, no production line changed (diff: README.md, docs/configuration.md, docs/how-it-works.md, dev/audit/rounds/round4/D6/claims.{json,md}); confirmed by `git diff --stat`.
- `python3 tests/doc_claims.py` at head: ALL 348 checks PASSED, rc 0; `--markers --user`: 0 user-doc marker(s), 0 due. Re-derived, matches the body.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` re-run at head leaves claims.json/claims.md byte-identical; C108 reads 92 links, broken=[]. Re-derived, matches the body.
- Scope line: `python3 tests/closure.py select --diff e23124ff6e --workdir $D` prints `MODE: SCOPED -- 6 script(s) run, 27 scoped out.`, matching the body's figure block.
- Enumeration rule re-run (body's first-parent loop over f44e761c19..origin/main): returns #3511, #3526, #3512, #3536, #3505, #3441, #3534, #3530, #3524 plus the two stamps and #3513 itself; every product merge is dispositioned in the body. `git merge-base --is-ancestor 3246aa389f origin/main` true. ev/enum_and_code.txt.
- Verified true against code: supply MIN_RUN/MIN_PAUSE = 10 min, `_passes` exempts modes other than auto/economy, system identification and live boosts; retry `_TICK = timedelta(minutes=1)` via `supply_tick`; age from the switch's `last_changed` (`switch_age`), restart stamp pinned by tests/ha_contract.py `_restart_stamps_last_changed`; early_cutoff's own `_cycle_guard` refuses a cut under `MIN_ON` (= MIN_RUN), so the "never switched off less than 10 minutes" claim holds for both switch writers (`switch_supply` callers: `write_supply`, early_cutoff). Duty switch: `STOP_WINDOW_S = 180.0`, `N_ON = 5.0`, `P_ON = 0.5`, `SPAN_DAYS_ON = 2`, `HALF_LIFE_DAYS = 14.0` in `Direction._latch`; published keys `duty_switch_{dhw_space,space_dhw}_{p,n,stopped,kept,void,censored,median_off_s,span_days}` on the Compressor Starts sensor; `_switch_cost_fn` and the placement candidate return nothing when `cycling_cost` is not > 0 while `_stop_availability` still applies (start cost 0 plans only lost heat: true); cost term `p * min(level_before, level_after) / p_max` matches how-it-works' formula; option label "Cost of one compressor start" is `compressor_cycling_cost`. `_lead_mode` writes the mode only under DUTY_CONTROL with the switch reading off: true.
- `BOOST_SPACE_SETTLE_TAIL_HOURS: Final = 12.0` at head (body's #3505 disposition).
- Not re-derived: the body's "re-read, no stale claim found" for #3534, #3441, #3536 and the carries it marks implemented without touching; I did not re-read those pages in full.
- Code reads for duty_switch/optimizer were extracted by a delegated read-only worker quoting file:line; the three block items were read by me directly (ev/enum_and_code.txt).

## Delta diff: git diff 6295f868a4314316f5e12c72fa2d16ead4895d35 3fa750ea3861bf623ea3ff58e8e514321c511b52
diff --git a/dev/programme/delivery/3568.md b/dev/programme/delivery/3568.md
new file mode 100644
index 0000000000..38d20f1c96
--- /dev/null
+++ b/dev/programme/delivery/3568.md
@@ -0,0 +1 @@
+- [#3568](https://github.com/tvofi/heatpump_optimizer/pull/3568) — **open**, R10-USER-DOCS-VERIFY: r10 user docs verify (R10-USER-DOCS-VERIFY)
diff --git a/docs/configuration.md b/docs/configuration.md
index 1e16ae549d..3fc055f9f0 100644
--- a/docs/configuration.md
+++ b/docs/configuration.md
@@ -85,7 +85,7 @@ Every picker on this second screen is optional; skip any you do not have. Withou
 |---|---|---|
 | Indoor temperature sensor | none | The real room temperature. Without it the optimizer trusts its own model, which drifts over time — this is the sensor worth finding first. |
 | Outdoor temperature sensor | none | A local thermometer beats the forecast for the current hour. |
-| Heat pump on/off switch | none | A `switch` the optimizer may turn off during expensive hours. In *auto* and *economy* mode it is never switched off less than 10 minutes after it came on, nor on less than 10 minutes after it went off, and a run the plan would end within 10 minutes is not started unless the tank needs heat now (below its minimum, or a disinfection hold); a held switch is retried every minute and changes once its 10 minutes have passed. The age is the switch's own, whoever switched it; after a Home Assistant restart it counts from the restart. A boost, the other modes and the measurement experiment are not held. Without it — and without the ECL110 or frequency-control paths — the plan is published on sensors for your own automations to act on ([worked examples](automations.md)). |
+| Heat pump on/off switch | none | A `switch` the optimizer may turn off during expensive hours. In *auto* and *economy* mode it is never switched off less than 10 minutes after it came on, nor on less than 10 minutes after it went off, and a run the plan would end within 10 minutes is not started unless the step heats the tank and the tank needs heat now (below its minimum, or a disinfection hold); a held switch is retried every minute and changes once its 10 minutes have passed. The age is the switch's own, whoever switched it; after a Home Assistant restart it counts from the restart. A boost, the other modes and the measurement experiment are not held. Without it — and without the ECL110 or frequency-control paths — the plan is published on sensors for your own automations to act on ([worked examples](automations.md)). |
 | Solar radiation sensor | none | Irradiance in W/m². Lets the plan skip heating before a sunny afternoon. |
 | Solar irradiance source | Weather entity | `Weather entity` reads irradiance from your weather integration, which often does not publish any. `Open-Meteo` fetches a free forecast for the location below; no account needed. |
 | Solar irradiance location | your Home Assistant home location | The coordinate Open-Meteo is asked about. Only used when the source is Open-Meteo. |
@@ -848,14 +848,19 @@ writes, at every 15-minute plan step:
   disinfection cycle keeps *Heating + DHW* for the whole step.
 - **A switch that stops the compressor is priced.** Some pumps stop the
   compressor when the mode changes between hot water and heating. The
-  optimizer watches each switch it writes while the compressor runs: a stop
-  within 3 minutes counts against that direction. Once a direction has
+  optimizer counts only some of the switches it writes, among the conditions
+  the compressor running, the new duty asking for heat and the plan keeping
+  that duty; a stop within 3 minutes of a counted switch counts against its
+  direction, and a switch a person's own mode change explains is not
+  counted. Once a direction has
   stopped the compressor on at least half of a weighted 5 or more switches,
   seen on at least two calendar days (a switch weighs half after 14 days), the plan charges that switch a share of
-  the **Cost of one compressor start**, expects the median measured off time
-  as heat not delivered in the step that follows, and tries to place hot
-  water where no such switch follows it. With the start cost at 0 only the
-  lost heat is planned for. The counts per direction are attributes of the
+  the **Cost of one compressor start** and tries to place hot water where no
+  such switch follows it (not on a combi store). For a switch from hot water
+  to heating it also expects the median measured off time as heat not
+  delivered in the heating that follows; a switch the other way is priced
+  but costs no heat. With the start cost at 0 only that lost heat is planned
+  for. The counts per direction are attributes of the
   **Compressor Starts** sensor (`duty_switch_dhw_space_p`, `_n`, `_stopped`,
   `_kept`, `_median_off_s` and so on; `dhw_space` is hot water to heating).
 - **The mode goes first when the pump is switched on.** When the on/off switch
diff --git a/docs/how-it-works.md b/docs/how-it-works.md
index 3956d7f752..3cfdfc1faf 100644
--- a/docs/how-it-works.md
+++ b/docs/how-it-works.md
@@ -834,8 +834,9 @@ control** at Control the optimizer learns, per direction, how often a switch
 it wrote stopped the compressor and for how long; once that is established
 ([Pump duty control](configuration.md#pump-duty-control)), the plan charges
 the switch `min(a, b) / p_max` cycles at the cycling cost (`a` and `b` the
-draws on either side, `p_max` the pump's maximum) times that probability,
-and counts the off time as heat not delivered.
+draws on either side, `p_max` the pump's maximum) times that probability;
+for a switch from hot water to heating it also counts the off time as heat
+not delivered.
 
 ---
 
diff --git a/tests/doc_claims.py b/tests/doc_claims.py
index 8641c21162..fec787e548 100644
--- a/tests/doc_claims.py
+++ b/tests/doc_claims.py
@@ -812,6 +812,121 @@ def check_heat_pump_action_states() -> None:
     )
 
 
+# The direction each prose name stands for, keyed by duty_switch.DIRECTIONS.
+_DUTY_DIRECTION_PROSE = {"dhw_space": "hot water to heating", "space_dhw": "heating to hot water"}
+# Pre-fix sentences (6295f868a4), the null controls of check_duty_switch_claims.
+_LOST_HEAT_BAD = {
+    "configuration.md": (
+        "Once a direction has stopped the compressor on at least half of a weighted 5 or more "
+        "switches, seen on at least two calendar days (a switch weighs half after 14 days), the "
+        "plan charges that switch a share of the **Cost of one compressor start**, expects the "
+        "median measured off time as heat not delivered in the step that follows, and tries to "
+        "place hot water where no such switch follows it."
+    ),
+    "how-it-works.md": (
+        "With **Pump duty control** at Control the optimizer learns, per direction, how often a "
+        "switch it wrote stopped the compressor and for how long; once that is established, the "
+        "plan charges the switch `min(a, b) / p_max` cycles at the cycling cost times that "
+        "probability, and counts the off time as heat not delivered."
+    ),
+}
+_ENDS_SOON_BAD = (
+    "a run the plan would end within 10 minutes is not started unless the tank needs heat now "
+    "(below its minimum, or a disinfection hold)"
+)
+
+
+def _sentences_with(text: str, phrase: str) -> list[str]:
+    """The sentences of unwrapped prose that contain ``phrase``."""
+    flat = re.sub(r"\s+", " ", text)
+    return [s for s in re.split(r"(?<=[.;])\s+(?=[A-Z*(]|for |a )", flat) if phrase in s]
+
+
+def _lost_heat_direction() -> str | None:
+    """The one direction ``duty_legs.lost_share`` charges off time for, from the code."""
+    from heatpump_optimizer import duty_legs, duty_switch
+
+    charged = [
+        name for i, name in enumerate(duty_switch.DIRECTIONS)
+        if duty_legs.lost_share(tuple(0.5 * (j == i) for j in range(2)),
+                                tuple(300.0 * (j == i) for j in range(2))) > 0
+    ]
+    return charged[0] if len(charged) == 1 else None
+
+
+def _lost_heat_names(text: str, direction: str) -> bool:
+    """Every lost-heat sentence names ``direction`` and not the other one."""
+    other = next(v for k, v in _DUTY_DIRECTION_PROSE.items() if k != direction)
+    hits = _sentences_with(text, "heat not delivered")
+    return bool(hits) and all(
+        _DUTY_DIRECTION_PROSE[direction] in s and other not in s for s in hits
+    )
+
+
+def _ends_soon_held(duty: str) -> bool:
+    """``supply_hold._ends_soon`` for a cold tank, a run ending in 5 minutes, on a ``duty`` step."""
+    from datetime import datetime, timezone
+    from heatpump_optimizer import supply_hold
+
+    saved = supply_hold.step_supply, supply_hold.step_duty, supply_hold.tank_reason
+    supply_hold.step_supply = lambda *_: False
+    supply_hold.step_duty = lambda *_: duty
+    supply_hold.tank_reason = lambda *_: "tank_cold"
+    try:
+        inp = type("Inp", (), {"plan": None})()
+        return supply_hold._ends_soon(inp, None, datetime(2026, 1, 1, 0, 10, tzinfo=timezone.utc))
+    finally:
+        supply_hold.step_supply, supply_hold.step_duty, supply_hold.tank_reason = saved
+
+
+def _ends_soon_names_duty(row: str) -> bool:
+    """The on/off row's not-started exception names the step heating the tank."""
+    hits = [s for s in _sentences_with(row, "is not started unless")]
+    return bool(hits) and all("step heats the tank" in s for s in hits)
+
+
+def check_duty_switch_claims() -> None:
+    R.section("Duty-switch and supply-hold sentences match the code that decides them")
+    direction = _lost_heat_direction()
+    R.check(
+        "duty_legs.lost_share charges off time for exactly one direction (anchor)",
+        direction in _DUTY_DIRECTION_PROSE,
+        repr(direction),
+    )
+    for page in ("configuration.md", "how-it-works.md"):
+        R.check(
+            f"docs/{page}: every 'heat not delivered' sentence names the direction "
+            f"lost_share charges ({_DUTY_DIRECTION_PROSE.get(direction)}) and not the other",
+            direction is not None and _lost_heat_names(DOCS[page], direction),
+            repr(_sentences_with(DOCS[page], "heat not delivered")),
+        )
+        R.check(
+            f"docs/{page}: the lost-heat check fires on the pre-fix sentence (null control)",
+            direction is not None and not _lost_heat_names(_LOST_HEAT_BAD[page], direction),
+            _LOST_HEAT_BAD[page],
+        )
+    space_held, dhw_held = _ends_soon_held("space"), _ends_soon_held("dhw")
+    R.check(
+        "supply_hold._ends_soon holds a cold-tank start on a space step and passes it on a "
+        "hot-water step (anchor: the exemption needs a step that heats the tank)",
+        space_held and not dhw_held,
+        f"space={space_held} dhw={dhw_held}",
+    )
+    row = next((line for line in DOCS["configuration.md"].splitlines()
+                if line.startswith("| Heat pump on/off switch |")), "")
+    R.check(
+        "docs/configuration.md on/off switch row: the not-started exception names the step "
+        "heating the tank",
+        _ends_soon_names_duty(row),
+        repr(_sentences_with(row, "is not started unless")),
+    )
+    R.check(
+        "the on/off exception check fires on the pre-fix sentence (null control)",
+        not _ends_soon_names_duty(_ENDS_SOON_BAD),
+        _ENDS_SOON_BAD,
+    )
+
+
 def check_disabled_by_default_without_hot_water() -> None:
     R.section(
         "Disabled-by-default census covers a no-hot-water install too "
@@ -4727,6 +4842,7 @@ def main() -> int:
     check_simulate_plan_fields()
     check_two_zone_field_labels_and_placement()
     check_heat_pump_action_states()
+    check_duty_switch_claims()
     check_disabled_by_default_without_hot_water()
     check_multistart_starting_points()
     check_prose_tree_counts()

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
