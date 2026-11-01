Fix review: merge 4455f68483aa4be1ef5f2834225c366c975ff27b

bus-nonce: 16a17e7f63ff5ccf72fff3c2f74b56bc

## Round

Round 3 of this PR. Round 1 (`probe/rev-3066-e2ba7157`) blocked `b1a0be47d`; round 2 (`verdict/3066`) blocked `5a08ec2e9` (root-cause-detectable, three items). This is the last round a repair is allowed in: from round 4, `fixer.md` owes a re-cut.

I measured head `4455f68483aa4be1ef5f2834225c366c975ff27b` from a detached worktree at that SHA. It is the fixer's handoff `76cd77cb0` plus two automatic merges (`25b52d533`, and `4455f6848`, which merges main `1a8051350`). `tools/audit/seat/review_carry.py 76cd77cb0 4455f6848` printed `review_carry: CARRY`. Base ends: merge base `1a8051350` and the round-2 head `5a08ec2e9`, each in its own detached worktree.

Contract: `dev/governance/roles/fix-review.md` at origin/main `fb0a6d5a3`. Main changed it after this PR's merge base (the closing `carry_audit.py check` step was added, two sentences removed). I followed main's text.

## Policy

The diff touches these policy files, all code-owned:
- `dev/governance/rules/claim-files.md`
- its generated copies `.claude/rules/claim-files.md` and `.cursor/rules/claim-files.mdc`

It also touches `.gitattributes` (comment only) and `tools/pr/app_approve.sh` (comment only, from round 1's `bcd5f2657`). **It merges only on the owner's approving review**, which the orchestrator gives under the mandate in force at merge. I do not treat that review as given.

On the merits, the new rule text matches the driver at this head:
- "refuses ... where both sides rewrote one scenario's claims, one fixture's `may-drift` line or the `claims-for:` stamp": rows A, C, C2, D3, E-both-add-differing, H and J2, and stamp row S6, all `refused`.
- "or both changed claims under stamps that differ": S4 and S10 refused. S1 (both sides changed claims, both stamps the same) resolved.
- "a side's change or deletion wins over the other's silence": rows C3, D, D2 and D4, and S2, S3, S7, S8 and S9, all resolved.

`node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`. `rules_sync.mjs --check`: `RULES-SYNC ok`.

## Findings

- The census row e438816e3 prints `hand=differs` (`RESULT hand_differs=1`), and the body quotes the count without saying why. I re-derived it. The driver keeps four claims that the first parent added: `config_flow`, `valve_storage_flat_prices`, `valve_storage_low_target` and `valve_storage_small_tank`. The hand resolution dropped them, and its commit message calls them "main's four inherited claim lines". This follows the driver's rule (a side's added claim wins over silence). Inherited claims are the separate `INHERITED CLAIMS` guard's job, which `ci-autofix.md` repairs. So it is no defect in this diff. Carry: dismissed: the driver's stated rule, and inherited claims are the INHERITED CLAIMS guard's and its autofix's, not the merge driver's

## Evidence

**Round-2 block 1, `tests / fast (3.14)`: answered.**
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` at the head: `ALL 112 HARNESS HEADER CHECKS PASSED`, rc=0 (`ev/harness_headers-head.txt`).
- Both new harnesses (`claim_merge_mutants.py`, `claim_merge_census.py`) inline `repo_root`, byte-identical to `tools/audit/repo_root.py`'s function. Checked by extracting and comparing the function text: `RESULT repo_root byte-identical ... True` for both (`ev/untouched.txt`).
- `tests/harness_headers.py` is untouched against base `1a8051350` (`git diff --quiet`, `ev/untouched.txt`).
- Plant: `ROOT = Path(__file__).resolve().parents[3]` put back into `claim_merge_mutants.py` in a separate worktree gave `1 of 112 HARNESS HEADER CHECKS FAILED`, rc=1, naming `claim_merge_mutants.py:42` (`ev/harness_headers-plant-parents3.txt`).
- The census run from `/` completes and prints the same lines as from the repository (`SAME-FROM-SLASH`, `ev/census-from-root-cwd.txt`).
- CI: `tests / fast (3.14)` job 124855042540 is `success` at this head.
- The body's `## Red checks` names `tests / fast (3.14)` with its cause and the cheaper detector (`harness_headers.py`, in the scoped gate).

**Round-2 block 2, `governance / instrument-self-tests`: answered.**
- `tools/audit/seat/pr_args.sh` is untouched against base (`ev/untouched.txt`).
- `1a8051350` is "Merge pull request #3086 from tvofi/fix/r10-hotfix-uutils-sleep". This head contains it, and `governance / instrument-self-tests` job 124854932385 is `success` at this head. That is the fix observed on this diff.
- I fetched main's job 124813746788 that the body cites (run 41294924835). Its tail shows only the alert_list mutant section, so I did not see the `pr_args` lines in it myself. I rely on round 2's `evidence/ci-reds.txt` for the `unrelated-sleep` / uutils message on this PR's own job 124809082483, and on the body's quotation for main's run.
- The body names the cause and the fixing group (R10-HOTFIX-UUTILS-SLEEP), and records that no off-runner detector exists. It does not cite `#3086` by number.

