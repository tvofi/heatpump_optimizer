Fix review: merge 5a8b4e65fa92e3ddd3123b8d69b6ffd39438df73

bus-nonce: b05c7a05eb6b962108aa4d6cb6ca582d

Round 1 (full). Head measured: 5a8b4e65fa92e3ddd3123b8d69b6ffd39438df73; merge-tree with origin/main clean.
RESULT: carry predicate: only review_carry.py rc 0 moves C8's grade; the branch-diff decision is review_carry's unchanged L6 predicate, so no carry crosses a changed branch-authored diff.
RESULT: real ranges: #3925 129cc121..d50ab75e (bot mutation pin) CARRY; this PR's 72d1774e..55e2f0d8 (own-file edit) FRESH-REVIEW, the null control on a real range.
RESULT: C8 grades the carried head and refuses a concluded red there (self-test arm; mutant D, grading hsha, killed).
RESULT: mutants: always-carry killed (4 FAILs incl. both null controls); C8-at-hsha killed; tick oldest-record killed. bus.sh self-test 249 at head, same 28 macOS-only FAILs as base 245, none new.

Note: test-gap: mutant rc!=1 (undecidable range carries) survives; the body claims undecidable grades the verdict head but no arm drives rc 2. Carry: dismissed: rc 2 after a successful fetch of both shas is near-unreachable, C8 still grades the live head, and merge_train's admit_add re-asks app_approve.sh --carry.
Note: test-gap: dropping the live!=hsha guard survives; Carry: dismissed: it grades the same sha, only a cosmetic self-carry record follows.
Note: c8-pending: a carried head with pending checks posts a merge verdict whose own head had a concluded red. Carry: dismissed: C8 refuses only a concluded red by design, required checks still gate the merge.
Note: root-cause-red: gate runs 45962093208 and 45963427833 failed with gate.py's sibling deferral, run 45962092708 still being judged; its gate is success and classify reads red: none. Carry: dismissed: deferral by a superseded duplicate run, not a defect of this diff.
Note: nightly-status red: not in owed-reds, diff outside its reporter inputs. Carry: dismissed: not owed.
