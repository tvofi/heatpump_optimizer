Fix review: merge 40361071e1141c6bb63118daf6a90cda1588dced
bus-nonce: 2591291f991a37cd3e8d6253942a0d04

Records/evidence landing of finder box D3-u1b (handoff/audit-r11-find-D3-u1b at f0e90c2f4632), reviewed at 40361071e1141c6bb63118daf6a90cda1588dced with the live check state green (merge_train classify GREEN).

- Faithful landing: every one of the box's 683 files is accounted for. 558 land byte-identical (at their path or the -D3-u1b suffixed path); 119 are byte-identical in #3810 or #3814; finalize.py is byte-identical across boxes D3-top6, D3-m5, D3-rem and D3-u1b, and #3810 lands its repo_root-fixed copy; the 3 modified files (REPORT-D3-u1b.json, reports-D3-u1b.json, build_report_u1b.py) change only the report path and write targets to the suffixed names. Only CHECK.txt and one __pycache__ .pyc are dropped. Evidence: box-accounting file.
- No host paths: ref_privacy.py guard over the PR's commits and body-lines over the added lines both exit 0; the remaining paths are cloud-sandbox paths.
- No opinions: none found in the report or body.
- No budget raise: no *_budgets.json, VERSION, manifest, claim file or release notes touched; budget-raise-gate is green.
- 40361071e1 is the closures-autofix bot's re-record of 3 inert_reads entries for this PR's new scripts; the body's Red checks names that red and its cheaper detector, and pr-contract is green.
