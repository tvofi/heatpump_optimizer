Fix review: merge 724335f1fe61b0ea61058bbd860e0a512788f069

bus-nonce: 9d703c3237ec34f2948f9edb3c3fedb6

## Round

Round 2, a delta re-review of the round-1 block (mutation-vacuous, CM4, `verdict/3149`). I measured at head `724335f1fe61b0ea61058bbd860e0a512788f069` from a detached worktree. At the time of the verdict, `git ls-remote` still shows `fix/r10-audit-coverage-endgame` at this head.

## Findings

- none. Round 1's one finding is settled at this head: CM4 is now killed (see Evidence).

## Evidence

- Delta, round-1 head `1abb0abab` to this head: I compared the three-dot diff against main of each, file by file. Only `tools/audit/check_scopes.py` differs. The authored change is the one commit `ced02240f`: a docstring line, a `tempfile` import, a rewritten comment, and the subprocess arms in `--self-test`. The two merge commits bring in main (`25c46e76e`) and the code head. The other 14 branch files are unchanged from round 1.
- Mutants (`ev/mutants.txt`): each ran with `python3 tools/audit/check_scopes.py --repo . --self-test` and with the real default path, on the live scopes and on `ev/scopes_no_blueprints.json` (D4's and D6's `blueprints/` globs dropped). The file was restored after each, and the worktree is clean.
  - CLEAN: self-test rc=0. Default path: live rc=0, no-blueprints rc=1, which is the null control.
  - CM4: the predecessor's `ev/CM4.patch`, applied verbatim with `git apply` (`ev/cm4_patch_applied.txt`), and also re-planted by text substitution. Self-test rc=1 both ways. The arms "the default invocation exits 0 on the live scopes" and "and exits 1 without D4's and D6's blueprints globs" are False.
  - V1, `verdict()` called and its result discarded (`sys.exit(0)`): self-test rc=1.
  - V2, coverage dropped in the default path only (`coverage` stubbed to `(True, [])` just before main's exit): self-test rc=1. The default path's no-blueprints rc becomes 0, so the mutant is real.
  - V3, exit on `check()` plus citations, with the citation line still printed but no coverage: self-test rc=1.
  - CM2 (`both = []`), CM3 (header window `[:0]`), CM5 (citation never refused) and CM6 (`verdict()` drops coverage): self-test rc=1 each. All stay killed.
- Coverage figures (`ev/coverage_refs.txt`), `check_scopes.py --repo . --ref <r>`:
  - At `ced02240f`: tracked=8102 in_universe=1326 excluded=6776 unclassified=0, rc 0.
  - At `1abb0abab`: tracked=8107 in_universe=1329 excluded=6778, rc 0.
  - At this head: tracked=8159 in_universe=1331 excluded=6828 unclassified=0, harness citations 0, rc 0.
  - The body's 8102 and 8107 re-derive exactly. The body quotes no figure for this head, which carries main's `25c46e76e`.
- `--seat` (`ev/seat_r1_vs_head.txt`): I ran the head's script and the round-1 script on the same scopes at ref HEAD. Output is byte-identical for all 48 seats, so the repair does not regress the seat proof.
- fold_ledger (`ev/fold_head.txt`): `check` gives 47 classes, 749 instances, 0 violations, rc 0. `--self-test` rc 0.
- Merge: `git merge-tree --write-tree origin/main HEAD` gives rc 0 and no conflict. origin/main is `25c46e76e`, which is also the merge base (`ev/merge_tree.txt`).
- Claim files, `VERSION`, the manifest and `RELEASE_NOTES.md`: the three-dot diff touches none of them (`ev/claims_version.txt`). The delivery row `dev/programme/delivery/3149.md` is in the three-dot diff.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, rc 0. Scoped gate: `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` (`ev/gate_mode.txt`).
- CI (`ev/classify.txt`): `merge_train.py classify 724335f1fe61b0ea61058bbd860e0a512788f069 --pr 3149` gives `GREEN 724335f1fe61b0ea61058bbd860e0a512788f069 pending: none red: none`, rc 0. The commit's check-runs fit on one page of 100. No run concluded failure. `## Red checks` says `none`, which matches.
- `## Head` names `724335f1fe61b0ea61058bbd860e0a512788f069` and explains the code head `ced02240f` and the main merge.
- Not re-derived by me: the round-1 figures that this delta cannot move. These are the 4829 split at `ca6333333`, the stale census 274→273, and the policy caps. All of them sit in files the delta does not touch. The tracked figure, the ledger check and the seat proof were re-taken above.
