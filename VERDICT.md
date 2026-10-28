Fix review: blocked f74f6cbb23649562bcc3db7f6415334707b1fd23 class-open: reauth_confirm tibber_token spells a second widget for a registry-backed setting

bus-nonce: 5b8ea55477ed7080db60e6cc4e79d22b

## Block

The class the PR states, in its test's own header, is "every setup-flow field whose key has an `_OPTION_FIELDS` row renders that row's widget OBJECT". `async_step_reauth_confirm` (config_flow.py, reached by `async_step_reauth`) is a setup-flow form whose only field, `CONF_TIBBER_TOKEN`, has a registry row (`_F("entities", CONF_TIBBER_TOKEN, '', _tibber_token_selector(), ...)`). That row's widget is built a second time: `{vol.Required(CONF_TIBBER_TOKEN): _tibber_token_selector()}`. The site is not in the diff, and the body does not disposition it. `SETUP_FORM_STEPS` enumerates 10 of the flow's 13 form-rendering steps and leaves out `reauth`/`reauth_confirm`. The test's predicate therefore has an unguarded domain, and the finder's `--all` arm also stops at the first screens, so both read 0 while the seam is open. A reviewer-built census over every `async_step_*` of `HeatPumpOptimizerConfigFlow` reads `all_steps_spelled_twice=2` (`reauth:tibber_token`, `reauth_confirm:tibber_token`) at this head. With the one-line swap `_prefill_row(CONF_TIBBER_TOKEN).widget` it reads `0` (that swap was not pushed). `reconfigure` routes through `async_step_user`, so it is covered by C2. Repair: make that swap, add `reauth_confirm` to `SETUP_FORM_STEPS` (the reach floor moves with it), or disposition the site in the body with its reason.

Round: first fix review of this PR as far as this seat can see (no earlier verdict was read).

## Findings

- The finder's harness `wizard_widgets.py` (sha1 66b390554c0aa54c8960eacb532b04ff827ca8cf) exists only at `3930b421a`, which only `refs/tags/archive/handoff-audit-r10-arch2-s5` reaches. No branch or tree path holds it. The fixer and this reviewer both ran an out-of-tree copy, so the group's later arms (B merge resolution, arm D) depend on an archive tag for the instrument the body re-runs on the merged tree. It should land under `dev/audit/rounds/round10/D7/arch2-s5/` (fix-review.md 9, fixer.md 18). Carry: R10-CONFIGFLOW-PAGES

- The body quotes the \`class_excess_loc\` re-record as 18038 -> 17922. The diff to \`tests/structure_budgets.json\` writes 18037 -> 17921, so the quoted figure and the recorded one differ by one at both ends. The ratchet passes at the head, but this seat did not re-derive the row. The second of arm A and this PR to merge re-measures that row on the merged tree, as the body says, and should quote the file's value. Carry: R10-CONFIGFLOW-PAGES

## Evidence

- Head measured: f74f6cbb23649562bcc3db7f6415334707b1fd23. It is still the PR head at verdict time (`refs/pull/2915/head`), and the dispatch head is the same SHA. Role contracts: `git diff merge-base...origin/main -- dev/governance/roles/` is empty. The review packet reported no refusals and no advisories, and `CARRY-AUDIT` read 1 routed, 0 unrouted.
- Finder's harness (from `3930b421a`, run in this seat's worktrees on Python 3.14.7 /opt/hpo/venv-ci; ev/finder_harness.txt):
  - base 6d86acc90 and merge base b0b2d7697: RESULT wizard_fields=46 in_registry=44 spelled_twice=44 disagree=0 golden_equal=1. `--all` gives other_in_registry=20 other_spelled_twice=20 other_disagree=0. `--bump heat_pump_cop_nominal` gives disagree=2.
  - head: RESULT spelled_twice=0 disagree=0 golden_equal=1. `--all` gives other_spelled_twice=0. `--bump` gives disagree=0. Every figure the body quotes for the harness re-derives.
- Mutation proof (ev/mut*.txt), with each mutant restored afterwards:
  - base config_flow.py under head tests: `1 of 507 checks FAILED`, 64 spelled twice, rc=1.
  - `copy.copy` in `_wizard_fields`: FAILED, rc=1.
  - single C2 site `weather_entity` back to `_entity_of("weather")`: FAILED (`user:weather_entity`).
  - single wood probe back to `_entity_of(["sensor"])`: FAILED (`quick_setup:wood_tank_top_entity`).
  - `dhw_windows` given its own TextSelector: FAILED (`dhw:dhw_windows`).
  - No mutant survived.
- Head tests: `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py` reports ALL 507 checks PASSED, rc=0 (ev/steps_head.txt).
- Null control: golden_equal=1 at both ends and disagree=0 at both ends. The three-dot diff vs b0b2d7697 touches none of VERSION, RELEASE_NOTES.md, manifest.json, claimed_drift.txt, card_claimed_drift.txt (count 0). No golden moves and nothing is claimed.
- Figures: three-dot stat 6d86acc90...d52036166 reads 3 files changed, 169 insertions(+), 210 deletions(-), which matches the body. `score.py --diff b0b2d7697` reads `Architecture score: dS +0.5850 IMPROVES`, literal_clone_copies 185 -> 123, which matches the body. `tests/structure.py` at head reads STRUCTURE RATCHET PASSED. The figures `PRE-PR` and `ci_predict` were not re-run.
- Merge: `git merge-tree --write-tree origin/main f74f6cbb23649562bcc3db7f6415334707b1fd23` exits 0, with no MERGE-CLAIM marker.
- CI on the head (ev/ci_state.txt): no check run concluded red. coverage, closures, fast (3.14), codeql python and instrument-self-tests were still in progress at read time. The verdict does not turn on them.
- Reviewer-built instrument, disclosed as the reviewer's own and not the finder's: ev/census_all_steps.py. It drives every `async_step_*` with no input and checks widget identity against `_OPTION_FIELDS` (ev/reviewer_census.txt). Merge base: 66/66 spelled twice. Head: 2/66. Head plus the one-line reauth swap: 0/66.
