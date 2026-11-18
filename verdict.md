Design review: approve 29f8ba81157134ab65ab38a45c4668b6c4834ef5

Round 2. Delta-only review per the owner ruling (later rounds review the delta): git diff 9fe9f13b63 29f8ba8115, design.md only, plus both round-1 points checked from a detached worktree. Code read at the note base origin/main bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f.

Round-1 points:
1. class-open, debugger.py:325 _solver_smoke: resolved. Section E exempts it from admit_background and gives the reason: once per finalize, already bounded by SELF_TEST_BUDGET (debugger.py:76, :588), and a denial would leave the self-test with no answer. It is limited=False, so it stays out of the F slot. The section 5 grep now covers custom_components/heatpump_optimizer/*.py. At bc658f9 that grep gives four calls and the definition (coordinator.py:9007, :10712, :11174 def; debugger.py:325; services.py:775), which matches the note. Section 6 adds a test: a self-test run after the background slot is taken still returns cost_delta and leaves background_taken unchanged. The async_request_refresh count is re-derived to 18.
2. D1-s1-01 reproduces on main: resolved. Section 1 records it and H stays a fix. It falls back to a regression pin only if the fixer reads 0 on its own base.

Ruling 4 (button-1641) is folded into section C: PARALLEL_UPDATES is 0 at button.py:46 (6c1834977a), it stays 0 and is pinned, and the off_the_action docstring is updated. Section 6 adds a test that a reset pressed during the optimize-now press is not queued, and the carry is reworded. Nothing else changed, so seam, shape, sibling designs and cost carry from round 1.

Seat token count: not reported by this harness.
