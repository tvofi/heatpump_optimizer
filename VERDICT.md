Fix review: blocked 33660280381756f968ee197f374e9254eecfde19 countermeasure-silenced: owed_unactioned.py takes its own printed ack template as a live acknowledgement, so logging its output in the seat ledger turns 12 unactioned keys into exit 0

bus-nonce: 6f93cb1ec9cf1b0516fac9aafcdccaad

Round 1. Head measured: 33660280381756f968ee197f374e9254eecfde19, which is also the head the body names. Base and merge base: b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa, which is origin/main when I measured. `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract I followed is current.

## Block

- **The ready ack line the tool prints is a valid `OWED-ACK`.** For each UNACTIONED key, `run()` prints `ack: OWED-ACK <now> <key> <sha> ttl=1 <next action, by whom; what it waits on>`. `ACK` is matched with `.search`, so the `ack: ` prefix does not stop it, and the placeholder passes as the reason `(\S.*)`. Nothing refuses a placeholder reason. Step (5) of `sweep_template.md` reads acknowledgements from {{seat_ledger}}, and the same template tells the sweep to log in {{seat_ledger}}. So one sweep that logs the tool's output verbatim acknowledges every key for an hour.
- Reproduction is in `ev/attacks.txt` section A. I used the in-tree boards `tick-1904` and `tick-1912` with a fresh state. The tool prints 12 UNACTIONED and exits 1. Next I fed that output back unedited as the only `--acks` file. The tool then printed `12 acknowledged, 0 unactioned`, each with reason `<next action, by whom; what it waits on>`, and exited 0.
- This is the failure `defect-root-cause.md` names: "a check that passes while the bug is present". The record's class is a handling recorded without being done, and an unfilled template is that exactly. The self-test's "free text ... covers nothing" check does not cover it, because the template line is not free text.
- The fix belongs in this PR. Refuse an `OWED-ACK` whose reason still holds the placeholder (or any `<...>` placeholder). Make the printed template unparseable as an ack as it stands, for example by leaving the time slot as `<UTC>`. Add a self-test check that feeds `run()`'s own output back as the ack file and expects exit 1, plus the mutant that removes the refusal.

## Findings

- **An id of one hex character is accepted.** In the cover predicate, `x.startswith(a[0])` takes an id of any length. So `OWED-ACK <t> #2887 1 x` covers `#2887` on any tip that starts with `1` (`ev/attacks.txt` section B: `1 acknowledged`). The docstring says "a new tip needs a new acknowledgement". A short id defeats that for about 1 in 16 new tips per hex character it leaves out. The reverse direction already needs `len(a[0]) >= 7`, so the fix is the same floor on both directions (except `-` and the ledger's non-sha ids), plus a self-test check. Carry: #2930
- **A state file with `keys` present but malformed entries crashes the tool.** If an entry lacks `first` or `sweeps`, `run()` raises an uncaught `KeyError`/`TypeError`. That exits 1, the UNACTIONED code, instead of 2, UNREADABLE. Only the top-level `keys` object is validated (`ev/malformed_state.txt`: `KeyError: 'first'`, rc=1). The cost is low because the tool is the only writer of the state file. Carry: dismissed: the state is written only by this tool through an atomic replace, so the path needs a hand edit; the fixer may fold it into the re-cut at no cost

## Evidence

- `ev/HEAD.txt` holds the reviewed head.
- `ev/review-packet.md`, rendered here: Refusals none, Advisories none. CARRY-AUDIT reports 0 finding items. figure_lint reports 7 resolved, 0 not verified, 0 refused. Finder's harness: none named. The finding has no committed finder harness, because the instance is an RCA (`defect-root-cause.md`) and its instrument is the fixer's own, disclosed as such in the record.
- Self-test at the head: `owed_unactioned self-test: 21 checks, 0 failed` (`ev/selftest.txt`).
- Mutation proof re-run: `mutants: 10, not killed 0`. The per-mutant red counts match the body's table: 5, 1, 1, 1, 1, 3, 1, 1, 1, 1 (`ev/mutants.txt`). None of the 10 mutants touches the ack-reason or id-length predicates above.
- Live boards re-run with an empty ack file (`ev/live_rerun.txt`), outputs identical to the committed `live_out.txt` apart from the ack-file count line:
  - `tick-1904`: 12 keys, rc 0.
  - `tick-1912`: 12 unactioned, rc 1.
  - Null control, all acknowledged: rc 0.
- Figures I could not re-derive, because their inputs are session files not in the tree (`<session>/orch-sweep.log`, `cloud-relay.log`, `ORCH-QUEUE.md`, `seat-ledger.md`, `~/.local/state/hpo/dispositions.tsv`, the orchestrator transcript):
  - the 31-board replay (30 of 31 exit 1, mean 5.6; acked 31 of 31);
  - 19 reads and 15 filtered;
  - 33 `HELD-REVIEW #2916` passes;
  - `disposed=2`;
  - the instance hours 5.7, 5.6 and 1.9;
  - owed block at line 56 of 65;
  - the session queue's 0 `OWED-ACK` lines.
  The committed `replay_out.tsv` and `replay_acked_out.tsv` are their outputs as recorded, not re-taken.
- `sweep_render.py --self-test`: 21 checks, 0 failed. `{{orch_scratch}}` is a declared placeholder at `sweep_template.md:33`.
- `selftest_wiring.py --check`: `100 self-testing, 100 wired, 0 unwired`. The new governance step matches its siblings' `pipefail` and `grep -Eq` shape.
- `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden` are untouched in the three-dot diff. No claim file moved, so `env_drift` has nothing to compare.
- `git merge-tree --write-tree origin/main 33660280381756f968ee197f374e9254eecfde19` exits 0, tree 47723a709f67, with no conflict (`ev/merge_tree.txt`).
- CI at the head (`ev/check_runs.txt`): 10 runs, none concluded failure. Most are queued, and the gate and `pr-contract` have not reported. So no red-check trigger is owed at this head, and the body's `## Red checks: none` is consistent as far as the runs go.
- Class enumeration (step 6): the body's issue states one seam, the sweep's owed-line handling, and names no rule. Its countermeasure covers the one consumer, step (5). I found no second seam.
- Forward-carry: the body says none. The out-of-tree `orch_sweep.sh` and `HPO_STATE_DIR` repairs are named as the orchestrator's and are not stage carries.
- Code-owned path: `.github/workflows/governance.yml` needs the owner's approving review at merge, and the body says so.
