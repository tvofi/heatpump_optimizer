Evidence tree for this unit: handoff/audit-r9-evidence at 96b89163 (the finders' leads harnesses live there, not on this branch). Box G2-V2, verifier V2.

# D4-s2-81 verify-v2 (leads unit)

Finder harness re-run: `tools/audit/round9/D4/leads/l4_setup_labels.py` at baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Baseline: `en_identical_total=41 count` (exact match: 22 of 23 page lines, 16 of 16 slot labels, 3 of 3 advisor labels), `null_narrative_lines_identical_to_en=0 of 1`. load1=0.87, thread_factor=1.000. `--perturb`: `en_identical_total=0 count` (exact match to expected_direction=to_zero).

Own harness (V2, independent instrument): `tools/audit/round9/D4/verify-v2-leads/v2_setup_labels.py`. Metric: count, over `topology.describe_setup`, `topology.render_text_summary`, `topology.rank_sensor_advisor`, `config_flow._setup_overview_form`, of functions whose signature or body carries a language (`inspect.signature`/`inspect.getsource`, never string-diffing rendered output). Result: `no_lang_param=4 of 4` -- none of the four take or read a language. Positive control `narrative.render`: signature carries `language: 'str'` explicitly (`carries_language=True`). Secondary check: object identity of the returned slot labels / summary / advisor labels across an `en` and an `sv` call -- `identical_regardless_of_language=3 of 3`. load1=0.40, thread_factor=1.000.

Source check: `translations/sv.json`'s `setup_overview.description` template ("Vad optimeraren tror...") is genuinely Swedish -- rules out "the translation file itself is untranslated" as an alternative mechanism; only the `{setup_summary}` placeholder these four functions fill in stays English. Also: `config_flow.py` around line 858 (`_building_preset_warning`) already reads `hass.config.language` and picks a table by it in the same file, so the pattern is available and used elsewhere, but not by `_setup_overview_form`.

Attacks:
- Contention: load1 0.36-0.87, thread_factor 1.000 both runs.
- Gate mode: n/a.
- Grid artefact: n/a, not an aggregate.
- Null control: finder's `narrative.render` control reproduced exactly (0 of 1 identical); my own control (same function, signature-level) independently agrees it carries `language` while the four accused functions do not.
- Reachability: `description_placeholders` (config/options flow) and the card's verbatim `setup_topology` attribute are genuine production paths, not a stub artifact.
- Severity: kept at the finder's `medium` -- user-visible wrong-language text with no workaround (the field always misreports for a non-English install).

Vote: **verify**, severity `medium`.
