        tloop["tick_loop.sh"]
        relay["cloud_relay.sh pass<br/>probe arm, handoff arm"]
        busx["bus.sh"]
        tick["orchestrator_tick.py<br/>the board; it does not act"]
        jobs["beat_jobs.py<br/>the jobs of the beat's table"]
        plan["replan.py<br/>the plan model"]
        docs["state_docs.py"]
        page["plan_page.py"]
        rq["roster_queue.py"]
        redit["roster_edit.py"]
        opr["open_pr.sh"]
| merge_train.py | runs | postmerge.py | `tools/audit/seat/merge_train.py`: `tool("postmerge"), str(pr), "--repo"` |
| postmerge.py | runs | roster_sync.py | `tools/audit/seat/postmerge.py`: `/roster_sync.py", "--repo", repo, "--apply"` |
| postmerge.py | runs | state_docs.py | `tools/audit/seat/postmerge.py`: `/state_docs.py", "--repo", repo, "--push"` |
| postmerge.py | writes | obligations ledger | `tools/audit/seat/postmerge.py`: `"open", "postmerge-owed"` |
| roster_sync.py | runs | roster_edit.py | `tools/audit/seat/roster_sync.py`: `roster_edit.write_roster(` |
