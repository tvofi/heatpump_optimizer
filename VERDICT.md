Fix review: merge 4b43164c066faa16b508726512ca0314fb884edd

bus-nonce: efba72b0d7120ac06d941cfc706b4392
pending-ci: gate

## Scope

Round: a later round (delta), over the reviewed head 9c5485e367c7ce78d54a31155d31f43f8fe9f58b. `review_carry.py 9c5485e3 4b43164c` prints FRESH-REVIEW, so the scope is the delta 9c5485e3..4b43164c: merges of origin/main (61afd4f2, 2cfa3d7d, ef579d9b), the fixer's resolution 63c62197, and e9e70ff2 (tests/entities.py, test only). No custom_components/ line in the delta comes from the branch. The production lines in the delta all arrive through main's merges, and the PR's own patch has no file under custom_components/. So nothing widens the scope. The previous verdict at 9c5485e3 recorded no findings.

## Evidence

- Merge with main: `git merge-tree --write-tree origin/main 4b43164c` exits 0 (tree a726ff79). origin/main is ef579d9b, which is the head's merge base.
- Conflict set, re-derived: `git merge-tree --write-tree --name-only 9c5485e3 ef579d9b` exits 1 and names CLAUDE.md, dev/governance/config/policy_budgets.json, dev/governance/roles/orchestrator.md, dev/governance/roles/proposal-triage.md (modify/delete), standing-dispatch.md and standing-roster.md. tests/closures.json resolved through the ledgermerge driver. This matches the body's six conflicts.
- Union check: I read each conflicted file against both parents: main's side (ev/main_side.diff, 0a2139b1..ef579d9b), the PR's original side (ev/pr_orig_side.diff, 0a2139b1..9c5485e3) and the merged head against main (ev/head_vs_main.diff).
  - CLAUDE.md: main's `standing.md` row and its retired tick/roster row are present. The removal of the `proposal-triage.md` row is the PR's (C6). No clause of main's is lost.
  - policy_budgets.json: main's caps are all present: standing.md 50/553, standing-roster.md 7/92, standing-tick.md 6/83. Head against main removes only the two proposal-triage.md keys. No cap was raised.
  - orchestrator.md: main's section-1 heading, the "Two standing seats ... under `standing.md`" bullet, the section-6 rewording, the section-10b `roster-drain` text, the section-11 #2423 cut and the judge void-rule cut are all present unchanged. Section 9's "that is the price" sentence is replaced whole by the PR's C5 text. Main's edit to it was inside that same sentence.
  - One clause leaves that neither parent's patch removed. Section 5's "a seat was dispatched to fix what an open pull request fixed." was cut in 63c62197 to pay orchestrator.md's 295-line cap. The union read 296 lines; each parent read 294. This is disclosed in the body, the rule itself ("One `list_pull_requests` over the open set, and the issue's comments") stays, and what was cut is motivation. Head is at 295/295 with no budget change.
  - proposal-triage.md: stays deleted (C6). Main's last edit ("Sources: the sweep ...", "under `standing.md`") goes with the file. The bar and Machinery clauses read as before in orchestrator.md section 5.
  - standing-dispatch.md: main's header ("One of the two standing seats (`standing.md`; ...)") and its Read-the-ref section are kept. The Dispatch paragraph is the PR's (no delivery-row check; C4/C8). Main's change to it was a reflow plus that row check.
  - standing-roster.md: identical to main (retired). The PR's own edit there was on text main deleted.
- Interdiff of the PR's own patch, comparing (0a2139b1..9c5485e3) with (ef579d9b..4b43164c) per file: it differs only in orchestrator.md, proposal-triage.md, standing-dispatch.md, standing-roster.md, standing.md and tests/entities.py. Every one of those is a conflict file or its stated semantic interaction.
  - standing.md: main's new file. The one PR edit drops `proposal-triage.md` from "Binds ...", which keeps the citation lint clean.
  - tests/entities.py: e9e70ff2 drops `proposal-triage.md` from main's #3464 `_SR_FAIL` tuple, because the file is deleted. The four standing contracts stay pinned and nothing else in the check moved.
- Dangling citations: `git grep 'proposal-triage\.md'` at head, outside dev/programme, dev/audit, decisions and selftest_closures.json, prints nothing. Decision 0015 line 45 and tools/ci/selftest_closures.json still name it. Both were already the same at the reviewed head 9c5485e3, so the delta changes neither.
- Cheap checks at head (ev/lints.txt, ev/budgets.txt, ev/structure.txt):
  - `node tools/policy/policy_lint.mjs`: TOTAL: 0 error(s) across 50 policy file(s).
  - `--budgets` rc=0, with every per-file row at or under its cap. The `role policy` aggregate is ~9996 against 9958 +band 500, which is inside the band.
  - `rules_sync.mjs --check`: RULES-SYNC ok.
  - `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- The `VERSION`, `RELEASE_NOTES.md` and manifest changes in the delta are main's v7.1.11 stamp, which arrived through the merge. The head's diff against main touches none of them.
- Body: `## Head` names 4b43164c066faa16b508726512ca0314fb884edd, the head reviewed. Its repair-4 head note matches each union figure above that I re-derived. Not re-derived by this seat: the union's 4263-token figure and the entities control, which ran the predicate on a perturbed copy. My own --budgets run shows orchestrator.md at the cap.
- Mutation: the delta writes no production code line, so there is no mutant to plant. The PR is policy prose.
- Owed reds (ev/owed_reds.txt) and CI: classify at this head prints `WAIT 4b43164c066faa16b508726512ca0314fb884edd pending: gate red: none` (ev/classify.txt); polled from 03:27 to 03:57 UTC and still WAIT, so the verdict carries `pending-ci: gate`. The head is still 4b43164c (refs/pull/3451/head). No owed red exists at this head yet. The body's `## Red checks` answers budget-raise-gate (the designed refusal on the deleted proposal-triage.md key; only tvofi's review clears it), tests / fast (3.14) (main's red) and gate.
