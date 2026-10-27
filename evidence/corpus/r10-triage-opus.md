Policy change, merged under mandate 6329234399. Triage ruling P127 (dev/programme/triage/s6-batch26.md#P127, owner ruling from tvofi, 2026-10-25): the proposal-triage seat runs on opus, not sonnet, because a ruling's claims are checked against the code. The edit is lines 8-9 of dev/governance/roles/proposal-triage.md: "One sonnet seat at medium effort: judgement with an oracle." becomes "One opus seat at medium effort: rulings are checked against code." The file stays at its 36-line cap. The token cap refused the ruled wording (494 against 489 tokens), so it was paid by trimming words (the clause "a ruling's claims are checked against the code" to "rulings are checked against code", and "keeps its own route" to "keeps its route"), never by raising the cap.

## Head

d62c9133fe71c50f1f7275257775dddeecb275ad

## Mutation proof

The edit is a wording change in a role contract, so no scripted check is expected to notice a revert. The line was reverted to origin/main's text and these were run: tests/entities.py reported 4 of 2445 failed (the four hb:positive_control py-spy timing checks, the same four as at the head); policy_lint.mjs --budgets exit 0; rules_sync.mjs --check exit 0. No check names the model wording. The only check keyed to the file is its line and token cap, shown by the null control below.

## Null control

One extra line appended to the file: policy_lint.mjs refuses with "37 lines exceeds its cap of 36" and a token overrun, exit 1. The unmodified head: policy_lint.mjs exit 0.

## Figures

- Lines and tokens of proposal-triage.md at the head: `node tools/policy/policy_lint.mjs --budgets | grep proposal-triage` prints 36 of 36 lines and 489 of 489 tokens.
- Lint at the head: `node tools/policy/policy_lint.mjs` exit 0.
- Mirror: `node tools/policy/rules_sync.mjs --check` exit 0 (the file needs no mirror change).
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints MODE: SCOPED, 1 script, tests/entities.py.
- Scoped script: `PYTHONPATH=tests/hastub python3 tests/entities.py` prints 4 of 2445 ENTITY CHECKS FAILED, the same four hb:positive_control checks (py-spy timing on a loaded host) that fail on origin/main's text of the file; CI owns them.

## Red checks

none

## Forward-carry

none

## Friction

none

## Approval

Policy change, merged under mandate 6329234399 (scope all). The ruling it implements is the owner's: tvofi, 2026-10-25, quoted in `## V48` of the s6 proposals and ruled ACCEPT as P127 in dev/programme/triage/s6-batch26.md. The owner's approving review, or the orchestrator's merge under the mandate, is recorded at merge.
