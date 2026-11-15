Fix review: merge 7f4a9be89c98d6ff59dc396c479b95b73b761cf6

bus-nonce: c672b47338407dcd219cca608cbdd231

## Findings

- The PR body's text is stale in two places at this head. `pr-contract` passed it, and the Raise justification does carry the live raise, so neither blocks. (1) Under `## Red checks`, the `budget-raise-gate` bullet still describes the old key removal (`489 -> None`). The live red at 7f4a9be8 is a raise, `36 -> 40` lines and `489 -> 563` tokens. (2) The top section's older "This round's commits" block still says `grep -c proposal-triage dev/governance/config/policy_budgets.json prints 0 at this head`. At 7f4a9be8 that command prints 2. The fixer can refresh both lines at the next body push. Carry: dismissed: body hygiene on a superseded round's text, no later stage reads it, and the live raise is answered under `## Raise justification`

## Evidence

- **Round.** This is a delta round over the reviewed head bd0f383b52f98d73c15d9619ae4efeaa59024070 (`Fix review: merge`, probe/rev-3451-43597925, which had no findings).
  - The packet reads `Review scope: full` only because verdict/3451 does not name bd0f383b. The brief fixes the scope as the delta.
  - `review_carry.py bd0f383b 7f4a9be8` prints FRESH-REVIEW, because 7a12cec875 is a hand-resolved merge. So the delta was read in full.
  - The PR's measured head is 7f4a9be89c98d6ff59dc396c479b95b73b761cf6, and the body's `## Head` names the same SHA.
- **The PR's own delta.** I compared the PR's own diff at bd0f383b (three-dot from base 8af37bdf) with the one at 7f4a9be8 (base 29b3e5a7), as a sorted set of `+` and `-` lines (ev/own_delta.txt). It contains only these changes:
  - 921da41b4: the restored proposal-triage contract, the orchestrator.md section-5 bullet, the restored citations, and the CLAUDE.md row and its paid wording.
  - e69850297: one bus.sh fixture line. Its closures.json entry leaves the PR's diff, because closures.json is now byte-identical to main.
  - 7a12cec875: the hand resolution of the app_approve.sh `carry()` union, plus a fixture-only change (`refs/test/h` becomes `refs/heads/carried-bare`, and that branch is deleted after the arm).
  - The other merges are automatic: 939c91fc0e, ffaa8b57c9 and 7f4a9be89c each equal `git merge-tree` of their parents. No `custom_components/` line is in the delta, so the scope does not widen.
- **Check (1): the repair e6985029 does what its body says.**
  - At the head, `bash tools/audit/seat/bus.sh --self-test` prints `237 checks, 0 failed`, rc 0 (ev/bus_selftest_head_tail.txt).
  - **Mutant.** I removed `HPO_BUS_CLASSIFY="bash $W/classifier"` from `adopt_run`. The self-test then prints `237 checks, 1 failed`, rc 1, with `FAIL ... and bus.sh confirm signs and posts it as any reviewer's proposal` (ev/bus_selftest_mutant_noclassifier.txt). So the line is load-bearing and is the C8 interaction the body names.
  - **The closures.json entry.** `PYTHONPATH=tests/hastub python3 tests/entities.py` ran at the head and again with the `proposal-triage.md` entry deleted (ev/entities_*.txt).
    - At the head it prints `ALL 2723 ENTITY CHECKS PASSED`, rc 0.
    - **Mutant.** With the entry deleted it prints `2 of 2723 ENTITY CHECKS FAILED`, rc 1. One failure is `FAIL every tracked file is either measured or deliberately classified [these force the FULL suite when touched: dev/governance/roles/proposal-triage.md]`; the other is the citation-sources arm. So the entry is load-bearing.
  - `bash tools/pr/app_approve.sh --self-test` prints `363 checks, 0 failed`, rc 0, which matches the body.
  - `roster_edit.py --self-test` prints `311 checks, 0 failed`, matching the body.
  - `outside_intake.py --self-test` prints `all checks passed`.
  - `policy_lint.mjs` prints `TOTAL: 0 error(s) across 52 policy file(s)`. The body's 51 was counted at 921da41b, before main's merge added a file.
  - `rules_sync.mjs --check` prints `RULES-SYNC ok`, `brief_lint.mjs` exits rc 0, and `tests/structure.py` prints `STRUCTURE RATCHET PASSED` (ev/checks_head.txt).
  - The prior verdict's evidence still applies. Neither `dev/README.md` nor `tools/ci/selftest_closures.json` is touched by the delta's own lines.
