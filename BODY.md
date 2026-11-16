The owner's item (tvofi 2026-11-15, folded into round 11, not finder-critical): a brief, typical code of conduct and a set of issue forms, so that GitHub's Community Standards page lists both as present and an issue arrives with what a fixer or designer needs to start without a follow-up question. No product code; no `VERSION`, manifest or `RELEASE_NOTES.md` change.

**`CODE_OF_CONDUCT.md`** is the exact text the owner approved (tvofi 2026-11-15), byte for byte, and applies to people and agents alike. It has an agents section. It carries no attribution and sets no limit on how many issues, comments or pull requests an agent may open. Enforcement names only the GitHub account `tvofi`; private reports go through the advisory form SECURITY.md names, or GitHub's "Report content". It contains no email address, name or other personal contact.

Carry 0: superseded by carry 1 and carry 2, which replace the file with the approved text; the file now is that text. Carry 1: the file is the approved text with the agents section and no volume limit. Carry 2: no attribution, link or mention of another code of conduct appears in the file, and this body names none. Carry: dismissed: all three answered in this diff.

**`.github/ISSUE_TEMPLATE/`** holds five YAML issue forms and `config.yml`:
- **Bug report** (`bug`). Required fields:
  - what happened and what was expected;
  - the integration version and the Home Assistant version;
  - the heat pump or controller brand and model;
  - the control path. This is a multi-select of the five paths the README's "Supported heat pumps and controls" table names, plus plan-only and "Not sure". The frequency path is split into Observe and Control.
  - when it happened, with date, time and time zone.

  Optional fields: steps to reproduce, diagnostics, log lines and card screenshots. The diagnostics field gives the download path (Settings > Devices & services > Heat Pump Optimizer > ⋮ > Download diagnostics) and a plain warning that the repository is public. "Heat Pump Optimizer" is the default entry title in `config_flow.py`'s `async_create_entry`.
- **Feature request** (`enhancement`). Required: the need in the user's own terms, what they would like, and their setup (equipment, control path, and price source or tariff type). Optional: alternatives considered and how they do it today.
- **Feature request with design notes** (`enhancement`). It has the feature request's fields plus:
  - proposed behaviour;
  - the entities, options or services it adds or changes;
  - configuration;
  - edge cases and failure behaviour;
  - verification;
  - whether the contributor intends to open a pull request.

  The form says that a significant feature gets a design and a design review first (decision 0014) and links the plan page, `plan_public.PLAN_URL`.
- **Hardware or price source support** (`enhancement`), added. The README says control goes only through ordinary Home Assistant entities, so whether a device can be supported depends on its Home Assistant integration and the entities it exposes, with their units and writability. Neither the bug form nor the feature form asks for that, so this request would otherwise need a follow-up. Required: device, its Home Assistant integration, its entities and units, what the user wants done with it, and whether they can test it (with writes, read-only, or not at all).
- **Documentation problem** (`documentation`), added. A docs report filed as a bug would have to fill in device and version fields that do not apply, and would still leave out the page and the sentence. Required: the page, the sentence, and what is wrong.
- **Not added: a question form.** Discussions is disabled on the repository, so `config.yml` has no questions link. A question can be a blank issue, which stays enabled.
- `config.yml`: `blank_issues_enabled: true`, and a contact link that routes security reports to SECURITY.md's private advisory form.

**Labels.** Each form applies only a label that already exists on the repository, because GitHub drops a form label that does not exist. `get_label` confirmed `bug`, `enhancement` and `documentation`; `design` and `outside-intake` do not exist. The three `enhancement` forms are told apart by their title prefixes `[Feature]:`, `[Design]:` and `[Support]:`, and the other two by `[Bug]:` and `[Docs]:`.

**Issue-body readers checked.** A form's body is markdown made of `### <label>` headings.
- `tools/audit/seat/outside_intake.py` reads only an issue's number, `user.login`, `user.type`, `created_at` and whether it is a pull request (the `_ISSUE`, `_COMMENT` and `_THREAD` jq programs). It reads comment bodies only for `ANSWER_MARK` and `REFUSED_MARK`. It reads no issue body, title or label, so a form issue is listed, answered and refused exactly as a blank one is.
- `tools/audit/seat/plan_public.py` reads no issue. It stages the plan page from the state ref.
- `tools/audit/carry_audit.py`'s `gh_issue_text` reads the body of an issue a pull request closes. `fold_problems` matches only `FOLD_LINE` (`Fold (x): ...`) line by line, which neither `### ` headings nor `_No response_` can match.
- `tools/policy/friction_issues.mjs` compares the bodies of its own `[policy] recurring friction` issues byte for byte, not form issues.
- No tracked code routes on issue label names. The only label code is `tools/audit/seat/ci_probe.py`, which writes labels, and `tools/ci/prelude.py`, which reads pull-request labels.
- No workflow is triggered by `issues:`. The matches in `.github/workflows/*.yml` are permission blocks.

**Classification.** `CODE_OF_CONDUCT.md` and the `.github/ISSUE_TEMPLATE/` prefix are on `tests/closure.py`'s `INERT` list, next to `SECURITY.md`. GitHub renders these files and no gate script reads them. `CODE_OF_CONDUCT.md` is also placed in `tests/layout.json`'s `root` category; `.github/**` already covers the forms. Editing `closure.py` is what makes the scope `MODE: FULL`. `CODE_OF_CONDUCT.md` is also in `dev/audit/config/scopes.json`'s D6 `universe` and seat `s5`, directly after `SECURITY.md`, so the D6 finder that reads the other top-level contributor documents reads it; `.github/ISSUE_TEMPLATE/*.yml` is no `classify` glob of any dimension and needs no entry.

