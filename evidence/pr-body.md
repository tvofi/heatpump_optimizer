Triage batch 37 rules V125, the STOP result body that reads as an orphan handoff on every pass. The verdict is **DEFER**. The item's group is `R10-ORCH-LEDGER`; the existing one-command remedy, `python3 -I tools/audit/seat/ledger.py dispose <ref> <sha40>`, already heals the one instance, and the class's frequency is unmeasured — which `dev/governance/roles/proposal-triage.md` sends to DEFER ("an unmeasured benefit is DEFER, never ACCEPT").

The measurement that decided it. The corpus is every `handoff-body/` ref, and each carries a `BODY.md`. Exactly one has a STOP marker on its first non-blank line — the ref the proposal names — and that first line is an H1, so the proposal's "begins `STOP:`" test does not reach it. That ref was disposed and read back, and a fresh `level` pass at the default home no longer owes it. The exemption's effect over today's corpus is therefore zero level lines changed. The narrower marker-plus-owed-text arm measures zero too: the one STOP body states its work under `## What is owed`, so requiring the absence of owed text newly exempts nothing.

Two constraints bind any future arm. A STOP body may state uncarried work, and this one does under `## What is owed` (three items), so a marker-only test exempts the only automatic signal that the topic is unowned. And `dispatch/` is not an `ARMS` prefix, so the test cannot check that a claimed follow-up dispatch exists. The narrowed test that survives both is "marker AND no owed text", with a null control proving a STOP body carrying `## What is owed` stays owed.

What would change the answer: two or more live STOP result bodies that `dispose` does not heal, or a body whose owed text is machine-checkable.

This head replaces the previous ruling's "the board's only OWED line" with the measurement: the pass the board read finished at `owed=3`, so the OWED channel carried three lines and the jidoka ref was one of them. It removes the unbacked claim that the seat most needing the advice did not read its brief, the carried board literals, and the `R10-TRIAGE-B37` id that resolves nowhere; names `handoff_level()` rather than the `level` verb; and corrects the disposition store path.

The batch's numbering line cites `dev/programme/triage/s6-batch36.md` (P204). That file is not on this branch or `origin/main`; it is on #2877's `fix/triage-s6-batch36`, still open. The citation resolves by merge order — #2877 merges, then this branch merges `origin/main` — not by an edit here.

## Head

`5fc0158aa9921acfca259f7a0f64d254174a303d` merges the authored code head `f57f8dbd84250f804c5cf3ba4a894ce2dec29ffd` and then merges origin/main `4db1d3e28` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`f57f8dbd84250f804c5cf3ba4a894ce2dec29ffd` is the head this ruling is re-measured at. It sits on `70a772f04098b46b12a40cb6a42d7a5a852dc80d`, which merged the authored code head `41c31b170e82d5df73aa77154aa1ed9bc4442c6d` and then origin/main `2b45d098c`. It is unpushed at handoff, so no check run exists at it; the previous head `e766c3bdceca6e64156cb0b44212dc62c1159b6e` is the one the review at `45375ae40` blocked.

## Mutation proof

The batch's in-tree consumer is `tools/audit/seat/roster_edit.py`'s triage gate: an ACCEPT is what lets a carry cite it, and a DEFER must not be citable. On the committed file at `f57f8dbd`, with `PYTHONPATH=tools/audit/seat`:

```
$ python3 -c 'import roster_edit as r; s=open("dev/programme/triage/s6-batch37.md").read(); print("verdict:", r.ruling_verdict(s,"P205")); print("refusal:", r.triage_refusal(["P205 triage: dev/programme/triage/s6-batch37.md#P205"], lambda p: s))'
verdict: DEFER
refusal: dev/programme/triage/s6-batch37.md#P205 is not an ACCEPT ruling (DEFER)
```

Flipping the `Verdict:` line to `ACCEPT` in the same call prints `verdict: ACCEPT` and `refusal: None`: the gate tracks the ruling, and the refusal is the ruling's, not an unreadable file.

