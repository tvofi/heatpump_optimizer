Triage batch 60 rules the orchestrator's 2026-10-29T10:24Z roster-push proposal as P278, and its two 11:08Z tick proposals as P279 (train PARKs) and P280 (cloud-seat liveness), its 11:15Z tick-wiring proposal as P281, its 11:46Z review-packet proposal as P282, its 12:00Z STALE CHECKOUT proposal as P283, and V187 (REST quota attribution) as P284. It is the next rolling batch under V182, after batch 59 (#2945, merged as `66974d473`).
- **P278 (retry a roster push refused as non-fast-forward): ACCEPT, narrowed, to R10-ORCH-ROSTER-SCHEMA; the retry is REJECTED.**
  - The two refusals (09:15Z and 09:26Z, `append-group R10-FLY-OWED-LEVELS`) were rc 3. That is `roster_edit.py`'s lint-gate refusal (`:657-660`), which returns before any push. A lost race takes its own path (`:682`), retries up to `PUSH_ATTEMPTS = 3` (`:137`), and refuses with rc 2. `roster_queue.py` retries again on a stale lint checkout or a race (`:122`, `:137`).
  - Reproduced without `--push` and with no rival: brief_lint gives `TOTAL: 2 error(s)`, both in the group's own brief. One sentence cited `orchestrator_tick.py:690` and `owed_unactioned.py:50`, and the linter's clause window (`brief_lint.mjs` `clauseWindow`, `:391`) searched each file for the other's name. A retry would have refused every time.
  - The cause was invisible because the roster loop keeps only the last line matching `pushed|REFUSED|error`, which is "... nothing pushed". Both re-queue notes recorded a race.
  - Carried: the lint-gate refusal's last line names cause, count and outcome together. rc stays 3. The carry adds a self-test arm, a mutant of the old two-line form and a clean-fixture null control.
  - The authoring defect is this seat's (P277's brief, batch 59). The group JSON is corrected out of tree, and the same dry run now gives `TOTAL: 0 error(s)` with nothing pushed. This seat now dry-runs every group and carry op it queues.
  - One held roster op (`append-carry R10-ORCH-ROSTER-SCHEMA`), released once this file is on main.

- **P279 (the tick should owe a PR the merge train PARKed): ACCEPT, in two parts.**
  - Item 1 amends P265's owed-PR buckets on R10-ORCH-LEDGER. A PR the latest train run PARKed is bucket `owed`, reason `train-parked <step>: <why>`, keyed (train-parked, PR, head) in the ledger. Without this, P265 would bucket it `train`, because it is still queued at its verdicted head.
  - Item 2 is new fly-in R10-FLY-TICK-TRAIN-RC. The tick reads the train's exit status from `<log>.rc` (`orchestrator_tick.py:536`), but `train.sh` writes `$state/rc` and a `TRAIN_RC=` log line (`:396`). 16 of the 23 runs in the live log ended `TRAIN_RC=1`, and none was flagged. The self-test passes because its fixture writes the reader's own name (`:2420`).
  - Measured: 6 PARKs in the live log since 2026-10-27 (4 `findings`, 2 `policy`). At 10:58Z the tick showed #2933 and #2939 as `MERGE-READY` with an unflagged log tail.
  - Not built: a separate `OWED train-parked` line outside the ledger. In the interim R10-FLY-OWED-LEVELS (P277) makes those PRs' `MERGE-READY` lines owed.
  - Two held roster ops (`append-carry R10-ORCH-LEDGER`, `append-group R10-FLY-TICK-TRAIN-RC`), released once this file is on main.
