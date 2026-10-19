Round 10 hand-rolled variants of canonical instruments: a tick driver in session scratch instead of `tick_loop.sh` under `daemonize.py`; a private cloud relay and a cloud-reviewer payload helper instead of `cloud_relay.sh` and `cloud_dispatch.py`; a typed sweep prompt instead of `sweep_render.py`; shell merge-poll loops instead of `merge_pr.sh --mandate`, `proof_watch.py` or `merge_train.py`; python/gh body edits with no read-back instead of `head_note.py`/`push.sh`/`body_push.sh` (one blanked two PR bodies); ad-hoc job-log greps instead of `failure_logs.sh`; hand `gh run rerun` instead of `ci-watch.sh`/`autofix_statuses.sh`; and the canonical relay run over un-ledgered state replayed 80 stale probe refs. Root cause: the orchestrator contract never sent the reader to the instruments guide, and nothing required re-checking briefs when an instrument landed. This adds one paragraph and four bullets to `orchestrator.md` section 13 (look up first; a new helper needs a reason and lives in `tools/`; render the sweep; re-check briefs on a merge; seed a stateful instrument's ledger first) and one pointer sentence in `nudge.md` step 18. It names the guide and the template without their file names so `named-docs` does not pull those usage guides into the corpus. No `.cursor` rule changed; `rules_sync.mjs` wrote 0 files.

## Head

c3405516046ef301e9fc85bcc4b243f5709102a7

## Approval

This changes policy (`orchestrator.md`, `nudge.md`) and raises three per-file caps in `policy_budgets.json`. Authority is tvofi's round-10 mandate on #201, comment 6175172275 (https://github.com/tvofi/heatpump_optimizer/issues/201#issuecomment-6175172275), scope all, valid to 2026-10-28, quoted verbatim:

> MANDATE: agents may approve as tvofi, scope all, from 2026-10-14T18:14Z until 2026-10-28T18:14Z

Context only, not the approval: tvofi in chat on 2026-10-19 directed this edit: "Yes, update orchestrator.md and any other policy documents where the existence of canonical instruments in instruments.md needs to be reinforced. Budget raises ok."

Raises, each to the measured value `policy_lint.mjs --budgets` printed (the band is untouched; `corpus_tokens` measures ~61449 against 61026 + 500 band, so it is not raised): `orchestrator.md` lines 319 to 336 and tokens 4513 to 4794; `nudge.md` tokens 3814 to 3827. Payments considered: cutting spent prose from `orchestrator.md` sections 1 to 14, none of which is spent or duplicated after the uniqueness test; shortening the new text further drops the reason clause, which is what makes a seat check the guide.

## Mutation proof

n/a: policy prose with no detector of its own. The only check it moves is the budgets arm of `policy_lint.mjs`: with the text added and the caps left at their old values it printed three `[budgets]` errors (orchestrator lines and tokens, nudge tokens); with the caps re-recorded it prints `TOTAL: 0 error(s)`.

## Null control

`node tools/policy/policy_lint.mjs` on the unmodified base tree prints `TOTAL: 0 error(s) across 41 policy file(s)`.

## Figures

- `node tools/policy/policy_lint.mjs --budgets` prints the orchestrator.md row `336 319 4794 4513` and the nudge.md row `115 115 3827 3814` (measured, cap), and `corpus: ~61449 tokens, cap 61026 +band 500 = 61526`.
- `python3 tools/audit/archscore/score.py --diff origin/main` prints `Architecture score: dS +0.0000 NULL`.

## Raise justification

Payments tried: cutting prose from `orchestrator.md` sections 1 to 14 (none is spent or duplicated under the uniqueness test); moving the new rule into the instruments guide or the sweep template (both are outside the corpus, so that is the move `ratchet-budgets` calls a reclassification and refuses); shortening the new text (it drops the reason clause that makes a seat consult the guide). The change adds no code, so no refactor applies.
Architecture score: dS +0.0000 NULL

## Red checks

`budget-raise-gate` is red until the owner's decisive review lands on this exact head: three caps rise (`orchestrator.md` lines 319 to 336, tokens 4513 to 4794; `nudge.md` tokens 3814 to 3827). Cheaper detector: none; this gate is the detector for a raise, and its standing cost is one mandated review per raise. Answer: the review is given under mandate 6175172275 (scope all, the `## Approval` quote above) and the `## Raise justification` section above is the shape the gate parses for a mandated approval.

## Forward-carry

none. Each instrument in the measured cases (cloud_dispatch, merge_pr.sh, proof_watch, head_note, body_push, failure_logs, ci-watch, autofix_statuses) is already listed in the instruments guide, so no canonical path is missing.

## Friction

none
