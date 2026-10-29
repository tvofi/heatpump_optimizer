Fix review: blocked ef895338c0603c64adcf7ed6b2b25e06c5648b83 class-open: tools/policy/vendor/markdown-it.min.js, a restored file render_md.mjs loads with require(), outside every row's key and named_loads' grammar

bus-nonce: e7f016c03a11078336cb8db2a086745d

## Round

Review round 3. Round 2 blocked `38422dd15` `class-open` on `budget_raise_gate.py`. The repair is `c8eb2dc51` and `282496dce`, with the record updated in `7d3b78914` and `0ca059dee`. The round-2 seam is closed. One more seam of the same class is open.

## Block

Step 6 (open the class). Round 3's record defines the class as "every restored file a row's grader loads" (record, "Round 3: what a grader names keys it"). Its enumeration rule, `named_loads`, matches only two things: a quoted `.mjs`/`.py`/`.sh` path, or a `path.join` of single-quoted literals. A load written any other way is invisible both to the key (`mjs_closure`) and to the gap census (`grader_gaps`). The census uses the same `named_loads`, so it cannot report what it cannot see.

One such seam at this head:
- `tools/policy/render_md.mjs:13` loads the vendored parser with `const MarkdownIt = require('./vendor/markdown-it.min.js')` (ev/render_md-require.txt). `render_md.mjs` is in the keys of CORPUS, WAVE CHECK, RULES SYNC and LANE SELF-TEST. The `.js` file is in none of them, because `mjs_closure` skips any path that does not end in `.mjs`/`.py`/`.sh` (ev/class-probe.txt; I ran `mjs_closure` and `grader_hit` per row).
- `policy-docs`, `env-matrix` and `wave-script` each restore `tools/policy/vendor` (and `.claude/workflows/vendor`) from the base, by explicit pathspec in `agreement_py.restore_specs`. CI therefore always grades with the base's parser.
- Plant, a commit on top of this head (ev/plant-mdit.diff), editing only `tools/policy/vendor/markdown-it.min.js`: `ci_predict.py --base <head> --only graders` returns rc 0 in 0.5 s and runs no row (ev/plant-mdit-predict.txt).
- Control (ev/control-rendermd.diff): the same one-line edit to `render_md.mjs` keys the rows and runs them, rc 0 in 28 s (ev/control-rendermd-predict.txt). The predictor runs graders for the parser's loader but not for the parser.

A head that bumps the vendored parser and leans on its new parse in the corpus is predicted green. CI then grades it with the base's parser. That is the #2916 shape on a file the jobs restore deliberately. Neither the diff, the record's 42-site seam table, nor the body dispositions it.

Repair, either of:
- widen `named_loads` and `mjs_closure` to `require()`/`createRequire` loads and to any restored extension (`.js`), with a `grader_key_self_test` case that keys `markdown-it.min.js` under CORPUS; or
- disposition the seam with a reason in the record and the body. Zero round-10 instances plus a cost test would count, as in round 2.

My probe is my own instrument, not the finder's (step 9): `ev/classprobe.py`. It lists every tracked, restored basename that appears on any line of any key source, minus the key and `named_loads`' hits, giving 409 lines. I triaged the candidates by hand. Every other one I opened is a comment, a message string or a `field_coverage` table key, not a load. A repo-wide grep finds `require(`/`createRequire` only in `render_md.mjs` (and `require('fs')`). I did not read each of the 409 lines individually.

## Findings

