Fix review: merge b69828eb4a056850e7fc8914e6cde391f04743df
bus-nonce: f28528ad3234536c0ea115bf2fd72abb

Head reviewed: `b69828eb4a056850e7fc8914e6cde391f04743df`. `refs/pull/2853/head` re-read immediately before this verdict was written. Worktree `~/hpo-seats/r10s6/review-2853-r4/`, detached at the head and created by me; the main checkout and the fixer's tree were not used. Round: the fifth review and the fourth code head measured. Three `blocked` verdicts precede it — `915fef90c` on `fa18c13d2`, `23e775ee4` on `2724c87bb`, `09b2be3f3` on `fccb88371` — and this verdict tests all three against this head, not only the last. The body carries the `## Re-cut` note `fixer.md`'s past-three-rounds rule requires. Diff, three-dot from merge base `4db1d3e28`: 7 files, 522 insertions, 44 deletions. The head's merge of `origin/main` touches none of the four changed code files — `git diff bde48ac1 HEAD -- tools/pr/prepr.sh dev/audit/rounds/round4/D6/claims.py tests/harness_headers.py tools/audit/seat/body_push.sh` is empty — so the authored code at this head is `bde48ac1`'s, and the figures the body takes there describe the code I measured.

## B1 — the last block paid: step 6g's per-target interpreter

`09b2be3f3` found `claims_reg_line`'s derivation spawning `python3 -I -c` once per link target: 84 spawns, 2.84–3.12 s of the check's CPU, total 6.63–6.85 s (6.85–7.09 s with the copy) against the owner's 5 s per-added-check cap. Repair `2d63555e6` replaces that one line with `rel=${t#./}; case $rel in /*|..|../*) continue;; esac`.

My instrument, mine and not the fixer's: `claims_reg_line` and its constants extracted verbatim from the head into `~/hpo-seats/r10s6/review-2853-r4-ev/fx_head.sh` (`diff` against `prepr.sh` lines 243–255 and 293–387 empty), driven exactly as the step drives it — a `git archive HEAD -- $CLAIMS_INPUTS $CLAIMS_GEN` copy, then the function on it — timed with `/usr/bin/time -p`, CPU = user+sys. The pre-repair variant `fx_spawn.sh` is that same file with this one line restored to `2d63555e6^`'s and nothing else changed (`diff` is one 1-for-3 line replacement).

**(a) The check's CPU cost at this head.** Five runs, 8 cores, load 129–139: copy 0.26–0.28 s; `claims_reg_line` 3.85–4.08 s; **total 4.11–4.35 s CPU** — under the 5 s cap by 0.65 s at the worst run. Same host, same hour, the pre-repair line measured function 7.08–7.28 s, total 7.35–7.56 s, so the separation the block measured is reproduced. The body's 3.99–4.10 s and the delivery row's 3.99–4.10 s agree with mine in order and in margin.

**(b) Interpreter spawns.** **Three per `claims_reg_line` call, zero per target**: `python3 -I … claims.py --print-link-targets`, `python3 … claims.py` (the generator), and the header `-c`. Counted with a `python3` shim first on `PATH` that logs every invocation (`spawn_count.txt`). The pre-repair line makes 84 more on this tree — 87 total — and 88 on my fixture A, which carries one added link.

**(c) The derived target set, as a set.** The raw **string** sets are *not* equal: 38 distinct values under `os.path.normpath`, 40 under the shell, because nine `docs/../x` targets keep their `docs/../` prefix instead of being collapsed (`target_set_equality.txt`). **No target is dropped, and the copy the step grades is identical.** Three measurements, not a count:

