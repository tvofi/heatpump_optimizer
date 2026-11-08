Owner ruling (tvofi, 2026-11-07, waste-study decision cards, card 2, ruled NARROW): a fix reviewer that returns `blocked` with class `mutation-vacuous` or `class-open` lists, in that one verdict, every survivor or open seam it found at that head. It no longer names one per round. The repair fixer then answers the whole list in one repair.

This is **policy**. It changes what a reviewer seat must do (`dev/governance/roles/fix-review.md` steps 1 and 6), so it merges only on tvofi's approving review.

What changes:
- `fix-review.md` step 1: `blocked <sha> mutation-vacuous: <mutants>` names every survivor the reviewer's driver run reports at that head. The driver output goes in the evidence directory, and `push-verdict` reads it there (`survivor_list.py`).
- `fix-review.md` step 6: `blocked <sha> class-open: <seams>` names every seam the review found, not one per round. No hunt past what the review already ran is owed. A listed item whose harness does not move under its own perturbation is void (`judge.md`), so padding the list buys nothing.
- `tools/audit/seat/survivor_list.py` is the mechanical half. `bus.sh push-verdict` runs `survivor_list.py check <verdict> <evidence dir>` and refuses a `mutation-vacuous` verdict that omits a survivor `<file>:<line>` (or a spec name) that the evidence's driver output reports. Both verdict paths go through this: a local seat's push, and `cloud_relay.sh`, which calls push-verdict. It reads the survivor lines of `mutant_run.py` (`--diff`, `--spec`) and `tests/mutation_table.py` (`LIVES`, and `--pin-killed` through its owner `mutation_table.survivor_sites`). It drops a site that the table marks `[triaged equivalent]`. Any other verdict class passes unread.
- `class-open` has no mechanical check. There is no driver output to count a seam against: the enumeration rule a body names is free-form, so the obligation stays in the reviewer contract. The body says so here, as the brief asked.
- The rule text is paid for inside `fix-review.md` by trimming spent prose in steps 2, 4, 8, 9, 11 and 13, with no meaning dropped. The file stays inside its `policy_lint.mjs --budgets` caps (133 of 140 lines, ~2449 of 2451 tokens). No budget was raised.

In-flight edits to `fix-review.md`: R10-PROCESS-SLIM (`handoff/r10-process-slim`), R10-HOTFIX-NONREQUIRED-REDS (`handoff/r10-hotfix-nonrequired-reds`) and R10-DISPATCH-AT-HANDOFF (`handoff/r10-dispatch-at-handoff`, `-p2`). None has landed: `origin/main` is still the given base `8a4cf2618c53`, so there was nothing to rebase onto. The two that touch the file (the dispatch-at-handoff heads touch none of it) edit the preamble's publish line and steps 11 and 12. This diff edits steps 1, 2, 4, 6, 8, 9, the GREEN-mutation paragraph of step 11 (below the hunk both siblings change) and step 13. `git merge-tree --write-tree` against each sibling head is in Figures.

## Head

