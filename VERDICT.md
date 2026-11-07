Fix review: blocked 8bc540e052a8a4ac048715d4d2e7d0ab9a260c08 ci-red: CodeQL code-scanning alert 50 py/jinja2/autoescape-false on the new render harness, unanswered in Red checks, so pr-contract and the code gate are red

bus-nonce: 87d2fb78f58176bbc3387d9dabb56fbe

## Block

This is fix-review round 4 of #3244 (R10-HOTFIX-SAV-ESTIMATE part 2, topic r10-sav-wood-heat), at head 8bc540e052a8a4ac048715d4d2e7d0ab9a260c08.

`python3 tools/audit/seat/merge_train.py classify 8bc540e052a8a4ac048715d4d2e7d0ab9a260c08 --pr 3244` prints `RED 8bc540e052a8a4ac048715d4d2e7d0ab9a260c08 pending: none red: gate` (rc 1). It printed that on every run from 23:36Z to 00:49Z (`ev/classify_series.txt`, `ev/classify_final.txt`). A red CI never carries.

This time the red is the diff's own. Round 3's deferral loop is not the cause.
- `CodeQL` (check run 128216329154) concluded `failure`: "1 new alert including 1 high severity security vulnerability … in code changed by this pull request". The packet rendered it while it was still `neutral`.
- The alert is code-scanning alert 50, `py/jinja2/autoescape-false`. Its only possible site is `dev/audit/harnesses/r10_sav_receipt_render.py:73`, `template = jinja2.Environment().from_string(receipt_message(path))`, which this PR adds. It is the only `jinja2.Environment` in the tree at the head, and `git grep jinja2.Environment origin/main` returns nothing.
- `pr-contract / pr-contract` (job 128227675815, code run 42312136574) started at 00:02:20Z, after every other job had concluded. It refused the body twice: `check \`CodeQL\` is red and \`## Red checks\` does not name it` and the same for `code-scanning alert 50 (py/jinja2/autoescape-false)`. The body's `## Red checks` reads "none: the final head has not run CI".
- The code run's `gate` (job 128227976173) failed on `pr-contract / pr-contract: failure (this run)`. The two edit-run gates only deferred to it (`FAIL run(s) [42312136574] at this head are still being judged; their gate decides`). Details are in `ev/ci_reds.txt`. Carry: dismissed: evidence, not a finding

Step 11 applies: the head's workflows have all concluded, and a `pr-contract` run started after the last red. The body owes an answer to `CodeQL` / alert 50: the cheaper detector and its standing cost, or the finding that none exists. No ruff or bandit is installed on this host (`ev/ruff_s701.txt`, the S701 rule), so I cannot name one as present.

Unblock, the fixer's choice: change the harness's environment so CodeQL no longer flags it, then re-run the render arms. Note that `select_autoescape()` escapes string templates by default, which would turn the note's apostrophe into `&#39;` and break the arms' count. Or keep the harness, dismiss the alert with a reason, and answer it in `## Red checks`. Either way, re-classify.

Every code finding below supports `merge` once the head is GREEN.

## Findings

- Follow-up: the card mutant R9, `const wood = !!(fuel && fuel.show_whatif)` → `!!fuel` (a note on a house where wood is present but not configured), and the body's C3 (`woodNote = false`) both survive `tests/card.mjs` and die only in `tests/card_browser.mjs`. Only CI's `tests / browser` lane runs that script, and it ran green at this head, so this is not a block. Round 3 raised the same point. Carry: R10-HOTFIX-SAV-ESTIMATE | dismissed: covered by the tests browser lane

## Evidence

- Head: `ev/HEAD.txt` holds 8bc540e052a8a4ac048715d4d2e7d0ab9a260c08. The body's `## Head` names it, and `git ls-remote` reads the same at 00:48Z. The merge base is 28482eceeb6b. `git diff 2c147208a00d 8bc540e0` is empty, so the head's code is the handoff `2c147208`.
- Role contract: `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the contract is current. This is round 4, and the body carries the re-cut that `fixer.md` owes (`## Re-cut`).
- Delta since round 3 (`a258212553e1`, three-dot against three-dot): the new `dev/audit/harnesses/r10_sav_receipt_render.py`, its `tests/closures.json` INERT entry, and the `tools/policy/agreement.mjs` `SHARED_GRAMMARS` entry. Production code, tests, docs and goldens are byte-identical to round 3's.
- Merge: `git merge-tree --write-tree origin/main 8bc540e0` exits 0 against origin/main 80016a71f567, with `LEDGER-MERGE: resolved tests/closures.json`. There is no conflict and no `MERGE-CLAIM` line (`ev/merge_tree.txt`).
- Review packet rendered here (`ev/review-packet.md`): refusals none at render. carry_audit at the head: 3 items, 3 routed.
- Finder's harness: `r10_rca_sav_estimate.py census`, the copy at `handoff/r10-rca-sav-estimate` d8eeae8f8e51, sha1 04b644563c84d26378cad42a603dc050e7e5fd88, the same as the body's. I ran it at the base 28482eceeb6b and at the head (`ev/census_base.log`, `ev/census_wt.log`). Both ends print the same six lines and rc 0, so it is flat by design, as the body says:
  - `RESULT census single: booked over horizon mean 1.00 ok`
  - `unvalved 0.92 ok`
  - `valve-at-curve 1.00 ok`
  - `valve-charged 1.00 ok`
  - `wood-warm 1.00 ok`
  - `wood-hot 1.00 ok`
