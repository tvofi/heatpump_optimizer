# BLOCKED: r11-seam-kernel-step

Question: The brief says "Do your work inline, with no subagents" and "Never work around a hook or a refusal", but the frugal@synced plugin's PreToolUse hook refuses every further inline read in this session ("frugal: inline search op 6 this prompt exceeds budget of 5 ... Delegate the remaining discovery to frugal:scout ... or set FRUGAL_ALLOW_INLINE=1"), on Bash and on Read alike, and the budget is per prompt, so a scheduled one-prompt seat cannot get it back. May this seat delegate its reads to a frugal:scout/extractor subagent, or will the dispatch be re-fired with the guard off for this seat?

State at the stop (no code written):

- Worktree cut from origin/main at bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f; cloud-setup.sh --check OK.
- Baseline harness, from the plan export 819aa2e354b4e5baaf824b8568fd72bea8168a75 (`$EXPORT/dev/audit/rounds/round11/D7/s3/m8_agree.py`, sha1 aaef9a3b34b9c3d8a523eb24410ff97f7ce6b0d1), run at bc658f9ded with `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D7/s3/m8_agree.py --only <family>`:
  - step_covering_now_disagreements=4 (D7-s3-03 reproduces at main: both `_planned_room` copies hold the last step past the plan's end)
  - naive_instant_disagreements=2, finite_number_disagreements=9, water_heat_disagreements=1 (D7-s3-04's 12 reproduces at main)
