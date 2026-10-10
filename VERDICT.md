Fix review: merge a01d262cf500331b4a0a50138855afaff8357ccc

bus-nonce: b6cc3637f5ab10dc51151bfef718e3cc

# Fix review — PR #2109 (docs land: three round-9 pre-study documents)

Head measured: `a01d262cf500331b4a0a50138855afaff8357ccc`
Merge base vs `origin/main`: `d22172b6e504943f3b4878fb0a59b951cd75e50e`
(`origin/main` at review: `c729bb32e`). Head unchanged at post (`git ls-remote`).

This is a docs land: it adds documents and read-only evidence under
`dev/audit/rounds/round9/prestudy/` plus a delivery row. No production line
changes, so `fixer.md`'s mutation proof (step 1) is n/a by design and the
null control is the `layout --guard` classification arm.

## RESULT — byte-identity of every landed file to its handoff-ref source

Every landed blob compared with `git hash-object`-equivalent
(`git rev-parse <head>:<path>` vs `git rev-parse <ref>:<old-path>`).

- 17/17 `runs/` blobs IDENTICAL to their source (12 diag @ `3c90f86a3`, 5
  debugger @ `eae236d66`).
- `boost_drift_refit.py` IDENTICAL to `3c90f86a3`.
- `friction-prestudy-r2-groups.json` IDENTICAL to `c8a6be1cf`.
- The four `.md` documents differ from source by EXACTLY one added leading
  line each — the disclosed provenance HTML comment. `tail -n +2` of each
  landed doc is byte-identical to its source (0-line diff). The added line is
  the one the body discloses; no content beyond it changed.

So the documents are not byte-identical, but the difference is exactly the
disclosed provenance line, not a silent edit. Verbatim transcription holds.

## RESULT — classification by the tree's own checks

- `tests/closure.py:297` — `"dev/audit/"` is an INERT prefix: all 23
  pre-study paths land in it.
- `tests/layout.json:79` — `"dev/audit/rounds/**"` category;
  `tests/layout.json:67` — `"dev/programme/delivery/*.md"` for the row.
- All 24 diff paths classified (23 `dev/audit/` INERT + 1 delivery row); none
  unclassified.
- `python3.13 tests/layout.py --guard --base origin/main` → `GUARD: 0
  refusal(s)`.
- `python3.13 tests/structure.py` → `STRUCTURE RATCHET PASSED` (no metric
  moved).
- `VERSION`, manifest, `RELEASE_NOTES.md` untouched; both `*_claimed_drift.txt`
  byte-identical to the merge base; no budget/closure/layout file touched.

## RESULT — body's "absent from main under any name" claim (three-dot)

At the merge base and at current `origin/main`, no file named
`debugger-prestudy*`, `boost-drift-prestudy*` or `friction-prestudy*` exists
under any path. The names occur on `origin/main` only as citations
(`handoff/round9/plan-table-live.md`, `tools/replay/debug_replay.py`). The
cited reference `tools/replay/debug_replay.py:49` is present on main and names
`debugger-prestudy.md section 5`, which is why this landing resolves it. Claim
holds.

## RESULT — checks

42 check-runs at the head; every one `success`/`neutral`/`skipped`, none red,
none in progress at post. No `root-cause-unanswered` trigger.

## RESULT — merge state

`git merge-tree --write-tree origin/main HEAD` → rc 0, no conflict (against
current `origin/main c729bb32e`). No claim-file conflict.

## RESULT — entities (corroboration)

`PYTHONPATH=tests/hastub python3.13 tests/entities.py` → `ALL 2234 ENTITY
CHECKS PASSED`, matching the body. A first run under CPU contention (my own
concurrent CI polling) printed `1 of 2234 … FAILED` once; a clean re-run and
a base-`origin/main` run (`ALL 2250 ENTITY CHECKS PASSED`) both pass, so that
single failure was a transient timing flake, not this diff.

## Notes

- The dispatch named `tools/audit/briefs/fix-review.md`; that path does not
  exist on `origin/main`. This review used the role contract
  `dev/governance/roles/fix-review.md` (the contract, which overrides).
- No forward-carry: this lands documents; the body records `none` and none is
  owed.

Verdict: **merge**.
