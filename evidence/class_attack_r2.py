import sys; sys.path.insert(0, sys.argv[1] + "/tools/audit"); import carry_audit as ca
H = "Fix review: merge " + "a"*40 + "\n\n"
cases = {
 # round 1's attack
 "r1 same-sentence nit": "nightly-status is not a required check, and one nit is not blocking: the usage string lists arms by hand.",
 "r1 same-sentence minor": "composed-proof is not a required check and a minor defect stays, not blocking.",
 "r1 same-sentence defect": "The guard misses a deleted ref, which is not a required check to fix, so not blocking.",
 "r1 parenthetical": "The floor is written 0.27 K low (not a required check) and is not blocking.",
 "r1 semicolon": "composed-proof is not a required check; not blocking: the guard misses a deleted ref.",
 # round 2: joiners the body says it left out
 "semicolon joiner, defect first": "The guard misses a deleted ref; mutation is not a required check; not blocking.",
 "so joiner, defect first": "The guard misses a deleted ref, which is not a required check so not blocking.",
 "paren joiner": "The floor is written 0.27 K low (not a required check) not blocking.",
 # round 2: the clause's own tail carries a defect's block-state
 "defect, then clause+tail": "The guard misses a deleted ref; composed-proof is not a required check, not blocking.",
 "defect, clause+tail, comma": "The floor is written 0.27 K low, but floor-check is not a required check and does not block.",
 "two clauses": "nightly-status is not a required check, not blocking, and mutation is not a required check, not blocking.",
 "clause then deferred": "composed-proof is not a required check and does not block; tightening it is a follow-up.",
 "clause then minor": "composed-proof is not a required check and does not block, a minor gap.",
 "newline-wrapped": "composed-proof is not a\nrequired check, non-blocking; one nit, not blocking: x.",
 "null: #2544 sentence": "composed-proof is queued, but it is not a required context and does not block the PR (tests.yml:2775).",
}
for sec in ("## Evidence", "## Notes"):
  for k, v in cases.items():
    its = [i for i in ca.items(H + sec + "\n\n- " + v + "\n", True) if i.get("why")]
    print(f"{sec:12} {k:32} -> {[i['why'] for i in its]}")
