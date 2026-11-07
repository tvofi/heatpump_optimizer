Fix review: merge 4ee05dcd9ac1bfd8a9fc8ee63a95f98d9b2eff9b

bus-nonce: 8132d0bde94d2efd9c0682d2c6c23e33

## Verdict

This is fix-review round 5 of #3244 (R10-HOTFIX-SAV-ESTIMATE part 2, topic r10-sav-wood-heat), at head 4ee05dcd9ac1bfd8a9fc8ee63a95f98d9b2eff9b. Round 4 blocked 8bc540e0 as ci-red on CodeQL alert 50, `py/jinja2/autoescape-false`. That block is repaired at its root.
- `CodeQL` (check run 128325422020) concluded `success` at the head: "No new alerts in code changed by this pull request".
- The harness now builds `jinja2.Environment(autoescape=True)`. Nothing is suppressed or dismissed.
- The head is GREEN, and every code finding of rounds 1 to 4 still holds at this head, because the production, test, doc and golden trees are byte-identical to 8bc540e0's.

## Findings

- Follow-up: the card mutant C3 (`woodNote = false`) and the earlier R9 (`!!fuel`) survive `tests/card.mjs` and die only in `tests/card_browser.mjs`, which only CI's `tests / browser` lane runs. That lane is green at this head, and my own `card_browser.mjs` run passed. Carry: R10-HOTFIX-SAV-ESTIMATE | dismissed: covered by the tests browser lane
- Follow-up: the body names `af56818b5` as "the merge base" for its census and null-control base. The PR's merge base is f2a015142714. `af56818b5` is an older ancestor of main, from before part 2. The conclusion still holds: I re-ran both harnesses at f2a015142714 and they read the same as the body says. Carry: dismissed: wording slip with no effect on any figure, re-derived here at the true base
- Follow-up: some check-run ids in the body's `## Red checks` are no longer the live ids. GitHub re-issued the job ids at the head around 08:01Z, so `instrument-self-tests` is now 128347084107, where the body has 128324881150. The jobs are still named correctly by job name and run id. `pr-contract / pr-contract` (128346768943) concluded `success` at 08:03:39Z, after those reds. Carry: dismissed: the contract accepts the body after the last red; the ids are cosmetic

## Evidence

- Head: `ev/HEAD.txt` holds 4ee05dcd9ac1bfd8a9fc8ee63a95f98d9b2eff9b. `git ls-remote` read `fix/r10-sav-wood-heat` at the same SHA at 08:27Z. The body's `## Head` names it and the code handoff 07461bb3. `git diff --stat 07461bb3 4ee05dcd9` is empty (`ev/body_figures.txt`).
- Role contract: `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- The delta since round 4 (8bc540e0 to the head) is one PR commit, 07461bb37. It changes one line of `dev/audit/harnesses/r10_sav_receipt_render.py` and adds four lines of comment. The rest is main's merge 992dd8a58. `git diff --stat 8bc540e0 HEAD -- custom_components blueprints docs README.md tests/entities.py tests/features.py tests/card.mjs tests/card_browser.mjs tests/golden` is empty (`ev/class_delta.txt`).
- Harness sha1s equal the body's: 6af7338b358b at the head, b97e785bf7c0 at 8bc540e0.
- Merge: `git merge-tree --write-tree origin/main HEAD` against origin/main 0e9c508c1260 exits 0. It prints `LEDGER-MERGE: resolved tests/closures.json`, with no conflict and no MERGE-CLAIM line (`ev/merge_tree.txt`).
- CI, read across all check-run pages (81 runs, one page of 100):
  - `merge_train.py classify` exited rc 0 at 08:33:23Z: `GREEN 4ee05dcd9ac1bfd8a9fc8ee63a95f98d9b2eff9b pending: none red: none` (`ev/classify_series2.txt`).
  - Before that, an earlier run of the same waiter printed `RED … red: gate` (`ev/classify_series.txt`). The red was edit run 42345649254's `gate` (128347075228). At 08:02:30Z it printed `FAIL run(s) [42345230614, 42353428221] at this head are still being judged; their gate decides`. That is the edit-gate deferral race, not a content red.
  - The run that decides is code run 42345231019: its `gate` 128347084313 printed `PASS` at 08:05:58Z. Both deferred-to edit gates printed `PASS`: 128347088909 at 08:05:42Z and 128347497957 at 08:06:49Z. Run 42345649254 was then re-run at 08:18Z, and classify turned GREEN.
  - `governance / instrument-self-tests` (128347084107) is `cancelled` at 06:48Z after its 30-minute timeout. The body answers it (R10-HOTFIX-SELFTEST-TIMEOUT), and the code gate passed over it.
- Alert 50 is closed at the head. `CodeQL` (128325422020) is `success` with the title "No new alerts in code changed by this pull request". `codeql / Analyze (python)` (128347084264) is `success`. I could not query code-scanning directly: this seat has no code-scanning API tool. Its CodeQL check summary is the evidence.
- Mutants on the new line, my own (`ev/mutants_harness.txt`), in a `git archive` export of the head under venv-ha:
  - M0, the null: rc 0, three arms ok.
  - M1, `autoescape=True` → `False`: rc 0 and identical output. It survives, as the body states and as it should: the rendered output is the same either way, and CodeQL is that line's detector.
  - M2, the escape perturbation (the note moved inside `{{ "…" }}`): `RESULT wood notes=0 want=1 DEFECT` with `Firewood&#39;s`, rc 1. So the body's claim holds: an edit that moves the note into an expression goes loudly red, not silently green.
  - Identity: the round-4 harness and the head harness on the same blueprint give byte-identical output (`ev/render_identity.txt`: IDENTICAL).
