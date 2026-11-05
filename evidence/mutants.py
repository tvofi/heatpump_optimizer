"""Reviewer's mutants on the ledger.py resolution at the head. Each: copy wtH, apply one
exact replacement (asserting it hits once), run the full tests/features.py, record rc and
failing lines. Usage: python3 mutants.py <name> [<name> ...]; 'null' applies nothing."""
import re
import shutil
import subprocess
import sys
from pathlib import Path

W = Path("/tmp/tmp.KVLBZkC6X5")
F = "custom_components/heatpump_optimizer/ledger.py"
RAW = "(1.0 if self.meter_calibration(key) is None else self.meter_calibration(key))"
MUT = {
    "null": [("    def savings_months(", "    # reviewer null\n    def savings_months(")],
    "floordel": [("                calibration = max(1.0, calibration)\n", "                pass\n")],
    "floormin": [("calibration = max(1.0, calibration)", "calibration = min(1.0, calibration)")],
    "stored_drop": [('["sek"] * scale + stored_sek', '["sek"] * scale')],
    "split_scale": [
        ('stored_sek = 0.0 if cop is None or actual["kwh"] <= 0 else scale * (',
         f'stored_sek = 0.0 if cop is None or actual["kwh"] <= 0 else {RAW} * ('),
        ('comfort_sek = self.line(key, SAVINGS_COMFORT_LINE)["sek"] * scale',
         f'comfort_sek = self.line(key, SAVINGS_COMFORT_LINE)["sek"] * {RAW}'),
    ],
    "stored_unscaled": [('stored_sek = 0.0 if cop is None or actual["kwh"] <= 0 else scale * (',
                         'stored_sek = 0.0 if cop is None or actual["kwh"] <= 0 else 1.0 * (')],
    "comfort_unscaled": [('comfort_sek = self.line(key, SAVINGS_COMFORT_LINE)["sek"] * scale',
                          'comfort_sek = self.line(key, SAVINGS_COMFORT_LINE)["sek"]')],
    "oldbasis_off": [("old_basis = self.meta_mean(key, REFERENCE_BASIS_META) != REFERENCE_BASIS",
                      "old_basis = False")],
}


def run(name):
    dst = W / f"mut_{name}"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(W / "wtH", dst, symlinks=True)
    p = dst / F
    src = p.read_text()
    for old, new in MUT[name]:
        assert src.count(old) == 1, (name, old, src.count(old))
        src = src.replace(old, new)
    p.write_text(src)
    env = {"PYTHONPATH": "tests/hastub", "OPENBLAS_CORETYPE": "Haswell", "PATH": "/opt/hpo/venv-ci/bin:/usr/bin:/bin",
           "HOME": "/root"}
    r = subprocess.run([sys.executable, "tests/features.py"], cwd=dst, env=env, capture_output=True, text=True)
    out = r.stdout + r.stderr
    (W / "ev" / f"mutant_{name}.log").write_text(out)
    fails = [l for l in out.splitlines() if re.search(r"FAIL|Traceback|Error:|PASSED", l)]
    summary = f"MUTANT {name} rc={r.returncode}\n" + "\n".join("  " + l[:400] for l in fails[:12])
    shutil.rmtree(dst)
    return summary


if __name__ == "__main__":
    for n in sys.argv[1:]:
        s = run(n)
        print(s, flush=True)
        with open(W / "ev" / "mutants_summary.txt", "a") as fh:
            fh.write(s + "\n")
