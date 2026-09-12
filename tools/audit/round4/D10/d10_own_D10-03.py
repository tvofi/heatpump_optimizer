#!/usr/bin/env python3
"""D10-03 (seat 1 own harness) — does the root entry alias leave runtime_data Any?

METRIC (own, differs from the finder's probe): the finder's probe imported the
two aliases and revealed `entry.runtime_data`. This harness measures the claim
at its production sites instead:
  (1) AST: every module-level binding of HeatPumpOptimizerConfigEntry in the
      package, with its exact RHS text;
  (2) AST: for each of the three functions Home Assistant calls
      (async_setup_entry, async_update_options, async_unload_entry) in
      __init__.py, the annotation on the `entry` parameter, resolved to the
      module-local alias binding it names, plus the count of
      `entry.runtime_data` loads/stores inside that function;
  (3) the real stub's own declaration of ConfigEntry (PEP 696 default) and
      runtime_data, read out of the stub file, not recalled;
  (4) an OWN mypy probe (arm B venv: homeassistant-stubs 2025.4.4, mypy 2.3.1)
      whose functions carry the EXACT production signature
      `(hass: HomeAssistant, entry: HeatPumpOptimizerConfigEntry)` importing
      the alias from the package root, revealing `entry.runtime_data` AND
      `entry.runtime_data.effective_config` (an attribute only the coordinator
      declares) -- if the root alias is bare, both reveal Any and the second
      one is the unchecked production access async_update_options makes.

RUN (from the worktree root):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D10/d10_own_D10-03.py

EXPECTED (if the finding holds):
    RESULT root_alias_rhs=ConfigEntry
    RESULT entry_points_annotated_with_root_alias=3 of 3
    RESULT runtime_data_uses_in_entry_points=3
    RESULT stub_configentry_decl=class ConfigEntry[_DataT = Any]:
    RESULT probe_root_runtime_data=Any
    RESULT probe_root_effective_config=Any
BASELINE 7dd68dd; run at branch head 0855277 (custom_components unchanged
between the two).
MACHINE: 8-core Apple M1, macOS 25.6.0. Counts/type names, not timings.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(".").resolve()
PKG = ROOT / "custom_components" / "heatpump_optimizer"
ARM_B = Path("/private/tmp/hpo-d10-mypy13/venv/bin/python")

ENTRY_POINTS = ("async_setup_entry", "async_update_options", "async_unload_entry")
ALIAS = "HeatPumpOptimizerConfigEntry"


def module_alias_bindings(path: Path) -> list[str]:
    """RHS text of every module-level `ALIAS = ...` assignment, in file order."""
    out = []
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == ALIAS:
                    out.append(ast.unparse(node.value))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                and node.target.id == ALIAS and node.value is not None:
            out.append(ast.unparse(node.value))
    return out


def entry_point_facts(path: Path) -> list[dict]:
    facts = []
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in ENTRY_POINTS:
            ann = next(
                (ast.unparse(a.annotation) for a in node.args.args if a.arg == "entry"),
                "(none)",
            )
            rd = 0
            for sub in ast.walk(node):
                if isinstance(sub, ast.Attribute) and sub.attr == "runtime_data":
                    rd += 1
            facts.append({"fn": node.name, "entry_annotation": ann, "runtime_data_uses": rd})
    return facts


def probe() -> dict[str, str]:
    if not ARM_B.exists():
        return {"skipped": f"arm B venv missing: {ARM_B}", "runtime_data": "(not run)",
                "effective_config": "(not run)"}
    with tempfile.TemporaryDirectory(prefix="hpo-v-d10-own3-") as td:
        probe_py = Path(td) / "own_probe.py"
        probe_py.write_text(
            "from homeassistant.core import HomeAssistant\n"
            f"from custom_components.heatpump_optimizer import {ALIAS}\n"
            "\n"
            "async def async_unload_entry_shape(  # the production signature\n"
            "    hass: HomeAssistant, entry: HeatPumpOptimizerConfigEntry\n"
            ") -> bool:\n"
            "    reveal_type(entry.runtime_data)\n"
            "    reveal_type(entry.runtime_data.effective_config)\n"
            "    return True\n",
            encoding="utf-8",
        )
        r = subprocess.run(
            [str(ARM_B), "-m", "mypy", "--strict", "--no-error-summary",
             "--no-incremental", "--cache-dir", str(Path(td) / "cache"),
             "--python-version", "3.13", str(probe_py)],
            capture_output=True, text=True, cwd=str(ROOT),
            env={k: v for k, v in os.environ.items()
                 if k not in ("MYPYPATH", "PYTHONPATH")},
        )
        rev = re.findall(r'Revealed type is "(.+?)"', r.stdout)
        return {
            "runtime_data": rev[0] if len(rev) > 0 else f"(probe rc={r.returncode})",
            "effective_config": rev[1] if len(rev) > 1 else f"(probe rc={r.returncode})",
        }


def main() -> int:
    init = PKG / "__init__.py"
    coord = PKG / "coordinator.py"

    root_bindings = module_alias_bindings(init)
    coord_bindings = module_alias_bindings(coord)
    print(f"RESULT root_alias_bindings={len(root_bindings)}: {root_bindings}")
    print(f"RESULT coordinator_alias_bindings={len(coord_bindings)}: {coord_bindings}")
    bare = root_bindings == ["ConfigEntry"]

    facts = entry_point_facts(init)
    used_root = sum(1 for f in facts if f["entry_annotation"] == ALIAS)
    rd_uses = sum(f["runtime_data_uses"] for f in facts)
    print(f"RESULT entry_points_found={len(facts)} of {len(ENTRY_POINTS)}")
    print(f"RESULT entry_points_annotated_with_root_alias={used_root} of {len(facts)}")
    print(f"RESULT runtime_data_uses_in_entry_points={rd_uses} attribute_accesses")
    for f in facts:
        print(f"    {f['fn']}: entry: {f['entry_annotation']}, runtime_data uses: {f['runtime_data_uses']}")

    stub_path = ARM_B.parent.parent / "lib" / "python3.13" / "site-packages" / \
        "homeassistant-stubs" / "config_entries.pyi"
    decl = "(stub not found)"
    rd_decl = "(stub not found)"
    if stub_path.exists():
        text = stub_path.read_text(encoding="utf-8")
        m = re.search(r"^class ConfigEntry\[[^\]]*\]:", text, re.M)
        if m:
            decl = m.group(0)
        m2 = re.search(r"^\s+runtime_data: \S+", text, re.M)
        if m2:
            rd_decl = m2.group(0).strip()
    print(f"RESULT stub_configentry_decl={decl}")
    print(f"RESULT stub_runtime_data_decl={rd_decl}")

    p = probe()
    if "skipped" in p:
        print(f"RESULT probe=skipped {p['skipped']}")
    else:
        print(f"RESULT probe_root_runtime_data={p['runtime_data']}")
        print(f"RESULT probe_root_effective_config={p['effective_config']}")

    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=n/a (counts/type names, not timings)")
    verdict = bare and used_root == len(facts) == 3
    print("VERDICT root_alias_bare_and_used_by_entry_points=" + str(verdict))
    return 0


if __name__ == "__main__":
    sys.exit(main())
