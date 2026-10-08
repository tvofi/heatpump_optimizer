Fix review: merge a102be643fbdc76dc9886536b46310202e0a9a56

bus-nonce: 8298f0149d1ec76b9f883a103ea70eaf

Round 2. PR #2041 (R9-DBG-2, closes #1940). The measured head is `a102be643fbdc76dc9886536b46310202e0a9a56`: fixer code head `a5e96956` plus origin/main `6b91e238`. The body's `## Head` names it, and it was still the live head when I posted. I worked from a fresh detached worktree at the head. Evidence: `/Users/timmalmstrom/hpo-seats/review-2041/evidence-r2`. Round 1's evidence: `/Users/timmalmstrom/hpo-seats/review-2041/evidence`.

## Round-1 blockers: resolved

1. **The `fast (3.14)` red from the harness depth seam.** `1a6ccbc5` replaces `parents[3]` with the canonical `repo_root` walk-up. Locally, `depth_root_seams()` returns `[]`. CI `fast (3.14)` at the head is **success** (job 113167219786): `MODE: SCOPED -- 23 script(s) run`, `ALL 109 HARNESS HEADER CHECKS PASSED`, `ALL 58 DEBUG COLLECT CHECKS PASSED`. The body's `## Red checks` now names the round-1 red and answers it: the detector is `tests/harness_headers.py` itself, and the gap was the seat not re-running it after the move.
2. **The claim that the download stays under the cap.** `capped()` now measures `download_bytes(bundle) + DOWNLOAD_HEADROOM_BYTES`. `download_bytes` is `json.dumps({"data": {"debug": bundle}}, indent=2)`, which is HA 2025.2.0's writer at the bundle's real depth. I re-ran my round-1 size instrument against the new measure (`download_size.py`, my own, not the finder's). The largest week repeat that `capped()` keeps inline is 23, with `capped_measure=8206065` against `cap=8388608`. The full download payload built around it comes to `download_indent2_bytes=7947300`, `within_cap=True`. That payload is HA's sections plus `data.{config, coordinator, domain, debug}`, with the coordinator snapshot counted a second time as the real file does. At repeat 24, `capped()` returns the summary. Round 1's figure for the same measurement was 13069459 B, 1.58x the cap. A16 now judges `_async_get_json_file_response` when it is importable and otherwise `json.dumps(indent=2, ExtendedJSONEncoder)`, printing which writer ran. Its inline arm now sits 512 rows under the cap instead of using 10 rows. The container half runs on schedule or dispatch only. The body says it was smoke-run under the stub with a stand-in encoder, and I did not run it.

## Verified (RESULT lines)

- Targeted mutants on the new measure, against `tests/debug_collect.py`. `RESULT targeted_old_compact_measure` (`size = len(_dumps(bundle).encode())`) gives `killed=True`. `RESULT targeted_no_headroom` (headroom dropped) gives `killed=True`. Both fail `a bundle at the cap is carried inline, and one byte over it is the summary`.
- Ledger pins: I replayed all 16 committed `debugger.py` pins, the 15 from round 1 plus `download_bytes RETURN_DEL 74c13f7a`, with my round-1 `pin_replay.py` (`pin_replay.out`). `RESULT null_unmutated rc=0`, `RESULT null_comment rc=0`, and **16/16 killed=True**. CI `mutation` at the head (job 113167219841): `4670 unpinned site(s) of 5855 candidate sites, 4670 at the ratchet base 6b91e238…; the ledger agrees with the deterministic inventory`, 3 sampled mutants killed by debug_collect.py, `MUTATION TABLE PASSED`.
- Finder's pricing harness at the head (`price-head.txt`), whose measure now matches `capped()`. `--repeat 1` gives `selftest_total_ms=11.9`, `bundle_bytes=588243`, `bundle_inline=1`. `--repeat 23` gives `bundle_bytes=5454298`, `inline=1`. `--repeat 40` gives `bundle_bytes=9214433`, `inline=0`. Every total is under the 900000 ms budget. Round 1's null at the merge base (`RESULT selftests=absent`) stands.
- Read-only and the 15-minute bound: unchanged since round 1, where I checked them by reading the code (`async_simulate` writes nothing under `limited=False`; each check runs under `asyncio.timeout` on what is left; once nothing is left the rest are skipped).
- `git merge-tree --write-tree origin/main HEAD` gives rc 0. VERSION, the manifest and the release notes are untouched, and so are the claim files.

## Red checks at the head (step 11)

- **`closures` (job 113167290472) and `closures-autofix` (job 113182278842) are main's, not this branch's.** The only refusal is `INERT READS UNDER-APPROXIMATED … tests/harness_headers.py: dev/audit/harnesses/r9_ro12_batch_mutants.sh`. That file is #2044's (last commit `8911527f`) and is not in this diff. Main `6b91e238`'s own `closures` (job 113159208937) refuses with the identical line (`main-closures-excerpt.txt`). The recording does not refuse this PR's hand-added `harness_headers.py → r9_dbg2_selftest_price.py` entry, so that entry is consistent with CI's recording at this head. Under `defect-root-cause.md`'s enforcement, the trigger falls on "the fixer whose branch turned a check red", and this branch did not. **`closures` is required, so this PR cannot merge until main's `inert_reads` gap for `r9_ro12_batch_mutants.sh` is repaired on main**; that is the orchestrator's.
- `delivery-status` (job 113167219953) grades main. The diff adds only its own row.
- `budget-raise-gate`: the cancelled twin 113167218406 has a success twin, 113167223693.

## Residual (not blocking)

`DOWNLOAD_HEADROOM_BYTES` (256 KiB) covers the coordinator snapshot, which appears a second time at `data.coordinator`. The synthetic week's snapshot is 3150 B at indent=2. A real install's snapshot size is not measured here. The pre-study left real-install bundle size owed by DBG-1's body.
