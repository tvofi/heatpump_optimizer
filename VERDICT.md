Fix review: blocked e766c3bdceca6e64156cb0b44212dc62c1159b6e ruling: "the board's only OWED line" is false (the ledger's own summary at the cited pass is owed=3), the ACCEPT fails proposal-triage.md's unmeasured-benefit rule (one STOP body in the whole corpus, already disposed), and the blanket marker test would exempt a STOP body that states owed work — this instance's own "## What is owed" does.
bus-nonce: 877f5c03bd92a7ba023d0607932a9a72

# Fix review — #2879 triage: s6 batch 37 (P205), round 3

Head reviewed: `e766c3bdceca6e64156cb0b44212dc62c1159b6e` (re-read at
`refs/pull/2879/head` immediately before posting: unchanged). Merge base
`67178dc6a589cf95d2ce7cff36d8bbf17343e8dc` (= origin/main tip). Diff: 2 files,
+71/-0 — `dev/programme/triage/s6-batch37.md` +70, `dev/programme/delivery/2879.md` +1.

Form notes. Line 1 uses `bus.sh`'s enforced grammar (`verdict_sha`,
`tools/audit/seat/bus.sh:164-170`: `Fix review: merge <40-hex>` or
`Fix review: blocked <40-hex> <class>: <reason>`); `push-verdict` refuses the brief's
`Verdict:` form at this head. `push-verdict` also takes a third argument, the evidence
directory; it was passed.

## Findings

1. **"The board's only OWED line" is wrong (blocking).** The batch (lines 33-35) says
   the jidoka body "is the board's only OWED line, so it is the whole of the OWED
   channel". The ledger's own summary for the pass the board read is `owed=3`, not
   `owed=1`. `~/hpo-orch/r10s6/tick-loop.log`:
   - the relay pass that finished `2026-10-27T11:09:14Z` (`started=2026-10-27T11:01:38Z`,
     the level the `11:11:37Z` board read): `ledger: level carried=167 disposed=26
     open-pr=16 owed=3 state-ref=4`;
   - the preceding pass prints the same.
   `cloud_relay.sh:459-464` writes `ledger level`'s stdout into `<log>.level` for the
   `handoff-no-pr` kind; `orchestrator_tick.py:742-750` prints every such line. All
   three owed refs are `handoff-no-pr` (ARMS, `ledger.py:99-101`), so the board had
   three OWED lines. The jidoka ref was one of them (not disposed until `11:28:57Z`),
   so two others were owed on the same board. The three-line *shape* of the cost is
   right (it reproduces from `ledger.escalate`); the "only OWED line" claim is not.
   Evidence: `evidence/owed.txt`.

2. **The ACCEPT does not meet `proposal-triage.md`'s bar (blocking).**
   `dev/governance/roles/proposal-triage.md`: "An even or marginal trade is REJECT;
   **an unmeasured benefit is DEFER, never ACCEPT.**" The batch's own remedy disposes
   the one instance (`ledger.py dispose`, read back rc=0; the store row is
   `... b9b690af… 2026-10-27T11:28:57Z disposed`), and a full `ledger.py level` pass at
   the default home no longer owes it (`carried=192 disposed=27 owed=5`, no jidoka row).
   So the measured benefit is zero for the instance. For the class it is unmeasured:
   across all 102 `refs/heads/handoff-body/*` refs (every one carrying a `BODY.md`),
   exactly one has a STOP first line — the ref already disposed. The batch's own text
   is "Instances: one". A benefit already delivered by a one-command remedy, with the
   class frequency unmeasured, is the contract's DEFER. Evidence: `evidence/ruling.txt`.

3. **The blanket marker test exempts a STOP body that states owed work (blocking).**
   The arm exempts any `handoff-body/` ref whose first non-blank line is a STOP marker.
   The motivating body is exactly a STOP body that states owed work — its own
   `## What is owed` gives three items (the code fix on `fix/r10-flow-jidoka-p2`, the
   body re-take, the carry-audit record). The work happens to be keyed to the sibling
   topic `r10-flow-jidoka-p2` (a `handoff/r10-flow-jidoka-p2` code ref exists), but the
   ruling neither says so nor checks it. The constructed case the heading form does not
   catch: a body whose first line is `# STOP: r10-foo — blocked on X`, whose text names
   work, and where no `handoff/r10-foo` code ref, no dispatch and no roster row exists.
   The marker test exempts it and the OWED line — the only automatic signal that the
   topic is unowned — is gone. `dispatch/` is not an ARMS prefix (`ledger.py:99-101`),
   and `carry_audit.py check --body` runs on PR bodies (`prepr.sh:837`,
   `app_push.sh:260`), not on result bodies automatically. The arm needs to verify the
   follow-up is carried (a `handoff/<topic>` code ref or a dispatch), or the ruling
   should keep the `dispose` route rather than exempt on the marker alone.
   Evidence: `evidence/exemption.txt`.

4. **Wrong identifier.** The batch says the exemptions live in `level()`; they live in
   `handoff_level()` (`ledger.py:393`). `level` is the CLI verb. The PR body uses the
   correct name. `evidence/exemption.txt`.

