Fix review: merge ffe44c221c888ba3cb24141577b25732ac2024d6

bus-nonce: d3d0732625388918968402ecb546882f

Round 2 (re-check; head unchanged since round 1's `blocked ffe44c221 carry-missing: not carried to R10-ORCH-ROSTER-SCHEMA`). Reviewed from a detached worktree at `ffe44c221c888ba3cb24141577b25732ac2024d6`; merge base `fd7e289d0`; `git diff fd7e289d0...origin/main -- dev/governance/roles/ dev/governance/rules/finding-propagation.md` is empty at origin/main `c5e1be196` (contracts current).

## Round 1's blocking finding: discharged

- **Carry in the tree.** `456bd9e99` (`roster_edit append-carry R10-ORCH-ROSTER-SCHEMA`) is an ancestor of origin/handoff/audit-r10-roster tip `1bee483c8`; the carry is the group's last `carry[]` entry at the tip (jq over `wave-r10-groups.json`; 1 entry citing #2670). `git diff --stat origin/main...origin/handoff/audit-r10-roster -- dev/programme/rosters/` is non-empty (1 file, 45+/27-), so the roster carry is live per `finding-propagation.md` enforcement. The group is `resume.stage: not-started` (a live destination).
- **Linted.** `node tools/policy/brief_lint.mjs` on the roster at `1bee483c8`: 0 error(s), 0 warning(s).
- **Content.** It names the defect (`PROPOSAL_RE` matches only a numbered label), the measurement (19 carries at `e4c92864f` with a lettered label and no ruling cited; the module's regex matches the numbered form, not the lettered one — round 1 re-derived both), states the cure as a precondition (widen the grammar or refuse an uncitable label), the control (a self-test row refusing a lettered label uncited and passing it with an ACCEPT citation; null control: text naming no proposal still lands), and the scope limit (existing carries not re-judged; `s5-batch1.md` re-rules them). It contains no `triage P<digits>` string, so the triage gate does not read it as proposal-sourced. This is the cure round 1 named.

## Re-checked

- **Carry markers.** `python3 tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <body>`: `4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)`, rc 0. P14/P21/P33's lines (R10-FLY-RELAY-REVIEW-FF in-progress, R10-FLOW-DESIGN-STAGES not-started, R10-ORCH-LEDGER in-progress) state text "to append" with `roster_edit.py append-carry`, which resolves `#P<n>` only once `s5-batch1.md` is on main; the body does not claim them applied, and none is on the roster yet (0 carries citing `s5-batch1` in each). Owed by the roster seat after merge, not a pre-merge carry of this PR (round 1's non-blocking note, unchanged). Carry: dismissed: routed by the body's own Forward-carry lines
- **Scope.** `git diff --stat fd7e289d0...HEAD`: `dev/programme/delivery/2670.md` (+1, its own `**open**` row only) and `dev/programme/triage/s5-batch1.md` (+382). VERSION, manifest, RELEASE_NOTES.md and both claim files untouched (`git diff --quiet`: clean). `git merge-tree --write-tree origin/main HEAD`: rc 0 (no conflict at `c5e1be196`).
- **Checks at the head** (commit check-runs API, 40 runs): 30 success, 9 skipped, 1 failure — `delivery-status` (job 120536798598): `DELIVERY STATUS OVERDUE — 40 rowed, 12 pending, 1 overdue`, overdue row #2639. Main's, not this PR's: the diff adds only its own row and touches nothing that check reads beyond it (`defect-root-cause.md` exemption), so `## Red checks: none` stands. `pr-contract` re-ran at 17:12:25Z after that red concluded: success.
- **Round 1's other points.** Head unchanged, so its passing checks (coverage of s4's 25 drafts onto P5-P29 plus P30-P33, entry shape, 25 carry indices matched, 12 source spot-checks, citations) carry unmodified. Its non-blocking notes stand as dismissed: P21's `git grep handoff-wip origin/main` evidence wording, P12's ACCEPT to a done group, P30's merits — none moved. Carry: dismissed: round 1 dismissed each, head unchanged

RESULT round1-carry: R10-ORCH-ROSTER-SCHEMA carried at 456bd9e99, present at roster tip 1bee483c8; brief_lint 0 errors; roster diff vs main non-empty
RESULT carry-audit: 4 routed, 0 unrouted, 0 bad destinations
RESULT scope: 2 files; delivery row is own row only; merge-tree clean at c5e1be196
RESULT checks: 40 runs; 1 red (delivery-status, main's #2639 overdue); 0 in progress
RESULT downstream: P14/P21/P33 routings owed by the roster seat post-merge; 0 applied, none claimed applied

bus: verdict/2670 at 79817aea5a7bc6c153cfa83cddc234fad672f3d7, confirmed from s5-rev-2670 (review/2670 at ba52f87198785b8aad6f65521e91c99945f0c6ff); evidence: ~/.zcode/bus/verdicts/2670/79817aea5a7bc6c153cfa83cddc234fad672f3d7/evidence
