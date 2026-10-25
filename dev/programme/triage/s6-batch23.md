# Proposal triage, session s6, batch 23 (P106-)

Rulings from the s6 `proposals.md`, collected 4 or 5 to a pull request under
tvofi's batching rule of 2026-10-24. Numbering continues after
`s6-batch22.md` (P101-P105; P105 withdrawn).

## P106: a PR title op for body_patch.sh (S6-V39)
Verdict: DEFER -> R10-FLOW-BODY-ONLY (one instance; the group owns the body-only update seam and is not started).
Source: s6 `proposals.md` `## V39` (dispatch w29, #2804 round 2).
Instances: 1, the #2804 retitle of 2026-10-25, as V39 records it; I did not open the PR. Nothing recurs yet.
Considered:
- R10-FLOW-BODY-ONLY (not-started, size S): files `update_pr.sh`, `cloud_relay.sh`, `pr_args.sh` and `INSTRUMENTS.md`, and its domain is changing a pull request's metadata without moving a clean head. It is the closest group by seam and domain, though it does not list `body_patch.sh` as a file. If the title arm is ever built, the carry goes here.
- R10-FLOW-JIDOKA (in-progress): owns `prepr.sh`, a pre-push check; a post-open title edit shares no file or seam with it. Does not fit.
- R10-POLICY-LINT-FAMILY (done) and R10-ORCH-MACHINERY (absorbed) mention `body_patch`/`app_mint` only in prose and cannot take work.
Cost: an `--title` arm on `body_patch.sh` is a few dozen lines with a self-test (the PATCH, a read-back of the title and the unchanged head), and one more mint per use. A title needs fixing only when a seat opens a PR under a merge-commit subject, as #2804 did; `handoff_push.sh` and `open_pr.sh` already set the title with `gh pr edit` at open.
Binding: a single instance and an unmeasured benefit; the bar is "clearly", and an unmeasured benefit is DEFER.
What would change the answer: a second retitle that a seat hand-rolls on `tools/pr/app_mint.sh`, counted from the dispatch report.

## P107: roster-to-issue and carry-destination checks are opt-in or missing (S6-V38)
Verdict: DEFER -> R10-ORCH-ROSTER-SCHEMA (owner of the carry that asks the same refusal; no second ACCEPT). Round 1 ruled ACCEPT -> R10-ROUTING-INVARIANTS; that group is now absorbed into SCHEMA, so the ruling is re-cut.
Source: s6 `proposals.md` `## V38` (owner request, 2026-10-25). Roster read: `origin/handoff/audit-r10-roster` at 0574da74ae2f7ddf7c9250548f08c2f8b06d8775 (the roster tip; `origin/main` b89fea13e does not yet carry the fold).
Instances: 17 carries appended after their group reached done, on 8 groups (a walk of 1115 roster commits), 8 BAD-DEST from `carry_audit sweep --last 20 --issues`, 6 open issues with every listing group done and 4 live groups with no issue, as the "Measured instances" carry on SCHEMA records at that roster; I did not re-run them.
Considered:
- R10-ORCH-ROSTER-SCHEMA (live, not-started; owns `roster_edit.py`; absorbed R10-ROUTING-INVARIANTS on 2026-10-25): its carries hold the three invariants (the folded brief), the tick CARRY default pass and V38's own measured instances, which is V38 (b) and (c). Its carry from commit 2308e06b1 ("absorbed as terminal in DONE_STAGES") also asks to refuse a Carry: to an absorbed group as one to a done group is refused. That is candidate (a): same file, same seam, same refusal. The carries state that `roster_sync` refuses a done destination and `roster_edit append-carry` accepts it; the refusal at the producing command is the remaining half, and the DONE_STAGES change plus the 2308e06b1 carry is its natural site. Closest group, and the only one that fits.
- R10-ROUTING-INVARIANTS: absorbed; cannot take work.
- R10-FLY-CARRY-DISPOSITION (owns `carry_audit.py` at a distinct seam), R10-FLOW-POSTMERGE (ruled out for set-stage checks by P101): do not touch the append gate.
Cost: nothing new to build here; a second ACCEPT would put the same few lines in one file under two carries.
Binding: (a) is already owned, so a new ACCEPT adds no benefit; (d) has no count of its own: its 3 issues were left open by closing-keyword form (prose or code span), which a post-merge printout would not fix. An unmeasured benefit is DEFER.
What would change the answer: when SCHEMA's fix lands, a `roster_edit append-carry` to a done or absorbed group that is still accepted (null control: the same call to a live group is accepted) re-opens (a) as a ruling to SCHEMA; a count of issues left open after a merge re-opens (d).

## P108: drop the fix review for bookkeeping PRs (S6-V40, tvofi's question)
Verdict: REJECT (a) and (c) as stated; (b) stands for triage and roster batch PRs. The cost to cut is rounds, not reviews, and the measured rounds are mostly one mechanical cause that already has a detector. The record-row PRs already merge without a review (`record_row.py --automerge-check`) and are not in question.
Source: s6 `proposals.md` `## V40` (tvofi, 2026-10-25: "are reviews really needed for bookkeeping PRs?").
Instances: 48 h to 2026-10-25 ~13:00Z, from `git fetch origin 'refs/heads/verdict/*'` and `git log origin/main --merges --since=<48h>`:
- Triage PRs merged: 18 (`--format=%s | grep 'from tvofi/triage/'`, #2734 to #2790). Review blocks on them, counted as VERDICT.md commits in each `origin/verdict/<n>` whose first line is `Fix review: blocked`: 11 blocks on 8 of the 18 PRs (#2734 1, #2735 2, #2738 3, #2743 1, #2755 1, #2758 1, #2759 1, #2767 1). The other 10 PRs merged on the first verdict.
- What the 11 blocks caught, from each block's Findings section: judgement content, in every one of the 8 blocked PRs. A nonexistent owning group (P58 in #2734), contradictory briefs for one new group (P55 against P60, #2734), a carry that conflicts with the destination's existing brief (P88 in #2767), a false cost premise because `tests/entities.py` pins `--max 40` (P85 in #2759), a ruling that ignored that `update_pr.sh` and `merge_train.py --free-holders` already free holders (three rounds on #2738), a dependency on an unmerged `s6-batch4.md` (#2735, 2 blocks), a REJECT resting on a run log not in the tree (the REJECT in #2755), and a carry text that `brief_lint` does not lint (#2743). Purely mechanical in the same blocks: a stale `## Head` in the body (#2758, and a part of #2755 and #2743), which `policy_lint.mjs --pr-body` at the final head would catch.
- Roster batch PRs merged: 12 (`from tvofi/.*roster`, `fix/audit-r10-roster`, `fix/r10-roster-freeze-*`; #2663 to #2797). Blocks: 1, on #2797: a carry claiming an ordering ("merges after ROSTER-FREEZE") that the groups' after-edges at that head did not carry. Judgement again.
- Today's #2804 block caught P101 routed to a group that owns neither file, and the absorbed-group re-route that followed.
Considered:
- (a) roster/triage on a mechanical guard (every commit a lint-passed `roster_edit` op, read back, `carry_audit` clean): the guard exists for roster ops already (`roster_edit --push` lint gate), and the 1 roster block it would have let through was an ordering claim no lint reads. For triage it would have passed all 11 blocks except the stale-head ones: a ruling's destination, cost premise and instances are judgement, and a wrong ACCEPT dispatches a fixer.
- (c) a cheaper check (destination is live and owns the files the carry edits), with review only for ACCEPTs that create work: it reads 2 of the 11 blocks (P58's nonexistent group; #2804's misroute and absorbed re-route), none of the false-premise, existing-mechanism or contradiction catches. A batch holds ACCEPT and DEFER rulings together, so the PR is reviewed whenever any ACCEPT is in it, and the one REJECT-only block (#2755) was a reproducibility catch. The check would also be a new script and a new policy branch.
- (b) status quo: costs a seat and ~20-40 min per round, 11 blocks across 8 of 18 PRs (44% of triage PRs blocked at least once), each block a defect that a later seat would have built on or the reviewer reached first. I did not measure seat time or tokens per round; no figure for it is in `seat-ledger.md` beyond V40's own estimate.
Cost: (a) removes a seat and ~30 min per PR but pays in ruling defects reaching the roster; (c) adds a new check that reads under a fifth of the catches. The benefit of cutting the review is not measured; the benefit of keeping it is 11 blocks in 48 h.
Binding: a review that blocks 44% of triage PRs at least once, on judgement content no mechanical check reads, clearly outweighs the ~30 min it costs. The rounds that do not need a human are the 4 stale-`## Head` ones, and `policy_lint.mjs --pr-body` already catches them locally before handoff; fixing that is a fixer-habit gap (`ci-autofix.md`: repair what a red `prepr.sh` predicts), not a new instrument.
Policy file that would change had this been ACCEPTed: `dev/governance/roles/orchestrator.md` section 11 ("A `merge` verdict from a reviewer that measured this head, or a carry"), by adding a bookkeeping exemption. Nothing changes; the merge condition is untouched.
What would change the answer: a second window where fewer than 15% of triage PRs are blocked (the 48 h figure is 44%), or a measured per-round seat cost showing the review dominates the triage lane's wall-clock; for roster PRs alone, a window of 25 or more roster PRs with 0 judgement blocks (this window: 12 PRs, 1 block).
