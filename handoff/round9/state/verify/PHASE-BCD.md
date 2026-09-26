# Round 9: phases B, C and D fanned out over threads

tvofi asked for this at 12:09Z (cmsg_01EL5jLi4rokGBbkaevYXSJV7qUMPtPV8pNP9MHmcrrM7m). It is PLAN.md sections 5 to 7, placed on threads the way phase A was placed on boxes B1 to B10.

## Phase B: 12 verifier threads
- There are four dimension groups, and each group has one thread per lens. So the three members of a triple always run on three different containers, as PLAN section 5 requires.

| group | dimensions | findings (batch 1) | threads |
|---|---|---|---|
| G1 | D1, D0, D3, D13 | 29 (D1 in two shards of 15 and 7, split by seat) | G1-V1, G1-V2, G1-V3 |
| G2 | D4, D8, D10, D12 | 33 | G2-V1, G2-V2, G2-V3 |
| G3 | D14, D2, D9 | 28 | G3-V1, G3-V2, G3-V3 |
| G4 | D5, D6, D11, D7 | 32 | G4-V1, G4-V2, G4-V3 |

- The input is branch `handoff/audit-r9-evidence`: baseline 1936d5ca plus every box's `tools/audit/round9/`, with `tools/audit/round9/verify/G<n>-findings.json` for each group.
- The output is `handoff/audit-r9-verify-g<n>-v<k>`, holding the reports plus `tools/audit/round9/verify/votes-G<n>-V<k>.json`.
- The findings the leads seats raise go to the same threads later, as an extra unit per group.
- The panel tally (the kill rule: two refutes, each with a number) is computed by the orchestrator from the 12 votes files, using the rules in audit-verify.js's PANEL block.

## Phase C: one judge thread and two runner threads
- There is one judge. PLAN section 6 and judge.md, carried into policy by #1627, keep a single judge for dedup and verdicts, because dedup needs the whole set. Changing that would be a policy change for tvofi.
- What does fan out is the mechanical re-runs. Two runner threads run `tools/audit/judge_batch.py --shard 1/2` and `--shard 2/2` on quiet containers. They measure and do not decide.
- Order of work:
  1. The judge dedups.
  2. The judge writes JUDGE-INPUT.json.
  3. The runners start.
  4. The judge reads their rows and gives verdicts and classes.
- Briefs `J.md`, `R1.md` and `R2.md` are generated when every group's panel is in.

## Phase D: sweep threads, packed by class
- There is one sweep seat per class with a surviving finding (D14.md steps 3 and 4). The seats are packed onto about four threads, S1 to S4, balanced by finding count. A class never splits across threads.
- Briefs are generated from JUDGE.json. RCA flags follow the rule N >= 3, or any instance in a barriered class.

## Standing rules carried in every brief
- Read CLAUDE.md, .claude/rules/ and the role contract first.
- Call the owner "tvofi", never "Tim".
- No heavy D3 re-runs.
- The resume rule: report every milestone to the orchestrator.
- No PRs, no GitHub comments and no issues from the cloud.
- Do not read another verifier's report.
