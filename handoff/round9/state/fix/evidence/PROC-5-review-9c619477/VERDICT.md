Fix review: merge 9c619477699fded70a91e518201122a1213748b1

Round 4 of R9-PROC-5, on handoff/r9-proc-5-v3. Code head 9c619477, whose only parent is 90335cbd. Transport head c611312a.

Checked
- Ancestry. 9c619477 is a single commit on 90335cbd. Its tree has no tools/audit/handoff/r9-proc-5. The only file changed from 9c619477 to c611312a is BODY.md.
- Content. Outside tools/audit/handoff, 9c619477's tree is byte-identical to 54ffa311 (`git diff --quiet`). That is the round-3 content I already verified: gen.py exits 0, its roster output has no "appends its milestone" or "mirror log" text, and brief_lint gives 0 errors with output identical to the base.
- Every blocking finding from rounds 1-3 is resolved:
  - The generator sources match standing.md.
  - The body makes no unverified cmp claim.
  - HANDOVER.md matches standing.md's plan-branch copy of RESUME-CURRENT.md.
  - Transport is kept out of the code head.
  - pickup_local and FIX-PLAN-head.md name RESUME-CURRENT.md.
- `git diff --check` is clean. `git merge-tree` against current main 0bfb8883 is clean.

Notes
- tools/audit/round9/prestudy/ALT-ROSTER.json still has the old pickup_local text. It is an archived prestudy file, unchanged from main and not generated, so it is history.
- Commits are authored as tvofi with the noreply address, pushed with plain git. The Mac opens the PR as hpo-author.
- The diff changes policy (standing.md binds every seat), so it merges on tvofi's approving review, which the orchestrator gives under the mandate.
- Not run: the gate and CI. The PR is not open yet. The Mac merges only on green CI at a head that contains main.