## Head

3f464acc3daf31e66d9b1a001e01a70429ec923d, measured on origin/main e352724335c136b65562cd3e71f728549ad04a82 (merge base e75ad291ff5c58f7c8362b0a20fbe6b230adf717) at 2026-11-16T14:31Z. One commit on bba6698d438e: the D6 classification of `CODE_OF_CONDUCT.md` in `dev/audit/config/scopes.json`. `git merge-tree --write-tree origin/main HEAD` reports no conflict, so main was not merged. `PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh BODY.md` at this head exits 0 (`PRE-PR: 3f464acc3daf... rc=0`).

## Mutation proof

The fix's production lines are the two `INERT` entries in `tests/closure.py`: `"CODE_OF_CONDUCT.md"` and `".github/ISSUE_TEMPLATE/"`. Delete both in a detached worktree at the head and run `PYTHONPATH=tests/hastub python3 tests/entities.py`. It exits 1, where the restored head exits 0. Its `  FAIL` lines differ from the head's by exactly one check, ignoring timing digits:

    FAIL every tracked file is either measured or deliberately classified  [these force the FULL suite when touched: .github/ISSUE_TEMPLATE/1-bug_report.yml, .github/ISSUE_TEMPLATE/2-feature_request.yml, .github/ISSUE_TEMPLATE/3-feature_design.yml, .github/ISSUE_TEMPLATE/4-hardware_support.yml, .github/ISSUE_TEMPLATE/5-documentation.yml, .github/ISSUE_TEMPLATE/config.yml, CODE_OF_CONDUCT.md]

The other `  FAIL` lines appear at both ends: they are the script's own negative controls, which print FAIL and pass. Comparing the two is `diff` of `grep "  FAIL"` over the head and mutant outputs, cut to 80 columns.

The `tests/layout.json` root entry has its own mutation. Without it, `tests/layout.py` exits 1 with `placement: CODE_OF_CONDUCT.md is in 0 categories of tests/layout.json`, which is the first run on this branch. With it, the script exits 0.

The `scopes.json` entry has its own mutation: at bba6698d438e, the head without it, `python3 -I tools/audit/check_scopes.py --repo .` exits 1 with `FAIL D6 ... classified in neither universe nor static: CODE_OF_CONDUCT.md` and `FAIL coverage ... in no universe and not excluded: CODE_OF_CONDUCT.md`; at this head it exits 0 (`ok D6 ... universe=354`, `ok coverage ... unclassified=0`).

## Null control

On the base `INERT` list with the new files present, `closure.orphan_files()` returns all seven new paths, and the head returns `[]`. That is the control: the classification is what clears it. The forms have no executable null control; GitHub validates them when it renders them. The YAML was parsed locally: every `id` and `label` is unique within its form, and every dropdown option is a string.

## Figures

- Fields per form: bug 11 (7 required), feature 5 (3), design notes 11 (9), support 6 (5), docs 4 (3). Counting rule: the non-markdown `body` items, and those whose `validations.required` is true, from `yaml.safe_load` of each `.github/ISSUE_TEMPLATE/*.yml`.
- `has_discussions: false`: `gh api -X GET search/repositories -f q='repo:tvofi/heatpump_optimizer' --jq '.items[0].has_discussions'`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: FULL`, reason "tests/closure.py changes the gate itself".
- Run at the head with `PYTHONPATH=tests/hastub`, each exiting 0: `tests/env_drift.py --claims-only origin/main`, `tests/closure.py selftest`, `tests/layout.py`, `tests/harness_headers.py` and `tests/entities.py`. These are `tests/run.sh`'s `run_always` scripts plus the classification check. The rest of the `MODE: FULL` suite is left to CI.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `python3 -I tools/audit/check_scopes.py --self-test --repo .`, the command `governance.yml`'s `instrument-self-tests` step runs: `SELF-TEST FAILED` at bba6698d438e, `SELF-TEST passed (every perturbed scope refused)` at this head. D6 seat `s5` reads 3245 units against `ledger.max_units` 4500 (check_scopes.py's own `s5:` field).

<!-- figure-block: scope-line mb=e75ad291ff5c58f7c8362b0a20fbe6b230adf717 head=3f464acc3daf31e66d9b1a001e01a70429ec923d -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

## Red checks

- `instrument-self-tests` (step `python3 -I tools/audit/check_scopes.py --self-test --repo .`), red at bba6698d438e and not at its merge base. Cause: the PR added the tracked top-level `CODE_OF_CONDUCT.md`, which D6's `classify` glob `**.md` claims, without placing it in D6's `universe` or `static`; the live-scopes arms of the self-test refused it. Repaired in 3f464acc3daf. Cheaper detector: the live check `python3 -I tools/audit/check_scopes.py --repo .` names the file by itself (shown failing at bba6698d438e and passing at this head above); it is in no `tools/pr/prepr.sh` step, so it first ran in CI. Run by prepr only on a diff that adds a tracked file, its standing cost is 23-24 s wall-clock per such run (two timed runs, at bba6698d438e and this head) and 0 s otherwise. Not built in this PR: the detector is a `prepr.sh` change, outside this group's seam.

## Forward-carry

none

## Friction

none
