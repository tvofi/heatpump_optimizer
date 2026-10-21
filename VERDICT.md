Fix review: merge a85e97a7325fc48767ba5abb1ec4c6fb92506939

Round 1 (no earlier Fix review verdict on #2521). Measured head a85e97a7325fc48767ba5abb1ec4c6fb92506939, re-read as the PR head and branch tip just before writing. Baseline is the merge base 289426c1f; the body's base df6ca4bc6 was also exported for the F3 cross-check. Interpreter: the seat venv /opt/hpo/venv-ci (Python 3.14.7). The container's system Python 3.11 cannot parse tests/entities.py, so under it comment_symbols drops that file's tokens and F3 reads 9 instead of 6, and service_count_comments dies on voluptuous. That is this container's environment, not the PR. Every figure below was taken with the venv.

1 Mutation proof (ev/mutation_proof.txt). At the head, each production file was replaced by its merge-base copy, doc_claims was run, and the file was restored. README.md, docs/configuration.md and docs/setup.md each fail 2 of 183 (the UI-label check, plus the existing check that the setup-flow diagrams are identical). docs/dashboard-card.md fails 2 (the placeholder check and its null control). __init__.py fails 1 (the registry count). docs/index.html fails 1 (the PNG header). All of this matches the body. Failing first: the head's tests/doc_claims.py on the base tree gives 5 of 183 FAILED; the head gives ALL 183 checks PASSED (ev/null_controls_and_failing_first.txt).
RESULT mutation_files_reverted=6 all_fail=6
2 Finder harnesses at both ends (ev/finder_harness_both_ends.txt). These are the committed main copies, and web_claims.py comes from handoff/audit-r10-d6-web 39909e462 (sha1 5ec0c0a7, the same as the body).
RESULT ui_labels.mismatches base=5 head=0
RESULT service_count_comments.stale_count_statements base=4 head=0 (registered_actions=13 at both)
RESULT web_claims.img_dim_mismatch base=1 head=0 (claims false 1 -> 0)
RESULT card_banner.banner_mismatch base=1 head=AttributeError -- the body discloses this: the regex expects a numeric version and the sample now has none. I checked the companion myself: the doc_claims banner arm is red at base and green at head.
RESULT stale_structure_refs retired_key_claims base=3 head=2, lint_missed_stale_counts 1 at both (the remainder is D7.md, which is policy)
3 Null controls at base: sweep_i5 --null null_stale=0; card_banner --perturb banner_mismatch=0; web_claims --perturb-dims img_dim_mismatch=0; sweep_i5 --perturb stale_W3 2->3. The PR's four in-memory controls pass at the head inside the 183.
4 Claims: no golden or claim file is touched (ev/merge_tree_and_untouched.txt), and env_drift --claims-only origin/main reports ok.
5 VERSION, the manifest and RELEASE_NOTES are untouched. The diff is empty, and pr-contract prints "no version edit".
6 Class: I ran the body's rule (STALE lines of sweep_i5.py, sha1 7e411536) in a checkout. Base: stale_total=26 (F1 5, F2 1, F3 6, F4 4, F5 4, W1 1, W2 3, W3 2). Head: 12 (F3 6, F5 3, W2 2, W3 1). That is the body's archive figures (22 -> 9) plus the F5 rows the body says only a checkout prints. Every seam left at the head is dispositioned in the body. The W4 SEAM rows (dashboard-card.md '24 months', '30 samples') are not STALE lines, so the rule does not count them.
Attacks at the head (ev/class_attack_plants.txt):
- changing services.py to say 'fourteen services' fires the count check;
- a bold '(advanced)' suffix fires the label check;
- 'Add integration -> Heat Pump Optimizer' in README fires it;
- a wrong height on advisor-light.png fires the PNG check;
- a literal v7.0.2 in the banner fires the banner check.
The brief asked for image sizes to be checked on every tracked page. The arm narrows that to published pages, and that loses nothing today: all 1365 tracked .md/.html files hold 10 sized <img> tags, and the published pages hold the same 10. Mismatches are 0 in both (ev/class_attack_images.txt).
7 The body names a85e97a73 as the head and describes it as an automatic main merge over the code head cc42450a4.
8 Figures re-derived: mutation counts, 183 checks, finder metrics, 28 tracked docs/img PNGs, 10 opened, and the sweep counts (see 6). One body figure does not reproduce. The body quotes carry_audit at "3 finding item(s)", but against this body it prints 4 items, 4 routed, rc 0, both locally and in CI (ev/carry_audit.txt). The body grew a fourth, dismissed Forward-carry item. Only the count is stale; the routing holds. Carry: dismissed: one count in the body went stale when an item was added; the instrument passes
entities.py at the head prints 2375 checks, against the body's 2360 at cc42450a4. The difference comes from the main merge.
9 Every harness the body names is committed, and I built none of my own beyond the readers in ev/ (imgscan.py and pngset.py). Those import doc_claims' own functions.
10 Forward-carry, opened at roster tip 2c76c3128:
- The D7/D9 lines of #2222 are in R10-BRIEFS-FOLD's brief string.
- D5-s3-01 is in R10-CURRENCY's brief ("Also take D5-s3-01").
- The tests/README.md:272 k1725 correction is in R10-BRIEFS-FOLD's carry list ("From #2521: ...", appended by roster_edit 617ce1316). The path it names does not exist on main, and dev/audit/harnesses/k1725_blas_kernel_gap.py does exist.
Note: that last carry is in the group's carry list but not yet copied into its brief string, as that brief's own heading does for the R10-GATE-YIELD item. The body also names the roster ref but no roster SHA. Carry: R10-BRIEFS-FOLD
11 CI (ev/ci_check_runs.txt): all 49 runs have concluded. The only red is nightly-status, which grades main and is answered in the body; this diff does not reach what it reads. The latest pr-contract (started 13:33:36Z, after every other run concluded) is green, with no refusal. The body answers the earlier pr-contract red (an unrouted item) by naming carry_audit as the cheaper detector, and the earlier local entities failure as already caught.
12 The head was unchanged at the start and the end of the review: ls-remote and the PR API both return a85e97a73.
13 git merge-tree --write-tree origin/main(5d433771a) a85e97a73 gives rc 0, tree f07246d1. On that merged tree doc_claims passes all 183 checks, img_dim_mismatch=0, ui_labels=0 and stale_count_statements=0 (ev/merged_tree_checks.txt).
14 Earned movement: the 10 PNGs added to INERT_EXCEPT, the 10 doc_claims PNG reads recorded in closures.json and the 10 PNGs the arm opens are the same set (ev/closure_png_sets.txt). If the arm is removed, nothing opens them. No budget or score file moves. structure.py passes; closure selftest passes all 124; select --diff gives MODE: FULL.
15 The added lines are test arms in doc_claims.py's existing R.check idiom plus comment edits. There is no architect note and no breach.
Local cheap checks at the head (ev/cheap_checks_head.txt), all rc 0: structure, entities (2375), closure selftest, env_drift claims, deployment_shape, validate, harness_headers, md_tables, rules_sync.
Non-blocking: a label written in backticks (`Enter thermal values directly (expert)`) gets past both the new arm and the finder's ui_labels. That form is outside the finding's stated rule (bold or quoted), and there are 0 instances in the tree. Carry: dismissed: outside the finding's seam rule, and the finder harness has the same reach

bus-nonce: 7b4fa5ee6cfb88d3dab2c78e78093b49
