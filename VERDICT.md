Fix review: blocked f6f67eded114eb7dfcda2dacae5e2f977890a3e0 carry-missing: 1ac59f510 appends the R10-HEAT-METER clamp-reset ruling to R10-RATIO-ANCHOR, which is resume.stage done (#2698, 2f88db054) on main and at this head; finding-propagation.md: a done group is not a destination, so the carry reaches no stage

bus-nonce: c7604e11195fc9adc15dbc2fe71bfc79

Round 1. Reviewed head f6f67eded114eb7dfcda2dacae5e2f977890a3e0 (refs/pull/2823/head at review time); origin/main dfcd8d9be.

## Block

- `1ac59f510` (roster_edit append-carry R10-RATIO-ANCHOR) adds "From R10-HEAT-METER's design (orchestrator ruling under mandate 6329234399 ...): on the #2698 clamp-reset carry, keep \"clamp means reset\" ... the question is this group's, not HEAT-METER's. Re-measure the clamp behaviour at your merge base". R10-RATIO-ANCHOR's resume is `stage: done`, `pr: 2698`, `commit: 2f88db054...` at the commit's parent, on origin/main and at this head (ev/carry-dest.txt). `dev/governance/rules/finding-propagation.md` lines 67-68: "A group at `resume.stage: done` is not a destination: nothing dispatches or lints it." The ruling hands a question to a stage that will never run; `carry_audit.py`'s own destination check (`Dests`, lines 327-334) reports a done group as "is done". `roster_edit.py append-carry` has no write-time refusal for a done destination, which is how it landed. Repair: drop that carry (`roster_edit.py drop-carry R10-RATIO-ANCHOR`) and put it on a live destination: either keep it on R10-HEAT-METER (the void path is HEAT-METER's code, and the carry asks only to keep clamp-means-reset and re-measure) or, if the question really needs a new stage, a carry-<N>.json / new group per finding-propagation.md.

## Findings

- Body misattribution: the Figures paragraph lists "the R10-HEAT-METER design carries (`0378e16f9`, `02ee07bea`, `460d9f19b`)" and "their routing ... (`42008e799`, `33c505efc`, `1ac59f510`, `fac3e1de0`)", but per-commit replay (ev/per-commit-carries.txt) shows only `0378e16f9` is a design carry; `02ee07bea` is lead L6, `460d9f19b` is L9 and `fac3e1de0` is L1 (as the same paragraph later says correctly). The summary also says "leads L1 to L9 as carries on their owning groups", while L8 is the new group R10-LEGIONELLA-COMPLETION's brief, not a carry. Correct the body in the re-cut. Carry: dismissed: body-only wording on this PR, fixed with the block's repair push; no later stage reads it.
- `roster_edit.py append-carry` writes a carry to a done group without refusal (the write-time arm the R10-ORCH-ROSTER-SCHEMA carry 2d45acb7a extends for `absorbed` does not cover `done` either). Carry: R10-ORCH-ROSTER-SCHEMA

## Evidence

- RESULT commits: `git log --no-merges --reverse ... 9442cb4ea..9e5f5cf1c -- dev/programme/rosters/` prints 25, identical to the body's list (ev/log.txt).
- RESULT merge: `git merge-tree --write-tree origin/main f6f67eded114eb7dfcda2dacae5e2f977890a3e0` exit 0, tree 75b15cdac, equal to the head's own tree; no conflict.
- RESULT blobs: main b7f33d15eed0b6d23974e784a52ad56382471e66, head and merged tree 98bf056affd7635e08facf871657f03030e8c3b0, as the body states.
- RESULT diff: numstat roster 85/26 (111 lines), delivery/2823.md 1/0; no other file (ev/numstat.txt).
- RESULT groups: main 190, head 191, new R10-LEGIONELLA-COMPLETION, removed none, changed 18; every per-group carry delta and both stage tallies match the body (ev/groups.txt; stage read from resume.stage).
- Stage ops verified: R10-PARAMS-OWNER and R10-ARCH-SHAPES not-started -> in-progress with pr 2817 / 2819; R10-DEMAND-OVERBOOK done at da12aa37d; R10-UPDATE-PR-SIGNALS ends in-progress with commit fd9914851 (carries-open then back).
- set-after edges verified as the body names: ORCH-DISPATCH-REG drops ORCH-LEDGER (now empty); CLOSEOUT-CLEANUP drops ARCH-DOCS and ROUND-PLAYBOOK; ROUND-PLAYBOOK drops ARCH-DOCS; ARCH-DOCS adds LEGIONELLA-COMPLETION.
- Lead placement verified: L1, L2 -> R10-COP-GATE; L3, L4 -> R10-BUFFER-STORE; L5 -> R10-SAV-ACTUATION; L6, L9 -> R10-HEAT-METER; L7 -> R10-DIAG-REDACT; L8 -> new group R10-LEGIONELLA-COMPLETION (queued, wave 2). HEAT-METER design carries: COP-GATE (42008e799), UX-HEALTH (33c505efc), RATIO-ANCHOR (1ac59f510, blocked above).
- Carry destinations on main (ev/carry-dest.txt): all not-started or queued except R10-RATIO-ANCHOR (done). None absorbed.
- No added line names a host, a home path or an address (grep for /home/, /Users/, /root/, 192.168, .local, @: no hits); lead texts quote aggregate figures and code locations only.
- `node tools/policy/brief_lint.mjs` at head: TOTAL: 0 error(s) across 48 file(s). `figure_lint.mjs --pr-body`: 0 resolved, 26 not verified, 0 refused (ev/figure_lint.txt).
- The diff holds neither a roster queue line 334 op nor a CLOSEOUT carry (CLOSEOUT-CLEANUP changes only its `after`), as the body says.
- Contention: #2817 and #2819 touch no file under dev/programme/rosters/; no roster conflict.
- CI on this head at review time: prelude, refresh, cancel-superseded queued; arm skipped; no check concluded, so no red check to answer.
- Mutation proof, null control, claim files, VERSION: n/a, no production, test, golden or version file in the diff.
