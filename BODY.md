_Requested by **tvofi**_

Round-9 F11.5: the nine policy drafts tvofi approved (cards A1-A9) land as policy text, one commit each, each naming the process state it addresses. Part of #201. No finding is fixed here and no code changes; this PR builds what tvofi commissioned. It is policy (code-owned): it merges only on tvofi's approving review at the head, and the budget raises below on the budget-raise gate.

RCA source path of every draft: `handoff/audit-r9-plan:handoff/round9/state/rca/<slug>/RCA.md` for the recompute, future-instant and I5 write-ups (their own `handoff/r9-rca-*` branches carry only prototypes); `handoff/r9-rca-p2`, `-i3` and `-i4` carry theirs under `tools/audit/round9/rca/`.

| card | file and place | state | source |
|---|---|---|---|
| A1, A2 | `fixer.md` step 8: a P2 finding's rule is a P2 owners registry entry; a census asserts its preconditions (A1 rides here, A2) | (c) | rca/p2 |
| A7 | `fixer.md` step 8: a fix to one reader of a governance concept registers it in `agreement.mjs` | (a) | rca/i4 |
| A3 | `fixer.md` step 15: a per-row twin removes re-entry, not work; re-measure the cost | (c) | rca/avoidable-interpreter-bound-recomputation |
| A5 | `fixer.md` step 16 (new): an age from a stamp ahead of the reading clock is unknowable, never 0 | (b)-shaped | rca/persisted-future-instant-trusted-without-bound |
| A6 | `root-cause.md` section 2: an instance of an already-barriered class is not state (a) | (c) recorded as (a) | rca/i5 |
| A4 | `D1.md` step 2: a stamp written by a clock ahead of the reader, across a restart | (c) | rca/persisted-future-instant-trusted-without-bound |
| A8 | `tests/README.md` no-copies section: one governance tool must not re-implement another | (a) | rca/i4 |
| A9 | `defect-root-cause.md`: a check over a structured input is covered by `field_coverage.mjs` | (c) | rca/i3 |

**Choices that are mine, not the drafts'.** The A5 and A8 phrasing and placement are the seat's: the draft for A5 names no location, so it is a new step 16 (cross-references to step 15 stay valid), and the A8 draft says the section gains "and one governance tool re-implementing another", which is that clause in the section's first sentence. The A1 and A7 paragraphs are placed after step 8's closing sentences ("... a reviewer refuted all three a draft quoted."), so that step's "This is step 11 ... #592 added this step" stays attached to its own text; the words are the drafts'. **A9 clause:** the draft read "a check over a structured input is registered in `field_coverage.mjs`"; with F11.3's derivation built (card C10) only the trailing clause changed, to "a governance check is in the derived set and registers its input or declares none". A4, A3, A6 and A1/A7 are the drafts' words. Nothing else deviates from the drafts.

**Budget raises (CLAUDE.md rule 2; the order in `ratchet-budgets.md`).** Prose was not cut, because the drafts are approved text and cutting other policy would be an unapproved policy edit. One commit raises five caps to exactly the measured value, nothing padded, `_band` untouched: `fixer.md` 280 to 295 lines and 4585 to 4866 tokens; `D1.md` 58 to 60 and 784 to 819; `root-cause.md` 81 to 84 and 951 to 998; `defect-root-cause.md` 146 to 149 and 1774 to 1813; `corpus_tokens` 55433 to 56039. Card B4 allowed the first three; `defect-root-cause.md` and `corpus_tokens` extend B4 under the mandate, announced on #201 comment 5956454383. `tests/README.md` needs no raise.

**Open, nothing built: the tenth card.** `stamp.py`'s `unattributed_direct_pushes` is still unwired (pinned in its self-test only). Gating a release on it needs tvofi's call on the pre-decision-0010 legacy fixture (the `_w/ccc3333` row): re-demand a sha citation there, or scope the check to commits after a cutoff tag. No decision exists, so it is undecided and this PR wires nothing.

**Accepted residual (card C11, carried from F11.4).** A second reader with a different grammar for an unregistered governance concept stays undetected beyond the A7 and A8 text. Accepted by tvofi; nothing is built for it.

## Head

4fa6bbe8633be2b9e2b02f26f292e8d7d2cf7b98

## Mutation proof

The change is prose and caps. The detector it must satisfy is `policy_lint`'s per-file and corpus budgets: the cap-record commit's `policy_budgets.json` replaced by main's copy turns it red (9 errors), restored it is green (0).

## Null control

`policy_lint.mjs` at the merge base prints 0 errors; at this head with main's `policy_budgets.json` it prints 9 (above); at this head it prints 0. The class sweep: the roster names no class for F11.5 (`Class sweeps (final): .`), no finding and no instance, so there is no `fixer.md` step-8 enumerator to run and no seam to disposition.

## Figures

- `node .claude/workflows/policy_lint.mjs` at this head: `TOTAL: 0 error(s) across 40 policy file(s)`; the same with main's `.claude/workflows/policy_budgets.json`: `TOTAL: 9 error(s) across 40 policy file(s)`; at the merge base 8fa06663c: 0.
- `node .claude/workflows/policy_lint.mjs --budgets` prints the measured values the raises record (the instrument, not a restated number).
- `node .claude/workflows/rules_sync.mjs --check`: ok, `.cursor/rules/defect-root-cause.mdc` regenerated.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED -- 1 script(s) run, 27 scoped out.`

## Red checks

`budget-raise-gate` is red, as designed: this PR raises policy caps, and the gate refuses until tvofi's approving review at the PR head (decision 0013; budget-raise-gate). No cheaper detector exists or is needed: the gate is the detector for an unapproved raise, and it goes green on that review. The red is expected at every push until then.

## Forward-carry

none

## Friction

none

## Approval

tvofi approved each draft on decision cards A1-A9 (2026-09-26; A9 over the recommendation to skip it) and the cap raises for `fixer.md`, `D1.md` and `root-cause.md` on card B4; the raises for `defect-root-cause.md` and `corpus_tokens` extend B4 under the mandate (#201 comment 5956454383). This PR is policy and code-owned: it merges only on tvofi's approving GitHub review, owed at the final PR head, given under tvofi's mandate (comment 5951564627). `budget_raise_gate.py` accepts an approval only at the PR head, so the review must name that head, not an earlier one.
