Fix review: blocked 7f91e684293abb4ba0276d8b16eb7010448d9fff body-head-stale: the body's Head names feb44bd88, the head is 7f91e684 (the record row commit), which does not carry, and policy_lint --pr-body refuses the body at this head

bus-nonce: c795bc653a9679064f57d1ff06d84ae6

## Block

- The `## Head` section names `feb44bd885e566535671469ee95c2b0556676290`. The live head is `7f91e684293abb4ba0276d8b16eb7010448d9fff` ("record: the delivery row for #2758", which adds only `dev/programme/delivery/2758.md`). `tools/pr/app_approve.sh --carry feb44bd88 7f91e684 origin/main` prints `CARRY: no ... is a commit of the branch's own` (ev/carry.txt), so fix-review.md step 7 fails.
- `node tools/policy/policy_lint.mjs --pr-body <live body> --head 7f91e684...` exits 1 with "`## Head` does not name 7f91e68, which is the head this ran on" (ev/pr_body_lint.txt). This is the check `pr-contract` runs, so the body will be refused at this head. No `pr-contract` run was listed among the head's 32 check runs when I read them.
- The repair is a body edit and needs no tree change. Edit `## Head` to name `7f91e684293abb4ba0276d8b16eb7010448d9fff`, as #2744's body did for its record commit 54ee10354. Then a fresh `pr-contract` event is needed. Everything else below holds at this head, so a re-review can be a delta check of the body alone.

## Findings

- The body's `## Head` is stale, as set out under Block. This is the orchestrator's to repair, by an edit to the PR body. Carry: dismissed: settled by this block; the repair is the body edit named above, and nothing passes to a later stage.

## Evidence

- Round: first review of #2758. The head I measured is `7f91e684293abb4ba0276d8b16eb7010448d9fff` (ev/HEAD.txt), and it was still the PR head when I read it. The role contract is current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty (ev/roles_current.txt).
- Merge: `git merge-tree --write-tree origin/main <head>`, with origin/main at 2636ce9e9, exits 0 with tree f430363a2 (ev/merge_tree.txt).
- Three-dot diff from merge base a260e5630, which matches the body: 2 files and 21 insertions, namely `dev/programme/triage/s6-batch15.md` (+20) and `dev/programme/delivery/2758.md` (+1). VERSION, the manifest and RELEASE_NOTES.md are untouched (ev/diff3dot.txt). The delivery row is in the same shape as the merged rows (for example 2752.md): `- [#2758](...) — **open**, <title>`.
- RESULT `roster_edit.ruling_verdict` at head: P84 ACCEPT and P99 None, which reproduces the body's null control. `triage_refusal` on a carry citing `s6-batch15.md#P84` returns None, so the gate accepts it (ev/ruling.txt).
- RESULT figure: the body's `rg` figure gives `1 ACCEPT`, which matches. The ruling's "4174-line file" is right: `wc -l tools/audit/seat/merge_train.py` gives 4174 (ev/figures.txt).
- The ruling's tree claims were read at the head. `policy_gate` is merge_train.py step 5. It requires the owner's APPROVED review at the head, citing a mandate by `MANDATE_CITE`, re-read at the merge with `MANDATE_COVERS_POLICY = ("all",)`. The `approve` step (step 6) posts only on app_approve's code-owned refusal. Its body reads "under {self.mandate}" (line 1281), a free-text label that `MANDATE_CITE` does not match unless the label itself carries the word "mandate". `merge_pr.sh` owner mode posts "under mandate <id>", which `MANDATE_CITE` does match. All of this is as stated.
- The corpus-filter claim reproduces. A probe of 6 paths printed only `CLAUDE.md` and `dev/governance/roles/fixer.md`, so the triage file and the delivery row are non-policy and this PR lands on-train (ev/corpus_filter.txt).
- The authority claim is consistent with the gates. The carried post would be judged by `MANDATE_COVERS_POLICY` (`all`), which is narrower than merge_pr.sh's `MANDATE_COVERS_CODE_OWNED` (`code-owned`, `all`). The ruling therefore widens no authority, and it keeps `policy_gate` as the judge at the merge.
- The triage ruling matches the finding as the file states it: hand-rolled shell standing in for the train for policy heads, narrowed to the train posting the citing approval, and `merge_par.py` rejected. I could not re-derive the 3 instances, or the "about 45 minutes", because the source is the out-of-tree s6 `proposals.md` `## V19`. The ruling says itself that these were not re-counted.
- The mutation proof is n/a, because the diff writes no code. The carry text was not re-linted by `brief_lint.mjs`. I did not reproduce the body's null control on the scratch roster.
- CI at the head, read from the check-runs API across all 32 runs: no run concluded failure. `closures`, `browser`, `coverage`, `env-matrix` and `instrument-self-tests` were still in progress. The rest were success or skipped. The body's `## Red checks: none` holds so far.
