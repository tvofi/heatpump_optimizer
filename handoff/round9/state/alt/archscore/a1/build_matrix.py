#!/usr/bin/env python3
"""Build matrix.tsv: metric x perturbation -> delta vs baseline, expected sign, verdict.

Grading, per cell:
  NULL  : expected 0.        delta != 0            -> WRONG (a null moved it)
  GOOD  : expected <= 0.     delta > 0             -> WRONG (punishes an improvement)
  BAD   : expected >= 0.     delta < 0             -> WRONG (rewards a regression)
  targeted cells (the metric the move is ABOUT) expect a strict move:
  GOOD target expected < 0, BAD target expected > 0; delta == 0 -> MISS.
  otherwise OK.
"""
import json
from pathlib import Path

A = Path(__file__).resolve().parent
OUT = A / "out"
base = json.loads((OUT / "base.json").read_text())
METRICS = sorted(base)

CC_LOC = {"max_cc", "functions_cc_over_15", "functions_cc_over_25", "max_method_loc", "methods_over_150", "methods_over_200"}
COUPLING = {"cross_seam_edges", "cut_dhw", "cut_fetch", "cut_grid", "cut_learning", "cut_views"}
P = [  # (name, class, targeted metrics, one-line description)
    ("G1_extract_block", "GOOD", CC_LOC, "extract cohesive wood-tank block of _update_current_state (CC44) into a helper"),
    ("G2_dedupe", "GOOD", {"duplication_blocks"}, "dedupe the two fabric learners' replay block into _replay_interval"),
    ("G3_move_cluster_with_state", "GOOD", {"coordinator_attrs", "coordinator_methods", "coordinator_loc", "coordinator_multiassigned_attrs"} | COUPLING, "frequency cluster + its 4 attrs -> freq_seat.FrequencyControl, args in / bool out"),
    ("G4a_public_accessor_existing", "GOOD", COUPLING, "pump_arbiter: 21 coord._x reaches -> existing public accessors"),
    ("G4b_public_accessor_new", "GOOD", COUPLING, "new current_state property; 4 pump_arbiter reaches use it"),
    ("G5_frozen_record_arg", "GOOD", {"coordinator_attrs", "coordinator_multiassigned_attrs"}, "order-coupled _last_house_sample(_time) -> frozen _HouseSample passed as arg"),
    ("B1_copy_cross_module", "BAD", {"duplication_blocks"}, "clone coordinator._as_float (18 lines) into pump_arbiter.py, used"),
    ("B1c_copy_same_module_control", "BAD", {"duplication_blocks"}, "same clone inside coordinator.py (detector control)"),
    ("B2_private_reach", "BAD", COUPLING, "5 new coord._private reads in pump_arbiter.diagnostics_view"),
    ("B3a_passthrough_chain_optimize", "BAD", CC_LOC, "optimizer.optimize (CC48) cut into 4 tail-call fragments passing all locals"),
    ("B3b_passthrough_chain_coordinator", "BAD", CC_LOC | {"coordinator_methods"}, "_update_current_state cut into 4 tail-call fragments"),
    ("B3c_passthrough_chain_greedy", "BAD", CC_LOC, "top-5 CC functions greedily tail-split until no fragment >15 has a legal cut"),
    ("B4a_inplace_write_shared_dict", "BAD", {"coordinator_attrs", "coordinator_multiassigned_attrs"}, "per-solve values written into self._current_action[...] before an await"),
    ("B4b_inplace_write_new_attr", "BAD", {"coordinator_attrs", "coordinator_multiassigned_attrs"}, "per-solve value as new self._solve_prices (init + async writer)"),
    ("B4c_inplace_write_via_helper", "BAD", {"coordinator_attrs", "coordinator_multiassigned_attrs"}, "same new attr, written via module-level _note_solve_prices(coord)"),
    ("B5a_dead_method", "BAD", {"dead_methods"}, "dead coordinator method, unique name"),
    ("B5b_dead_property", "BAD", {"dead_methods"}, "dead coordinator @property"),
    ("B5c_dead_method_common_name", "BAD", {"dead_methods"}, "dead coordinator method named 'summary' (name used elsewhere)"),
    ("B5d_dead_method_selfcalled", "BAD", {"dead_methods"}, "two dead methods, one calls the other"),
    ("B5e_dead_top_level", "BAD", {"dead_top_level_symbols"}, "dead top-level function (detector control)"),
    ("B6_cyclic_import", "BAD", {"local_imports"}, "module-level away<->boost import cycle"),
    ("B6b_cyclic_import_local", "BAD", {"local_imports"}, "same cycle via function-scope import"),
    ("B7_god_helper_module", "BAD", {"coordinator_attrs", "coordinator_methods", "coordinator_loc"} | COUPLING, "same 5 freq methods -> free functions f(coord) reaching privates; state stays"),
    ("B8_star_import_const", "BAD", {"const_modules_over_50"}, "coordinator: 264-name const import -> from .const import *"),
    ("N1_rename_local", "NULL", set(), "rename local reader->input_reader in _update_current_state"),
    ("N1b_reformat_signature", "NULL", set(), "re-wrap peak_cost_smooth's 11-param signature (AST identical)"),
    ("N1c_reformat_explode_call", "NULL", set(), "explode 12 calls one-arg-per-line in _optimize_with_dhw (AST identical)"),
    ("N2_docstring", "NULL", set(), "+4 docstring lines on _optimize_with_dhw and a coordinator method"),
    ("N3_seam_relabel", "NULL", set(), "move one method's label in tests/seam_map.json (no code change)"),
    ("N4_const_namespace_import", "NULL", set(), "coordinator: 264-name const from-import -> `from . import const` + const.X"),
]


def grade(cls, targeted, d):
    if cls == "NULL":
        return ("0", "OK" if d == 0 else "WRONG")
    if cls == "GOOD":
        exp = "<0" if targeted else "<=0"
        if d > 0:
            return (exp, "WRONG")
        return (exp, "MISS" if targeted and d == 0 else "OK")
    exp = ">0" if targeted else ">=0"
    if d < 0:
        return (exp, "WRONG")
    return (exp, "MISS" if targeted and d == 0 else "OK")


rows = ["perturbation\tclass\tmetric\tbase\tafter\tdelta\texpected\tverdict\ttargeted"]
summary = {}
for name, cls, targets, _desc in P:
    f = OUT / f"{name}.json"
    if not f.exists():
        continue
    after = json.loads(f.read_text())
    for m in METRICS:
        d = after[m] - base[m]
        exp, v = grade(cls, m in targets, d)
        rows.append(f"{name}\t{cls}\t{m}\t{base[m]}\t{after[m]}\t{d:+d}\t{exp}\t{v}\t{'y' if m in targets else ''}")
        summary.setdefault(m, []).append((name, d, v))
(A / "matrix.tsv").write_text("\n".join(rows) + "\n")

# compact wide view: metric rows, perturbation columns, nonzero deltas with flags
names = [p[0] for p in P if (OUT / f"{p[0]}.json").exists()]
short = [n.split("_")[0] for n in names]
wide = ["metric\t" + "\t".join(short)]
for m in METRICS:
    cells = []
    for n, d, v in summary[m]:
        flag = {"OK": "", "WRONG": "!", "MISS": "?"}[v]
        cells.append(f"{d:+d}{flag}" if (d or flag) else "0")
    wide.append(m + "\t" + "\t".join(cells))
(A / "matrix_wide.tsv").write_text("\n".join(wide) + "\n")
print("\n".join(wide))
