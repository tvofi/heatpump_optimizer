# Class sweep: N-name-sort (round 11)

Class status in `dev/audit/config/bugclasses.json`: `open`, no detector, no barrier
(barrier refusal: `tests/entities.py` #1760 does not enumerate every seam).
Finding: D8-s2-02 (weakened, low).

## Enumerator
`dev/audit/rounds/round11/D14/sweep-N-name-sort/enumerate.sh` wraps
`D8/s2/m3_naming.py`, which builds every entity of every platform through
`async_setup_entry` and sorts by entity_id (per platform and all) and by display
name (en, sv, de; per-language collation), counting family runs minus 1.

- Positive control: `enumerate.sh positive` gives `fam_runs_excess_entity_id_sensor=2`
  (lifetime: 3 runs), re-finding D8-s2-02 exactly.
- Null control: `enumerate.sh null` gives `null_fixture_runs_excess=0` on a
  contiguous synthetic fixture.
- Perturbation: `enumerate.sh perturb` prefixes one en name (`sensor.dhw_energy`)
  in a temporary edit restored on exit; `fam_runs_excess_name_en` moves 0 to 1.
  The finding's own perturbation (`--perturb-lifetime-ids`) moves sensor 2 to 0.

## Seam dispositions
| seam | disposition |
|---|---|
| sensor entity_id sort, family `lifetime` | instance (D8-s2-02 site; probe: positive reads 2, expect 0) |
| binary_sensor, button, switch, climate, datetime entity_id sorts | guarded: 0 at head; family-prefixed ids pinned by `tests/entities.py` (#1227/#1760 blocks) |
| display-name sort en, sv, de | guarded: 0 at head; `tests/entities.py` check "every declared family sorts as one contiguous run in every shipped language (#1760)" |
| entity_id_all (away, dhw, heat, learning, prediction, wood, lifetime): 9, 7 after lifetime move | not applicable: every remaining boundary is a platform change; HA lists entity_ids grouped by domain |

## Count
Instances beyond the finding: 0. The one instance is the judged site. The
#1760 check guards names but not legacy sensor entity_ids; proposed barrier:
extend #1760 to assert per-platform entity_id contiguity (the enumerator's
`fam_runs_excess_entity_id_<platform>`), about 1 s of gate time.
