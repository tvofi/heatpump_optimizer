Fix review: blocked b986847149298b9d0fa2cf479fa5be221003556d transport-in-code-head: round-1 transport commits 1e55fec4 and 996f63c1 sit under the code head, and gen.py pickup_local still has Mac seats append to the mirror

Round 2 of R9-PROC-5. Code head b9868471, transport head 921ed0fb, merge base 90335cbd.

Fixed since round 1
- In FIX-PLAN-head.md, section 3 is now "No run log". The gen.py brief sentences at lines 346 and 577, the roster log field at line 443, and the data.py:924 record role no longer mention RESUME.md lines.
- The body no longer claims a cmp check.
- standing.md now has the orchestrator copy RESUME-CURRENT.md to handoff/round9/ on handoff/audit-r9-plan, which makes the HANDOVER.md wording true.

Blocking
1. Transport commits are in the code head's ancestry. `git merge-base --is-ancestor 996f63c1 b9868471` is true. The tree at b9868471 contains tools/audit/handoff/r9-proc-5/BODY.md, so the code head that would merge carries a transport file (see ancestry.txt). Fixers may not force-push, so the fix is a new branch, handoff/r9-proc-5-v2, cut from 90335cbd. It needs the code changes of 893022c2 and b9868471 with BODY.md left out, and BODY.md alone in a transport commit above them.
2. One stale instruction is left in the generator. gen.py:445 `pickup_local` still says "a Mac seat appends its milestone lines to the mirror only, and the orchestrator copies them into the /mnt log at its next pass". Running gen.py at b9868471 (rc 0, gen_b9868471.log) writes that sentence into every roster entry's resume.pickup_local. That is the field a seat now reads through jq, and it contradicts standing.md. Fix: say the Mac reads handoff/round9/RESUME-CURRENT.md and appends nothing.

Not blocking, but they belong in the same push
- In the generated FIX-PLAN.md (the FIX-PLAN-head.md lines from 332), "the log from /mnt", "the log from handoff/audit-r9-plan's mirror" and "restarted from the mirror log" should name RESUME-CURRENT.md (see generated_stale_refs.txt).
- FIX-PLAN-head.md:11 cites the archived RESUME.md section names. That is history and can stay.

How I checked
- build.sh is archived and hard-codes another seat's scratch directory, so I ran its first step, `python3 gen.py <out>`, at b9868471 into scratch. It exited with rc 0. I grepped the output for leftover RESUME or log wording.
- I did not run brief_lint against main, and I did not re-run the gate.
