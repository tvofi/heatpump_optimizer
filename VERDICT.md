Fix review: blocked 8cb08929c3cee3ea7e1252f95538f3e3b93692ab merge-conflict: the merge with origin/main d6308d77c fails policy_lint, CLAUDE.md about 3627 tokens against this head's 3609 cap, after main's fdf930b52 (#2631)

bus-nonce: 19426281adf66339d3e838af3fcea571

## Block

This is round 2. The head is still `8cb08929c3cee3ea7e1252f95538f3e3b93692ab`: I re-read it through `git ls-remote` and the PR API before writing this (ev/HEAD.txt). Main, though, moved during the review, from `e45fc34fb` to `d6308d77c` (#2631, #2635).

`git merge-tree --write-tree origin/main 8cb08929c` exits 0. The only message is `LEDGER-MERGE: resolved tests/closures.json` (ev/merge-tree-new-main.txt, ev/merge-tree-new-main.stderr). So the merge has no textual conflict. It does have a measured one. `node tools/policy/policy_lint.mjs` on that merged tree (commit ev/merged_tree_commit.txt) prints `ERROR [budgets] CLAUDE.md: about 3627 tokens across its lines exceeds its cap of 3609 tokens (files_tokens)` and `TOTAL: 1 error(s) across 50 policy file(s)` (ev/policy_lint_merged.txt, ev/policy_budgets_merged.txt). Origin/main on its own reads `TOTAL: 0 error(s)`, with CLAUDE.md at 3515 against 3590 (ev/policy_lint_newmain.txt, ev/policy_budgets_newmain.txt).

The cause is that main's `fdf930b52` (R10-BRIEFS-FOLD, #2631) lengthened CLAUDE.md's `ci-autofix.md` row by 18 tokens. That fit inside main's own headroom. This PR recorded CLAUDE.md's cap at exactly its measured 3609 over the old base, so main's 18 tokens put the merged file over that cap. Per-file caps get no band. Merging this head as it stands would turn `policy-docs` red on main.

The fixer's resolution delta has three parts:
1. Merge `origin/main`.
2. Pay the 18 tokens in CLAUDE.md, or re-record its `files_tokens` to the merged measurement, with this body's `## Raise justification` updated to cover it.
3. Re-take the figures the body quotes as functions of main's tip.

Apart from that, the evidence below found the change sound, and it carries over to the re-review of that delta.

## Findings

- `CLAUDE.md`'s `files_tokens` cap has to be paid or re-recorded over the merge with `origin/main` (`d6308d77c` or later), and the body's raise line and its `corpus_tokens` figure re-taken. On the merged tree the corpus reads ~66456 against the recorded 66507, so it still fits; always-loaded reads 3627 against 3349 +band 500 = 3849, which the band still admits. Carry: R10-FLOW-ARCH-PLANNER | dismissed: owed by this group's own resolution delta, re-reviewed before merge
- A surviving mutant in the triage gate. In `tools/audit/seat/roster_edit.py` `triage_refusal`, I changed `if verdict != "ACCEPT":` to `if verdict not in ("ACCEPT", "DEFER"):`. The self-test still reads `roster_edit self-test: 116 checks, 0 failed` (ev/reviewer_mutants.txt). The self-test pins REJECT and missing-verdict rulings but no DEFER ruling. So an edit that lets a cited DEFER reach the roster passes, although `proposal-triage.md` and the owner's brief say only an ACCEPT is routed. The production line is correct, and the fixer's own T2 plant is killed by the REJECT case. What is missing is one self-test check that a carry citing a `Verdict: DEFER` entry is refused. It is cheap enough to ride the resolution push. Carry: R10-FLOW-ARCH-PLANNER | dismissed: one self-test check, owed in this group's resolution push and re-reviewed with it

## Evidence

- Contract currency. `git diff e45fc34fb...origin/main -- dev/governance/roles/` moves `fix-review.md` and `fixer.md` (#2631). In `fix-review.md`, step 11's silence now splits into `root-cause-detectable`, `root-cause-unrecorded` and `root-cause-unanswered`, and steps 12 and 14 are compressed. I applied the new step 11. The body answers all three red checks below, so no class from it applies.
- Round-1 finding answered. #2628's section-10b wording (the `brief_lint.mjs` read set; "putting one there is not carrying it"; "that rule's remedies"; the `FIXTURE ok: N error(s)` exit-code rule) now appears verbatim in `standing-roster.md`'s "`brief-citations.md` binds every op". The only change is that the tool is named by its full path, `tools/policy/brief_lint.mjs`. In `orchestrator.md` it is reduced to the pointer "Through the roster seat, on `standing-roster.md`'s terms." Nothing is lost or weakened, and it is stated once. `git diff e45fc34fb HEAD -- dev/governance/roles/orchestrator.md` shows no hunk outside sections 2b, 4, 5, 5b and 10b. #2628's other edits survive the merge unchanged.
- The moved text is compressed, not dropped. Section 4's `preflight.sh` rules (stdin, intended-number arguments, the empty-stdin `clean`, the 143 on held-open stdin, the per-number escape, the after-merge read-back with #224 and #195) appear in `standing-merge.md`. Section 5b's ref-not-record rule, with `ls-remote`, opener vs `update_pr.sh`, and `bus.sh orphans`, appears in `standing-dispatch.md`. What was dropped is explanatory prose only: "neither looks like a failure", and "a pre-merge scan that asks which form was used". No obligation went with it.
- Check 1 (policy soundness). Each of the seven contracts carries a delivery item the group brief names: the architect-planner and plan-review contracts, the proposal-triage seat and its gate, the four standing seats with their sweep liveness step and the pulse arm, the critical-path owner ruling in section 5, and the CLAUDE.md rows. Each names its seat, model and effort, input, instruments, what it never does, report and restart. The owner of all of it is tvofi's 2026-10-22 rulings, carried verbatim on the roster.
- Check 1, restatement scan. I ran my own 6-word-shingle overlap scan (my instrument, not the finder's; ev/overlap6.txt). Across the seven contracts it finds only the shared standing-seat boilerplate. Against the rest of the corpus it finds one sentence, `standing-merge.md`'s "never with a custom `--subject`: four readers parse it (#2423)", which repeats `orchestrator.md` section 11. Against decision 0015, which is outside the corpus, `architect-planner.md` shares 16 shingles.
- Check 2 (raise), re-derived at the head. `policy_lint.mjs --budgets` prints `corpus: ~66507 tokens, cap 66507` (ev/policy_budgets.txt); at the base it was `~62888, cap 62892` (ev/policy_budgets_base.txt). The delta is +3619, and I itemised it exactly: the seven new files add 3768 (1261+507+509+489+368+330+304), `orchestrator.md` falls 4512 -> 4251 (-261), and CLAUDE.md rises 3497 -> 3609 (+112). The body has `## Raise justification`, lists its payments tried and its refusals, and carries `Architecture score: dS +0.0000 NULL`. I re-took that score: `score.py --diff e45fc34fb HEAD` prints the same line (ev/archscore.txt).
- Check 2, my own payment hunt. The one candidate is the #2423 sentence and "leaves #N open", about 35 tokens in `standing-merge.md`. I judge that it does not pay. The merge seat is the one applying those rules, and citing them instead would make a sonnet seat open the 4251-token `orchestrator.md` to read one line. That is not sounder, so it is not `metric-gamed`.
- Role caps at the head, inside the band, not raised: fixer 6288/5852, record 7432/7405, policy 10016/9958, each +500. Always-loaded is 3609 against 3349 +band 500 = 3849, so the lint band really does admit it; at the base it was 3497. `orchestrator.md`'s caps are re-recorded down to measured, 295 lines and 4251 tokens.
- Check 3. At the head, `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python tests/harness_headers.py` gives `ALL 109 HARNESS HEADER CHECKS PASSED`, rc=0 (ev/harness_headers_head.txt). With `ROOT = Path(__file__).resolve().parents[3]` re-inserted, `check_repo_roots()` gives `FAIL depth seams: dev/audit/harnesses/r10_triage_gate_replay.py:34` (ev/repo_roots_mutant_parents3.txt). Restored, it reads ok (ev/repo_roots_head.txt). CI `fast (3.14)` is success on this head.
- Check 4. `git diff $(git merge-base origin/main HEAD)...HEAD -- dev/programme/rosters/wave-r10-groups.json VERSION RELEASE_NOTES.md custom_components/*/manifest.json` is empty (ev/untouched.txt).
- Figures re-run at the head after the merge, which the body cites and the brief says the fixer did not re-run. All of them match the body:
  - `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python tests/entities.py`: `ALL 2399 ENTITY CHECKS PASSED`, rc=0 (ev/entities_head.txt).
  - `python3 tests/env_drift.py --claims-only e45fc34fb`: `claims hygiene: e45fc34fb ok`.
  - `python3 tests/closure.py selftest`: `ALL 112 closure shrink pins PASSED`.
  - `/opt/hpo/venv-ci/bin/python tests/layout.py`: `layout self-test: ok`.
  - `closure.py select --diff e45fc34fb`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`
  - `ci_predict.py`: no red predicted.
  - `policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`.
  - `brief_lint.mjs`: `TOTAL: 0 error(s) across 47 file(s)`.
  - `RULES-SYNC ok`.
  - `STRUCTURE RATCHET PASSED`.
  - Self-tests at the head: pulse 37, roster_edit 116, r10_roster_ops_mutants 78, sweep_render 21, all with 0 failed. At the base: 22, 106, 63 (ev/selftests*.txt).
  - Replay over the roster at `0a326689b`: `replay: 447 carries, 5 proposal-sourced, 5 refused`, and with `--cite` `1 refused` (ev/replay*.txt).
- Mutation proof, my own plants beside the fixer's (ev/reviewer_mutants.txt).
  - Killed: `added_texts` not judging a changed brief; `ruling_reader` without the origin/main fallback; held carries re-judged; pulse ignoring the cadence override; `max` -> `min` age; UNREADABLE read as ok; `--seat-queue` refusal disabled.
  - Survived: the DEFER plant, listed under Findings.
  - I did not re-run CI's heavy gate or the mutation table (step 11).
- CI on the head (ev/check_runs.tsv, every workflow concluded):
  - `budget-raise-gate` is red twice. That is by design until the approving review (decision 0013), and the body answers it.
  - `nightly-status` is red, `NIGHTLY ABSENT`. It is not one of the required contexts on `main-protect` and does not block. It grades main's schedule, and the body names its cause, #2627.
  - Every other check is success, skipped or neutral, including `fast (3.14)`, `closures`, `coverage`, `policy-docs`, `instrument-self-tests` and `pr-contract`.
  - Those runs measured the PR merged with `e45fc34fb`, not with `d6308d77c`. That is why they are green while the merged tree is not.
- On the merged tree: `rules_sync --check` is ok, `brief_lint` gives 0 errors, `structure.py` passes, and `policy_lint` gives the one error under Block.
