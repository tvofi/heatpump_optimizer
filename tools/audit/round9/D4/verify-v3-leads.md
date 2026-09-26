# D4 leads, verifier V3 (reach and class), round 9

Box G2-V3, lens V3 (reach and class), leads unit. Read at evidence 96b89163 (leads harnesses under `tools/audit/round9/<dim>/leads/`); own harnesses under `verify-v3/leads/` here. Real HA: core 2026.2.3 on CPython 3.14.0rc2, numpy/scipy from the gate venv; shims: stand-in `typing.ByteString` ABC before importing HA, `http` marked loaded.

## D4-s2-81 — Setup overview and diagram publish English slot text on a Swedish install

**Step 1.** `l4_setup_labels.py`: `flow_page_lines_identical_to_en=22`, `slot_labels_identical_to_en=16 of 16`, `advisor_labels_identical_to_en=3 of 3`, `en_identical_total=41`, null `narrative` 0 of 1. thread_factor 1.000, load1 2.11. Exact.

**Step 2 / reach, real HA.** `realha_setup_overview.py`: real `OptionsFlowManager` to `setup_overview`, real `helpers.translation` loader, `hass.config.language="sv"`.
- `real_template_is_swedish=1`: the sv catalogue's prose around `{setup_summary}` is Swedish through the real loader, ruling out a broken catalogue.
- `real_rendered_lines_sv=21`, `real_identical_lines_sv_en=20`, `real_slot_labels_identical_to_en=14 of 14`.
- Perturbation (the lead's localisation stand-in around the real flow): identical lines 0, slot labels 0 of 14. load1 0.57–0.86.

**Attacks.** Contention: counts. Gate mode: n/a. Grid: single config, both engines agree. Null control: `narrative.render` (takes `TEMPLATES[language]`) 0 of 1. Reachability: real — no language parameter reaches `describe_setup`/`render_text_summary`/`rank_sensor_advisor`.

**Severity:** medium confirmed (visible, persistent on every non-English install; no functional harm).

**Seam rule.** 14 hits: 3 definitions (topology.py), `config_flow.py:2196,2201`, `coordinator.py:7042,7050` (into `sensor.py:1456,1573` `setup_topology`), `sensor.py:111`, plus doc mentions. **Partial**: every call site of the three named functions, but the phenomenon_property ("every user-facing string the backend publishes for the setup diagram and sensor advisor") is wider than the grep — an inline English literal in topology.py outside those three functions would not be caught.

**Class:** new confirmed — a text-producing function takes no language parameter while its sibling `narrative.render` does (P8 is currency/unit, a different axis).

**Vote: verify, medium.**
