Fix review: blocked acd78b4d770d1666652baa9d94559aa3ea9f57eb class-open: the minor-defect rule's severity vocabulary leaves the roster's medium and high unmapped, and the cut silently drops triage obligations

bus-nonce: 716baba79d85034ebfd87d74f0c43f83

## Block

Round 1, from a detached worktree at acd78b4d770d1666652baa9d94559aa3ea9f57eb. The two threshold moves (rule 1, over 20%; the keep test, at least 10%) are correct and mutation-proven. Two things in `dev/governance/roles/proposal-triage.md` block the merge:

1. **The predicate's domain is unguarded (fix-review step 6).** The new "Minor defects" paragraph tells the triage seat to read the roster group's `severity`. Then "minor or low" takes the bar, and "major or critical" skips it. But the roster's `severity` field (origin/handoff/audit-r10-roster, wave-r10-groups.json) holds these values: medium 201, high 90, low 56, None 24, critical 8, normal 7, major 1. So `medium` and `high` cover 291 of 387 groups, and neither side of the rule names them. `normal` is not named either. This PR's own group is `medium`. "Classified first, never assumed major" covers only an absent severity, not a value outside the rule's words. A triage seat therefore cannot decide the most common case. Fix: map the field's real values in the paragraph. For example: low takes the bar; high, critical and major skip it; medium and normal are stated explicitly one way; None is classified first. The owner rules on medium (their words were "minor" and "major and critical"), and the body discloses the mapping for the approving review.
2. **The cut to fit the 489-token cap removed operative obligations, and the body does not disclose it.** It says only "paid by cutting prose". These sentences at the merge base afc1586a appear nowhere else in dev/governance, decisions, CLAUDE.md or .claude/skills (git grep is empty):
   - "An ACCEPT runs its rule on each instance, result beside it."
   - "Git and local logs before the API." (this backs the owner's 2026-11-08 API-discipline order)
   - "rulings are checked against code" and "at medium effort"
   - the exemption ACCEPT's "its PR records it"
   - DEFER's "or the owning group"
   - `Cost:`'s "the estimate"
   - the tool's refusal trigger (text naming `triage P<n>` or `proposal P<n>`)

   Each of these changes what the seat must do, and the owner's two rulings did not ask for any of them (CLAUDE.md: "if the honest description is 'this changes what a seat must do', it is policy"). The brief authorises paying by cutting, but not silently deleting duties. Keep the first two and the effort line, and pay from text that does not bind: the sources sentence, the cost list, or the closing paragraph's description of the tool. Alternatively, list each deleted duty in the body so the owner's approving review sees it.

## Findings

- Residual: the roster still states the old bar. The "Machinery freeze after v10.0.0" and "Proposal bar" texts in dev/programme/rosters/wave-r10-groups.json (2 hits on origin/handoff/audit-r10-roster) still say "more than a 10% improvement" for the shared exemption. Those texts sit outside the brief's grep scope (dev/governance, tools, .claude), and the body does not disposition them. Only the orchestrator edits the roster (roster_edit.py), so this is routed rather than blocked here. Carry: R10-FLY-TRIAGE-BAR
- Follow-up: paragraph 1 still exempts "a finding's fix", and the new paragraph 3 bars a minor instrument or machinery defect repair, which is usually a finding's fix. The specific rule plausibly overrides, but the text never says so. Add "except as below" (or similar) to paragraph 1 when re-cutting. Carry: R10-FLY-TRIAGE-BAR

## Evidence

- RESULT head-selftest: `machinery_ratchet self-test: 54 checks, 0 failed` (ev/head-selftest.txt); base afc1586a also has 54 checks, 0 failed (ev/base-selftest.txt).
- RESULT mutant A (THRESHOLD restored to Fraction(1, 10)): 2 failed, the exactly-20% cases. This confirms the body's mutation proof (ev/mutant-tenth.txt).
- RESULT mutant B (Fraction(1, 4), upper-side control): 3 failed, the 21% cases and the positive control. The cases bracket 1/5 from both sides.
- RESULT mutant C (`gain > THRESHOLD` relaxed to `>=`): 2 failed. The strictly-above rule is pinned.
- Old-figure enumeration: my own git grep over dev/governance, tools and .claude (ev/grep-old-figures.txt) finds no remaining 10% site in the exemption or proposal sense. The hits are sleeps, solver literals and similar. A whole-tree grep (ev/grep-wholetree.txt) adds only round-6/8/9 sysid figures, the s6 triage records the body leaves as written, and the roster texts in Findings.
- policy_lint --budgets: base proposal-triage.md 34 lines / 489 tokens against caps 36 / 489 (at cap); head 35 / 487. No `*budgets*.json` change in the three-dot diff (ev/budgets-base.txt, ev/budgets-head.txt).
- rules_sync.mjs --check: `RULES-SYNC ok`. The .claude and .cursor copies match their source.
- Merge: `git merge-tree --write-tree origin/main acd78b4d` exits clean, with no conflict.
- CI: `merge_train.py classify acd78b4d... --pr 3310` printed `GREEN acd78b4d770d1666652baa9d94559aa3ea9f57eb pending: none red: none`, rc 0 (ev/classify-1.txt). The packet digest has no red. Step 11 is owed nothing.
- VERSION, manifest and notes heading: untouched (not in the diff). There is no claim-file or fixture change, so step 4 does not apply.
- Head: `git ls-remote` shows fix/r10-fly-triage-bar at acd78b4d770d1666652baa9d94559aa3ea9f57eb when posting. The body's head is the same.
- Finder's harness: none is named. This is a policy group with no finding, so the self-test and the policy lint are its instruments. The null control holds: the base self-test passes at 10% and the head separates 20% from 21%.
- The body's prepr `tests/entities.py` 3-failure environmental claim was not re-derived. CI's closure lanes are green at the head.
