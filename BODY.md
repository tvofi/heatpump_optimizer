Record: `dev/programme/HANDOVER.md` was `updated-for` fe8c213320c7, about 50 commits behind main. The stale "Round 9 in flight" state (naming `handoff/audit-r9-fixplan` and `handoff/audit-r9-plan`) is rewritten as closed at v7.0.0, those branches now being `archive/handoff/` tags, and round 10's durable state is added: the tvofi rulings, the owner-approval mandate 6175172275 with its expiry, the three merged pull requests, and D15 (#2209) in flight. Volatile state stays on #201. Delivery rows are added for #2197, #2201 and #2203, which merged without one; `origin/record/autofix` carries rows for #2202, #2206, #2207, #2208 and #2210 only, so none of the three is duplicated.

## Approval

policy (record) under mandate 6175172275; the orchestrator approves at the head.

## Head

0ec36c91dc1cc2c7d0aee0e03a15b1ff0420825d

## Mutation proof

n/a: a record edit changes no behaviour; the checks that read it are `policy_lint.mjs`, `policy_lint.mjs --budgets`, `brief_lint.mjs` and `tests/structure.py`.

## Null control

n/a: no quantified claim; the base tree at a77faf30d has the stale `updated-for` and no rows for the three pull requests.

## Figures

none

## Red checks

`nightly-status` (main's #2205) is not a result of this diff: it touches no workflow, test or code path that check reads, only `dev/programme/` records. Cheaper detector: `tests/nightly_status.py` is already the detector for that red and its standing cost is the nightly run itself; no cheaper one exists for a record-only branch.

## Forward-carry

none

## Friction

none
