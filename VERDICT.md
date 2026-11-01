Fix review: blocked 5a08ec2e93f715504ac98d7cd5adb87382cbef2e root-cause-detectable: tests / fast (3.14) is red on this PR's own new harness (claim_merge_mutants.py hand-rolls a parents[3] depth root that tests/harness_headers.py refuses), and ## Red checks says none; python3 tests/harness_headers.py, in the scoped gate, shows it before the handoff

bus-nonce: 64f243704e5f2706389e7fa73bcc57fe

## Block

The round-1 block is answered: D2, D3, M3 and R-mine-eq-main-only are each repaired and pinned, and the stamp class is closed (Evidence). This head is blocked on its own CI, under fix-review.md step 11.

1. **`tests / fast (3.14)` is red because of this diff, and the body does not name it.**
   - **The failure.** `tests/harness_headers.py` fails 1 of 112 checks: `FAIL every inlined walk matches the canonical helper and no depth root remains [FAIL depth seams: dev/audit/harnesses/claim_merge_mutants.py:28: ROOT = Path(__file__).resolve().parents[3]`.
   - **Its source.** The harness is new in this PR (`30a7a59a5`). The depth-seam rule (`845f2fd8b`, "Find audit harness roots by walking up to the manifest") is already present at the code head's own base `2b6bef745`, so the red was there to see before the handoff. I reproduced it locally at this head (`ev/harness_headers.txt`).
   - **The cheaper detector.** It is `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: about 2 minutes, and one of the 7 scripts the body's own `MODE: SCOPED -- 7 script(s) run` selects. CI's fast lane ran it as a scoped script.
   - **The repair.** Find the root with the canonical walk-up helper the rule names, not `parents[3]`. Then re-run the scoped gate.
2. **`governance / instrument-self-tests` is red, and the body does not name it either.**
   - **The failure.** `pr_args self-test: 158 checks, 2 failed`: `open_pr: the null control -- an unrelated sleeper survives` and `null control: a normal successful update_pr leaves nothing behind and stops nothing it did not start`.
   - **Likely cause.** The log shows ``Security violation: Requested utility `unrelated-sleep` does not match executable name: /usr/lib/cargo/bin/coreutils/sleep``. That reads as the runner's multicall `sleep` refusing the self-test's symlinked `unrelated-sleep` (`tools/audit/seat/pr_args.sh:625`), a file this diff does not touch. It points to the runner, not this diff, but I did not check main's runs for the same red.
   - **What it still owes.** It is a gate check, and the body has to name it and answer it. If it is the runner, the answer is the finding that no cheaper detector exists.
3. **The `pr-contract` result.** `pr-contract` job 124817627544 started at 10:09:56Z, after the last red concluded at 09:55:26Z. It read the body and refused it: "check `governance / instrument-self-tests` is red and `## Red checks` does not name it", and the same for `tests / fast (3.14)` (`PR-BODY: 2 error(s)`). The body's "`## Red checks` none ... This head has had no CI run yet" is stale.

**Round.** This is round 2, so a repair is still allowed. From the fourth round, `fixer.md` owes a re-cut.

The code fix itself measured clean. I found no class-open seam and no surviving mutant at this head. Once the harness root is repaired and `## Red checks` answers both reds, the measurements below should carry, apart from the CI state.

## Round

Round 2, the second review of this PR. Round 1 (`probe/rev-3066-e2ba7157`) blocked `b1a0be47d`. I measured head `5a08ec2e93f715504ac98d7cd5adb87382cbef2e` from detached worktrees at:
- this head
- the round-1 head `b1a0be47da301a23025cf40671053b5dbf6b129b`
- the merge base `f4a5082a666fcffc4968ed6bc540a6ab3e267c63`

`dev/governance/roles/` has no change on main since the merge base, so the contract I followed is current.

## Policy

The diff changes `dev/governance/rules/claim-files.md` and its generated copies, under mandate 6329234399. **It merges only on `tvofi`'s approving review at its head** (or under an agent mandate in force), so the merge needs that approval. I did not block on its absence. I checked the new text against the driver:
- "merges three-way claims per scenario and `may-drift` lines per fixture: a side's change or deletion wins over the other's silence": holds. See rows C3, D, D2, D4 and I, and stamp rows S2, S3, S7 and S8.
- "refuses, naming them, where both sides rewrote one scenario's claims or one fixture's `may-drift` line, or stamped differing `claims-for:`": holds. See rows A, C, C2, D3, E-both-add-differing, H and J2, and stamp row S6.
- The driver refuses in one case the text does not list: both sides bump the stamp identically and change disjoint claims (S1). It refuses there, so it widens nothing. See Findings.

## Findings

