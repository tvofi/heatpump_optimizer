# D5#1 verify report (verifier, round 11), seat D5-s10, seven findings

All numbers below were taken in the planted export copy `/home/user/audit-r11-px-D5-1` (plain directory, no .git), `PYTHONPATH=tests/hastub`, `--repo /home/user/heatpump_optimizer --ref 92d38ecb`, python3, load1 0.66-0.77, thread_factor 1.000. Side note only: an earlier run in the branch worktree gave the same numbers except m4_ledger (units 1800, long_sentences 347, 193 files), which carries branch-only units.

## D5-s10-01 pre-edit.sh names .claude/rules/ as the source of .cursor/rules
- Claim: the hook's comment (line 14) and refusal (line 94) send a seat to `.claude/rules/`, itself generated; the real source is `dev/governance/rules`.
- V1 (export): edit_reaches_cursor=0, unguarded_generated=1, named_source=.claude/rules/. Perturbation (message rewritten to dev/governance/rules/): edit_reaches_cursor 0 -> 1, correct direction. Null control: null_prod_rc=0 (non-generated path passes), regenerate_rc=0.
- V2: own read of `rules_sync.mjs` lines 29-31: SRC=dev/governance/rules, CLAUDE_OUT=.claude/rules, CURSOR_OUT=.cursor/rules; hook text at lines 14 and 94 names `.claude/rules/`. Metric: does the named directory equal rules_sync's SRC (no = 1 mismatch). Agrees.
- V3: repo tooling text, not Home Assistant. Severity low (a seat's edit is discarded; CI catches via --check). Seam rule covers the hook's one message and the two generated dirs, so it enumerates its seam. Class: I5 (stale reference); N-move-stale-path is defensible.
- Vote: verify.

## D5-s10-02 stop-selfcheck.sh prefix list misses AGENTS.md and dev/audit/README.md
- V1 (export): policy_files=65, escaped=2, e2e AGENTS.md rc 0. Null controls: CLAUDE.md rc 2, a production path rc 0. Perturbation (add AGENTS.md and dev/audit/ to the prefixes): escaped 2 -> 0, AGENTS.md rc 2.
- V2: own read of line 28: the prefix regex has no AGENTS or dev/audit alternative, and both files exist in the export. The header's own comment says a too-narrow prefix is the failure that matters. Agrees.
- V3: dev tooling. Severity low (a lint skipped on a turn; CI still lints). Seam rule lists each escaped path, so it enumerates the seam. Class I4 (two definitions of one set disagree).
- Vote: verify.

## D5-s10-03 session-start.sh header miscounts its report; "HANDOVER trap 11" absent
- V1 (export): behind_pos=4, tip_pos=5 (header says 5 and 6), other_items=4 (header says 3), mismatches=3, handover_trap_11_found=0. Null: the traps section exists. Perturbation (one printf inserted before `behind main:`): mismatches 3 -> 1.
- V2: own grep of HANDOVER.md: heading "Traps that cost a session" at line 1190, zero matches for "trap 11". Agrees.
- V3: dev tooling comment, severity low. Seam rule: single script. Class I5.
- Vote: verify.

## D5-s10-04, -05, -06 docstrings citing absent paths
- Claim: `k1725_blas_kernel_gap.py` and `thermal_parity.py` cite tools/audit/README.md; `cop_duty_floor.py` cites dev/programme/carries/carry-2065.json; neither exists.
- V1 (export): the three files alone give units=31, failing units=3, unresolved_paths=4. Whole cell: unresolved_paths=26, verdict_false=24. Perturbation (`--rewrite tools/audit/README.md=dev/audit/README.md`): unresolved_paths 26 -> 24, verdict_false 24 -> 22, i.e. down, as stated. Null: 28 of the 31 units resolve.
- V2: `ls` of both paths in the export reports them absent, and `dev/audit/README.md` exists.
- V3: harness docstrings, severity low. The seam rule is the C2 resolvability check over every unit, which enumerates the phenomenon (26 unresolved in the cell, 3 reported here). Class I5.
- Vote: verify, each of the three.

## D5-s10-07 339 sentences over 40 words across 193 files (C5)
- V1 (export): long_sentences=339, files_with_long_sentence=193, units=1794, exact.
- V2: own counter (`/home/user/vout/D5-v1/own.py`, comment paragraphs of `.claude/hooks/*.sh` and `.claude/workflows/*.js`): 45 sentences over 40 words in 11 files, including a few embedded-code false positives. pre-edit.sh examples of 41 to 53 words confirmed. The count depends on the sentence splitter.
- Attack: the 40-word ceiling is the owner's criterion C5 (D5-criteria.md line 31). The finding is a style count with no behavioural consequence, and it is a population of 339, not one defect.
- V3: dev tooling, severity info/low. Class new (cosmetic).
- Vote: weaken, severity info/low.
