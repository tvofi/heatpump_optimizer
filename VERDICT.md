Fix review: merge 91f2bcd4c236095d621f238d44a6ae005e3df220

bus-nonce: ef854b3cf12bc993f013716925b9bc21

## Scope

Delta review of PR #2622 (R10-CI-LAYOUT-P2, P2a) from the full review at 67942203677a3a416fc84e25161a614390c67a99 (review/2622, VERDICT.md, verdict merge) to the live head 91f2bcd4c236095d621f238d44a6ae005e3df220. The delta is a merge of origin/main de69745ff into 67942203. I reviewed nothing else; the full review stands for all content at 67942203.

## Findings

- No new finding. The delta is only main (evidence below).
- The full review findings are non-blocking as stated: (1) the statuses: write gap in the forgery pin is carried to P2b (Carry: R10-CI-LAYOUT-P2), no workflow grants it today; (2) the stale ci_probe figure (466) was already corrected to 499 in the body at 21:50Z per the orchestrator, and the PR builds exactly the approved rule. I did not re-read the body from the API (sparing it); the orchestrator reports the fix.
- CI is not yet complete: classify prints WAIT, pending Analyze (python), closures, fast (3.14); red: none. The merge train must see these green before merging.

## Evidence

- git log --no-merges 67942203..91f2bcd4c236095d621f238d44a6ae005e3df220 ^origin/main: 0 commits.
- Parents of 91f2bcd4c236095d621f238d44a6ae005e3df220: 67942203677a3a416fc84e25161a614390c67a99 and de69745ffcab66b566b3e75aee0b572023f80857.
- git merge-tree --write-tree 67942203 de69745ff gave tree 6bb681842ee3494cbba9d844910980c84a3a9aae, equal to the tree of 91f2bcd4c236095d621f238d44a6ae005e3df220. It printed LEDGER-MERGE: resolved tests/closures.json (inert_reads.tests/harness_headers.py merged as a set, 828 entries): the ledger driver resolution only.
- tools/pr/app_approve.sh --carry 67942203.. 91f2bcd4c236095d621f238d44a6ae005e3df220 origin/main printed: CARRY: yes (only automatic merges from origin/main, ci: commits and the autofix bot, and the branch own diff compares equal).
- merge_train.py classify 91f2bcd4c236095d621f238d44a6ae005e3df220: WAIT (pending Analyze (python) closures fast (3.14), red: none).
- Evidence dir: HEAD.txt holds the head SHA.
