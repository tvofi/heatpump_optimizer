"""Round 9, Phase D class sweep -- class I5 ("Docs, comments or a compliance
checklist drift stale against the code").

I5 has no single production seam: its 19 canonical findings are stale claims
of 8 different shapes (help-text units, setup-flow prose, entity counts,
quick-setup promises, card-version banner, field-label prose, card comment
names, in-code comment numbers, README claims table, entity census, service
schema prose, translation concept names, a compliance-checklist mode line).
Ten of those shapes already had a per-shape checker built during finding
(each already scans *every* seam of its own shape across the whole package,
not only the demonstrated instance -- e.g. claims.py checks all 82 README
claims, services_claims.py all 59 service-field claims, comment_numbers.py
every numeric citation in the three files it names). This enumerator is the
class-level wrapper `D14.md` step 3 asks for: it runs every one of those
shape-checkers plus their siblings that were built but did not surface a
round-9 finding (architecture_claims, behaviour_claims, howitworks_claims,
setup_claims, scan_const_numbers, scan_qualified_refs), so the sweep covers
every seam any shape-checker can reach, and files each hit as one seam.

Command: PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/sweep/I5/enumerator.py [--base DIR]
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Pure subprocess dispatch + text parse, no timing claims of its own (each sub-harness times itself).
"""
import json
import re
import subprocess
import sys
import pathlib

# I5 -> sweep -> D14 -> round9 -> audit -> tools -> repo root: 6 parents.
ROOT = pathlib.Path(__file__).resolve().parents[6]

SHAPES = [
    dict(id="D4-s2-09", cmd=["python3", "tools/audit/round9/D4/s2/unit_typography.py"],
         result_keys=["bare_unit_help_texts_en", "bare_unit_help_texts_sv"]),
    dict(id="D5-s1-01", cmd=["python3", "tools/audit/round9/D5/s1/setup_section.py"],
         result_keys=["stale_facts"]),
    dict(id="D5-s1-02", cmd=["python3", "tools/audit/round9/D5/s1/quick_setup_promise.py"],
         result_keys=["unhonoured_promises"]),
    dict(id="D5-s1-03", cmd=["python3", "tools/audit/round9/D5/s1/card_version_doc.py"],
         result_keys=["doc_claims_card_lags"]),
    dict(id="D5-s1-05", cmd=["python3", "tools/audit/round9/D5/s1/field_labels.py"],
         result_keys=["unfindable_field_refs"]),
    dict(id="D6-s2-01/D5-s1-06/D5-s1(entity_counts)", cmd=["python3", "tools/audit/round9/D5/s1/entity_counts.py"],
         result_keys=["disagreeing_claims"]),
    dict(id="D5-s2-01", cmd=["node", "tools/audit/round9/D5/s2/card_comment_names.mjs"],
         result_keys=["card_stale_private_names"], env={"HPO_PLANDATA": "/tmp"}),
    dict(id="D5-s2-02/D5-s2-03", cmd=["python3", "tools/audit/round9/D5/s2/comment_numbers.py"],
         result_keys=["comment_number_mismatches"]),
    dict(id="D5-s2-51", cmd=["python3", "tools/audit/round9/D5/leads/dataflow_comments.py"],
         result_keys=[]),  # inspected by hand: no offset/sequence writes present
    dict(id="D6-s1-01/02/03", cmd=["python3", "tools/audit/round9/D6/s1/claims.py", "--no-net"],
         result_keys=["claims_false"]),
    dict(id="D6-s2-02", cmd=["python3", "tools/audit/round9/D6/s2/flow_census.py"],
         result_keys=["doc_entity_counts_wrong"]),
    dict(id="D6-s2-03/04", cmd=["python3", "tools/audit/round9/D6/s2/behaviour_claims.py"],
         result_keys=["behaviour_claims_false"]),
    dict(id="D6-s2-04(howitworks)", cmd=["python3", "tools/audit/round9/D6/s2/howitworks_claims.py"],
         result_keys=["howitworks_claims_false"]),
    dict(id="D6-s2-05", cmd=["python3", "tools/audit/round9/D6/s2/services_claims.py"],
         result_keys=["services_claims_false"]),
    dict(id="D8-s3-02", cmd=["python3", "tools/audit/round9/D8/s3/m3_translation.py"],
         result_keys=["concept_mismatch"]),
    # Siblings built during finding that did NOT surface a round-9 finding.
    # Run for widening: any nonzero *_false/*_mismatch beyond the known ids
    # above would be a new I5 instance.
    dict(id="(widen) architecture_claims", cmd=["python3", "tools/audit/round9/D6/s2/architecture_claims.py"],
         result_keys=["architecture_claims_false"]),
    dict(id="(widen) setup_claims", cmd=["python3", "tools/audit/round9/D6/s2/setup_claims.py"],
         result_keys=["setup_claims_false"]),
    dict(id="(widen) scan_const_numbers", cmd=["python3", "tools/audit/round9/D5/s2/scan_const_numbers.py"],
         result_keys=["const_adjacent_mismatch"]),
    dict(id="(widen) scan_qualified_refs", cmd=["python3", "tools/audit/round9/D5/s2/scan_qualified_refs.py"],
         result_keys=["qualified_ref_rows"]),  # docstring: expect 19, all false positives (not_applicable)
]

RESULT_RE = re.compile(r"^RESULT\s+(\S+)=(\S+)")


def run(shape, base):
    env = dict(**{"PYTHONPATH": "tests/hastub"})
    env.update(shape.get("env", {}))
    import os
    full_env = dict(os.environ)
    full_env.update(env)
    p = subprocess.run(shape["cmd"], cwd=str(base), env=full_env,
                        capture_output=True, text=True, timeout=120)
    out = p.stdout + p.stderr
    results = {}
    for line in out.splitlines():
        m = RESULT_RE.match(line.strip())
        if m:
            results[m.group(1)] = m.group(2)
    return out, results


def main():
    base = pathlib.Path(sys.argv[2]) if "--base" in sys.argv else ROOT
    seams = []
    for shape in SHAPES:
        try:
            out, results = run(shape, base)
        except Exception as e:  # noqa: BLE001
            print(f"ERROR running {shape['id']}: {e}")
            continue
        flagged = 0
        for k in shape["result_keys"]:
            v = results.get(k)
            if v is not None:
                try:
                    flagged += float(v)
                except ValueError:
                    pass
        seams.append(dict(id=shape["id"], cmd=" ".join(shape["cmd"]), flagged=flagged,
                           result_keys={k: results.get(k) for k in shape["result_keys"]}))
        print(f"{shape['id']:45s} flagged={flagged}")
    print(json.dumps(seams, indent=2))


if __name__ == "__main__":
    main()
