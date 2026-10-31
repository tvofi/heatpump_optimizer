Fix review: merge ba30a714fa0f7c0ce09728e4cc6381b82921777b

bus-nonce: 97bfdde5221a5bbc2a1fd24d2d209953

Round 1. Record PR (triage s8 batch 87, P324 REJECT): 2 files, both under dev/programme/; no production code, so steps 1-3, 5-6 and 14 have nothing to mutate or measure.

## Findings

None. Every ground checked against the tree holds.

## Evidence

- Head measured: ba30a714fa0f7c0ce09728e4cc6381b82921777b, the head at verdict time. CI: merge_train.py classify exits 0 (GREEN, pending none, red none). Packet refusals none, carry_audit 0 findings, figure_lint 3 resolved.
- Merge with origin/main: git merge-tree --write-tree exit 0, no conflict.
- (a) holds: .github/workflows/budget-raise-gate.yml restores the check source from the base SHA and runs tools/policy/budget_raise_gate.py under python3 -I; review_carry.py and app_approve.sh are not in that pin, so moving the carry judgement into the check would trust the head's copy or pin more.
- (b) holds: train.sh line 87 reads "--approval-carry ... shift 2 ;;  # on already"; _carry_owner_approval is at merge_train.py line 1635 and is called at lines 1720 and 2040.
- (c) holds: merge_train.py lines 1653-1655 are the chain filter and no("this run's recarry did not move the head"). 958b4af8e and 9033a5958 are both tvofi merge commits on #3006's branch; 76d96ac77 is "ci: merge main".
- (d) figure re-derived with the named enumerator: budget_raise_gate.raises_between(<merge>^1, <merge>) over first-parent merges of origin/main since 2026-10-17 that touch a *_budgets.json gives 51 touching, 7 raising, exactly the body's 7 of 51 (ev/figure-7of51.txt). The "about 3 refusals" and "about 5 minutes each" come from orchestration logs (#2368, #3006) that are not in this tree; I did not re-derive them and they are unverified here.
- (e) The re-open trigger (3 or more refusals on raise PRs in one round, narrowed variant only) is stated and carries a fixture and nulls.
- The 2026-10-12 owner condition quoted in the body was not located in the tree by a grep of dev/governance and decisions; the docstring at merge_train.py 1636-1650 states the same condition. Not an error in the ruling.
