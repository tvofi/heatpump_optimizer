Fix review: blocked a63c6bfd59a2703f03638054410d672cc0ae1af4 other: the batch and body misstate the self-test evidence for the carried why counter — the only count("handoff-no-pr") == 4 pin is tools/audit/seat/ledger.py:831 (the ledger self-test), not "the tick's own test", and the assertion a new why key can break is ledger.py:810's exact-dict; two figures also carry no enumerator or do not reproduce ("four ref globs" reads 3/4/5 depending on the pass; the "660 s to 1800 s" dead-seat precedent is absent from the tree and from the orchestrator state)
bus-nonce: 24e891934da58adefff8a9e3fc8e3dad

# Fix review — #2879 triage: s6 batch 37 (P205)

Head reviewed: a63c6bfd59a2703f03638054410d672cc0ae1af4 (re-read at origin `refs/heads/fix/triage-s6-batch37` immediately before posting: unchanged).
Merge base: 524c1896b6943b3da03d6cad61420ced31e14c9c (= origin/main tip).
Diff: 2 files, +62/-0 — `dev/programme/triage/s6-batch37.md` +61, `dev/programme/delivery/2879.md` +1.

## Findings

1. **Wrong file for the pin (blocking).** The batch and the body's Figures both say "The tick's own test pins `count("handoff-no-pr") == 4`, so that test moves with the counter." `grep -rn 'count("handoff-no-pr")' tools/ tests/` returns exactly one line, `tools/audit/seat/ledger.py:831`, which is the ledger's own `--self-test` (run by `governance.yml:585`), not the tick. `orchestrator_tick.py` has no such assertion. Separately, the assertion a `result-body` key added to `why` can break is `ledger.py:810`'s exact-dict `dict(why) == {...}`, which the batch does not name. A fixer implementing the carry as written would update the wrong test and can leave the governance self-test red.
2. **Uncounted figure.** "a pass that already fetches four ref globs" names no enumerator. `ledger.fetch_world` has three globs plus a plain `main` (four refspecs); `cloud_relay.sh`'s relays use five `ls-remote` globs (probe, review, handoff, handoff-body, verdict). The number is not reproducible as stated.
3. **Unverifiable precedent.** "the same argument that moved the dead-seat threshold from 660 s to 1800 s": no `660` in the tree or the orchestrator state; the only `1800` is `tests/gate_lock.py`'s `LEASE_SECONDS`, a different mechanism.
4. **Path unresolved at head.** `s6-batch36.md` is not in `HEAD`; it exists only on `origin/fix/triage-s6-batch36`. The P204 content is correct (batch 36's own header), but a reader at this head cannot open the file the numbering line cites. Every earlier batch cites the merged file.
5. **Out-of-tree path unresolved at head.** `proposals.md` is not in the tree. It is the s6 session register every batch cites, and the batch correctly says the entry was not appended (the register stops at V123), so this is a note, not the batch's unique defect.

## Verified

- One entry: `grep -c '^## P'` = 1. P204 = batch 36. V-chain contiguous V119-V125.
- `git ls-remote origin 'refs/heads/handoff-body/r10-flow-jidoka*'` = 3 refs: the named `b9b690afb… handoff-body/r10-flow-jidoka-p2-body` plus two siblings.
- `git show b9b690afb:BODY.md | sed -n 1p | od -c` first bytes `# S T O P :`; the line is `# STOP: r10-flow-jidoka-p2-body — 5ab48352 does not carry the voluptuous fix`.
- `ct=1793007293` = 2026-10-26T09:34:53Z; age at 2026-10-27T11:09:39Z = 25.579 h = 25.6 h. `AGING_DEFAULT = (4.0, 12.0)` = the 12 h threshold.
- Relay state `dispositions.tsv` (r10s6) holds exactly two entries, `grep -c … r10-flow-jidoka-p2-body` = 0. The ledger store beside its log holds the ref at 2026-10-27T11:28:57Z, `how=disposed`. `ledger.py disposed <ref> <sha>` reproduced rc=0.
- `ARMS` maps `refs/heads/handoff-body/` and `refs/heads/handoff/` to `handoff-no-pr`. `why` keys today: state-ref, open-pr, disposed, carried, owed. (The function is `handoff_level`; the batch's `level()` is the CLI verb — naming note only.)
- Triage gate reproduced: `P205 verdict: ACCEPT`; `refusal on committed file: None`; DEFER mutant prints the stated refusal; the P999 and missing-file nulls print the stated lines.
- Destination exists: R10-ORCH-LEDGER, size `L`, `resume.stage: carries-open`, `files` = cloud_relay.sh, orchestrator_tick.py. Not on the roster branch yet, consistent with unmerged batch 36 (0 P204 hits there).
- Check-runs at the head: no `failure` conclusion (superseded runs read `cancelled`/`skipped`).
- `git merge-tree --write-tree origin/main HEAD`: rc=0.
- Delivery row: one line, #2879, names batch 37 and R10-TRIAGE-B37.

## Not established

- The three board lines, "the board's only OWED line", and 11:09:39Z: `tick.txt` has been overwritten by a later pass (mtime 14:26), so the cited lines are gone; only the `ct`/25.6 h/12 h arithmetic is checkable.
- "one process spawn today": not re-derived.
- The batch routes the arm to R10-ORCH-LEDGER, whose `files` omits `tools/audit/seat/ledger.py` even though the arm edits it; the group's own P79 carry already asks to add it, and P205 neither repeats nor dispositions that.
- Lint: `brief_lint.mjs` does not take a triage markdown (it reads it as JSON and reports a shape error), so it is out of scope. `policy_lint.mjs` reads it when named explicitly, though `POLICY_GLOBS` excludes `dev/programme/triage/` so CI does not, and it reports two `[citations]` errors (`s6-batch36.md`, `proposals.md`). Merged batches 34 and 35 draw 14 and 26 such errors, so that class is corpus-wide, not this batch's.
