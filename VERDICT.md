Fix review: blocked d3e34be538b02f1186419a3e7e4220bdf269803d ruling-unmet: 0012 recorded void-in-part not revoked per addendum 6322712314, and both contracts follow drafts at ddacf98 not pin 30c57744a

Round 1 of PR #2586 (R10-FLOW-DESIGN-POLICY), reviewed from a detached worktree at d3e34be538b02f1186419a3e7e4220bdf269803d. `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the fix-review contract read is current. Head re-read before writing: still d3e34be5.

## Blocking

- Decision 0012 is not revoked. The owner's addendum (#201 comment 6322712314, 17:49Z, before this PR opened) says 0012 is revoked, not only voided, with the file kept as history. At this head 0012 reads "Void since 2026-10-21 ... the rest of this record stands" and adds "Superseded in part (2026-10-21) ... The cadence, the one enforcement point and D14's stop rule stand". Decision 0014 item 1 says "The rest of 0012 stands", and the PR body cites only ddacf98's R16 ("voids"). The fix: mark 0012 as revoked by the ruling and its addendum, history only, in both 0012 and 0014, and drop the "stand" sentences. Evidence: ev/ruling_6322712314.txt, ev/decisions.diff. Carry: dismissed: blocking this head, the fixer's next round
- Both contracts were built from the drafts at ddacf98, not at the brief's pack pin 30c57744a. The drafts changed in substance between those two commits (ev/drafts_ddacf98_to_30c57744a.diff), and this head keeps the superseded text:
  - `designer.md`'s last paragraph still has "Blocks you: a finding without a harness". At the pin this became "A note, not a stop": an owner-reported finding with no harness (R10-SCORES, R10-UX-HEALTH, R10-HEAT-METER) is quoted as the evidence and the work carries on. Under the head's text those owner groups block at the designer.
  - `design-review.md`'s last paragraph keeps "after two revise rounds ... to the orchestrator". The pin replaced it with three sections: "Notes for the fixer are findings, not revise points", "Decisions are routed, not revised" (`decision: orchestrator|owner`) and "Three notes at most", where the designer re-cuts at the third. None of the three is in the contract.
  - The pin's carried-observation grammar for fixer notes is absent from the contract. That grammar is `Carry: <group> (item <id>)`, and rule 19's set includes `Carry: dismissed: <reason>`, with the colon. Neither contract states any `Carry:` marker grammar.

  The fix: re-derive both contracts from 30c57744a, keep the PR's deliberate changes (the threshold per R17, the hard 1-h box, token counts, `design-verdict/<group>`), then re-measure the per-file caps and `corpus_tokens`. Carry: dismissed: blocking this head, the fixer's next round

## Verified (would pass as they stand)

- The PR's other deliberate departures from the drafts are sound. The R17 threshold is every L/XL group with no approved design, pre-study or prototype. The 1-h revalidation box is hard. Verdicts go to `design-verdict/<group>` because seats make no GitHub write. The moratorium-class line is dropped. Carry: dismissed: verified, no action needed
- No policy file at the head still treats 0012's moratorium as in force. I ran `git grep -iE 'moratorium|0012'` over the tree without 0012 and 0014 (ev/grep_0012_moratorium.txt, 21 hits). The hits are history (RELEASE_NOTES, delivery rows, archived rosters, rca R9-RO-PC1) and float values. One is a code comment, `tools/policy/policy_lint.mjs:562`, which still describes the "process moratorium until 2026-10-31"; that file is not in this group's files. Carry: dismissed: code comment outside group files
- The `CLAUDE.md` diff is two role-table rows only, and it loosens nothing. Carry: dismissed: verified, no action needed
- The edits to `orchestrator.md` section 5, `fixer.md` step 17 and `fix-review.md` step 15 match brief items 2–4. Carry: dismissed: verified, no action needed
- The raise figures are real. `corpus_tokens` 62423 is the measured value, and M4 at 61922 gives exactly one corpus error while 61923 gives TOTAL 0. The base reads 61142 against cap 61026. The per-file caps (designer 46/666, design-review 35/521) equal the measurements. `## Raise justification` records five payments tried and an `Architecture score: dS` line; I re-ran `score.py --diff origin/main` and got `dS +0.0000 NULL`. These figures will move once the contracts are re-derived from the pin. Carry: dismissed: re-measured after the re-derivation
- Mutants M1 (CLAUDE.md rows dropped → 2 `[index]` errors) and M4 reproduce as the body states. Carry: dismissed: verified, no action needed
- On red checks, `budget-raise-gate` is red by design and the body answers it. `nightly-status` is red on main and this diff does not reach what it reads (fix-review step 11). `coverage` was still in progress at 19:24Z, and `pr-contract` is green ×3. Carry: dismissed: verified, no action needed
- `git merge-tree --write-tree origin/main d3e34be5` is clean (tree 22ec8214, exit 0). VERSION, the manifest and the notes heading are untouched. Carry: dismissed: verified, no action needed

## RESULT

RESULT policy_lint: TOTAL 0 error(s) across 43 policy file(s), FIXTURE ok, exit 0
RESULT policy_lint --budgets: corpus ~62423 cap 62423 (+500); base ~61142 cap 61026
RESULT rules_sync --check: RULES-SYNC ok, exit 0
RESULT brief_lint: exit 0
RESULT entities.py (venv-ci python 3.14.7): ALL 2382 ENTITY CHECKS PASSED, exit 0
RESULT archscore --diff origin/main: dS +0.0000 NULL
RESULT mutant M1: TOTAL 2 [index]; M4 (61922): TOTAL 1 [budgets]; 61923: TOTAL 0
RESULT merge-tree vs origin/main 57f0c9c7: clean, exit 0
RESULT spec-match vs pin 30c57744a: FAIL (designer harness-stop, design-review notes/decisions/three-notes, carry grammar)
RESULT 0012 revocation per addendum: FAIL
RESULT carry_audit --roster-ref origin/handoff/audit-r10-roster check: CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

Item ids: carry_audit assigns none here. A `blocked` verdict makes every section a block section, so it reads 0 finding items, and no `(item <id>)` is quotable. Every bullet above still ends in a `Carry:` marker. Neither design group is on origin/handoff/audit-r10-roster yet, so none routes to a group.

bus-nonce: 1ebc1fe85a6438a89a0e5b7681c01870
