R10-FLY-MANDATE-REVOKE-GUARD (S, instrument), built with triage P336's amendment (dev/programme/triage/s6-batch94.md#P336, on `handoff/triage-s9-batch94` until batch 94 merges) and the dS value-check carry from the #3045 fix review (roster `origin/handoff/audit-r10-roster`, this group's `carry`).

Issue #2724 is this group's, and the roster lists it under `issues` with `fixes: []`, so the body names no closing keyword (prepr step 7's intended list refuses one); the roster's `fixes` is the orchestrator's to set.

Carry 1, the roster's only carry for this group (the #3045 fix review's dS value check), is built. `measured_score` and `score_check` in `budget_raise_gate.py` refuse a planted false IMPROVES and pass the true figure (Mutation proof B2 to B4, and Figures, the score arm).

Two defects, one owner each:

- **The revocation kill switch fires on a seat's own words.** `budget_raise_gate.py` voids a mandate on any owner-account #201 comment whose current body holds the revocation word stem and the mandate comment's id as a whole number. Two instances: comment 6322712314 (2026-10-21, about 6 h of frozen mandated raises) and comment 6546832523 (2026-10-31), a state comment naming this group, whose name carries the stem, beside the session mandate's id. #3006's `budget-raise-gate` read it at 18:43Z. Nothing stopped either post, and an edit (`gh_comment.py patch`) revokes the same way, because the gate reads every comment's current body.
- **The raise justification's score line was shape-checked only.** #3045's round-1 body claimed `dS +0.0012 IMPROVES` on a diff that scores `+0.0000 NULL`, passed the gate and reached a mandated approval.

What changed:

- `tools/policy/budget_raise_gate.py`
  - The inline revocation test in `mandate_state` is now `revokes(body, cid)`, behaviour unchanged (the self-test's revocation rows pass unchanged, and a new row pins the leading `(?<!\d)`).
  - `mandate_grant(comment)` is the first-line grammar reading, shared by `mandate_state` and the new `revocable(comment, now)`: an owner comment on #201, its first line the grammar, its window not closed.
  - On the mandated arm, `gate()` runs `measured_score(base, head)`: the **base's** `tools/audit/archscore/score.py --diff <merge-base> <head>`, from a scratch worktree of the base, as `arch-score.yml` runs it, so a head cannot edit the scorer that grades it. Then `score_check` refuses a `## Raise justification` with no score line whose dS (at score.py's four decimals) and verdict word equal the measured ones. A scorer that fails, or prints a line that does not parse, is a refusal.
- `tools/pr/gh_comment.py`: `post` and `patch` are refused when the target is #201 on `tvofi/heatpump_optimizer` (for a patch, the comment's `issue_url`, read from the API), the gate's own `revokes()` holds for the body, and the gate's `revocable()` reads the id as a grant in the live #201 thread. The exception is `--withdraw-mandate <cid>` naming that id. Both predicates are imported, never copied. Fast path: a body without the gate's `MANDATE_REVOKED` match reads nothing more. That regex is `revokes()`'s first conjunct, and its docstring says so.
- `tools/audit/seat/pr_args.sh`: its rowless fixture copies `gh_comment.py` into a mock tree. It now copies the gate and `tests/layout.py` beside it, which `gh_comment.py` imports.
- `tools/audit/seat/r10_mandate_guard_mutants.py`: the in-tree mutant driver (eight plants, `--null`, `--self-test`). `.github/workflows/governance.yml` runs its `--self-test`, as it does for the other r10 mutant drivers. `dev/audit/harnesses/r10_mandate_guard_instances.py`: both field instances, replayed against any tree. `tests/closures.json`: the two new files classified (`ci_predict.py --apply-inert`).

Design choices, stated:

- **The guard does not ask which account is posting.** It does not know which one `gh` holds, and a seat rewords at no cost.
- **An expired grant is not guarded.** A grant whose end does not parse is guarded.
- **Only one score line must match.** The section's other score lines report payments tried, on trees the gate cannot rebuild, so they stay shape-checked. Residual: a false line beside the true one passes.
- **Stated gaps, not built:**
  - A raw `gh api` or `gh issue comment` post bypasses the guard (`comment-readback.md` makes this file the posting instrument).
  - `merge_train.py`'s approve and `--check-body` still judge the justification's shape only. The required `budget-raise-gate` context is where the figure is checked, and the train stops on that red.
  - The measurement costs about 59 s of CPU, measured on this machine with `score.py --diff` over a 5-commit diff, and only on the mandated arm. The gate job's `timeout-minutes: 5` is unchanged.

Alternatives considered:

- Reading the `arch-score` job's log was rejected: it needs `actions: read`, and that job can finish after this one.
- Building the guard's candidate ids from digit runs in the body was rejected: it re-implements the whole-number test, and P336's named mutant would pass it.

## Head

86123b4e363b846d337b51ac9a89630eb140c94a, cut from origin/main a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0. `git diff $(git merge-base origin/main HEAD)...HEAD --stat`: 7 files, +544/-29.

## Mutation proof

`env -u BASH_ENV python3 tools/audit/seat/r10_mandate_guard_mutants.py` (each plant applied, both self-tests run, file restored): `RESULT plants=8 killed=8`. The failing checks per plant:

