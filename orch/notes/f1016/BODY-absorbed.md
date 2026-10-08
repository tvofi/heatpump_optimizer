_Requested by **tvofi**_

This is a record-only pull request: the delivery-row batch seat R9-F10.16. `python3 tests/delivery_status.py --check` at base `b3372838b` (`origin/main`, v6.7.16) held three pending merges — #1886, #1891 and #1892 — with no `docs/delivery/<N>.md` row. Each now has its row. #1893 and #1894 were open at the base and at hand-off, so they row at a later batch. No `VERSION`, manifest version or `RELEASE_NOTES.md` heading is touched.

## Head

`15aa29349dc858902d6d9b5e42fc5d35216b825c` (extends b2c7121a by an automatic origin/main absorb; the row files are unchanged between the two heads, so the round-1 verdict carries) on `fix/r9-f10-16`, one commit over `origin/main` (`b3372838b`, PR #1892's merge).

## Mutation proof

Record-only change: the fix IS the three rows, so breaking it is removing one. With any of `docs/delivery/1886.md`, `1891.md` or `1892.md` absent, `python3 tests/delivery_status.py --check` lists that merge `pending`. No production or test code changed, so no code mutant applies.

## Null control

The unmodified tree this branch is cut from (`b3372838b`, the three rows absent) prints `DELIVERY STATUS OK — 0 rowed, 3 pending, 0 overdue (overdue at 12 commits)`; at this head the same command prints `DELIVERY STATUS OK — 3 rowed, 0 pending, 0 overdue`. The three rowless merges are the entire delta.

## Figures

- `python3 tests/delivery_status.py --check` at base `b3372838b` — `DELIVERY STATUS OK — 0 rowed, 3 pending, 0 overdue (overdue at 12 commits)`, pending `#1892 b337283`, `#1891 283eb22`, `#1886 cc442e3`.
- `python3 tests/delivery_status.py --check` at head — `DELIVERY STATUS OK — 3 rowed, 0 pending, 0 overdue (overdue at 12 commits)`, `every merge in the window carries a row`.
- `GITHUB_TOKEN=$(gh auth token) node .claude/workflows/policy_lint.mjs --record --since v6.7.16` — `TOTAL: 0 error(s) over 3 merged pull request(s)` at this head.
- merge SHAs, first 8 hex: #1886 `cc442e3e`, #1891 `283eb22f`, #1892 `b3372838` (`gh pr view <N> --json mergeCommit`).

## Red checks

- `nightly-status`: none red to answer at base — the latest completed `push main` Tests run on main (run 37198767224) is `success`; the run at base `b3372838b` (run 37201727328) was `in_progress` at hand-off. This record diff reaches nothing that check grades.

## Forward-carry

The documented deferral: this batch pull request's own merge is itself a rowless merge the moment it lands, so a later batch (or the merge train) owes `docs/delivery/<this PR>.md`. The standing countermeasure is unchanged from #1888's forward-carry: the merge train's successor (`tools/audit/seat/merge_train.py` on `handoff/audit-r9-fixplan`) should write the merged PR's own row at merge time; R9-F10.16 owns that carry.

## Friction

none
