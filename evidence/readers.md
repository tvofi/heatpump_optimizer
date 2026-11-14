Check-run / rollup readers, merge_train.py at dbe75142ac7c, its imports and callers (scout enumeration, spot-read by reviewer for 2057, 3055, record_row 857):
- merge_train cross_check ROLLUP_Q -> rollup_walk: cursor paging (this diff)
- merge_train _check_runs 2103, ancestry 3621: gh_read.read_pages (fails whole, never partial)
- merge_train _selftest_runs 2059: per_page=100 single, filtered by check_name
- merge_train policy_refusal 3056: gh pr view --json statusCheckRollup, single (post-refusal diagnosis only)
- record_row.py:857: per_page=100 single (missing required -> pending, fail closed)
- callers with --paginate: proof_watch.py:220, orchestrator_tick.py:380, bus.sh:534, ci-watch.sh:321, prepr.sh:1421, replan.py:3201
- callers single page: review_packet.py:245,267; failure_logs.sh:125; merge_pr.sh:282-283; prepr.sh:1432
