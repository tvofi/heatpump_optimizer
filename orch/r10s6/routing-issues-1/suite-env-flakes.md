R10-FLY-SUITE-ENV-FLAKES was set done after #2659, which fixed only the harness CPU-headroom flake; tests/features.py still fails four checks under HASTUB_TZ=Europe/Stockholm at base and head alike, and coverage_tree.sh's per-script data check races a script's descendants. The group's carries hold both findings with their evidence; it is reopened to carries-open to fix them.

Roster group: `R10-FLY-SUITE-ENV-FLAKES`. Part of #201.
