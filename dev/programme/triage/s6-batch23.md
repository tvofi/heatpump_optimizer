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
