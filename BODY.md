Group: R10-FLOW-DESIGN-POLICY (registration pending: roster PR-B). Spec: pack file `dev/programme/flow-study/roster/groups/R10-FLOW-DESIGN-POLICY.json`, plus `design-seats/designer.md` and `design-seats/design-review.md`, at pin 30c57744ad8aab329d0054880fc9a3154262f204 on `claude/dazzling-gauss-7l3u2b`. Authority: owner ruling 2026-10-21, `RULINGS-201-3.md` at the same pin (R16–R19), and the owner's addendum to R16 (#201 comment 6322712314), which revokes decision 0012.

**This is policy.** Every file it changes is code-owned: `dev/governance/roles/`, `dev/governance/decisions/`, `CLAUDE.md`, `dev/governance/config/policy_budgets.json` and `tools/policy/policy_lint.mjs`. It merges only on the owner's approving review at its head.

What it lands:

1. Two new role contracts, `dev/governance/roles/designer.md` and `dev/governance/roles/design-review.md`, re-derived from the drafts at pin 30c57744a. They include "A note, not a stop", "Notes for the fixer are findings, not revise points", "Decisions are routed, not revised", "Three notes at most", and `carry_audit.py`'s `Carry:` grammar in both. The PR's deliberate changes: the R17 threshold (L/XL with no approved design, pre-study or prototype), a hard 1-h revalidation box, and verdicts at `design-verdict/<group>`.
2. `orchestrator.md` section 5, `fixer.md` step 17 and `fix-review.md` step 15 dispatch and gate on `Design review: approve <sha>`.
3. **`CLAUDE.md` names both contracts in its role table.** This round changed the `design-review.md` row. It now reads "only `Design review: approve` dispatches the fixer; a third `revise` sends the designer to re-cut", which matches the contract's "Three notes at most". Before, it carried the drafts' retired exit, "two `revise` rounds go to the orchestrator".
4. Decision 0012 is revoked and kept as history, and 0014 records the revocation. The `policy_lint.mjs` comment on 0012's `CORPUS_EXCLUDED` entry is in the past tense, a comment-only edit.

Alternatives considered:
- **Delete 0012.** Rejected: the addendum keeps the file as history.
- **Drop the `CLAUDE.md` row's exit clause instead of restating it.** Rejected: the always-loaded index would then name no exit, and a reader of the index alone would not know the loop is capped.

## Head

e4f021a5feb25503025f6e09ae63f866fa5d2025. It is the PR head: a merge of origin/main into c97b6745b, which merged the handoff code d8fe765384ddee5c548b4a95187aebf8c78e2a3f. Against d8fe7653 the head differs only in three `dev/programme/delivery/` rows (2527, 2581, 2583). The code d8fe7653 is a merge of origin/main 500668757 into 8d7f5bb6f, the one-commit `CLAUDE.md` row fix on PR head bb9f93e8. It was never rebased. The merge's only conflict was `tests/closures.json`, which the `LEDGER-MERGE` driver resolved. `policy_lint --budgets` and `score.py --diff origin/main` were re-run at e4f021a5 for this repair: corpus ~62891 (cap 62892), `Architecture score: dS +0.0000 NULL`.

## Mutation proof

This round's change is one wording line. No check pins wording: putting the old row back (the reviewer's plant P1, reversed) leaves `policy_lint` at TOTAL 0. The pin is the grep below. The earlier rounds' mutants (M1 `[index]`, M2/M3/M3b `[budgets]`) target files and caps this round does not touch, and round 2's review reproduced them. No production code line changed.

## Null control

- `git grep -n -e 'two \`revise\` rounds' -e 'two revise rounds'` at bb9f93e8 prints `CLAUDE.md:119`, the stale row. At d8fe7653 the same grep finds no match in `CLAUDE.md`, `AGENTS.md`, `.cursor/` or `.claude/` either. So the grep finds the stale row when it is there.
- `node tools/policy/policy_lint.mjs` at origin/main 50066875 prints `TOTAL: 0 error(s) across 41 policy file(s)`. At d8fe7653 it prints 43; the difference is the two new contracts.

## Figures

All at d8fe7653 unless a line says otherwise.

- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 43 policy file(s)`, `FIXTURE ok`, rc 0.
- `node tools/policy/policy_lint.mjs --budgets` aggregates, at origin/main 50066875 and then at this head:
  - corpus: ~61142 (cap 61026), then ~62891 (cap 62892). The new wording is one token shorter than the old, so the cap recorded in round 2 has one token of headroom. It was not re-recorded.
  - always-loaded: ~3410, then ~3497 (cap 3349 + 500).
  - `CLAUDE.md`: 208 lines (cap 221) and ~3497 tokens (cap 3590).
  - roles fixer ~6172, record ~7320, policy ~9905, each under its cap plus band.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `node tools/policy/brief_lint.mjs`: rc 0.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`. `scope.run` names `tests/entities.py`, which passed under the seat venv's Python 3.14.7: `PYTHONPATH=tests/hastub python3 tests/entities.py` printed `ALL 2382 ENTITY CHECKS PASSED`, rc 0.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>` on a branch named `handoff/r10-flow-design-policy`: rc 0, `PRE-PR: d8fe7653...`. Its ancestry-reds step printed "the body answers every red this branch pushed (budget-raise-gate nightly-status)".
- `carry_audit.py --roster-ref origin/handoff/audit-r10-roster check`: 2 finding items, 2 routed, 0 unrouted, rc 0.

## Raise justification

This is unchanged from round 2, and this round moves no budget. The raise is `corpus_tokens` 61026 → 62892, plus two new per-file entries, `designer.md` 60 / 878 and `design-review.md` 53 / 778. Each cap was re-recorded to the value measured in round 2, and the owner's ruling R19 approves it.

Payments tried: shortened the pin's added sections (220 → 191 and 295 → 281 in bytes/4); no trim of any other policy file was tried, because the edits to `orchestrator.md`, `fixer.md` and `fix-review.md` are paid inside each file, so their per-file caps do not move, and the raise is the two new contracts the ruling adopts.
- **Shorten the pin's added sections.** Taken (220 → 191 and 295 → 281 in bytes/4).
- **Cite the carry grammar across contracts.** Not taken: the brief puts it in both contracts.
- **Move prose into an uncapped file.** Not a payment: `corpus_tokens` does not move.
- **Stay inside the band.** Not possible: 61526 is below the 62891 measured.

Architecture score: dS +0.0000 NULL

## Red checks

The PR head bb9f93e8 has 55 check runs. `closures` concluded success at 20:38:01Z. The only reds are these two:
- `budget-raise-gate`: red by design until the owner's approving review at the head, because it reads the raises in `policy_budgets.json` (decision 0013). No cheaper detector is owed: a push cannot supply approval. Carry: dismissed: owner approval pending
- `nightly-status`: it reports `main`'s `record` conclusion onto every pull request, so it grades `main` and not this diff. This diff touches no workflow, test lane or what that job reads. Carry: dismissed: grades main, not this diff

## Forward-carry

- `dev/programme/rosters/wave-r10-groups.json` still briefs the in-progress R10-RCA-ORCH-CONTINUITY seat that "Decision 0012 forbids a new policy file, lint class or rules entry until 2026-10-31". That constraint is void under the addendum. The roster is the orchestrator's to correct, not this PR's. This is the review's non-blocking observation. Carry: R10-RCA-ORCH-CONTINUITY (item 3703aa13)

## Friction

- brief: cost: the brief names `tools/audit/seat/carry_audit.py`, but the instrument is at `tools/audit/carry_audit.py`. That path was run instead, at the cost of one failed call. Carry: dismissed: brief path slip

## Carry index

`carry_audit.py` hashes an item's whole text, marker included, so no item can quote its own id. These lines repeat each marker with its id.

- Carry: R10-RCA-ORCH-CONTINUITY (item 14c702a5)
- Carry: dismissed: brief path slip (item 9d6ca05e)

The Red checks lines are not finding items to `carry_audit.py`. They keep their `dismissed:` markers as answers.

## Approval

Awaiting the owner's approving review at the head. The ruling (R16–R19) and the addendum authorise the change, but they are not the approval: every changed path is code-owned.

## Attribution

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_013EDukvk1TqcqvFs3n7b8Nz
