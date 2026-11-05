Fix review: blocked 794fe6a76d5d24cd10cf0756d1c1a8bf4b0fc957 mutation-vacuous: merged_steps call in prepr.sh main flow deleted, prepr self-test 504 passed 0 failed

bus-nonce: 33fa557d147d0c98b1e4a968418e7d0a

Round: first fix review of #3221 (R10-HANDOFF-PATH part 1, P386), measured at head 794fe6a76d5d24cd10cf0756d1c1a8bf4b0fc957 from a detached worktree; the head was re-read at the end and had not moved.

## Block

Two defects. Each lets a receipt skip a check that the body says still runs.

1. **mutation-vacuous: the call that runs the merged-tree checks is unpinned.** Delete the one main-flow line `merged_steps "${1:-}" "$UNPINNED_SITES"` in tools/pr/prepr.sh. `bash tools/pr/prepr.sh --self-test` still reads `504 passed, 0 failed` (ev/mutants-prepr.part1.txt, P1). Under `PREPR_SKIP_CODE` that line is the only ci predict and the only `tests/structure.py` on HEAD merged with main: step 6d's predict is behind `if [ -z "$REUSE" ]`. Without it, a reuse run checks neither, and no test notices. The self-test drives the `merged_steps` function directly (arms (d) and (e)). The `(a)` arm runs a real `PREPR_SKIP_CODE` prepr but asserts only that the code-keyed steps are absent, never that `merged structure` and `ci predict` are present. The body's own mutant edits inside the function, which is why it was killed. Repair: in the `(a)` arm's real run, assert that both `merged structure` and `ci predict` lines appear. Then the deleted call fails a check.
2. **A receipt names the HEAD at the run's end, not the HEAD it measured.** `receipt_write` writes `git rev-parse HEAD` after the run, and nothing in the main flow pins the HEAD the run started on. Demonstrated end to end (ev/realrun2-summary.txt, ev/realrun2.sh):
   - A real `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>` started at `1acf58eb7c1f` (02:32:46), with this PR's own handoff body.
   - At 02:36:46 a commit of new code (`fba41aea801e`) landed in the worktree, and the body's `## Head` was pointed at it.
   - The run ended `rc=0` and wrote `receipt fba41aea801e written`.
   - `body_push.sh` would carry that receipt as `Prepr: fba41aea… <its tree>`, and `app_push.sh --reuse` would then drop the code-keyed steps for code that the steps run before 02:36 never saw.
   
   This is the brief's "head that moved after the receipt", moved during the run instead. The function-level form is ev/midrun-receipt.txt (ev/midrun.sh). Without the body edit, step 7's `## Head` check refuses, and so does the early `## Head` arm (ev/realrun-summary.txt). So the hole needs code and body to change mid-run, which is a seat working while its prepr runs. Repair: capture `HEAD` (and its tree) where the main flow starts, and have `receipt_write` refuse when either differs at the end. Add a self-test row for it.

## Findings

- Follow-up: surviving mutant: in `reuse_verdict`, remove the first-parent-chain check of (c) (`rev-list --first-parent … | grep -x "$mb"` replaced by `true`). `app_push.sh --self-test` stays at `219 checks, 0 failed`; only this reviewer's planted R6 (HEAD holds a main commit off main's first-parent chain) kills it (ev/mutants-app_push.txt, M2b). Carry: R10-HANDOFF-PATH
- Follow-up: surviving mutant: the trailer-count test `= 1` relaxed to `-ge 1`. The self-test stays at 219/0; only planted R7 (two `Prepr:` trailers) kills it (M5). Carry: R10-HANDOFF-PATH
- Follow-up: surviving mutant: under `--reuse`, `row_only_checks` after prepr removed (`[ "$reused" = 0 ] || row_only_checks` replaced by `true || …`). The self-test stays at 219/0 (M6). The live-title body contract and carry check the header promises under reuse are unpinned. Carry: R10-HANDOFF-PATH
- Follow-up: surviving mutant: the main flow's early `rm -f "$(receipt_file)"` removed. The self-test stays at 504/0 (P3). The body's claim that "a failing run leaves none" is unpinned; the `--body-check` row deletes the receipt itself before it runs. Carry: R10-HANDOFF-PATH
- Follow-up: surviving mutant: in body_push.sh `prepr_trailer`, the sha comparison `[ "$s" = "$2" ]` weakened to `[ -n "$s" ]`. The self-test stays at 504/0 (P6), because the tree comparison masks it in the only row. Downstream, `reuse_verdict`'s is-ancestor and tree-diff arms would still refuse a mismatched sha, so this is a test gap, not a hole. Carry: R10-HANDOFF-PATH
- Out of scope: the receipt is an unsigned self-attestation. A hand-written `Prepr: <C> <tree(C)>` trailer on handoff-body/<topic>, with no prepr run behind it, is accepted (planted R8 → REUSE). Likewise a seat may set `PREPR_SKIP_CODE` by hand. Carry: dismissed: P386 rules that the fixer's prepr is trusted; the body says so under Alternatives; CI gates the merged head, and PREPR_SKIP_* knobs were already seat-settable

