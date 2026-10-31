Fix review: blocked 7c43d8fb1505320e2b10d7c122dab3215ebd085c mutation-unpinned: the three button.py sites the diff adds stay unpinned because mutation-autofix reports skip-measure-failed, so tests / mutation stays red with no repair path

bus-nonce: b8365800b79795f88651d7eca094d1d0

## Block

- `tests / mutation` (job 124122284888) concluded failure at this head: `MUTATION TABLE REFUSED -- 3623 unpinned site(s) against 3620 at the ratchet base e77418f9b`. The three sites are `button.py:226 GUARD_OFF`, `:228 GUARD_OFF` and `:230 RETURN_DEL`. The diff deletes the three old pins and records none.
- The body answers the red with "mutation-autofix pins killed sites after the push". It did not. `tests / mutation-autofix` (job 124123187126) concluded failure with `AUTOFIX: skip-measure-failed -- THE REPAIR DID NOT HAPPEN. No commit will be pushed`. `ci-autofix.md` says a red autofix job means no bot commit comes and the repair is the seat's. `pinned by mutation-autofix` stays a prediction until a `mutation-pins` log or `--pin-killed` kills the site.
- The body already knew the tool path refuses. Its `## Unpinned sites` says `--pin-killed` and `--anchor` refuse with `no full-line comment in any file in the pool`. I reproduced that refusal at this head (ev/pin_killed.txt, rc=1). So the CI autofix was bound to fail for the same reason, and the handoff relied on a repair the fixer had already seen refuse.
- `tests / mutation-autofix` is red and is not named in `## Red checks`. `review_packet.py` also refuses `red-unanswered` on `tests / mutation`, because the body names it only as `mutation`. That is the spelling `policy_lint.mjs` keys on.
- What clears this: commit dispositions for the three sites under `tests/mutation_ledger/` that `tests / mutation` accepts at a new head. That can be hand-written `killed_by` records backed by the hand kills the body reports (I re-confirmed one of them below), or an instrument fix that lets `--pin-killed` run on `button.py`. Then name `tests / mutation` and `tests / mutation-autofix` in `## Red checks` with their answers.

## Findings

- Instrument gap: `mutation_table.py --pin-killed`/`--anchor` and `mutation-autofix` refuse to pin any site in a file pool with no full-line comment (`button.py` here). Every such diff then ends with `tests / mutation` red and no automated repair, and `ci-autofix.md`'s table lists `mutation-autofix` as the repair for unpinned sites without naming this case. Carry: R10-UX-HEALTH
- The P9 storage-reset and chart collision are withheld. The body's own forward-carry routes them; I did not open the roster at `handoff/audit-r10-roster` to confirm the precondition (step 10), because the block above stops the review first. Carry: R10-UX-HEALTH
- The "driving scale" widget is not built and waits on orchestrator confirmation, per the body. Carry: R10-UX-HEALTH
- #2499 stays open: the no-meter over-booking (body figure plan/deliv 1.908) is not met. I did not re-derive that figure. Carry: #2499

## Evidence

- Round: first review of #2997. Head measured: 7c43d8fb1505320e2b10d7c122dab3215ebd085c, the PR head when read. The base is origin/main e77418f9b48f89421bd72b0ab511c057341c7fa4, which is also the merge base. `dev/governance/roles/` does not differ between the merge base and main.
- `git merge-tree --write-tree origin/main <head>`: rc=0, tree a40fbbec5b3f, no conflicts (ev/merge_tree.txt).
- VERSION, the manifest and RELEASE_NOTES are untouched. No claim file is touched.
- RESULT head: `node tests/card.mjs` ALL CARD CHECKS PASSED. `tests/debug_collect.py` ALL 159 DEBUG COLLECT CHECKS PASSED.
- RESULT mutation proof, each mutant run in its own worktree at the head (ev/mut-*.txt):
  - Delete `host._render();` in `openSetupSlot`: 2 CARD CHECK(S) FAILED, as the body says (the new check plus the pre-existing Assign redraw check).
  - `b.cfgPage = L(page)`: 1 CARD CHECK(S) FAILED.
  - `healthModelTitle` returns the metric alone: 2 CARD CHECK(S) FAILED (hover spec en and sv).
  - button.py final branch returns `debug_collect`: 1 of 159 DEBUG COLLECT CHECKS FAILED.
  - All four match the body.
- Class: the only setter of `waiting_for` values is `button.py:227/229`. No card, translation or doc consumer exists at the head, so the #2809 class is one seam. The hover test enumerates every `data-model-row` the page draws and asserts 6.
- CI at review time:
  - Red: `tests / mutation` and `tests / mutation-autofix`.
  - Green: `tests / browser`, `typing`, `arch-instrument`, `arch-score`, `budget-raise-gate`, `delivery-status`, `policy-docs`, `env-matrix`, `hassfest`, `validate-hacs`, `briefs`, `closure-scope`, `nightly-status` and `mutation-pins (1)`.
  - Still in progress: `tests / fast (3.14)`, `closures`, `coverage`, `governance / instrument-self-tests` and `codeql / Analyze (python)`.
  - No `pr-contract` run is listed on this head. The red checks above are read from the check-runs API, not from the body.
- Not re-derived: the scoped-gate count (16 run, 17 scoped out), the #2499 harness figures and the P9 grid counts (850/1190 pairs, 30 entries). I have not verified them.
- No finder's harness is named for these carries (the packet says "none named"). The figures I checked are the four mutants and the merge.
