Triage batch 88 rules the orchestrator s8's slip proposal of 2026-10-31 06:30Z. `review_carry.py` printed FRESH-REVIEW for #3014 (`42b228ec` to `c41c4053`, one automatic main merge) because main had moved context lines around the branch's edits. The proposal is to compare change lines only. This is the next rolling batch after batch 87, with one ruling and no roster op.

- **P325: REJECT for code files.** P17, the brief of R10-FLY-CARRY-DOC-CONTEXT, already carries context-only differences in `*.md` and keeps code strict (`py-context no` is one of its controls). That ruling stands.
  - **Hunk headers are already handled.** `app_approve.sh` `carry()`'s `norm()` already drops `@@` headers and `index` lines, so a pure line shift carries today.
  - **#3014's difference is in code.** It is context in `tests/closure.py` and `tests/doc_claims.py`, where main replaced calls directly beside the branch's added checks. That is the adjacency P17 keeps under review.
  - **The `range-diff` evidence is vacuous here.** A merge-forward keeps the branch's commits as they were, so `range-diff` prints `=` for every merge-forward.
  - **Benefit, measured: about one delta review a week.** Of the merged PRs since 2026-10-17 whose head moved by merges only, 153 compare equal today, 9 differ in context only and 7 differ in change lines. All 9 context-only PRs predate 2026-10-24, and #3014 is the only one since.
  - **The trade is marginal.** About one delta review a week does not clearly pay for losing review of main's adjacent code.
  - **Re-open trigger:** at least 5 delta reviews of context-only code heads that found nothing in the adjacent lines.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`628c067c7e9c6081a1b414b0b1757bee2348b223`; the file is the whole diff against `4822c8f9b`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P325 as `REJECT`. A probe carry citing `triage: dev/programme/triage/s6-batch88.md#P325` is refused: `dev/programme/triage/s6-batch88.md#P325 is not an ACCEPT ruling (REJECT)`.
- With `Verdict: REJECT` changed to `Verdict: ACCEPT`, the same carry passes: `triage_refusal` returns None.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it as not on the roster branch or origin/main.

## Figures

- #3014: `norm()`-style diffs of `437f1ba9..42b228ec` and `4822c8f9..c41c4053` differ in 8 lines across two hunks, all of them context. The `+`/`-` lines alone compare equal.
- The merged-PR probe over first-parent merges since 2026-10-17, with `verdict/<N>` tips: 231 at the head, 12 with branch-own commits, 153 equal, 9 context-only, 7 with a change-line difference.
- `tools/pr/app_approve.sh` line 390: `norm()` drops `index` lines and rewrites `@@ .*` to `@@`.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
