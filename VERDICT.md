Fix review: merge b660da5528f359a375011497bee49e27ed561722

bus-nonce: bc7bd5f495f0379b7bfa90cfb20a4cc7

This is round 1 for #1850, the precursor of #1847. It must merge before #1847.

Measured head: b660da5528f359a375011497bee49e27ed561722. I re-read the live head before posting and it was unchanged. Main at measurement: aab94eea. The contract diff for `tools/audit/briefs/` was empty at the #1847 review against the same main.

## It carries nothing else

`git diff --stat aab94eea HEAD` touches three files (`diff_vs_main.txt`):
- `.claude/workflows/check-wave-script.mjs`, +16: group 15, the `rulePaths` pin.
- `.claude/workflows/policy_lint.mjs`, +7 -3: the squash alternative in `resolvePrFromCommit`, its fixture row, and the export.
- `docs/delivery/1850.md`: its own row.

There are no DECLARED entries, no workflow change and no version files. These are the same two pieces I mutated at #1847's head.

## Mutation proof, my mutants on this tree (`precursor_mutants.sh`; `git status` clean after)

| mutant | detector |
|---|---|
| P1: `\|\| MERGE_SUBJECT_RE.exec(...)` removed (D13-s1-01 back) | `policy_lint.mjs` `FIXTURE VACUOUS ... squash-shape subject`, rc 1 |
| P2: `rulePaths` dropped from the export | `check-wave-script` `FAIL rulePaths is exported typeof undefined` |
| P3: `rulePaths` returns `[]` | `FAIL ... parseRuleFrontmatter ... read []`, 152 passed, 1 failed |

## Null control on this tree (`null_head.txt`)

- `policy_lint.mjs`: `FIXTURE ok`, 233 pins, rc 0.
- `check-wave-script`: 153 passed, 0 failed.
- `policy_lint.mjs --budgets`: rc 0.
- `rules_sync --check`: rc 0.
- `field_coverage.mjs`: `refused=0`, `FIELD COVERAGE ok`.
- Scoped gate: `MODE: SCOPED -- 1 script(s) run` (tests/entities.py, which runs on CI; see below).

The stamp-subject row stays null.

## CI at this head (`checks_final.tsv`, commit check-runs API, background watch until every run completed)

No check is red. Every completed run passed or was skipped, among them all the required ones: `fast (3.14)` (which runs tests/entities.py, the one script the scoped gate selects, so the body's local 1-of-2060 environment failure did not reproduce on CI), `browser`, `closure-scope`, `closures`, `typing`, `hassfest`, `validate-hacs`, `policy-docs`, `wave-script`, `pr-contract`, `env-matrix`, the three `Analyze` jobs, `mutation` and `budget-raise-gate`. The one cancelled `pr-contract` run and the one cancelled `budget-raise-gate` run were each superseded by a later run of the same name that succeeded.

The body says "none expected". It is right that `policy_lint.mjs` and `check-wave-script.mjs` are base-pinned, so CI ran main's copies here, and the two new rows first run on main after the merge. My local runs above are the only execution of the new rows before then.

## Non-blocking observation (not filed)

The squash alternative now sits under comments that argue the opposite:
- Above `MERGE_COMMIT_SUBJECT_RE`: "`\(#(\d+)\)$` cannot be reused for the per-commit gap below".
- The D13-s1-01 block: "strictly narrower than falling back to subject mode".

The reuse is harmless in the window I measured. Of 442 first-parent commits in `v6.5.0..origin/main`, 0 are non-merge subjects ending `(#N)` (`fp_squash_shape_nonmerge.txt`; the squash shape occurs 611 times before v6.5.0). So no issue number can be over-collected there. But the comments are now false as written. They belong in #1847's next touch of `policy_lint.mjs` or in a later D5 pass, not as a block here.

Evidence: `evidence/`. `HEAD.txt` names the head.
