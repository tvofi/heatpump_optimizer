Fix review: merge 916431aefd47a8953cb5b84a990c993a77c371e3
bus-nonce: 03ec7d662c9771a80a7c37590e1c0fbb

Round 1. Reviewed from a detached worktree at the head; my own harness and its
outputs are in `~/hpo-seats/r10s3/rev-2488-ev` (they read the production
`landed()`, `guard()` and `stale_lines()`, not the fixer's instrument).

## The move is content-preserving

`git diff -M --summary 76bb456...916431a` prints two 100% renames,
`{handoff => dev/archive/handoff}/round9/fix/resume/FR-8.md` and its
`plan-table-live.md` twin; `--numstat` is `0 0` for both. Each file's blob OID
is equal at both ends (`b4efe3b2…`, `0d4ab78c…`) and so is its sha256
(`02885f6b…`, `13352f8e…`). `git ls-tree -r HEAD -- handoff/` is empty.

## The mechanism, attacked

- **Same shape in both instruments.** One `landed()` (tests/layout.py);
  `guard()` and `stale()` pass `manifest.get("ref_namespaces", ())`,
  `moved_paths.py` passes the same key from the same manifest. Three callers,
  no copy of the rule.
- **Head:** `GUARD: 0 refusal(s) against 76bb45628745`.
- **Null arm:** the base tree against its first parent `a2b25bbc5518` is 0
  refusals, and the base manifest has no `ref_namespaces` — the head's clean
  run is not a check that was already clean for the new reason.
- **Mutation proof re-run, not taken:** delete the clause in a scratch
  worktree → `layout self-test: 1 case(s) FAILED` (the ref-namespace parent case,
  `{'new-reference': 1, 'unswept': 1, 'placement': 0}`) and
  `moved_paths self-test: 11 checks, 1 failed` (its parent case). Restored.
- **P1:** a staged live line citing `handoff/round9/plan-table-live.md` is
  refused (new-reference + unswept). **P2:** a staged live line citing
  `handoff/` as a branch namespace is not refused. **P3:** a staged live line
  citing the moved tree directory `handoff/round9/` is refused — the explicit
  entry is still swept under the namespace.
- **Planted depth probe (mine, `planted_refns_2488.py`):** when a directory
  under a ref namespace is retired file by file (no directory entry), a live
  citation of the emptied directory draws **0 refusals**. The filter is
  `startswith`, so it skips a manufactured parent at any depth, not just the
  emptied top. This map is safe because `handoff/round9/` *is* an explicit
  directory entry (P3). A future real move under `handoff/` must retire a
  directory entry; if someone later lists `verdict/` or `review/` as a ref
  namespace, the same applies. Stated as a residual risk, not a defect here.
- **`since: null`:** every reader uses `old`/`new` or `.get("since")`
  (`layout.py`:210, 708; `dual_path.py`; `budget_raise_gate.py`; `entities.py`),
  so null is accepted.

## Figures re-derived

With the clause deleted at the head the guard refuses **287** (282 `handoff/`
citation lines in **53** files + 5 new-reference); with it, 0. The body's
counterfactual `322 + 39 = 361` reproduces at the authored base as
`325 + 39 + 3 = 367`: 322 is 325 less the three doc lines this PR itself adds
that spell `handoff/`, and 53 is 55 less the two instrument files; the 39
(30 `bugclasses.json` + 2 plan + 7 live) is exact. I state the reconciliation
rather than reporting 322 as literally confirmed; the class it measures is real.

## The remaining `handoff/round9` mentions

26 files at the authored code head `5fd7fbdf`, 27 at the head (the delivery row
this head adds). None is live: 1 map entry (`tests/layout.json`), 7
`dev/archive/**`, 1 under `dev/audit/rca/` (GUARD_EXEMPT), 18 `historical`
(12 `dev/audit/rounds/`, 2 delivery, `plan-2026-09-open-issues.md`, rosters,
round9, `bugclasses.json`). The two newly `historical` files are evidence
ledgers pinned to shas (`origin/handoff/…@<sha>:path`) and a quoted gate error;
keyed on the exact file, which is the right shape.

`moved_paths.py` over the added lines: 2 hits, both the map's own entry, no
live line. Over every touched file whole: 187 hits, all other pre-existing
moves (the map's own entries, the `R9-RCA-1990` record, the archived plan
table, `.claude/rules/`) except the new `tests/layout.json:630-631`.

## Other claims

- CI's own gate at this head: `MODE: SCOPED -- 10 script(s) run, 23 scoped
  out.`; `ALL 2359 ENTITY CHECKS PASSED`; `layout self-test: ok`;
  `ALL 109 HARNESS HEADER CHECKS PASSED`; 12 scripts passed, 23 scoped out.
  The local `closure.py select` prints the same mode line.
- Delivery row `dev/programme/delivery/2488.md` is this PR's own and names
  `R10-HANDOFF-ARCHIVE`; `delivery-status` is green.
- `VERSION`, the manifest version and the notes heading are untouched.
- `env_drift.py --all`: `NO UNCLAIMED DRIFT` (56 scenarios), `NO STALE
  FIXTURE`. `card_drift.mjs` needs `tests/plan_view.py`'s payload and will not
  run standalone; the card diff is comments only (6/6 lines) and CI's `browser`
  passed.
- `git merge-tree --write-tree origin/main HEAD`: exit 0, no conflict.
- The mutation lane reports `MUTATION TABLE PASSED (empty scope)` — no
  production line in scope, so it is no evidence; the clause-deletion proof
  above is, and I re-ran it.
- CI at the head, every run concluded: every gate check green, including
  `closures`, `fast (3.14)`, `browser`, `coverage`, `typing`,
  `instrument-self-tests`, `pr-contract`, `delivery-status`, `arch-score` and
  `budget-raise-gate`, so no root-cause answer is owed. Two exceptions, neither
  a finding against this diff: `nightly-status` is red because it grades main's
  scheduled run 39387919507 (head `0c298f6`, pinned main `76bb456`); and
  `Analyze (python)` concluded `cancelled` at 30m30s, the job's own
  `timeout-minutes: 30`, because the diff touches Python so
  `codeql_scope.py` starts the full-repo analysis instead of skipping it. That
  required context needs a rerun before the merge train can see it pass.

## Verdict

merge — the move is byte-identical at both ends, the one new mechanism is
load-bearing and both of its self-tests redden when it is deleted, every
remaining mention is a map entry, an archive or a record, and every gate check
the diff can reach is green at the head.
