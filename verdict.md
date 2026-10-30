Fix review: merge 76e025ff0e7f0645dfee4b8118286d40aed0b69d

bus-nonce: b9762bf6aaa9824ca81431843e282611

Round 1. Record PR: diff is dev/programme/triage/s6-batch74.md plus dev/programme/delivery/3007.md and nothing else (three-dot). No production code, VERSION, claim or budget file touched.

## Findings

- The ruling's cost sketch ("keep LEAD.match(first) and the inherited lead, drop the DEFERRED/NONBLOCK clause", about 5 lines) does not produce its own third null control. At origin/main an Evidence item with no lead and no trigger word that carries `Carry: <invented group>` is not flagged (items() gives flagged=False), so finding_rows never checks its destination. The rule text and the carry text do say a `Carry:` marker makes the item a finding; the host fixer must therefore ADD a Carry clause to the Evidence branch, not only delete one, and the cost line understates that. The roster carry is correct, so the host is covered once it builds the clause. Carry: R10-FLY-RELAY-REVIEW-FF

## Evidence

- Re-ran `carry_audit.py pr N` at origin/main cc930cdd1 (ev/carry-audit-*.txt). Each named item is UNROUTED [evidence] and trips on the word the ruling states: #3002 af269651 on DEFERRED "residual"; #3001 c4431278 on NONBLOCK "deferred" (stage-name list); #3001 3de8ca1d on DEFERRED "residual"; #2987 08d5f26d on NONBLOCK "not a block". None opens with a LEAD. All four are measurements, so the false-park claim holds. I re-derived the four trigger words directly with the module's regexes.
- Null controls: an unmarked `## Findings` item is refused (that branch is untouched); an Evidence item opening `Follow-up:` flags as "lead" (checked on a synthetic verdict); the Evidence `Carry:` destination check is stated in the carry text but see the finding above. Each is stated with a pass/fail outcome, and the single mutant (restore the DEFERRED/NONBLOCK clause, the four field rows must fail) is checkable.
- What is given up (the #2441 and #2465 fixture rows, carry_audit.py lines ~1018-1021, flip to pass) is stated with its cost, the writer-side remedy (a handed-on defect goes under `## Findings` or opens with a lead), and the measured basis (12 Evidence flags, 0 findings over 30 verdicts plus 4). I could not re-derive the "30 verdicts / 7 items" figure from P293 (not re-run); the four field items I did re-derive.
- Roster: R10-FLY-RELAY-REVIEW-FF exists in wave-r10-groups.json on origin/handoff/audit-r10-roster (resume.stage carries-open, not done). R10-FLY-CARRY-DISPOSITION is stage done, consistent with "folded". The destination's files list names cloud_relay.sh and bus.sh, not carry_audit.py, so the host fixer's file list needs carry_audit.py and the mutants harness added when it picks this up.
- Merge: `git merge-tree --write-tree origin/main 76e025ff0e7f0645dfee4b8118286d40aed0b69d` rc 0. Commits carry no Claude footer or trailer.
- CI at this head, check-runs API, read at ~18:10Z: no red. Success: policy-docs, delivery-status, wave-script, arch-score, briefs, mutation, nightly-status, coverage-ratchet, hassfest, CodeQL. Still queued or in progress at read: tests/fast, typing, closures, closure-scope, browser, coverage, instrument-self-tests, env-matrix, pr-contract, budget-raise-gate. This verdict attaches to a head whose gate had not concluded; re-read it before merging.
