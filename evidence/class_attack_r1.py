import sys; sys.path.insert(0, sys.argv[1] + "/tools/audit"); import carry_audit as ca
H = "Fix review: merge " + "a"*40 + "\n\n"
cases = {
 "same-sentence nit": "nightly-status is not a required check, and one nit is not blocking: the usage string lists arms by hand.",
 "same-sentence minor": "composed-proof is not a required check and a minor defect stays, not blocking.",
 "same-sentence defect": "The guard misses a deleted ref, which is not a required check to fix, so not blocking.",
 "parenthetical": "The floor is written 0.27 K low (not a required check) and is not blocking.",
 "plain defect, no words": "The stale-head guard misses a deleted ref.",
 "nit word only": "One nit: the usage string lists arm names by hand.",
 "abbrev e.g. split": "composed-proof is not a required check, e.g. it does not block. One nit, not blocking: x.",
 "semicolon": "composed-proof is not a required check; not blocking: the guard misses a deleted ref.",
 "control nonblock": "The guard misses a deleted ref, not blocking.",
}
for sec in ("## Evidence", "## Notes"):
  for k, v in cases.items():
    its = [i for i in ca.items(H + sec + "\n\n- " + v + "\n", True) if i.get("why")]
    print(f"{sec:12} {k:24} -> {[i['why'] for i in its]}")
