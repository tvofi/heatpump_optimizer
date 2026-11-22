# R11-SEAM-store: blocked at the handoff on the group's live carries

Question: the live roster (handoff/audit-r11-roster) gives R11-SEAM-store two carries that the dispatch PROMPT (a6b6a9b4fd) predates: carry 0, the late P1 sweep's six loaders that read a stored boolean as a number (dhw_draws.py, tariff.py, off_restore.py, two coordinator.py loaders, legionella.py); and carry 1, the late P2 sweep's three readers of the DHW weekday/weekend windows (boost.py, the coordinator's circulation pump, dhw_learning.py). With them the group is 7 items, past fixer.md's cap of five findings. Should they be dispatched as a second part (a `Part 2 of 2: build carries 0-1` line), or should this part build them before its handoff?

State, so a resume loses nothing:
- The five findings are built and verified at handoff/r11-seam-store = ea5c36ab348672cb9f93438075e40b43cd769292 (merge base 1207ee13b0; `git merge-tree --write-tree origin/main HEAD` reports no conflict at 49cb3207a9). Production diff: 4 files, +80/-49.
- `PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh` on the body is clean at that head (rc=0). The scoped gate passed at b54a76e0e6, and the later delta's scoped scripts passed at the head.
- `tools/audit/seat/body_push.sh r11-seam-store` refused only on `review_packet: REFUSE brief-carries: carry 0 / carry 1 is not named in the body`. The body it refused is kept at handoff-wip/r11-seam-store-body 194bb6de89.
- With a part line naming carries 0-1 for a later part, this head's body needs no change, and body_push.sh can be re-run on it as is.
