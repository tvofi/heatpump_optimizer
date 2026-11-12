Read-only study, R11-PROTECTION-CENSUS brought into round 10 (owner ruling P734/P737). Evidence: dev/audit/rounds/round10/protection-census/CENSUS.md. Result: the readable ledgers cannot support B1; per-head check reads are UNREAD (no gh or API token in this seat).

## Head

23d7ac26f4d64451839c64d83565e961428bbac4 (base 14f227c5bd0eb80855b21055cc668857a5f820b4)

## Mutation proof

n/a: no production or tool code changed; the diff adds a study document and a read-only enumerator.

## Null control

Runs 4080, 4107 and 4116 are green and yield no row: `python3 -I dev/audit/rounds/round10/protection-census/main_reds.py | awk '$1==4080||$1==4107||$1==4116' | wc -l` prints 0.

## Figures

- 28 red-job rows over 14 main push runs: `python3 -I dev/audit/rounds/round10/protection-census/main_reds.py | wc -l`
- 18 fix-review red entries over 14 PRs: `python3 -I dev/audit/rca/ci-red/entries.py` (prints ENTRIES 18 PRS 14)
- Classes of the 18 (real catch 9, infrastructure 7, grader skew 2) are counted by hand from the table in CENSUS.md; reds a B1 drop list would have removed (briefs, policy-docs, wave-script): none among the 18, a statement about ledger coverage only.

## Red checks

none

## Forward-carry

Per-head API read (r10_red_list_lag.py --rows, needs a token) and the cause of the 8 failed main ci-ratchet runs are UNREAD in CENSUS.md; the owner decides B1 from this result. Carry: dismissed: a study row marked UNREAD owes a later read by a seat holding a token, not a fix in this diff

## Friction

none
