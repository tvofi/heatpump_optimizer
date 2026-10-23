Base-pinned grading of P2b, simulated (reviewer's own instrument, disclosed):
- base B = 9c9d276e051d4cda04ae9df29433814bdedee4f8 = origin/main c6ef06684 merged with head f8c05fbf7e1ddaf4d15652b88cd40b77372df0f6 (merge-tree, clean)
- P2b assembly = 1cce735c3 (origin/handoff/r10-ci-layout-p2-probe-B1 == -probe-B2, the newest assembly; B1 #2656 and B2 #2657 are cut from it)
- checkout = 2d66d61abcc0989b731dd9b5f04a01911b57c317 = B merged with 1cce735c3 (clean), as a pull_request run's merge ref would be once P2b merges main
- each job's pathspec list was taken verbatim from 1cce735c3:.github/workflows/governance.yml and restored from B (restore.sh), then the job's run steps were executed as written
policy-docs: rules_sync ok, codeowners_gap --check ok, policy_lint TOTAL 0 with "the live set is the recorded PRE-CUT-OVER shape" (live ruleset read), fragments_sync ok, --hooks ok  => GREEN
  null (same checkout, graders restored from origin/main): policy_lint TOTAL 37 error(s)  => the CI red reproduced
env-matrix: 16 declared outcome(s) held, 0 did not, across 6 environment shape(s)  => GREEN
wave-script: check-wave-script 209 passed; agreement_py --out ok (no FileNotFoundError); agreement.mjs --py-json:
  UNREGISTERED "[0-9a-f]{40}"; UNREGISTERED "DERIVED=\$\(.*?\)"; UNREGISTERED "fast\)\s+(SCRIPTS=.*?) ;;"
  RESULT divergent=0 unregistered=3 dead=0 refused=0  AGREEMENT REFUSED  => RED
  with 1cce735c3's own agreement.mjs in place of the restored one: unregistered=0, AGREEMENT ok
  the three SHARED_GRAMMARS entries added to the head's agreement.mjs over main's tree: dead=3 (refused), so they cannot simply land on main
