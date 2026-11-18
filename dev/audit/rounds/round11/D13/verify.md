# D13 verify, round 11

Tree: the worktree audit-r11-verify-D13 at handoff/audit-r11-register 28b864af6d. D13-s2 is not a planted scope. load1 171-173, thread_factor 1.00. These are count harnesses with no timing.

## D13-s2-01: verify (medium)
- V1: block_classes.mjs --no-window-read gives blocked_verdicts=448, untaught_blocked=214, untaught_share=0.478 and untaught_words=93. These are exact. With `--perturb reshape-one`, blocked drops to 447 and outside_grammar rises to 1, the stated direction. With `--perturb teach-ci-red`, untaught drops to 151 (0.337), a fall of exactly 63. Null control: unperturbed outside_grammar=0. Leave-one-out without ci-red, the largest word: 0.392, so the aggregate still holds.
- V2: my own Python parser (scratch v2.py) reads window.json comments and reviews. It extracts VERDICT_CLASSES from the literal (17 words), and a verdict counts as blocked when its first line matches `Fix review: blocked <sha40> [word:]`. Result: 448 blocked, 214 untaught, 0.478, 93 words, 155 PRs. This agrees with V1.
- V3: the instance is in process tooling (the merge and record path), not in Home Assistant runtime. The defect is real for statsHistogram, the bus and the wave. Class N-vocabulary-drift exists in bugclasses.json and is confirmed. The seam_rule greps only bus.sh and web-fix-wave.js. It shows the demonstrated seams but does not enumerate all of them, because it misses prose vocabularies (fixer.md, fix-review.md).

## D13-s2-02: verify (medium)
- V1: friction_keys.mjs gives accepted=174, no_file=105 and no_file_ids=84 (0.603). These are exact. With `--perturb readme`, one_file goes from 69 to 68 and ambiguous from 0 to 1, as stated. `bare` and `unticked` are invariance perturbations and hold. No perturbation moves no_file itself, which is a gap in the method, but not a void.
- V2: my own parser (a `## Friction` section and a bullet with a leading id; an id names a file when its basename matches a .md under dev/governance or .claude, or a skill directory) accepts 153 entries. Of those, 93 name no file (0.608, 73 ids). The definitions differ in which entries count as accepted, but the share agrees within 0.005.
- V3: the instance is in process tooling only. Class N-vocabulary-drift is confirmed. The seam_rule only re-prints this harness's rows. It does not enumerate other readers of the friction key.
