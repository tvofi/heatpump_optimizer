Fix review: blocked 245ddf7876bf9662937d4e9077172e1e3cd2275a mutation-vacuous: the CI settle call in governance.yml and the settle CLI dispatch survive deletion

bus-nonce: 659487de38804b312d0cff911a14a807

Round 1 of review for #3419 (R10-HOTFIX-PREPR-READSET). Measured head: 245ddf7876bf9662937d4e9077172e1e3cd2275a. It is still `refs/pull/3419/head` at verdict time.

## Block

The fix works. My base/head records reproduce it (Evidence). But the two production lines that take it to the red on main are pinned by nothing. Deleting either one leaves every check green, so a later edit can drop the countermeasure, and main goes red again only when checkout timing happens to make the index racy:

1. **`.github/workflows/governance.yml`: delete `python3 -I tools/ci/selftest_scope.py settle`** from the `strace` step. Self-test at the head: rc 0, 109 checks, 0 failed (`ev/mut-ci-wiring.txt`). `selftest_scope.py static`: rc 0, `111 gated step(s), 0 problem(s)` (`ev/mut-ci-static.txt`). This is the line the body's Fix section names as the CI countermeasure ("It runs untraced in CI's `strace` step, before `launch`"). On a PR it never runs (`SELFTEST_TRACE` is empty there; this head's instrument-self-tests log shows `SELFTEST_TRACE: ` blank). So only a static check can pin it.
2. **`tools/ci/selftest_scope.py` `main`: replace `return settle_index(root)` under `argv == ["settle"]` with `return 0`.** Self-test rc 0, 0 failed (`ev/mut-cli-settle.txt`). The workflow then calls a no-op and stays green.

The self-test already parses the live job and pins its wiring (`wrapper: the ungated steps [...] run untraced`, `wrapper: its UNTRACED list is UNGATED`, `the live job parses ... and its gating is consistent`). The repair is to add the same kind of check: an untraced step ordered before `launch` runs `selftest_scope.py settle`. Add a `main(["settle"])` dispatch check over the racy fixture, and add the first to `selftest_scope_mutants.sh` as a mutant. The killed mutants below stay killed. Nothing else blocks.

## Evidence

- Merge with main: `git merge-tree --write-tree origin/main 245ddf78…` rc 0, clean (`ev/merge-tree.txt`).
- Role-file currency: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` touches only `nudge.md` and `orchestrator.md` (#201 → #3394 renames). `fix-review.md` is current.
- CI: `merge_train.py classify 245ddf78… --pr 3419` read `GREEN … pending: none red: none` at 12:37:19 UTC (`ev/classify.log`). The packet's `gate` failure was the interim `FAIL run(s) [42811139125] at this head are still being judged`, superseded by GREEN. The packet re-rendered after that carries no refusal (`ev/review-packet.md`). `owed-reds` set: `ev/owed-reds.txt`. No owed red remains, so `## Red checks: none` is accurate.
- PR-named mutants at the head (in-tree harness `sh tools/ci/selftest_scope_mutants.sh --self-test`): `settle never rewrites the index` killed (`FAIL settle: no index entry is left racily clean (rc=1)`, `FAIL record: it settles a racy index before tracing`). Harness ends `SELFTEST-SCOPE MUTANTS: every mutant refused` (`ev/mutants-harness.txt`).
- Reviewer mutants (untraced self-test with strace on PATH):
  - record-no-settle killed, 1 FAIL;
  - racy `>=`→`>` killed, 3 FAIL;
  - settle returns 0 up front, killed, 3 FAIL;
  - settle wait loop removed (`time.time() < newest + 1.1`→`False`), killed, 10 FAIL;
  - CLI dispatch to `return 0` SURVIVED;
  - workflow settle line deleted SURVIVED (see Block).

  Files: `ev/mut-*.txt`.
- The body discloses that the record-no-settle mutant is killed only by an untraced run, so it would survive in CI's traced mutant step. My run confirms the kill untraced.
- Finder's harness at both ends. No committed harness exists; the finder's instrument is CI's traced instrument-self-tests drift check, which a PR cannot run. I used the body's own instrument, `python3 -I tools/ci/selftest_scope.py record --step prepr --out <f>`, two fresh worktrees per end, recorded in parallel, about 910 s each.
  - Base 30c785330fc727ae26d6a6d2d51b38f1856fe87c: 128 and 21 prepr `files` entries, against 86 committed. They differ from each other, and 100 and 18 entries respectively are absent from the committed entry. That is the moving read set.
  - Head: 84 and 84 entries, identical. Each worktree started with 9726 and 8309 racy entries (`racy_entries`). Against the committed entry, one entry is extra (`tools/policy/fixtures/required-contexts.json`, the environment read the body discloses) and 3 are not read.

  Files: `ev/rec-*.json`, `ev/rec-*.log`. The body's baseline counts (253/84/21/282) are one-off runs. I re-derived the shape, not the numbers: base varies, head is identical across runs.
- Self-test at the head: `109 checks, 0 failed`, strace arms included (`ev/selftest-head.txt`). Flake: 30 of 30 runs passed under five concurrent loops of six (`ev/flake-loop*.txt`). That is consistent with the body's 0 of 40, on a smaller sample.
- `VERSION`, manifest, `RELEASE_NOTES.md` and both claim files are untouched (three-dot diff empty). No fixture moved, so the claim-file drift check has nothing to compare.
- Head section: the code commits 143a53d41 and 9679946bc, a merge of main, and a delivery-row record commit. `git diff 9679946bc 245ddf78 -- tools/ci .github/workflows/governance.yml` holds only main's changes.
- Not re-derived: the 9811/3862 per-pid open counts (scratch probe, not in tree), and `settle`'s 0.82 s / 0.08 s timing.
- Forward-carry: the body's one item is dismissed as R10-RCA-MAIN-SELFTESTS-RED done, with the countermeasure in this PR. The packet's carry_audit reports it routed.
- Closing self-audit: `carry_audit.py check` rc 0 (`CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`). It ran over an abridged local copy of the PR body, with the `## Forward-carry` section verbatim, and over this verdict.

## Findings

none