- When both sides bump `claims-for:` to the same release and change disjoint claims, the driver refuses (`ev/stamp_probe.txt` S1), although the new text lists no refusal for this case and the stamp's own per-key rule (`mine == main`) accepts it. The cause is `merge_claim_decision`'s stamp guard (`tests/env_drift.py` near line 1805). It requires `base == ours == theirs` whenever both sides changed claims, where the marker rule compares the stamp three-way. This direction refuses and widens nothing, and the base and round-1 drivers refuse it too. It is the last stamp comparison that does not use the per-key rule. Carry: R10-996-RUNNER-CLAIMS
- The PR body states no `prepr.sh` result line, although the brief's gate asked for "full prepr rc=0 at this head". I did not run `prepr.sh`. Its CI re-execution, `pr-contract / pr-contract`, is red at this head on the body's `## Red checks` (see Block). Carry: R10-996-RUNNER-CLAIMS

## Evidence

- **Finder's harness**: round 1's own `ev/reviewer-instruments/` (`adv.py`, `adv2.py`, `m3probe.py`, `mut.py`, `cmrun.py` and `replay.sh`), taken from `probe/rev-3066-e2ba7157` and run unchanged at both ends. I did not run the fixer's driver in its place. My own additions are disclosed under `ev/reviewer-instruments/`:
  - `stamp_probe.py`, a stamp-class probe
  - `plant.py`, my plants
- **D2 is fixed.** `adv.py` at `b1a0be47d`: `D2-ours-del-flat-theirs-edit-wood: resolved FAIL`, with the suspended `flat_prices` line reinstated beside both `wood_coil` wordings. At this head: `resolved OK`, with md=`['# may-drift: wood_coil -- machine-sensitive (reworded)']` (`ev/adversarial.txt`).
- **D2c is fixed.** `adv2.py`, D2 with its claim: at `b1a0be47d` `may_drift_error: CLAIMED AND MAY-DRIFT`; at this head `None` (`ev/d2c-m3probe.txt`).
- **D3 is fixed.** At `b1a0be47d`: `D3-widen-theirs-del-ours-reword: resolved FAIL`. At this head: `refused OK`, `CONFLICTING MAY-DRIFT OR STAMP`, naming `may-drift: flat_prices` with both sides' lines.
- **Null control for D2 and D3:**
  - `D4-both-delete`, `D` (a may-drift deletion beside a neighbouring claim edit), `I-disjoint` and both `E-both-add-identical` rows resolve OK at both heads.
  - `adv.py` totals: 15 OK / 2 FAIL at `b1a0be47d`, 17 OK / 0 FAIL at this head. That equals the body's figure.
