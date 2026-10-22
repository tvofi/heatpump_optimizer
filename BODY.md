R10-CI-LAYOUT-P2: BLOCKED. No code head pushed; this body is the fixer seat's return

Group R10-CI-LAYOUT-P2 (roster `handoff/audit-r10-roster` at `4209e135b`), part of #2495. Nothing was pushed to `handoff/r10-ci-layout-p2`. The seat stopped under `fixer.md` step 17: "a fix that cannot be sound within it stops and asks the orchestrator". This body asks. Base read: origin/main `738d950aa981efbdf866ff369942a69c5ae7d205`, at 2026-10-22T14:05Z.

## Why the seat cannot build PR 2 as dispatched

1. **The plan addendum and its design review were not in the dispatch.** The brief scopes PR 2 as "units U0-U11 as amended, A1 as amended (poll floor 60 s everywhere), A2/U11, A5, B3 ...". It also says "the orchestrator supplies both documents in the dispatch" and "build exactly the approved design, read from the ref, never from memory". Neither document reached this seat.
   - The approved design `1371a0a6` (DESIGN-P2.md) defines U0-U10 only. It defines no U11, A1-A6 or B1-B9: `grep -n -iE 'U11|A2|A5|poll floor'` over DESIGN-P1.md, DESIGN-P2.md, RESPONSE.md and the round-5 REVIEW.md (`afc00bfe`) matches only two unrelated REVIEW.md lines.
   - `git log --all -S'poll floor'` finds the phrase only in verdict records and `wip-sync/orchestrator-scratch:orch/SEATS.md`. SEATS.md (12:53Z and 13:08Z entries) puts the two documents on the orchestrator's own machine, under `plans/ci-layout/` (PLAN.md, DESIGN-REVIEW.md). No ref carries them.
   - Issue #2495's body says the same thing as the brief. The issue has no comments.
2. **The design's own build method needs GitHub writes this seat is barred from.** DESIGN-P2 section 10 builds PR 2 as a fan-out: U0-U10, each on its own `probe/ci-layout-<unit>` ref, checked by `workflow_dispatch` CI. U4-U8 also need draft probe PRs and twin `-before` PRs. The live controls need still more:
   - M-1 to M-7, including M-2's ship-or-delete decision for `gate-sweep.yml` and M-3's decision on the held-run approve steps;
   - U6's planted code-scanning alert, a SARIF upload and a dismissal;
   - U8's review submit and dismiss.

   The dispatch says to write no branch except the two return refs and to open no pull request. Decisions 0011 and 0013 make every GitHub write the orchestrator's. Without those runs, two of the design's choices stay open: whether `gate-sweep.yml` ships (M-2) and whether the approve steps stay (M-3). Building `ci.yml`, `gate.py` and the callee conversions without them would mean guessing at those choices.
3. **Size.** The roster sizes the group XL. Section 9 alone changes about 40 reader sites in one diff, plus policy text. `fixer.md`'s preamble bounds one fixer at about 400 production lines. The design itself plans the work as a fan-out, not a single seat.

## The ci-ratchet carry: why it was not paid separately

The carry asks for `tests/arch_score.py` and `tests/arch_score_head.py` to move into their own parallel job. The seat measured the current state and did not ship that move on its own, for two reasons.

- **Main's ratchet is green at this base.** The window is the 8 newest completed push `Tests` runs on main, read once from `actions/workflows/tests.yml/runs?event=push&branch=main&per_page=12`, the newest being `39778976748`. `tests/ci_ratchet.py`'s own `critical_path_minutes` reads median **49.86** min over that window, against a budget of 54.825. Null control: the same 8 runs with `status` set to `queued` give `no completed push Tests runs ... (fail closed)`, so the 49.86 comes from the data. `fast (3.14)` is still the run's critical path: 45.3 min in `39778976748` and 56.9 min in `39771546309`, against `closures` at 35.6 and 34.2. So a slow runner can still redden the ratchet, and the payment still has value. It is just not urgent at this base. Job logs could not be read (the log blob host answered 403 through the proxy), so the carry's 2350-2436 s for the arch_score pair was not re-derived.
- **On its own, the move weakens protection.** `fast (3.14)` is one of the 17 required contexts (`tools/policy/fixtures/required-contexts.json`, ruleset 23698884). A new job would not be required until the ruleset names it. Until then, a PR that breaks `tests/arch_score.py` would merge green. Only tvofi can add the context. Inside PR 2 the move costs no extra owner step: U5's `tests.yml` conversion places the job, and the `gate`'s `REQUIRED` lists it. That is the same rule as B3's REQUIRED[push] enumeration.
- **Recommendation.** Fold the pair's job into U5 and require it through `gate`. If the orchestrator wants the payment before PR 2, a standalone PR can do it, but it must stage a ruleset `required_status_checks` PUT that adds the new context in the same freeze.

## Other carries: their state at this base

- `python3 -I tools/audit/seat/selftest_wiring.py --check` → `selftest_wiring: 77 self-testing, 77 wired, 0 unwired`, rc 0. No merge of main happened, so the per-merge obligation did not arise.
- #2579 (R10-FLOW-YIELD-PROBE): its head `45754ede2` is not an ancestor of origin/main (`git merge-base --is-ancestor` → not-merged). A PR 2 seat must still rebase onto it once it merges.
- Carry 1 (`same_sha_dup_heads`), K9 (`merge_group` on the one required check), the self-test hygiene items, and the RECORD-API-BUDGET hand-off: none of these was started. They are all PR 2 work and stay owed as written in the roster.

## What the seat needs to proceed

1. The plan addendum (A1-A6) and its design review (B1-B9, the amended unit list), committed to a ref the seat can read. For example, add them beside the design at an archive tag, or include them in the dispatch.
2. A ruling on the fan-out. Either the orchestrator runs U0-U10 as the design says (one seat per unit, on probe refs, with the orchestrator doing the GitHub writes), or the dispatch grants this seat push rights to `probe/ci-layout-*`, draft probe PRs, and the U6 and U8 live writes.
3. Optionally, the ci-ratchet decision above: keep it inside U5, or ship it standalone with a staged ruleset PUT.

## Red checks

none. No code was pushed, so no check ran on this seat's work.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01SSiNtqXjY7fXbVrhF6MAui