**Round-2 block 3, `pr-contract`.**
- `## Head` names `4455f68483aa4be1ef5f2834225c366c975ff27b`. The stale "no CI run yet" text is gone.
- `## Red checks` names every red at `5a08ec2e9`: `tests / fast (3.14)`, `governance / instrument-self-tests`, `pr-contract` and `gate`.
- At this head, every check-run concluded so far is success, skipped or neutral (41 runs, one page of 100). CI state at verdict time is under "CI".

**S1 change (`76cd77cb0`): mutation-proven.**
- Stamp probe (round-2 reviewer's `stamp_probe.py`) at `5a08ec2e9` and at this head: only S1 changes, `refused` to `resolved stamps=['# claims-for: 7.0.5'] claims=['alpha','beta','delta','gamma']`. `diff` of the two outputs shows that one line alone (`ev/finder-r2.txt`, `ev/finder-head.txt`).
- My own mutants of the new guard, run with round 1's `cmrun.py` over a copy of this head's `tests/` (`ev/mutants-head.txt`):
  - O-guard-three-way (round 2's guard restored): `1 of 31 CM FAILED`
  - O-no-guard: 1
  - O-guard-base-vs-ours: 2

**Finder's harness at both ends** (round 1's `adv.py`, `adv2.py` and `m3probe.py`, and round 2's `stamp_probe.py`, all unchanged):
- Base `1a8051350`: 11 OK / 6 FAIL. The base driver refuses where the fix resolves.
- `5a08ec2e9`: 17 OK / 0 FAIL.
- This head: 17 OK / 0 FAIL, plus `RESULT D2c may_drift_error: None` and `RESULT theirs-deleted alpha: ['beta', 'gamma']`.

**Earlier repairs still hold.** Round 1's `mut.py` and round 2's `plant.py`, each through `cmrun.py`; the unmutated null gives `ALL 31 CM PASSED`:
- M1: 11 of 31 failed
- M2: 6
- M3: 4
- M6: 1
- R-mine-eq-main-only: 2
- P-D2-no-cut: 5
- P-D2-no-cut-no-defect: 6
- P-D3-ignore-marker-refusal: 2
- P-D3-ignore-refusal-and-defect: 4
- P-stamp-not-marker: 3
- M4 has no anchor at this head. O-no-guard is its re-spelling, and it is killed.
- R-keep-deleted in round 1's spelling raises `NameError` (CM rc=1), as round 2 recorded. The fixer's harness carries a re-spelled copy, which is killed.

The fixer's `claim_merge_mutants.py`, which I ran as evidence and not as the judge: `RESULT baseline_pass=1`, `killed=16`, `survived=0`, `stale=0`. This equals the body.

**Figures re-derived at this head.**
- Census, driver `f4a5082a6`: `resolved=0`, `refused=7`.
- Census at this head: `resolved=5`, `refused=2`, `hand_same=1`, `hand_differs=1`. The per-row ours/theirs/overlap counts equal the body's: 5/1/0, 41/1/0, 41/5/0, 5/5/5, 3/1/0, 4/41/0 and 45/50/42 (`ev/census-*.txt`).
- The body's `CM 31` and the mutant counts above equal mine.
- Not re-derived: the body's "8 of 30 failed with `b1a0be47d`'s driver" and its prepr rc line. Those are round-2-era and fixer-run figures, and I did not rebuild them.

**Standing checks.**
- Delivery row: `dev/programme/delivery/3066.md` is added in the three-dot diff.
- Claim files: `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt` are byte-identical to base `1a8051350` and to `f4a5082a6`. `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched (`ev/untouched.txt`).
- `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 1a8051350`: `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE: 56`, rc=0. `--claims-only 1a8051350`: `claims hygiene: ... ok`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `tests/closure.py select --diff <merge-base>`: `MODE: SCOPED -- 7 script(s) run, 26 scoped out.`
- With the claimnotes driver installed, `git merge-tree --write-tree origin/main 4455f6848` gave rc=0 with no conflict and no MERGE-CLAIM line. I ran it at main `fb0a6d5a3` and again at `bc56483a8` just before the push (`ev/merge-tree.txt`).
- Architecture score: CI's `arch-score / arch-score` is success. The body states `dS +0.0000 NULL`, which I did not re-run.

**Class.** The body's stamp enumeration (`grep -nE "CLAIM_VERSION_MARKER|_parse_claims\(" tests/env_drift.py`, round 2's rule) dispositions every site. The only stamp comparison this repair changed is the guard at `tests/env_drift.py:1806`. S1 to S10 cover that guard's domain (which side bumps, crossed with which side changes claims).

**CI.** `python3 tools/audit/seat/merge_train.py classify 4455f68483aa4be1ef5f2834225c366c975ff27b` exited 0 at 13:35:27Z: `GREEN 4455f68483aa4be1ef5f2834225c366c975ff27b pending: none red: none` (`ev/classify.txt`, `ev/classify.log`). No check concluded red at this head, so step 11 owes nothing new at this head. Before the push I re-read the PR branch head with `git ls-remote`, and it was still the SHA measured (`ev/heads-at-post.txt`).
