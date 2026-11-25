# RESUME: R11-OWNER-FAULT-HOLD repair (PR #3872, review round 1 answered)

- Code: handoff/r11-owner-fault-hold at 8d8b30aabf42b183ea006b832026928c235fc478 (fdcf373670 plus the config_flow re-record and claim answering fast at d6a54399). It carries ce9619a4f4 (the four verdict sites' checks and mutants) and the merge of origin/main af4d89f763 (2b1f96e77b, resolved against #3812), plus the follow-ups listed under ## Head.
- Measured at fdcf373670: harness mutants=38 survived=0; mutant_run.py spec on the four verdict/3872 sites: all KILLED (NULL SURVIVED); full tests/features.py ALL 6173 PASSED; fault-hold block 59 PASSED; scoped prepr rc=0.
- origin/main 0f63320c96 merges cleanly with this head (git merge-tree exit 0); not re-merged.
- Next: update_pr.sh onto fix/r11-owner-fault-hold, then a delta reviewer: git diff d6a54399a63b HEAD.
