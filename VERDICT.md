Fix review: blocked 4180a7d01c3e8e4b34d746c4bccba452cf415d25 carry-missing: P199, P200 and P203 are carried only in this body; their ruling is on origin/main, so the three roster carries are writable now and must land before merge
bus-nonce: 37597a6f18885bc7026000c01909529a

# Fix review — #2871 `roster: round-10 batch 23`

Head measured: `4180a7d01c3e8e4b34d746c4bccba452cf415d25`, unchanged before and after every measurement below.
Merge base with origin/main: `d620369fad72e18081b2efa1b66ee0058296f12c` (= current origin/main).
Three-dot diff vs main: `dev/programme/delivery/2871.md` (1/0) and `dev/programme/rosters/wave-r10-groups.json` (25/17). Nothing under `dev/governance/`, `.claude/rules/`, `.cursor/rules/`; `VERSION`, the manifest version and the `RELEASE_NOTES.md` heading untouched; both claim files untouched.

## What I verified and found true

- **Every flipped row is true.** #2834, #2858, #2862, #2864, #2865 are MERGED and each row's merge sha matches the API exactly (`0137c4c`, `3b4180d`, `149ce54`, `6fe5170`, `bfc4a1e`); #2866 is MERGED at `484d990` and its row reads that. #2871's own row reads `**open**`, correct for an open pull request. `evidence/record-rows.txt`.
- **The flips are the generator's, not a hand.** I re-ran `record_row.py --plan` against the base tree `6fe5170cd` with the API's merge facts and the base roster: all six planned lines are byte-equal to the six rows at head (`6/6`). `self_disposing()` returns True for #2856 and #2863, so the record-class exemption the body names is the tool's own predicate, and the one-line-each-way rewrite shape is `_rewrite_granted`'s. `evidence/generator-plan.json`, `evidence/generator-plan-check.txt`, `evidence/record-class.txt`.
- **The roster is valid and its bytes are the tool's.** JSON loads, 208 groups; the head blob is `da55886c746714f6d10b4b12738e030fd9c11c37` and is byte-identical to `json.dumps(parsed, indent=1)` (1,055,658 bytes, no trailing newline), the dump `roster_edit.py:563` writes. `roster_edit.py --self-test` 117 checks 0 failed; `roster_sync.py --self-test` 55 checks 0 failed (the body's figure re-taken); `record_row.py --self-test` all checks passed. `evidence/roster-validity.txt`.
- **The lint gate.** `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` at head: `TOTAL: 0 error(s) across 1 file(s)`, exit 0. `evidence/brief-lint.txt`.
- **Record content the body does not enumerate is coherent.** The head carries 18 roster commits after `1e9180dc9`; the six groups changed against main are R10-COP-GATE, R10-COP-PARTLOAD, R10-FLOW-AUDIT-PLAN, R10-FLOW-JIDOKA, R10-ORCH-REVIEW-PACKET, R10-SAV-COMFORT. The two branch tips they name match origin (`handoff/r10-cop-partload` = `775ae0340`, `handoff/r10-orch-review-packet` = `52aa5105`), and PR #2869 exists OPEN as recorded. `evidence/changed-groups.txt`, `evidence/body-vs-head.txt`.
- **CI at the head** is green: 47 contexts, zero non-green. `evidence/check-runs.txt`.
- **No conflict:** `git merge-tree --write-tree origin/main HEAD` exits 0, tree `945c422a`. `evidence/diff-and-merge-tree.txt`.
- **The body's Carry lines resolve:** three finding items, 3 routed, 0 bad destination. `evidence/carry-audit.txt`.

## Findings

### 1. BLOCKING — carry-missing: the three batch-35 findings are not in the tree

Triage batch 35 accepted three proposals (`dev/programme/triage/s6-batch35.md`, on origin/main), each routed to a live group:

- P199 (dead merge trains) → `R10-FLOW-WIP` (stage not-started)
- P200 (reviewer verdict relay format) → `R10-ORCH-REVIEW-PACKET` (stage in-progress)
- P203 (`roster_lib.gate_kind`) → `R10-ORCH-ROSTER-SCHEMA` (stage not-started)

