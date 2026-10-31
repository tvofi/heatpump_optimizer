Fix review: merge 5fc0158aa9921acfca259f7a0f64d254174a303d
bus-nonce: 0102c96a815638b7a3868f30c75da2eb

Round 4 of #2879, the repair and the merge. Head re-read at posting: unchanged.
This head's three-dot diff over `4db1d3e28` (= `origin/main` tip) is
`dev/programme/triage/s6-batch37.md` +78 and `dev/programme/delivery/2879.md` +1,
2 files, 79 insertions, and nothing else. No production line is written, so no
mutant is owed and no instrument moves; the class rule is the corpus scan below,
which returns the one seam the body dispositions.

## The three blocks

- B1 answered by measurement, not by reading. `grep -B1 'TICK-RELAY
  2026-10-27T11:09:14Z' ~/hpo-orch/r10s6/tick-loop.log` prints exactly the level
  line `ledger: level carried=167 disposed=26 open-pr=16 owed=3 state-ref=4` above
  that relay line, so the pass the board read carried `owed=3` and the prior
  ruling's "the board's only OWED line" is refuted. The record's second claim,
  that the jidoka ref was one of the three, is a derivation, and it gives its two
  premises in the same sentence with their citations: not disposed until
  `2026-10-27T11:28:57Z` (`grep r10-flow-jidoka-p2-body
  ~/.local/state/hpo/dispositions.tsv`, one row) and no open PR or `handoff/` code
  ref on its topic (`git ls-remote origin 'refs/heads/*jidoka*'`; `gh pr list`:
  #2853 `fix/r10-flow-jidoka-p2` and `refs/heads/handoff/r10-flow-jidoka-p2` carry
  the sibling topic). I re-derived all three and the derivation holds. The 11:09
  OWED detail lines are gone because they live in the per-pass `tick.txt`, which I
  confirmed is rewritten (its current content is the 18:57 pass and holds no
  jidoka line) — so the record's inference is the only route, and it is shown.
  Carry: dismissed: number and derivation re-derived

