Fix review: blocked 893022c25756de27a60f10d26342b41d6bd939e4 incomplete-propagation: standing.md stops RESUME.md appends, but FIX-PLAN-head.md and gen.py still order them; the body claims a cmp that was not run

Reviewed: code head 893022c2 (merge base 90335cbd), transport 996f63c1 (BODY.md only), roster R9-PROC-5 at 0b442c06.

Blocking
1. Incomplete propagation. build.sh regenerates the plan from data.py, standing.md and FIX-PLAN-head.md. At the head, FIX-PLAN-head.md lines 317-322 ("3. The run log") still tell every seat to append to the /mnt RESUME.md and its mirror. gen.py:346 and gen.py:577 still put "RESUME.md line(s)" in each brief's routing sentence, gen.py:443 writes every roster `resume.log` as "RESUME.md ... append-only", and data.py:924 lists "RESUME.md lines". The next rebuild therefore emits FIX-PLAN.md with two contradicting instructions, and every roster entry a seat reads through jq still points at the append-only log. Fix: change all five in-tree sources in this PR (see stale_resume_refs.txt).
2. False claim in BODY.md. The "Null control" section says the archive is byte-identical to the old log by cmp against the pre-split copy. The fixer's own handoff says cmp was not run. There is no pre-split copy, and the archive's mtime (16:57:47.529) is later than the pointer that overwrote RESUME.md (16:57:47.496), so I could not verify it either. The archive ends at the 14:50:04Z F1.10 line. Fix: say it was not verified, or name the source the archive came from.
3. HANDOVER.md now says handoff/audit-r9-plan holds RESUME-CURRENT.md and RESUME-ARCHIVE.md. That is false: the mirror there is unsplit and was last touched at 07:46Z. standing.md also has the orchestrator regenerate only the /mnt file, and the Mac cannot read /mnt. Fix: either standing.md has the orchestrator regenerate the plan-branch RESUME-CURRENT.md too, which is the only file the Mac can resume from, or HANDOVER.md must not name files that do not exist.

Not blocking
- RESUME-CURRENT.md says "updated: 2026-10-01T17:10Z", which is later than its own mtime of 16:57Z. Its size is 2664 B, under the 10 KB budget. Its in-flight list is already stale: #1815 is done on the roster at ea77625d.
- The jq rule and the --carry routing text are sound. `app_approve.sh --carry` exists at tools/audit/app_approve.sh:372.
- Commits are authored as tvofi with the noreply address. The plain git push is acceptable only if the Mac opens the PR as hpo-author.

Not run: the gate and CI. The PR is not open yet, so there is no head CI to cite. The diff is prose-only.
