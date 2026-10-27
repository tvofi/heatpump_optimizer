# Proposal triage, session s7, batch 37 (P205)

One entry. Numbering continues after `s6-batch36.md` (P204). Facts read at origin/main
`524c1896b` on 2026-10-27.

## P205: a STOP result body reads as an orphan handoff on every pass (V125)
Verdict: ACCEPT narrowed -> a carry of **R10-ORCH-LEDGER** (`carries-open`, L; it owns
`tools/audit/seat/cloud_relay.sh` and `tools/audit/seat/orchestrator_tick.py`, and
`tools/audit/seat/ledger.py` is the schema both import). The carried arm exempts, in
`level()`, a `handoff-body/` ref whose body commit's first non-blank line is a STOP marker,
matched with an optional markdown heading. Two alternatives are REJECTED: telling seats to
name result bodies differently (the seat that most needs it did not read its brief), and
teaching the tick to suppress the line (the strike belongs where the line is computed, and
the tick only prints what the ledger hands it). A zero-code remedy exists for this instance
and costs one command: `python3 -I tools/audit/seat/ledger.py dispose <ref> <sha40>`.

Source: orch s7, 2026-10-27, relayed to this seat with its measurement done; the
`proposals.md` entry was not yet appended when this ruling was cut.

Instances: one, measured on the ref the proposal names, and the measurement changes the arm
the proposal describes.
- The ref exists: `git ls-remote origin 'refs/heads/handoff-body/r10-flow-jidoka*'` prints
  `b9b690afb9830a20e046b3515bd18858757d2047 refs/heads/handoff-body/r10-flow-jidoka-p2-body`
  (and two sibling body refs).
- Its `BODY.md` first line is `# STOP: r10-flow-jidoka-p2-body — 5ab48352 does not carry the
  voluptuous fix`, measured byte-exact with `git show b9b690afb:BODY.md | sed -n '1p' | od -c`,
  whose first bytes are `# S T O P :`. It is an H1, so the proposal's stated test — the first
  non-blank line *begins* `STOP:` — does not match the one ref it was written for; the arm
  must accept the heading form.
- The cost is three board lines per pass, not one: `OWED ... handoff-no-pr
  refs/heads/handoff-body/r10-flow-jidoka-p2-body ... ct=1793007293`, `DISPATCH: ? ... no code
  ref (25.6h)` and `OWNER FLAG: ? ... stranded 25.6h (threshold 12h)`, at 11:09:39Z in the
  board log `tick.txt` in the orchestrator state directory. It is the board's only OWED line,
  so it is the whole of the OWED channel, and the line cannot heal itself because the ref
  is correct and will never move.
- The emitter: `tools/audit/seat/ledger.py` classifies by ref prefix (`ARMS` maps
  `refs/heads/handoff-body/` and `refs/heads/handoff/` to `handoff-no-pr`), and `level()`'s
  exemptions today are state-ref, open-pr, disposed and carried. At ruling time the ref was
  not disposed: the relay state directory's `dispositions.tsv` held two entries and neither
  was this ref (`grep -c r10-flow-jidoka-p2-body dispositions.tsv` printed 0). The
  orchestrator applied the manual route after the ruling,
  `ledger.py dispose refs/heads/handoff-body/r10-flow-jidoka-p2-body b9b690afb9830a20e046b3515bd18858757d2047`,
  and read it back with `ledger.py disposed <ref> <sha>` (rc=0): the store is written beside
  the ledger's log path, not in the repository or the relay state directory, so a `grep` of
  either copy still prints 0 after a successful dispose and reads as a failed write.

Cost: about 6-10 lines in `level()` plus a `result-body` counter in its `why` mapping, and one
`git show <ref>:BODY.md` per otherwise-owed `handoff-body/` ref per pass — one process spawn
today, zero on a clean board, against a pass whose `ledger.fetch_world` already asks `git fetch`
for four refspecs (a plain `main` plus the `handoff/*`, `handoff-body/*` and `fix/*` globs;
`tools/audit/seat/ledger.py:434-437`) and which runs a `for-each-ref`/`covered` per owed topic.
`cloud_relay.sh`'s relays are a different count — five `git ls-remote` globs, `probe/*`,
`review/*`, `handoff/*` plus `handoff-body/*`, and `verdict/*` (lines 270, 306, 401 and 404) —
so the two are not the same figure. Self-test arms owed with it: one on the real shape
(the H1 marker) going from owed to exempt, and one null (an ordinary PR body stays owed). The
pin is the ledger's own `--self-test` (`self_test()` in `tools/audit/seat/ledger.py`), run by
`.github/workflows/governance.yml:585`, not the tick's:
`grep -rn 'count("handoff-no-pr")' tools/ tests/` prints exactly one hit,
`tools/audit/seat/ledger.py:831`, asserting the `level` CLI's stdout carries
`r.stdout.count("handoff-no-pr") == 4`; and the same `self_test()` at `ledger.py:810` compares
`dict(why)` exactly against a five-key literal, so a `result-body` key added to `why` breaks
that exact-dict too. Both assertions move with the counter. No
GitHub API call, no CI minutes, no new file, and no hot file beyond `ledger.py`.

Binding: the marker must be the one seats actually write — the H1 form measured above — or the
arm is a no-op on the ref that motivated it; the exemption must be scoped to `handoff-body/`
so a `handoff/` code ref (which has no `BODY.md`) is never exempted by a missing file; and it
must test the line's beginning, not a `STOP` anywhere in the text, so a PR body that discusses
a stop is not exempted. Per `defect-root-cause.md`'s detector rule, the arm owes the failing
fixture on the real shape and the passing one after, not only the happy path.
