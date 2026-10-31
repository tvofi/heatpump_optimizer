#!/usr/bin/env python3
"""ARCH-s3 harness: does family_splits' Python sort approximation agree with the collator HA's
frontend actually sorts entity names with (Intl.Collator(<language>))?

Metric: for en and sv, (a) order_disagreements = adjacent-pair inversions between
family_splits.sort_key(lang) and Node's Intl.Collator(lang).compare over the shipped catalogue
names, and (b) collator_splits = declared families (family_splits.families(rows, "DECLARED"))
that are not one contiguous run in the collator order. The headline the score uses is
family_splits.measure(root)["value"]; a disagreement that changes a split is an instrument gap.

Run:     PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s3/family_sort_collator.py [--perturb]
         --perturb renames one en catalogue name in a temp copy (sensor.prediction_accuracy ->
         "Zz prediction error") so the prediction family must split under both orders: both the
         metric and collator_splits_en must read +1 (the control that the comparison is live).
Root:    the working directory. Node >= 18 with full ICU on PATH.
Expected at baseline 554e2ecfa: metric 0, collator_splits_en=0, collator_splits_sv=0.
Machine: macOS arm64, tvofi's audit box. Counts only.
Instrumented: archscore.metrics.family_splits:measure / sort_key / families.
"""
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path.cwd()
sys.path[:0] = [str(ROOT / "tools" / "audit")]
from archscore.metrics import family_splits as F  # noqa: E402

NODE = r"""
const rows = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
const out = {};
for (const [lang, idx] of [['en', 2], ['sv', 3]]) {
  const c = new Intl.Collator(lang);
  out[lang] = rows.map((r, i) => i).sort((a, b) => c.compare(rows[a][idx], rows[b][idx]));
}
console.log(JSON.stringify(out));
"""


def measure(root: Path, tmp: Path) -> dict:
    rows = F.load_rows(root)
    F.OV.clear()
    F.OV.update(F.overrides(root))
    fam = F.families(rows, "DECLARED")
    (tmp / "rows.json").write_text(json.dumps(rows))
    (tmp / "sort.js").write_text(NODE)
    order = json.loads(subprocess.run(["node", str(tmp / "sort.js"), str(tmp / "rows.json")],
                                      capture_output=True, text=True, check=True).stdout)
    res = {"metric": F.measure(root)["value"]}
    for lang, idx in (("en", 2), ("sv", 3)):
        py = sorted(range(len(rows)), key=lambda i: F.sort_key(lang)(rows[i][idx]))
        icu = order[lang]
        pos = {r: n for n, r in enumerate(icu)}
        res[f"order_disagreements_{lang}"] = sum(1 for a, b in zip(py, py[1:]) if pos[a] > pos[b])
        seq = [(rows[i][0], rows[i][1]) for i in icu]
        res[f"collator_splits_{lang}"] = sum(1 for m in fam.values() if F.runs(seq, m) > 1)
    return res


def main() -> None:
    t_cpu, th_cpu = time.process_time(), time.thread_time()
    with tempfile.TemporaryDirectory(prefix="arch-s3-fam-") as tmp:
        tmp = Path(tmp)
        for k, v in measure(ROOT, tmp).items():
            print(f"RESULT {k}={v} count")
        if "--perturb" in sys.argv:
            dst = tmp / "tree" / "custom_components" / "heatpump_optimizer"
            shutil.copytree(ROOT / "custom_components" / "heatpump_optimizer", dst)
            p = dst / "translations" / "en.json"
            d = json.loads(p.read_text())
            d["entity"]["sensor"]["prediction_accuracy"]["name"] = "Zz prediction error"
            p.write_text(json.dumps(d))
            for k, v in measure(tmp / "tree", tmp).items():
                print(f"RESULT perturb_{k}={v} count")
    print(f"RESULT thread_factor={(time.process_time() - t_cpu) / max(time.thread_time() - th_cpu, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
