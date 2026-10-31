#!/usr/bin/env python3
"""arch-a V2 (round 10 catch-up verify, ARCH2-s2 P1..P7): what each prototype removes, site by site,
and whether the patch's ADDED lines carry an in-place write the census does not count.

Independent of arch2_delta.py's weighted sum: for each patch alone on the baseline, the set
difference of shared_inplace_writes' and hub_solve_writes' site lists (base minus proto = removed,
proto minus base = added), plus a plain-text scan of the patch's '+' lines in custom_components for
mutation spellings (attribute/item store on a non-self, non-local base; .update/.append/.pop/
.setdefault/.clear/.extend; setattr; __dict__) -- each such line is printed for a human verdict, so
a site moved into a spelling the census cannot see shows up here even though the score credits it.

Metric: removed_sites / added_sites (census sets), suspect_added_lines (text scan count).
Count key: census site strings "file:line obj .field" with the line number stripped, so a pure line
          shift is not a removal.
Command:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/catchup/arch-a/v2_s2_sites.py
          from the root of a checkout whose git objects contain BASELINE.
Null control: UNION + N0_rename_null.patch (renames only) against UNION must read shared_diff 0,
          hub_diff 0 (N0 applies on the union only).
Expected: P2, P3 remove 1 shared site each; P6, P7 remove 2; P1, P4, P5 remove 0 shared sites.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tools" / "audit"))
from archscore import score  # noqa: E402
from archscore.metrics import common as C  # noqa: E402
from archscore.metrics import hub_solve_writes as H  # noqa: E402
from archscore.metrics import shared_inplace_writes as S  # noqa: E402

BASELINE = "9061fbd3d710d5894b7083d8a58b8203f9e7aa97"
D = ROOT / "dev/audit/rounds/round10/D7/arch2-s2"
PATCHES = ["UNION_P1_P7", "N0_rename_null", "P1_config_notices_owned", "P2_fixed_action_priced_whole",
           "P3_store_owns_its_digest", "P4_event_readings_published_whole", "P5_peak_billing_record",
           "P6_price_tile_rotation_owned", "P7_price_learner_owns_its_days"]
MUT = re.compile(r"\.(update|append|pop|setdefault|clear|extend|insert|remove|popitem)\(|setattr\(|__dict__"
                 r"|^\s*[A-Za-z_][\w.]*\.[\w]+(\[[^\]]*\])?\s*(\+|-|\*)?=(?!=)|^\s*[A-Za-z_][\w.]*\[[^\]]*\]\s*=(?!=)")


def strip(sites: list[str]) -> set[str]:
    return {re.sub(r":\d+ ", " ", s) for s in sites}


def census(root: Path) -> tuple[set, set]:
    C.reset_caches()
    s = S.measure(root)["details"]["sites"]
    C.reset_caches()
    pkg = C.load(str(root))
    eng = C.engine(pkg)
    hs: set = set()
    for r in H.ROOTS:
        q = f"{C.COORD_MODULE}:{C.COORD_CLASS}.{r}"
        if q in pkg.funcs:
            hs |= {f"{x[0]} {x[2]}.{x[3]}" for x in H._sites(eng, q)}
    return strip(s), hs


def main() -> int:
    t_cpu, th = time.process_time(), time.thread_time()
    with tempfile.TemporaryDirectory(prefix="archa-s2-") as tmp:
        base = score.tree_of(BASELINE, Path(tmp) / "base")
        b_s, b_h = census(base)
        print(f"RESULT base shared={len(b_s)} hub={len(b_h)} (distinct, line-stripped)")
        for p in PATCHES:
            d = score.tree_of(BASELINE, Path(tmp) / p)
            chain = ["UNION_P1_P7", p] if p == "N0_rename_null" else [p]
            for c in chain:
                subprocess.run(["git", "apply", "--include=custom_components/*", "--whitespace=nowarn",
                                str(D / f"{c}.patch")], cwd=d, check=True)
            p_s, p_h = census(d)
            if p == "UNION_P1_P7":
                u_s, u_h = p_s, p_h
            if p == "N0_rename_null":  # the null compares against the union, not the baseline
                print(f"RESULT N0_vs_union shared_diff={len(u_s ^ p_s)} hub_diff={len(u_h ^ p_h)}")
            plus = [ln[1:] for ln in (D / f"{p}.patch").read_text().splitlines()
                    if ln.startswith("+") and not ln.startswith("+++")]
            # only code lines of production files: crude but independent of the role engine
            suspects = [ln.strip() for ln in plus if MUT.search(ln) and not ln.strip().startswith(("#", "self."))
                        and "==" not in ln]
            print(f"RESULT {p} shared_removed={len(b_s - p_s)} shared_added={len(p_s - b_s)} "
                  f"hub_removed={len(b_h - p_h)} hub_added={len(p_h - b_h)} suspect_added_lines={len(suspects)}")
            for s in sorted(b_s - p_s):
                print(f"   - shared {s}")
            for s in sorted(p_s - b_s):
                print(f"   + shared {s}")
            for s in sorted(b_h - p_h):
                print(f"   - hub {s}")
            for s in suspects[:12]:
                print(f"   ? {s[:110]}")
    print(f"RESULT thread_factor={(time.process_time() - t_cpu) / max(time.thread_time() - th, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
