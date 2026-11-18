# BLOCKED: r11-arch-fabric-learner (fixer)

Question: The brief ("After: R11-SEAM-learners"; "the fixer still waits on R11-SEAM-learners") and the approved design (221c246ece, section 7: "the fixer waits on R11-SEAM-learners"; step 9 re-read owed at the predecessor's merge) both put this fixer behind R11-SEAM-learners, which has not merged: origin/main at 1723f9fdc9 carries no R11-SEAM-learners commit, and `git ls-remote origin` lists no dispatch, handoff or handoff-wip ref for it. Should this fixer wait for R11-SEAM-learners to merge (and the designer's step-9 revalidation of the arm at that SHA), or is it released to cut from 1723f9fdc9 now?

Evidence, re-runnable:
- `git log origin/main --format='%s%n%b' | grep -i 'seam-learners'` prints nothing at 1723f9fdc9.
- `git ls-remote origin | grep -i 'seam-learners'` prints nothing.
- Design 221c246ece section 4: the predecessor "edits the same lines" of `coordinator.py`; its revalidation stops on a moved anchor.

No code was written; no branch other than this ref was pushed.
