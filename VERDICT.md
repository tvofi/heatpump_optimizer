Fix review: merge 89572df03499ba0f0293e863138c4c94ec2539a5

PR #1834, R9-F1.11, delta review on the round-1 merge verdict at de27770e (earlier commit on this branch).
Head 89572df0 = de27770e + e13193c3 (docs/delivery/1834.md, one row) + 5d2592ba (github-actions[bot] "ci: re-record closures") + merge of main 1aefd2d0.

RESULT e13193c3 vs de27770e: docs/delivery/1834.md only, +1 line, PR #1834's own row
RESULT 5d2592ba: tests/closures.json only. One closure changes: tests/entities.py gains 4 paths and loses none:
  blueprints/automation/charge_ev_from_grid_headroom.yaml
  blueprints/automation/economy_mode_on_price_peak.yaml
  blueprints/automation/notify_on_manual_plan.yaml
  tests/features.py
  These are exactly the 4 out-of-closure reads the fixer reported. Arm B of P6 reads the blueprints; the P2 CENSUS-MISSING check reads features.py. The 3 blueprints are already on closure.py's read-file exception list (tests/closure.py:515-517, as doc_claims.py reads them), so recording them is not an INERT contradiction. Every other change is a per-script "seconds" timing.
RESULT main delta 8a0ca90a..1aefd2d0: 13 files (card JS, card tests, card claims, docs, bus.sh, delivery rows). It shares no file with #1834's diff.
RESULT tree 89572df0 = 27b29ccf = git merge-tree --write-tree 1aefd2d0 5d2592ba (clean)

Nit, not blocking: the comment at tests/entities.py:1856 ("The blueprint FILES are not read") is now false for this script, because arm B reads them. It can ride a later edit.
Round-1 measurements at tree 99ee5a82 stand; no production or test line changed in the delta. CI on 89572df0 was still running when I posted: merge only on green.
