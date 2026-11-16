Fix review: merge 6ee7ba56e48bdeb1b8d1c05cb7a9df3a43c17daa

bus-nonce: 24d67ab9e740de5c2d23225c2931d8c7

## Scope

Round 2 (a later round over reviewed head bba6698d438e). The packet's `## Review scope` reads `full`: no verdict on verdict/3628 names bba6698d438e, so there are no prior findings to confirm resolved, and the whole three-dot diff was reviewed. The diff has no `custom_components/` line. It touches `.github/ISSUE_TEMPLATE/` (five forms and `config.yml`), `CODE_OF_CONDUCT.md`, `tests/closure.py` (two `INERT` entries), `tests/layout.json` (one root entry), `dev/audit/config/scopes.json` (D6 universe and seat s5) and the delivery row `dev/programme/delivery/3628.md`. The delta from bba6698d438e is only the two `scopes.json` lines, which is an instrument/config delta.

## Findings

none

## Evidence

- Head: PR #3628's live head is 6ee7ba56e48bdeb1b8d1c05cb7a9df3a43c17daa, as the verdict names and as the body's `## Head` names (ev/HEAD.txt).
- Role contract current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- CI: `merge_train.py classify 6ee7ba56e48b... --pr 3628` exited 0 with `GREEN 6ee7ba56e48bdeb1b8d1c05cb7a9df3a43c17daa pending: none red: none` (ev/classify_final.txt). The only failed check run at the head is `tests / nightly-status` (ev/check_runs.txt). It is not in the `merge_train.py owed-reds` set, so it owes no answer and is no block. The digest's earlier `gate` failure was superseded; classify reads GREEN.
- Merge: `git merge-tree --write-tree origin/main 6ee7ba56e48b...` exits 0, so there is no conflict (ev/merge_tree.txt).
- `VERSION`, `custom_components/heatpump_optimizer/manifest.json` and `RELEASE_NOTES.md` are untouched across merge-base...head.
- Mutation proof, step 1. Each was run in a detached worktree at the head and then restored:
  - Delete both `INERT` entries: `PYTHONPATH=tests/hastub python3 tests/entities.py` exits 1, where the head exits 0. The `  FAIL` lines differ from the head's only by `every tracked file is either measured or deliberately classified`, which names all seven paths. The other FAIL lines are the hb:positive_control negative controls, at both ends, differing only in timing digits (ev/entities_head.txt, ev/entities_mut_both.txt). This reproduces the body.
  - Delete `".github/ISSUE_TEMPLATE/"` only: entities.py exits 1 and names the six form files (ev/entities_mut_tmpl.txt).
  - Delete `"CODE_OF_CONDUCT.md"` only: the entities.py run was killed at the 30-minute background limit before it finished, so it has no result. In its place, `closure.orphan_files()` returns `['CODE_OF_CONDUCT.md']` against `[]` at the head (ev/orphan_files.txt). That is the function the failing entities.py check reports.
  - Delete the `tests/layout.json` root entry: `tests/layout.py` exits 1 with `placement: CODE_OF_CONDUCT.md is in 0 categories`, where the head exits 0 (ev/layout_*.txt).
  - Delete both `scopes.json` entries: `check_scopes.py --repo .` exits 1 with `FAIL D6 ... universe=353` and `FAIL coverage ... unclassified=1`. The head exits 0 with `ok D6 ... universe=354` and `ok coverage ... unclassified=0` (ev/scopes_*.txt).
- Null control: base `tests/closure.py` (e75ad291) on the head tree gives `orphan_files()` = the seven new paths; the head gives `[]` (ev/orphan_files.txt). This matches the body.
- Step 2: no finder's harness applies. This is the owner's item, not a finder's finding, and the packet reads `Finder's harness: none named`. The forms have no executable harness; GitHub validates them on render.
- Step 4: no golden or claim file is touched. `tests/env_drift.py --claims-only origin/main` exits 0 at the head (ev/env_drift_claims.txt).
- Step 14: no budget, score, ledger or closures.json moves. `python3 tests/structure.py` prints STRUCTURE RATCHET PASSED (ev/structure_head.txt). The `INERT`, `layout.json` and `scopes.json` additions each classify a file this diff adds, and the mutations above show each one is what clears its check.
- Figures re-derived at the head under the body's stated rules:
  - Fields per form from `yaml.safe_load`, counting non-markdown body items and the required ones: bug 11 (7), feature 5 (3), design notes 11 (9), support 6 (5), docs 4 (3). All match.
  - `id` and `label` are unique per form, and every dropdown option is a string.
  - Labels `bug`, `enhancement` and `documentation` exist; `design` returns 404.
  - `has_discussions` is false.
  - `tests/closure.py select --diff <merge-base>` prints `MODE: FULL`.
  - `check_scopes.py --self-test --repo .` prints `SELF-TEST passed (every perturbed scope refused)`, and D6 `s5` reads 3245u (ev/scopes_selftest_head.txt, ev/scopes_head.txt).
- Body claims checked:
  - README's "Supported heat pumps and controls" table has five rows (switch, ECL110, offset entity, stored parameter, compressor frequency).
  - `config_flow.py` defaults the entry title to "Heat Pump Optimizer".
  - `plan_public.PLAN_URL` resolves to https://tvofi.github.io/heatpump_optimizer/plan/, the URL the design form links.
  - The linked decision 0014 file and docs/CONTRIBUTING.md exist at the head.
  - No workflow has an `issues:` trigger; the only matches are permission blocks.
  - `CODE_OF_CONDUCT.md` contains no email address, personal name, attribution or volume limit, and names only the account `tvofi` for enforcement.
- Not re-derived: the body says `CODE_OF_CONDUCT.md` is "byte for byte" the text the owner approved. That approved text is not in the tree, so this was not compared.
- Red checks: the body answers `instrument-self-tests` (red at bba6698d438e, repaired in 3f464acc3daf, cheaper detector named, countermeasure refusal recorded). That context is not in the owed-reds set. At this head it passes.
- Steps 15 and 16: no production code and no actuator write, so they do not apply. Step 10: the body's Forward-carry is none, and its CoC carries 0–2 are dismissed as answered in this diff; the file content above confirms that.
