# D5-v3 verifier report (round 11)

Trees: D5-s4 and D5-s5 findings measured in px export copy; line/path greps also in px. Load1 0.4-0.9, thread_factor 1.000 throughout.

## D5-s4-01 - verify (severity low)
- metric: D5 comment units with >=1 sentence over 40 words, s4 cells (planted px tree)
- reproduced: 558 units / 716 sentences / 45 files; independent: 557 units, 707 sentences, 44 of 51 files (own splitter)
- method: finder comments.py in px: units=3367 long_units=558, 716 sentences, 45/51 files; perturbation pump_mode.py long_units 3->2 (header's target is line-wrapped in the header; real text is one line, used that); own regex splitter over py comment blocks/docstrings and JS comments
- attacks: null/perturbation moved 3->2; grid check: files 45/51 reproduced; header claim 'longest 156 words' does not reproduce (finder's own json max=217, mine 217); no timing claim
- class: new; reach: not applicable: comment/tooling text, no runtime path in Home Assistant; stub divergence irrelevant
- seam_rule: enumerates all units of the seat cells for its check (whole-cell scan), not only the demonstrated one

## D5-s4-02 - weaken (severity low)
- metric: comment units citing a name no code token defines, sysid.py (px tree)
- reproduced: 2 units (1 after perturbation); independent: grep: prior_w, data_w, T_prev occur only in the 2 comment lines; code uses prior_rel = s_noise / prior_sd; 1 of 2 is a real stale name
- method: finder harness: unresolved_units 2 -> 1 under the stated perturbation (px, tokens 3->1); grep of T_prev/prior_w/data_w across tree
- attacks: prior_w / data_w is a genuinely stale name (line 2073 in px; claim says 2071); T_prev is mathematical notation for the previous sample in the D2-01 derivation, not a claimed identifier, so that half is weak; lines are 1984/2073 not 1983/2071
- class: new; reach: not applicable: comment/tooling text, no runtime path in Home Assistant; stub divergence irrelevant
- seam_rule: enumerates all units of the seat cells for its check (whole-cell scan), not only the demonstrated one

## D5-s4-03 - verify (severity low)
- metric: card units whose text_ledger line differs from the unit's true line
- reproduced: 737/892, max 11; independent: same harness only; patched 1
- method: ledger_lines.py in px: misplaced 737 of 892, max_offset 11; --patched (one-line fix counting the newline) -> 1, max 1
- attacks: perturbation moves 737 -> 1 as stated; tool-only (instrument) defect; load1 0.46 thread_factor 1.000
- class: I5; reach: not applicable: comment/tooling text, no runtime path in Home Assistant; stub divergence irrelevant
- seam_rule: enumerates all units of the seat cells for its check (whole-cell scan), not only the demonstrated one

## D5-s5-01 - verify (severity low)
- metric: D5 units in prepr.sh naming a path/branch the tree lacks
- reproduced: 3 -> 2 on one fix; independent: grep/ls: 3 of 3 stale references confirmed
- method: m4_ledger --file prepr.sh base 3; fixing usage line -> 2; grep confirms tools/audit/prepr.sh absent, attr-only vs attronly (line 2604/2610), tools/audit/briefs/fixer.md absent
- attacks: line 29 says CI may restore a base copy at tools/audit/prepr.sh, so the usage line is partly defensible; attr-only and briefs/fixer.md are plainly stale
- class: I5; reach: not applicable: comment/tooling text, no runtime path in Home Assistant; stub divergence irrelevant
- seam_rule: enumerates all units of the seat cells for its check (whole-cell scan), not only the demonstrated one

## D5-s5-02 - verify (severity low)
- metric: gh_comment.in_shared_root docstring naming absent tools/audit/prepr.sh
- reproduced: 1 -> 0; independent: grep confirms
- method: --edit to tools/pr/prepr.sh: false 1 -> 0
- attacks: ls tools/audit/prepr.sh absent; shared_root() at tools/pr/prepr.sh:1523
- class: I5; reach: not applicable: comment/tooling text, no runtime path in Home Assistant; stub divergence irrelevant
- seam_rule: enumerates all units of the seat cells for its check (whole-cell scan), not only the demonstrated one

## D5-s5-03 - verify (severity low)
- metric: preflight.sh unit naming moved fix-review.md path
- reproduced: 1 -> 0; independent: grep lines 145,191
- method: --edit of line 191 to dev/governance/roles/fix-review.md: 1 -> 0
- attacks: line 145 mention is historical narrative (path at the time) and fine; line 191 prescribes the second home and is stale; tools/audit/briefs absent
- class: I5; reach: not applicable: comment/tooling text, no runtime path in Home Assistant; stub divergence irrelevant
- seam_rule: enumerates all units of the seat cells for its check (whole-cell scan), not only the demonstrated one

## D5-s5-04 - verify (severity low)
- metric: open_pr.sh usage line naming nonexistent openpr.sh
- reproduced: 1 -> 0; independent: find: 0 files
- method: --edit openpr.sh -> open_pr.sh: 1 -> 0
- attacks: find . -name openpr.sh: none
- class: I5; reach: not applicable: comment/tooling text, no runtime path in Home Assistant; stub divergence irrelevant
- seam_rule: enumerates all units of the seat cells for its check (whole-cell scan), not only the demonstrated one

## D5-s5-05 - verify (severity low)
- metric: merge_train comment naming _outside_self_test
- reproduced: 1 -> 0; independent: grep tools: 1 hit, the comment
- method: --edit to _outside_gate: 1 -> 0
- attacks: grep: _outside_self_test only in the comment (line 5063); code restores inline at 5275/6305 via globals()['_outside_gate'] and real_fork_head
- class: I5; reach: not applicable: comment/tooling text, no runtime path in Home Assistant; stub divergence irrelevant
- seam_rule: enumerates all units of the seat cells for its check (whole-cell scan), not only the demonstrated one

## D5-s5-06 - weaken (severity low)
- metric: orchestrator_tick HEARTBEAT_SECONDS comment vs merge_train.HEARTBEAT_SECONDS
- reproduced: 1 -> 0; independent: grep: 480 at orchestrator_tick:209, 240 at merge_train:1048; check at tick:2750 uses train log mtime
- method: --set orchestrator_tick.HEARTBEAT_SECONDS=240: false 1 -> 0; base 1
- attacks: constants differ (480 vs 240, confirmed by grep), but the comment says the 'watcher heartbeat the tick assumes' and the threshold is a deliberate 2x of an assumed value, so it may be an assumption, not a misstatement; the stale threshold is 960 s = 4 train beats
- class: I5; reach: not applicable: comment/tooling text, no runtime path in Home Assistant; stub divergence irrelevant
- seam_rule: enumerates all units of the seat cells for its check (whole-cell scan), not only the demonstrated one

## D5-s5-07 - verify (severity low)
- metric: strict (prose paragraphs only) comment sentences over 40 words, s5 cells
- reproduced: 483 / 60 files; independent: 660 / 67 files (looser definition)
- method: m4_ledger base: raw 743, strict 483 in 60 of 74 files
- attacks: own splitter, all comment paragraphs/docstring paragraphs with no exclusion: 660 sentences in 67 of 74 files, bracketing the finder's strict count; definitions differ (mine includes usage/list lines)
- class: new; reach: not applicable: comment/tooling text, no runtime path in Home Assistant; stub divergence irrelevant
- seam_rule: enumerates all units of the seat cells for its check (whole-cell scan), not only the demonstrated one

