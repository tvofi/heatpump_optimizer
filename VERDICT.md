Fix review: merge 0cf78fa5b147d4ef6638609e03b45adec0ea1b0a

bus-nonce: 83340fd7ad1b5e3c29857a0a5d2940fb

## Evidence

- Round 1, full scope (first review of this PR). Reviewed head 0cf78fa5b147d4ef6638609e03b45adec0ea1b0a, merge base 83b9012d61eb9dba11c265cf987dd1d5960c8c96; `git diff <base>...origin/main -- dev/governance/roles/` is empty, so the contract read is current.
- Merge with main: `git merge-tree --write-tree origin/main <head>` exits 0 (tree 6a6cbfa529ec), so there is no conflict.
- Re-derivation of the body's null control (ev/drift-base.txt, ev/drift-head.txt): `selftest_scope.drift(committed table, artifact 14404437877 steps, workflow_steps())` at the base gives 33 refusals, all UNDER-SCOPED, with no STALE, UNMEASURED, UNRECORDED or EXTRA line. At the head it gives 0 refusals and 0 notes. CI's own count on main's red job 134592553541 (run 44242125570, 7c2f4c30) is `127 gated step(s), 33 refusal(s)` (ev/ci-main-red-log.txt), which matches.
- Recipe re-run (ev/rewrite-cmp.txt): `write_table(union_entries(base table, artifact))` at the base checkout is byte-identical to the head's tools/ci/selftest_closures.json. The 67 added and 120 removed lines in that file come from the recipe; nothing was edited by hand. The removed lines are the per-card `instruments/*.md` paths, which `collapse` folds into `tools/audit/seat/instruments/**`, and owner-only-launcher's four probes, which `compact_probes` drops because the measured `dirs` `['.']` answers them.
- `selftest_scope.py static` at the head: 127 gated steps, 0 problems (ev/static-head.txt).
- Targeted mutants on the table at the head, each scored against the artifact (ev/mutants.txt). The unmutated control gives 0 refusals. Every mutant was killed:
  - M1, scopes.json removed from plan-public: 1 refusal.
  - M2, owner-only-launcher `dirs` emptied: 1 refusal.
  - M3, owner_only.py removed from open-pr: 1 refusal.
  - M4, leak_detectors.py removed from pr-args: 1 refusal.
  - M5, `instruments/**` removed: 3 refusals.
  No mutant survived.
- Class: the enumeration rule is `drift` over every gated step. At the head it returns nothing, so none of the 33 seams is left open.
- No VERSION file, manifest version, release-notes heading or claim file is touched (ev/untouched.txt). No golden fixture or budget moves, so `env_drift` has nothing to compare.
- Artifact provenance (ev/artifact-meta.txt): the API reports artifact 14404437877 with name `selftest-closures`, workflow run 44242125570, head_sha 7c2f4c30cab5, size 52617 B. I could not compare its bytes with the inbox copy (commit fddace05) because this seat's proxy refused the zip download from blob storage. The match of the 33 refusals to CI's count is the indirect check.
- Live checks: `merge_train.py classify 0cf78fa5… --pr 3718` returned rc=0, `GREEN … pending: none red: none`, at 15:13:13Z (ev/classify.txt and ev/classify-log.txt). `tests / nightly-status` is red in the review packet but is not in the `owed-reds` set (ev/owed-reds.txt), so it is neither answered nor a block. I re-read the head before pushing: refs/pull/3718/head is still 0cf78fa5b147d4ef6638609e03b45adec0ea1b0a.
- Notes (paperwork, non-blocking):
  - Note: body-stale: the body says tools/ci/selftest_closures.json is the only file changed, but the head also adds dev/programme/delivery/3718.md through the record commit. The `## Head` section also carries a stray `2cb38f075d…` line, which is the commit prepr ran at. The only difference between that commit and the head is the delivery row. Carry: dismissed: paperwork on this PR's own body, settled by this note
