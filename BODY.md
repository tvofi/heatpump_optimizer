Group: R10-FLOW-DESIGN-POLICY (registration pending: roster PR-B). Spec: pack file `dev/programme/flow-study/roster/groups/R10-FLOW-DESIGN-POLICY.json` at pin ddacf9856acb612692d1e9c8a28f0433d16219b3 (fields `brief`, `files`, `carry`; `architect_note` is empty), with `design-seats/STUDY.md`, `designer.md`, `design-review.md` and FUTURE-STATE section 11 items 46–53 at the same commit. Authority: owner ruling 2026-10-21, RULINGS-201-3.md at the pack commit (R16–R19).

**This is policy.** Every file it changes is code-owned (`dev/governance/roles/`, `dev/governance/decisions/`, `CLAUDE.md`, `dev/governance/config/policy_budgets.json`), so it merges only on the owner's approving review at its head.

What it lands, item by item against the brief:

1. **Two role contracts**, `dev/governance/roles/designer.md` and `dev/governance/roles/design-review.md`, from the drafts at the pack commit. They keep the drafts' steps and scope. Three changes:
   - **Threshold.** The drafts' "Applies to" named only L/XL groups of kind `arch` or with `coordinator.py` in their hot files. R17 and FUTURE-STATE item 47 name every L/XL group with no approved design, pre-study or prototype (7 eligible, 5 exempt). The contract follows the ruling.
   - **Shortened against `fixer.md`.** The evidence plan and the sibling-site census cite `fixer.md` steps 2–4 and 8 instead of restating them. The "modelled on" source lists and the "after the moratorium" landing note are cut: they were the drafts' motivation, and the study keeps them.
   - **What the ruling and §11 add.** The "moratorium bars a new class" line is dropped (R16). The 1-h revalidation box is marked hard (item 47). Each seat reports its token count where the harness gives one (item 53). The verdict goes to `design-verdict/<group>`, and the orchestrator reads it back from there, because seats make no GitHub write (decision 0011). Those are the ref names STUDY §8 step 5 and item 48 give.
