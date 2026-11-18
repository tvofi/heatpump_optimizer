Fix review: merge 8e0363b8902905a78733e8f0fe7a2b27fd8c3211

bus-nonce: 17a4a05889104e11481d6205e629d1a3

Round 1 (first review; packet review scope: full).

## Evidence

- Head re-read before return: `refs/heads/policy/r11-instrument-triage-phase` = 8e0363b8902905a78733e8f0fe7a2b27fd8c3211 (`git ls-remote`); merge base ae0ed64af898d8923ac35afe6e9c031ac1e6b111; body `## Head` names this head. `ev/HEAD.txt`.
- CI: `merge_train.py classify 8e0363b8902905a78733e8f0fe7a2b27fd8c3211 --pr 3732` exit 0, `GREEN 8e0363b8902905a78733e8f0fe7a2b27fd8c3211 pending: none red: none` (`ev/classify.txt`). `tests / nightly-status` reads failure in the packet digest but is outside the `owed-reds` set (`ev/owed-reds.txt`), so it is neither answered nor a block.
- Merge with main: `git merge-tree --write-tree origin/main 8e0363b8902905a78733e8f0fe7a2b27fd8c3211` exit 0 at origin/main 1723f9fdc9d8a6e6987190d2887686297a621dd4; no claim file in the diff, so no `MERGE-CLAIM` line (`ev/merge-tree.txt`).
- Mutation proof re-run (step 1), `python3 tools/audit/seat/plan_page.py --self-test` with `PYTHONDONTWRITEBYTECODE=1` and `__pycache__` cleared: pristine head `154 checks, 0 failed`; mutant 1 (drop `instrument-triage` from `PHASES`) `154 checks, 3 failed`; mutant 2 (move it after `closure`) `154 checks, 2 failed`; an extra mutant 3 of mine (move it before `stamps`) `154 checks, 1 failed`; restored `0 failed` (`ev/mutants.txt`). This matches the body's mutant 1 and 2 figures. A first pass without clearing the bytecode cache ran a stale `.pyc` on the restored file (same size and same-second mtime as the mutant); I discarded it and re-ran everything clean.
- Null control (step 3): `python3 tools/audit/seat/plan_phases.py --check dev/programme/round11/phases.json` rc=0, and the file holds 0 `instrument-triage` entries; `plan_phases.py --phases dev/programme/round11/phases.json --html` draws `<tr data-phase="instrument-triage" data-st="not-started">` (`ev/mutants.txt`, `ev/lints.txt`). Reproduces the body's claim.
- Lints at the head: `brief_lint.mjs` reports `PLAYBOOK ok`, and the CI run of `tests / briefs` at this head succeeded. `rules_sync.mjs --check` prints `RULES-SYNC ok`. `roster_edit.py`, `architect-planner.md` and `plan-review.md`, cited in the new row and paragraph, all exist (`ev/lints.txt`).
- Policy budgets, `node tools/policy/policy_lint.mjs --budgets` and the plain run at four trees (`ev/policy-budgets.txt`). The playbook (`dev/audit/README.md`, cap key `tools/audit/README.md`) reads 5934/6059 at the merge base and 6072/6059 at the head standalone (`TOTAL: 1 error(s)`). It reads 5915/6059 at origin/main and 6052/6059 on the probe merge of the head into origin/main 1723f9fd (`TOTAL: 0 error(s)`). `proposal-triage.md` reads 589/594 tokens and 42/42 lines at the head. The corpus reads 71405 on the merge, under 71712. No budget raised.
- Steps 4 and 5: no golden fixture, no claim file, no `VERSION`, manifest or `RELEASE_NOTES.md` change in the three-dot diff (`ev/lints.txt`), so `env_drift.py --all` has nothing to compare.
- Step 6, class: a scout ran `git grep` for hard-coded phase keys (`"fix-waves"`, `"verify-judge"`) and for `PHASES` / `plan_phases` imports across `tools/` and `tests/`. The only hits are `plan_page.py`'s `import plan_phases` and the data file `dev/programme/round11/phases.json`, so no second list of phase keys needs the new entry. That makes this a one-seam class, not proof of compliance.
- Step 9: there is no finder's harness, since this is a policy change carrying an owner ruling, not an audit finding. The packet records `Finder's harness: none named`. The instrument evidence is the PR's own self-test arms, which the mutants above show detect the change.
- Step 11: the reds in the branch history on owed-reds checks (`tests / briefs`, `pr-contract / pr-contract`, `governance / policy-docs`, `governance / env-matrix`, `tests / fast (3.14)`) are each named in `## Red checks` with a cheaper detector or a cause. I checked only that an answer exists, not that it is right.
- Steps 14 and 15: the diff moves no budget, score or closure; the new tuple and its self-test arms follow the existing `PHASES` / `refuses` pattern.
- Code-owned paths (`dev/governance/roles/proposal-triage.md`, `dev/audit/README.md`): merging still needs the owner's approving review at the head, as the body's `## Approval` states. This verdict is not that approval.

## Notes

- Note: figure: the body states `node tools/policy/policy_lint.mjs` exits 0. At this head standalone it exits 1, with the playbook at 6072/6059 tokens. It passes only on the merge with current main (6052/6059, 7 tokens of headroom), because main shortened the playbook after the merge base. The PR's own addition overruns the cap measured at its own merge base, and the train must re-prove it on whatever main it merges onto. Carry: dismissed: the merged tree is within cap and the train re-runs `policy-docs` on the current main; it is a figure in the body, not a code defect
- Note: body: `## Head` keeps three stale paragraphs for earlier heads (3990b047, 21df11ae, 2df90159) and a bare SHA line `26b42ae5…`; the first paragraph correctly names this head. Carry: dismissed: paperwork only, no effect on the reviewed head

## Friction

- Friction: the session's stop hook reported six `policy_lint` citation errors in `tools/audit/README.md` (`wave-1b-groups.json` and others) and said "this turn touched the policy corpus", while `git status` in the checkout was empty and this seat edited no file; the plain `policy_lint.mjs` at the merge base and at origin/main prints `TOTAL: 0 error(s)`. Unmeasured beyond that. Carry: dismissed: not established by a measurement with a null control, and not a finding of this PR
