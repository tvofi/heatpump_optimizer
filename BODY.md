Adds audit dimension D15, a debugging run from a live diagnostics bundle (#1938's addendum: scope, graders, pass/refuse bar), and registers it in every enumeration the round drivers and checks read. Stacked on #2207 (`fix/r10-instruments`).

## Approval

Owner approval is required before merge on three counts. The raise was approved before the push: tvofi, 2026-10-14, in session, verbatim "Approve raise (Recommended)". It covers exactly the three caps below, and the commit message carries it.

- **New policy file** `dev/governance/dimensions/D15.md` and its `CLAUDE.md` index row.
- **Moratorium override:** decision 0012's process moratorium (to 2026-10-31) refuses a new policy file; tvofi ruled on 2026-10-14, in session, to override it for this one file.
- **Cap entries (a budget raise):** `dev/governance/config/policy_budgets.json` gains `files` and `files_tokens` entries for `dev/governance/dimensions/D15.md`, and `corpus_tokens` is re-recorded to the value `node tools/policy/policy_lint.mjs --budgets` measures (approved). Payments considered: (1) cutting D15 to fit inside the corpus band. One draft fitted, but the owner's version-seam and attribution rules then took it past the band, and cutting further drops a grader or the privacy gate. (2) Cutting other policy files. They are outside this lane, and each is at or near its own zero-headroom cap.

D15 is isolated (own worktree), because its perturbations edit production. It runs every round (CADENCE 1). Its three seats sit on box B8: D15-s2 and D15-s3 are heavy, D15-s1 is light. The bundle path reaches D15 seats only through `args.debug_bundle` and `args.debug_export`, which must be absolute paths.

Seat split, disjoint by `check_scopes.py`:

- s1: M1 to M4, covering intake and version seam, the privacy gate, ingest, and store replay.
- s2: M5 and M6, timeline replay and the monitor re-run.
- s3: M7 and M8, the row scan and anomaly-to-seam mapping.

## Head

`05e3146f74fb960628a6b5dfe339c56cb43b8e35` (`handoff/r10-d15`), merge base `17f1c55fa`, stacked on #2207's `4b58d3d6e`.

## Mutation proof

- `.claude/workflows/audit-find.js`: replacing `BUNDLE_DIMS.has(dim) ?` with `false ?` turns this red: `FAIL D15's finders carry the named bundle and export, or are told to report every step unfinished` (`node tools/policy/check-wave-script.mjs`, 178 passed, 1 failed).
- Disabling the absolute-path refusal (`if (false && [debugBundle, debugExport].some`) turns this red: `FAIL a relative bundle path is refused before Prepare`.

## Null control

At the unmutated head, `node tools/policy/check-wave-script.mjs` passes all its checks. In the new test, the null arm checks that no non-D15 finder prompt carries the bundle path, and it passes.

## Figures

- `python3 tools/audit/check_scopes.py --repo . --ref HEAD` rc=0 (prints `ok D15 mode=cells seats=3`)
- `python3 tools/audit/check_scopes.py --repo . --ref HEAD --self-test` rc=0
- `node tools/policy/check-wave-script.mjs` rc=0
- `node tools/policy/policy_lint.mjs` rc=0. It was rc=1 at the parent commit, without the cap entries (the D15 `budgets` and `named-docs` errors).
- `node tools/policy/policy_lint.mjs --budgets` prints D15 and the corpus against their caps
- `node tools/policy/rules_sync.mjs --check` rc=0
- `node tools/policy/brief_lint.mjs` rc=0
- `python3.13 tests/layout.py` rc=0
- `PYTHONPATH=tests/hastub python3.13 tests/structure.py` rc=0
- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh` with python3.13 first on PATH: rc=0, `MODE: SCOPED -- 2 script(s) run, 31 scoped out`: `tests/entities.py` (its template-acceptance arm green) and `tests/harness_headers.py`, plus the run_always lines; `5 TEST SCRIPT(S) PASSED`
- `git diff $(git merge-base origin/main HEAD)...HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION custom_components/heatpump_optimizer/manifest.json RELEASE_NOTES.md` is empty

## Red checks

- `budget-raise-gate`: red by design. This diff makes two budget raises (`corpus_tokens` 60449 -> 61026, and the new D15 caps), and the gate stays red until tvofi approves at the head. That approval follows review and cites mandate 6175172275 (tvofi's #201 comment, scope all, 2026-10-14T18:14Z to 2026-10-28T18:14Z). There is no cheaper detector, because this gate is the detector.
- `nightly-status`: this check grades main's nightly (#2205, which a fixer is working on), not this diff. The diff touches nothing the nightly reads: dimension briefs, audit config, audit drivers and policy caps. No cheaper detector applies to this branch.
- `wave-script`: red because CI grades with the base's checker. The step "Restore the check source from the base commit" in `.github/workflows/governance.yml` takes `tools/policy/check-wave-script.mjs` and `tools/audit/*.sh` from the base, not from this head. Check-run 116063565766 at `21ef4cdbf` gave 173 passed and 3 failed:
  - Two failures are the base checker's own negative controls, which used `D15-s1` as the seat id that does not exist.
  - One failure is the base `prepare_baseline.sh` list `ISOLATED_DIMS`, which lacks D15, against this head's `audit-find.js`, which has it.
  This head's checker passes all three (`node tools/policy/check-wave-script.mjs`, 179 passed, 0 failed). The check clears once the base carries the graders this stack changes: #2207 merges, then main is merged in. The base-graded check is the detector, so no cheaper detector exists.
- `tests/entities.py`, template-acceptance arm: red only before the cap commit, because `policy_lint` refused the uncapped D15. That refusal is the cheaper detector, it already exists and it fired. It is green at the head.

## Forward-carry

- D15.md, Out of scope: the fix-phase lead that each cycle row should record the version that wrote it.
- The bundle-specific version attribution case (v6.7.17 against v7.0.0, rows 1 to 552 and 553 to 554) belongs in the round-10 D15 seat brief, not in policy.

## Friction

- `policy-caps-canon-path`: unclear: existing dimension briefs are capped as `tools/audit/briefs/D<k>.md`, but a new file's cap must use its own path `dev/governance/dimensions/D15.md`. The canon key refuses with "matched by no POLICY_GLOBS pattern".

🤖 Generated with [Claude Code](https://claude.com/claude-code)
