"""r3_classprobe: my own harness for #2320 round 3. It plants one spelling of the layer coupling at a
time into the pinned tree's silent_mode.py and reads the score at the instrument of the tree it is run
from. Named as the reviewer's own, not the finder's (fix-review.md 9).

  python3 r3_classprobe.py <tree-with-tools> <pin-dir> [spelling ...]

Prints one RESULT line per spelling: verdict, dS, and the metrics that moved.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

TREE = Path(sys.argv[1]).resolve()          # worktree whose instrument is measured
PIN = Path(sys.argv[2]).resolve()           # extracted pinned package tree
sys.path.insert(0, str(TREE / "tools" / "audit"))

from archscore import score, vector  # noqa: E402

ORIG = "from .optimizer import _utc_step_starts\n"
PKG = "custom_components.heatpump_optimizer"
P = PKG + ".optimizer"


def _edit(import_stmt: str, callee: str):
    """Replace the pinned import line with IMPORT_STMT and every call site's callee with CALLEE."""
    def go(src: str) -> str:
        assert src.count(ORIG) == 1, "pin anchor not found"
        src = src.replace(ORIG, import_stmt)
        assert "_utc_step_starts(" in src
        return src.replace("_utc_step_starts(", callee)
    return go


def _raw(fn):
    """A spelling written directly as a function of the source."""
    return fn


def _prepend(text: str, import_stmt: str, callee: str):
    """As _edit, plus TEXT inserted before the import statement (a module-level constant)."""
    def go(src: str) -> str:
        assert src.count(ORIG) == 1, "pin anchor not found"
        src = src.replace(ORIG, text + import_stmt)
        return src.replace("_utc_step_starts(", callee)
    return go


CALL = "_utc_step_starts("  # includes the open paren: it replaces the call site's callee

