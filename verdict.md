Fix review: merge 46bf82435f4060d449788b704210f3e0bc33054e

bus-nonce: 700beefffcd4d722ba75c4f02df582d9

Round: third review of #2765. This is a delta review. Round 1 (review/2765) returned `blocked 4df5a42f1 carry-missing`, and round 2 returned `blocked c3bc47e86 carry-missing: not carried to R10-ORCH-DISPATCH-REG`.

## Findings

- Still open from round 2: the Friction item ("first-pass merges" in carry (2), where the statistic is incidence) is routed to `Carry: R10-FLY-YIELD-GUARD`. The body's own Round 2 section says that group ends at this merge, so no seat reads the item after it. Route it to whoever owns the yield-probe record's carry text, or close it as recorded friction. It does not block, because the guardrail already implements incidence. Carry: R10-FLY-YIELD-GUARD
- Still open from rounds 1 and 2, an instrument gap: `carry_audit.py` reads an `absorbed` group as a live destination, and it does not check that a roster carry's text is actually in the destination group. In round 2 that is how it passed `5 routed` while two carries were absent. In this round the carries are present, but I proved that by hand (ev/carry_compare.txt), not with the tool. Carry: R10-ORCH-ROSTER-SCHEMA

## Evidence

- **Head.** The PR head is `46bf82435f4060d449788b704210f3e0bc33054e` (REST pulls API, and `git ls-remote` just before return in ev/head_at_post.txt). It matches the body's `## Head`. Its parents are the round-2 head `c3bc47e86272bc57df9aa387892b7f5dac6f9cbf` and origin/main `662a3809ced43b41dba2166f04277f2d3c95e991`.
- **Code and harness unchanged since round 2.** `git merge-tree --write-tree origin/main c3bc47e86` gives tree `eb8de68419d7`, and `git diff` of that tree against the head is empty. The head therefore equals the round-2 head plus a clean merge of main, and no file is resolved by hand (ev/delta.txt). The three-dot diff against the merge base still lists the same 5 files, 177 insertions and 8 deletions.
- **Merges with main.** `git merge-tree --write-tree origin/main 46bf82435` exits 0. The base equals origin/main, so this merge is trivial.
- **Contract is current.** `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- **The carry, which was round 2's block, is now paid** (ev/carry_compare.txt):
  - `2124781cf86064c9bba6639755f73d60b5d54627` is the tip of `origin/handoff/audit-r10-roster`.
  - Its two parents in the roster history are `226307773a1c` and `080152c524dd`, both `roster_edit append-carry R10-ORCH-DISPATCH-REG`. Each adds one carry line (`080152c52` adds the model arm, `226307773` adds the planted-defect audit). These match the commits the body cites.
  - At that SHA, R10-ORCH-DISPATCH-REG is `resume.stage: not-started` with 10 carries, so it is live.
  - `RESULT carry index=8 verbatim=True len_roster=1245 len_body=1245 precondition=True control=True`.
  - `RESULT carry index=9 verbatim=True len_roster=1397 len_body=1397 precondition=True control=True`.
  - Each states "Precondition, not opportunity" and a control with its null control, as finding-propagation.md requires. The body cites the SHA in `## Forward-carry`.
  - Disclosure: the body side of the comparison is the two Forward-carry quotes, transcribed from the PR body as the GitHub MCP read returned it into ev/body8.txt and ev/body9.txt. It was not fetched raw.
- **The other two carries** (the owner's call on a trip, and the unclassified-words lower bound) are in this PR's tree as entries of `dev/programme/carries/carry-201.json` (`effect: narrows` and `effect: invalidates`). Round 2 verified them and they are byte-unchanged.
- **Results carried forward from earlier rounds.** No production line has moved since round 1. Round 1 verified the finder's-harness sweep at the code head (`RESULT mutants=3090 killed=3036 survived=54 disposed=54 undisposed=0 stale=0`) and the base run (`2612/2562/50/50/0`). Round 2 re-derived the binomial lines and the round-2 back-test figures on the bus (813 verdicts), and both matched the body. I did not re-run either.
- **Re-taken at this head** (ev/selftest_head.txt, ev/hand_mutants_r3.txt):
  - M0: `review_strength self-test: 114 checks, 0 failed`.
  - M1 (trip forced False): fails, including `FAIL: a planted miss of each class trips: 4/30 ...` and `FAIL: the seat-family arm at the carry's point ...`.
  - M7 (P0 0.24): `114 checks, 4 failed`, as the body says.
  - The file was restored and `cmp` reports it identical.
- **Untouched files.** The three-dot diff leaves VERSION, the manifest version, RELEASE_NOTES.md, golden and claim files and budget files untouched.
- **CI on the head** (check-runs API; ev/checks_head.txt): 7 runs. `arm` was skipped, and prelude, refresh and cancel-superseded (two each) are queued. None is red, so step 11 is not engaged. The head's workflows have not concluded, and there is no pr-contract or mutation run to cite.
- **Instruments.** I built none. The verbatim comparison is a short inline Python, shown in ev/carry_compare.txt.
