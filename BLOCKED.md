# BLOCKED: r11-seam-actuation-writes

Question: Both predecessors named in the brief's `After:` line are unmerged at the base 107988b792139c60e3831cbd91cfe65c4db497b3 (origin/main). Should this fixer wait until R11-SEAM-kernel-step and R11-SEAM-actuation-release merge and then be re-dispatched from that main, or build on their unmerged heads?

Evidence, measured on 2026-11-18 against origin/main 107988b792139c60e3831cbd91cfe65c4db497b3:
- `git log --oneline origin/main | grep -i -E 'kernel-step|actuation-release'` prints nothing (null control: the same grep matches merge commits for other groups' topics in that log).
- R11-SEAM-kernel-step: handoff/r11-seam-kernel-step at e265279b8df87854e10ae549db9f07d2a021cac9, cut from ae0ed64af8, not on main. The approved design (28bedac8a678436dba49f3f44c18f2c2ddcd826b, section 2 Re-cut) reads `plan_step_index` from it.
- R11-SEAM-actuation-release: only handoff-wip/r11-seam-actuation-release at 1474730e65290650d3be927c8ad860e4409392d4, with no handoff head. `git diff --stat $(git merge-base <that> origin/main)...<that> -- custom_components` touches coordinator.py, pump_arbiter.py, freq_control.py, mixing_valve.py, legionella.py and off_restore.py: this group's hot files (design section 6).
- The design places this group "third on the actuation chain, after both predecessors merge", and Notes for the fixer 1 says to re-read the release group's merged diff first, because the frequency and valve tails move to freq_control.py and mixing_valve.py there and the availability predicate goes before their send in those places. Building from main now would write those tails in coordinator.py and conflict with the release diff. Building on its WIP head would build on an unreviewed tree that may still move.

No code was written. Carry: R11-SEAM-actuation-writes
