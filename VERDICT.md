Fix review: merge c5795f202c761b4fb2367bcb723985137e52dddd
bus-nonce: e8de1474aa9249e7b96eee26160efa54

Records/evidence landing of finder box D3-rem (handoff/audit-r11-find-D3-rem at 6ff1235867ed), reviewed at c5795f202c761b4fb2367bcb723985137e52dddd with the live check state green (merge_train classify GREEN).

- Faithful landing: every one of the box's 321 files is accounted for. 34 land byte-identical; 212 are byte-identical in #3814 or #3810; 45 differ from #3814 only because they are inherited byte-for-byte from box D3-top6 (fdd9e2d827a9), whose repaired copies #3814 lands, and REPORT-D3-top6.json differs from #3814's only in the report_path #3814 corrects; 28 are modified exactly as the body states: the 15 probe_*.py inline repo_root in place of parents[6], the suffixed report_path and writes, the home-path scrub to ~, and nine gate logs trimmed to their first 100 lines, a marker and their last 200, each kept line identical to the box's. Only the two CHECK.txt files are dropped. Evidence: box-accounting and log-trim files.
- No host paths: ref_privacy.py guard over the PR's commits and body-lines over the added lines both exit 0; the remaining paths are cloud-sandbox paths or the /Users/<owner-home> placeholder.
- No opinions: none found in the reports, findings or body.
- No budget raise: no *_budgets.json, VERSION, manifest, claim file or release notes touched; budget-raise-gate is green.
- c5795f202c is the closures-autofix bot's re-record of 18 inert_reads entries for this PR's new scripts; the body's Red checks names that red and its cheaper detector, and pr-contract is green.
