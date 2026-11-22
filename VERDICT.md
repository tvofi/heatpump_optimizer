Fix review: merge e7dec855cbf1688c5c0ef97b9e53740f5e3fc0e8

bus-nonce: cc4bb87774d9b1a831556b0fc4ded4f2
pending-ci: gate

Round 1 (first round: no reviewed head). The diff adds `dev/audit/rca/R11-RCA-MODEX.md` and `dev/programme/delivery/3843.md` only: no production, check or test code, so steps 1 (mutation), 4 (claims), 6 (class) and 14 to 16 have no object here.

## Evidence

- RESULT merge-tree: `git merge-tree --write-tree origin/main e7dec855cb` exits 0 (tree `72d670e5d9`), so the head merges cleanly (`ev/merge-tree.txt`).
- RESULT VERSION, manifest, notes: the three-dot diff touches only the two files above (`ev/diffstat.txt`), so `VERSION`, the manifest version and the `RELEASE_NOTES.md` heading are untouched.
- RESULT roles current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` prints nothing.
- RESULT body head: the body's `## Head` names `e7dec855cb`, the head reviewed (`ev/HEAD.txt`).
- RESULT run A re-derived: in an export of `d4bd8ed29e`, `python3 tests/structure.py` prints `RESULT module_excess_loc=21779`, `FAIL module_excess_loc 21779 > 21718 (+61)`, `1 STRUCTURE BUDGET(S) BREACHED`, rc 1; that tree's table reads `module_excess_loc` 21718 at `recorded_at` `e698fc8ac3`, as section 1 states (`ev/runA-d4bd8ed29e-structure.txt`).
- RESULT main lacks the row: `git show origin/main:tests/structure_budgets.json | grep -c module_excess_loc` prints 0.
- RESULT re-record chain: `git log -G module_excess_loc origin/handoff/r11-seam-ratchet-raise -- tests/structure_budgets.json` lists `045f358a4f` and the re-records `0dfa61d887`, `ef7d2e4038`, `0800f342ef`, `b278df39d6`, `bd58b7341e`, `611f843468`, whose subjects carry the moves 21549->21536->21571->21633->21694->21718->21779 the section-1 table states (`ev/rerecords-611f843468.txt`). The merge commits and their author times (`382df86816` 05:51Z ... `d4bd8ed29e` 22:39Z) match the table.
- RESULT mechanism: `tests/structure.py` at main compares `if current > budget:` (FAIL) and returns 2 on an unrecorded gain, and prints "never to make a failure go away", as section 2 quotes.
- RESULT new key is no raise: `tools/policy/budget_raise_gate.py` `_leaf_raise` returns None for a leaf absent at the base unless its kind is MAX0, consistent with section 6 rung 1.
- RESULT carry: the body's forward-carry is on `handoff/audit-r11-roster` at `582010efc2`, `dev/programme/rosters/wave-r11-groups.json` line 3005, group `R11-CLOSEOUT-CLEANUP`; `carry_audit` at the head: 1 routed, 0 unrouted.
- Not re-derived: the `modex.py` column of the section-1 table at the main-only revisions (`ae0ed64af8`, `35402f7817`, `4ebd430fbf`: main's `structure.py` does not measure the row and `modex.py` is not in the tree), the CI run and runner-minute counts of section 5, the open-PR and 14-merge census of section 4, and prototype runs B to F (the prototype is in the orchestrator's local overlay, not in the tree). Carry: dismissed: evidence, not a finding
- RESULT CI: `merge_train.py classify e7dec855cb --pr 3843` printed `WAIT e7dec855cbf1688c5c0ef97b9e53740f5e3fc0e8 pending: gate red: none` (rc 3) on every run from 03:20Z to 03:52Z (`ev/classify-poll.txt`). Live check runs at 03:29Z: every context in `owed-reds` (`tests / coverage-ratchet`, `tests / fast (3.14)`, `tests / mutation`, `tests / typing`, `validate / validate-hacs`) reads success; `gate` (job 137080328015) and `tests / lane-proofs` were queued; the packet's `gate` failure is job 137063908896 of the earlier run 44970215676, superseded. No owed red, so no `## Red checks` answer is owed.

## Notes

- Note: figure: section 1 says `git log -G` over the branch lists "the introducing commit and seven re-records"; at `611f843468` it lists six; the seventh, `21428d8202`, is in no ref this seat fetched (`fix/r11-seam-ratchet-raise`, `handoff/r11-seam-ratchet-raise`, `archive/fix-ratchet-raise-fix-ratchet-raise-r3-3e1e9141`). Carry: dismissed: paperwork in a record, no stage changes on it
- Note: figure: the section-1 red windows sum to 7.16 h from the table's own times (2.67 + 0.66 + 1.28 + 0.67 + 0 + 1.88), the record and the body state 7.18 h; the first row's 2.67 h uses `0dfa61d887`'s author time, 7.18 matches its committer time (08:33:05Z). Carry: dismissed: paperwork in a record, a 0.02 h difference that moves no conclusion of the cost test
- Note: carry-control: the roster carry at `582010efc2` line 3005 restates the two open questions but not the control that answers the second, which section 4 itself names: a `-G` key count also matches table rewrites and is only an upper bound, so each key-introducing merge must be classified per instance. Carry: R11-CLOSEOUT-CLEANUP

## Findings

- Follow-up: the record's measurements rest on two out-of-tree instruments, the #3735 seat's `modex.py` and the prototype `proto/RCA-MODEX/local_rows.py` with `demo.sh`, both disclosed as such; neither is in the tree, so runs B to F and the main-side column cannot be re-run by a later seat. Landing the prototype (or its successor) with its runs is part of proposal P-R11-99's ruling at round-end triage. Carry: R11-CLOSEOUT-CLEANUP
