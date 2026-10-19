Round 10 hand-rolled variants of canonical instruments: a tick driver in session scratch instead of `tick_loop.sh` under `daemonize.py`; a private cloud relay and a cloud-reviewer payload helper instead of `cloud_relay.sh` and `cloud_dispatch.py`; a typed sweep prompt instead of `sweep_render.py`; shell merge-poll loops instead of `merge_pr.sh --mandate`, `proof_watch.py` or `merge_train.py`; python/gh body edits with no read-back instead of `head_note.py`/`push.sh`/`body_push.sh` (one blanked two PR bodies); ad-hoc job-log greps instead of `failure_logs.sh`; hand `gh run rerun` instead of `ci-watch.sh`/`autofix_statuses.sh`; and the canonical relay run over un-ledgered state replayed 80 stale probe refs. Root cause: the orchestrator contract never sent the reader to the instruments guide, and nothing required re-checking briefs when an instrument landed. The new text is one paragraph and four bullets to `orchestrator.md` section 13 (look up first; a new helper needs a reason and lives in `tools/`; render the sweep; re-check briefs on a merge; seed a stateful instrument's ledger first) and one pointer sentence in `nudge.md` step 18. It is paid for inside `orchestrator.md`: the section 8 restatement of `CLAUDE.md`'s rule is shortened (that deletion lowers the recorded duplicate count in `policy_known_bad.json` from 6 to 1, as the lint required), the stdin paragraph of section 4 is reflowed (all three misleading modes kept, including held-open stdin), and a few sentences elsewhere are trimmed. Round 1's rule-dropped finding restored the held-open clause and the tag-citation, step 9 and not-when-CI-settles clauses. It names the guide and the template without their file names so `named-docs` does not pull those usage guides into the corpus. No `.cursor` rule changed; `rules_sync.mjs` wrote 0 files.

## Head

26189a1fdf61777848fca426634bcc14b07a0f93

## Approval

This changes policy (`orchestrator.md`, `nudge.md`). Authority is tvofi's round-10 mandate on #201, comment 6175172275 (https://github.com/tvofi/heatpump_optimizer/issues/201#issuecomment-6175172275), scope all, valid to 2026-10-28, quoted verbatim:

> MANDATE: agents may approve as tvofi, scope all, from 2026-10-14T18:14Z until 2026-10-28T18:14Z

Context only, not the approval: tvofi in chat on 2026-10-19 directed this edit: "Yes, update orchestrator.md and any other policy documents where the existence of canonical instruments in instruments.md needs to be reinforced. Budget raises ok." No cap is raised: the new text is paid for by deleting prose in `orchestrator.md`.

## Mutation proof

n/a: policy prose with no detector of its own. The checks it moves are the budgets and known-bad arms of `policy_lint.mjs`: with the new text and nothing deleted, `orchestrator.md` measured 336 lines and 4794 tokens against caps of 319 and 4513 (three `[budgets]` errors). After the deletions it measures 319 and 4507.

## Null control

`node tools/policy/policy_lint.mjs` on the unmodified base tree prints `TOTAL: 0 error(s) across 41 policy file(s)`.

## Figures

- `node tools/policy/policy_lint.mjs --budgets` prints the orchestrator.md row `319 319 4507 4513` and the nudge.md row `115 115 3812 3814` (measured, cap); no cap file changes.
- `node tools/policy/policy_lint.mjs` prints `TOTAL: 0 error(s) across 41 policy file(s)`.

## Red checks

none. No budget leaf rises, so `budget-raise-gate` stays green.

## Forward-carry

Carry: dismissed: each instrument in the measured cases (cloud_dispatch, merge_pr.sh, proof_watch, head_note, body_push, failure_logs, ci-watch, autofix_statuses) is already listed in the instruments guide, so no canonical path is missing.

## Friction

none
