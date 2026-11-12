Fix review: blocked 11a6c579bb8e354b4f76209b1b4c472ddfee5c19 evidence-cut: the cap payments delete sole-copy measurements and a reader constraint that writing-for-agents.md forbids cutting

bus-nonce: 8e594cebb0274059591ac9f2f2909201

## Block

Round 1 of this review (first review of #3510), measured at head `11a6c579bb8e354b4f76209b1b4c472ddfee5c19`, merge base `19baca76181cb019d9b1cfd93ee6bc0a08e20047`.

The body says every addition "is paid by cuts of spent prose and by correcting stale claims". Several of those cuts are not spent prose. They delete measurements, and a constraint on downstream seats, whose only copy in the tree was the deleted text (`ev/sole-copy-grep.txt`). `writing-for-agents.md`: "A short artifact missing a control is a defect; cutting evidence is never compliance with this rule." A sentence stays if it carries a measurement or a downstream constraint and is the only place carrying it. Each of the following is the only place:

- `dev/audit/README.md`, harness contract: the round-2 judge's measured `load1` ambient floor (1.86, best of ten retries 1.55). This measurement is the basis for "`load1` is quoted, not gated". The replacement, "(the box's ambient floor exceeds any useful bar)", states the conclusion with no number behind it.
- `dev/audit/README.md`, harness contract: `h2_cycle.py`'s structural `thread_factor` of 1.27-1.30 over four re-takes. This is the measurement showing that a deliberate second thread can never meet the bare 1.05 ratio, so the subtraction rule rests on it.
- `dev/audit/README.md`, rounds 1-3: "the round-2 numbers were recorded at `c398fc84`". The register names that SHA only as v6.2.14's stamp. Also cut: `web-phase0.js` and `triage-quiet-judges.json` are at `d5d8c4a`, and the constraint "their briefs record what a judge established and refuted, so read them before re-deriving anything a group in them settled". Neither file name appears anywhere else in the tree.
- `dev/audit/README.md`, instrument defects: "say which you could not separate", an obligation on a verifier, with no other copy.
- `dev/governance/roles/orchestrator.md` section 9: "twenty had no disposition while the check reported clean". This is the measured instance behind the failure shape, with no other copy. The paired "thirty-one ... eight" figure does survive in `dev/programme/plan-2026-09-open-issues.md:437`.

The `CLAUDE.md` cuts (the four-issues anecdote) are disclosed and put to the owner under carry 14's terms, so they are not part of this block. The README and `orchestrator.md` cuts are not disclosed as evidence cuts.

Re-cut, either way: keep these sentences, or relocate them to a tree destination the body names (for example the register, or the README's own trap list), and pay with genuinely spent prose. Where no such payment exists, ask the owner for the cap raise before pushing (CLAUDE.md rule 2). Also: the body's carry 29 line says "See Friction for 10% versus 20%", but `## Friction` reads `none`. The question actually sits under `## Approval`.

## Evidence

- Head and base: `ev/HEAD.txt`. `dev/governance/roles/` is unchanged between the merge base and origin/main (empty diff), so the contract is current.
- `git merge-tree --write-tree origin/main 11a6c579bb8e354b4f76209b1b4c472ddfee5c19`: rc 0, clean (`ev/merge-tree.txt`). origin/main is at 8c10361eb1fea539dc5acb8f7442eac2810faa47.
- Mutation proof re-run. The head prints `roster_edit self-test: 281 checks, 0 failed`. With `LOG` removed from `VERDICT_LINE_RE` it prints `281 checks, 1 failed` and `FAIL triage gate: a LOG ruling is refused as LOG, never routed (got: )`. Restored afterwards (`ev/selftest-head.txt`, `ev/selftest-mutant.txt`). The body's mutation proof is confirmed.
- `node tools/policy/policy_lint.mjs --budgets` at the head: rc 0. Every cap row the body quotes re-derived equal (`ev/budgets-head.txt`): README key 314/321 6051/6059; CLAUDE.md 214/221 3604/3605; fixer.md 315/315 5215/5216; orchestrator.md 294/295 4246/4251; architect-planner.md 84/85 1261/1261; plan-review.md 24/24 304/304; proposal-triage.md 36/36 488/489; D13.md 79/79 1149/1149; D11.md 1494/1499 (5 tokens of headroom). No cap is raised.
- Not re-derived: the body's pre-payment null control "395/321, 7333/6059", which is an intermediate tree state that is not committed.
- `wc -c` base to head: README 24230 to 24205, CLAUDE.md 14401 to 14415. Both re-derived equal.
- `brief_lint.mjs`: rc 0, and `PLAYBOOK ok: the renamed fixture is refused for its 7 moved instruments and the null fixture lints clean`. The only error lines come from deliberate fixtures (`ev/brief_lint.txt`).
- `rules_sync.mjs --check`: `RULES-SYNC ok`. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- VERSION, manifest and RELEASE_NOTES.md: untouched.
- Stale-claim corrections confirmed. `grep -n 'sleep(0.002)'` in optimizer.py finds three call sites, in `_lbfgsb_restart`, `_multi_start_minimize` and the DHW-to-space seam. The README table lists four instruments. `grep -c '"tools/audit/' policy_budgets.json` returns 50. "(the first trap above)" resolves: the first trap is `FakeHass.async_add_executor_job`, README:242.
- Carry 14 and carry 29 were read on roster `handoff/audit-r10-roster` at c454574f36a140f712384aee1f5516f92f4856da. The written red definition matches carry 29. The 10% vs 20% discrepancy is the body's own open question to the owner.
- CI: `merge_train.py classify 11a6c579bb8e354b4f76209b1b4c472ddfee5c19 --pr 3510` printed `WAIT 11a6c579bb8e354b4f76209b1b4c472ddfee5c19 pending: gate red: none` (rc 3) on both runs (`ev/classify.txt`). This verdict blocks on substance and does not depend on CI. No HTTP 503 was met. `tests / nightly-status` is red but is not in `owed-reds` (`ev/owed-reds.txt`), so it blocks nothing. The body's `## Red checks: none` was not contradicted by any concluded owed red at the time of reading.
- The finder's harness: none is named, and none is owed for a playbook prose group. The executable change's harness is the self-test above.