2. **`orchestrator.md` section 5** gets one bullet. Dispatch the designer when the group's last predecessor dispatches, the design reviewer at the design's head, and the fixer only after `Design review: approve <sha>`. The approved note is the group's architect note.
3. **`fixer.md` step 17**: the architect note is followed, and a departure is raised, not made.
4. **`fix-review.md` step 15**: a departure from the architect note or the approved design note is `architecture-unsound`.
5. **`CLAUDE.md`** names both contracts in its role table.
6. **Decision 0014** (`dev/governance/decisions/0014-design-seats-and-the-end-of-0012s-moratorium.md`) records R16–R19, the rationale and the monitoring (STUDY §8's kill and keep criteria). **Decision 0012** points to it, both in its moratorium section and in a new "Superseded in part (2026-10-21)" section. Its cadence, its one enforcement point and D14's stop rule stand.

Alternatives considered:
- **A second document beside the architect note.** Rejected: STUDY §7 extends the note, and one artifact means fix review judges one thing.
- **Restating the design step in `fixer.md`.** Rejected: the orchestrator's bullet is the one place it lives. `fixer.md` already binds the note, and its file is at its cap.

## Head

87c3672fbd5a645915ec80709ea28ec7cac0788f, measured 2026-10-21T18:52Z. It merges origin/main 57f0c9c77cfd5958e0a2443e158bea8326bedae2, never rebased, on top of three commits:
- the change commit 3ecf461753;
- a merge of origin/main 4b36dc7301;
- the closure record 6ecbf8a9cb.

`git merge-tree --write-tree origin/main HEAD` is clean. Neither merged-in main delta touches a policy file, and `--budgets` reads the same across both merges.

## Mutation proof

The checks that pin this change are `policy_lint.mjs`'s `index` and `budgets` classes. Each mutant was applied in a detached worktree at the change commit and restored:

- **M1.** Delete the two `CLAUDE.md` role-table rows. Two `[index]` errors: "`CLAUDE.md` does not name `dev/governance/roles/design-review.md`", and the same for `designer.md`. TOTAL 2.
- **M2.** Restore `corpus_tokens` to the base cap. One `[budgets] (whole corpus)` error. TOTAL 1.
- **M3.** Drop `designer.md`'s per-file caps. One `[budgets]` error ("no line cap recorded") and one `[named-docs]` error. TOTAL 2.
- **M4.** Set `corpus_tokens` one below the smallest cap that passes (measured minus `_band`). One `[budgets] (whole corpus)` error. TOTAL 1. So the recorded cap is the measured value (`ratchet-budgets.md` step 3), not padded.

No production code line changed, so there is no production mutant to draw (`changed_lines`), and there are no unpinned sites.

## Null control

- M0: the same worktree, unmutated, prints `TOTAL: 0 error(s) across 43 policy file(s)`. At origin/main it prints 41 policy files: the two contracts are the new files.
- `score.py --diff origin/main origin/main` prints `dS +0.0000 NULL`, the baseline the "after" score below is read against.

## Figures

All taken at the head above unless a line says otherwise.

- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 43 policy file(s)`, exit 0; `FIXTURE ok`.
- `node tools/policy/policy_lint.mjs --budgets`, corpus line: about 62423 tokens against a recorded cap of 62423. At origin/main f2fb1b0e the corpus read about 61142 against a cap of 61026 (both plus the 500 band).
- `--budgets`, per-file rows at origin/main against the head:
  - `orchestrator.md`: 317 lines / 4502 tokens → 318 / 4511 (cap 319 / 4513);
  - `fixer.md`: 315 / 5215 → 315 / 5212 (cap 315 / 5216);
  - `fix-review.md`: 140 / 2451 → 140 / 2451 (cap 140 / 2451);
  - `CLAUDE.md`: 206 / 3410 → 208 / 3498 (cap 221 / 3590, always-loaded within its band);
  - `designer.md`: new, 46 / 666, capped at exactly that;
  - `design-review.md`: new, 35 / 521, capped at exactly that.
- `python3 tools/audit/archscore/score.py --diff origin/main` (after): `Architecture score: dS +0.0000 NULL`. Before, `--diff origin/main origin/main`: `dS +0.0000 NULL`.
- `node tools/policy/rules_sync.mjs --check`: exit 0.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/throwaway_git.py --check`: 0 raw git init or clone sites, 0 stale allow entries.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, and `scope.run` names `tests/entities.py`. Before the closure record it was `MODE: FULL`, because no recorded closure mentioned the two new role files. `tests/entities.py` reads `dev/governance/roles/*.md` as citation sources (`tests/closure.py`'s `_is_citation_source`), and it failed exactly two checks at 2c0a954c: "every tracked file is either measured or deliberately classified" and the #2312 citation-source check, both naming the two files. Commit 6ecbf8a9 records them into `tests/entities.py`'s closure with `tests/derive_closures.sh --single tests/entities.py` on Linux, by the two-step route `gate-scoping.md` names (`--record-only`, then `closure.py merge --partial --allow-failures`), because the recording fails on the classification it records. It then re-records clean: `done tests/entities.py (exit 0)`, rc 0. The diff to `tests/closures.json` against origin/main is those two paths.
- `tests/entities.py` at the head: see the last line of this section. `tests/layout.py`, `tests/closure.py selftest`, `tests/harness_headers.py` and `tests/env_drift.py --claims-only origin/main` exited 0 at 2c0a954c under the pinned seat interpreter, which differs from the head only by the closure record and delivery rows.
- Payment arithmetic, tokens as `--budgets` counts them (bytes/4 per file). Each file was rebuilt with only the addition applied, then compared with the head:
  - `orchestrator.md`: the addition alone costs +89 tokens / +5 lines, and 80 / 4 were paid inside the file;
  - `fixer.md`: +8 / 0, and 11 were paid;
  - `fix-review.md`: +5 / 0, and 5 were paid;
  - the drafts, at 828 and 652 tokens, became contracts of 666 and 521.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` at 87c3672f: `ALL 2382 ENTITY CHECKS PASSED`, exit 0. The null control is the same script at 2c0a954c, before the closure record: `2 of 2382 ENTITY CHECKS FAILED`, the two classification checks named above.

## Raise justification

The raise is `corpus_tokens` alone, re-recorded to the measured value. The two new per-file caps are classification of new policy files at their measured size, which `checkBudgets` requires. No existing file's cap moves. The owner's ruling R19 approves the corpus-cap raise; it still merges only on the owner's approving review at this head (budget-raise-gate, decision 0013).

Payments tried:
- **Shorten against `COMMON.md` and `fixer.md`.** Taken: the contracts cite `fixer.md` steps 2–4, 8 and 17 instead of restating them, and the drafts' source lists and landing notes are cut, about 293 tokens below the drafts. Nothing in `COMMON.md` (the finder's contract) overlaps a design step, so nothing there could be cited.
- **Delete spent or duplicated prose in the files this PR edits.** Taken; it paid each edit inside its own file, so no per-file cap moves:
  - `orchestrator.md`: "A sample is not a quantifier", which `fixer.md` step 3's "every"/"none" rule already carries; "These sections do not replace the source rules", which section 0 already says; the `preflight.sh` motivation clause; and two tails;
  - `fixer.md` step 1: the stamp sentence `CLAUDE.md` rule 4 already states;
  - `fix-review.md`: two rewordings.
- **Delete more elsewhere in the corpus, to pay the whole corpus delta.** Not taken. The remaining candidates in the three edited contracts each carry a measurement, a decision or an incident under `writing-for-agents.md`'s uniqueness test. Cutting them to fit is the "delete working functionality merely to fit" `CLAUDE.md` rule 2 forbids.
- **Move prose into an uncapped file.** Not a payment: `corpus_tokens` does not move when prose moves (`ratchet-budgets.md`), and a move into an excluded file is the escape `checkOrphanCaps` refuses.
- **Leave the cap and stay inside the band.** Not possible: the head measures more than the base cap plus `_band` (M2).

Architecture score: dS +0.0000 NULL

## Red checks

- `budget-raise-gate`: red by design until the owner's approving review at this head. It reads three raises in `policy_budgets.json`: `corpus_tokens` 61026 → 62423, and the two new per-file entries for `designer.md` and `design-review.md`. No cheaper detector is owed. The gate is already the earliest detector for an unapproved raise, it runs at push time, and approval is the owner's to give, not something a push can supply (R19, decision 0013).

## Forward-carry

- The verdict grammar R10-FLOW-DESIGN-STAGES must parse and mechanise is fixed by `design-review.md` step 7: `Design review: approve <sha>` or `Design review: revise <sha> <class>`, at `design-verdict/<group>`, with the design at `design/<group>`. Its pack carry already says its templates cite these contracts, and it merges after this group. Carry: dismissed: pack carry already binds it

## Friction

- policy_lint.mjs: unenforced: the comment on `CORPUS_EXCLUDED` says the next ADR costs a line in that list, but decision 0014 added without one keeps TOTAL at 0, measured above, and the `policy-docs` job restores that file from the base before grading, so a branch-side line would not reach CI either. Carry: dismissed: outside this group's files
- fixer.md: cost: the session's default `python3` was 3.11 without the pinned dependencies. `tests/entities.py` raised a SyntaxError and `tests/harness_headers.py` failed on the missing `voluptuous` module until the seat venv `cloud-setup.sh` builds was put first on PATH. Carry: dismissed: environment setup, not policy

## Approval

Awaiting the owner's approving review at the head. The change is authorised by owner ruling 2026-10-21, RULINGS-201-3.md at the pack commit ddacf9856acb612692d1e9c8a28f0433d16219b3: R16 voids 0012's moratorium, R17 adopts the seats, and R19 approves the corpus-cap raise. That ruling is not the approval. Every changed policy and budget path is code-owned, so `main-protect-checks` and `budget-raise-gate` merge it only on the owner's own review at this head.

## Attribution

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01TXZwxcxTebvpufuWFE43aU
