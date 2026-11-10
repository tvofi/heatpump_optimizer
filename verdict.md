Fix review: merge f56324930bd42b3caa795df4b3e86bbead11a235

bus-nonce: 62399b7a8f2e889e70a1e92a7c093eb4

Round 1 of this review (first review at this head). Head measured: f56324930bd42b3caa795df4b3e86bbead11a235 (PR head at review time; classify GREEN). Docs-only PR: one ruling file plus its own delivery row; no production code, VERSION, manifest or notes touched.

## Findings

- Stale measurement: three rulings order work already on the base. `7b864f152` (2026-11-08, in the base `01782a1e3c`, not in the ruling's read point `364353e67`) landed P409's fetch-and-recheck plus update-ref and P418's repeatable `--add` extend in `roster_edit.py`; `c70ed6b58` (same day) landed P416's `owed_unactioned` key for the tick's own OWED lines (`OWED body-ahead` arm in `owed_unactioned.py`, self-test lines ~407-413). P417 is partly landed: `roster_queue.py` now prints `batch failed <type>: <msg>`, but I did not find the per-line re-batch. The carries P409, P416, P418 and P417's print half are redundant at the base; P406 (single shared `REPORTER_INPUTS` Set, `policy_lint.mjs` line 6819) and the re-batch half of P417 still stand. The groups' fixers re-measure at their merge base, so no wrong code follows, but the owed carries are noise. Carry: dismissed: the destination groups (R10-ROSTER-WRITE-SWEEP, R10-TICK-LEVELS) are done and fixers re-measure at their merge base; the orchestrator re-routes P417 re-batch half and P406 if still open
- Follow-up: the file is named `s6-batch133.md` while its title and the delivery row say session s12; all 8 carry/brief citations use the `s6-` path and resolve, so nothing breaks. Carry: dismissed: naming only, every citation resolves

## Evidence

- RESULT mutation proof: ruling_verdict reads P406-P409, P411-P413, P416-P418 ACCEPT, P410/P414 REJECT, P415 DEFER, P419 None (ev/gate-proof.txt). All 8 Binding carry/brief texts pass triage_refusal. Mutants: P409 flipped to REJECT refused ("not an ACCEPT ruling (REJECT)"); a P410 citation refused; file absent refused ("not on the roster branch or origin/main"). Matches the body's claims.
- RESULT merge: `git merge-tree --write-tree origin/main f56324930bd42b3caa795df4b3e86bbead11a235` exit 0, clean.
- RESULT CI: `merge_train.py classify` printed `GREEN f56324930bd42b3caa795df4b3e86bbead11a235 pending: none red: none`. The body's red `gate` (job 129456755922) was an in-flight race at an earlier head; the digest shows `gate` success now. Body answers it with a Carry: dismissed.
- RESULT packet: no refusals, carry_audit 0 findings, mutation ledger diff none, the head's three-dot diff is 2 added files (delivery/3387.md, triage/s6-batch133.md).
- Governance diff `dev/governance/roles/` against merge base: empty.
- Not re-derived: host-local figures (orchestration logs, queue lines, seat a50195df evidence, 529 / 7 instance counts, replay hours); the ruling states these are host-local. The git-log counts (16 of 194 merges, email counts) I did not re-run.
- The code head `671a3f714` named in the body is carried by the added row-only commit; diff is the same single ruling file.
