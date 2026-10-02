# R9-EG-B5a resume note (fixer seat)

- Code head: handoff/r9-eg-dhw-closure-dedupe-v2 dafa803ca025876621db0fb2d1f8c0ab794af3dd,
  the merge of origin/main 2b6c5b87 (#1838) into 5a69e874. The body lives here on
  handoff-body/r9-eg-dhw-closure-dedupe-v2. The older handoff-body/r9-eg-dhw-closure-dedupe
  is superseded.
- Stage: handed off. The branch is frozen; only the orchestrator moves it.
- At the merged head: structure.py rc=0. The production delta is byte-identical to
  5a69e874's. The claim files are untouched. prepr.sh (PREPR_SKIP_CLOSURES=1) is clean
  with MODE: SCOPED.
- The merge commit's message carries the methods_over_200 correction that was owed
  against 5a69e874.
- Not run locally (no numpy): features, mutation_table --scope changed,
  env_drift --all, stress and the other numeric scripts in the scope. CI runs them.
