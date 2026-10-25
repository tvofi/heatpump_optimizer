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
Verdict: ACCEPT narrowed -> R10-ROUTING-INVARIANTS (candidate (a) only: `roster_edit.py append-carry` refuses a done or absorbed destination). Candidates (b) and (c) are already that group's brief; (d) DEFER.
Source: s6 `proposals.md` `## V38` (owner request, 2026-10-25).
Instances: 17 carries appended by `roster_edit append-carry` to 8 groups after those groups were done, 8 BAD-DEST from `carry_audit sweep --issues`, 6 open issues owned only by done groups (3 closed after verification) and 4 live groups with no issue, all as V38 records for ~10:00Z; I did not re-run the sweep. The earlier #2404 blocks recorded in P101 are the same class.
Considered:
- R10-ROUTING-INVARIANTS (not-started, size S; `carry_audit.py`, `roster_edit.py`, `roster_sync.py`, `orchestrator_tick.py`, `brief_lint.mjs`): its brief (issue #2733) already makes the three invariants hold. Invariant 2 (every live group lists an issue) is a `brief_lint` warning, which is V38 (c) first half. Invariant 3 (every open issue is listed by a live group) is a default-pass tick line from the cached issue list with CARRY made default and offline, which is V38 (b) and (c) second half. The `carries-open` stage covers pending carries on a done group. Closest group by files, seam and domain.
- R10-ORCH-ROSTER-SCHEMA (owner of `roster_edit.py`): the after-edge on ROUTING-INVARIANTS sequences the two on that file, so the carry goes to the later group.
- R10-FLY-CARRY-DISPOSITION (owns `carry_audit.py` at a distinct seam): dispatch-side carry disposition; does not touch the append gate.
- R10-FLOW-POSTMERGE: ruled out for set-stage checks by the P101 review.
Cost: (a) is one refusal in `append-carry`, the guard `roster_sync` already has, with a fixture pair (a done destination refused, a live one accepted); under 20 lines and no new file, in a file the group already edits. (b)/(c) cost nothing new.
Binding: (a) closes the producer: 17 carries stranded by the one command that creates them, after which (b) only detects what (a) lets in. It is cheaper than any sweep and clearly beats its cost. (d) has no count of its own: V38 records 3 issues left open after a merge because the PR named them in prose, a different cause that a post-merge printout would not fix (the closing keyword grammar owns it); an unmeasured benefit is DEFER.
What would change the answer on (d): a count of issues left open after a merge that `set-stage done` would have named, taken once ROUTING-INVARIANTS lands.
