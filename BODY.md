R11-PRE-TOKEN-LEDGER (owner ruling 2026-11-13, card P4; decision 0018 section 2 `tokens_per_change`, section 6 "Cannot read"). `tools/audit/seat/token_ledger.py` sums Claude transcript usage per (session, agent, UTC day), the four usage fields kept apart and `tokens` their sum, keyed by the `Seat key: group= role= dimension= model= seat=` line that `cloud_dispatch.render` now ends every prompt's first line with. The beat's `scorecard` row runs `collect` daily into `<state>/scorecard/tokens.tsv` in the shape `round_metrics.token_line` reads (columns `t`, `seat_class`, `tokens`, unchanged reader). `sessions()` is the importable per-session iterator yielding each session's own transcript and its `subagents/agent-*.jsonl` files (carry 6's precondition for part C). `check_scopes.py --round` refuses an evaluator or reviewer named as a `seat` of a ledger row in the graded round's window (`ledger_gaps`, wired by `round_ledger_gaps`), and prints `LEDGER unread` with no ledger or no window. A flag-path fixer re-dispatch keeps its ref's part line (`cloud_dispatch.inherit_part`, carry 4).

Brief carries, each built here:

- Carry 0 (fc61d366): `token_ledger.COLUMNS` keeps `input_tokens`, `output_tokens`, `cache_creation_input_tokens` and `cache_read_input_tokens` apart, and a seat is keyed by `group`, `role`, `dimension` (plus `model` and `seat`) from its `Seat key:` line.
- Carry 1 (69822206) and Carry 2: `tokens_per_change` reads this ledger through `round_metrics.token_line`, unread (never a partial) while the cloud class has no row; `check_scopes.py --round` refuses an evaluator or reviewer seat in the graded round's ledger, with its self-test arms (`ledger_gaps`' B1 arms and `ledger_round_self_test`).
- Carry 3 (ecf8207d): the ledger writes `<state>/scorecard/tokens.tsv` with tab-separated `t`, `seat_class` (`orchestrator`, `local`, `cloud`) and `tokens` first; `round_metrics.py` is unchanged, and the token ledger's self-test drives `token_line` on what `collect` writes.
- Carry 4 (d29d6a0f): `cloud_dispatch.inherit_part` keeps a split part's generated part line on a flag-path fixer re-dispatch of its ref.
- Carry 5 (ee874351): the ledger reads Claude project transcripts, not the gh shim's host log, so nothing here reads that log (`## Friction`).
- Carry 6 (221c4254): `token_ledger.sessions()` is the importable per-session iterator yielding each session's own transcript and its subagent transcript files, the precondition for part C; part C and its [paths] stay the orchestrator's dispatch.

Cloud half, measured: a cloud seat's transcript is readable per session, but only inside its own container, at `~/.claude/projects/<cwd slug>/$CLAUDE_CODE_SESSION_ID.jsonl`; no tracked path carries it to the host the beat runs on. So the cloud class has no ledger row and `token_line` prints unread, never a partial (0018 section 2). `collect --seat-class cloud` labels a cloud seat's own rows, for whatever channel later carries them.

## Head

8bafe16f10165288b0f203b5654efa94487270ea, merge base e3cb5c019b464a770cc7c6fe2fbc858ed29debf7 (origin/main 7f7e05118f at 2026-11-25T13:02Z).

## Mutation proof

Each production line deleted or neutered at the head, the named self-test run, then restored:

- `token_ledger.read_transcript`'s once-per-response guard (`if ident in seen ...` to `if False:`): `python3 -I tools/audit/seat/token_ledger.py --self-test` fails `a response written once per content block counts once (m1 twice is 1111, not 2222)`, `every usage field is kept apart and tokens is their sum`, `one cloud row makes it read, summing tokens`.
- `round_metrics.token_line`'s `if missing or not prod:` to `if not prod:` (the reader this ledger feeds): the same self-test fails `round_metrics reads the ledger and prints unread while the cloud class has no row`.
- `cloud_dispatch.render`'s key insertion (`text = f"{first} {key}\n{rest}"` to `pass`): `python3 -I tools/audit/seat/cloud_dispatch.py --self-test` fails `every role's prompt ends its first line with its seat key` and `a group seat's prompt keys it, on its first line, by group, role, model and dispatch name`.
- `cloud_dispatch.main`'s `known["brief"] = inherit_part(...)` to `pass`: the same self-test fails `a flag-path repair of part 2 on its own ref keeps the part's line`.
- `check_scopes.main`'s `gaps += round_ledger_gaps(a, show, tree)` to `pass`: `python3 -I tools/audit/check_scopes.py --repo . --self-test` fails `--round reads its token ledger: an absent one prints unread`. At f614bb7364 the same deletion left the self-test passing.
- `check_scopes.ledger_gaps`' window `a <= at(t) < b` to `a < at(t) < b`, and in `round_ledger_gaps` the record guard off, the window read at `a.round - 2`, or the window `(win[1], win[1])`: the same self-test fails `--round: the evaluator a seat at the graded window's first second is refused` (the arms of `ledger_round_self_test`, over a scratch repo tagged v9.0.0 and v10.0.0); the B1 null arms pass their window upper bound first, so a moved bound takes the row in and fails them. At 7b39f19bae these survived: on the live tree no v9.0.0 tag opens round 10, so the run-whole arm read the unread branch only.
- `beat_jobs.scorecard`'s ledger rc read is the in-tree mutant `scorecard_tokens_rc_dropped`, run by `python3 -I tools/audit/seat/beat_jobs.py --self-test`.

## Null control

At the merge base no `tokens.tsv` writer exists: `round_metrics.token_line` returns `tokens unread (no token ledger tokens.tsv; R11-PRE-TOKEN-LEDGER builds it)`. In the head's self-test the ledger with no cloud row prints `seat classes with no ledger row: cloud;`, and one appended cloud row turns it into `tokens 4449 per production merge` (the unread arm's control). `ledger_gaps`' null arm: the same seat outside the window, another seat, or a `-` seat is no gap.

## Figures

- token ledger self-test: `python3 -I tools/audit/seat/token_ledger.py --self-test` (every check ok, 0 failed).
- cloud_dispatch self-test: `python3 -I tools/audit/seat/cloud_dispatch.py --self-test` (0 failed).
- beat_jobs self-test: `python3 -I tools/audit/seat/beat_jobs.py --self-test` (0 failed).
- check_scopes self-test: `python3 -I tools/audit/check_scopes.py --repo . --self-test` (`SELF-TEST passed`).
- cloud transcript readable in-container: `python3 -I tools/audit/seat/token_ledger.py collect --projects ~/.claude/projects/-home-user-heatpump-optimizer --out <scratch>/tokens.tsv --seat-class cloud`, run inside this cloud seat, wrote one cloud row for this session's own id with each usage field apart; the host beat has no such directory for a cloud seat.
- structure ratchet: `python3 tests/structure.py` (`STRUCTURE RATCHET PASSED`).

- diff mutants: `MUTANT_IN_PLACE=1 PREPR_SKIP_CLOSURES=1 MUTANT_CMD="sh -c 'python3 -I tools/audit/check_scopes.py --repo . --self-test && python3 -I tools/audit/seat/beat_jobs.py --self-test'" bash tools/pr/prepr.sh <body>` drew the first 40 mutants of the diff's added `.py` lines (31 in check_scopes.py, 9 in beat_jobs.py); its one SURVIVED line is under `## Unpinned sites`.

## Unpinned sites

- `tools/audit/check_scopes.py`, the run-whole arm's own assignment (`cov["--round reads its token ledger: an absent one prints unread"] = ...`), STMT_DEL: deleting a self-test's arm removes the check, which no arm observes; the behaviour that arm pins, `main()`'s `gaps += round_ledger_gaps(a, show, tree)`, is killed by it (`## Mutation proof`).

## Red checks

none

## Forward-carry

none

## Friction

- check_scopes-round-window: stale: `check_scopes.py --round 11` prints `LEDGER unread: no tag v9.0.0 opens round 10`, because `round_metrics.round_window` opens round n at tag v(n-1).0.0 and no v9.0.0 tag exists; from round 12 the window (v10.0.0 to v11.0.0) resolves and the refusal reads. Carry: dismissed: a one-round bootstrap of the scorecard's own window convention, printed unread rather than a guessed window.
- brief-carry-5: unclear: the ledger reads Claude project transcripts, not the gh shim's host log that r10-gh-read-residue-p3 moved, so carry 5 changes nothing here. Carry: dismissed: no reader of that log in this group.