## Null control

At a path the reader cannot open, the same call refuses rather than reading a ruling out of nothing:

```
$ PYTHONPATH=tools/audit/seat python3 -c 'import roster_edit as r; print("verdict:", r.ruling_verdict("", "P205")); print("refusal:", r.triage_refusal(["P205 triage: dev/programme/triage/s6-batch37.md#P205"], lambda p: None))'
verdict: None
refusal: the triage ruling dev/programme/triage/s6-batch37.md is not on the roster branch or origin/main
```

At `f57f8dbd`, an entry the file does not hold prints `dev/programme/triage/s6-batch37.md#P999 is not an ACCEPT ruling (no such entry)`.

## Figures

- the corpus is `104` handoff-body refs at 2026-10-27T17:47Z: `git ls-remote origin 'refs/heads/handoff-body/*' | wc -l`.
- exactly one has a STOP first line, the named ref: `git ls-remote origin 'refs/heads/handoff-body/*' | cut -f1 | while read s; do git show "$s:BODY.md" 2>/dev/null | grep -m1 -v '^[[:space:]]*$' | grep -qE '^#{1,6}[[:space:]]*STOP:' && echo "$s"; done`.
- its first non-blank line is the H1 `# STOP: r10-flow-jidoka-p2-body — 5ab48352 does not carry the voluptuous fix`: `git show b9b690afb9830a20e046b3515bd18858757d2047:BODY.md | grep -m1 -v '^[[:space:]]*$'`.
- the dispose row is in the default-home store:

  ```
  $ grep r10-flow-jidoka-p2-body ~/.local/state/hpo/dispositions.tsv
  refs/heads/handoff-body/r10-flow-jidoka-p2-body	b9b690afb9830a20e046b3515bd18858757d2047	2026-10-27T11:28:57Z	disposed
  ```

  and `python3 -I tools/audit/seat/ledger.py disposed refs/heads/handoff-body/r10-flow-jidoka-p2-body b9b690afb9830a20e046b3515bd18858757d2047` exits 0.
- the `level` pass at the default home owes no jidoka ref: `tools/audit/seat/ledger.py level <hrefs> <topics>`, hrefs from `git ls-remote origin 'refs/heads/handoff/*' 'refs/heads/handoff-body/*'` and topics from the open PRs, then `grep -c r10-flow-jidoka-p2-body` over its stdout prints zero.
- the marker-plus-owed-text arm newly exempts `0` bodies: the one STOP body carries a `## What is owed` heading, so it is excluded on every arm.
- the pass the board read finished at `owed=3`: `grep -B1 'TICK-RELAY 2026-10-27T11:09:14Z' ~/hpo-orch/r10s6/tick-loop.log`.
- the exemptions live in `handoff_level()`, not the `level` verb: `git grep -n 'def handoff_level' -- tools/audit/seat/ledger.py` (`:393`), and its `why` keys are `state-ref`, `open-pr`, `disposed`, `carried`, `owed`: `git grep -n 'why\["' -- tools/audit/seat/ledger.py`.
- `ARMS` maps `refs/heads/handoff-body/` and `refs/heads/handoff/` to `handoff-no-pr`: `git show f57f8dbd:tools/audit/seat/ledger.py | sed -n '99,101p'`.
- the pin a `result-body` key would move is the ledger's own `--self-test`: `git grep -n 'def self_test\|dict(why) ==\|count("handoff-no-pr")' -- tools/audit/seat/ledger.py` (`:592`, `:810`, `:831`), run by `git grep -n 'seat/ledger.py --self-test' -- .github/workflows/governance.yml` (`:585`).
- the diff is `2 files changed, 79 insertions(+)`: `git diff --stat $(git merge-base origin/main HEAD)...HEAD`.
- the batch holds one entry: `grep -c '^## P' dev/programme/triage/s6-batch37.md`.

## Red checks

none.

## Forward-carry

none

## Friction

none