ed4d90addd9fe9f6d46ca008db40f1ab9d30905d, measured against merge base and `origin/main` 8a4cf2618c53a6dca6b65df3eae5efc8832d1796 (2026-11-08T15:09Z). `tools/pr/prepr.sh <body>` passed at this head against that base (`PRE-PR: ed4d90add... rc=0`). After that run, `origin/main` moved to 6b92bca124462875080a270202d78615c29972b8 (#3320, entities host-determinism; 2026-11-08T15:25Z). `git merge-tree --write-tree origin/main HEAD` exits 0, and the moved range touches none of this diff's files. Under the owner ruling of 2026-11-07 (merge `origin/main` only on a merge-tree conflict), the branch is not merged. Every figure below is at the 8a4cf2618c53 base.

## Mutation proof

- `survivor_list.py`, via `python3 tools/audit/seat/mutant_run.py --spec <4 mutants> --cmd 'python3 -I tools/audit/seat/survivor_list.py --self-test'`: `SURVIVED NULL`, then `KILLED class_gate_off` (the class predicate forced to `if True: return []`), `KILLED listed_always` (the listed test forced false), `KILLED triaged_not_dropped` (`found - triaged` becomes `found`), `KILLED check_rc_zero` (`if missing:` becomes `if False:`).
- `bus.sh`: deleted the two-line `survivor_list.py check` call in `push_verdict` and ran `bash tools/audit/seat/bus.sh --self-test`. Red: `FAIL push-verdict refuses a mutation-vacuous verdict naming one of two survivors, and review/7 does not move`. Restored. (`FAIL an ordinary append with no intervening fetch is the same commit object as before` is red at `origin/main` too. See Red checks.)

## Null control

- `bus.sh --self-test`: `ok null control: another blocked class over the same evidence proposes`. A `harness:` verdict over the same two-survivor evidence that refuses the `mutation-vacuous` one is pushed unchanged.
- `survivor_list.py --self-test`: `ok null control: another blocked class with the same evidence passes`, `ok null control: a merge verdict passes`, `ok evidence with no driver output counts nothing`.
- The brief's control: a `mutation-vacuous` verdict naming one survivor while the driver output at that head shows two is refused by `push-verdict`. This is the arm `push-verdict refuses a mutation-vacuous verdict naming one of two survivors` (rc != 0, `UNLISTED custom_components/x/a.py:40`, `review/7` unmoved). The same verdict listing both is proposed (`ok and proposes the mutation-vacuous verdict once it lists both survivors`).

## Figures

- `python3 -I tools/audit/seat/survivor_list.py --self-test`: `survivor_list self-test: 19 checks, 0 failed`. The checks include four that pin the producers' own print statements (`mutant_run.py`, `tests/mutation_table.py`), so a format change turns this red. Without them, every survivor would silently read as none.
- `bash tools/audit/seat/bus.sh --self-test`: 162 checks, 1 failed at the head. At `origin/main` 8a4cf2618c53 it is 159 checks, 1 failed, and the failure is the same check, `an ordinary append with no intervening fetch is the same commit object as before`. The 3 added checks are this diff's arms, all `ok`.
- `node tools/policy/policy_lint.mjs --budgets`: `fix-review.md` 133 lines (cap 140), ~2449 tokens (cap 2451). The rule is `Math.round(bytes / 4)`. At the base it was 137 / 2448.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `4 of 2666 ENTITY CHECKS FAILED` at the head and at `origin/main`. The four top-level names are identical at both ends (`diff` of the two `FAIL` lists, sub-check rows excluded, printed `SAME-4-AT-BASE`): the coverage-reuse, release-ZIP and two Pages workflow checks. This diff touches none of them.
- `tests/doc_claims.py`: `ALL 296 checks PASSED`. `tests/harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`. `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Scope: `python3 tests/closure.py select --files <the three-dot diff's files>` printed `MODE: SCOPED -- 3 script(s) run` (doc_claims, entities, harness_headers).
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: `125 self-testing, 125 wired, 0 unwired`, `0 index gap(s)`. The new governance.yml step wires the self-test.
- `node tools/policy/agreement.mjs`: no `UNREGISTERED` line after `df7f154da`. Before it, `survivor_list.py` carried a second copy of `mutation_table.py`'s `--pin-killed` grammar, which it now imports instead.
- The brief's measurement, re-run here: `python3 -I tools/audit/seat/review_strength.py --window last3d=2026-11-04T19:00:00Z..2026-11-07T19:00:00Z --by class`. It printed `mutation-vacuous ... PRs 18 verdicts 24` and `class-open ... PRs 9 verdicts 17`. The brief states 25 on 19 and 23 on 13. The instrument reads live verdict refs, so its counts depend on when and where it runs. I re-took it from this cloud checkout and cannot reconcile the difference. The instrument is named, not either number.
- Sibling conflicts. `git merge-tree --write-tree HEAD origin/handoff/r10-hotfix-nonrequired-reds` exits 0. `git merge-tree --write-tree HEAD origin/handoff/r10-process-slim` exits 1, on `dev/governance/roles/orchestrator.md` and `tools/audit/seat/INSTRUMENTS.md`. `git merge-tree --write-tree origin/main origin/handoff/r10-process-slim` names the same two paths, so this diff adds no conflict of its own with that sibling, and none in `fix-review.md`.

## Red checks

none at the handoff (no CI has run on this head). Local reds that predate this diff, unchanged from `origin/main`: `tests/entities.py` 4 of 2666 (named above) and `bus.sh --self-test`'s `ordinary append` check. Neither is reached by this diff.

## Forward-carry

none

## Friction

none

## Unpinned sites

`tools/audit/seat/survivor_list.py`'s predicates are pinned by the four spec mutants above, all killed by its self-test. `bus.sh`'s added call is pinned by the bus.sh self-test arm named under Mutation proof.

## Approval

Policy: merges only on tvofi's approving review (`CLAUDE.md`, "Where the policy is").
