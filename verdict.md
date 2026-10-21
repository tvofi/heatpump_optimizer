Fix review: merge e4f021a5feb25503025f6e09ae63f866fa5d2025

bus-nonce: 8cf5689414fe84c888fb236a7eb0f536

## Round

Fourth fix review of PR #2586 (R10-FLOW-DESIGN-POLICY). The earlier ones were 6324652583 ruling-unmet at d3e34be5, 6325426393 body-stale at bb9f93e8 and 6326243759 spec-unmet at bb9f93e8. As the brief says, only the open items were judged. This round's authored change is one line, 8d7f5bb6f (bb9f93e8 -> 8d7f5bb6f touches only `CLAUDE.md:119`). On top of it are two main merges: d8fe7653 (main 500668757) and e4f021a5 (main 1ebc737e7). The worktree was detached at e4f021a5feb25503025f6e09ae63f866fa5d2025, and `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` was empty, so the contract copy was current.

## Findings

None open. This round settles the spec-unmet block. The body's one forward-carry, R10-RCA-ORCH-CONTINUITY, is already landed on the roster (see Evidence).

## Evidence

- RESULT (1) retired rule: at the head, `git grep -nE 'two revise|revise round|two \`revise\`'` finds no match anywhere in the tree. The three-dot diff from origin/main has no added line matching it either. A wider sweep outside history files, `revise.{0,40}(orchestrator|rounds)|second revise|two revise`, hits only design-review.md:45 ("Decisions are routed, not revised. A point only the orchestrator or owner"), which is the decision-routing rule and not the retired exit. `CLAUDE.md:119` now reads "only `Design review: approve` dispatches the fixer; a third `revise` sends the designer to re-cut". That matches design-review.md's "Three notes at most ... If the third note still draws `revise`, there is no fourth: the designer re-cuts". Evidence: ev/grep.txt, ev/checks.txt.
- RESULT plant P1: restoring the retired row in the worktree made the grep find `CLAUDE.md:119` (rc 0), while `policy_lint` still ended `FIXTURE ok`. So no lint pins this wording and the grep is the pin, as the body says. Restoring the file made the grep return rc 1. Evidence: ev/plant.txt.
- RESULT (2) previously verified items: decision 0012 at the head opens "Status: Revoked 2026-10-21 (owner addendum 6322712314); kept as history. Revoked by decision `0014-design-seats-and-the-end-of-0012s-moratorium.md`." The authored delta since bb9f93e8 is the one `CLAUDE.md` line, so designer.md, design-review.md, 0012 and 0014 are byte-unchanged from round 3. Re-diffed against the pack at pin 30c57744ad8aab329d0054880fc9a3154262f204 (`design-seats/*.md`), the only differences are the draft/provenance preamble being dropped, rewrapping, and the PR's deliberate changes: the R17 threshold (L/XL with no approved design, pre-study or prototype), "revise within 1 h of seat time, a hard box", and the `design-verdict/<group>` verdict ref. "A note, not a stop", "Notes for the fixer are findings, not revise points", "Decisions are routed, not revised", "Three notes at most" and the `Carry:` grammar are all present. Evidence: ev/pack-diff.txt, ev/delta.txt.
- RESULT (3) budgets at the head, from `node tools/policy/policy_lint.mjs --budgets` (rc 0):
  - corpus: ~62891, cap 62892 (+band 500)
  - always-loaded: ~3497, cap 3349+500
  - `CLAUDE.md`: 208/221 lines, 3497/3590 tokens
  - designer.md: 60/60 lines, 878/878 tokens
  - design-review.md: 53/53 lines, 778/778 tokens
  - roles: fixer ~6172, record ~7320, policy ~9905

  All of these match the body's Figures. The budget diff against origin/main is corpus_tokens 61026 -> 62892 plus the two new per-file entries, and `## Raise justification` carries `Architecture score: dS +0.0000 NULL`. `policy_lint` printed `TOTAL: 0 error(s) across 43 policy file(s)`, `rules_sync --check` printed RULES-SYNC ok, and `brief_lint` exited rc 0. Evidence: ev/policy_lint.txt, ev/checks.txt.
- RESULT (4) CI at the head: 49 check runs, all completed (30 success, 16 skipped, 3 failure). The three failures are two `budget-raise-gate` runs and `nightly-status`. The body's `## Red checks` names and answers both. `budget-raise-gate` waits on the owner's approving review (decision 0013), which a push cannot supply. `nightly-status` grades main, and this diff does not reach what it reads. No `ci-ratchet` run exists on this head. `closures` concluded success at 22:23:01Z. A `pr-contract` run completed success at 22:24:05Z, after the last red concluded at 21:48:52Z. `mutation` is green, but this diff writes no production code line, so it drew no mutant. The section's opening figure ("bb9f93e8 has 55 check runs", closures at 20:38:01Z) is stated for the earlier head, bb9f93e8, and was not re-derived here. At this head the reds are the same two checks. Evidence: ev/check-runs.json, ev/ci-summary.txt.
- RESULT merge: `git merge-tree --write-tree origin/main e4f021a5` exits 0 with tree 63a4fb224804adf5368a7dd62f4e425ab30e1db0. The only driver line is `LEDGER-MERGE: resolved tests/closures.json`. No `MERGE-CLAIM: refused` appears. origin/main was 5a755f53efda8c099af7d6a98fb0b22828a0593c. VERSION, the manifest and RELEASE_NOTES.md are untouched. Evidence: ev/merge-tree.txt.
- RESULT (5) forward-carry: origin/handoff/audit-r10-roster at 1790cf900 (ev/roster-ref.txt) holds, at `dev/programme/rosters/wave-r10-groups.json:5447`, the carry "From #2586 (item 3703aa13, #2586): ... Decision 0012 forbids a new policy file ... That constraint is void under the owner's addendum". `carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body` on the live body returned `2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)`, rc 0. Evidence: ev/carry_audit.txt, ev/body.md.
- Head re-read before writing: the PR head is still e4f021a5feb25503025f6e09ae63f866fa5d2025, and the body is byte-identical to the one measured.
- Harness: the finder's harness is the round-3 reviewer's grep, re-run unchanged. The reviewer built no instrument. The heavy gate and the mutation table were cited from CI, not re-run.
