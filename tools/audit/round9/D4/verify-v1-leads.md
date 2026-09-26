# D4 verify-v1, leads unit (round 9, lens V1 reproduce), box G2-V1

Tree: /home/claude/wt/leads at evidence 96b89163. Finder's harness re-run unmodified with PYTHONPATH=tests/hastub; perturbations in memory; no harness written.

## D4-s2-81 -- Setup overview page and setup diagram publish English text on a Swedish install (vote: verify, medium)
- Re-run: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/leads/l4_setup_labels.py` -> flow_page_lines_identical_to_en=22 of 23, slot_labels_identical_to_en=16 of 16, advisor_labels_identical_to_en=3 of 3, en_identical_total=41. The finder's value is 41, so exact. load1=1.74, thread_factor=1.000.
- Perturbation `--perturb` (describe_setup / render_text_summary / rank_sensor_advisor wrapped through a "[sv] " stand-in table): en_identical_total 41 -> 0. Finder's observed 0, direction to_zero.
- Null control: `null_narrative_lines_identical_to_en=0` of 1 -- narrative.render already follows hass.config.language (TEMPLATES[language]); the topology seams are the outliers. Matches the finder.
- Leave-one-out: n/a (one house configuration, three fixed seams; not a >=5-cell grid).
- Method attacks: exact count, contention-immune; reach checked in source: `config_flow._setup_overview_form` fills the sv template's `{setup_summary}` with `topology.describe_setup` / `render_text_summary` output, neither of which takes a language argument; production path, not stub-only.
- Metric (finder's): published setup strings (setup_overview lines, setup_topology slot labels, sensor_advisor labels) byte-identical between an en and sv install.
- Severity medium: user-visible untranslated UI; no money, comfort or data consequence.
