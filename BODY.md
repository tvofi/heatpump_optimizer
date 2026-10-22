R10-FLOW-ARCH-PLANNER: the architect/planner seat, its plan reviewer, proposal triage and the four standing seats land as tracked role contracts, wired into `orchestrator.md`, `CLAUDE.md`, the sweep and two instruments; decision 0015 records the rulings. Policy, under the mandate in force with scope all (#201 comment 6329234399). Closes nothing; leaves #201 open.

What each brief and carry item became:

- **(1) contracts**: `dev/governance/roles/architect-planner.md` and `plan-review.md`, from the study drafts at `30c57744a` (`dev/programme/flow-study/architect-planner/architect-planner.md`, branch `claude/dazzling-gauss-7l3u2b`), the method list cut to what binds a step.
- **(2) `orchestrator.md`** section 2b: from round 11 P3 is the architect's plan, reviewed and owner-approved; P4 executes it and records each deviation on `plan/r<N>`.
- **(3) decision 0015** item 2: move 5 amended to grouping by owning seam, the class id kept as a tag, a cross-seam class split per seam with its sweep as a fitness function. 0014 had revoked 0012 whole, so the record states the rule rather than patching a revoked file.
- **(4) the target**: `architect-planner.md` "The programme target", every condition from the study's section 4; it binds the plan, never a seat.
- **(5) `tools/audit/archscore/ABOUT.md`**: one sentence, after "a review trigger, never a target a seat is rewarded for moving".
- **(6) `CLAUDE.md`**: one role-table row per new contract (seven).
- **(7) plan of record**: "Round template, from round 11" in `dev/programme/plan-2026-09-open-issues.md`, P3 <= 8 h and P4 <= 56 h.
- **Proposal triage**: `proposal-triage.md` (sonnet, medium). Rulings go in `dev/programme/triage/`, not the delivery record: a row is written per pull request at its merge, and a REJECT or DEFER yields no pull request (decision 0015, "Why the triage record is its own directory"). The check extends `roster_edit.py`, not `carry_audit.py`. It runs in `write_roster()`, the one write path, which every op and `roster_sync.py`'s carry appends go through. It judges only the text a write adds, and refuses proposal-sourced text (`triage P<n>` / `proposal P<n>`, any case) that cites no `triage: dev/programme/triage/<file>.md#P<n>` ACCEPT. The s4 batch 1 (P1-P4) is re-recorded as `dev/programme/triage/s4-batch1.md`. Its instance figures are the carries' own, cited at roster SHA `0a326689b`: the s4 cost estimates are not in the tree, so none is carried.
- **Critical path, every cap** (owner ruling and the third restatement): `orchestrator.md` section 5 dispatches a ready critical-path group at the WIP cap, a drain-first hold, the coordinator K/2 limit or the seat cap, with `pr_cap.py dispatch-gate --over-cap "critical path: <group>"`, first in every queue. `standing-merge.md` puts critical-path PRs first in the train.
- **Standing seats**: `standing-tick.md`, `standing-merge.md`, `standing-dispatch.md` and `standing-roster.md`. The out-of-tree s4 briefs were not readable from this seat, so each contract is folded from the carry's text and the instruments' own headers, with no host path.
  - The sweep gains step (1b), standing-seat liveness: a seat that is absent, finished with work owed, or reported `STOPPED seat <name>:` is restarted on its contract, with a new `seat_queues` placeholder. It also gains step (7), Proposals: send to triage.
  - `pulse.py`: each origin arm's STOPPED line names the seat its input waits on, and `--seat-queue SEAT=FILE[:MIN]` adds one arm per seat, STOPPED once a queued input passes the seat's cadence.
- **Paid by moving text**: from `orchestrator.md`, section 4's `preflight.sh` and post-merge read-back rules moved to `standing-merge.md`, section 5b (read the ref) to `standing-dispatch.md`, and section 10b (brief citations) to `standing-roster.md`, each leaving a pointer. Section 4's first two paragraphs stay put: they carry decision 0010's only corpus citation, which `policy_lint`'s citation-presence acceptance elides by its recorded spelling and the layout guard refuses on a new line. `orchestrator.md`'s caps are re-recorded down to the measured value.

## Head

64813b0db3547400e9098b63013e0b73b42043e7, merge base `fef4a1351db3e8e328d714e84299284c6876eecb` (origin/main's tip, re-read 2026-10-22T22:42Z; `origin/main` merged in, never rebased; every figure below re-taken at this head).

## Mutation proof

Triage gate, `python3 tools/audit/seat/r10_roster_ops_mutants.py T1 T2 T3 T4 T5` (the plants land in the harness in this PR):
- T1 (the uncited arm `if False`) rc=1 fails=11, first: `triage gate: a proposal-sourced carry citing no ruling is refused`, `triage gate: a new group's brief is judged`;
- T2 (`verdict is None` for `!= "ACCEPT"`) rc=1 fails=11, first: `triage gate: a REJECT ruling is refused`, `triage gate: an entry with no verdict line is refused`;
- T3 (a missing batch read as `""`) rc=1 fails=1: `triage gate: a citation to a missing batch is refused, proposal named or not`;
- T4 (the gate's call in `write_roster` deleted) rc=1 fails=15, first: every `triage gate:` arm;
- T5 (`added_texts` blind to appended carries) rc=1 fails=15, including `added_texts: only what the write adds is judged`.
- The later drop-carry FAIL lines in each are the cascade from `triage gate fixture restored`.

pulse.py, each plant applied by hand, `python3 -I tools/audit/seat/pulse.py --self-test`, then restored:
- `if ages and max(ages) > cadence:` -> `if False:`: 2 failed, `a queued input older than the seat's cadence is STOPPED, naming the seat`, `--snapshot judges the seat queues: exit 1, ...`;
- the seat prefix on a STOPPED origin arm deleted: 3 failed, the three `names the ... seat` checks;
- `if not q["entries"]:` -> `if q["entries"] is None:`: 1 failed, `null control: idle standing seats with nothing queued are ok, and add one arm each`;
- the merge/dispatch choice -> always `"dispatch"`: 1 failed, `a STOPPED merge verdict names the merge seat`;
- roster cadence 60 -> 90: 2 failed;
- the seat-queue loop emptied: the self-test raises KeyError, rc=1.

## Null control

- `python3 tools/audit/seat/r10_roster_ops_mutants.py --null`: `RESULT mutant=null rc=0 fails=0`.
- The gate's own null control, in `roster_edit.py --self-test`: the same `Triage P1 (s9)` carry is refused uncited and lands citing its ACCEPT ruling, and text naming no proposal lands untouched.
- pulse's: an idle seat with an empty queue reads `seat roster: idle, nothing queued`, ok; the 61 min input under a 90 min override reads ok.
- The detector over the live roster, `python3 dev/audit/harnesses/r10_triage_gate_replay.py <roster at 0a326689b>`: `replay: 447 carries, 5 proposal-sourced, 5 refused`. The five are exactly s4's P1-P4 and P5 carries. With `--cite dev/programme/triage/s4-batch1.md`: `5 proposal-sourced, 1 refused`. The one is R10-ARCH-DOCS's P5, which batch 1 does not hold.
- Base `fef4a1351`: `pulse self-test: 22 checks`, `roster_edit self-test: 106 checks`, `r10_roster_ops_mutants self-test: 63 checks`. Head: 37, 116 and 78, all `0 failed`.
- `sweep_render.py` with one contract path misspelt in a template copy: `REFUSED citation: dev/governance/roles/standing-nope.md cited and not in the tree`, rc=1; the head template renders rc=0.

## Figures

- `python3 -I tools/audit/seat/pulse.py --self-test` (3.11 and `/opt/hpo/venv-ci/bin/python` 3.14): `pulse self-test: 37 checks, 0 failed`
- `python3 tools/audit/seat/roster_edit.py --self-test`: `roster_edit self-test: 116 checks, 0 failed`
- `python3 -I tools/audit/seat/r10_roster_ops_mutants.py --self-test`: `78 checks, 0 failed`
- `python3 -I tools/audit/seat/sweep_render.py --self-test`: `21 checks, 0 failed`
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`; `node tools/policy/policy_lint.mjs --budgets` for every cap (not restated)
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`
- `node tools/policy/brief_lint.mjs`: `TOTAL: 0 error(s) across 47 file(s)`
- agreement lane, head copy, `python3 -I tools/policy/agreement_py.py --out ag.json && node tools/policy/agreement.mjs --py-json ag.json`: `AGREEMENT ok`
- agreement lane, BASE copy (`git show origin/main:tools/policy/agreement.mjs`, run beside `counts.mjs`), same JSON: `RESULT divergent=0 unregistered=0 dead=0 refused=0`, `AGREEMENT ok`, rc=0
- `python3 tests/structure.py` (3.11 and 3.14): `STRUCTURE RATCHET PASSED`
- `python3 tools/audit/archscore/score.py --diff fef4a1351 HEAD`: `Architecture score: dS +0.0000 NULL`
- `python3 tests/closure.py select --diff fef4a1351 --workdir $D`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out`, scope.run `tests/entities.py` and `tests/layout.py` (`tests/layout.json` gains the `dev/programme/triage/*.md` glob the layout guard asked for). Before the closure commits it read `MODE: FULL`, with "no recorded closure mentions" the seven contracts that `_is_citation_source` reads for entities.py's #2227 arm.
- `python3 tools/pr/ci_predict.py`: `no closures or fast red predicted against fef4a1351db3`. Before the closure commits it predicted 10: 7 UNCLASSIFIED contracts and 3 INERT READS, the latter written by `--apply-inert` (commit 2).
- `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python tests/entities.py` at this head: `ALL 2399 ENTITY CHECKS PASSED`. Before the closure entry (`PYTHON=/opt/hpo/venv-ci/bin/python ./tests/derive_closures.sh --single tests/entities.py`, two-step, then re-recorded clean at rc=0), the same script read `2 of 2397 ENTITY CHECKS FAILED`, both the classification of the seven contracts. The dispatch says CI owns closures, but `body_push.sh` refuses a head `ci_predict.py` predicts red, so the entry was recorded here on Linux, by the route decision 0014's contracts took (`6ecbf8a9c`).
- `/opt/hpo/venv-ci/bin/python tests/layout.py`: `layout self-test: ok`
- `python3 tests/env_drift.py --claims-only fef4a1351`: `claims hygiene: ... ok`; `python3 tests/closure.py selftest`: `ALL 112 closure shrink pins PASSED`; `python3 tests/layout.py`: `layout self-test: ok`
- target arithmetic, `cd tools/audit/archscore && python3 -c "import score,math; w=score.weights(); print(len(w), sum(w.values()), math.log2(1/0.7)*sum(w.values()))"`: `17 44.18 22.74`

## Approval

Not yet given. This diff is policy (seven new contracts, `orchestrator.md`, `CLAUDE.md`, decision 0015, `policy_budgets.json`), so it merges only on the owner's approving review at the head, or an approval citing the mandate in force with scope all (#201 comment 6329234399), which the dispatch names as covering it.

## Raise justification

`corpus_tokens` is re-recorded to the `--budgets` measurement of this head. `files_tokens` for `CLAUDE.md` rises by the seven role-table rows the carries require, less what was cut. The seven new contracts get caps at their measured values. `orchestrator.md`'s two caps are re-recorded down.

- Payments tried:
  - `orchestrator.md` text (part of section 4, all of 5b and 10b) moved into the standing contracts whose seats now do that work. This is net zero to the corpus by construction: `ratchet-budgets.md`, "corpus_tokens does not move when prose moves". It is what fits `orchestrator.md`'s additions under its own cap.
  - `CLAUDE.md`: the instrument list restating the instruments guide was cut; so was the AGENTS.md sentence restating its POLICY_GLOBS and cap mechanics, which `ratchet-budgets.md` carries; the new rows were shortened. That paid most of the rows' cost; the rest is the raise.
  - Refused: moving the target's conditions or the standing seats' rules into decision 0015, an unmeasured path. That is the residual risk `policy_lint.mjs`'s ADR comment names, the shape `fixer.md` step 17 forbids.
  - Refused: one combined standing-seats file. The carry asks for each seat as its own contract with its own row, and the saving would be four headers.
  - Refused: cutting other seats' contracts to fit. None of their prose is spent by this change.
- Architecture score: dS +0.0000 NULL
- This raise is the mandate's decision (scope all): CLAUDE.md rule 2's exception and 0013's `budget-raise-gate`. It is surfaced here, not taken quietly.

## Architecture score

`python3 tools/audit/archscore/score.py --diff fef4a1351 HEAD`: dS +0.0000 NULL, no gate metric rises.

## Unpinned sites

none: `prepr.sh` step 6d, `the diff adds no unpinned mutation site`.

## Red checks

- `budget-raise-gate`: red by design until an approving review at this head. That is the owner's, or an agent's citing the mandate in force with scope all (#201 comment 6329234399) beside this body's `## Raise justification`. No cheaper detector exists: the check is an approval gate (decision 0013), not a defect detector, and `prepr.sh`'s pr-body step already predicts it locally at no standing cost, which is how this line was owed.

## Forward-carry

- The `audit-plan` workflow and move ledger implement these contracts as landed. The plan hands off at `plan/r<N>`, and the verdict grammar is `Plan review: approve|revise <sha>`; after two `revise` the plan goes to the owner. The move ledger reconciles each merge's `## Architecture score` lines against its move's prediction, and the target's conditions are `architect-planner.md`'s "The programme target", re-read at that group's merge base, not copied. Carry: R10-FLOW-AUDIT-PLAN
- R10-ARCH-DOCS carry 5 cites "triage P5 ACCEPT" with no ruling in the tree. Any re-append or rewrite of that text through `roster_edit.py` is refused until a batch file holding a `## P5:` ACCEPT lands under `dev/programme/triage/`; the replay above shows it (`1 refused` with batch 1 cited). Carry: R10-ARCH-DOCS

## Friction

- ratchet-budgets.md: contradiction: the brief says to pay the new contracts' caps "by moving text, not by raising a cap", but `corpus_tokens` sums every policy file, so a new contract cannot be paid by moving text inside the corpus; only a cut or a raise moves it. Carry: dismissed: answered by this body's raise justification
- policy_lint.mjs: unclear: `named-docs` refuses a policy file that names an uncapped guide (`INSTRUMENTS.md`, archscore's `ABOUT.md`, `sweep_template.md`), and CI grades with the base copy, so `CORPUS_EXCLUDED` cannot be extended in the same PR. The contracts cite the directories instead. Carry: dismissed: worked around in the text, no rule changed
