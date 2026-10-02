Fix review: blocked ddb14ac5209da2fe6efd706ae3ab82f1935b838e code-in-transport: the round-3 fixes to gen.py pickup_local and FIX-PLAN-head.md are in transport commit 54ffa311, not in the code head

Round 3 of R9-PROC-5, on handoff/r9-proc-5-v2. Code head ddb14ac5, transport head 54ffa311, merge base 90335cbd.

Fixed
- The round-2 problem is gone. ddb14ac5's parent is 90335cbd. None of 1e55fec4, 996f63c1 or 921ed0fb is in its ancestry, and its tree has no BODY.md.

Blocking
1. ddb14ac5's tree is byte-identical to round-2's b9868471 outside tools/audit/handoff. The round-3 edits are the gen.py:445 pickup_local fix and the FIX-PLAN-head.md lines 330-338. They exist only in transport commit 54ffa311 (`git diff --stat ddb14ac5 54ffa311` shows BODY.md plus FIX-PLAN-head.md and gen.py; see transport_carries_code.txt). The PR opens and merges from the code head, so round-2 item 2 is still unfixed where it counts. The edits themselves are right: gen.py at 54ffa311 emits no "appends its milestone" or "mirror log" text.
   Fix, with no force-push: cut handoff/r9-proc-5-v3 from 90335cbd. Commit the code as `git checkout 54ffa311 -- docs tools/audit/round9` (one commit), then BODY.md alone in a transport commit above it. Once that is pushed, I expect a merge verdict on content alone.

brief_lint
- I ran gen.py at 90335cbd and at 54ffa311 (rc 0 both), then brief_lint.mjs on each generated roster in a 90335cbd tree. Both report "TOTAL: 0 error(s)", and the two outputs are identical (brief_lint_*_roster.out). The diff adds no lint error. I could not reproduce the W1 path errors the fixer saw. They are probably from linting the live plan-branch roster or a tree not at main, and either way they are not this diff's.

Not run: the gate and CI. There is no PR yet.
