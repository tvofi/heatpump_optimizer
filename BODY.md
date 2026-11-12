R10-ROUND-PLAYBOOK-FINAL, **draft pass** (dispatched ahead of closure: every carry is answered from the tree at the base; a short final pass after the last after-group merges adds only what merged after this handoff). The round playbook in `dev/audit/README.md` gains the freeze's red definition (carry 29), the pre-v10.0.0 soak step in the closure sequence (carry 30), the P545 lessons and the spelling-corpus rule (carries 27, 28), and the round-11 opening items (brief intake (a) and (b), carries 32-40). Six contracts take the carried paragraphs (carries 14, 15, 16, 18), and `roster_edit.py` reads a `LOG` verdict as itself (carry 18's vocabulary half). Every policy file stays inside its `policy_lint.mjs --budgets` cap: no cap is raised; each addition is paid by cuts of spent prose and by correcting stale claims.

**This is policy.** `CLAUDE.md`, `dev/audit/README.md` and five role contracts change, so it merges only on tvofi's approving review at its head (`CLAUDE.md`, "Where the policy is"). Carry 14's own terms apply: if the owner accepts no cut, that paragraph is closed unimplemented.

## Approval

Awaiting tvofi's approving review at the head: the diff changes `CLAUDE.md`, `dev/audit/README.md` and five role contracts, all of them policy. No budget is raised.

## Head

a8fbc286a5ce5e78838893617cfd440d89bd6354: the fix commit a75d2565170045c6ad90d94009d5bdb5fa2c2cbf merged twice with `origin/main`, last at 19baca76181cb019d9b1cfd93ee6bc0a08e20047 (#3501, #3430, #3504, #3500, #3428; none touches this diff's files). Both merges were clean. `prepr.sh` was re-run in full on the final merged head (stamped 2026-11-12, `git rev-parse origin/main`). The caps, `brief_lint` and the `roster_edit.py` self-test figures below were re-taken after the first merge, and the caps again at this head.

## Mutation proof

`roster_edit.py`'s `VERDICT_LINE_RE` with `LOG` removed from its alternation (the fix's production line), then `python3 tools/audit/seat/roster_edit.py --self-test`: `281 checks, 1 failed`, `FAIL triage gate: a LOG ruling is refused as LOG, never routed (got: )`. Restored: `281 checks, 0 failed`. The prose changes have no executable predicate. Their control is `brief_lint.mjs`'s PLAYBOOK fixture: the renamed-instrument fixture is refused and the null fixture lints clean.

## Null control