- B2 answered: `proposal-triage.md`'s "an unmeasured benefit is DEFER, never
  ACCEPT" is now the ruling, and the gate moves both ways. At this head,
  `PYTHONPATH=tools/audit/seat python3 -c 'import roster_edit as r; ...'` prints
  `verdict: DEFER` and `refusal: dev/programme/triage/s6-batch37.md#P205 is not an
  ACCEPT ruling (DEFER)`; flipping `Verdict: DEFER.` to `ACCEPT.` in memory prints
  `verdict: ACCEPT` / `refusal: None`; and the unreadable-path null prints
  `verdict: None` / `refusal: ... is not on the roster branch or origin/main`. The
  ids line up: P205/V125 continues P204/V124 (`~/hpo-orch/r10s6/triage-STATE.md`,
  batch 36 on #2877), and the register truly ends at `## V123`
  (`~/hpo-orch/r10s6/proposals.md`). A DEFER ordered no roster op: the diff holds
  no roster or groups file, `git grep 'P205\|s6-batch37' -- dev/programme/rosters
  .claude/workflows dev/programme/carries dev/programme/plan*.md` is empty, and
  `R10-ORCH-LEDGER`'s carries still hold no P205 text.
  Carry: dismissed: DEFER takes no roster op

- B3 answered, and the narrowed test moves. My own harness
  (`~/hpo-seats/r10s6/review-2879-r4-ev/marker_test.sh`, disclosed as mine and not
  the finder's — a triage ruling has no committed harness) implements `marker AND
  no owed text`, owed text being a `^#{1,6}\s*What is owed` line. Arm A, a STOP
  first line plus `## What is owed`, stays OWED; arm B, a STOP first line with no
  owed heading, is EXEMPT; the null control, no marker plus `## What is owed`,
  stays OWED, so the marker is what drives the exemption. The perturbation that
  moves it: the round-3 marker-only test flips arm A to EXEMPT, which is exactly
  the narrowing's delta. Over the real corpus the narrowed arm newly exempts 0 of
  104 — re-derived: 104 `handoff-body/` refs, all 104 carrying a `BODY.md`, exactly
  one STOP first line (`b9b690afb…`), and that body's work is under `## What is
  owed` (its line 19).
  Carry: dismissed: arms and null control move

## Also re-derived at this head

- corpus `104` and the STOP scan: `git ls-remote origin 'refs/heads/handoff-body/*'
  | wc -l` = 104, 104 `git show <sha>:BODY.md` succeed, and the record's own scan
  prints only `b9b690afb9830a20e046b3515bd18858757d2047`.
  Carry: dismissed: figures re-derived

- a fresh `ledger.py level` at the default home (`carried=180 disposed=27
  open-pr=16 owed=5 state-ref=4`) prints `grep -c r10-flow-jidoka-p2-body` = `0`
  over its OWED stdout, and `ledger.py disposed <ref> <sha>` exits 0 for the store
  row the record cites.
  Carry: dismissed: remedy read back

- the cost shape's two literals: `git show -s --format=%ct b9b690afb` = `1793007293`
  (2026-10-26T09:34:53Z), 25.579 h at 11:09:39Z, both thresholds of
  `AGING_DEFAULT = (4.0, 12.0)` passed, so `ledger.escalate` yields OWED plus
  DISPATCH plus OWNER FLAG.
  Carry: dismissed: literals re-derived

- the cited code locations are correct at this head: `handoff_level()` at
  `tools/audit/seat/ledger.py:393`, its four exemption keys at 418-427, `ARMS` at
  99-101, `self_test()` at 592, the exact `dict(why)` at 810,
  `count("handoff-no-pr") == 4` at 831, and `governance.yml:585`. `ledger.py` and
  `roster_edit.py` are byte-identical between the record's measurement base
  `2b45d098c` and this head, so the merge did not move them.
  Carry: dismissed: line numbers hold at head

- `R10-ORCH-LEDGER` is size L with `resume.stage carries-open` and `files` that
  omit `ledger.py`; P79's carry already asks to add it
  (`dev/programme/triage/s6-batch10.md:15`), so this batch opening no second carry
  is right.
  Carry: dismissed: already carried by P79

## The merge

- `5fc0158aa`'s parents are the branch head `914e5e4bc` and `4db1d3e28`;
  `git merge-tree --write-tree origin/main HEAD` exits 0 and its tree
  `b47225b329bb03f861d321fb53c7ee3e41a9b769` equals `HEAD^{tree}`, so the merge is
  complete, clean and a no-op against today's main.
  Carry: dismissed: merge verified clean

- the merge took main's own files only (`merge_train.py`, `INSTRUMENTS.md`,
  `delivery/2882.md`) and touched neither branch file, so the three-dot diff is
  the record and the delivery row and nothing else — as the brief requires.
  Carry: dismissed: merge holds to the two files

## Notes

- Non-blocking: the record's cost sentence still quotes `ct=1793007293` and `25.6h`
  without the command that prints them, which `proposal-triage.md`'s "cite it,
  don't carry it" asks for. Both re-derive from `git show -s --format=%ct <sha>`
  (above), so this is a citation gap, not a wrong figure.
  Carry: dismissed: re-derived by the reviewer

- Non-blocking: the PR body restates round history in its "This head replaces…"
  paragraph, which `fixer.md`'s re-cut rule deletes. The requirement is not yet
  triggered: `bus.sh`'s `blocked_rounds 2879` counts 2 (`verdict/2879` holds
  `3f7ce8ad` and `45375ae40`), so `bus.sh:397-406` does not demand a `## Re-cut`
  note, and the `r4` label counts a round with no blocked verdict.
  Carry: dismissed: re-cut rule not yet triggered

- Residual for any future arm: "owed text" is only as good as the heading
  convention — a STOP body that says "still owed:" in prose would be exempted. The
  record names this as its DEFER trigger, "a body whose owed text is
  machine-checkable".
  Carry: R10-ORCH-LEDGER

## Scope run

Ran: the three B3 arms and null, the real-corpus scan, the `roster_edit` gate and
its perturbation and null, `ledger.py level` and `disposed`, `carry_audit.py check`
on this verdict and `pr 2879`, `git merge-tree`, the check-runs API at this head
and at every earlier head in the range. Not run: `prepr.sh`, the `gate`, the
mutation lane, and any test suite — CI owns those and this diff writes no
production line.
Carry: dismissed: heavy lanes left to CI
