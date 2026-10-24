Fix review: merge 7765613293f0ac49037ef90ef9cd046a6999d9dc

bus-nonce: 20486f41542ef2008c4f03470b458e10

Round 1. Measured head 7765613293f0ac49037ef90ef9cd046a6999d9dc (PR #2741 head at review time), merge base 73b69fe0a9fa9e45736cd1cdbc2077d3958b41ec, which is origin/main.

## Evidence
- Scope: the diff adds two files, dev/programme/triage/s6-batch7.md (one ruling, P65) and dev/programme/delivery/2741.md (the delivery row). Neither is a policy file named in CLAUDE.md (dev/programme/ is the record, not dev/governance/ or .claude/rules/), so no binding of any seat changes; the brief's policy-change lens finds no sentence of policy text to check against tvofi's words. The ruling's binding sentence ("an unmeasured benefit is DEFER, never ACCEPT") quotes dev/governance/roles/proposal-triage.md verbatim.
- Ruling shape (proposal-triage.md): one "## P65:" entry carrying Verdict, Source, Instances, Cost and Binding; the DEFER names what would change the answer and the owner of the interim fix, as the contract requires.
- Numbering: s6-batch6.md on origin/triage/s6-batch6 holds P64 and s6-batch8.md on origin/triage/s6-batch8 opens at P66, so P65 is contiguous; the body's "continues after s6-batch6.md (P64)" holds.
- Consumer: RESULT ruling_verdict P65 = DEFER; null control P99 = None; mutant with the Verdict line removed = unreadable; triage_refusal refuses a roster cite of P65 as not ACCEPT (ev/ruling_verdict.txt). The body's null-control claim re-derives.
- Figure: the body's verdict count (1 DEFER) re-derives at this head.
- Figures I could not re-derive: the Instances line's counts (19 of 32 lines in to-main.txt, proposals.md line 92, sweep.md line 35) are read from the orchestrator's out-of-tree scratch files, which this cloud seat cannot see. They are cited with their commands, not carried, per proposal-triage.md; they are not verified here.
- Classification: tests/closure.py lists the dev/programme/ prefix INERT (line 273 at this head), as the body says.
- Host paths: none in either added file (a grep for home, tmp, Users and root directory prefixes returns nothing).
- VERSION, manifest version and the notes heading are untouched; no claim file, budget, closure or golden fixture moves, so steps 4, 5 and 14 have nothing to measure. Mutation proof is n/a: no production line changed.
- Merge: git merge-tree --write-tree origin/main <head> exits 0 (ev/merge.txt).
- CI at this head when the review was taken: hassfest, codeql javascript-typescript, prelude, refresh and cancel-superseded succeeded; record, delivery-status-publish and kernel-points skipped; the rest were still queued. No check was red, so step 11 had nothing to answer; the orchestrator's merge waits on those runs concluding green.