- Companion at both ends: `/opt/hpo/venv-ha/bin/python dev/audit/harnesses/r10_sav_receipt_render.py` (sha1 b97e785bf7c0, equal to the body's).
  - At the head (`ev/render_head.txt`), rc 0: `RESULT wood notes=1 want=1 ok`, `RESULT no-wood notes=0 want=0 ok`, `RESULT no-saving notes=0 want=0 ok`.
  - On the base's blueprint (`ev/render_base.txt`), rc 1: `RESULT wood notes=0 want=1 DEFECT`.
  - Round 3 did not run this render. I have now run it, and it reads the defect at the base and not at the head.
- Class, by my own rule (`ev/class_enum.txt`):
  - A, the value keys `savings_sek|saving_sek|savings_pct|saving_pct|savings_months|monthly_receipt|plan_monthly_savings|saving_includes_wood|wood_note|MonthlySavingsSensor` over custom_components (less www), blueprints, README.md and docs, excluding design and decisions.
  - B, the card's `savings.*|receipt.*|headline.*|health.learn_*` keys.
  - C, the prose `plain thermostat|would have|saved … against|monthly receipt`.
  - Every file A returns is in the body's table. C's extra hits are code comments, the Contract Comparison strings (a contract comparison, not the no-wood reference), and the blueprint input description `notifications.yaml:25-28`, which names the event and states no figure.
  - MonthlySavingsSensor states wood (`saving_includes_wood`), so the round-2 block stays repaired. No seam is undispositioned.
- The body's figures, re-derived at the head with its own commands (`ev/body_rules.txt`): R1 43 lines over 15 files, R2 12, R3 102, R1 on `dea3c729 -- blueprints` 4. All equal the body's.
- Full suites at the head, run in full:
  - `entities.py`: ALL 2639 ENTITY CHECKS PASSED, rc 0.
  - `features.py`: ALL 4877 FEATURE CHECKS PASSED, rc 0.
  - `structure.py`: STRUCTURE RATCHET PASSED, rc 0.
  - `plan_view.py && card.mjs`: ALL CARD CHECKS PASSED, rc 0.
  - `card_browser.mjs`: ALL BROWSER CHECKS PASSED, rc 0.
  - My first card and browser run omitted `plan_view.py`. That was my setup error, and the rerun is the measurement. The `FAIL a8:*` and `a9:*` lines (7) in entities are its own negative self-tests and print in the null run too.
- Golden claims: `env_drift.py --all 28482eceeb6b` at the head, rc 0 (`ev/env_drift.log`): `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE`. `claims-for: 7.1.4` equals VERSION 7.1.4. `claimed_drift.txt` adds only the five `coord_*` claim lines, and each of those moves one key, `saving_includes_wood`. `card_claimed_drift.txt` is unchanged.
- Protected files: `git diff --quiet 28482eceeb6b HEAD -- VERSION manifest.json RELEASE_NOTES.md card_claimed_drift.txt` exits 0.
- Mutants: my own, plus every mutant the body lists. Each ran in its own detached worktree at the head with one exact replacement (runner `ev/mut.py`, logs `ev/mutants/*.txt`). The null control is the head's own full runs above.
  - B1, blueprint note deleted: killed by entities (the blueprint check) and by the render (`wood notes=0 DEFECT`).
  - B2, guard → `saving_sek is not none`: killed by entities and by the render (`no-wood notes=1 DEFECT`).
  - B3, second wording: killed by entities and by the render.
  - B4, guard → `saving_includes_wood` alone: killed by entities and by the render (`no-saving notes=1 DEFECT`).
  - R3, guard negated: killed by entities and by the render.
  - R11, `and` → `or`: killed by entities and by the render.
  - S1 and S2, the sensor attribute → `False` / `True`: killed by entities (`((False, True), …)` and `((True, True), (True, False), (True, False))`).
  - N1 and N2, the notifier → `False` / `True`: killed by entities and by features (1 of 4877, the receipt-event check).
  - D1, the definition → `bool(data.get("wood_fuel"))`: killed by entities and by features.
  - D2, the definition → `.get("ready")`: killed by features only. The entities wood case sets `ready` and `show_whatif` together.
  - L1, the mutation ledger's own RETURN_DEL (`pass`): killed by entities `((None, None), …)` and by features (1 of 4877). The ledger entry is earned.
  - C1, the receipt note → empty: killed by card.mjs.
  - C2, `wood = true`: killed by card.mjs and by card_browser.
  - C3, `woodNote = false`: survives card.mjs, killed by card_browser (`a house with wood configured carries the disclaimer`).
  - R8, receipt `${wood` → `${!wood`: killed by card.mjs.
  - R9, `wood = !!fuel`: survives card.mjs, killed by card_browser (`a house with no wood configured carries none`; see Findings).
  - R10, `receiptHtml` called without `wood`: killed by card.mjs.
  - R12, the sv `savings.wood_note` → the en text: killed by card.mjs (the en/sv check).
- Carry B (`wood-plant`): not re-run this round. The harness's sha1 dfcdcc46269e and its code are unchanged since round 3, which re-derived every figure (mean −1.95 %, min −4.50 at m 1.2; +0.00 % at m 0.8 and 1.0; perturbation +0.00 %).
- Figures I did not re-derive: the scoped gate's `MODE: SCOPED -- 28 script(s) run` (I cite CI's heavy runs and do not re-run the gate), and the agreement lane line, for which I cite CI's `governance / policy-docs`, green at this head.
- Closing self-audit: `carry_audit.py check --comments <this verdict>` exits 0, 2 routed and 0 unrouted (`ev/carry_audit_verdict.txt`). It ran with an empty `--body`, because the PR body was read over MCP and not saved here. The packet's own carry_audit of the body read 3 routed.
- Delivery row `dev/programme/delivery/3244.md` is in the three-dot diff. The one Forward-carry item carries a `Carry:` line (carry_audit 3 routed, 0 unrouted).
