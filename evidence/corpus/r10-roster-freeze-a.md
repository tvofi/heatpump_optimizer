R10-FLOW-ROSTER-FREEZE, arm (a): the relay freeze. Arm (b) merged as #2779 (`c01d54b98`) and is not redone here.

Part of #2389.

Cause: `tools/audit/seat/cloud_relay.sh`'s `handoff_arm` ran `update_pr.sh` for every open pull request whose `handoff/<topic>` was ahead of its head. The only things that stopped it were a missing body ref, ancestry, the orchestrator's hand-written hold file, or a recorded failed update. It never read a verdict or a review in flight. So every `roster_edit.py` push to `handoff/audit-r10-roster` was carried into the open roster pull request while it was under review, and the review came back head-moved (#2559 lost five reviewer rounds that way). Triage P-H (carry 4) found the same gap for a posted merge verdict.

Change (`handoff_arm` and a new `review_freeze`, after the hold check and before the failed-update record):
- **HELD-VERDICT.** If `verdict/<pr>`'s tip subject is `verdict: #<pr> Fix review: merge <head>` and `<head>` is the PR's live head, the arm does not update the PR. The arm lists `refs/heads/verdict/*` once per pass, outside the per-PR loop. It fetches one tip only for a PR whose handoff is ahead. A verdict ref that is listed but cannot be fetched holds the PR as `HELD-UNREAD`, so an unread merge verdict is never moved past.
- **HELD-REVIEW.** If there is no verdict at the live head and a review of that head is in flight, the arm does not update the PR. In flight means a `bus.sh dispatch` record of `<pr> <head>` in `$HPO_BUS_STATE/dispatched`, or a detached worktree of the relay's checkout at `<head>` (`fix-review.md`'s review worktree). A verdict at that head disposes the review, whether merge or blocked. A blocked one lets the held edits land on the next pass. This is "roster edits accumulate on the handoff ref and land between reviews".
- **Not frozen.** A `blocked` verdict at the head, or any verdict naming an older head, freezes nothing. A fixer handoff is exactly what a blocked head needs (P-H's null controls).
- **Report.** Each hold prints `cloud_relay: HELD-<why> #<pr> <handoff tip> (head <head> under review; merge it, or list #<pr> in <release file> and re-dispatch)` once per pass. It is also `OWED <utc> handoff-held refs/heads/handoff/<topic> <tip> #<pr> <why>` in `<log>.level`, rewritten every pass. The tick therefore shows it as a decision for main, not a failure. `ledger.py` registers `handoff-held` as a derived kind.
- **Release (P-H's open risk).** `<state>/cloud-handoff-release` uses the hold file's grammar, parsed by the same `hold_list`, and only the orchestrator writes it. It releases a listed PR from the freeze, for genuine new work that voids a merge verdict. Re-dispatch with `bus.sh dispatch` after the update. It never releases a PR from the hold file, which outranks it. A malformed release file refuses the whole arm, like a malformed hold file: rc 2, and `OWED handoff-hold-malformed <release file> -`.
- The freeze covers every head, not only the roster PR. A predicate keyed on the roster PR's branch name would need a roster-PR detector, a second seam to keep right. `fixer.md` step 6 already freezes a fix head after the handoff, so holding a fixer re-handoff during a dispatched review is that rule made mechanical. Carry 1 says the beat's handoff job generalises the same way.
- `INSTRUMENTS.md` (the relay's handoff-arm entry) and the relay's header describe the freeze. `dev/audit/harnesses/r10_seat_selftests_mutants.py` gains `cloud_relay-22`..`cloud_relay-28` inside the relay's block.

Alternatives considered: (1) Hold on an APPROVED review. P-H rejected it: it costs a per-PR `gh` read every pass over up to 100 PRs, and approval is conditioned on a merge verdict at the head anyway. (2) Hold on `review/<pr>`. That ref is the reviewer's proposal, not the posted verdict, so a proposal that main never confirms would freeze the head forever. (3) Have the orchestrator list the roster PR in the hold file by hand. That is the status quo, and it fails whenever nobody lists the PR before the beat (P-H).

## Head

`07cbe6fe18260380148c9ed7b7cce91d02f6bde9`: one commit on `origin/main` at `8a11b8bdd6bfdca0b5f6bd356638fad2b234525f`, measured 2026-10-25T05:40Z.

## Mutation proof

Failing test first: the 30 new self-test rows were run against the tree with the freeze's `if` disabled (`if false && ! grep -qxF "$pr" <<< "$released" && why=$(review_freeze ...`): `cloud_relay self-test: 268 checks, 13 failed`, among them `FAIL a merge verdict at the head holds the handoff ahead: no update_pr call`, `FAIL a dispatch at the head with no verdict holds the handoff: no update_pr call` and `FAIL a detached review worktree at the head holds the handoff`. The 17 others are null controls, so they pass with the freeze gone.

`python3 dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_relay-22 cloud_relay-23 cloud_relay-24 cloud_relay-25 cloud_relay-26 cloud_relay-27 cloud_relay-28` (each mutant is a one-occurrence replacement in `cloud_relay.sh`, then the governance step that runs `cloud_relay.sh --self-test`):
- `cloud_relay-22` drops the freeze: KILLED, 13 failed.
- `cloud_relay-23` drops the verdict match: KILLED, 8 failed.
- `cloud_relay-24` stops a blocked verdict at the head from disposing a review: KILLED, 1 failed.
- `cloud_relay-25` drops the head match on the dispatch record: KILLED, 1 failed.
- `cloud_relay-26` drops the head match on the worktree: KILLED, 1 failed.
- `cloud_relay-27` drops the release: KILLED, 1 failed.
- `cloud_relay-28` drops the level line: KILLED, 2 failed.
- `RESULT survivors=0`.

`ledger.py` with `"handoff-held": "derived"` removed: `FAIL every kind cloud_relay.sh writes is a ledger kind (census of level_line and ledger_open)`, `56 checks, 1 failed`.

## Null control

All of these are rows in the relay self-test (`bash tools/audit/seat/cloud_relay.sh --self-test`), run against the same fixture PR #41 whose handoff is ahead:
- A merge verdict naming an older head still updates.
- A blocked verdict at the head still updates.
- A merge verdict whose head is not exactly the live head (`<head>x`) still updates.
- No verdict ref and no review: updates.
- A dispatch at an older head holds nothing, and neither does a dispatch of another PR at the same head.
- A detached worktree at another commit holds nothing.
- A released `#141` does not release `#41` (whole-line match).
- A pass that holds nothing drops `handoff-held` from the level.
- The relay's 238 rows from before this change still pass, the hold file's nine malformed variants and `a well-formed hold file owes no refusal (null control)` among them.

## Figures

- `bash tools/audit/seat/cloud_relay.sh --self-test`: `cloud_relay self-test: 268 checks, 0 failed` at head, against `238 checks, 0 failed` at `origin/main` `8a11b8bdd`. The 30 new rows are the freeze controls above.
- `python3 tools/audit/seat/ledger.py --self-test`: `ledger self-test: 56 checks, 0 failed`.
- `python3 tools/audit/seat/r10_ledger_mutants.py --self-test`: `88 checks, 0 failed`. Every anchor still occurs exactly once; its `R3_update_level_unset` line is kept whole, with the new `level_set handoff-held` on a line of its own.
- `python3 -I dev/audit/harnesses/r10_ledger_class_reach.py`: `level_writers=12 level_unkinded=0 ... events_uncleared=0` at head, against `level_writers=10 level_unkinded=0` on `origin/main`'s `cloud_relay.sh`. The two new writers are the two `handoff-held` and release-malformed `level_line`s, both kinded.
- `python3 -I dev/audit/harnesses/r10_relay_owed_class_reach.py`: `events_uncleared=10` at head, against `8` on `origin/main`'s relay. This round harness counts every `level_line` writer as an event a POSTED should clear, as it already does for `handoff-update`. The +2 are the two new level writers, which no POSTED closes by design (a level).
- `python3 -I tests/throwaway_git.py --check`: `0 raw git init or clone site(s) refused, 0 stale allow entries at HEAD`. The new rows' scratch repositories come from `throwaway_git_init` (carry 2b).
- `python3 -I tools/audit/seat/ref_privacy.py --self-test`: `92 checks, 0 failed`. The diff adds no push site (`git diff origin/main -- tools/audit/seat/cloud_relay.sh | grep '^+.*push'` prints nothing), so `PUSHERS` is unchanged (carry 2c).
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: SCOPED -- 0 script(s) run, 33 scoped out`. `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2440 ENTITY CHECKS PASSED`. With this container's `BASH_ENV` (a toolchain profile that resolves `python` to the venv ahead of the checks' stub) left set, prepr's closure record of `tests/entities.py` exits 1. This is the same container effect #2779's body recorded at `origin/main`, so prepr was run with `BASH_ENV` unset.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `CI PREDICT: no closures, fast, wave-script or instrument red predicted against 8a11b8bdd6bf`.
- Class seams. The rule is `grep -n 'upd=(bash "$HERE/update_pr.sh")\|update_pr.sh' tools/audit/seat/*.sh tools/pr/*.sh`, the callers that move a PR head from a handoff.
  - `cloud_relay.sh` `handoff_arm`: closed in this diff.
  - `bus.sh` `orphans`: names `update` as a repair and never runs it.
  - The orchestrator's hand-run `update_pr.sh`: outside any loop, and the orchestrator is the one seat `fixer.md` step 6 lets move a frozen head.
  - The beat's handoff job: not in the tree yet. Carry 1 assigns it the same predicate.

## Red checks

- `nightly-status`: red on main's ancestry at `c01d54b98` (Nightly run 156) and green at `8a11b8bdd` (run 158). It is not this PR's: the diff touches no file the nightly reads beyond the instrument self-tests, which pass here. No cheaper detector is owed by this PR.
- `tests / ci-ratchet`: red on main's push CI (`cc9d584ac`, the repo-wide artifacts listing answering 0 bytes), with a hotfix in flight. It is not this PR's, and `tests/ci_ratchet.py` is untouched.

## Carries

The six carries this group's brief holds, each discharged or answered:
- Carry 0 (pre-study K13): the Lean flow pre-study is not in the tree (`grep -rn K13 dev docs tools` finds no section). This PR builds the brief's own statement of K13: the roster PR as a frozen head.
- Carry 1 (seam with R10-ORCH-MACHINERY): `design/R10-ORCH-MACHINERY` at `2fc665c61` is a step-2 stop that defines no `workers.json` shape. So the freeze uses the else-branch the carry names: the review-worktree heuristic, plus the dispatch record. Both reads sit in `review_freeze` alone, which a `workers.json` read replaces when the design lands. The beat's handoff job inherits the predicate for every head.
- Carry 2 (self-test hygiene):
  - (a) The mutants take per-file ids `cloud_relay-22..28` and sit inside the relay's block, after `cloud_relay-21`.
  - (b) The rows build repositories only through `throwaway_git_init`, and `--check` is clean.
  - (c) No new push site.
  - (d) `## Red checks` above.
- Carry 3 (hold-file grammar): kept. The release file reuses `hold_list`: plain PR-number lines, the same refusal (rc 2, `OWED <utc> handoff-hold-malformed <file> -`). The nine malformed variants and the well-formed null control still pass. `held <pr>` still reads only the hold file.
- Carry 4 (triage P-H): discharged above.
  - The hold is on a git-read merge verdict at the head, from one `ls-remote` of `verdict/*` per pass outside the loop.
  - It prints `HELD-VERDICT #<pr> <handoff tip>` plus a level line.
  - Its four null controls are the self-test rows above.
  - The release is the release file, and the report line names re-dispatch.
  - `R10-UPDATE-PR-SIGNALS` as an after-edge is the orchestrator's roster op (Forward-carry below).
- Carry 5 (card 1, retiring the standing roster seat): not retired by this PR, and correctly so under the owner's binding constraint that the seat stays until its replacement job is live and verified. The runner exists already (`tools/audit/seat/roster_queue.py run`). The job that hosts it is the beat (`beatd.py`), which is `R10-ORCH-BEATD` (not-started), so BEATD merges later than this group. By the card's own rule, BEATD's contract edit is where `standing-roster.md` changes. Its acceptance (a seeded no-op-safe op on a scratch roster branch, a seeded lint failure refused, one cycle beside the seat) runs on the orchestrator's host. The roster op this needs is in Forward-carry below.

## Forward-carry

- R10-FLOW-ROSTER-FREEZE: P-H asks for `R10-UPDATE-PR-SIGNALS` (in-progress, also edits `cloud_relay.sh`) as an after-edge if not already there. Check at origin/handoff/audit-r10-roster `041d307c4`: ROSTER-FREEZE's `after` is `R10-ROSTER-OPS, R10-FLOW-RELAY-HOLD`, so the edge is still owed, as `set-after R10-FLOW-ROSTER-FREEZE R10-ROSTER-OPS,R10-FLOW-RELAY-HOLD,R10-UPDATE-PR-SIGNALS`. Carry: R10-FLOW-ROSTER-FREEZE
- ROSTER-APPEND R10-ORCH-BEATD
  From R10-FLOW-ROSTER-FREEZE arm (a) (carry 5, tvofi 2026-10-24 card 1): this group merges after ROSTER-FREEZE, so its contract edit owns the standing roster seat's retirement in dev/governance/roles/standing-roster.md. A beat job runs tools/audit/seat/roster_queue.py run over the orchestrator's roster queue file (roster_edit.py ops with --lint-cwd at a fresh origin/main and --push), writing one 'roster: <op> <group> pushed <sha>' or 'refused <reason>' line per op into the digest; a refusal is never retried past the lint gate. Binding (owner, verbatim): 'make sure the retirement of the standing seats dont cause you to run things inline'. The seat stays until the job lands a seeded no-op-safe op on a scratch roster branch and refuses a seeded lint failure, with the seat running beside it for one cycle. Carry: R10-ORCH-BEATD

## Friction

none
