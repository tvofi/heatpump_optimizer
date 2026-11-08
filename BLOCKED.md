# BLOCKED: r10-outside-first repair, handoff refused (superseded by a parallel handoff)

Refusal, verbatim: `git push origin HEAD:refs/heads/handoff/r10-outside-first` was rejected as non-fast-forward. handoff/r10-outside-first is already at 4c4dd755dc73f1b18718e8ca55a4cbe2be9f9219, pushed by another hpo-fixer seat at 2026-11-08 09:54Z, and `body_push.sh` printed: `body_push: handoff/r10-outside-first is at 4c4dd755dc73, this checkout at 10fac77c39ad; push the code, then the body`. Not overridden.

The other seat's handoff is complete. Its code is 4c4dd755 (a fast-forward of PR head ed1f1b1d), and its body is handoff-body/r10-outside-first aad9fa6d26 (11:33Z), naming that head, with Prepr 4c4dd755.

This seat's head is 10fac77c39ad35eb2af763fd0cbac2966cf96ed2. It merges origin/main 4fe7d5934b0a into ed1f1b1d, then makes one replan commit. The replan.py repair is the same in effect as 4c4dd755's: the real slots go to `pick(sorted(ready))` in the dispatch order, and the critical path overflows exempt only when no real slot is free. 4c4dd755 writes it as two loops and also asserts slot 0 and that CPA, CPB and CPC are exempt, which is a stricter fixture. This head adds a `tier-before-overflow` entry to replan's mutation table, which 4c4dd755 lacks. Measured at 10fac77c: replan --self-test 0 failed; `PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh` rc=0 in 90m57s with 18 diff-mutant survivors (merge_train fixture lines, plus three open_driver survivors that `open_driver.py --self-test` kills); `prepr.sh --body-check` 0 errors.

Question for the orchestrator: keep 4c4dd755 / aad9fa6d as the handoff (recommended: it is complete and was handed off first). Optionally carry the `tier-before-overflow` mutation-table entry from 10fac77c onto it. Nothing here needs to replace it.
