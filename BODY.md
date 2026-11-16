`checkOrphanCaps` in `tools/policy/policy_lint.mjs` read only the `files` table of `dev/governance/config/policy_budgets.json`, so a `files_tokens` cap on a path no `POLICY_GLOBS` pattern matches was compared against nothing and passed. It now reads both per-file tables (one `flatMap` over `['files', 'files_tokens']`, the table named in the message), and the acceptance drives a token-only orphan cap. Run over the tree, the extended check returns two orphan token caps, both dropped: `tools/audit/briefs/nudge.md` (the retired orchestrator turn's, the carried one) and `tools/audit/harnesses/README.md` (a token cap with no line cap and no glob). Triage: dev/programme/triage/r10-round-end.md#P764. The budget file only loses entries; `budget_raise_gate.py` at the merge base grades `files_tokens.*` as `CAPFILE`, and removing a cap whose file is absent at the head is not a raise (Figures).

Carry 0 (from R11-INTAKE-R10-RESIDUE): built here, both halves. Re-measured at this merge base as it asked: `budget_raise_gate.py` at the merge base has the `files_tokens.*` → `CAPFILE` rule, so the drop is routine. Its measurement holds there too: a `files` orphan cap is refused, a `files_tokens` one passed (`TOTAL: 0 error(s)`) until this change.

Alternatives: a second, `files_tokens`-only check function duplicates the filter and fixture exemption and was not taken; adding a glob for the two paths would measure files that no longer exist at either path.

## Head

8d758b7d806173a2609c926fcc7f3f855fe26350, on merge base 367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c (origin/main tip at the run, 2026-11-16 UTC).

## Mutation proof

Failing test first: the new acceptance drive, run on the merge base's `checkOrphanCaps` with the fixture added, exits 1 with `FIXTURE VACUOUS: checkOrphanCaps did not report the files_tokens cap on docs/a-file-no-glob-matches.md exactly once (got [])`.
Mutant at the head: `['files', 'files_tokens'].flatMap` → `['files'].flatMap` in `checkOrphanCaps`; `node tools/policy/policy_lint.mjs` prints the same `FIXTURE VACUOUS` line and exits 1; restored, `cmp` against the saved copy identical.
No `.py` lines added, so `prepr.sh`'s mutant draw has no site.

## Null control

At the merge base, `node tools/policy/policy_lint.mjs` prints `TOTAL: 0 error(s)` with both orphan token caps present: the property the check now states was false on the unmodified tree without a finding. With the lint change and the caps still kept, it prints `TOTAL: 2 error(s)`, one `[budgets]` error each for `tools/audit/briefs/nudge.md` and `tools/audit/harnesses/README.md`. With the caps dropped: `TOTAL: 0 error(s)`, `FIXTURE ok`.
Grader control: the same `file_raises` call over the merge base's budget file with `files_tokens["CLAUDE.md"]` removed reports `files_tokens.CLAUDE.md: cap removed while the file it caps is still in the tree`, so the empty raise list below is not a grader that reads nothing.

## Figures

<!-- figure-block: scope-line mb=367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c head=8d758b7d806173a2609c926fcc7f3f855fe26350 -->
~~~text
MODE: SCOPED -- 1 script(s) run, 32 scoped out.
~~~
<!-- /figure-block -->
- Orphan-cap seams (the class instrument, the extended check over the tree): `node tools/policy/policy_lint.mjs` with the lint change and the budget at the merge base → `tools/audit/briefs/nudge.md` (dropped here), `tools/audit/harnesses/README.md` (dropped here); no others.
- Budget raises: `budget_raise_gate.raises_between(merge-base, HEAD, …)` → `[]`.
- `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD` → `Architecture score: dS +0.0000 NULL`.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` → `MODE: SCOPED`, runs `tests/entities.py`; `PYTHONPATH=tests/hastub python3 tests/entities.py` → exit 0.

## Red checks

none

## Forward-carry

none

## Friction

none