## Evidence

- RESULT: `bash tools/pr/app_push.sh --self-test` at the head: `app_push self-test: 219 checks, 0 failed` (ev/app_push-selftest.txt). Matches the body.
- RESULT: `bash tools/pr/prepr.sh --self-test` at the head: `504 passed, 0 failed` (ev/prepr-selftest.tail.txt). Matches the body.
- RESULT: the body's two mutants re-checked in kind:
  - M3, the tree-diff arm (d) removed: self-test 2 failed. M7, the verdict forced to reuse: 3 failed.
  - P7, ci predict never run in `merged_steps`: 2 failed. P2, the dirty check removed: 1 failed. P4, `PREPR_SKIP_CODE` writes a receipt: 1 failed. P5, the rc check removed: 1 failed.
  - All killed. All mutants were restored, and `git status --short` was empty after each batch.
- RESULT: equivalent mutants. M1 (the is-ancestor check of (c) removed) and M4 (the commit count of (e) removed) survive both the self-test and the planted harness. Read as subsumed: when C is not in HEAD, or HEAD carries extra commits, either the tree diff (d) differs, or the trees are identical and reuse is sound.
- RESULT: planted receipts, this reviewer's own harness (ev/plant.sh) against the production `reuse_verdict` extracted from the head (ev/planted-receipts.txt). Each verdict is as expected:
  - null genuine receipt → REUSE
  - R1, a trailer naming a sibling head with its own matching tree → FULL
  - R2, the head moved after the receipt (a new commit, then main merged) → FULL
  - R3, the code rebased onto a new base with the old-base receipt kept → FULL
  - R4, a forged tree → FULL
  - R5, an evil merge carrying extra content → FULL
  - R6, an off-first-parent main commit → FULL
  - R7, two trailers → FULL
  - R8, an unbacked hand trailer → REUSE (the trust boundary, Findings)
- RESULT: no weakening for a PR with no receipt. With no trailer, every arm falls to the full prepr with no `PREPR_SKIP_CODE`. This is the stub run in the self-test and planted R1/R4/R7. update_pr.sh's former empty `RO` becomes `--reuse`, which falls back to the full prepr. In a full run, `merged_steps` adds `tests/structure.py` on the merged tree, so it only adds checks. Every `take_slot` call (lines 4155, 4209, 4278, 4358, 4401) sits inside a `REUSE`-skipped group or the `elif` closures arm, and no function defined in a skipped group is called after it.
- RESULT: the merge resolution kept both sides. `git diff origin/main 794fe6a7 -- tools/pr/prepr.sh` removes only the moved `PREPR_RECORDER_CACHE` lines, which are re-added before the gate. Main's `8f6f0ea2f`, `18481fd52` and `1584530f3` (lazy `take_slot`, `closures_owes_slot` fixture, early `## Head` arm) are intact.
- RESULT: merge with main is clean. `git merge-tree --write-tree origin/main <head>` gives rc=0 at main 499162c8, and again at main 7c274274 after main moved (ev/merge-tree.txt). No claim file is in conflict.
- RESULT: figures re-derived at the head (ev/figures.txt):
  - `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`
  - `STRUCTURE RATCHET PASSED`
  - The three-dot diff of the claim files, VERSION and RELEASE_NOTES.md is empty, and no manifest is touched.
  - The handoff body's trailer `Prepr: 1acf58eb… 09585b95…` matches `1acf58eb^{tree}`.
  - Not re-derived: the body's 27 s kept-step wall time, measured at 91a75ed8.
- RESULT: the body carries all seven template headings of .github/PULL_REQUEST_TEMPLATE.md.
- CI at this head: `merge_train.py classify` exit 1, `RED 794fe6a7… pending: none red: gate` (ev/classify-final.txt).
  - The red `gate` is `cancelled`, not failed: job 127007801588 in run 41953678981, cancelled at 02:24:51 alongside that run's prelude and cancel-superseded. `pr-contract` was skipped in the same run.
  - The other workflow run (41952980694) has `tests / mutation`, `arch-score`, `closure-scope`, `policy-docs`, `wave-script`, `budget-raise-gate`, hassfest, validate-hacs and two codeql analyses green.
  - `governance / delivery-status` is red on OVERDUE rows #3089 and #3192 only (not this PR's row; not a required context). `tests / nightly-status` is red; its inputs are not reached by this diff.
  - This head has no completed gate, so the body's `## Red checks: none` could not be checked against a finished gate run.
- Real-run 1 (ev/realrun-summary.txt) refused on the early `## Head` arm before any mid-run commit, because the handoff body names the code head `1acf58eb`, not the row head `794fe6a7`. It was inconclusive for block 2 and was re-run at `1acf58eb` as real-run 2.
- Process: a container restart interrupted real-run 2 and the mutants P3–P7, and both were re-run from scratch. handoff-wip was not pushed, because the seat's instructions allow only the probe ref.
