Fix review: merge 04820384b7cbbf1d7d5a96fc6b103cff7a6da2a6

bus-nonce: a6ca654c7be00d72659d0a1a2718eb38

This is round 2 of review for #2707 (R10-FLY-CIPREDICT-LAYOUT). Round 1 returned `blocked cd7dc09a8 class-open`. Measured head: `04820384b7cbbf1d7d5a96fc6b103cff7a6da2a6`. `git ls-remote` showed it was still the branch head when this verdict was written (`ev/ls-remote.txt`). The head's merge base with origin/main is `806aa2ce89aeb6c00cf756195f31026ab798f3ca`. Live main is now `646dbaa65`. The role contract under `dev/governance/roles/` is unchanged between that merge base and origin/main.

Round 1's block is settled:
- the agreement lane (AGREEMENT arm) and `ref_privacy.py --check` (REF PRIVACY arm) are implemented, with the controls the carries named;
- the census rule is widened to three rules, and they now return step 3f4;
- the round-1 survivors M6, M7 and M8 are pinned by new layout cases.

## Findings

- Surviving mutant R12 (my own): in `privacy_preds`, replacing `else ["the scan found no push site at all, so it checked nothing"])` with `else [])` passes the self-test (rc 0, `ci_predict self-test: 0 failed`, `ev/mut-R12.txt`). The arm's refusal of an empty push-site scan has no case; `ref_privacy.check` refuses the same state in CI. This is a defensive line, outside every mutant the body names, and every mutant the body names is killed. A plant that removes every push site from the scanned paths would pin it. Carry: R10-FLOW-JIDOKA
- At `handoff/audit-r10-roster` `86278a5ae`, R10-FLOW-JIDOKA's roster entry (`carry` and `brief`) does not yet hold three of the body's four `## Forward-carry` items:
  - the handoff seam over `fast`'s always-run `tests/closure.py selftest` and `tests/harness_headers.py`;
  - prepr steps 3f5 and 3h and `selftest_wiring.py --check`;
  - the root-seat `_leaks` substring match in `ref_privacy.py`.

  The base-pinned grader replay and the `ref_privacy`/`tmp_paths` prepr arms are already in its carries (Triage P3 (s4), s6-batch9 P78). Each body line ends `Carry: R10-FLOW-JIDOKA`, a live group, and `carry_audit` routes it, but `finding-propagation.md`'s Enforcement wants the write in the tree before this merges. The train's `roster_edit append-carry` for these three items is owed before the merge. Carry: R10-FLOW-JIDOKA
- `privacy_preds` judges the whole HEAD tree's push-site registry, and judges content against `tmp_paths.ledger_base` (origin/main), not against the predictor's `--base`. The module docstring still says every arm is scoped to what the three-dot diff adds. Carry: dismissed: CI's `ref_privacy.py --check` is whole-tree and origin/main-based in the same way, so the prediction matches CI's verdict; only the docstring sentence overstates, and it costs no wrong prediction.

## Evidence

