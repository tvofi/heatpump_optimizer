# BLOCKED: r11-service-schema-p2

Base measured: 38bf516bdd73f926ee9639ffda7b9ca5163fd50e (origin/main at dispatch).

## The two buildable carries are already on main

Carry 0 (5375ae6f) and carry 1 (7965f82b) landed in #3677, commit 6d369cd68f
("services: simulate_plan bounds what its selectors offer; drop dated examples"),
an ancestor of the base (`git merge-base --is-ancestor 6d369cd68f 38bf516bdd` exits 0).
Probe at the base, `PYTHONPATH=tests/hastub:.`, against `SERVICE_SCHEMA_SIMULATE_PLAN`:
min_temp 5, max_temp 40, comfort_weight 100, comfort_temp_night 5, dhw_min_temperature 70
each REFUSED; null control min_temp 20 ACCEPTED. `services.yaml` `apply_manual_plan`
fields carrying an `example`: none (yaml.safe_load over the field map). Nothing is left
to build for either; this seat built nothing.

## The two that need the owner

Question: apply_schedule drops an explicit `silent_mode_power_fraction: 1.0` as "the default" (`_quiet_schedule_fields` in services.py), so a stored lower fraction survives the call. Should an explicit 1.0 reset a stored lower fraction to the default (behaviour change), or does the call stay as it is with the text saying so (carry 56724b85)?

Question: `set_thermal_parameters` admits `dhw_legionella_temperature` 55-75 (`vol.Range(min=55, max=75)`), while the 70 °C hard maximum caps every cycle, so 71-75 writes nothing above 70. Should the service range narrow to the cap (refusing 71-75, a user-facing change), or stay and the service text say that 71-75 is capped to 70 (carry bde9263f)?
