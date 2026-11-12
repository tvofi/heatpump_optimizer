Fix review: merge 976aa66d2af97950eb5efcffc4ac5d558cc27e76

bus-nonce: 89dbb6444bd59f229420ab08da5f6987
pending-ci: gate

This is round 5, the delta review from the reviewed head 8cf976936e013314c513ecf4bb283b7c88f63d8b. The delta adds three self-test checks to `tools/audit/carry_audit.py` and changes one `tests/closures.json` value. It cures all three survivors that the 8cf97693 block named.

## Evidence

- RESULT head reviewed: 976aa66d2af97950eb5efcffc4ac5d558cc27e76 (`ev/HEAD.txt`). It is the tip of `fix/r10-carry-audit-p5` per `git ls-remote`, and it matches the body's `## Head`.
- Prior block, the three survivors. I re-ran them with the reviewer's harness at this head. Each mutant was applied alone to `tools/audit/carry_audit.py`, `--self-test` was run, and the file was restored (`ev/mutants_head.txt`):
  - `quoted_lookbehind_alone`, `(?<![\w"])` dropped from `QUOTED_PHRASE`: 447 checks, 1 failed, on `carry 3: an opening quote glued to a word ...`. KILLED.
  - `quoted_lookahead_alone`, `(?!\w)` dropped: 447 checks, 1 failed, on `carry 3: a quote closed against a word ...`. KILLED.
  - `mdlink_url_any`, `[^)\s]*` changed to `[^)]*` in `MD_LINK`: 447 checks, 1 failed, on `carry 3: a link whose destination holds a space is no link ...`. KILLED.
  - Null control, a whitespace-only edit: 447 checks, 0 failed.
  - Each new check is the distinguishing probe that the prior verdict's `ev/survivor_probes.txt` named.
- RESULT `carry_audit.py --self-test` at the head: 447 checks, 0 failed (`ev/carry_selftest_head.txt`). This matches the body's `## Figures`.
- RESULT `bus.sh --self-test` at the head: 178 checks, 0 failed (`ev/bus_selftest_head.txt`). This matches the body's `## Figures`.
- `tests/closures.json` changes `recorded["tests/entities.py"].rc` from 1 to 0, with seconds unchanged at 867.9. origin/main already holds exactly this entry, landed by 106d87c338 ("entities.py recording at its fixed point (rc 0)"). That is the record-then-plain-`--single` sequence that `tests/closure.py` documents beside its `broken` refusal. The head now equals main's entry for that key, and the closure file list is unmoved. The number is earned by the same mechanism main used, not gamed (step 14).
- Delta scope: it touches only `tools/audit/carry_audit.py` (in `_self_test`) and `tests/closures.json`. No production line and nothing under `custom_components/` changed, so nothing widens the scope (step 12). The delta adds no mutable production line, so there is no new mutant to draw.
- Merge: `git merge-tree --write-tree origin/main 976aa66d` exits 0 against origin/main 8c10361eb1fe, with `LEDGER-MERGE: resolved tests/closures.json` (`ev/merge_tree.txt`).
- Versions: VERSION, the manifest version and the RELEASE_NOTES.md heading are untouched since the merge base. There are no golden or claim files in the PR.
- Role drift: `git diff <merge-base>...origin/main -- dev/governance/roles/` changes fix-review.md. I read the current text through `role_pack.py`.
- `tests / nightly-status` is red from a cancelled scheduled run. It is not in `merge_train.py owed-reds`, so it is owed no answer and blocks nothing.
- CI: `merge_train.py classify 976aa66d --pr 3493` read WAIT (`pending: gate red: none`) on every poll from 15:47Z to 16:20Z (`ev/classify.txt`), with no red among the required contexts. I stopped waiting after about 30 minutes, as the brief allows, so the merge holds only once CI is green at this head.
- The body check ran on the PR body's carry-bearing sections (Red checks, Forward-carry and Friction, all `none`) written to a local file, plus this verdict: `carry_audit.py check` gives 0 finding items, rc 0.
