R11-PRE-TOKEN-LEDGER (owner ruling 2026-11-13, card P4; decision 0018 section 2 `tokens_per_change`, section 6 "Cannot read"). `tools/audit/seat/token_ledger.py` sums Claude transcript usage per (session, agent, UTC day). It keeps the four usage fields apart, with `tokens` their sum. A seat is keyed by the `Seat key: group= role= dimension= model= seat=` line that `cloud_dispatch.render` ends the first line of every cloud event with, the `publish_seat` stub included, so a cloud seat's first user message carries it. The beat's `scorecard` row runs `collect` daily into `<state>/scorecard/tokens.tsv`, in the shape `round_metrics.token_line` reads (columns `t`, `seat_class`, `tokens`; the reader is unchanged). `sessions()` is the importable per-session iterator. It yields each session's own transcript and its `subagents/agent-*.jsonl` files, which is carry 6's precondition for part C. `check_scopes.py --round` refuses an evaluator or reviewer named as the `seat` of a ledger row in the graded round's window (`ledger_gaps`, wired by `round_ledger_gaps`). It prints `LEDGER unread` in four cases (`ledger_unread`): there is no ledger; there is no window; a seat class (`round_metrics.SEAT_CLASSES`) has no row inside the window `[a, b)`; or a non-orchestrator row in that window has no seat key. A keyed seat it does find is still refused. A flag-path fixer re-dispatch keeps its ref's part line (`cloud_dispatch.inherit_part`, carry 4).

## Re-cut

This is a fresh branch from origin/main dbdc520e86. It carries #3898's code diff (`git diff d9100de781 dbaca057`, without the delivery row) and adds the two arms that pin the upper bound of `ledger_unread`'s window. The arms added in this pass:

- `--round: a seat class whose only row falls at the window's end prints unread`. The cloud row is dated 2026-01-03T00:00:00Z, the tag v10.0.0, which is the window's `b`.
- `--round null: an unkeyed seat row at the window's end is no unread`. A `-` row at `b` is not counted toward the window's unkeyed total.

Brief carries, each built here:

- Carry 0: `token_ledger.COLUMNS` keeps `input_tokens`, `output_tokens`, `cache_creation_input_tokens` and `cache_read_input_tokens` apart. A seat is keyed by `group`, `role` and `dimension`, plus `model` and `seat`, from its `Seat key:` line.
- Carries 1 and 2: `tokens_per_change` reads this ledger through `round_metrics.token_line`, which prints unread (never a partial) while the cloud class has no row. `check_scopes.py --round` refuses an evaluator or reviewer seat in the graded round's ledger.
- Carry 3: the ledger writes `<state>/scorecard/tokens.tsv` with the tab-separated columns `t`, `seat_class` (`orchestrator`, `local`, `cloud`) and `tokens` first. `round_metrics.py` is unchanged.
- Carry 4: `cloud_dispatch.inherit_part` keeps a split part's generated part line on a flag-path fixer re-dispatch of its ref.
- Carry 5: the ledger reads Claude project transcripts, not the gh shim's host log (see `## Friction`).
- Carry 6: `token_ledger.sessions()` is the per-session iterator, the precondition for part C. Part C and its paths stay the orchestrator's to dispatch.

Paths that write the seat key, by rule and residue:

- Rule: every cloud seat is fired with a `cloud_dispatch.render` event. `dispatch_group` and `main --publish` go through `publish_seat`, and the flag path calls `render` directly. `render` ends that event's first line with the key, whether the event is the stub or the whole prompt.
- Enumeration: `git grep -nE 'CLOUD (REVIEWER|FIXER|PROBE|DESIGNER)|environment_id|job_config|RemoteTrigger|PAYLOAD.json' -- tools .claude` finds no event or payload builder outside `cloud_dispatch.py`. The other hits are readers, self-test fixtures or docs.
- Residue, by category: a local seat spawned by a host session's Agent tool. The spawning session writes its first message, and no rule keys it. Its row is `seat=-`, and `check_scopes.py --round` prints its refusal unread while the graded window holds such a row.

Cloud half: a cloud seat's transcript is readable only inside its own container, at `~/.claude/projects/<cwd slug>/$CLAUDE_CODE_SESSION_ID.jsonl`. No tracked path carries it to the host the beat runs on. Until one does, the cloud class has no ledger row and `token_line` prints unread. `collect --seat-class cloud` labels a cloud seat's own rows, for whatever channel later carries them.

## Head

92e79681f6f7b4430db6914db0b35db48e953a79, merge base dbdc520e86 (origin/main at the cut).

## Mutation proof

Each mutant was applied at the head, the named self-test run, and the file restored.

