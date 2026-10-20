# Evidence — fix review of PR #2488, round 1

Head measured: `916431aefd47a8953cb5b84a990c993a77c371e3`
Merge base: `76bb45628745ff8843f61c1708641f271643a224`
Review worktree: `~/hpo-seats/r10s3/rev-2488` (detached at the head, clean)
Harness: `~/hpo-seats/r10s3/rev-2488-ev/derive_2488.py`,
`counterfactual_2488.py`, `counterfactual_authored.py`, `planted_refns_2488.py`
— the reviewer's own, reading the production `landed()` / `guard()` /
`stale_lines()` from `tests/layout.py` at the head. Nothing here is the
fixer's instrument.

## RESULT lines

- `landed.head.with_key`: 162 entries, no `handoff/`
- `landed.head.without_key`: 163 entries, `handoff/` present
- `guard.head.with_clause`: 0 refusal(s) against `76bb45628745`
- `guard.head.deleted_clause`: 287 refusal(s) (282 `handoff/`, 5 new-reference)
- `sweep_without_key.handoff`: 282 citation(s) in 53 file(s) (guard's own dedup)
- `sweep_without_key.handoff_round9`: 0 at head (already swept)
- base live files: 7 `handoff/round9/` citations in 4 file(s) — the body's "7
  refusal(s)" perturbation
- counterfactual at the authored base (move staged, key dropped, sweep undone,
  the two record files un-historical): 367 = 325 unswept `handoff/` + 39
  `handoff/round9/` + 3 new-reference (`handoff/`). The body's 322 + 39 = 361
  is 367 less the three doc lines this PR itself adds that spell `handoff/`;
  53 files is 55 less the two instrument files. The 39 is exact.
- planted deep manufactured parent under a ref namespace (files retired one by
  one, live line cites the emptied directory `ns/sub/deep/`): 0 refusal(s) —
  the skip is `startswith` at any depth. Safe here only because
  `handoff/round9/` is an explicit directory entry, which P3 shows is swept.
- null arm (base tree, against its first parent `a2b25bbc5518`): 0 refusal(s);
  the base manifest has no `ref_namespaces`.
- clause deleted in a scratch worktree: `layout self-test: 1 case(s) FAILED`;
  `moved_paths self-test: 11 checks, 1 failed`. Restored by rebuilding the
  worktree at the head.
- `moved_paths` over the added lines: 2 hits, both the map's own entry
  (`"old"` STALE?, `"new"` FALLBACK); no added live line.
- `moved_paths` over every touched file whole: 187 hits; the only
  `handoff/round9/` moved-path hits are `tests/layout.json:630-631` (the map's
  own entry). The rest are other pre-existing moves in the map, the
  `R9-RCA-1990` record, the archived plan table and `.claude/rules/`.
- remaining `handoff/round9` mentions: 26 files at the authored code head
  `5fd7fbdfb87051270d66fec0ef2ed860ce12f6a9`, 27 at the head (the delivery row
  this head adds). Classification: 1 map entry, 7 `dev/archive/**`, 1
  `dev/audit/rca/**` (GUARD_EXEMPT), 18 `historical` (12 `dev/audit/rounds/`,
  2 delivery, plan-2026-09-open-issues.md, rosters, round9, bugclasses.json).
  No live tool, test or product file.
- `git grep -l handoff/round9` at the authored head: 26.

## Files

- `rename-proof.out` — 100% renames, equal blob OIDs and sha256 at both ends
- `versions-untouched.out` — VERSION / manifest / notes untouched
- `head-selftests.out`, `clause-deleted-selftests.out` — the mutation proof
- `guard-head.out`, `guard-perturbations.out` — head run and P1/P2/P3
- `derive_2488.out`, `counterfactual_2488.out`,
  `counterfactual_authored.out`, `counterfactual_authored2.out` — the sweeps
  and the counterfactual
- `planted_refns_2488.py`, `planted_refns_2488.out` — the depth probe
- `added_lines_2488.txt`, `moved-paths-added-lines.out`,
  `moved-paths-touched-whole.out` — the move-map scan
- `mention-classification.out` — every remaining mention classified
- `merge-tree.out` — no conflict with `origin/main`
- `drift-and-closure.out` — `env_drift --all` (no unclaimed drift, no stale
  fixture) and the closure mode line
- `ci-fast-and-mutation.out` — CI's own mode line, entities, harness headers;
  the mutation lane's empty scope
- `delivery-row.out`, `head.txt`
