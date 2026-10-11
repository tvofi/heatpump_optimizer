Fix review: blocked a4c134fce1420e531982f31da6c4ab0a07cbd19f root-cause-unanswered: mutation went red at the head -- the lane's null-control refusal (accuracy.py:44 NULL_COMMENT "killed" by tests/env_drift.py, which crashed on `git worktree add ... e1501bf48` exit 128), a refusal `## Red checks` does not answer: its mutation entries answer the unpinned-count refusals only, enumerated 2026-10-10T19:20Z; this red landed 2026-10-11T09:47Z (check-run 114440311454, run 38129371794) after the body's last figure stamp 09:26Z.

Round 4 of this review (resolution delta 271373ad5..a4c134fce only; the substance at 271373ad5 is established and was not re-opened).

bus-nonce: d05cb4476e828c50cc30cedf0bfbc7dd

## The resolution delta measured clean on every other axis

- Delta commits (first-parent): `18a04ed62` github-actions[bot] `ci: pin killed mutants` (22 killed_by rows, tests/mutation_ledger/ only, zero non-ledger files); `4b71d669` merge of the authored head; `a4c134fce` merge of origin/main (e1501bf48). The only non-bot, non-merge authored commit is `d0e5d209f` "test(R9-UX-6): record the mutation ledger the pin lane measured": 17 files, all under tests/mutation_ledger/ (3 killed_by + 14 survivor_triage). Everything else in the two-dot delta is main's own merged work (#2110/#2111/#2121/#2122/#2124), arrived through the merge commits.
- RESULT delta-commits: PASS -- reviewed production code untouched.
- The 3 applied pins (`accuracy.py:plan_promise CMP_BOUND f4529abb`, `GUARD_OFF f4529abb`, `ledger.py:restate_total RETURN_DEL 637aad71`) are payload-identical (killed_by, old, reason) to the CI shard artifacts `mutation-pins-1/2/3` of run 38090917611 (head 18a04ed62); `mutation-pins-4` is the empty skip-nothing-killed shard. Old anchor strings verified present in the head tree. This is exactly ci-autofix.md's division: the bot measured, the fixer recorded; the loop-guard path (bot declined its second pass on its own `ci:` subject) is the rule's recorded open path.
- RESULT pins-provenance: PASS.
- 5 sampled triages of 14 (`@module.CONST 4ac79a47`, `_stored_promise GUARD_OFF d997c270` [the one `equivalent`], `book_capacity GUARD_OFF 6dd41738`, `freeze_month_report CMP_BOUND 9ccdc7b1`, `roll_receipts CLAMP_DROP 2f982717`): each names the CI measurement (run 38090917611 at head 18a04ed62) for survival and analyses the concrete boundary input no recorded driver builds; every `old` line verified in the tree. Verdict census: 1 equivalent + 13 gap, as the body states.
- RESULT triage: PASS -- no assertion-only disposition found.
- Local ratchet at the head: `4601 unpinned site(s) of 6017 candidate sites, 4608 at the ratchet base e1501bf48...; the ledger agrees with the deterministic inventory` -- no MUTATION TABLE REFUSED. The script's driving half then dies on this box's Python 3.11.5 at tests/features.py:3935 (the disclosed macOS f-string limit), after the count ratchet. `ci_predict.py --base origin/main` reports `no closures or fast red predicted` -- the unpinned line is gone. The same count line, green, is also in the head's own CI log.
- RESULT ratchet + ci_predict: PASS.
- custom_components/ across the delta: only `debugger.py` moved, byte-identical to main tip e1501bf48 (main's #2110); all seven UX-6 production files byte-identical between 271373ad5 and a4c134fce. Claim files, budgets, VERSION, manifest untouched by the delta.
- RESULT production-bytes: PASS.

## The one unanswered red

The head's check-runs (38 total at measurement): `mutation` completed failure; closures/fast/coverage in progress; no other red. Its log shows the count ratchet green (4601 vs 4608, no count refusal) and then:

`MUTATION TABLE REFUSED -- the null control custom_components/heatpump_optimizer/accuracy.py:44 NULL_COMMENT was killed by tests/env_drift.py (subprocess.CalledProcessError: ... git worktree add --detach /tmp/env_drift_.../baseline e1501bf48 ... exit status 128)`

i.e. the lane's null control tripped on a driver crash (the same driver's baseline run passed rc=0 seconds earlier), not on the repaired red -- that repair is green in the same log. But the refusal stands at the head the body names, and the body is silent on it; by this body's own standard (its nightly-ha entry: an infrastructure red that re-fires at the publishing head owes an answer, and is not waved through by a note that it is not the diff's), this needs a `## Red checks` entry: name the refusal, show the count repair held in CI, and answer the driver crash (re-run/lane defect) -- then re-push.

Measured at detached worktree /Users/timmalmstrom/hpo-seats/r9rev-2119c/wt, head a4c134fce1420e531982f31da6c4ab0a07cbd19f, 2026-10-11T09:58Z. Evidence: /Users/timmalmstrom/hpo-seats/r9rev-2119c/ev (head.txt, delta-attribution.txt, pins-vs-artifacts.txt, triage-samples.txt, mutation-local.txt, ci-predict.txt, mutation-ci-refusal-a4c134fce.log, checkruns-head.txt).