The first set targets `ledger_unread`'s window, `win = [r for r in rows if r.get("t") and a <= at(r["t"]) < b]`. Each was checked against `ledger_round_self_test`'s arms, and the upper-bound mutant also through the whole `python3 -I tools/audit/check_scopes.py --repo . --self-test`:

- Upper bound dropped (`a <= at(r["t"])`), the reviewer's surviving mutant D5b. Before the new arms, all 9 ledger arms held under it. At this head it fails `--round: a seat class whose only row falls at the window's end prints unread` and `--round null: an unkeyed seat row at the window's end is no unread`.
- Upper bound widened to `<= b`: fails the same two arms.
- Lower bound dropped (`at(r["t"]) < b`): fails `--round: a seat class whose only row predates the window prints unread`.
- Whole filter dropped (`win = [r for r in rows if r.get("t")]`): fails all three.

The second set comes from #3898 and was re-run at this head:

- `token_ledger.read_transcript`, `if first and o.get("type") == "user":` changed to `if o.get("type") == "user":`. `python3 -I tools/audit/seat/token_ledger.py --self-test` exits 1, failing `a keyed transcript stays keyed by its first user message through later user lines (a tool_result, another key): one local fixer row`.
- `d["t"] = max(d["t"], stamp)` changed to `d["t"] = stamp`. The same self-test exits 1, failing ``a day's `t` is its latest stamp, not its last-written one``.
- The once-per-response guard, `if ident in seen and ident != (None, None):` changed to `if False:`. The same self-test exits 1, failing `a response written once per content block counts once (m1 twice is 1111, not 2222)`, ``every usage field is kept apart and `tokens` is their sum`` and ``one cloud row makes it read, summing `tokens` (null control for the unread arm)``.
- `cloud_dispatch.render`'s key insertion, `text = f"{first} {key}\n{rest}"`, replaced by `pass`. `python3 -I tools/audit/seat/cloud_dispatch.py --self-test` exits 1, failing `every role's prompt ends its first line with its seat key: the role, the model, the dispatch name` and `a published fixer's stub ends its first line with the seat key its whole prompt carries`. It also fails the reviewer's stub arm and the group seat's arm.
- `cloud_dispatch.main`'s `known["brief"] = inherit_part(_prev_prompt(".", ref), brief)` replaced by `pass`. The same self-test exits 1, failing `a flag-path repair of part 2 on its own ref keeps the part's line, after its hand brief`.

## Null control

On the unmutated head, `ledger_round_self_test`'s 11 arms all hold, and the check_scopes self-test prints `SELF-TEST passed`. The new null arm puts an unkeyed row at `b` beside a keyed fixer row inside the window; it returns no gap and prints nothing. Its sibling `--round null: every class keyed in the window, an orchestrator's - included, prints no unread` still holds. At the merge base no `tokens.tsv` writer exists, and `round_metrics.token_line` returns `tokens unread (no token ledger tokens.tsv; R11-PRE-TOKEN-LEDGER builds it)`.

## Figures

- check_scopes self-test: `python3 -I tools/audit/check_scopes.py --repo . --self-test` prints `SELF-TEST passed`.
- token ledger self-test: `python3 -I tools/audit/seat/token_ledger.py --self-test` reports 0 failed.
- cloud_dispatch self-test: `python3 -I tools/audit/seat/cloud_dispatch.py --self-test` reports 0 failed.
- beat_jobs self-test: `python3 -I tools/audit/seat/beat_jobs.py --self-test` reports 0 failed.
- structure ratchet: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Unpinned sites

- `tools/audit/check_scopes.py`: a STMT_DEL of a self-test arm's own assignment (`cov[...] = ...` or `arms[...] = ...`). Deleting an arm removes the check itself, which no arm observes. The behaviour each arm pins is killed by it, as listed under `## Mutation proof`.

## Red checks

none

## Forward-carry

none

## Friction

- check_scopes-round-window: stale: `check_scopes.py --round 11` prints `LEDGER unread: no tag v9.0.0 opens round 10`. `round_metrics.round_window` opens round n at tag v(n-1).0.0, and no v9.0.0 tag exists. From round 12 the window (v10.0.0 to v11.0.0) resolves and the refusal reads. Carry: dismissed: a one-round bootstrap of the scorecard's own window convention, printed unread rather than a guessed window.
- seat-brief-handoff-push: contradiction: the seat brief named `tools/audit/seat/handoff_push.sh` for the code push and also said never to push the PR head or open a PR. `handoff_push.sh` opens or updates the PR as `hpo-author`. So the code head went to `handoff/r11-pre-token-ledger-pr` by a plain `git push`, and the PR step stays the orchestrator's. Carry: dismissed: the brief's wording; the instrument works as its page states.
- seat-brief-prepr-path: stale: the brief named `tools/audit/seat/prepr.sh`, which does not exist. The prepr run used `tools/pr/prepr.sh`. Carry: dismissed: the brief's wording.