5. **The dispositions file named is not the relay state directory's.** The relay's
   state dir is `$HPO_STATE_DIR` (default `~/.local/state/hpo`), whose
   `dispositions.tsv` is the ledger's store (236 refs, this one included). The
   two-entry file is the orchestrator session dir's copy (`~/hpo-orch/r10s6/`). And
   "a grep of either copy still prints 0" is not true of the repository, where no such
   file exists (only two policy fixtures); grep there exits 2. `evidence/notes.txt`.

6. **The three board lines and 11:09:39Z are carried, not cited.** `tick.txt` is
   rewritten every pass (mtime 17:36) and no longer holds `1793007293`,
   `r10-flow-jidoka-p2-body` or `11:09:39`. `proposal-triage.md` requires "cite it,
   don't carry it". The shape and the 25.6h/12h arithmetic reproduce; the literals do
   not. `evidence/notes.txt`.

7. **The destination's `files` omit `ledger.py`, and P79 already asks for it.** The
   roster gives R10-ORCH-LEDGER `files` = `cloud_relay.sh`, `orchestrator_tick.py`; the
   arm edits `tools/audit/seat/ledger.py`. `s6-batch10.md:15` (P79) already carries "Add
   `tools/audit/seat/ledger.py` to the group's files." P205 neither repeats that ask nor
   dispositions it, though its line 63 says "no hot file beyond `ledger.py`".
   `evidence/notes.txt`.

8. **`R10-TRIAGE-B37` resolves nowhere.** 0 hits in `wave-r10-groups.json`;
   `roster_lib.group_for_branch(..., 'fix/triage-s6-batch37')` is `None`;
   `record_row.py:145` emits a group tail only from that lookup; every other triage
   delivery row carries no id. `evidence/notes.txt`.

9. **One uncited assertion.** "the seat that most needs it did not read its brief" has
   no command or log reference. `evidence/notes.txt`.

## Prior round — each finding answered at this head

1. Pin attribution — answered; the batch now names the ledger's own `--self-test`
   (`governance.yml:585`), `ledger.py:831`, and the exact-dict at `:810`. Re-derived.
2. "Four ref globs" — answered; `ledger.py:434-437` (four refspecs) and
   `cloud_relay.sh:270,306,401,404` (five globs), both re-derived.
3. 660 s / 1800 s precedent — answered by deletion.
4. `s6-batch36.md` unresolvable — answered in the PR body: on #2877's
   `fix/triage-s6-batch36`, open, "resolves by merge order". Confirmed absent from the
   tree and origin/main; #2877 OPEN. Still unopenable at this head until #2877 merges.
5. `proposals.md` — answered; the batch says the entry was not appended, and the
   register (`~/hpo-orch/r10s6/proposals.md`) ends at V123.

The prior "Not established" note on the board lines is not answered (finding 1 shows
one of them false); the note on `ledger.py` in the group's `files` is not answered
(finding 7).

## Verified

- One entry: `grep -c '^## P'` = 1. Diff +71/-0. Delivery row 1 line.
- `git ls-remote origin 'refs/heads/handoff-body/r10-flow-jidoka*'` = 3 refs, the named
  `b9b690afb9830a20e046b3515bd18858757d2047 refs/heads/handoff-body/r10-flow-jidoka-p2-body`
  plus two siblings.
- `git show b9b690afb:BODY.md | sed -n 1p | od -c`: first bytes `# S T O P :`; the line
  is `# STOP: r10-flow-jidoka-p2-body — 5ab48352 does not carry the voluptuous fix`.
  It is an H1, so the proposal's "begins `STOP:`" test does not match it.
- `ct=1793007293` = 2026-10-26T09:34:53Z; age at 2026-10-27T11:09:39Z = 25.579 h = 25.6 h;
  `AGING_DEFAULT = (4.0, 12.0)`, so both thresholds are passed.
- `grep -rn 'count("handoff-no-pr")' tools/ tests/` = exactly one hit,
  `tools/audit/seat/ledger.py:831`; `def self_test` at `:592`; `dict(why) ==` at `:810`;
  `governance.yml:585` runs the self-test.
- `fetch_world` at `ledger.py:434-437` asks four refspecs (plain `main` + `handoff/*`,
  `handoff-body/*`, `fix/*`). `cloud_relay.sh`'s relays use five `ls-remote` globs at
  270, 306, 401 (two) and 404.
- `ARMS` maps `refs/heads/handoff-body/` and `refs/heads/handoff/` to `handoff-no-pr`;
  `why`'s keys today are state-ref, open-pr, disposed, carried, owed.
- The dispose read-back: `ledger.py disposed <ref> <sha>` rc=0; store row
  `b9b690af… 2026-10-27T11:28:57Z disposed`; `ledger.py level` at the default home no
  longer owes the jidoka ref.
- R10-ORCH-LEDGER: `size` L, `resume.stage` `carries-open`, `files` =
  `cloud_relay.sh`, `orchestrator_tick.py`.
- `git merge-tree --write-tree origin/main HEAD` rc=0. Check-runs at the head: 22
  success, 8 skipped, 7 still running, no `failure`.

## Not established

- The literal three board lines and the exact `tick.txt` timestamp: the file was
  overwritten (finding 6); the contradiction in finding 1 comes from the surviving
  `tick-loop.log` summary.
- "the seat that most needs it did not read its brief" (finding 9).
- That the ref "will never move": a future push to it would change the tip; the body is
  final today but the claim is a forecast, not a measurement.
- The frequency of future STOP bodies; that is precisely the unmeasured benefit in
  finding 2.
