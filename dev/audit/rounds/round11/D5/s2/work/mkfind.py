import json, sys
SHA = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
M = "B2 (orchestrator's macOS box), venv-ci python3"
H = "dev/audit/rounds/round11/D5/s2/comments.py"
CMD = "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/comments.py --plandata $TMPDIR/plandata.json"
def ev(value, unit, harness=H, cmd=CMD, kind="count", load=172.87, tf=0.999):
    return {"command": cmd, "harness_path": harness, "value": value, "unit": unit, "baseline_sha": SHA,
            "machine": M, "cpu_or_wall": kind, "contention_note": "box heavily loaded (load1 150-185); counts are contention-immune",
            "tolerance": "exact", "load1": load, "thread_factor": tf}
F = []
F.append({
 "id": "D5-s2-04", "scope": "D5-s2", "step": "D5.M4",
 "title": "make_model_figures.py docstring says no test reads it; tests/doc_claims.py imports it and its closure holds it",
 "severity": "low",
 "claim": "The module docstring of docs/img/model/make_model_figures.py states that docs/ is INERT so 'nothing under tests/ reads it, so it needs no closure entry and editing it selects no gate script', but closure.is_inert returns False for the file, closure.INERT_EXCEPT lists it, and tests/closures.json puts it in tests/doc_claims.py's closure (doc_claims.py imports it); the store_decay docstring also carries a 45-word sentence (C5).",
 "mechanism": "#1413 moved the generator into tests/doc_claims.py's recorded closure (closure.py INERT_EXCEPT, 'the generated model figures') after the docstring was written; the docstring kept the earlier rationale. A seat reading it expects an edit to the generator to select no gate script, while the scoped gate runs doc_claims.py.",
 "evidence": ev("false_units[make_model_figures.py]=1 (is_inert=False, readers=['tests/doc_claims.py']); long_sentences[make_model_figures.py]=1", "count"),
 "instrumented_symbol": "tests/closure.py:is_inert (with closure.INERT_EXCEPT and tests/closures.json) for docs/img/model/make_model_figures.py",
 "perturbation": {"change": "--perturb-closure: make_model_figures.py removed from closure.INERT_EXCEPT and from closures.json's readers (mock), so the docstring's claim becomes true", "expected_direction": "down", "observed_value": "false_units 2 -> 1 (this file's unit leaves)"},
 "null_control": {"command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/comments.py", "value": "the same closure claim in make_card_figures.mjs:1 and make_card_weekly_figure.mjs:1 checks true (is_inert=True, readers=[])", "note": "the check separates a generator the gate reads from one it does not"},
 "metric_definition": "Comment units in the file whose executed check contradicts them (C1), plus prose sentences over 40 words (C5).",
 "phenomenon_property": "Every comment or docstring that states how the gate classifies a file agrees with tests/closure.py:is_inert and tests/closures.json for that file.",
 "seam_rule": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/comments.py  (false lines; any unit containing 'INERT')",
 "stop_rule_class": "hygiene", "class_guess": "I5",
 "files": ["docs/img/model/make_model_figures.py"],
 "proposed_fix_scope": "Rewrite the docstring's second paragraph: the generator lives beside its output; tests/doc_claims.py imports it, so it is in that script's closure and an edit selects doc_claims.py. Split the 45-word store_decay sentence."
})
F.append({
 "id": "D5-s2-05", "scope": "D5-s2", "step": "D5.M4",
 "title": "make_card_figures.mjs: font-stack comment names a README hero that has no such font; 5 sentences over 40 words",
 "severity": "low",
 "claim": "In docs/img/card/make_card_figures.mjs the comment 'The one font stack, matching the hero in README.md.' is false (README.md's hero is banner.png, whose 0 <text> elements are glyphs outlined from Outfit / Instrument Sans by make_readme_figures.banner, carrying no CSS font stack), and 5 prose sentences of its comments exceed C5's 40-word limit (41, 55, 44, 46, 43 words).",
 "mechanism": "The README hero was redrawn by make_readme_figures.py with outlined brand fonts; the card-figure generator's FONT constant and its comment kept pointing at it. The long sentences are the header and renderChart/onlySeries docstrings chaining clauses with '--' and ':'.",
 "evidence": ev("false_units[make_card_figures.mjs]=1; long_sentences[make_card_figures.mjs]=5", "count"),
 "instrumented_symbol": "README.md line 1 hero and docs/img/readme/make_readme_figures.py:banner (fonts outlined), against docs/img/card/make_card_figures.mjs:FONT; tools/audit/text_ledger.py:units_of for the sentence count",
 "perturbation": {"change": "--perturb-text: the false unit rewritten in memory to the truth and each >40-word sentence split", "expected_direction": "to_zero", "observed_value": "false_units 2 -> 0 (both files), long_sentences 8 -> 0"},
 "metric_definition": "Comment units in the file whose executed check contradicts them (C1), plus prose sentences over 40 words (C5).",
 "phenomenon_property": "Every comment in the file is true of the code and artefacts it names, and no comment sentence exceeds 40 words.",
 "seam_rule": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/comments.py  (false and long lines for this file)",
 "stop_rule_class": "hygiene", "class_guess": "I5",
 "files": ["docs/img/card/make_card_figures.mjs"],
 "proposed_fix_scope": "Reword the FONT comment (the system stack the figure SVGs share with make_model_figures.py, not the README hero) and split the five long sentences."
})
F.append({
 "id": "D5-s2-06", "scope": "D5-s2", "step": "D5.M4",
 "title": "make_card_weekly_figure.mjs header: two sentences of 51 and 55 words",
 "severity": "low",
 "claim": "The header comment of docs/img/model/make_card_weekly_figure.mjs carries two prose sentences of 51 and 55 words, over C5's 40-word limit; every checked fact in it is true.",
 "mechanism": "The header packs the figure's subject and the payload construction into two chained sentences joined by ':' and parentheses.",
 "evidence": ev("long_sentences[make_card_weekly_figure.mjs]=2", "count"),
 "instrumented_symbol": "tools/audit/text_ledger.py:units_of (D5 comment units) over docs/img/model/make_card_weekly_figure.mjs",
 "perturbation": {"change": "--perturb-text: each >40-word sentence split at its first clause break after word 20", "expected_direction": "to_zero", "observed_value": "long_sentences 8 -> 0"},
 "null_control": {"command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/comments.py", "value": "render.mjs, render_mermaid.mjs and make_readme_figures.py: long_sentences 0 each", "note": "indented command lines inside comments are not counted as prose, so the 69-word false hit in render_mermaid.mjs's run block is excluded"},
 "metric_definition": "Prose sentences (indented command lines excluded) over 40 words in the file's comment units (C5).",
 "phenomenon_property": "No comment sentence in the file exceeds 40 words.",
 "seam_rule": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/comments.py  (long lines)",
 "stop_rule_class": "hygiene", "class_guess": "new",
 "files": ["docs/img/model/make_card_weekly_figure.mjs"],
 "proposed_fix_scope": "Split the two header sentences."
})
F.append({
 "id": "D5-s2-07", "scope": "D5-s2", "step": "D5.M4",
 "title": "text_ledger.py check --plant always fails for seat D5-s2: it plants into README.md, which D5 reads no units from",
 "severity": "low",
 "claim": "For a complete D5 ledger over seat D5-s2's cells, text_ledger.py check --plant prints plant_refused=0 planted_units=0 and exits 1, because run_check plants into files[0] (README.md after seat_files' sort) and units_of under --dim D5 yields only the unchanged `file` unit for a .md file before and after the plant, so the per-seat null control D5.md step 4 relies on can never pass for this seat.",
 "mechanism": "run_check: `f0 = files[0]` with no regard to whether the dimension reads any unit from f0; plant() appends a sentence, units_of(.md, D5) returns [(0,'file',path)] either way, so `planted` is empty and `refused = bool(planted) and ...` is False.",
 "evidence": ev("plant_refused=0 planted_units=0 rc=1", "flag", harness="dev/audit/rounds/round11/D5/s2/plant.py", cmd="PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/plant.py", load=184.83, tf=1.0),
 "instrumented_symbol": "tools/audit/text_ledger.py:run_check (its --plant arm) and text_ledger.py:units_of",
 "perturbation": {"change": "--perturb: the plant goes to the first file carrying a D5 suffix (files reordered in memory)", "expected_direction": "up", "observed_value": "plant_refused 0 -> 1, rc 1 -> 0"},
 "null_control": {"command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/plant.py", "value": "plant_refused_d6=1 rc_d6=0 over the same files, README.md first", "note": "D6 reads Markdown sentences, so the same order passes there: the defect is D5's rule meeting a non-carrier first file"},
 "metric_definition": "plant_refused flag and exit code of run_check --plant for a complete ledger (every unit rowed) over the seat's sorted cells.",
 "phenomenon_property": "For every seat and dimension, check --plant on a complete ledger passes: the plant lands in a file the dimension reads units from.",
 "seam_rule": "for s in 1..10: python3 tools/audit/check_scopes.py --seat D5-s$s ... | first M4 file without a .py/.js/.mjs/.sh suffix (today only D5-s2: README.md)",
 "stop_rule_class": "bug", "class_guess": "new",
 "files": ["tools/audit/text_ledger.py"],
 "proposed_fix_scope": "In run_check, plant into the first file whose units under `dim` change when planted (for D5, the first file with a D5_SUFFIXES suffix); add a self-test arm with a .md first file under D5."
})
for f in F:
    open(f"dev/audit/rounds/round11/D5/s2/findings/{f['id']}.json", "w").write(json.dumps(f, indent=1) + "\n")
print(len(F))