- Self-test at the head (`ev/selftest.txt`): `ci_predict self-test: 0 failed`, rc 0, 22 cases ok, which is 3 carry, 7 layout, 4 privacy, 7 agreement and the JOB check. Wall time was 2m45s on this seat, with other runs in parallel. The body says 120 s.
- Mutation proof, my own mutants, each a single-occurrence replacement in `tools/pr/ci_predict.py`, run in its own worktree at the head with the file restored afterwards (`ev/mut-R*.txt`):
  - R1, `content_check` with the seat's identity (the body's A2): 4 failed. These are the seat-home null and the three staged-not-committed nulls, matching A2's row.
  - R2, merge onto HEAD instead of the tip (B4's class): 1 failed, the base-tip-registration case.
  - R3, restore pathspecs checked out from the merge instead of the tip (B2's class): 2 failed, the head-only registration red and the `process.exit(1)` null, matching B2's row.
  - R4, lane key without the `.mjs` import walk: 1 failed, the head-only registration red.
  - R8, node never run: 1 failed, the same red case.
  - R12 survives (see Findings).
- Both ends against the RCA controls, re-run in `--shared` clones with `PYTHONPATH=tests/hastub` (`ev/rca-*.txt`):
  - base predictor (`fd7e289d0`'s and `e6dd46277`'s file): rc 0 at #2671 and rc 0 at #2669.
  - head predictor at #2671 `338c9ba49` against `fd7e289d0`: rc 1, with `AGREEMENT RESULT divergent=0 unregistered=3 dead=0 refused=0`, the three UNREGISTERED grammars and `REF PRIVACY REFUSE tools/audit/seat/ledger.py:726`, in 14.7 s.
  - head predictor at #2669 `0506a55b2` against `e6dd46277` (null): rc 0 in 15.4 s.

  This reproduces the body's both-ends table.
- Null control on this head's own diff: `CI PREDICT: no closures, fast, wave-script or instrument red predicted against 806aa2ce89ae`, in 3.3 s (`ev/figures.txt`). That is within the body's 2.9–3.3 s standing cost.
- Figures re-derived at this head against `806aa2ce8` (`ev/figures.txt`):
  - `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`
  - `STRUCTURE RATCHET PASSED`
  - `Architecture score: dS +0.0000 NULL`
  - `ref_privacy --check ... 0 refused`
  - `GUARD: 0 refusal(s)`
  - `tmp_paths: 0 refused`
  - `throwaway_git: 0 ... refused`
  - `selftest_wiring: 93 self-testing, 93 wired, 0 unwired`

  All match the body.
- Census rules re-run (`ev/census.txt`):
  - prepr steps: 29;
  - `instrument-self-tests` `--check` lines in governance.yml lines 243–939: 4, namely tmp_paths, ref_privacy, selftest_wiring and throwaway_git (job bounds at 243 and 940 confirmed);
  - `run_always "$PYTHON"` in tests/run.sh: 4.

  Each open seam the rules return is carried in the body to R10-FLOW-JIDOKA, a live group (see Findings for the write).
- Trigger rate: re-derived as `merges 456 | lane 62 | restore 142` over the body's window, with a probe I rebuilt myself from the body's stated rule (`ev/trigger-probe.py`, `ev/trigger-probe.txt`). The body's probe is not in the tree, so I disclose this one as my own. The cost arithmetic (1.5 s against 3.4 s against the RCA's 4.1 s) follows from these counts.
- I did not re-run `prepr.sh`, the closures recording of `tests/entities.py`, or `carry_audit` on the body. CI's runs on this head are cited instead: `tests / closures` and `pr-contract` are green.
- CI on this head (`ev/ci-checks.txt`): all 53 check runs completed, none red. `pr-contract` concluded success at 17:30:54Z and `gate` at 17:34:46Z, both after the rest. `governance / wave-script`, `governance / instrument-self-tests`, `tests / fast (3.14)`, `tests / closures`, `tests / mutation` and `codeql / Analyze (python)` are success. The round-1 head's `pr-contract`/`gate` red (codescan_wait racing an unfinished Analyze) is answered in `## Red checks`, with the cheaper detector named.
- `git merge-tree --write-tree origin/main 04820384b` exits 0 against `646dbaa65`, the current main (`ev/merge-tree.txt`). There is no conflict and no claim-file conflict.
- VERSION, the manifest version, `RELEASE_NOTES.md` and both claim files are untouched. The three-dot diff touches only `tools/pr/ci_predict.py` and `dev/programme/delivery/2707.md`.
- The body's `## Head` names `04820384b7cbbf1d7d5a96fc6b103cff7a6da2a6`, the head I measured. Its figures were taken at `7ff66e5a5`. The merge commit after that brings in only main's `ref_privacy.py` change from #2700, and the body controlled for it with a throwaway merge. My figures above are taken at this head.
- Architecture (step 15): the three arms call CI's own functions (`layout.guard`, `ref_privacy.sites`/`registry_refusals`/`content_check`, `agreement_py.closure`/`restore_specs`) rather than re-implementing them. Clones go through `throwaway_git_clone`, as other arms in this module do.
