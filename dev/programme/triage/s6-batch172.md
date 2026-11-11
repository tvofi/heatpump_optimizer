# Proposal triage, session s14, batch 172 (P588, P589)

This batch rules queue lines 267 (the orchestrator's rate-limit intake) and 268 (s14-12), 2026-11-11.

Sources:
- origin/main `a7628041dc`. Every line number below is at that commit.
- A 600 s process sample of `gh` invocations (07:25:05Z-07:35:05Z) with the core `rate_limit` read at both ends.
- The relay and tick-loop logs of the orchestrator's state dir.

## P588: GH-BUCKET-SPENDER-UNLOGGED

Verdict: ACCEPT, as a PART 2 ITEM carry on R10-GH-READ-RESIDUE (stage in-progress, severity
medium). That group owns `tools/audit/seat/gh_calls.py` and `tools/audit/seat/shims`, and holds
P449, the same drain on 2026-11-08. Its PR 3427 is handed off, and its body dismissed P449's
"install reaches every daemon PATH" half as having "no tracked caller". This is the second instance
of that drain. No call cut is accepted on this sample: the named spenders are a minority of the
bucket, and the rest cannot be attributed until the log reaches the loops.

Source: the orchestrator's queue line 267, 2026-11-11 ("GitHub core bucket hit 0 at 07:19Z ...
gh_calls.py --top --since 06:24Z reads '0 calls' ... name the spender, propose the cut"). It is
ruled under the owner's 2026-11-08 no-API-hammering order.

Instances:
- **Why the log is empty.**
  - `seat_venv.sh --install-shims <dir>` installs the shim as `<dir>/gh` (`seat_venv.sh:304-307`).
    `~/.local/state/hpo/bin` holds only `python` and `python3` (installed 2026-10-14) and no `gh`.
    So every caller resolves to `/opt/homebrew/bin/gh`.
  - `$HPO_STATE_DIR/gh-calls.log` does not exist under the orchestrator's state dir.
  - `gh_calls.py --top --since 2026-11-11T06:24:00Z` prints `(none)` under both tables with
    rc 0. Had the shim been reachable, it would have listed callers.
- **Which loops would log, by `ps eww` PATH.** The merge train's `merge_train.py batch` and
  `beatd.py run` have the seat bin dir on PATH. The tick loop (`tick_loop.sh`), `wake.sh` and the
  dispatch seat's `watch2.sh` do not.
- **The spender, sampled.** `ghsample.py` polls `ps` every 50 ms for 600 s from 07:25:05Z and
  attributes each new `gh` pid to its parent chain.
  - The bucket went from 4987 to 4424, so 563 calls in 10 min, about 3380/h.
  - 240 `gh` processes were sampled:
    - `orchestrator_tick.py`: 121, about 21% of the bucket. Of those, 31 are `check-runs` reads
      over 31 distinct shas, 10 are `search/issues` (the search bucket, not core), and 4 are
      `--paginate --slurp` reads of the #201 and #3394 comments. One of those passes
      `since=2026-10-28`, which is 4 pages of #201's 2500 comments.
    - `blind_spots.py`: 42, about 7.5%. This script is the orchestrator's own out-of-tree sweep
      runner, not in the repository. 19 of its calls are `check-runs?check_name=gate` per sha.
    - `merge_train.py` classify and batch: 21, about 3.7%. Everything else is 5 or fewer per
      caller.
  - About 300 of the 563 calls (roughly 50%) have no local `gh` process. They are pagination
    pages, calls the sampler missed, or other holders of the token. Only the log can split these.

Cost:
- **The fix is two small edits:**
  - `gh_calls.py --top` refuses with rc 3 and a line naming the first `gh` on PATH and whether it
    is the shim, when no call is logged since `--since`. Today it prints `(none)`.
  - The tracked `tools/audit/seat/tick_loop.sh` prepends the seat bin dir to the PATH of its
    children (`orchestrator_tick.py`, `cloud_relay.sh`). It prints one flag line each pass in
    which `command -v gh` is not the shim.
- **Benefit.** It names the 50% of the bucket nobody can attribute today. Every cut the owner's
  order asks for depends on that, and the drain has now recurred, so the 20% bar is met.

Binding: two drains (11-08, 11-11) could not be attributed because a dismissed half left the tick
loop off the shim. The instrument printed a clean zero both times.

Rule per instance:
- **Now, an operational step for the orchestrator, no code.**
  - Run `seat_venv.sh --install-shims ~/.local/state/hpo/bin`. The train and beatd log at once,
    since they already carry that dir on PATH.
  - Restart the tick loop with that dir first on PATH. One hour later, `gh_calls.py --top` names
    the remaining spender, and the cut is ruled on that log.
- **The 11-11 instance under the carry.** `gh_calls.py --top --since 2026-11-11T06:24:00Z` would
  have printed `gh_calls: UNATTRIBUTED: no call logged since ...; gh on PATH is
  /opt/homebrew/bin/gh (not the shim)` and rc 3, instead of a clean zero.
- **Self-test.**
  - An empty log with a non-shim `gh` on PATH gives rc 3 and the line.
  - Null control: one logged call gives rc 0 with today's tables.
  - The tick loop's child PATH starts with the seat bin dir.
  - A mutant that drops the prepend fails the PATH check.

## P589: EVIDENCE-CARRY-WORD-NOT-MARKER

Verdict: ACCEPT, re-pointed, as a carry on R10-CARRY-AUDIT-P5 (stage not-started, severity
medium; it owns `tools/audit/carry_audit.py`, and P587 also lands there). Both proposed fixes are
REJECTED:
- **(a), a prompt line.** The reviewer prompt already says that an Evidence item carrying `Carry:`
  is a finding (`cloud_dispatch.py:291-296`). All three instances below happened under that text.
- **(b), ignoring `## Evidence`.** It would undo P308/P314. It would also drop a routed finding
  that a reviewer files under Evidence.

Source: the proposal queue, s14-12, 2026-11-11 (line 268: "push-verdict refused a carry-only merge
verdict because an '## Evidence' bullet began 'Carry: review_carry.py ... prints CARRY' ... PR
3425").

Instances:
- **The 3425 instance.** The verdict ref is `probe/rev-3425-a7ac54c9`, commit `f051f4562d`, and
  `verdict.md:7` reads ``- Carry: `review_carry.py c6becb31 c93903f0` prints CARRY.``
  `tick.txt.relay.log:25` records "bus: REFUSE: push-verdict: 1 finding item(s) with no valid
  Carry: ... UNROUTED review push-verdict item b6e4992b (## Evidence) [carry]".
- **The whole class.** `grep 'UNROUTED review.*(## Evidence)'` over `tick-loop.log` (since
  2026-10-24), `tick.txt.relay.log` and `cloud-relay.log` gives 8 lines. They are 3 distinct
  items, and every one has the reason `[carry]`:
  - item b6e4992b (PR 3425): "Carry: `review_carry.py ...";
  - item 2c51d159: "Contradiction grep (own group, own-group, Carry: across
    dev/governance ...)";
  - item 8e3e097e: "The deleted closing line of fix-review.md ... states it as a Carry: marker".
  In each, `Carry:` is a word the text mentions, not a destination marker. Each refusal sends the
  verdict back for a second reviewer turn.
- **The marker regex.** It is `CARRY = (?<![\w-])Carry:` (`carry_audit.py:169`), and it matches
  any mention. Destination tokens have fixed shapes: `GROUP_TOK` (`carry_audit.py:176`),
  `ISSUE_TOK` (line 177), `O<n>` and `dismissed:`.

Cost:
- About 6 lines in `carry_audit.py`, plus three self-test checks. No new file.
- The group's severity is medium, so the machinery bar does not apply.
- The benefit is 3 of 3 measured Evidence `[carry]` refusals removed, each one reviewer turn.

Binding: a word mentioned in evidence costs a full review turn. In every section, a destination
shape separates a marker from a mention without reading meaning.

Rule per instance:
- **The rule.** In a structural section (`## Evidence`, and a merge verdict's sections other than
  findings), a `Carry:` counts as a marker only when its next token matches a destination shape:
  `GROUP_TOK`, `ISSUE_TOK`, `O<n>` or `dismissed:`, with trailing punctuation stripped.
  - A findings section keeps today's rule, so an off-shape `Carry:` there is still refused as
    UNROUTED.
  - An on-shape but unknown group is still refused as a bad destination, so a mistyped group
    name is still caught.
- **Run against the instances** (`CARRY.search` plus the shape test, run at main `a7628041dc`):
  - The three mentions are not markers: the next tokens are `` `review_carry.py ``, `across` and
    `marker`.
  - The null controls are markers: `Carry: R10-CARRY-AUDIT-P5`, `Carry: #3425` and
    `Carry: dismissed: dup`.
- **Self-test.** The three mention shapes under `## Evidence` route nothing. A
  `Carry: R10-NO-SUCH` under Evidence is still refused. A mutant that drops the shape test refuses
  the first shape again.
