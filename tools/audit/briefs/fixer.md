# The fixer's contract (the standing gate protocol as a checklist)

You own one PR group: one subsystem, at most five findings, at most about 400
production lines. You work in your own worktree branched from `origin/main`.

1. **Never touch `VERSION`, the manifest version or the `RELEASE_NOTES.md`
   heading.** Versions are assigned by `tools/release/stamp.py` after the
   merge. The reviewer checks
   `git diff origin/main -- VERSION custom_components/heatpump_optimizer/manifest.json`
   is empty.
2. **Failing test first**, importing the production symbol (a test that
   re-implements a formula pins nothing; `tests/README.md`). Record the
   mutation proof in the PR body: delete the fix's production line(s), run
   the closure, paste the failing check names, restore.
3. **Re-execute the finding's harness on your branch**: before and after, with
   the head SHA measured, in the PR body. A cost, gain or time claim carries
   its null control. A learner or guard change is measured at both ends of
   its input range — an install with zero evidence, and one sitting on the
   clamp — because a fix has been worse than its bug before, silently.
4. **Goldens that move are claimed by whoever measured the drift**, in
   `tests/golden/claimed_drift.txt` or `card_claimed_drift.txt`, with the
   expected direction per fixture. `claims-for:` stays at the current
   `VERSION`.
5. `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh`
   green locally, through the gate lock (`mkdir /tmp/hpo-gate.lock`; strict
   golden mode does not reproduce on this box, see the README), then CI green.
6. Hand off to the adversarial fix reviewer. **After any rebase, steps 2–4
   are re-executed**: the evidence describes one tree, and a rebase makes a
   new one.
7. The PR body closes its issues (`Closes #N`), names the head SHA measured,
   and carries every executed number.
