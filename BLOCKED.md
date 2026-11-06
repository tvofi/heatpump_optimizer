# BLOCKED: r10-fly-cloud-frugal-off

Still blocked, now on the owner's 2026-11-06 approval. The owner approved this change ("FLY-CLOUD-FRUGAL-OFF should be implemented"), so this is not an approval gap.

The edit to `.claude/settings.json` (add `"env": { "FRUGAL_ALLOW_INLINE": "1" }`, the variable `guard_inline.py` names in its refusal) was refused again by the auto-mode classifier as `[Self-Modification]`. The refusal stands; I did not route around it with a shell write.

Question for the owner: how should the edit land? Options that fit the classifier: a user-applied edit to `.claude/settings.json` on `fix/r10-fly-cloud-frugal-off`, or a session permission that allows this one file for this seat. Once the change is in the tree, the fixer resumes: JSON validation, the 8-call cloud control, the scoped gate and the handoff.

State at the stop:
- Branch cut from origin/main at 9cbd7dd0d; no code change in the tree.
- cloud-setup check: OK (venv-ci python3); numpy 2.5.4 and scipy 1.18.1 match tests/requirements-ci.txt.
- Variable name read from the plugin's `guard_inline.py`: `FRUGAL_ALLOW_INLINE`, value `"1"`.
- Not run: the cloud control and the scoped gate, since there is no change to test yet.