At the base, `tools/policy/brief_lint.mjs` prints `PLAYBOOK ok: the renamed fixture is refused for its 7 moved instruments and the null fixture lints clean`. The head prints the same line, and the edited README lints with 0 errors. That is the unchanged-tree control the brief asks for. At the base, a `Verdict: LOG` entry reads `unreadable` (the mutant above is the base's regex), so the base cannot tell LOG from a missing verdict.

## Figures

- Caps, `node tools/policy/policy_lint.mjs --budgets` (columns lines/cap, ~tokens/cap), at the head: `tools/audit/README.md` (the README's cap key, carry 25) 314/321, 6051/6059; `CLAUDE.md` 214/221, 3604/3605; `fixer.md` 315/315, 5215/5216; `orchestrator.md` 294/295, 4246/4251; `architect-planner.md` 84/85, 1261/1261; `plan-review.md` 24/24, 304/304; `proposal-triage.md` 36/36, 488/489. Null control: the same command on the README alone printed 395/321, 7333/6059 before the payments.
- Bytes, `wc -c` base -> head: README 24230 -> 24205; `CLAUDE.md` 14401 -> 14415, where carry 14's paragraph (414 bytes) is paid by 428 bytes of cuts with the token cap unchanged.
- `node tools/policy/brief_lint.mjs`: 0 errors on every linted file; PLAYBOOK fixture line as quoted under Null control.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Scope, `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`. It names `tests/entities.py`, which was run with `PYTHONPATH=tests/hastub` and is green.
- Stale claims corrected, each checked by reading the tree. The README intro said "the three harnesses a judge still re-runs", but its own table lists four. The traps said `optimizer.py` has two `sleep(0.002)` calls; `grep -n 'sleep(0.002)' custom_components/heatpump_optimizer/optimizer.py` returns three (`_lbfgsb_restart`, `_multi_start_minimize`, the DHW-to-space seam), so the text now names them and carries no count. `architect-planner.md`'s "the 17 scored metrics" is a count the tree answers, so it now reads "the scored metrics".

<!-- figure-block: scope-line mb=19baca76181cb019d9b1cfd93ee6bc0a08e20047 head=a8fbc286a5ce5e78838893617cfd440d89bd6354 -->
~~~text
MODE: SCOPED -- 2 script(s) run, 31 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none

## Carries answered

Each carry, 0-based as dispatched, with its answer (carry 31, the one not landed, is under Forward-carry):

- Carry 0, Carry 1, Carry 2, Carry 3, Carry 4, Carry 5, Carry 6, Carry 7, Carry 8, Carry 9, Carry 10, Carry 11, Carry 12: dismissed duplicates of carries 13 to 25 in order (roster marks); each is answered under its kept twin below.
- Carry 13: decided. A decision record is named by number, never by path, so none joins `policy_lint`'s named-docs corpus, and 0015 and 0016 need no caps. The decision is written into the README's "Recorded decisions" item.
- Carry 14: built. The paragraph is in `CLAUDE.md` verbatim, after the fix-or-file rule that binds every seat. It is paid by cutting the four-issues anecdote, the `AGENTS.md` sentence and the duplication-rationale sentence (428 bytes); the token cap is unchanged and not raised. This needs the owner's acceptance of the cuts at review; otherwise it closes unimplemented, as the carry states.
- Carry 15: built. `orchestrator.md` section 9 rotates the orchestrator at a ledger-clean point near 500 k through `state_docs.py` and the resume, and points to the README for seat caps. It is paid by dropping section 9's anecdote counts and tightening section 10's preamble.
- Carry 16: built. (1) `architect-planner.md` step 6 makes the target a floor, not a cap, with cheap moves past it costed beside their dS; its closing paragraph now says a seat is never credited for dS alone. (2) `plan-review.md` step 4 sends back as `revise` a plan that stops at the floor with a cheap move left. `fixer.md` step 17's score bullet makes a production diff take sound score gains in code it touches, with the dS in `## Figures`. (3) was already stated in the README.
- Carry 17: written into the README's round-11 list (`pr_cap.py`'s production slots), because the machinery code half is not this group's seam.
- Carry 18: built. `proposal-triage.md`'s Bar and Verdicts now carry LOG, citing the README's exemption, and `roster_edit.py`'s `VERDICT_LINE_RE` reads LOG (mutation proof above).
- Carry 19: already answered at the base. `grep -n -i owed dev/programme/HANDOVER.md` lists no `pr_cap` owed entry, and the open-PR-cap bullet describes `pr_cap.py` as it is. The exemption is `pr_cap.py`'s module docstring ruling: "opening or updating a pull request for an owed handoff is never refused by it".
- Carry 20: still true at the base. `beat_jobs.py`'s `ROWS` has no dispatch or relay row, so the README keeps "has no row and stays". The final pass re-checks this, and carry 32's retirement item is now on the round-11 list.
- Carry 21: answered by rule. The README states no record-merge figure. The baseline belongs to the 2026-10-24 rule quoted in R10-ROUND-PLAYBOOK's own body, so this draft carries no number.
- Carry 22: still true at the head. The R10-ROUND-PLAYBOOK items stay in the README's round-11 list and production-share paragraph, and the closure sentence is unchanged and verbatim.
- Carry 23: already fixed at the base. `review_packet.py`'s `unnamed_carries` counts 0-based (`range(carries)`) and states that `cloud_dispatch.py` renders from 0.
- Carry 24: already answered at the base. The README's last round-11 item states the one invocation; kept.
- Carry 25: written into the README's round-11 list: re-key the moved files' `policy_budgets.json` caps at their new paths, as a re-key the raise gate reads as no raise. It was not done here because 50 keys still sit under `tools/audit/` (`grep -c '"tools/audit/' dev/governance/config/policy_budgets.json`), and re-keying one alone would split the convention.
- Carry 26: written into the README's round-11 list by pointer to this roster carry (D15's drawn-power gain). Its text stays verbatim on the roster, because restating 350 words in full does not fit the README's cap.
- Carry 27: written into the README as the "Lessons" paragraph after the phase table (all four).
- Carry 28: written. The Lessons paragraph cites `fixer.md` step 2 for the spelling-corpus rule; phase 7's contract column already names `fixer.md`.
- Carry 29: written. Production share now says the machinery is frozen. "Fixes a red" means the required `gate` job's red on main (`tools/ci/gate.py`) or a self-test red the pull request introduces, never one inherited from main. Each round-11 machinery group names its ground. Policy wording: it binds only on tvofi's approving review. See Friction for 10% versus 20%.
- Carry 30: written. The closure sentence is followed by the soak step: the patch release, tvofi's own install, and the card's tabs opened before v10.0.0, never without.
- Carry 32: written into the round-11 list (seat retirement, its precondition, the s14 load, size L, design first).
- Carry 33: written. Every round-10 group at stage deferred reopens as written, and the re-homes to the groups owning `merge_train.py`, `tools/pr/cancel_superseded.py` and `tests/entities.py` are named with their triage batches.
- Carry 34: written through the same deferred-groups item; R10-DISINFECTION-STEP-NOTICE is at stage deferred.
- Carry 35: written into the round-11 list by pointer (the stubs bump).
- Carry 36, Carry 37 and Carry 38: written into the round-11 list by pointer (R10-CI-PRIORITY-PAUSE's three).
- Carry 39: written into the round-11 list by pointer (the boost settling tail).
- Carry 40 (appended after dispatch): written into the round-11 list by pointer (R10-PREPR-RESIDUE's seven).
- Brief intake (a) and (b): the round-11 list names R10-PROTECTION-CENSUS's rows as the intake baseline (the census is in progress at this draft; the final pass adds its result) and B1 as conditional on it, unless the owner orders it into round 10.
- The `CLAUDE.md` index row for `dev/audit/README.md` is unchanged, because the README's role did not change.

## Forward-carry

- Carry 31: not landed; this is the one forward carry. `dev/governance/dimensions/D13.md` is at its exact cap (79/79 lines, 1149/1149 tokens), and the carry forbids changing any other sentence, so no payment exists. D11.md has 5 tokens of headroom. The scorecard has not landed, because R10-TICK-RESIDUE-P3 is deferred to round 11 (carry 33). Both paragraphs need the owner's budget-raise confirmation, which this seat may not presume. The README's deferred-groups item reopens the scorecard group. Carry: R10-ROUND-PLAYBOOK-FINAL (final pass: land both paragraphs after the owner rules on the D11 and D13 raise)

## Friction

- production-share: contradiction: carry 29 quotes the 2026-11-01 freeze as "proves 20%" (from a plan's constraints table, triage P664), but the same ruling as recorded on R10-ROUND-PLAYBOOK's carry 19 and in the README says "more than a 10% improvement". The README keeps 10%, and `proposal-triage.md` keeps its separate over-20% exemption to add machinery. Carry: R10-ROUND-PLAYBOOK-FINAL (owner ruling at review)
- named-docs: cost: every carried policy addition here had to be paid inside a file at or within a few tokens of its cap (seven files), and carry 31 has no lawful payment at all. Carry: R10-ROUND-PLAYBOOK-FINAL (owner ruling on the D11 and D13 raise)
