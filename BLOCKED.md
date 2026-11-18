# BLOCKED: r11-pre-security-privacy-p2

Question: carry 1 (the DX0 brief, scopes, DIMS, OWNER_ONLY, schema patterns) cannot pass `governance / wave-script`, an owed check, under the grader the job restores from the base (governance.yml's "Restore the check source from the base commit" step, `tools/policy/*.mjs` glob). May the orchestrator dispatch a grader-only part first (fixer.md step 5, BOOTSTRAP: "p1 the grader hunks alone, p2 the rest, a WIP handoff until p1 is on main"), under a topic this seat may write, or rule another route?

Base: origin/main 3f7f29e778e009f12a2008318b1f879f531ef3a1 (2026-11-18).

## Measurement

Control: `node tools/policy/check-wave-script.mjs` at the base exits 0, `293 passed, 0 failed`.

Perturbation: a scratch copy of the base with only the data half of carry 1: `dev/governance/dimensions/DX0.md` holding a `## Owner-only` heading, `'DX0'` appended to `audit-find.js`'s `DIMS`, `OWNER_ONLY = new Set(['DX0'])` in `audit-verify.js`, a `DX0` entry in `scopes.json` with `owner_only: true` and five seats over the axis S1..S5 that design.md section 3.1 names, schema patterns widened to `X0`. The same command, with the grader unchanged, exits 1. Grader-side refusals, which no data edit can clear:

1. `every brief has scopes ...`: "scopes.json names DX0, which has no brief". The brief listings (check-wave-script.mjs `briefListing().filter(([f]) => /^D\d+\.md$/.test(f))`, three sites plus the owner-only set's) do not match `DX0.md`.
2. `the owner-only declaration is one ...`: "the briefs with a "## Owner-only" heading are []". Same filter.
3. `a run handed a private root dispatches the owner-only seats and nothing else` and `a private root with no owner-only dimension ... refused`: the fixture arms build `fxScopes` on the real `scopes` and assume its owner-only set is empty. Any real member trips them (the labels list the real seats beside the fixture seat; `noDim` is no longer refused). This one holds for a `D18` name too: p1's grader does not yet admit a non-empty real set.

The other refusals in the run (seat count, the finder's return schema) are the data half not yet complete (`fold_ledger.py sync`, the seat list). They are not grader limits.

## What the grader part needs (for its dispatch)

- Brief listings admit `DX0.md` (e.g. `/^D(?:\d+|X0)\.md$/`), at every `D\d+` id regex in the grader (verifier and finder label regexes included). The owner ruling: every id pattern carries DX0.
- The fixture arms of block "the owner-only dimensions" build on scopes with the real owner-only members removed, so they stay independent of the real set.
- The `D18_BRIEF` switch beside `scopeRe`/`ownerRe` is either retired or re-keyed to `DX0.md`.
- Outside the grader, and so belonging to p2 (none is restored from the base): `audit-verify.js` `ownerOnlyRecord`'s `/^D[0-9]+/`, `fold_ledger.py` `DIM_OF`, `ref_privacy.py` `_DIM`, `finder_overlap.py` `SEAT_RE` and its bound, `check_scopes.py` `BRIEF_NAMED`.

No code was pushed. This file states no security or privacy finding; this seat looked for none.
