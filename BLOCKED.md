Question: this seat ran dispatch 72dac8c18e (start 9774026d05), which was superseded by dispatch fbe372565b (start 95c04821e5). The newer seat has returned: handoff/r10-plan-page-residue is at 0b32b0ba31, and handoff-body/r10-plan-page-residue is at 8bc2a3c5b9. My push to handoff/ was refused as non-fast-forward, and I did not force it. This ref's parent, 11911ca117, is an independent repair of the same round-2 verdict. Should it be discarded, or diffed against 0b32b0ba31 for anything the returned head lacks?

What 11911ca117 holds, for that comparison:
- hot-render, hot-gates, hot-discharged and hot-notdone are killed in dev/audit/harnesses/r10_plan_page_mutants.py: M0 null, 38 killed, survived=0.
- blk and the hotfix mark share one gating(entry) predicate.
- size_durations.fetch_rest has --sizes-fetch rest, and its provenance names the read path ("Input: 1025 merged PRs created since 2026-10-12, read over rest.").
- durations.json was re-measured at 2026-11-11T07:24:11Z.
- check_plan's dead closure fallback is deleted.
- tools/pr/prepr.sh rc=0 at 11911ca117.