- Render companion at both ends: at the head, rc 0, `RESULT wood notes=1 want=1 ok`, `no-wood notes=0 want=0 ok`, `no-saving notes=0 want=0 ok` (`ev/render_head.txt`). On the merge base f2a015142714's blueprint, rc 1, `RESULT wood notes=0 want=1 DEFECT` (`ev/render_base.txt`).
- Finder's harness: `r10_rca_sav_estimate.py census` from `handoff/r10-rca-sav-estimate`, sha1 04b644563c84d26378cad42a603dc050e7e5fd88, the same as the body's.
  - Run at f2a015142714 and at the head, both rc 0, with identical six lines: single 1.00, unvalved 0.92, valve-at-curve 1.00, valve-charged 1.00, wood-warm 1.00, wood-hot 1.00, all ok (`ev/census_base.log`, `ev/census_head.log`).
  - It is flat by design, because part 1 settled the census.
- Consumers of the monthly saving, by my own rule. The rule is `git grep -E 'savings_sek|saving_sek|savings_months|monthly_receipt|saving_includes_wood|MonthlySavingsSensor|wood_note'` over custom_components, blueprints, docs (less design) and README.md.
  - It returns 12 files (`ev/class_delta.txt`), each in the body's seam table.
  - No production line changed since round 4, which enumerated the class with three rules and found no undispositioned seam.
- Full suites at the head, in a detached worktree, run in full:
  - `entities.py`: ALL 2642 ENTITY CHECKS PASSED, rc 0. Its FAIL lines are its own negative self-tests.
  - `features.py`: ALL 4877 FEATURE CHECKS PASSED, rc 0.
  - `structure.py`: STRUCTURE RATCHET PASSED, rc 0.
  - `plan_view.py && card.mjs`: ALL CARD CHECKS PASSED, rc 0.
  - `card_browser.mjs`: ALL BROWSER CHECKS PASSED, rc 0.
  - `git status --porcelain` was empty afterwards (`ev/wt_status.txt`).
- Golden claims: `env_drift.py --all f2a015142714` gives `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56`, rc 0 (`ev/env_drift.log`).
  - `claims-for: 7.1.4` equals VERSION 7.1.4.
  - `claimed_drift.txt` adds only the five `coord_*` lines, each one key (`saving_includes_wood`), never recorded. `card_claimed_drift.txt` is identical to origin/main's.
  - VERSION, manifest.json, RELEASE_NOTES.md and card_claimed_drift.txt are unchanged against the base: `git diff --quiet` exits 0.
- Delivery row: `dev/programme/delivery/3244.md` is in the three-dot diff.
- Body: `## Head` names the code SHA. `## Red checks` names every concluded red across all pages by job name: `instrument-self-tests` cancelled, and the edit-run `gate` deferrals. Each Forward-carry item has a Carry line.
- Review packet rendered here (`ev/review-packet.md`): refusals none, advisories none. carry_audit: 3 items, 3 routed.