- G1, P336's named mutant: `gh_comment.py` re-implements the id test without `(?<!\d)`. Fails `arm6_id_inside_a_longer_number_posts (the gate's whole-number test)`.
- G2, the patch is never judged as a #201 comment. Fails `arm6_brief_row_refused_on_patch` and `arm6_field_text_refused_on_patch`.
- G3, `--withdraw-mandate` passes whatever id it names. Fails `arm6_withdraw_naming_another_id_is_refused`.
- G4, `run()` never calls the guard. Fails 6 checks: both brief rows, both field-text rows, the other-id withdraw row and `arm6_a_thread_read_that_fails_refuses`.
- B1, the gate's `revokes()` loses `(?<!\d)`. Fails `gh_comment.py: arm6_id_inside_a_longer_number_posts` and the gate's `mandate: a revocation naming a longer id that ends in this one revokes nothing (null control)`.
- B2, a well-formed section is never compared with the measured figure. Fails 8 checks, among them `score: a planted false IMPROVES under a mandate is refused` and `score: a scorer that fails is a refusal`.
- B3, the scorer runs from the head. Fails `e2e: ... and on a head whose own scorer prints it under a mandate exits 1, naming the measured figure`.
- B4, the dS is compared and the verdict word is not. Fails `score: the same dS with another verdict word is refused`.

`pr_args.sh` with the copy deleted, `env -u BASH_ENV bash tools/audit/seat/pr_args.sh --self-test`: `156 checks, 8 failed`, against 6 with it. The two added FAILs are `open_pr: a refused row push closes the PR with a read-back comment naming the refusal, and leaves no stranded worktree` and `open_pr: a step errexit stops after the PR exists (its title edit) closes it with a read-back comment naming the stop`. The other 6 are the host's own, the same set at the base (Figures).

## Null control

- `r10_mandate_guard_mutants.py --null` (no plant): `RESULT mutant=null rc=0 fails=0`.
- Guard rows that must pass: the brief's text with `--withdraw-mandate` naming the id; the stem with no mandate id; a mandate id with no stem (which reads no thread); a non-#201 post (no thread read); a patch of a non-#201 comment; another repository; the field text with the group's name replaced, on post (no thread read) and on patch; an id inside a longer number; an expired grant; a grant by another account; a stem beside a comment that is no grant.
- Score rows that must pass: the true figure; the same figure at fewer decimals; `-0.0000` read as `+0.0000`; the true line beside a payment's own line; score.py's `(inadmissible: ...)` suffix.

## Figures

- `env -u BASH_ENV python3 tools/policy/budget_raise_gate.py --self-test | tail -1`: `budget_raise_gate self-test: 255 checks, 0 failed`. At the base: 237 checks, 0 failed.
- `env -u BASH_ENV python3 tools/pr/gh_comment.py self-test | tail -1`: `SELF-TEST PASSED` (`TOTAL: 0 failed`).
- `env -u BASH_ENV python3 tools/audit/seat/r10_mandate_guard_mutants.py --self-test | tail -1`: `r10_mandate_guard_mutants self-test: 8 checks, 0 failed`.
- Finder's harness, both ends: `python3 dev/audit/harnesses/r10_mandate_guard_instances.py <tree> guard <dir>` and `... <tree> score`.
  - Base export a7dd7f50d: `body=field rc=0` (the defect: posts), `body=field-without-word rc=0`. Score: both claims `accepted=True`, `measured=None`.
  - Head: `body=field rc=2` (REFUSED, naming the session mandate's comment), `body=field-without-word rc=0` (null control). Score: `+0.0012 IMPROVES` `accepted=False` against `measured='Architecture score: dS +0.0000 NULL'`, and `+0.0000 NULL` `accepted=True` (null control).
  - The guard arm reads the live #201 thread, and the score arm runs score.py on #3045's round-1 head b02ffd170d5049d8869689cbc889a5cf46097a1e.
- `env -u BASH_ENV bash tools/audit/seat/pr_args.sh --self-test` at the head and at the base export: `156 checks, 6 failed` both. `diff` of the two FAIL sets is empty. They are this macOS host's own (`sed: invalid command code`, `pr_bounded` timing), and the rowless arm, which posts through `gh_comment.py`, passes.
- `python3 tests/structure.py | tail -1`: `STRUCTURE RATCHET PASSED`.
- Scoped gate, `tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 0 script(s) run, 33 scoped out`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `no closures, fast, governance or instrument red predicted`, after `--apply-inert` wrote the two INERT READS entries and the governance step wired the driver's self-test.
- `env -u BASH_ENV bash tools/pr/prepr.sh`, no `PREPR_SKIP_CLOSURES`: `PRE-PR: 86123b4e363b846d337b51ac9a89630eb140c94a ... rc=0`, with `MODE: SCOPED`, `self-test 431 passed, 0 failed`, and `ci predict` printing `CI PREDICT: no closures, fast, governance or instrument red predicted against a7dd7f50d67e`, so 0 predicted reds. Its `closures` step printed its own skip: `the diff cannot be scoped, so CI re-records every closure; a full derive here is forbidden`. `--body-check` on this body: pr-body, carry, preflight, figures and ref_privacy all ok.
- Architecture score: the diff touches no file under `custom_components/`, which is all `score.py` reads.

## Unpinned sites

`none`: step 6d listed no site, because the diff adds none under `custom_components/`. The `tools/` predicates this diff adds are pinned by the in-tree driver `tools/audit/seat/r10_mandate_guard_mutants.py`, which killed 8 of 8 (Mutation proof).

## Red checks

`none` on this branch. The triggering reds, answered:

- #3006's `budget-raise-gate`, red on the second instance. Cheaper detector: this guard, at post time. Standing cost: one #201 thread read, only for a #201 body holding the stem.
- #3045's metric-gamed approval. Detector: `score_check` in the required context. Standing cost: one base-scorer run on the mandated arm only.

## Forward-carry

`none`

## Friction

`none`

## Approval

Owner approval is owed before merging, or the orchestrator's under a mandate in force that covers it. `.github/workflows/governance.yml` is code-owned (`/.github/workflows/`). `tools/policy/budget_raise_gate.py` and `tools/pr/gh_comment.py` are policy instruments.
