Fix review: merge ca804c6dfb6156bf348345f5fabbff4cda302b9b

bus-nonce: fe302dc2e863b1c82a6ccba5f945f853

Round: 1. PR #2741, a triage ruling record (P65 DEFER), 2 files and +12 lines under dev/programme/ (INERT). Measured head: ca804c6dfb6156bf348345f5fabbff4cda302b9b, base 73b69fe0a.

## Policy reading
The brief flags this as a policy change. The diff touches only dev/programme/triage/s6-batch7.md and dev/programme/delivery/2741.md. CLAUDE.md does not name either path as policy, and the diff changes no rule, role or brief. The ruling follows proposal-triage.md as written: "an unmeasured benefit is DEFER, never ACCEPT" is the binding it cites, and the DEFER names what would change the answer (an unread line after step 10, or a cheap tick-side offset read). The entry carries every required field (Verdict, Source, Instances with commands beside the figures, Cost, Binding). It adds, drops and loosens no binding. Owner quotes: the body cites none, and the ruling needs none beyond proposal-triage.md's text, which it matches.

## Findings
- The body's Head section says ca804c6dfb6156bf348345f5fabbff4cda302b9b "merges origin/main 73b69fe0a into this PR's previous head", but the history is linear: d367b16d9 has 73b69fe0a as its parent, and ca804c6df has d367b16d9 as its only parent, so the branch contains no merge commit. This is template wording. The SHA line ("d367b16d9 on origin/main 73b69fe0a") is correct, and nothing reads the Head paragraph. Carry: dismissed: cosmetic body boilerplate, the head and base SHAs are correct and nothing parses that sentence.

## Evidence
- RESULT ruling_verdict(s6-batch7.md, P65) = DEFER (ev/ruling.txt), which matches the body.
- RESULT null control: ruling_verdict(P99) = None, which matches the body.
- RESULT mutants: rewriting the entry to Verdict: ACCEPT makes triage_refusal return None, so roster_edit would let an ACCEPT carry through. At the head it refuses with "not an ACCEPT ruling (DEFER)". Removing the verdict line returns "unreadable". So the ruling's one consumer reads this exact line, and the record is not vacuous.
- Figure "1 DEFER" re-derived with an equivalent grep (ev/checks.txt).
- Figures I could not re-derive: "19 of 32 lines" in to-main.txt, "line 92" in proposals.md, "line 35" of sweep.md and the filing time 15:04Z. All four are in out-of-tree files on the orchestrator's machine (/Users/timmalmstrom/hpo-orch/r10s6/), which this cloud seat cannot reach. They are unverified, not wrong.
- Numbering: s6-batch6.md (P64) exists on origin/triage/s6-batch6 (not yet on main), so continuing at P65 is consistent.
- INERT: tests/closure.py INERT covers both added paths (ev/checks.txt). I could not run tests/entities.py here because the container has no homeassistant module. CI closure-scope covers it.
- VERSION, the manifest and RELEASE_NOTES are untouched. Both claim files are byte-identical against the merge base.
- dev/governance/roles/ shows no drift between the merge base and origin/main, so this contract is current.
- git merge-tree --write-tree origin/main ca804c6dfb6156bf348345f5fabbff4cda302b9b gives rc=0, tree 8163811236e8b8fbf9397a12fa667ea81e5a3d8c. The merge is clean.
- No mutation proof is owed: the diff writes no production line. There is no class to open: one ruling, one seam. Forward-carry n/a is correct: a DEFER routes nothing.
- CI (ev/ci.txt): no check is red. arch-score, policy-docs, briefs, hassfest, codeql and budget-raise-gate pass. instrument-self-tests, delivery-status, closure-scope, wave-script, nightly-status, mutation, env-matrix and validate-hacs were still queued when I read them, so the merge train must confirm them before merging. The body's "Red checks: none" holds at the time I read the runs.
- The head was still ca804c6dfb6156bf348345f5fabbff4cda302b9b when I published this verdict (re-read below).
