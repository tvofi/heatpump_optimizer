# Proposal triage, session s7, batch 37 (P205)

One entry. Numbering continues after `s6-batch36.md` (P204). Facts re-measured on
2026-10-27 at origin/main `67178dc6a` and against the live refs and logs named below.

## P205: a STOP result body reads as an orphan handoff on every pass (V125)
Verdict: DEFER. The item's group is `R10-ORCH-LEDGER` (`carries-open`, L). What would
change the answer: two or more live STOP result bodies that `dispose` does not heal, or
a body whose owed text is machine-checkable.

Source: orch s7, 2026-10-27, relayed to this seat with its measurement done; the
`proposals.md` entry was not appended when this ruling was cut (the register ends at
`## V123`).

Instances: one, and the existing remedy already heals it.
- Corpus: `git ls-remote origin 'refs/heads/handoff-body/*' | wc -l` prints `102`, and
  every one carries a `BODY.md`. Exactly one has a STOP marker on its first non-blank
  line: `git ls-remote origin 'refs/heads/handoff-body/*' | cut -f1 | while read s; do
  git show "$s:BODY.md" 2>/dev/null | grep -m1 -v '^[[:space:]]*$' |
  grep -qE '^#{1,6}[[:space:]]*STOP:' && echo "$s"; done` prints only
  `b9b690afb9830a20e046b3515bd18858757d2047`, the ref the proposal names.
- That line is the H1 `# STOP: r10-flow-jidoka-p2-body — 5ab48352 does not carry the
  voluptuous fix` (`git show b9b690afb:BODY.md | grep -m1 -v '^[[:space:]]*$'`), so the
  proposal's "begins `STOP:`" test does not reach it; only the heading form can.
- The existing remedy has healed it with one command and no code: the store row reads
  `refs/heads/handoff-body/r10-flow-jidoka-p2-body … 2026-10-27T11:28:57Z disposed`
  (`grep r10-flow-jidoka-p2-body ~/.local/state/hpo/dispositions.tsv`), and
  `python3 -I tools/audit/seat/ledger.py disposed refs/heads/handoff-body/r10-flow-jidoka-p2-body b9b690afb9830a20e046b3515bd18858757d2047`
  exits 0.
- A fresh `level` pass at the default home summarises
  `ledger: level carried=174 disposed=27 open-pr=20 owed=3 state-ref=4` on stderr, and
  `grep -c r10-flow-jidoka-p2-body` over its stdout (the OWED lines) prints `0`: the
  ref is not owed.
- The arm's effect over today's corpus is therefore zero lines changed. So is the
  narrower marker-plus-owed-text arm: the one STOP body states its work under
  `## What is owed`, so requiring the absence of owed text newly exempts `0` of the
  102 bodies.

Cost: about 6-10 lines in `handoff_level()` plus a `result-body` counter in `why`, one
`git show <ref>:BODY.md` per otherwise-owed `handoff-body/` ref per pass, and a new
self-test arm and null. `handoff_level()` is `tools/audit/seat/ledger.py:393`; the four
exemptions it applies today are the `why` keys `state-ref`, `open-pr`, `disposed`,
`carried` (`ledger.py:419-427`), against a fifth, `owed`. `ARMS` at `ledger.py:99-101`
maps `refs/heads/handoff-body/` and `refs/heads/handoff/` to `handoff-no-pr`. The pin
that moves is the ledger's own `--self-test` (`self_test()` at `ledger.py:592`, run by
`.github/workflows/governance.yml:585`): `ledger.py:810` compares `dict(why)` against a
five-key literal and `:831` asserts `r.stdout.count("handoff-no-pr") == 4`.

Binding: an unmeasured benefit is DEFER, never ACCEPT (`proposal-triage.md`). The
benefit is zero for the instance — a one-command remedy already healed it — and the
class frequency is unmeasured: one STOP body in 102 today. Two constraints bind any
future arm. A STOP body may state uncarried work and this one does, under
`## What is owed` (three items), so a marker-only test exempts the only automatic
signal that the topic is unowned. And `dispatch/` is not an `ARMS` prefix
(`ledger.py:99-101`), so the test cannot check that a claimed follow-up dispatch
exists. An arm that survives both is "marker AND no owed text", and owes a null
control proving a STOP body carrying `## What is owed` stays owed.

Note for that group's `files`: `R10-ORCH-LEDGER` lists
`tools/audit/seat/cloud_relay.sh` and `tools/audit/seat/orchestrator_tick.py` and omits
`tools/audit/seat/ledger.py`, which any arm here edits; P79's existing carry already
asks to add it (`dev/programme/triage/s6-batch10.md#P79`), so this batch opens no
second carry.

The prior ruling's "the board's only OWED line" is withdrawn as measured: the pass the
board read finished `2026-10-27T11:09:14Z` and its level line is
`ledger: level carried=167 disposed=26 open-pr=16 owed=3 state-ref=4`
(`grep -B1 'TICK-RELAY 2026-10-27T11:09:14Z' ~/hpo-orch/r10s6/tick-loop.log`), so the
board carried three OWED lines, not one.
