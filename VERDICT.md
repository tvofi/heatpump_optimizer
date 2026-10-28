Fix review: merge c818b4677192d9476555d6001a1b5d5d8842ea35

bus-nonce: 6470be1239e37bd641f0ad413de0ff8d

## Round

Round 1 for PR #2600 (R10-ROSTER, branch fix/audit-r10-roster-9). I measured head c818b4677192d9476555d6001a1b5d5d8842ea35 from a detached worktree. That is still refs/pull/2600/head at verdict time, and origin/main is 01cf1398a9cfa3dcae5945221afd0c1dae9cf682. dev/governance/roles/ shows no diff between the merge base and origin/main, so the contract I followed is current.

## Findings

None. Every carry lands with its source verdict's text, and nothing is handed on.

## Evidence

- Scope: `git diff origin/main c818b4677` changes two files, 9 insertions and 3 deletions. The first is dev/programme/delivery/2600.md, one new line: the PR's own `open` row for R10-ROSTER. The second is dev/programme/rosters/wave-r10-groups.json, where the only change is to the `carry` arrays of exactly three groups. Each existing prefix is kept byte-identical:
  - R10-ORCH-MACHINERY goes from 30 to 31 entries.
  - R10-FLOW-ROSTER-FREEZE goes from 3 to 4 entries.
  - R10-RCA-FRICTION-RESIDUE goes from 0 to 2 entries.
  - The 3 deleted lines are the comma re-terminations of the previous last entries, plus `"carry": []`.
  - No group is added or removed: 147 groups on both sides.
  - These are exactly the four append-carry ops 3093279db, c4e214691, 844c6c694 and 8da941ac3. The roster at the head equals 8da941ac3 (0 diff lines).
  - Evidence: ev/diff-main-head.txt, ev/figures.txt, ev/carry_texts.txt.
- Carry texts against their source verdicts:
  - The R10-ORCH-MACHINERY entry is byte-equal to line 11 of review/2580 VERDICT.md.
  - The R10-FLOW-ROSTER-FREEZE entry is byte-equal to line 12 of review/2580 VERDICT.md.
  - In #2580's posted verdict, comment 6335670563 by hpo-approver[bot], the first line is `Fix review: merge caac2c8d...`.
  - The two R10-RCA-FRICTION-RESIDUE entries are review/2598's two `## Findings` bullets verbatim. The only edit is that the leading `- ` and the trailing ` Carry: R10-RCA-FRICTION-RESIDUE` are replaced by ` (from #2598 verdict, bus 15d0bf56)`.
  - 15d0bf56ae0f is the verdict commit `verdict: #2598 Fix review: merge 35dd3965...` on origin/verdict/2598.
- Destination groups are live on origin/main's roster:
  - R10-ORCH-MACHINERY is `not-started`.
  - R10-FLOW-ROSTER-FREEZE is `not-started`.
  - R10-RCA-FRICTION-RESIDUE is `queued`.
- Figures re-derived at this head. Every figure in the body reproduces:
  - The merge base of 8da941ac3 with origin/main is 4da10dbae84c7915488ce9fcd29240fc14750eb0.
  - The null control `git diff --exit-code origin/main 4da10dbae -- roster` gives rc 0.
  - The roster diff is 8 insertions and 3 deletions over 4 commits.
  - The body's jq program prints 147/147, removed [], new [], and changed [R10-FLOW-ROSTER-FREEZE, R10-ORCH-MACHINERY, R10-RCA-FRICTION-RESIDUE].
  - Carry counts afterwards are 4, 31 and 2.
  - bfc609664 is the merge of 01cf1398a into 8da941ac3, and c818b4677 adds only dev/programme/delivery/2600.md.
- RESULT brief_lint: `node tools/policy/brief_lint.mjs` at the head prints `TOTAL: 0 error(s) across 47 file(s)`. The non-zero counts after that line are its fixture self-tests, each reporting `ok` (ev/brief_lint.txt).
- RESULT carry_audit: `carry_audit.py check --body` on the PR body at the head prints `0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)` (ev/carry_audit_body.txt, ev/body_full.md). CI's pr-contract printed the same line.
- RESULT merge-tree: `git merge-tree --write-tree origin/main c818b4677` exits 0 with tree 1755eff9102b, which equals the head's own tree. That is clean, and no claim-file driver was invoked (ev/merge-tree.txt).
- Mutation proof, class rule, claim files and metric moves do not apply. The diff writes no production or test line, moves no budget, closure, golden or claim file, and touches neither VERSION nor the manifest or notes heading. pr-contract confirms `no version edit`.
- CI at this head: 40 check runs, all concluded (ev/check-runs-c818b467.tsv, ev/ci-logs.txt).
  - Every one is success, skipped or neutral (CodeQL), except nightly-status.
  - nightly-status failed with `NIGHTLY ABSENT: no scheduled run of the workflow was found at all`, pinned to main 01cf1398a. It grades main's nightly schedule, which a roster-only diff cannot reach. It is not a required check on main-protect and does not block.
  - pr-contract started at 08:21:50Z, after nightly-status concluded red at 08:16:11Z, read the body and passed (`clean no refusal`).
  - The body's `## Red checks` section reports main's tip as read before that run concluded. pr-contract accepted it, and that section is not what this verdict judges.
- Figures I could not re-derive: none.