- Class-open: `tools/policy/vendor/markdown-it.min.js` is loaded by `render_md.mjs` through `require()`. Every pinned job restores it, and no row keys it. This needs fixing in this PR (see the block). Carry: R10-RCA-PREPR-HEAD-GRADERS
- Surviving mutant M14: drop the `path.join` alternative from `NAMED` (rename `path\.join\(` to an unmatchable token), and `grader_key_self_test` still reports 0 failed (ev/mutants-round3.txt). Yet the mutant takes `tools/release/stamp.py`, `tests/delivery_status.py` and `dev/audit/rounds/round4/D6/claims.py` out of the keys of CORPUS, WAVE CHECK, RULES SYNC and LANE SELF-TEST (ev/mutants-round3.txt, key diff). The record lists `path.join(ROOT, 'tools', 'release', 'stamp.py')` as a keyed seam, but no self-test case pins it. The gap row cannot catch the mutant because it reads the same `NAMED`. Add a key case, for example LANE SELF-TEST keyed by `tools/release/stamp.py`. Carry: R10-RCA-PREPR-HEAD-GRADERS
- The PR body is stale against this head:
  - Its `## Head note` still says "Round 2" and answers only round 1's block. Round 2's `budget_raise_gate.py` block, round 3's `named_loads` mechanism, the plant re-run and round 3's mutants appear only in the record, not in the body.
  - The body's cost test still gives "about 13 s" per PR and "Keys hit … any row 30". The record re-took these at round 3 as about 49 s per PR and 40 keyed merges ("pays for itself about 1.9 times over", against 7 in the body).
  - The `## Mutation proof` table stops at M9, and the self-test row count is still 51.
  - Bring the body to the head: a round-3 head note, the round-3 cost and key figures, and the round-3 mutants (M10-M13 below kill; M14 above). Carry: R10-RCA-PREPR-HEAD-GRADERS
- `review_packet.py render` refused `host-path` again (body; record `:4` and `:473`), so no packet was written. The cause is `ref_privacy._leaks`'s bare-substring home match: `/root` occurs inside `roles/root-cause.md`. The passwd home is also `/root`, so overriding `HOME` does not avoid it, and I did not work around it further. The body carries it to R10-RECORD-API-O1. The record states the read-back (`jq` over `dev/programme/rosters/wave-r10-groups.json` printing `carry` and `brief`), which answers round 2's open question about the carry. I did not run that `jq` myself. Carry: R10-RECORD-API-O1

## Evidence

- Head measured: `ef895338c0603c64adcf7ed6b2b25e06c5648b83` (ev/HEAD.txt). `git ls-remote` showed `fix/r10-rca-prepr-head-graders` at this SHA at 00:17Z. The body's `## Head` names this SHA. The merge base is `6493ea362`, which equals origin/main. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so this contract is current.
- RESULT `grader_key_self_test` at head: 15 ok, 0 FAIL (ev/grader_key_self_test.txt). This matches the record's "Fifteen rows". I did not re-run the full `--self-test` (420 s), and I did not run the record's 292 s plant re-run.
- RESULT mutants of the round-3 code, run in process from a patched copy of `ci_predict.py` at head (ev/mut.py, ev/mutants-round3.txt):
  - M10 (`named_loads` not followed in `mjs_closure`): 4 failed. These include the round-2 plant row (`budget_raise_gate.py`) and the gap null control, which lists 15 unkeyed named sites.
  - M11 (Python imports not followed): 1 failed, the `tests/layout.py` row.
  - M12 (stale-exempt refusal dropped): 1 failed.
  - M13 (named-gap enumeration dropped): 1 failed, "a key blind to named files…".
  - M14 survived (see Findings).
- Round 2's block is closed: `grader_hit("CORPUS", budget_raise_gate.py)` and `tests/layout.py` are keyed at this head (self-test rows 4-5), and M10 shows the keying is earned by `named_loads`.
- `git merge-tree --write-tree origin/main ef895338c`: rc 0, tree `4f02d6250`, empty stderr (ev/merge-tree.txt, ev/merge-tree.stderr.txt).
- `VERSION`, the manifest, `RELEASE_NOTES.md`, `tests/golden`, `*budgets*.json`, `tests/closures.json` and `tests/closure.py` have no three-dot diff from the merge base. Step 4 is not applicable.
- CI at this head, read at 00:17Z (ev/check-runs.json, ev/workflow-runs.txt): `CI edit` was in progress and `CI code` was queued. No gate check had concluded, and none was red. Step 11 has nothing to answer at this read. The block does not depend on CI. The authored code head `0ca059dee` has no workflow runs of its own (ev/workflow-runs-codehead.txt).
- Figures not re-derived: round 3's key table (539 merges, 21/32/27/21/4/7/28, any row 40), the 0.7 s unkeyed overhead, the 16.3 s / 49 s weighted cost, the 292 s plant, and the round-2 figures listed in the body.
- Forward-carry: the body names only the `ref_privacy` carry (see Findings). The proposed `gate-scoping.md` line is stated as needing the owner's approval.