- **P280 (cloud-seat liveness from the session's run log): REJECT.**
  - `get_run_log` is a call of the orchestrator's session. No file in the tree reads a cloud run log (`cloud_dispatch.py` only writes `cloud-sessions.tsv`).
  - The instance, #2872 blocked at an unmoved head, is P277's `BLOCKED-UNFIXED: #2872 <head8>`, owed after two sweeps once R10-FLY-OWED-LEVELS lands.
  - The tick's WORKERS section already judges liveness from the work, but the live tick passes it no workers file.

- **P281 (the live tick's `--queue` is a hand-kept link; `--workers-file` is unwired): ACCEPT, narrowed, folded into R10-FLY-TICK-TRAIN-RC.**
  - The link named an Oct 27 queue for two days, so every pass printed a stale #2867 line. `train.sh` already logs `train.sh: queue=<path> ... pid=<n>` at each start (`:378`, 27 lines in the live log), in the log the tick already reads.
  - With `--train-log` and no `--queue`, the tick reads the path from that log's last start line. An explicit `--queue` still wins.
  - Rejected: a stable link kept by `train.sh`, which would be a second record of the same fact. Also rejected: `--workers-file` wiring, because nothing in `tools/audit/seat/` writes a workers file.
  - No new roster op: the held R10-FLY-TICK-TRAIN-RC group carries it as item 3.

- **P282 (the review packet owes main-graded reds an answer): ACCEPT, reframed, as a new fly-in R10-FLY-PACKET-RED-PATHS.**
  - The exemption already lives in `policy_lint.mjs --pr-body`, and it applies only when it is given the changed paths. With none it restores the obligation on purpose (`:4447`).
  - `review_packet.py:331` calls it with `--pr-body`, `--head` and `--red` only, although `touched` (`:321`) holds the diff's paths. So #2933, #2946, #2948 and #2925 were refused on `tests / nightly-status`.
  - Reproduced: the same body with reds nightly-status and typing reports both without paths, and only typing with a `--paths-file`.
  - The fix passes `--paths-file`, `--existing-file` and `--base` as `prepr.sh` does. Rejected: a second exemption list (`prepr.sh:1239` refuses the copy).
  - One held roster op (`append-group R10-FLY-PACKET-RED-PATHS`), released once this file is on main.

- **P283 (the pushers' STALE CHECKOUT guard refuses from a current worktree): ACCEPT, narrowed, as a new fly-in R10-FLY-RELAY-TOOLS-LEVEL; both options REJECTED.**
  - The guard already judges the running script's own checkout (`pr_args.sh:166-178`, `dirname "${BASH_SOURCE[0]}"`), which is option (a).
  - All 41 recorded refusals (28 in `tick-loop.log`, 13 in `cloud-relay.log`) name the orchestrator worktree, never the main checkout. It was behind origin/main each time, and nothing levels it.
  - The relay runs `bash "$HERE/update_pr.sh"` from its own checkout (`cloud_relay.sh:154`, `:438`). The fix: it runs `update_pr.sh` from a tools checkout it owns and levels to origin/main before each call, as `roster_queue.py` does for its lint clone.
  - (b) is rejected: a guard that fast-forwards its own checkout rewrites the bash scripts executing from it.
  - One held roster op (`append-group R10-FLY-RELAY-TOOLS-LEVEL`), released once this file is on main.

- **P284 (V187, nothing attributes the shared REST quota to its caller): ACCEPT, as a new fly-in R10-FLY-GH-CALL-LOG.**
  - P248 (`s6-batch50.md`) deferred a cache until a consumer is attributed. Today's 15:11Z exhaustion is the second, and its consumer is still unnamed.
  - The local tools reach GitHub through `gh`: 21 Python files and 18 shell scripts. The one direct HTTP call is `urlopen` in `record_row.py` (`:882`). So a `gh` shim beside `seat-python` sees nearly every call.
  - The shim logs time, parent and endpoint, never field values, then execs the real `gh` unchanged. It is installed by `seat_venv.sh --install-shims`, and a `--top` reader ranks callers. Only `merge_train.py` has the shims directory on PATH today, so the fly-in names each daemon that does not.
  - Blind spots: the cloud seats, and `record_row.py`'s one read. The cache stays with R10-ORCH-BEATD.
  - One held roster op (`append-group R10-FLY-GH-CALL-LOG`), released once this file is on main.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`e30cd6e9839fe9729873bf49dd4fe48d6b2caa40`; the file is the whole diff against `66974d47312caa46e9817b9aeae7186e9764e560`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P278, P279 and P281-P284 as `ACCEPT` and P280 as `REJECT`. `triage_refusal` passes the P278 and P279 carry texts and the R10-FLY-TICK-TRAIN-RC brief and resume note, which cite P279 and P281, the R10-FLY-PACKET-RED-PATHS brief and note, the R10-FLY-RELAY-TOOLS-LEVEL brief and note, and the R10-FLY-GH-CALL-LOG brief and note (returns None). A text citing `#P280` is refused as `not an ACCEPT ruling (REJECT)`.
- With P278's `Verdict: ACCEPT` changed to `Verdict: REJECT`, the same carry is refused: `dev/programme/triage/s6-batch60.md#P278 is not an ACCEPT ruling (REJECT)`. The first draft led its verdict line with "REJECT the retry" and would have been refused the same way. It was reordered before commit.

## Null control

- With the file absent, the carry returns `the triage ruling dev/programme/triage/s6-batch60.md is not on the roster branch or origin/main`. That is also what the real dry run of the held op printed before this push.
- For the ruling's measurement: the roster at tip `68406609a`, without the new group, lints `TOTAL: 0 error(s)`. With the original group it gives 2 errors, and with the clause-split group 0. So the errors belong to the brief alone.

## Figures

- Dry run: `roster_edit.py append-group R10-FLY-OWED-LEVELS <json> --roster-ref handoff/audit-r10-roster --lint-cwd <origin/main 66974d473 checkout>` without `--push`, on a scratch worktree that was then removed. Original brief: `LINT GATE REFUSED`, `TOTAL: 2 error(s)`. Corrected brief: `lint gate: TOTAL: 0 error(s)`, `ready: ... (no --push)`.
- The carry text was linted by appending it to a copy of the roster at `68406609a` (group R10-ORCH-ROSTER-SCHEMA): `TOTAL: 0 error(s)`.
- P279: `grep -o 'TRAIN_RC=[0-9]*'` over the live train log gives 7 `TRAIN_RC=0` and 16 `TRAIN_RC=1`. `grep -o 'PARK #[0-9]* [a-z-]*'` gives #2939 findings, #2933 policy and findings, #2881 findings, #2880 policy and #2876 findings. The train state dir holds `rc` and `skipped.json`, and no `train.rc`.
- P279's carry and group were linted on a roster copy. The only error is the group's citation of this not-yet-merged file (`not in the tree`), which clears on merge.
- P282: `node tools/policy/policy_lint.mjs --pr-body <batch-59 body> --head <main> --red 'tests / nightly-status' --red typing` reports both unanswered. With `--paths-file` (one triage path) and an empty `--existing-file` added, it reports only `typing`.
- P283: `grep -c 'STALE CHECKOUT'` gives 28 in `tick-loop.log` and 13 in `cloud-relay.log`. Every one names `.../orch-wt/tools/audit/seat`. `git log --since=2026-10-29T00:00Z` on origin/main gives 23 first-parent commits to `b87019b86`, 9 of which change `tools/audit/seat` or `tools/pr` against their first parent.
- P284: `grep -lE 'urllib.request|http.client|api.github.com'` over `tools/audit/seat/*.py` finds one direct `urlopen` (`record_row.py:882`). `gh_read.py`'s `http.client` use is failure classification (`:132`). Of the live daemons, only `merge_train.py` has the shims directory on its environment's PATH.
- Roster tip: R10-FLY-ABORT-OWN-MERGE and both batch-59 carries landed at 09:15Z (`79542c319`, `539b4b5e2`, `13aa34d67`). R10-FLY-OWED-LEVELS is absent.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
