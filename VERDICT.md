Fix review: blocked 5a119e8af148efbfb5ee3605323b75cd7af4a01c class-open: tools/policy/vendor/markdown-it.min.js, still unkeyed and undispositioned at round 4; re-cut owed

bus-nonce: e83542ededa392ce8703c448e9029197

## Round

This is review round 4. Round 3 blocked `ef895338c` as `class-open` on `tools/policy/vendor/markdown-it.min.js`. Since `ef895338c` the branch has two first-parent commits:
- `63789e164` merges `46686b677`, which changes two lines of the RCA record so they name the root-cause contract instead of its path.
- `5a119e8af` merges `origin/main`.

The PR's three-dot diff stat is the same as at round 3 (`ev/delta-since-round3.txt`). No commit answers the round-3 block.

## Block

**Step 6 (the class).** The class is still open on the seam round 3 named.
- At this head, `tools/policy/render_md.mjs:13` still loads `require('./vendor/markdown-it.min.js')`.
- `governance.yml` still restores `tools/policy/vendor` from the base, at lines 144, 1061 and 1171.
- Neither `ci_predict.py`, the record, nor the PR body names `markdown-it` or a `require()` load (`ev/seam-still-open.txt`).

Round 3's plant, re-run at this head, shows the miss. I edited only the vendored parser, in a commit on top of `5a119e8af` (`ev/plant-mdit.diff`). `ci_predict.py --base 5a119e8af --only graders` returned rc 0 in 0.59 s and ran no row (`ev/plant-mdit-predict.txt`).

**Re-cut, not repair.** This is the fourth round, so `fix-review.md` says `fixer.md` owes a re-cut, and the brief asked me to judge minimality. The branch has gone well past what the RCA record needs.
- Each round widened a load grammar: `named_loads` and `mjs_closure` grew to 462 added lines in `ci_predict.py`.
- Each review then found a restored file the grammar still could not see. Round 2 found `budget_raise_gate.py`; round 3 found `markdown-it.min.js`.
- A rule that guesses loads from spelling cannot close a class that is defined by the jobs' restore pathspecs.

Re-cut from current `origin/main` with these parts:
1. The record: cause, process state (c), cost test, figures re-taken at the new head.
2. One countermeasure that is closed by construction. Key the graders arm on the restore pathspecs that `pinned_runs` already derives from `governance.yml`. A diff touching any restored path runs that job's graders with the head copy against the base copy. This needs no load grammar. Alternatively, the record can decide not to build a countermeasure, with that cost test.
3. Its self-test, with `markdown-it.min.js` and `budget_raise_gate.py` as plant cases.

Drop `named_loads`, the `grader_gaps` load census and their exempt-site table unless the new key still needs them.

## Findings

- Class-open, the block: `tools/policy/vendor/markdown-it.min.js` is restored by `policy-docs`, `env-matrix` and `wave-script`, is loaded by `render_md.mjs` through `require()`, and is in no row's key. A head that edits the parser is predicted green, and CI then grades it with the base's parser. Re-cut as described under `## Block`. Carry: R10-RCA-PREPR-HEAD-GRADERS
- The PR body's head note is stale (step 7). `## Head note` still says "Round 3". `## Head` names `46686b67727e2e1db00c689ab15e8a9ab8e5a77d` as the head, with a merge-tree against `6493ea362`. The actual head is `5a119e8af148efbfb5ee3605323b75cd7af4a01c` (`ev/pr-body.md`). The re-cut's body must name its own head. Carry: R10-RCA-PREPR-HEAD-GRADERS
- The review packet still cannot render on a cloud seat. `review_packet.py render` refused `host-path` (home-directory in the body) under both `HOME=/root` and a neutral `HOME`, and wrote no packet. The cause is `ref_privacy.Identity.of_host` adding passwd's `/root`, combined with the bare-substring match; the body's own description of the defect contains `/root`. Under a non-root identity, `body_refusal` returns `None` (`ev/packet-refusal.txt`). This is the defect the body already carries; it is not this PR's. Carry: R10-RECORD-API-O1

## Evidence

- Head measured: `5a119e8af148efbfb5ee3605323b75cd7af4a01c` (`ev/HEAD.txt`). Its merge base equals `origin/main` `0265f524e`. `git diff merge-base...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Merge: `git merge-tree --write-tree origin/main 5a119e8af` exits 0, so there is no conflict (`ev/merge-tree.txt`). `VERSION`, the manifest, `RELEASE_NOTES.md` and the claim files are untouched.
- CI on this head, read from the check-runs API when this verdict was written (`ev/check-runs.txt`): 27 runs. Twelve are queued or in progress, including `policy-docs`, `env-matrix`, `mutation` and `pr-contract`'s prerequisites. None has concluded red. Step 11 is not judged, because the block does not depend on it.
- Review packet: not rendered (see the third finding). I ran the checks directly instead.
- Not re-taken this round: the body's figures (the 42-site, 10-file census, the key-hit counts and the 16.3 s and 292 s costs). The re-cut must re-take them, so I did not verify them here.