- **Check (2): the owner ruling on proposal-triage.md.**
  - `git diff --name-status $(git merge-base origin/main H)...H -- dev/governance/roles/proposal-triage.md` prints `M`, so the file is not deleted (ev/merge_tree_and_triage.txt).
  - Against main's text, it changes only these places:
    - The seat sentence becomes the once-per-round paragraph, which quotes "keep it in the once per round shape". It drops "under `standing.md`", as a seat that runs once per round is not a standing one.
    - "a next-round roster group".
    - "the round's" batch file.
  - Bar, Machinery, exemption, ruling format and "You never" are main's text word for word. Nothing is reshaped beyond the ruling.
  - `standing.md` and `tests/entities.py`'s standing-terms check still omit the seat. That is consistent with it no longer being a standing seat.
- **Check (3): budgets on the head merged with origin/main 2a257fce** (merge commit 8f042edb, tree eddab085), ev/budgets-merged.txt:
  - corpus: about 69077 tokens, cap 69333.
  - always-loaded: about 3604, cap 3349 + band 500 = 3849.
  - CLAUDE.md: 213/221 lines, 3604/3605 tokens.
  - proposal-triage.md: 40/40 lines, 563/563 tokens.
  - role fixer: 6279/5852 + band 500; role record: 7236/7405 + 500; role policy: 10012/9958 + 500.
  - rc 0.
  - At the bare head: corpus about 69078 (ev/budgets-head.txt).
- **Step 14: the raise.**
  - Against main, `policy_budgets.json` moves one cap pair: `proposal-triage.md` lines 36 -> 40 and tokens 489 -> 563.
  - main's file measures 36/36 lines and 488/489 tokens, so it has no headroom.
  - The +4 lines and about +75 tokens are exactly the ruled once-per-round paragraph that replaces a two-line sentence. Taking that paragraph out takes away the growth, so the growth is earned by the ruling's text and not by the instrument.
  - I found no payment the body missed that would improve the code. Of the three payments the body lists, moving the paragraph into orchestrator.md would put the rule in a contract the triage seat does not read.
- **Merge with main.** `git merge-tree --write-tree origin/main 7f4a9be8` exits 0, tree eddab085a79300930a18df725d4638ca672f1a3b, at origin/main 2a257fce0895e9e1a77d049f879adac438517c3a.
- **Versions.** The PR's own three-dot diff touches no `VERSION`, manifest, `RELEASE_NOTES.md` or claim file (ev/own_delta.txt and the file list).
- **CI.**
  - `merge_train.py classify 7f4a9be89c98d6ff59dc396c479b95b73b761cf6 --pr 3451` exits 4: `APPROVAL-OWED 7f4a9be89c98d6ff59dc396c479b95b73b761cf6 2 budget raise(s), first .claude/workflows/policy_budgets.json: files.dev/governance/roles/proposal-triage.md: 36 -> 40 (a cap went up): a raise is the owner's (0013): tvofi's approval is on 939c91fc0e31, not this head 7f4a9be89c98` (ev/classify.out). Per the brief, I judge the head GREEN; the approval follows this verdict.
  - Live reds are `budget-raise-gate` and `gate`, both the owed approval, plus `tests / nightly-status`, which is outside `owed-reds` (ev/owed_reds.txt).
  - `governance / instrument-self-tests` is green, so no introduced step red.
- **Mutation.** The delta writes no production line, so no mutant is owed beyond the targeted fixture mutant above. CI's `tests / mutation` is a success.
