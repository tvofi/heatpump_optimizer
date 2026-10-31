Fix review: merge d1ee705999d5c3de1ac5d071bb8fd91051dbbd4c

bus-nonce: 1decc9fc90c8761d9c30068b4489144b

Round 1. Head measured: d1ee705999d5c3de1ac5d071bb8fd91051dbbd4c (record PR, two added files: dev/programme/triage/s6-batch78.md, dev/programme/delivery/3020.md; no production code).

## Findings

None.

## Evidence

- RESULT cited code resolves at origin/main 5d4e0bcfb: `def run_queue` at roster_queue.py:93; `_git` at 45-46 is a bare subprocess.run with cwd=; the lint-clone fetch/checkout at 123-124. The packet's figure_lint printed 1 resolved, 1 not verified (a git-show reference), 0 refused.
- RESULT a missing cwd makes subprocess.run raise FileNotFoundError (re-run here), which agrees with the claimed mechanism: raise before rep() writes a line.
- RESULT P300 overlap: s6-batch68.md#P300 exists at main and adds `--mark` (#done/#refused) to the same run_queue; the stated order (distinct seams, second to land merges main) is consistent with it.
- RESULT triage gate: carry_audit at head 0 findings; no refusals or advisories; merge-tree against origin/main exit 0, no conflicts; no VERSION, manifest or notes change; no claim, closure or budget file touched.
- RESULT CI: merge_train.py classify at this head returned GREEN (pending none, red none).
- Not verified (out of tree, on the orchestrator's machine): the ledger lines 2765-2769 and the count of 17 FileNotFoundError lines, the queue lines 520/532, the group file s8/beatrace/R10-FLY-BEAT-FETCH-RACE.json, the claim that the group is absent from origin/handoff/audit-r10-roster, and the held op b78-P315.txt (not in the tree, so I could not compare it with the ruling). The ruling's own wording is consistent with the in-tree facts; those figures stand as the orchestrator's account.
- No mutation proof applies: the PR writes no production code; the mutant the carry text names belongs to the carry's later fixer.
