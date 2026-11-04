Fix review: blocked b2499f12d1cb100b36a1820717fbf623566ebd24 owner-stale: P378 DEFER names R10-TICK-PR-BUCKETS as the owner, a group the roster marks absorbed

bus-nonce: 738d6816e5a82b714861fd5b254b2f3e

Round 1.

## Block
The ruling's DEFER names "the group already owning the item" as R10-TICK-PR-BUCKETS at stage `not-started`, read at roster `efd37113a` (2026-11-02). On the roster branch head `9bc39aede` that group is `stage: absorbed`; its FIRE-OWED level and the payload-file arm were folded into R10-TICK-LEVELS (`stage: in-progress`, `pr: 3200`, note "s11 replan fold", `aa6b12a8e`, 2026-11-04 06:59 +01:00), which is before this head (18:19 +01:00). The substance holds (R10-TICK-LEVELS's brief still carries the FIRE-OWED predicate, its null control, and "Apply the same definition to FIRE-OWED"), but a DEFER must name an owner that exists (proposal-triage.md), and "the answer changes if that group closes without building" is undefined for an absorbed group. Fix: name R10-TICK-LEVELS (PR #3200), re-read at the then-current roster head, in the Verdict, Instances and Binding lines.

## Findings
- Residual: Instances cite "line 201 to 230", "line 223" etc. and render/fire timestamps from the session-local seat and fire ledgers, which are not in the tree; I could not re-derive them. Carry: dismissed: session-local logs, outside any reviewer's reach; the ruling names the files read.
- Residual: the `gh pr view <n> --json files` counts (8, 3, 12, 2 files; 0 under custom_components/) were not re-derived. Carry: dismissed: not contradicted by anything readable here, and the ruling's DEFER does not turn on them.

## Evidence
- Checked and fine: verdict grammar (DEFER with owner and change condition), one `## P378` entry with Verdict/Source/Instances/Cost/Binding, `s6-batch115.md#P375` exists with the payload-file definition, `standing-dispatch.md` exists, no capped file touched, no VERSION/manifest/notes/claim edit (two files in the three-dot diff), carry_audit 0 findings, figure_lint 0 refused (1 unverified, a generic git diff).
- merge-tree against origin/main `d7582ed40`: rc 0.
- CI on this head: classify returned WAIT (rc 3, pending, gate red: none) when I reviewed; not awaited, since the block is content, not CI.
- No roles/ drift between merge base and main.