SPELLINGS: dict = {
    # --- the four this round pins (control: NULL at the head, IMPROVES at the round-2 head) ---
    "28_import_abs_alias": _edit(f"import {P} as _o\n", "_o." + CALL),
    "29_import_abs_plain": _edit(f"import {P}\n", f"{P}." + CALL),
    "30_from_abs_module_alias": _edit(f"from {PKG} import optimizer as _o\n", "_o." + CALL),
    "31_import_module_kw": _edit(
        "import importlib\n", f'importlib.import_module(name=".optimizer", package=__package__)._utc_step_starts('),
    # --- siblings under the same rule: does the diff see these too? ---
    "S1_import_abs_pkg_then_dotted": _edit(f"import {PKG}\n", f"{P}." + CALL),
    "S2_from_abs_module_plain": _edit(f"from {PKG} import optimizer\n", "optimizer." + CALL),
    "S3_getattr_alias": _edit(f"import {P} as _o\n", f'getattr(_o, "_utc_step_starts")('),
    "S4_import_parent_ns": _edit(
        "import custom_components as _cc\n", "_cc.heatpump_optimizer.optimizer._utc_step_starts("),
    "S5_from_parent_ns": _edit("from custom_components import heatpump_optimizer\n",
                               "heatpump_optimizer.optimizer._utc_step_starts("),
    "S6_relative_module_alias": _edit("from . import optimizer as _o\n", "_o." + CALL),
    "S7_import_module_const_anchor": _edit(
        "import importlib\n", f'importlib.import_module(".optimizer", "{PKG}")._utc_step_starts('),
    "S8_module_const_name": _prepend(
        "_MOD = \".optimizer\"\n", "import importlib\n", f'importlib.import_module(_MOD, __package__)._utc_step_starts('),
    "S9_dunder_abs": _edit("", f'__import__("{P}", fromlist=["_utc_step_starts"])._utc_step_starts('),
    "S10_dunder_dict_alias": _edit(f"import {P} as _o\n", f'_o.__dict__["_utc_step_starts"]('),
    "S11_from_importlib_alias": _edit("from importlib import import_module as _im\n",
                                      f'_im(".optimizer", __package__)._utc_step_starts('),
    "S12_alias_then_attr": _prepend(
        "_m = _o\n", f"import {P} as _o\n", "_m." + CALL),
    "S13_import_module_plain_rel": _edit("import importlib\n",
                                         f'importlib.import_module(".optimizer", __package__)._utc_step_starts('),
    "T1_import_pkg_alias_then_subattr": _edit(f"import {PKG} as _p\n", "_p.optimizer." + CALL),
    "T2_from_parent_child_alias": _edit("from custom_components import heatpump_optimizer as _p\n", "_p.optimizer." + CALL),
    "T3_import_parent_plain": _edit("import custom_components\n", "custom_components.heatpump_optimizer.optimizer." + CALL),
    "T4_relative_module_noalias": _edit("from . import optimizer\n", "optimizer." + CALL),
    "T5_getattr_parent_chain": _edit("import custom_components as _cc\n", 'getattr(getattr(_cc, "heatpump_optimizer"), "optimizer").' + CALL),
    # --- round-4 seam hunt ---
    "U1_ancestor_public_read": _edit("import custom_components as _cc\n", "_cc.heatpump_optimizer.optimizer.some_public_name("),
    "U2_fn_local_const_name": _raw(lambda src: src.replace(ORIG, "import importlib\n").replace(
        "    if fraction >= 1.0", '    _M = ".optimizer"\n    if fraction >= 1.0', 1).replace(
        "_utc_step_starts(", 'importlib.import_module(_M, __package__)._utc_step_starts(')),
    "U4_annassign_const_name": _prepend('_MOD: str = ".optimizer"\n', "import importlib\n",
        'importlib.import_module(_MOD, __package__)._utc_step_starts('),
    "U16_getattr_const_name_rel": _prepend('_NAME = "_utc_step_starts"\n', "from . import optimizer as _o\n",
        'getattr(_o, _NAME)('),
    "U17_getattr_const_name_anc": _prepend('_NAME = "_utc_step_starts"\n', "import custom_components as _cc\n",
        'getattr(_cc.heatpump_optimizer.optimizer, _NAME)('),
    "U12_dunder5arg_level": _edit("", '__import__(".optimizer", globals(), locals(), ["_utc_step_starts"], 1)._utc_step_starts('),
    "U19_ancestor_getattr_const_control": _edit("from custom_components import heatpump_optimizer as _p\n",
        'getattr(_p.optimizer, "_utc_step_starts")('),
    # --- round-5 seam hunt ---
    "V1_tuple_const": _prepend('_MOD, _X = ".optimizer", 1\n', "import importlib\n",
        'importlib.import_module(_MOD, __package__)._utc_step_starts('),
    "V2_binop_const": _prepend('_MOD = "." + "optimizer"\n', "import importlib\n",
        'importlib.import_module(_MOD, __package__)._utc_step_starts('),
    "V4_computed_getattr_ancestor_private": _edit("import custom_components as _cc\n",
        'getattr(_cc.heatpump_optimizer.optimizer, "_utc" + "_step_starts")('),
    "V5_deep_chain_ancestor": _edit("import custom_components as _cc\n",
        "_cc.heatpump_optimizer.optimizer._utc_step_starts.__call__("),
    "V6_fn_local_const_kw": _raw(lambda src: src.replace(ORIG, "import importlib\n").replace(
        "    if fraction >= 1.0", '    _M = ".optimizer"\n    if fraction >= 1.0', 1).replace(
        "_utc_step_starts(", 'importlib.import_module(name=_M, package=__package__)._utc_step_starts(')),
    "S14_from_dot_optimizer_f": _edit("from .optimizer import _utc_step_starts as _f\n", "_f("),
}


def main() -> int:
    names = sys.argv[3:] or list(SPELLINGS)
    with tempfile.TemporaryDirectory(prefix="r3probe-") as tmp:
        tmp = Path(tmp)
        base_tree = tmp / "base"
        shutil.copytree(PIN, base_tree)
        base = vector.measure(base_tree)
        for name in names:
            t = tmp / ("case_" + name)
            shutil.copytree(PIN, t)
            p = t / "custom_components/heatpump_optimizer/silent_mode.py"
            p.write_text(SPELLINGS[name](p.read_text()))
            cur = vector.measure(t)
            d = score.delta(base, cur)
            moved = {m: f"{base.get(m)}->{cur.get(m)}" for m in cur
                     if m in base and base.get(m) != cur.get(m) and not m.startswith("_")}
            print(f"RESULT spelling {name} verdict={d['verdict']} dS={d['dS']:+.4f} moved={moved}",
                  flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
