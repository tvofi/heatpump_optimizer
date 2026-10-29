Fix review: blocked ac7353951f00fa953844899eefc85bef14b6b3a0 instrument-broken: the rename breaks the committed dev/audit/harnesses/r10_nightly_pyspy_retry_mutants.py (M0-null fails at head, passes at base) and the body neither fixes nor dispositions it

bus-nonce: 59d3dfabad02212338a16082df1a6b8b

## Round

Round 1 (no earlier verdict ref for #2964 on origin). Measured head ac7353951f00fa953844899eefc85bef14b6b3a0, still the PR head at write time (refs/pull/2964/head). Merge base e5ddba1fad5e6eccfeceaeaaa249bc459963405b = origin/main.

## Block

1. `dev/audit/harnesses/r10_nightly_pyspy_retry_mutants.py` is a committed instrument (in `tests/closures.json`) that mutates the heartbeat control and runs the entities heartbeat block against the current tree. This PR leaves it broken:
   - At base e5ddba1fa: `M0-null all checks pass`, and M1 is killed (ev/pyspy_retry_mutants-base.txt; I cut the run at 200 s, rc=124).
   - At head: `M0-null FAILS: (block did not run: ... NameError: name 'subprocess' is not defined)`. The new `_hb_stdlib_reads` block in tests/entities.py uses `subprocess`, which the harness's extracted block does not import. Then `M2-timeout-30: the mutated site occurs 0 times, not once`, rc=1 (ev/pyspy_retry_mutants-head.txt).
   - Targets M2, M6, M9, X2 and X5 still name `spy_timeout`, `PY_SPY_TIMEOUT_S` and `"py-spy rc=0:"`, which this diff renamed.
   - The body's seam rule (`grep ... tests/nightly_ha.py`) does not look outside that one file, so this consumer of the renamed names was never dispositioned.
   - R10-NIGHTLY-HB-RESPAWN, the group this PR carries to, inherits this control-power instrument ("a stub that never answers ... still fails hb:positive_control").
   - Fix: re-target the harness to the new names, make the extracted block self-sufficient (import `subprocess` in it, or have the harness provide it), and show M0-null passing and the mutants killed at the new head.
2. Correct the body's nightly account in the same round, because it is false at this head (Findings, item 2). The re-run 40835853528 did not fail `hb:positive_control`: its `nightly-ha (stable)` job 123320354418 passed. Its red is `slow` job 123320354392, step "Closed-loop simulation", and that is what `tests / nightly-status` reports on this head. So merging this PR does not turn `nightly-status` green, and `## Red checks` says otherwise.

## Findings

- The PR breaks the committed harness `r10_nightly_pyspy_retry_mutants.py`, which this PR's diff neither re-targets nor dispositions (Block 1). It is owed in this group before re-review. Carry: R10-FLY-NIGHTLY-HB
- The body says "the manual re-run 40835853528 failed the same way", but its nightly-ha (stable) passed and its slow job failed in Closed-loop simulation. Fix the body's opening paragraph and `## Red checks` so they name what nightly-status actually reads now. Carry: R10-FLY-NIGHTLY-HB
- `tests / nightly-status` stays red after this merge on the `slow` lane's Closed-loop simulation failure in dispatch 40835853528 (head 486e65c). The diff does not touch that failure. Carry: dismissed: the orchestrator's on main per defect-root-cause.md ("their red is the orchestrator's on main"); a fix review has no seat to route it, only to name it
- Commit d63e5544d (the roster carry) has author `Claude <noreply@anthropic.com>`, against the dispatch's no-Claude-attribution rule. The code commit 120cd1bb6 and the harness commits are `hpo-fixer`, as the brief requires. Carry: dismissed: not the code commit, and rewriting history on the PR branch is refused; recorded for the orchestrator
- The `SYS_PTRACE` launch comment (tests/nightly_ha.py:3550) still names only py-spy, but the cap now also serves the stdlib unwinder. The body dispositions it as wording only. Carry: dismissed: comment wording, dispositioned in the body; it may ride the re-cut
- No finder's harness is committed for this finding. `dev/audit/harnesses/r10_fly_nightly_hb.py` is the fixer's own instrument, disclosed as such and landed in this PR (fixer.md 18). I could not run it here because this container's Docker daemon is down, so the body's container figures are not re-derived by me (Evidence). Carry: dismissed: disclosed per fix-review step 9; the independent measurement is CI's nightly-ha runs at this head

## Evidence

- RESULT mutation M1 (the body's mutant: delete both predicate lines of `sample_command()`, ev/mutant-M1.diff): `1 of 2473 ENTITY CHECKS FAILED`. The only FAIL that is not in the head's output is "the stall sampler is the interpreter's own unwinder where it ships one, staged or not; else the staged py-spy, nonblocking; else none". Killed.
- RESULT mutation M2 (my own: `_STDLIB_SAMPLE` prints `frame` in place of `f.funcname`, ev/mutant-M2.diff): `1 of 2473 ENTITY CHECKS FAILED`. The only new FAIL is "the stdlib sample of a real spinning process reads as the spin to the control, and of the same process outside it does not". Killed, so the companion check runs against a real process on CPython 3.14.7 and is not vacuous.
- RESULT entities head: `ALL 2473 ENTITY CHECKS PASSED`; base: `ALL 2471 ENTITY CHECKS PASSED` (CPython 3.14.7, PYTHONPATH=tests/hastub). The body quotes 2472/2470, measured at code head 877f4addb over merge base 486e65c. The +2 delta matches; the absolute figures moved by one with the main merge 0e64b5ea8. That is my reading of the shift: I did not run the suite at 877f4addb.
- RESULT positive control on the stable arm: CI nightly-ha (stable) at this head passes `hb:positive_control` on try 1. Its sampler section is the stdlib unwinder's format and names `_hb_spin` (ev/ci.txt). This is one run, against the body's 30-run `--mode side` figure, which I could not re-derive.
- RESULT null control (py-spy unchanged elsewhere): CI nightly-ha (2025.2.0, the 3.13 floor) at this head passes, and its sampler section is py-spy's format (`Thread 13 (idle): "asyncio_3"`), so the floor still samples with py-spy. The entities check pinning `sample_command()`'s four arms passes at head and is killed by M1.
- Figures I could not re-derive: base `--mode probe` 60 runs, ok 59 fail 1 spy_hung 1; fix `--mode side` 30 runs, ok 30 spy_hung 2; N1, N2 and N3 each 2 of 2 fail; the unwinder 6 of 6 in 0.052 to 0.097 s. All of these need Docker and the HA image, and this container's dockerd is not running.
- Verified figures:
  - Scheduled Nightly 40806276912 log reads `FAILED: 2 of 64 checks: ['hb:positive_control', 'run:exit_status']`, as quoted.
  - The body's seam grep returns 13 lines at head, as stated.
  - `python3 tests/structure.py` at head prints `STRUCTURE RATCHET PASSED`.
- Forward-carry: the R10-NIGHTLY-HB-RESPAWN `carry` entry is in dev/programme/rosters/wave-r10-groups.json at this head (commit d63e5544d). It states its control as a precondition: count the nightly-history reds after the fix against the same count before the merge, and build (b) only on a recurrence.
- `git merge-tree --write-tree origin/main ac7353951f00fa953844899eefc85bef14b6b3a0`: exit 0, tree 938bc933a, no conflict (ev/merge-tree.txt).
- VERSION, the manifest version, RELEASE_NOTES.md and both claim files are untouched by the three-dot diff.
- CI at this head:
  - Every concluded check is success, skipped or neutral, except `tests / nightly-status`. nightly-status is not a required check and does not block.
  - Still in progress at read time: fast (3.14), coverage, closures, instrument-self-tests, codeql python, prelude.
  - No `pr-contract` run exists on this head, so I give no root-cause verdict under step 11. The block above rests on the measurement, not on a red check.
- `tests / mutation` is green. This diff writes production lines only under tests/, and I did not read the lane log for whether any mutant was evaluated. M1 and M2 above are my targeted mutants.
- Review packet: rendered at this head, no refusals, carry_audit 2 routed (ev/review-packet.md).
