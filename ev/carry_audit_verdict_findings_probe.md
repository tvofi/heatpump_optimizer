## Head

x

## Forward-carry

- Surviving mutant: replacing `--max-age) max=${2:-}; shift 2 || shift ;;` with `--max-age) shift 2 || shift ;;` (the option is parsed but ignored, so the age limit is always 1200) leaves `heartbeat.sh --self-test` at 7 checks, 0 failed. Its two watcher fixtures (fresh at --max-age 600, 1800 s stale at --max-age 1200) give the same result under the default. My hand null control shows the arm works at this head (900 s old: STALE under --max-age 600, FRESH under 1200), and the owner's watcher uses the default. So this is a test gap, not a defect: the self-test should add one fixture whose verdict flips with --max-age (for example 900 s old under 600). Evidence: ev/own_mutants.txt R4, ev/null_controls_watch.txt. Carry: R10-ORCH-MACHINERY
- The roster carry "Revision 12" on R10-FLOW-ANDON (origin/handoff/audit-r10-roster 743463c61, added in 735981f4e at 2026-10-21T20:42Z) asks for three more alarms: a handoff tip ahead of its PR head for over 20 minutes, a lock whose owner pid is dead, and a seat self-test process older than 1 h. This PR does none of them and its body does not mention them. The heartbeat this PR lands is the group's K8 brief and is complete on its own, so the gap does not block this merge, but the alarms are still owed after it. Carry: R10-FLOW-ANDON
- Self-test hygiene item (a) in the same roster carry says a new mutant "sits inside the block of the instrument it tests, never appended at the file's end". tick_loop-1 and tick_loop-2 come after S35..S38 at the end of MUTANTS, not next to tick_loop's S31..S34. The ids follow the per-file convention and the merge with #2529 resolved cleanly. Whoever next adds mutants to that file should move them. Carry: R10-ORCH-MACHINERY

