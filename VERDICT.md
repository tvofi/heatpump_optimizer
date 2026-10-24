Fix review: blocked 06cb984bdc0172bdd8eceda1ba55de0e67b4830e body-head-stale: the Head section names c130c242, so pr-contract and gate are red at 06cb984bdc0172bdd8eceda1ba55de0e67b4830e

bus-nonce: bc147a899639c4f40a82cfb4b9c236b1

Round 1 for this reviewer. The verdict is on head 06cb984bdc0172bdd8eceda1ba55de0e67b4830e (the live head of triage/s6-batch14 when posted, ev/head_at_post.txt), against origin/main 646dbaa65ed4 and merge base 87ecf385b1d2.

## Block

- `pr-contract / pr-contract` (job 120962100585) failed at this head. policy_lint says: "`## Head` does not name 06cb984, which is the head this ran on" (ev/job_120962100585.excerpt.txt). `gate` (job 120962222537) is red only because of that: "FAIL pr-contract / pr-contract: failure (this run)" (ev/job_120962222537.excerpt.txt). The body's `## Head` still names `c130c242c8a3883f1a6f400b546d192cee7523fa`. The head is now 06cb984, which adds only this PR's own row, `dev/programme/delivery/2755.md` (ev/body_head_delta.txt). The body's `## Red checks: none` is therefore false at this head (fix-review step 7 and step 11). All of the head's workflows have concluded, and the pr-contract run that refused started at 19:12:30Z, after every other check finished. So this is a settled red, not a race.
- Remedy: change the body only, no code change. Rewrite `## Head` the way #2752's was written, naming 06cb984bdc0172bdd8eceda1ba55de0e67b4830e as the code head (c130c242) plus one commit that holds only this PR's own row. Then re-run pr-contract. A merge verdict carries to that head, because nothing in the tree changes.

## Findings

- The body's `## Head` names c130c242, but the head is 06cb984 (the delivery-row commit). This alone turns pr-contract and gate red. A local `policy_lint.mjs --pr-body` run at the final head would have caught it before handoff. Carry: dismissed: settled by the body edit this block asks for; it is the same check #2752 passed after its row commit, and nothing reaches a later stage.
- The REJECT rests on a run log (RemoteTrigger `get_run_log`, run cse_01SeVeYCKsQwZTCi9e1C7Vv4) that is not committed in the tree. From this seat I could not re-derive its per-event timestamps (17:53:51Z turn end, 18:12:02Z re-init, then 18:17, 18:20, 18:24 and 18:27). Carry: dismissed: the source is named by run id. get_session shows session_01SeVeYCKsQwZTCi9e1C7Vv4 (cloud, origin force_run_trigger) created at 17:49:16Z and updated at 18:43:25Z, about 50 minutes after the cited turn end, which fits the account (ev/run_log_corroboration.txt). The record also leaves #2750 unconfirmed instead of counting it.

## Evidence

- Scope: the diff from the merge base touches exactly `dev/programme/triage/s6-batch14.md` (+14) and `dev/programme/delivery/2755.md` (+1) (ev/diffstat.txt). There is no code, check, claim file, budget, VERSION, manifest or notes heading in it (ev/version.txt). The record is record-only, as the brief requires.
- Merge: `git merge-tree --write-tree origin/main 06cb984bdc0172bdd8eceda1ba55de0e67b4830e` exits 0, tree 7f7b3eee7f7e, with no conflict and no claim-file driver call (ev/merge_tree.txt).
- RESULT ruling_verdict(P83) = REJECT; ruling_verdict(P99) = None (null control re-run); triage_refusal on a cite of #P83 refuses it as "not an ACCEPT ruling (REJECT)" (ev/ruling_verdict.txt).
- RESULT figures: `rg -o '^Verdict: (ACCEPT|DEFER|REJECT)' ... | uniq -c` gives 1 REJECT, which matches the body (ev/figures.txt). preflight's "2750 r" figure check line names an issue number, not a count. It is a check line, not a refusal.
- Sources: P55 (dev/programme/triage/s6-batch4.md) is an ACCEPT, but its Binding rejects an N-minute reclaim because it "can race a live fixer". So "(b) as in P55: an idle reclaim races a live run" is accurately cited (ev/p55.txt). `_prompt` exists in `tools/audit/seat/cloud_dispatch.py` (line 106 at base), with the Monitor setup line at 114 (ev/sources.txt). s6-batch13.md (P82) is not in base 87ecf385b, as the record says. `proposals.md` V18 is out of tree and is named as such, in the same way P55 names its source.
- Carried counts: Instances "0 lost jobs" and "1 duplicate reviewer" come from the orchestrator's run-log read and are not restated from another record. "GitHub calls: 0" is the seat's own and is not re-derivable. No other count appears.
- No host or home paths appear in either added file (ev/hostpaths.txt). The commits carry no Co-Authored-By or session trailer (ev/commits.txt).
- CI at 06cb984bdc0172bdd8eceda1ba55de0e67b4830e (ev/check_runs.json): every check is success or skipped except gate and pr-contract. `mutation` is green, and the diff writes no production line, so it drew no mutant. The mutation proof is n/a for a ruling record, and the consumer check above stands in for it.
- red-history: "3 commit(s) between origin/main and this head, every failure conclusion across them: none".
