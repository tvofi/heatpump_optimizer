BLOCKED: R10-PARTLOAD-RESIDUE head 0940e9aae621ea196fa2db7842c802df30946467 has two reds caused by this diff, in code.

- arch-score / arch-score (job 128658352537): dS -0.1926 WORSENS, inadmissible: params_over_10 6->7. `wood_fuel.build_wood_fuel_view` went from 10 to 11 parameters (`partload_at`), `wood_fuel_from_parts` from 8 to 9.
- tests / arch-instrument (job 128658496674): tests/arch_score_head.py, "every function over ten parameters is a dispositioned row (#1776)", unlisted: wood_fuel.build_wood_fuel_view.
- tests / mutation (job 128658352721) is the expected unpinned-site red (wood_fuel.py:546 RETURN_DEL, :666 GUARD_OFF) that mutation-autofix pins.

Fix needed (a fixer, not this body seat): take the horizon/series record instead of an eleventh parameter, or row the function in PARAMS_OVER_10_LEFT with owner approval. Run `python3 tests/arch_score_head.py` and tools/audit/archscore/gate.py before the next handoff. The body pushed to handoff-body states this.
