# BLOCKED: r10-hotfix-nonrequired-reds at PR head 6ef8ac12236f3ff258f19180334cbe216962dfd3

Two concluded reds are caused by this diff. This body-push seat does not touch code, so they are unrepaired.

1. `tests / closures` (required; `gate` and `tests / closures-autofix` follow it).
   `UNDER-SCOPED: tests/entities.py really reads 1 file(s) the committed closure does not list: tools/policy/budget_raise_gate.py`.
   Cause: the `_pcr_unrestored` rule this diff adds to `tests/entities.py` walks the files `policy_lint.mjs` spawns, including `tools/policy/budget_raise_gate.py`.
   Repair: `./tests/derive_closures.sh --single tests/entities.py`, then commit `tests/closures.json`. The bot's `closures-autofix` reported `skip-merge-failed`, so it will not do it.
2. `code-scanning alert 52 (js/insecure-temporary-file)` (check `CodeQL`).
   `tools/policy/policy_lint.mjs` line 4524, `fs.writeFileSync(namedAll, ...)`, where `namedAll = path.join(os.tmpdir(), 'prbody-named-<pid>.md')`.
   Repair: write into a `fs.mkdtempSync` private directory and remove it after.

The body on `handoff-body/r10-hotfix-nonrequired-reds` names every concluded red and answers it; the body check passes against it.
