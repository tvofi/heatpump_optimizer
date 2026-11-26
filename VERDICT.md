Fix review: blocked bff0cd0fc16fe2eaedbfa1d351776c8838ada6c3 class-open: dev/audit/rounds/round4/D9/h9_batch_cost_loop.py:72 RESULT batch_rows_per_gradient=97 carries a "96 until R9 F2.2" chain the body's own rule returns, neither in the diff nor dispositioned

bus-nonce: 751dd133751457bb13653be7d82bc840

## Round

First review of this head (review scope: full, per the packet). Fix-review.md step 6, open-axis rule 9.

## Block

- The body names its enumeration rule, `git grep -cE "[0-9]+ until "` outside run logs and records, and says it returns seven files. Run at this head (ev/head_until_grep.txt; only `dev/audit/rounds/round11/D3/s1/state` and `dev/programme/` excluded), it returns 21 paths. One of them is a member of the class this diff closes: `dev/audit/rounds/round4/D9/h9_batch_cost_loop.py:72`, `RESULT batch_rows_per_gradient=97     (96 until R9 F2.2 put the point itself at the head of each gradient's batch)`. That is a live-header RESULT pin in `tests/harness_headers.py`'s executed set with an "N until X" history chain. It has exactly the shape of the two h7_memory_gate.py chains this diff deletes. It is not in the diff and not dispositioned in the body.
- The other undispositioned paths the rule returns are `tests/entities.py:21507` ("`contexts` stays the 17 until P2b's cut-over", a hand-kept count in a comment), `dev/audit/rounds/round9/D14/s2/i4_roster.py:27` ("stays 1 until", the same shape as naming_splits.py, which the body dispositions as finder evidence), and these prose "until"s: `.github/workflows/tests.yml:207`, `custom_components/heatpump_optimizer/coordinator.py:10387`, `dev/audit/rca/RCA-BULK-2.md:86`, `dev/audit/rounds/round11/D13/s1/window_fetch.mjs:4`, `dev/audit/rounds/round11/D13/s2/window.json`, `dev/audit/rounds/round11/D3/s1/PROGRESS-local*.log`, `dev/audit/rounds/round11/D5/s5/long_sentences.tsv`, `dev/audit/rounds/round4/D4/verify-0-1.md`, `dev/audit/rounds/round8/D3/verify-v1.md`, `dev/audit/rounds/round8/JUDGE-INPUT.json`, `tests/card_browser.mjs:2011` and `tests/features.py:97321`. The body's census must state the rule's real output, and give each path a disposition or a stated residue category, such as "a prose until, not a count history".
- In the same re-cut: the #1218 refusal regex in `tests/entities.py` (`_D308_CARRIED`) does not refuse the wording the block's own `derived (#1218):` line prints. If "the lane reaches all 124 production files" is written back, it is not matched. Neither are "190 script pairs" or a spelled-out "Eighteen of the pairs" (ev/mut_M7_regex.txt). The body says the block "refuses a count written back into the note", and that holds only for the old phrasings.

## Findings

- Follow-up: the claims.py header still pins `config_defaults_compared=97` and `config_ranges_compared=104`, and C29, C30, C31 and C37 state "25 option pages", "97 rows", "104 rows" and "15 services". These are hand-kept counts that option- and service-adding pull requests move. The deleted chains show 93 -> 97 and 101 -> 104 over R10 alone. The body keeps them by name ("the unchanged claim and config-row totals"), outside the module, pair and option-field counts card FG-1 scopes. Carry: dismissed: kept by name in the body and outside card FG-1's stated module, pair and option-field scope; the flow-green study's owner can widen the card

## Evidence

- Head reviewed: bff0cd0fc16fe2eaedbfa1d351776c8838ada6c3 (ev/HEAD.txt). It is the body's head. `git merge-tree --write-tree origin/main <head>` exits 0 with no conflict (ev/merge_tree.txt). There is no role-contract drift between the merge base and main.
- No production code is in the diff. VERSION, the manifest and the RELEASE_NOTES heading are untouched (diff stat). `env_drift.py --all 1d30777` prints NO UNCLAIMED DRIFT and NO STALE FIXTURE (ev/head_env_drift.txt).
- Head runs: doc_claims.py ALL 445 checks PASSED. deployment_shape.py ALL PASSED. claims.py prints claims_false=0, arch_map_missing=0, arch_map_phantom=0, ha_importers_unnamed=0 and leaves claims.md and claims.json byte-identical. option_doc_coverage.py prints option_pages_unrendered=0. structure.py PASSED. comment_ratchet.py OK (2295 = 2295). md_tables.mjs prints 0 orphaned and 0 misrendered. closure.py select prints MODE: SCOPED -- 7 script(s) run. entities.py was not run here; it is CI's run, cited.
- Mutants, each restored (ev/mut_*.txt):
  - M1, claims.py `if _hit:` -> `if False:`: claims_false=2 (C32, C35). Killed.
  - M2, option_doc_coverage.py `pages_ok += 0`: option_pages_unrendered=25 against the header's 0. Killed by harness_headers.py.
  - M3, doc_claims.py `_ABSENT_QUANTITIES = frozenset()`: 2 of 445 FAILED, the FG-1 refusal and its planted null control. Killed.
  - M4, architecture.md back to "105 modules, of which 36": doc_claims.py 1 FAILED, naming architecture.md:8; claims.py C32 false. Killed.
  - M5, a duplicate `__init__` in the boundary list: C34 false. Killed.
  - M6, a phantom `nosuch_module`: C34 and C35 false. Killed.
  - M8, opening rewritten to "most modules import": doc_claims.py passes. claims.py C32 is false, and entities.py's opening-share check needs the "fewer than half" sentence. Killed.
- CI: `merge_train.py classify` read WAIT ("pending: gate red: none") on every poll (ev/classify.log). The digest's `gate` failure and `tests / nightly-status` failure are as rendered. nightly-status is not in the owed-reds set. This verdict blocks on code, not on CI.
- Figures re-derived at the head: arch_modules_on_disk=105, ha_module_level_importers=36, option_fields_rendered=220 (printed, unpinned), and closure-select's 7 scripts. "The rule returns seven files" does not re-derive: it returns 21 paths (Block).