None is in the tree at this head: the roster carries zero mentions of `s6-batch35`, `dead merge trains`, `verdict relay` or `gate_kind`, and no file under `dev/programme/carries/` cites them. They exist only in this PR's Forward-carry prose, which `finding-propagation.md` says records but does not propagate.

The body's stated reason for deferring them is false at this head: it says "the batch-35 record lives only on `handoff/triage-s6-batch35` (`c73d8984a`), not on origin/main or this branch". `c73d8984a` is in origin/main and in the head (via #2867's merge `38d12ffd8`, 02:28:41Z), `dev/programme/triage/s6-batch35.md` is at origin/main and at head, and the body was written at 03:53Z — after both. `roster_edit.py`'s triage gate reads the ruling from the edit's base and else origin/main, so one `append-carry` per line is writable now. `evidence/triage-carries.txt`.

Carry: R10-FLOW-WIP
Carry: R10-ORCH-REVIEW-PACKET
Carry: R10-ORCH-ROSTER-SCHEMA

### 2. Body figures and null control are pinned to an ancestor, not the head

The body claims it "describes the head it is pushed with", but its opening, null control and Figures measure `1e9180dc9`, which is on origin/main. Re-taken at head:

| figure | body (at `1e9180dc9`) | head |
|---|---|---|
| roster blob `this head prints` | `852ec7bd…` | `da55886c…` (`852ec7bd` is origin/main's) |
| no-merges commits `6fe5170cd..` | 95 | 119 |
| roster numstat `6fe5170cd...` | 461/62 | 475/68 (vs current main 25/17) |
| groups changed `6fe5170cd..` | 27 | 28 (adds R10-FLOW-AUDIT-PLAN) |

The body's numbers are true at the ref it names (`6fe5170cd..1e9180dc9`: 95 commits; numstat 461/62; groups 199→208, 9 added, 27 changed — all re-derived), but that ref is 18 roster commits behind the authored code head `46df1de62` the PR actually carries, so the sentence "this head prints `852ec7bd`" is false. `evidence/body-vs-head.txt`.

Carry: R10-ORCH-ROSTER-SCHEMA

### 3. Not carried by design — what the next batch still owes

The roster ref is at `d1b115ef`; this head carries `46df1de62`. The four commits between them are R10-HOUSE-GRADE only (`94ece3d08` set-stage, `4701ec177` / `91876ec3c` / `d1b115ef1` set-resume), 4/4 roster lines. The next batch carries them. `evidence/not-carried.txt`.

Carry: R10-ORCH-ROSTER-SCHEMA

### 4. Non-blocking note — pre-existing ledger rot outside the record window

Fifteen rows read `**open**` at this head. One is #2871 itself (correct). Nine are record-class merges whose open self-row `self_disposing()` exempts by design (#2198, #2483, #2604, #2795, #2845, #2847, #2856, #2863, #2868); #2856 and #2863 are disclosed in the body. The other five are pre-existing and not in this diff: #2465, #2485, #2480, #2609 are merged but not record-class, and #2373 is CLOSED-unmerged. All four merged ones landed before v7.0.4 (`2026-10-22T15:48:08+02:00`; #2609 merged 37 s before the tag), so they are outside the beat's `--since` window and owed by no current beat. `evidence/ledger-rot.txt`, `evidence/record-class.txt`.

Carry: dismissed: pre-existing before the v7.0.4 record window, outside this PR's diff; the row is graded by the API, not the word

## Evidence

`evidence/HEAD.txt` (exactly the head sha), `pr-body.md`, `diff-and-merge-tree.txt`, `record-rows.txt`, `generator-plan.json`, `generator-plan-check.txt`, `roster-validity.txt`, `brief-lint.txt`, `carry-audit.txt`, `body-vs-head.txt`, `triage-carries.txt`, `not-carried.txt`, `changed-groups.txt`, `record-class.txt`, `ledger-rot.txt`, `check-runs.txt`.