1. On this head all 84 targets are already inside the copy, so the archive arm fires **zero times under either variant**: `RESULT targets=84 already_present_in_copy=84 archive_actions=0` (`archive_actions_head.txt`).
2. On two fixtures that make the arm fire — A, a link to `tools/audit/seat/INSTRUMENTS.md`, outside `CLAIMS_INPUTS`; B, `docs/../tools/pr/prepr.sh`, the divergence shape and also outside the list — the head and pre-repair variants produce **byte-identical copies** (`f38e9751…` and `8dd1ee4c…` each way) with the target present after both and the same pass line.
3. `git` normalises the `docs/../x` form in both `ls-tree` and `archive` (`git archive HEAD -- docs/../tests/README.md` extracts `tests/README.md`) and `test -e` resolves it. The one shape the shell no longer refuses at the string stage — an embedded `..` that `normpath` would have made leading, `docs/../../x` — still copies nothing: `git ls-tree` exits 128 *outside repository* and `git archive` extracts 0 files.

**(d) Graded verdicts unchanged.** Six arms at both variants, identical rc and identical message: A unlisted target rc 0 (copied); B `docs/../` unlisted target rc 0 (copied); C stale register rc 1; D target absent from the repository rc 1 (not copied); no docs change rc 3. The copies are byte-identical in every arm. The register itself re-records byte-identically at this head (5 of 5 runs: "rewrites claims.json and claims.md byte-identical, its header RESULTs hold").

## B2 — the three earlier blocks, each against this head

**Round-1 budget (`fa18c13d2`, `915fef90c`) — paid.** Its 6g item is (a). Its `--fill-red` item, "the wall time `--fill-red` adds to every body_push is not stated", is answered: `## Figures` states it in wall with the load beside it and in CPU, 2.86–3.16 s at `a0e741cf`, against 5.66–5.80 s for the whole predictor it replaced. I re-measured `bash tools/pr/prepr.sh --fill-red <body>` at this head: **3.42–3.71 s CPU**, wall 8.69–14.55 s at load 200–221 — under 5 s on CPU, wall tracking the host as the body says. The `8 s`/`15 s` restatement is withdrawn, not carried: its only occurrence is the sentence withdrawing it.

**Round-1 class-open (`2724c87bb`, `23e775ee4`) — paid.** The derivation is present and `2d63555e6` does not narrow it. Fixtures A and B show the narrow copy taking a link target the enumeration does not name (target present, rc 0), the whole-tree control passing rc 0 at both, and the derivation dropped reddening both (B3). The copy is not narrowed anywhere else in the re-cut.

**Round-2 budget (`fccb88371`, `09b2be3f3`) — paid.** B1 pays the budget item. Its B2 secondary, a delivery row asserting a clearance the class-open block had refused, is answered: `dev/programme/delivery/2853.md` now names all three blocks and what this head does about the class-open one and the 6g budget. Its B3, figures stopping at the pre-repair tree, is answered: the 6g and self-test rows are re-taken at `bde48ac1`, the `claims.py` change has its own bullet, and `prepr-13` — the derivation dropped — is reported as pinned by perturbation.

## B3 — perturbation

The repair's load-bearing line, not a comment: `rel=${t#./}; case $rel in /*|..|../*) continue;; esac` replaced by `rel=""; continue` (every target dropped) in a copy of the extracted function, nothing else changed (`fx_perturb.sh`). Fixtures A and B go from **rc 0 with the target copied** to **rc 1 with it absent** — `committed claims.json claims.md not what dev/audit/rounds/round4/D6/claims.py writes; header RESULT moved: claims_true=122 (header 123) claims_false=1 (header 0)`. C, D and the skip arm do not move. Restoring the head's line returns A and B to rc 0 with the target present. The in-tree mutant `prepr-13` has the same shape (`done < /dev/null`) and its pattern matches the head's line exactly once, so the arm is pinned in the tree as well as by me.

## Accepted, with the measurements that decided it

The head's checks all concluded: **55 check runs, 38 success, 17 skipped, 0 failure, 0 neutral, 0 pending** (`check_runs_head.tsv`). `gate` success twice (the last at 19:31:43Z), `pr-contract / pr-contract` success twice, `governance / instrument-self-tests` success in 18m46s, and `tests / fast (3.14)`, `tests / mutation`, `tests / closures`, `arch-score` and `budget-raise-gate` success. The PR workflow runs on the merge ref `872c44829`; `git rev-parse 872c44829^{tree}` equals the tree `git merge-tree --write-tree origin/main HEAD` prints locally, so CI's verdict is about the tree I measured.

