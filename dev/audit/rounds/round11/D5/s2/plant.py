#!/usr/bin/env python3
"""Instrument harness: text_ledger.py check --plant can never pass for a D5 seat whose sorted
cell list starts with a file D5's rule reads no comments from (README.md for seat D5-s2).

Metric: plant_refused (1 = the per-seat null control passed) and check rc, for a COMPLETE ledger
(every unit rowed `no-claim`), over seat D5-s2's files in the order `seat_files` returns them
(sorted, as check_scopes.py lists them). run_check plants into files[0]; under --dim D5 a .md file
yields only its `file` unit before and after the plant, so planted_units=0 and the control fails.
Key: the units text_ledger.units_of returns for the planted copy, not a count carried here.

Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/plant.py [--perturb]
  --perturb  the fix's direction: the plant goes to the first file carrying a D5 suffix
             (files reordered in memory), so plant_refused 0 -> 1 and rc 1 -> 0.
Null control: the same complete ledger under --dim D6 over the same files (README.md first)
passes the plant (D6 reads Markdown sentences), printed as plant_refused_d6.
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (exact): plant_refused=0 rc=1
planted_units=0; --perturb plant_refused=1 rc=0; plant_refused_d6=1.
Machine: B2 (orchestrator's macOS box).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time
sys.path.insert(0, "tools/audit")
import text_ledger  # noqa: E402

FILES = sorted(["README.md", "docs/CONTRIBUTING.md", "docs/architecture.md", "docs/automations.md",
                "docs/configuration.md", "docs/dashboard-card.md", "docs/ecl110.md", "docs/how-it-works.md",
                "docs/img/card/make_card_figures.mjs", "docs/img/model/make_card_weekly_figure.mjs",
                "docs/img/model/make_model_figures.py", "docs/img/readme/make_readme_figures.py",
                "docs/img/readme/render.mjs", "docs/img/readme/render_mermaid.mjs", "docs/setup.md"])


def complete(files, dim):
    units = text_ledger.enumerate_units(".", files, dim)
    return "\n".join(["\t".join(text_ledger.HEADER)] +
                     ["\t".join([u[0], str(u[1]), "no-claim", "", "", "-", ""]) for u in units]) + "\n"


def run(files, dim):
    out = []
    rc = text_ledger.run_check(".", files, dim, complete(files, dim), True, out=out.append)
    line = next(l for l in out if "plant_refused" in l)
    return rc, line


def main():
    files = list(FILES)
    if "--perturb" in sys.argv:
        files = [f for f in files if f.endswith(text_ledger.D5_SUFFIXES)] + \
                [f for f in files if not f.endswith(text_ledger.D5_SUFFIXES)]
    rc, line = run(files, "D5")
    print(f"RESULT first_file={files[0]}")
    print(line)
    print(f"RESULT rc={rc}")
    rc6, line6 = run(FILES, "D6")
    print(line6.replace("plant_refused", "plant_refused_d6"))
    print(f"RESULT rc_d6={rc6}")
    print(f"RESULT thread_factor={time.process_time() / max(time.thread_time(), 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
