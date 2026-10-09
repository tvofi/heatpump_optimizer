Fix review: merge a26f24285ccfa7f00f8ed0a0daa4bebc548c08a7

bus-nonce: e1cd51cfec69b0e78a507704c8df7648
seat: review-deltas-1015
Evidence: /Users/timmalmstrom/hpo-seats/review-deltas-1015/2068/evidence

Round 5 of this PR, judging a **resolution delta** — and unlike the other three in this batch, this delta carries a real conflict resolution, so the table merge is the thing I measured, not the fact that main arrived. The live head moved from `def887d8905bee4d9ad39f06e75068df074362f4` (my round-4 `merge` verdict, comment 6077635736) to `a26f24285ccfa7f00f8ed0a0daa4bebc548c08a7`. `isDraft` is still true; marking ready stays the orchestrator's.

## The delta

`git log --first-parent def887d8..a26f24285` is exactly one commit: `a26f24285 Merge origin/main into fix/r9-eg-a4`, parents `def887d89 b2b6acd64`. Delta diff stat `def887d8..a26f24285`: **29 files changed, 2680 insertions(+), 1294 deletions(-)**.

- RESULT every one of those 29 paths is a path `origin/main` itself changed (`comm -13` against `def887d8..origin/main` is empty) — nothing outside main rode in on the merge.
- RESULT of the branch's 27 owned files, **26 have byte-identical changed `+`/`-` lines** at both heads (1012 owned lines at each); the one that differs is `tests/closures.json` — the conflicted file, and only that file. `VERSION`, the manifest version and the notes heading are untouched.

## Step 13: the closures.json resolution, verified as a table merge

`merge-base(def887d8, origin/main) = 47b083b0`. Both sides edited the table; the branch owns it, and GitHub's `DIRTY` was driver-less (`claim-files.md`, steward S2). I re-derived the merge myself with the drivers installed and then checked the result key by key.

- RESULT the driver now finishes what the branch's older driver refused: `git merge-tree --write-tree def887d8 origin/main` → **rc=0**, stderr `LEDGER-MERGE: resolved tests/closures.json`, `inert_reads.tests/harness_headers.py: merged as a set (536 entries)`, `re-run the gate that owns this file before pushing`. **No `MERGE-CLAIM` marker** — neither claim file conflicted, and both are byte-identical to `origin/main` at the head (`62bf9eaba2…`, `c683379daf…`).
- RESULT the pushed resolution is reproducible, not hand-written: `git diff -r <merge-tree's tree> a26f24285` is **empty**. Bit-identical to the driver's deterministic output from the two parents alone.
- RESULT at the head, `git merge-tree --write-tree origin/main a26f24285` writes tree `91c2eb6a7dfc96fb48831e38e6a1a40aba5235fa`, which **equals** `a26f24285^{tree}`: the resolution is complete and the merge is now clean (GitHub: `mergeable=true`; `blocked` is the approval, not a conflict).
- **closures** (33 keys each side): main changed 0 keys vs base; the branch changed 3 — `tests/arch_score.py`, `tests/entities.py`, `tests/harness_headers.py` — each adding `.github/workflows/arch-score.yml` to the closure list. Head equals the branch on all three, and the arch-score entries survive: `tests/arch_score.py` and `tests/arch_score_head.py` are both present with the branch's exact value. Keys added or removed by either side: none.
- **inert_reads**: the one key both sides edited, `tests/harness_headers.py` (534 entries at base). Branch adds `dev/audit/harnesses/eg_a4_wave_deltas.py`; main adds `dev/audit/harnesses/r9_ci2b_closures_merge.py`. Head holds **536 = branch ∪ main exactly** — 0 lost against the branch, 0 lost against main, 0 phantom paths present in neither. This is the case a naive value-equality test calls a defect and the set test proves is a union; both sides' EG-A4 and R9-CI-2b entries are in the merged table.
- **recorded**: main changed 0 keys vs base; the branch changed 3 (`tests/open_meteo.py`, `tests/ha_contract.py`, `tests/md_tables.mjs`); head equals the branch on all three.
- RESULT the semantic content of the delta in this file is **one entry, and it is main's**: comparing `def887d8` to the head by section, `closures` identical, `recorded` identical, `_comment` equal, and `inert_reads` differs on one key — `tests/harness_headers.py` gains `dev/audit/harnesses/r9_ci2b_closures_merge.py` (535 → 536), loses nothing. The rest of the textual diff (`git diff def887d8..a26f24285 -- tests/closures.json` rewrites the whole file) is **section ordering**: the branch's copy had `[recorded, closures, inert_reads]`, main and the head have the canonical `[closures, inert_reads, recorded]`. That is exactly R9-CI-2b's point — a table out of layout conflicts with every branch that re-records it — and the driver's write canonicalized it.
- RESULT no instrument the delta moved: the merge earned no metric movement. `closures` and `recorded` are byte-equal to the branch's own values at `def887d8`, so the three arch-score closure edits and the three `recorded` edits were already reviewed at the verdict head and are unchanged here; the single `inert_reads` addition is main's recording, not a widening of this PR's scope.