- **M3 (round 1's Block 2) is killed.** `m3probe.py` gives `['beta','gamma']` at both heads. It was never a defect, only an unpinned mutant. Round 1's `mut.py` M3 at this head: CM rc=1, 5 FAIL lines, first `a claim main deleted and this branch left alone stays deleted` (`ev/mutants-r1set-head.txt`).
- **R-mine-eq-main-only is killed.** At this head: CM rc=1, first `a claim both sides added identically resolves, kept once [merged=None]`. Its null, the legitimate identical-add merge, still lands: `E-both-add-identical` and `E-both-add-identical-plus-disjoint` give `resolved OK` at this head.
- **Round 1's other mutants are killed at this head:**
  - M1: 11 FAIL lines
  - M2: 7
  - M4: 2
  - M6: 2
  - R-keep-deleted: CM rc=1, with 2 of 30 checks failed. The round-2 split moved the decision into `_decide_per_key`, which has no `base` in scope, so I re-spelled this mutant as a base-block reinstatement inside `merge_claim_decision`. In round 1's own spelling it raises `NameError`.
  - M5 mutated the removed two-way survival check, so it has no anchor at this head.
- **My plants, each omitting one part of the fix** (`ev/plants-head.txt`). Every one is killed by the committed CM section:
  - P-D2-no-cut: 5 red. Here adv D2 refuses rather than resolving, because the defect check still catches it.
  - P-D2-no-cut-no-defect: 6 red, and adv D2 again `resolved FAIL`.
  - P-D3-ignore-marker-refusal: 2 red, and adv D3 `resolved FAIL`.
  - P-D3-ignore-refusal-and-defect: 4 red.
  - P-stamp-not-marker: 3 red.
- The fixer's `claim_merge_mutants.py` at this head gives `RESULT baseline_pass=1`, `killed=15`, `survived=0` and `stale=0`, which equals the body's figure (`ev/claim_merge_mutants.txt`). Unmutated, the CM section gives `ALL 30 CM PASSED` at this head and `ALL 20 CM PASSED` at `b1a0be47d`.
- **Third instance, the `claims-for:` stamp, with the class opened.** `grep -nE "CLAIM_VERSION_MARKER|_parse_claims\(" tests/env_drift.py` finds every place the stamp is read or compared in the driver and its defect check:
  - `merge_claim_decision` near line 1805 compares the parsed first stamp `base == ours == theirs` when both sides changed claims.
  - `_marker_key`, `_marker_blocks` and `merge_marker_decision` merge the stamp lines three-way, compared verbatim, and `merge_claim_file` refuses on a marker refusal.
  - `merge_claim_defect` checks that the stamp survives and that the exact marker-block equality holds both ways.
  - `merge_claim_refusal` names the stamps or the marker keys.
  - `_marker_key` and `_parse_claims` use the same predicate (an empty body and a note starting with the marker), so the merge and the reader see the same stamp lines.

  `stamp_probe.py` at base, `b1a0be47d` and head (`ev/stamp_probe.txt`):
  - S7, S8 and S9 (one side bumps, the other edits a note beside the stamp) left two stamp lines at base and at `b1a0be47d`. At the head they leave one, the bumped stamp.
  - S6 (both bump differently, with no claim change) resolved with two stamps before. It now refuses.
  - S1, S4 and S10 (claims changed under differing stamps) refuse at all three ends.
  - S2, S3 and S5 (only one side bumped the stamp, and the other side's claim change or silence) resolve with that side's stamp, unchanged from base. That is the text's "change wins over silence".
  - S1 is the one leftover (Findings).
- **Seam census rule** from the body: `grep -nE "startswith\((CLAIM_VERSION_MARKER|MAY_DRIFT_MARKER|SHAPE_CLAIM_MARKER)\)" tests/env_drift.py`. Re-run at this head, it returns the body's sites, and every kind is dispositioned. `_may_drift`, `_is_may_drift` and `_marker_key` key a may-drift line by the same rule: an empty body, the marker, and the name before `--`.
- **Null replay**: round 1's `replay.sh` over P196's seven merges, run as git invokes the driver (`ev/replay.txt`):
  - At the merge base, all 7 refuse.
  - At `b1a0be47d` and at this head, #2841, #2745a, #2745b, 3a07c2eaa and e438816e3 resolve, and #2834 and 5bf232eac refuse.
  - `cmp` of the merged files between the two heads gives `SAME` for all seven, which equals the body's figure.
- **Merge with main**: `git merge-tree --write-tree origin/main 5a08ec2e9…`, with origin/main at `92588d581`, gives rc=0 and no claim-driver line, because the claim files are untouched (`ev/merge-tree.txt`).
- **The head's own merges**: `git show --remerge-diff` of `5a08ec2e9` and `da18c2a6b` is empty apart from the ledger driver's `closures.json` set-merge. There is no hand resolution, and `30a7a59a5` is the authored code head the body names.
- **Claim files**: byte-identical to the merge base and to origin/main (`ev/claims.txt`). `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched (`ev/version.txt`).
- **`env_drift.py --all f4a5082a6`** at this head: `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56`, rc=0.
- **`tests/structure.py`**: `STRUCTURE RATCHET PASSED`.
- **`policy_lint.mjs`**: `TOTAL: 0 error(s) across 50 policy file(s)`. `rules_sync.mjs --check`: `RULES-SYNC ok`.
- **`archscore --diff f4a5082a6`**: `Architecture score: dS +0.0000 NULL`. No budget, ledger or calibration figure moves. The `tests/closures.json` change classifies the two new harnesses, and nothing else.
- **Scoped gate**: `closure.py select --diff f4a5082a6` (the merge base at this head) gives `MODE: SCOPED -- 7 script(s) run, 26 scoped out.`, the body's figure. The body's command names the older base `2b6bef745`. At this head that command prints `MODE: FULL`, because main's own newer commits enter that diff. The body measured it at `30a7a59a5`, whose merge base was `2b6bef745`, so the figure stands for the code head and re-derives at the current merge base.
- **Delivery row**: `dev/programme/delivery/3066.md` is in the three-dot diff.
- **Forward-carry**: Carry 3 (P214) is on `origin/handoff/audit-r10-roster` at tip `806d2db83`, in group R10-996-RUNNER-CLAIMS, with its `edit-brief` precondition stated ("no fix touches the bot before it lands"), as the body says.
- **CI at this head** (`ev/ci-reds.txt`):
  - `merge_train.py classify` printed `RED 5a08ec2e9... pending: none red: gate` and exited 1.
  - `get_check_runs` read 55 runs. These failed: `tests / fast (3.14)`, `governance / instrument-self-tests`, `pr-contract / pr-contract` (twice) and `gate` (twice). Every other run succeeded or was skipped.
  - `tests / mutation` is green.
  - The `tests / fast (3.14)` red reproduces locally: `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` at this head gives `1 of 112 HARNESS HEADER CHECKS FAILED`, rc=1 (`ev/harness_headers.txt`).
- **Body figures I did not re-derive**:
  - the per-row census counts (#2841 5/1/0, and the rest). I re-ran the replay, not the census.
  - the "8 of 30 failed with `b1a0be47d`'s `env_drift.py`" failing-first figure
