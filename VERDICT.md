Fix review: merge 2fcf5b738bf4818405aeb0f3572f3083c96010d2
bus-nonce: 7cda6a2ac8c350f5c562e67340fc75a8

Round 1 (full review; no prior reviewed head). Tests-only diff: no file under custom_components/, VERSION, manifest, notes heading, golden or claim file is touched. `git merge-tree --write-tree origin/main <head>` exits 0.

RESULT mutation-proof: `bash dev/audit/rounds/round11/D3/pins-plant/run.sh` re-run at the head in a detached worktree: every spec's NULL SURVIVED; KILLED 47 of 47 (45 keys plus the two same-line siblings); no survivor. Log: evidence/run_sh.log.
RESULT finder-harness: the packet names none; I ran the judges' committed probes from a826f55f8c at the head for 43b54266f12bfb21 (moved_inputs=3, null_moved=0, pinned baseline 5.25 matches) and 3b9eddc7ba9a7488 (baseline 0.908072 after 12 matches the pin's 0.908; mutant 0.856486). A third (39041ccf21eedba6) needs the box's out-of-tree `valvecommon` helper and was not run. Log: evidence/finder_probes.log.
RESULT class: D3-FOLD.json at e8aefbb452, group R11-D3-PINS-plant, holds 46 keys; the diff pins 45; the 46th, dd40fdb4edae4d79, has 0 occurrences of its patched line at the head (thermal_model.py now computes the target with a conditional expression), so the non-finding stands.
RESULT code-scanning alert the body names: the diff does not touch its file.

Note: root-cause-unrecorded: `gate` (owed set) is red in run 45957663868 (the edit-kind CI run), which exited 1 with "FAIL run(s) [45957665192] at this head are still being judged; their gate decides". The gate of that deciding code-kind run (job 140411367182) is green at this head. The body's `## Red checks` does not name it. Carry: dismissed: this is a by-design deferral to the code run, not a defect in this diff; the deciding gate is green
Note: figure: the body's `tests / closures` / `nightly-status` answers stand; `nightly-status` is outside the owed set. Carry: dismissed: evidence, not a finding
