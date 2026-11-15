Fix review: merge 2407a4ed50fe092f4c3ebe4e94867dcd7bfbd828

bus-nonce: c1e1ebd6dd187f8d9a7876ed77a90047

## Scope

Round: the body cites earlier reviews at `d9677a53d5` and `3487296ce9`. No `verdict/3566` or `probe/rev-3566-*` ref is readable, so this is at least round 3 and I cannot confirm the exact count. The packet's `## Review scope` is `full` (no verdict names the reviewed head `3487296ce9`), so I reviewed the whole three-dot diff against merge base `e0ad8b2bd3`, not only the delta. PR head re-read before writing: `2407a4ed50fe092f4c3ebe4e94867dcd7bfbd828`, the head named on the first line.

## Findings

- Follow-up: the new `bus.sh` pin (`grep -nE '^[^#]*(echo|printf)[^|#]*"\$[A-Za-z_0-9]+" *\| *grep +(-[A-Za-z]*q|"\$@")'`) does not catch a quiet flag after another flag. Mutant B4 reverts one probe to `echo "$out" | grep -F -q "is not main's copy"`, and the pin reports 0 hits, so the mutant survives. B1-B3, the body's own mutants, each give 1 hit and are killed. Widening the second alternative to `(-[A-Za-z]+ +)*-[A-Za-z]*q` closes the gap. Carry: R11-INTAKE-R10-RESIDUE
- Follow-up: the same race shape (a captured variable piped into `grep -q` under `pipefail`) also exists outside `bus.sh`, and the pin reads `bus.sh` only. Sites: `tools/audit/seat/cloud_relay.sh:1139` (production, `set -uo pipefail` at line 172), `tools/audit/seat/heartbeat.sh:75,82,87,91,95` (self-test, `set -uo pipefail` at line 24), `tools/audit/seat/seat_venv.sh:164,204,237` (self-test, `set -euo pipefail` at line 44). `ci-watch.sh:337` has the shape but no `pipefail`. Every one of these pipes a short string, which goes out in a single write, so the race is unlikely there. This is why I do not block. The body's class rule is the `bus.sh` pin, and at this head it returns nothing, so the class is not open within this PR's finding. Carry: R11-INTAKE-R10-RESIDUE

## Evidence

- CI: `merge_train.py classify 2407a4ed50fe092f4c3ebe4e94867dcd7bfbd828 --pr 3566` printed `GREEN 2407a4ed50fe092f4c3ebe4e94867dcd7bfbd828 pending: none red: none`, rc 0, on the first run (`ev/classify.txt`). No red, so no `## Red checks` answer is owed at this head.
- Merge: `git merge-tree --write-tree origin/main 2407a4ed50fe092f4c3ebe4e94867dcd7bfbd828` exits 0 against origin/main `5825e1346c`. Its stderr shows `LEDGER-MERGE: resolved tests/closures.json` (merged as a set) and no `MERGE-CLAIM` line, since neither claim file is touched (`ev/merge-tree.txt`).
- Policy roles currency: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- Step 1, mutation proof, re-run in a detached worktree at the head (`ev/mutants.txt`), each mutant restored afterwards:
  - G1: the `files_tokens` schema line deleted. `budget_raise_gate self-test: 280 checks, 1 failed`, killed.
  - G2: the rule graded `MAX` instead of `CAPFILE`. 1 failed, killed.
  - M1: `orchestrator.md` section 11 made to hand `roster_sync.py --apply`. The CARRY 3 check fails (`got: ['roster_sync.py']`), killed.
  - M1b (my own): `standing-merge.md` made to hand `merge_train.py classify`. 2 failed, killed.
  - M2: `handed()` returns `[]`. The null control fails, killed.
  - B1, B2, B3: `bus.sh` pin hits 1 each, killed. B4 survives (Findings).
  - Unmutated: `postmerge 21/0`, `budget_raise_gate 280/0`, pin hits 0.
- Mechanism: I reproduced it as the body states it (`ev/mechanism.txt`). Under `set -o pipefail; trap '' PIPE`, with `$out` holding a match plus 300000 bytes, `echo | grep -q` prints `echo: write error: Broken pipe` and returns rc 1, while the here-string form returns rc 0.
- Probe count "162": re-derived. The base `bus.sh` holds 162 `echo "$out" | grep` probes plus 1 `$got` probe. The head holds 162 `outhas` uses, and its only remaining match is the explanatory comment at line 1201. `outhas() { grep "$@" <<< "$out"; }` behaves the same as `echo "$out" | grep`: both feed grep the string plus one trailing newline.
- Step 2 / step 9, the harness: the packet names no finder's harness. For this retirement the harness is the body's committed enumerator (`git grep -n 'nudge\.md' ... | wc -l`), and I re-ran it. It gives 46 at merge base `e0ad8b2bd3` and 5 at the head. Those 5 are the kept `files_tokens` cap (`policy_budgets.json:132`, carried), `HANDOVER.md:607` and three `PLAN-TABLE.md` rows, each dispositioned in the body (`ev/figures.txt`).
- Step 4, claims: `git diff --stat` over `tests/golden/claimed_drift.txt`, `card_claimed_drift.txt`, `custom_components/` is empty, and no fixture moves.
- Step 5: `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched.
- Step 8, figures re-derived at the head:
  - `policy_lint.mjs` prints `TOTAL: 0 error(s) across 51 policy file(s)`.
  - `rules_sync.mjs --check` prints `RULES-SYNC ok`.
  - `brief_lint.mjs` exits rc 0.
  - `structure.py` prints `STRUCTURE RATCHET PASSED`.
  - Self-tests: `sweep_render 39/0`, `orchestrator_tick 319/0`, `roster_edit 311/0`.
  - `--budgets` at the head: corpus ~65263, always-loaded ~3598/3349, fixer ~6273/5852, record ~7230/7405, policy ~10006/9958. Each matches the body.
- Step 14, budgets earned: the head merged with origin/main `5825e1346c` measures `corpus ~65926 tokens, cap 65926 +band 500`, with `TOTAL: 0 error(s)`. Main alone measures ~69740, and 69740 - 3814 (the deleted file's token cap) = 65926 exactly. The re-record down is therefore earned by the deletion: with the file restored, the merged corpus would sit ~3814 tokens above the new cap plus band. The `files_tokens -> CAPFILE` grader rule grades exactly as the existing `files -> CAPFILE` rule does. A dropped cap is routine only when its file is absent from the head, and a cap removed while its file is in the tree still grades as a raise (self-test pin). I planted a `MAX` grading (G2) and the test refuses it. No always-loaded or role cap is re-recorded.
- Step 10, forward-carry: `R11-INTAKE-R10-RESIDUE` is in origin/main's `dev/programme/rosters/wave-r10-groups.json`, and the item that drops the kept `files_tokens` cap is landed there (line 25801), stating the grader fix's merge as its precondition.
- Reconcile with #3499: the step-15 WAIT exception is carried verbatim in `tools/audit/seat/sweep_template.md` step (6) at line 87.
- Approval: this is a policy change (`CLAUDE.md`, `gate-scoping.md`, `policy_budgets.json`). The body cites the owner's mandate (comment 6893738184 on #3394, scope `all`). Checking the mandate is the merge seat's job; this verdict judges code, tests and harness only.
