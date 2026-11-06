Two merge-train residues in tools/audit/seat/merge_train.py: a pre-flight park rejoins at the same verdict once its cause is cured (carries 3, 18), and a same-tree commit appended after the posted verdict stands for it (carry 4). Carries 0 and 1 were already on main (d69619360, 21dc06f3e: ancestors of origin/main). Carries 9-12 were implemented by #3090 (merge 38dcb6c5d); nothing is built twice. Carries 2, 5, 6, 7, 8, 13-17 are not built in this PR and stay owed (see Forward-carry).

## Head

18ee08d3ea21d822a8d98eca1a437a5a87d7b1a0 (origin/main 9315526f8 merged in; prepr.sh rerun clean after the merge).

## Mutation proof

Mutants `merge_train-43` (drop the tree comparison) and `merge_train-44` (drop the pre-flight re-read in `train_add`) in dev/audit/harnesses/r10_seat_selftests_mutants.py. Each applied alone, `python3 tools/audit/seat/merge_train.py --self-test` reads `446 checks, 1 failed` (the same-tree null arm and the uncured-park arm respectively); unmutated reads `446 checks, 0 failed`.

## Null control

Unmodified tree: the pre-flight park is recorded with no class (except the holder), so the same-verdict re-add is `ALREADY`; `posted_verdict` returns `not verdict/<n>'s tip` for any tip other than the commented sha. Controls in the self-test: a `ci` skip at the same verdict stays ALREADY; an uncured park is `ADD REFUSED` rc 1 with no spool line; a different-tree tip and a same-tree non-descendant still wait.

## Figures

- `python3 tools/audit/seat/merge_train.py --self-test` : 446 checks, 0 failed
- `python3 tests/structure.py` : STRUCTURE RATCHET PASSED
- `bash tools/pr/prepr.sh` : rc=0

## Red checks

none

## Forward-carry

The packet numbers carries 1-based (brief "Carry 0" is Carry 1 here). Dispositions:

- Carry 1: already on main (d69619360); nothing built. Carry: dismissed: done on main or in this PR
- Carry 2: already on main (21dc06f3e); nothing built. Carry: dismissed: done on main or in this PR
- Carry 3 (bot tip held-run reading, measure first): not built. Carry: dismissed: already in the group brief, unchanged and still owed
- Carry 4 (pre-flight park re-admit): built here, with Carry 19 (the widened form). Carry: dismissed: done on main or in this PR
- Carry 5 (same-tree posted verdict): built here. Carry: dismissed: done on main or in this PR
- Carry 6 (`add --wait-post-approval`): not built. Carry: dismissed: already in the group brief, unchanged and still owed
- Carry 7 (git-transport retry classifier): not built. Carry: dismissed: already in the group brief, unchanged and still owed
- Carry 8 (harness `pages()` retry): not built. Carry: dismissed: already in the group brief, unchanged and still owed
- Carry 9 (undraft): not built. Carry: dismissed: already in the group brief, unchanged and still owed
- Carry 10, Carry 11, Carry 12, Carry 13 (moved from R10-TRAIN-POSTMERGE; implemented by #3090, merge 38dcb6c5d): discharged, nothing built twice. Carry: dismissed: done on main or in this PR
- Carry 14 (batch by default): not built. Carry: dismissed: already in the group brief, unchanged and still owed
- Carry 15 (record PRs ride the stamp): not built. Carry: dismissed: already in the group brief, unchanged and still owed
- Carry 16 (remerge_main.sh push log): not built. Carry: dismissed: already in the group brief, unchanged and still owed
- Carry 17 (git-transport, same text as Carry 7): not built. Carry: dismissed: already in the group brief, unchanged and still owed
- Carry 18 (instrument page default, owner instruction 2026-11-04): not built. Carry: dismissed: already in the group brief, unchanged and still owed
- Carry 19: built here as Carry 4's widened form (`findings` and `policy` parks). Carry: dismissed: done on main or in this PR

## Friction

none
