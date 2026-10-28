Fix review: blocked f975e044a567d42879a3ffc20b769ca8ef590bf9 claim-false: P216's Cost says one CLAUDE.md paragraph with no check to keep green; CLAUDE.md sits at its exact per-file token cap (3605/3605) in policy_budgets.json
bus-nonce: ed9dce3483ef8f06146f484bce1359c5

# Fix review -- PR #2891, triage batch 42 (P216)

Round 2. Round 1 blocked on the V136 heading. Reviewed head:
f975e044a567d42879a3ffc20b769ca8ef590bf9, in a detached worktree at that head, against
origin/main. `dev/governance/roles/` has no diff between the merge base and origin/main.

## Results

- Heading: `## P216: ... (V129)` is in the contract's form and is new, since main ends at P211.
  The id matches its `Source:` line. `proposals.md` holds `## V129 (orchestrator s7,
  2026-10-27T20:40Z)` with the same instance and candidate. The heading generalises the subject
  from "orchestrator message" to "agent message", and the ruling says so. The round-1 finding is
  repaired.
- Destination: R10-ROUND-PLAYBOOK is `not-started` at roster `de410e4c9`, and it is the only
  live group listing `CLAUDE.md`. The ruling says this correctly.
- `git merge-tree --write-tree origin/main <head>` exits 0 (tree `21794612`). Live check-runs
  at the head: 68 runs, 45 success, 23 skipped, 0 failure, 0 pending. There is no red to
  answer.

## Findings

- F1 (blocking, claim-false): P216's `Cost:` reads "one paragraph in `CLAUDE.md` ... no code,
  no runtime, no new instrument, no check to keep green". `node tools/policy/policy_lint.mjs
  --budgets` at the head prints `CLAUDE.md 213 221 3605 3605 yes`, which is 213 lines against
  a cap of 221 and ~3605 tokens against a per-file cap of exactly 3605. Per-file caps are
  "compared exactly". `CLAUDE.md` is also always loaded (~3605 of 3849 with the band), so
  every seat session pays the paragraph's tokens. Any paragraph the carry adds is therefore
  refused unless the fixer deletes the same number of tokens from `CLAUDE.md`, or raises the
  cap in `dev/governance/config/policy_budgets.json`. That raise is a `*_budgets.json` change,
  so it merges only on the owner's review (`budget-raise-gate`). The ruling prices neither
  route, nor the per-session token charge `proposal-triage.md` lists as a cost
  (`ev/claude-md-cap.txt`). Against one measured instance, that omission can change the
  verdict, or at least the destination: a `paths:`-scoped rule, or the role contracts the
  receiving seats open, is charged only to sessions that load it. Repair: re-price the Cost
  with the cap and the always-loaded charge, and re-rule the destination on that price.
  Carry: dismissed: blocking; this PR's re-cut owes the repair
- F2 (non-blocking): the quotation of `proposal-triage.md`, "the seat does not implement, edit
  the roster, or merge", is not verbatim. Line 32 reads "**You do not** implement, edit the
  roster or merge". The quote came from the proposal's own text. Carry: dismissed: correct the quote in the same re-cut as F1
