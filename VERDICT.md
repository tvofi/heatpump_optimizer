Fix review: blocked b0c7114dd6ce636514983b1e685c38e46096f35d mutation-vacuous: read_room sensor-unit mutant (state_unit(state) -> None, inputs.py:1290) survives the whole of tests/features.py

bus-nonce: fea914900c8c77f3a774848e51cfc1b8

Round 1 (first review of #3667), from detached worktrees at the head b0c7114dd6ce636514983b1e685c38e46096f35d.

## Block

- `inputs.read_room`'s sensor branch converts a room's reading by the sensor's own unit: `value = temperature_c(getattr(state, "state", None), state_unit(state))`. Replacing `state_unit(state)` with `None` leaves the PR's block passing (`ALL 16 FEATURES BLOCK PASSED`) and the whole of `tests/features.py` passing (`ALL 5735 FEATURE CHECKS PASSED`, ev/m6-features-full.log). No other script calls `read_room`: `grep` finds it only in `tests/features.py`. The mutant changes behaviour that users will hit. Home Assistant reports every temperature-class sensor in the instance's unit, so on a °F instance every sensor room would be dropped as `implausible`. A °F sensor reading 68.0 reads `temperature_c=20.0, problem=None` at the head and `temperature_c=None, problem='implausible'` under the mutant (ev/m6-probe-head.txt, ev/m6-probe-mutant.txt). The block's Fahrenheit check drives only the `climate` path, and every sensor room it builds is in °C. This is not equivalent and nothing pins it. The fix is one check: a °F temperature sensor room reads as degC, with a °C sensor as the null control. The CI mutation lane's operators (GUARD_OFF, CMP_BOUND, RETURN_DEL ...) generate no argument-replacement mutant at this site, so `mutation-autofix` will not pin it.

## Findings

- Follow-up: `rooms.ROOMS_MAX` is enforced only in the options flow (`_room_list_errors`). `read_rooms` reads whatever list is stored, so the docstring's "a bound on one cycle's reads" holds only while the options page is the only writer of `room_temperature_entities`. Carry: dismissed: the options page is that key's only writer at this head (seam enumeration, ev/seam-enum.txt); worth a line in P2's brief only if P2 adds another writer.
- The coordinator payment folds the ECL110 displace read from four lines to three. Dropping the dead default is a real improvement, and so is skipping a present-but-None displace, which previously raised in `float(None)` (M12 shows that path is pinned). Inlining the two temporaries into one long line is the kind of move a physical-line metric rewards with nothing improved. This is a known property of `max_class_loc`, not new here. Carry: dismissed: a known shape of the line-count ratchet, not new to this PR; the rewrite itself is sound and pinned.

## Evidence

- Head: `git ls-remote` shows `fix/r11-outside-rooms-p1` at b0c7114dd6ce636514983b1e685c38e46096f35d, the head I measured. `dev/governance/roles/` is unchanged between the merge base and origin/main (empty diff).
- Merge with main: `git merge-tree --write-tree origin/main b0c7114dd6…` exits 0, so no conflict (ev/merge-tree.txt).
- `VERSION`, `manifest.json` and `RELEASE_NOTES.md` are untouched (empty `git diff --stat` against the merge base 367c3b9cac).
- Re-run at the head with `PYTHONPATH=tests/hastub`. The features block printed `ALL 16 FEATURES BLOCK PASSED`, `tests/config_flow_steps.py` printed `ALL 595 checks PASSED` and `tests/structure.py` printed `STRUCTURE RATCHET PASSED`. All three match the body.
- Golden fixtures: `GOLDEN_MODE=drift` printed `NO UNCLAIMED DRIFT: 56 scenario(s)`. `CLAIMED config_flow: 4 leaves moved` matches the body's four leaves. `env_drift.py --all` printed `NO UNCLAIMED DRIFT` and `NO STALE FIXTURE`. Every moved fixture is claimed and the one claim moved. The reference was origin/main e352724335, which is newer than the body's merge base. The result is the same.
- Scope: `tests/closure.py select` at the head printed `MODE: SCOPED -- 30 script(s) run, 3 scoped out.`, which matches the body.
- Architecture score: `score.py --diff 367c3b9cac` printed `Architecture score: dS -0.0023 WORSENS (inadmissible: coord_footprint 2496->2500)`, which matches the body (ev/archscore.log). `arch-score` CI is green.
- `_registry_step`'s derived `clear` equals the six replaced steps' constants: `entities_pump`, `hot_water_pumps`, `solar_pv` and `away` are True; `tuning` and `learning_features` are False. The derivation is sound. The `class_excess_loc` 17446 -> 17424 drop comes from removing six near-identical step methods, not from moving them around.
- Reviewer mutants at the head (ev/mutants.txt): M6 survived and the other 13 were killed.
  - M1: a room read recorded into `InputHealth`.
  - M2: the sensor-setup guard forced true.
  - M3: `ROOMS_MAX` raised to 33.
  - M4: the spread zeroed.
  - M5: the `rooms.published` line deleted.
  - M7: the quorum changed from `<` to `<=`.
  - M8: the average sensor reading the spread path.
  - M9: calling set to `!= "off"`.
  - M10: `hvac_mode` dropped.
  - M11: the per-room target dropped.
  - M12: the ECL110 guard turned off.
  - M13: an implausible room keeping its value.
  - M14: `dropped` not published.
- The body's thirteen mutants were not re-run one by one. My M1, M4, M5, M7, M9 and M13 overlap or neighbour them, and each was killed.
- Seam enumeration: the body's rule finds the sites the body lists (ev/seam-enum.txt). No seam is outside the diff.
- Note: stale-body: the enumeration rule in `## Figures` still greps `rooms\.view`, which the head renamed to `rooms.published`. It still finds every site through `room_temperature_entities` and `read_room`.
- CI: `merge_train.py classify … --pr 3667` read WAIT for about 32 minutes, last line `15:54:19 rc=3 WAIT … pending: gate red: none` (ev/classify.log). I stopped polling once the block was established. `tests / mutation` is red at the head, and its log shows the pin shards `mutation-pins (1..6)` being launched. The body's `## Red checks` answers this as the lane's own pinning step, predicted by `prepr.sh` step 6d.
- Finder's harness: none. #3616 is an owner/outside report and the design names none. The body says so, and this review used the PR's r9f12 coordinator rig plus its own probes. The M6 probe is the reviewer's own instrument.