`git merge-tree --write-tree origin/main HEAD` exits 0 against the body's cited tip `2b45d098c`, the head's own base `4db1d3e28` and the current `origin/main` `6eb552157`.

`VERSION`, the manifest version, the `RELEASE_NOTES.md` heading, both claim files and every `tests/*_budgets.json` are untouched, three-dot from the head's own base as well as from `origin/main`. No budget is raised. `python3 tests/env_drift.py --claims-only origin/main` prints `claims hygiene: origin/main ok`. No Co-Authored-By, Generated-With or session trailer is on any authored commit.

`bash tools/pr/prepr.sh --body-check` on the real body exits 0: `figures ok: 17 resolved, 2 not verified, 0 refused`; `ref_privacy ok … 28 file(s) …, 479 line(s) added …, 0 refused`; `preflight ok`; `pr-body ok: 0 error(s)`. The body's `## Red checks` names the two historic reds with their check runs and counts and answers each, and `pr-contract` — which reads the body — is green at this head.

`python3 tools/audit/carry_audit.py pr 2853` on the draft, before this verdict published: **11 finding item(s): 11 routed, 0 unrouted, 0 bad destination(s)**. Re-run on the PR with this verdict at `refs/hpo-bus/review/2853`: **13 finding item(s): 13 routed, 0 unrouted, 0 bad destination(s)** — the two added are this verdict's own bullets, each carrying `R10-FLOW-JIDOKA`.

The cost of the added checks against the owner's second cap holds at this head: a prepr run adds 6g 4.35 + `ref_privacy` 1.26 + `check-wave-script` 0.25 = 5.86 s CPU, and a `body_push` adds `--fill-red` 3.71 + `figure_lint` 0.11 + `ref_privacy` 1.26 = 5.08 s, both under 10 s.

## Findings (non-blocking)

- The repaired cost is pinned by no check. `prepr-13` guards that the derivation runs, not what it costs, so a future change that reintroduces a per-target interpreter would put this check back over the owner's 5 s cap with nothing in the tree failing — only a reviewer's timing catches it. The margin is 0.65 s, 4.35 against 5.0, which is real but not large. Carry: R10-FLOW-JIDOKA
- The closing paragraph of `## Head` names merge base `34cd75bf1` and `origin/main` at `2b45d098c`. Those are the *figure-taking* head `bde48ac1`'s merge base and tip; this head merges `origin/main` `4db1d3e28`, so its merge base is `4db1d3e28`. No figure is invalidated — the code is identical and I re-took the 6g and `--fill-red` figures at the head — and the section's first paragraph names the head and its merge correctly, but the two paragraphs disagree about which tree the figures describe. Carry: R10-FLOW-JIDOKA

## Evidence

`~/hpo-seats/r10s6/review-2853-r4-ev/`: `fx_head.sh`, `fx_spawn.sh`, `fx_perturb.sh` (the three function extractions, diffed against each other and against the head), `drive6g.sh` and `time6g.sh` (my instruments), `timing_head.txt`, `timing_spawn.txt`, `target_set_equality.txt`, `archive_actions_head.txt`, `spawn_count.txt`, `containment.txt`, `body_check.txt`, `check_runs_head.tsv`, `merge_tree.txt`, `untouched.txt`, and `mkfixtures.sh`, which rebuilds the four fixture repositories deterministically from the reviewed head (I verified it reproduces the copies byte-for-byte: manifests `f38e9751…` and `8dd1ee4c…`).

## What could not be established

The self-test's 417 count. `governance / instrument-self-tests` is green at this head, but I did not re-run the 18-minute job — the contract says cite CI's heavy runs rather than re-run them — so the conclusion is established and the count itself is not.

The fixer's own host figures. Both sides of every before/after pair are same-host and same-hour, and the measure is `user+sys`, which the body itself declares load-independent; my wall figures at load 200+ are far above the body's at load 20–70 with the same CPU, which is what the body's disclaimer predicts.