## Step 11 at this head (settled — the head was mid-flight when this seat started, so I waited rather than judging a partial table)

Polled from the commit's own `check-runs` API every 300 s from 12:51Z; **settled at 13:40Z**. `evidence/checkruns_settled.tsv` is that final read.

- 42 records, 39 distinct names, **all completed**; **zero non-green runs anywhere in the head's records** — no red, no pending, and the three names with more than one run (`pr-contract` 113822541049 + 113822757824, `arch-score` 113822541077 + 113822545830, `budget-raise-gate` 113822541502 + 113822542900) are success on both, so there is no red-then-green to misread.
- **All 17 required status contexts (ruleset 23698884, `main-protect-checks`) ran and are success. None is absent.** The four that were still running when I started are the ones that mattered: `closures` **113822628451 success**, `coverage` **113822544871 success**, `fast (3.14)` **113822544801 success**, `Analyze (python)` success.
- RESULT the driver's instruction is discharged: `tests/closure.py`'s gate — CI's `closures` lane — **ran at this head and is green**, which is the lane that owns the file the merge resolved (and `closures-autofix` reports `skipped`, i.e. nothing was owed to the bot — `ci-autofix.md`). `tests/entities.py`'s classification arms have no context of their own; they run inside `fast (3.14)`, which is success at this head, so the new tracked files this PR adds stay classified. `mutation` 113822544901 success, `arch-score` success on both runs — the check this PR makes required graded its own head.
- `nightly-status`, the one red at `def887d8` in round 4, is **success here**, so nothing in `## Red checks` needed re-answering; the reds the body does answer stay answered.
- Heavy lanes are cited, not re-run. My local re-take of them was limited to the seconds-scale owners the driver named: `tests/structure.py` (**STRUCTURE RATCHET PASSED**, rc=0), `layout_errors` (**[]**), and the phantom scan (**0**).
- RESULT nothing round 4 verified is invalidated: 26 of the 27 branch-owned files keep identical changed lines (the 27th is the table, measured above); `.gitattributes`, `tests/structure.py`, `tools/audit/archscore/*`, `tests/arch_score*.py`, `tests/layout.json` and `tests/run.sh` — what the round-4 base-run-gate plants and the entry-type class exercise — are not in the merge's 29 paths at all. Round 4's non-blocking wedge-risk count, which it re-derived at main `83f7ca558`, is re-taken here at `b2b6acd64`: `custom_components/` is still 91 × `100644` with **0** symlinks and **0** gitlinks at main and at this head, and `git log 83f7ca558..origin/main -- custom_components/` is empty, so the note still holds.
- GitHub: `mergeable=true`, `mergeable_state=blocked` (the approval, not a conflict), `draft=true` — marking ready stays the orchestrator's, and the code-owner/tvofi review this PR's own `## Approval` section names as owed is outstanding.

