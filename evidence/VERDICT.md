Fix review: merge 271373ad592134828d25ed6bd080d9f48d34b177
bus-nonce: f52fba0ebe1ce1e8bcc3532af3a22fd1

Round: the repair round after `root-cause-unanswered` at 72b696d96 (a repair, not a
re-cut; the fix's substance was established at bc0488018/72b696d96 and is
re-measured below, unchanged).

## What I measured (fresh worktree at 271373ad5, venv-ci 3.14.7)

1. arch-score gate, base 7cd5a588c (the body's merge base, unchanged):
   `Architecture score: dS +0.0073 IMPROVES / coord_footprint 2586 -> 2573 /
   PASS: dS +0.0073 IMPROVES, no gate metric rose` -- the body's line exactly.
   shared_inplace_writes measured at head = 22 (inplace 22, borrow 0), and the
   site list carries no `ledger.py ... _month_reports` entry: the three sites
   the reviewed head added are gone. seam_map.json:172 `_roll_month: "grid"`.
   Payment earned, not instrument-shaped: the same gate at the red head
   96eaf4a00 reproduces the body's quoted failure verbatim
   (`dS -0.9549 WORSENS (inadmissible: shared_inplace_writes 22->25)`), so the
   rise was real and the code, not the instrument, removed it. The seam
   recording (762 -> 756) carries its reason in b19106207's message;
   `tests/structure.py`: STRUCTURE RATCHET PASSED, seam_cut_total=756 <= 756,
   max_class_loc=8745 <= 8745.
2. Baselines: `python3 tests/entities.py` -- `ALL 2250 ENTITY CHECKS PASSED`.
   `python3 tests/features.py` at head reaches its summary:
   `1 of 4005 FEATURE CHECKS FAILED` -- R9-F2.1 P3, the BLAS margin, with the
   body's exact figures (shipped 110.4366, seeded 110.1297); not a block on
   this macOS box.
3. ## Unpinned sites: ci_predict at the head lists 39 sites; the body
   dispositioned all 39 (two written `CMP_BOUND*2` over double-counted
   inventory rows). Five sampled and DRIVEN, each restored clean:
   - ledger.py:320 RETURN_DEL (M1): 4 UX-6 checks fail -- the body's four.
   - ledger.py:333 RETURN_DEL: 2 fail, both checks the body names.
   - accuracy.py:50 CONST (PROMISE_HOUR=23): 2 named UX-6 checks fail
     ("the promise is the first midnight plan's", "the next day replays").
     Nuance, not a defect: the specific check the body names for :50 ("a plan
     solved after the midnight hour is not the day's promise") did not fail
     under this constant value; the body does not claim these killed (the pin
     lane's drive is owed and stated as owed), and the site is live and pinned
     by the block.
   - accuracy.py:231 GUARD_OFF: the run breaks (TypeError on the None path);
     the named null-control check exercises it.
   - ledger.py:440 CLAMP_DROP: `ALL 19 FEATURES BLOCK PASSED` -- the block
     reads flat, exactly the body's disposition: a genuine survivor_triage
     candidate, recorded as owed, not faked.
   M0 at head: `ALL 19 FEATURES BLOCK PASSED`.
4. Ancestry reds: I re-ran prepr's own enumeration (same rev-list, same
   REDS_JQ, same pr-contract exclusion) over origin/main...origin/fix/r9-ux-6:
   exactly the seven names the body answers (arch-score, closures,
   coverage-ratchet, fast (3.14), mutation, mutation-autofix,
   nightly-ha (stable)), each named and answered in ## Red checks with head,
   output and repair. Spot-checks against the check-runs API: arch-score
   failure at all three heads (10b4ae172, 72b696d96, 96eaf4a00) with its
   quoted line reproduced by my gate run at 96eaf4a00; nightly-ha (stable)
   failure only at 96eaf4a00, matching the body's heads. CI has since run at
   the publishing head: arch-score green (matches my gate), pr-contract green,
   and a mutation red whose cause set (the 39 sites' dispositions plus the
   repaired baseline) the body's mutation entry already names and answers.
5. Substance unchanged: the fixture month at merge base 7cd5a588c gives
   `_freeze_month_report` total_sek=709.5 with no basis; at the head the same
   fixture gives 194.5 with basis ['spot','grid_fee','immersion','wear'] --
   the earlier rounds' figures, byte-for-byte.
6. VERSION, manifest, RELEASE_NOTES untouched; coord_* golden fixtures gained
   only new keys and each is claimed in claimed_drift.txt; worktree left
   clean after every mutant.

RESULT gate PASS dS +0.0073; shared_inplace_writes 22; entities 2250/2250;
features 4004/4005 (BLAS margin only); UX-6 block 19/19 at M0; ancestry: 7/7
answered; dispositions 39/39 listed, 5/5 sampled backed by measurements.
