Fix review: merge dee7a1fa45bb9a4b2843ef0ce6c26fac6094bae8

bus-nonce: 47cc22d78dca2e0db5318c5d3f39b4b1

Scoped body re-check only; head unchanged since the previous block (review commit 77cee4db), no code or mutants re-run.

## Evidence

- classify at the head: GREEN, pending none, red none, rc=0 (ev/classify.txt).
- merge-tree against origin/main: see ev/merge-tree.txt (rc recorded there).
- owed-reds (ev/owed-reds.txt) prints the required-context set, not a per-PR red list: it takes no --pr/--head, and no listed context is red at this head. The two reds the previous run listed are green: governance / wave-script success (job 129840403888) and tests / fast (3.14) success (job 129840406342).
- Required contexts at the head: pr-contract success on the latest run (job 129840450841 at 12:44:35Z, and 129839268293 at 12:49Z); the 12:28:58Z failure (129840407903) is the one the body explains. gate success, also on the runs of 12:50-12:52Z. budget-raise-gate, arch-score, hassfest, codeql, tests/* all success. governance / delivery-status failed but is outside the required set (owner ruling 2026-11-09), so it is not a block.
- Body ## Red checks answers wave-script: cause (the roster_edit.py to roster_lib.py registration move on main made the grammar UNREGISTERED), process state (base skew, cured by the main merge), countermeasure (ci_predict.py wave-script arm, standing cost nil) and a recorded dismissal.
- Body wording finding resolved: tests / fast (3.14) now names the stress.py memory reading (typical_slab/shoulder 3.9 MiB vs 1.8 MiB) fixed by #3406, and separates the earlier de.json / C112 red (#3378). It carries a cause, a cheaper-detector statement (none) and a dismissal.
- The pr-contract and delivery-status entries are answered as well.

## Findings

none
