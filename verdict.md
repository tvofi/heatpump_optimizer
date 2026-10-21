Fix review: blocked bb9f93e8bc0d8ed6bf2a9b397c41d378c7d8cf5e spec-unmet: CLAUDE.md role row for design-review.md keeps the retired two-revise-rounds rule

bus-nonce: 574c59fdd9cb535f9ae31690827f144e

Round 2 of fix review for PR #2586 (round 1 blocked, comment 6324652583, ruling-unmet). Measured head bb9f93e8bc0d8ed6bf2a9b397c41d378c7d8cf5e (tree identical to d2ba1e18); merge base 57f0c9c77cfd5958e0a2443e158bea8326bedae2 = origin/main. Roles dir current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.

## Block

- `CLAUDE.md:119` (the always-loaded index) describes `design-review.md` as "only `Design review: approve` dispatches the fixer, and two `revise` rounds go to the orchestrator". That is the drafts' retired rule. The pin at 30c57744a dropped it, and this head's `design-review.md` replaces it with "Three notes at most … the designer re-cuts to the minimal shape … remaining points become carries". The body says the "after two revise rounds" sentence is gone and calls the `CLAUDE.md` row "unchanged". The row is indeed unchanged from round 1 (`git show d3e34be5:CLAUDE.md` line 119 is the same text), which is how the stale rule survived. The index and the contract now give an L/XL design loop two different exits: escalate to the orchestrator after 2 rounds, or re-cut after 3 notes. Fix: reword the row to match the contract, for example "… dispatches the fixer; a third `revise` sends the designer to re-cut". Plant P1 in `ev/mutants.txt` shows that wording keeps `policy_lint` at TOTAL 0, so no budget moves. Carry: dismissed: fixer repairs this branch

## Verified (brief items 1–4)

- (1) 0012 reads "Status: Revoked 2026-10-21 (owner addendum 6322712314); kept as history", and its last section is "Revoked (2026-10-21)". The addendum is tvofi's comment 6322712314 (2026-10-21T17:49:45Z), which says revoked, file kept. 0014's title and item 1 say revoked. `policy_lint.mjs` is a comment-only edit in the past tense. `git grep -iE 'moratorium|0012'` outside history (roles, rules, CLAUDE.md, AGENTS.md, .claude, tools/policy) finds only 0014 and numeric strings.
- (2) `designer.md` and `design-review.md` match the pin section by section. The match covers "A note, not a stop" (3 bullets, the stop case kept), "Notes for the fixer are findings, not revise points", "Decisions are routed, not revised" (`decision: orchestrator|owner`), "Three notes at most", and the carry grammar with `Carry: dismissed: <reason of two or more words> (item <id>)`, colon, in both files. The PR's deliberate changes are present: the R17 threshold (L/XL, no approved design, pre-study or prototype; matches RULINGS-201-3 R17), the hard 1-h box, and `design-verdict/<group>`. `tests/seam_map.json`, which `designer.md` cites, exists.
- (3) Every budget figure re-derives at this head (`ev/head_checks.txt`, `ev/main_checks.txt`). The aggregates match the body: corpus ~62892 (cap 62892), at main ~61142 (cap 61026); always 3498; fixer 6173; record 7321; policy 9906. Per-file rows are designer 60/878 and design-review 53/778, each cap equal to its measurement. Mutants M1, M2/M2b, M3 and M3b reproduce exactly as the body states (`ev/mutants.txt`). `rules_sync --check` is ok, `brief_lint` rc 0, and STRUCTURE RATCHET PASSED. `archscore --diff origin/main` prints `Architecture score: dS +0.0000 NULL`, which matches `## Raise justification`.
- (4) `git merge-tree --write-tree origin/main bb9f93e8bc0d8ed6bf2a9b397c41d378c7d8cf5e` exits 0 (tree 25c64dc7). Check-runs at this head (`ev/check_runs.tsv`, 52 runs): the reds are `budget-raise-gate` (×4) and `nightly-status` (×1), and `## Red checks` answers both. `pr-contract` succeeded at 20:23:50Z, after the last red concluded at 20:23:36Z.

## Non-blocking observations

- `dev/programme/rosters/wave-r10-groups.json` (main and the roster ref 23ef06dc) still briefs the in-progress R10-RCA-ORCH-CONTINUITY seat that "Decision 0012 forbids a new policy file, lint class or rules entry until 2026-10-31". That constraint is void under the addendum, and it limits the seat's choice of countermeasure. The stale text is in the roster, not in this diff. Carry: R10-RCA-ORCH-CONTINUITY
- `design-review.md` step 7 lists `architecture-unsound`, `class-open` and `harness` but not `product-tradeoff-regression`, which its own step 2 uses. The list says "where they fit", so it is not exhaustive and this is not a defect. Carry: dismissed: illustrative list, non-exhaustive
- `closures` was still `in_progress` at this head when read at 2026-10-21T20:31:53Z (started 20:08:27Z), so its conclusion is not part of this verdict. Carry: dismissed: heavy lane still running

## Carry index

carry_audit.py hashes the whole item, marker included, so no item can quote its own id. These lines repeat each marker with its id.

- Carry: dismissed: fixer repairs this branch (item 66ab37aa)
- Carry: R10-RCA-ORCH-CONTINUITY (item 3703aa13)
- Carry: dismissed: illustrative list, non-exhaustive (item d441b8ee)
- Carry: dismissed: heavy lane still running (item 87822ce4)

RESULT policy_lint TOTAL=0 files=43 corpus=62892/62892 designer=60/878 design-review=53/778
RESULT mutants M1=2err M2=1err M2b=0 M3=1err M3b=1err P1(row-corrected)=0
RESULT merge-tree rc=0
RESULT reds budget-raise-gate,nightly-status answered; closures in_progress
RESULT index-contract-mismatch CLAUDE.md:119 "two revise rounds go to the orchestrator" vs design-review.md "Three notes at most … re-cut"
