Makes one ruling mechanical (group R10-REVIEW-CARRY). tvofi, 2026-10-27, verbatim: **"if there are no code changes, the previous review can be carried"**.

The test is a commit range, not an opinion: `git rev-list --count <reviewed>..<new> --not origin/main`. Zero, or a count whose commits are all merges, is a carry. A merge authors no commit -- what it joins is main's history (`--not` drops it) or branch commits, which the range already returns as non-merge commits -- so a merge of the branch's own previous head, the shape `update_pr.sh` re-cuts a head into, is not a change either. Any non-merge commit means the head carries code and takes a fresh review. A body rewrite is not a commit in the range and voids nothing.

Four sites, each demonstrated below:

1. `tools/audit/seat/review_carry.py` (new): prints the branch-only commits and exactly one of `CARRY` / `FRESH-REVIEW`; exit 0/1, and 2 when it cannot decide (an unknown sha). Listed in `tools/audit/seat/INSTRUMENTS.md`.
2. `tools/audit/seat/bus.sh dispatch --reviewed-head`: a refusal, not a warning, when the range is clean -- it names the reviewed head, mints nothing and records nothing.
3. `tools/pr/app_approve.sh --carry`: its rule was "every merge must merge a commit on `origin/main`", which refused #2876 at `d08647f05` -- a merge-only move of the branch's own previous head, the commonest clean carry there is. It now applies the same non-merge-commit criterion, and still reads the claim resolution: a `claimnotes` file resolved to the pure union of both parents' lines is not a change; one that drops or rewrites a line is. The literal union rule has a measured cost: over the last 200 first-parent merges 19 of 400 claim-file resolutions are not the pure union (15 keep main's copy alone, 4 keep the branch's), and each of those would refuse a carry. None of the 19 adds a line neither parent had (see Figures): the rule can refuse content loss, never pass content a review did not see.
4. The contracts: `fix-review.md` says which head a `merge` verdict attaches to and that it carries while the range is clean; `orchestrator.md` says a second reviewer over a clean range is the error, not diligence. Both stay inside their policy budget by cutting prose -- no `*_budgets.json` is touched.

`merge_train.py`'s owner-approval carry answers a different question and is untouched.

## Approval

Policy: this changes what a fix reviewer and the orchestrator must do (`dev/governance/roles/fix-review.md`, `dev/governance/roles/orchestrator.md`), so it merges only on tvofi's approving review at this head (`CLAUDE.md`; decision 0009 step 6). The ruling it makes mechanical, verbatim: **"if there are no code changes, the previous review can be carried"** (tvofi, 2026-10-27), and the coordinator's 2026-10-27 addition that a claim file resolved to the pure union of both sides is not a change. No cap raised; `policy_budgets.json` is untouched and the two role files stay inside it by cutting prose.

## Head

`6f905c40f7e48f640e849352e0696af5585874f9`

## Mutation proof

- `review_carry.py`, with the pre-fix rule (a merge with no parent on `origin/main` carries): `FAIL a re-cut merge of the branch's own previous head answers CARRY: got 'FRESH-REVIEW', want 'CARRY'` -- 14 checks, 1 failed.
- `bus.sh`, with the refusal branch disabled: `FAIL dispatch refuses to mint a nonce over a clean range, naming the reviewed head, and records nothing` -- 88 checks, 1 failed; its null control, `dispatch mints at a head that does carry code`, stays green, so the check does not pass for the wrong reason.
- `app_approve.sh`, with the old on-main merge rule restored: `FAIL CARRY: a re-cut merge of the branch's own previous head (#2876's shape) (got '1', want '0')` -- 259 checks, 1 failed.
- `app_approve.sh`, with the claim driver's stderr left visible: `FAIL with the refusing driver's own words kept out of the carry (got '1', want '0')` -- 259 checks, 1 failed.
- The two contract sentences are prose: no check in the tree reads them, so breaking one reddens nothing. What is measured is their size -- `policy_lint` reports `TOTAL: 0 error(s) across 50 policy file(s)` and `RULES-SYNC ok: every generated rule is the generated form of its source`.

## Null control

- At `origin/main`, `review_carry.py` does not exist and `bus.sh dispatch --reviewed-head` dies on the unknown flag; the two real heads below get opposite answers from the new instrument, one command.
- `origin/main`'s `app_approve.sh --carry` on #2876: `CARRY: no 253dc4867cf39f2aa9875f5f2540c5b67b7c1018 -> d08647f0513a5a568b5ac917748df02adf9fded6: b71541154e1f85ed9da2b86cb543a0cf9cbf49bf merges e0237e6d0e860f664512b2970d7ad65a54db8acd, which is not on origin/main`, exit 1; the same two SHAs at this head print `CARRY: yes`, exit 0.
- #2854's range still refuses at this head: `fccb883716ce7f8677ea64a2107971baa5381ea9 is not an ancestor of 9f424cf742eee1c00ab13a75a926874f72470eab`.

## Figures

- #2876 `253dc4867 -> d08647f05`: branch-only 3, all merges, `CARRY` -- `python3 tools/audit/seat/review_carry.py 253dc4867cf39f2aa9875f5f2540c5b67b7c1018 d08647f0513a5a568b5ac917748df02adf9fded6`
- #2854 `fccb88371 -> 9f424cf74`: branch-only 41, 27 of them non-merge, `FRESH-REVIEW` -- `python3 tools/audit/seat/review_carry.py fccb883716ce7f8677ea64a2107971baa5381ea9 9f424cf742eee1c00ab13a75a926874f72470eab`
- #2876 carried by `app_approve` -- `bash tools/pr/app_approve.sh --carry 253dc4867cf39f2aa9875f5f2540c5b67b7c1018 d08647f0513a5a568b5ac917748df02adf9fded6 origin/main`
- claim-file resolutions: 381 pure, 19 not, of 400 -- `git log --merges --first-parent -n 200 --format=%H origin/main | while read c; do set -- $(git rev-list --parents -n 1 $c); shift; [ $# -eq 2 ] || continue; for f in $(git show origin/main:.gitattributes | awk '$2=="merge=claimnotes"{print $1}'); do got=$(git show $c:$f 2>/dev/null | awk NF | sort -u); want=$({ git show $1:$f 2>/dev/null; git show $2:$f 2>/dev/null; } | awk NF | sort -u); [ "$got" = "$want" ] && echo pure || echo other; done; done | sort | uniq -c`
- the 19 non-union resolutions add 0 lines neither parent had -- `git log --merges --first-parent -n 200 --format=%H origin/main | while read c; do set -- $(git rev-list --parents -n 1 $c); shift; [ $# -eq 2 ] || continue; for f in $(git show origin/main:.gitattributes | awk '$2=="merge=claimnotes"{print $1}'); do got=$(git show $c:$f 2>/dev/null | awk NF | sort -u); want=$({ git show $1:$f 2>/dev/null; git show $2:$f 2>/dev/null; } | awk NF | sort -u); [ "$got" = "$want" ] || comm -13 <(printf '%s\n' "$want") <(printf '%s\n' "$got") | wc -l; done; done | awk '{s+=$1} END {print s+0}'`

## Red checks

`none`

## Forward-carry

`none`

## Friction

- `brief-citations`: stale: the brief names `python3 tools/audit/carry_audit.py pr-body <body>`, and the CLI is `{check,pr,sweep,owners}` with the body arm `check --body <file>`. Carry: dismissed: one command's cost on an out-of-tree brief; `--help` names the arm.
