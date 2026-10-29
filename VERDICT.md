Fix review: blocked f53ac2a3987e8dbf59ebedd0b708731d767aa5ab ci-red: required gate red only because arch-score died on gh HTTP 503 before scoring; re-run arch-score, then pr-contract and gate; the claim-file resolution delta is sound

bus-nonce: 22ad9a7d741e4dfaffbe0ae1014b26ad

## Round

Delta review (resolution delta of a main merge, fix-review.md step 12) after the merge verdict at c9bf05dfe0a1b29eb18dd444a8a32983ea781d77. Scope: merge f53ac2a3 = c9bf05df + origin/main 3042dcd4 only.

## Block

The required context `gate` is red at f53ac2a3987e8dbf59ebedd0b708731d767aa5ab, and that is the only thing between this head and a `merge` verdict. The red does not belong to this PR's content:

- `arch-score / arch-score`: its latest run (job 123519886484) failed at the step that reads the PR itself, `gh: HTTP 503`, before any scoring ran. Two earlier runs on this same head (123520033928, 123520051858) concluded success. It died before any test body ran, so the one re-run is warranted.
- `pr-contract / pr-contract` (123520160162) started after that red landed. Its only error is that the body's `## Red checks` does not name `arch-score / arch-score`. Its other steps were clean: preflight clean, FIGURES 14 resolved / 0 refused, CARRY-AUDIT 8 routed / 0 unrouted.
- `gate` (123520707738) fails on exactly those two.

Remedy, with no code or body change: re-run `arch-score / arch-score`, then `pr-contract` and `gate` on this head. If arch-score comes back green, this delta qualifies for `merge` on the evidence below. If arch-score fails a second time, that failure is real and the body owes it a `## Red checks` answer. No line of tests/golden/claimed_drift.txt needs to change.

## Findings

- The carry predicate `tools/pr/app_approve.sh --carry`, which `tools/audit/seat/review_carry.py` asks, refused this merge wrongly. Its claim-file test takes the sorted set-union of both parents' lines (`want = sort -u(parent1 + parent2)`). It is not a three-way union. A branch line deletion that main never touched since the merge base therefore reads as a "resolution other than the union". The case here: c9bf05df had deliberately deleted main's R10-HOUSE-GRADE and R10-BUFFER-STORE claim lines and restored the six suspended may-drift entries (commits 3f33c6796 and 535015a87, both inside the reviewed head). Main 3042dcd4 left the file byte-identical to the merge base 66974d47. So git's (and the claimnotes driver's) correct result is the branch's file, byte-identical to c9bf05df, but the predicate wants main's deleted lines back. To fix it, compare against the three-way result: base lines kept unless a side deleted them, plus each side's added lines. Then a merge whose claim file equals one parent's, while the other parent equals the merge base, carries. Until that fix, every branch that edits rather than appends a claim line is re-reviewed after each main merge. Carry: R10-REVIEW-CARRY

## Evidence

- Head measured: f53ac2a3987e8dbf59ebedd0b708731d767aa5ab (parents c9bf05df, 3042dcd4). It is still the PR head at verdict time (pulls API).
- Claim files, reconstructed at merge base 66974d47 (= merge-base(c9bf05df, 3042dcd4)), at both parents and at the head (ev/claimed_drift.{B,P1,P2,H}.txt):
  - Main side: 3042dcd4's tests/golden/claimed_drift.txt is byte-identical to the merge base (empty diff). card_claimed_drift.txt is identical at all four points.
  - Branch side: c9bf05df differs from the base by the R10-COP-GATE note (9 comment lines), the five coord_* claims rewritten from R10-HOUSE-GRADE to R10-COP-GATE reasons, the nine R10-BUFFER-STORE claims removed, and the six suspended may-drift entries restored verbatim. All of it was in the head the previous merge verdict measured.
  - Head f53ac2a3: byte-identical to c9bf05df for both claim files. That is the correct three-way result, since only the branch touched the file. It is also exactly the automatic merge: `git merge-tree --write-tree` of the two parents with the drivers installed gives tree 979206f0, and `git diff 979206f0 f53ac2a3` is empty. No line was hand-written by the merge.
  - The lines main still carries are not inherited into the branch (claim-files.md: a line excuses only the diff that wrote it). The branch's list names only its own R10-COP-GATE fixtures.
- Rule-3 checks at the head:
  - `claims-for: 7.0.5` equals VERSION 7.0.5. VERSION, the manifest and the RELEASE_NOTES heading are untouched by the delta (prepr --version-edit in CI: "no version edit").
  - The intersection of the bare claims (coord_all_features, coord_dhw, coord_grid_fee, coord_minimal, coord_two_zone) with the `# may-drift:` names is empty.
  - `PYTHONPATH=tests/hastub python3 tests/env_drift.py --claims-only origin/main` printed `claims hygiene: origin/main ok`, rc 0 (ev/env_drift_claims_only.txt).
- Branch's own diff unchanged: `git diff 66974d47 c9bf05df` and `git diff 3042dcd4 f53ac2a3` are equal with index and hunk headers stripped (45 files, +655/-117 each; ev/branch-diff-equal.txt). The delta brings in no branch-authored change.
- review_carry.py c9bf05df -> f53ac2a3: `FRESH-REVIEW`, reason "resolves tests/golden/claimed_drift.txt to something other than the union of its parents" (ev/review_carry.txt). It is a false refusal, explained under Findings; the delta was reviewed here by hand as the brief asked.
- Mergeability: `git merge-tree --write-tree origin/main f53ac2a3` exit 0 against origin/main 88c6ad5b (3 commits ahead of the PR base), with no conflict (ev/merge-tree-origin-main.txt).
- CI on this head, from the check-runs API (ev/check-runs.tsv, ev/ci-log-excerpts.txt): red are `arch-score / arch-score` (latest run, HTTP 503), `pr-contract / pr-contract` (latest run, consequent), `gate` (x3, consequent) and `tests / nightly-status`. `tests / nightly-status` reads main's nightly, and this diff does not reach what it reads. It is not this PR's (fix-review.md rule 11), but the body's `## Red checks` must still name it once pr-contract re-runs, as that run printed. Every other completed run is success or skipped, and none was still running.
- No mutation was planted: the delta authors no code line, so there is nothing to mutate. Heavy runs were cited, not re-run.
- Not re-derived: figures in the body about the fix itself. They were measured at c9bf05df by the previous verdict and are unaffected, since the branch diff is equal.
