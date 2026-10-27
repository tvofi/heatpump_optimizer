R10-ORCH-REVIEW-PACKET (owner card 8, tvofi 2026-10-24). `bus.sh dispatch` now renders, at the frozen head, a review packet (`tools/audit/seat/review_packet.py`) and names it in the reviewer's brief as `review-packet: <path>`; `fix-review.md` starts the reviewer from it. The packet holds the three-dot diff against the merge base, the head's check runs as read (state pending, green or red, each run's id; card 5's rejection stands, so nothing waits on the gate and the reviewer re-reads live checks before a verdict), `carry_audit.py check` and `figure_lint.mjs --pr-body --at <head>` at the head, the finder's harness output at the base and at the head, and the `tests/mutation_ledger/` three-dot diff. The renderer reads no clock, so the same facts render byte-identical.

What changes:

- **`tools/audit/seat/review_packet.py`** (new): `render`, `check` and `--self-test`. `render` writes the packet; `check` refuses a file whose `head:` line is not the head it is asked for; `dispatch` calls both.
- **`tools/audit/seat/bus.sh`**: `dispatch` renders the packet to `$S/packets/<pr>-<head>.md`, names it, and refuses (recording nothing) when the renderer refuses or the packet does not name the dispatched head. `--harness`/`--harness-file` passes the finder's harness through.
- **`dev/governance/roles/fix-review.md`**: the reviewer starts from the dispatch's packet and re-reads live checks before a verdict. Paid by cuts in the same paragraph; the file's policy budget is unchanged.
- **`tools/audit/seat/INSTRUMENTS.md`**: the entry for the packet and its refusal signals.
- **`dev/audit/harnesses/r10_review_gather_share.py`** (new): the reviewer gather-share measurement the body's figure comes from.
- **`tests/closures.json`**: inert reads for both new files, written by `ci_predict.py --apply-inert`.

Refs #2717 (not closed: roster carry [11], dispatch at the handoff ref, is not built here; see `## Forward-carry`).

The render refuses (rc 1, packet not written, dispatch records nothing), each named by its signal: `carry-audit` (`carry_audit.py check` returns 1), `head-note` (`## Head` does not name the dispatched head), `structure` (`tests/structure.py` refuses the head merged with main via `git merge-tree --write-tree`), `red-unanswered` (a CONCLUDED red `policy_lint.mjs --pr-body --red` reports unnamed in `## Red checks`), `required-red` (carry [6]: the latest run of the ruleset's required context, `gate`, concluded failure), `host-path` (`ref_privacy.body_refusal` on the body, `content_refusals` on the added lines), `hot-file` (carry [7]: the diff shares a `HOT_FILES` path with an open pull request whose `verdict/<pr>` commit's `VERDICT.md` first line, read by `proof_watch.parse_verdict` — the one Python reader of the verdict grammar, which `agreement` refuses a copy of — is a merge verdict at that PR's head and which is not in the train's spool or pending set under `HPO_BUS_TRAIN_STATE`). A pending check never refuses. Independence: `--harness` must exist at the merge base and be untouched by the diff, and runs from the base's bytes at both ends; `--harness-file` must be outside the tree and is cited by sha1; a diff-edited or base-absent harness is refused as the fixer's. `dispatch` then runs `review_packet.py check <packet> --head <head>` and refuses to name a packet that does not name its head.

Caveats a reviewer should weigh:

- The structure arm runs `tests/structure.py` on the merged tree, so a dispatch costs that run; a live render at #2866 measured `real 29.97` wall end to end (`/usr/bin/time -p`, below). It is the brief's signal as specified; a cheaper read was not found. Carry: #2717
- With `HPO_BUS_TRAIN_STATE` unset nothing reads as boarded, so a shared hot file with any merge verdict at its head refuses; the packet prints an advisory saying so. Carry: #2717
- The rule functions are unit-pinned in `review_packet.py --self-test`; the verdict read (`verdict_merge_head`, first line of `VERDICT.md` through `proof_watch.parse_verdict`) is fixture-pinned and mutated; the remaining `gather` I/O wiring (the gh reads, the `policy_lint` message match, the `ref_privacy` calls) is pinned only by the live renders below, not by a mutant. Carry: #2717

## Head

`52aa51050531e1d58e0217c58fb982ec3b358e61`

Every three-dot read below is against the merge base with `origin/main` at this reading, `bfc4a1e297fb2899be1c4643ae9d75b8a5829208`; `origin/main` tip `6fe5170cd7ce01e60ffebfc93e598c216e628fa3` merges the head cleanly (`git merge-tree --write-tree origin/main HEAD` exits 0).

## Mutation proof

Each refusal line in `review_packet.build`, and each rule line below, was replaced by `pass` (or `if False:`) one at a time and `python3 tools/audit/seat/review_packet.py --self-test` re-run: every mutant drew exactly one FAIL.

- `refusals.append("carry-audit…` → FAIL `carry-audit: an unrouted body refuses and names it`
- `refusals.append(f"head-note…` → FAIL `head-note: a ## Head naming another head refuses`
- `refusals.append(f"structure…` → FAIL `structure: a structure refusal at the merge refuses`
- `refusals.append(f"red-unanswered…` → FAIL `red-unanswered: an unanswered concluded red refuses`
- `refusals.append(f"required-red…` → FAIL `required-red: the required context's latest run concluded failure refuses`
- `refusals.append(f"host-path…` → FAIL `host-path: a host path refuses`
- `refusals.append(f"hot-file…` → FAIL `hot-file: a shared hot file with an unboarded merge verdict refuses`
- `out.append(f"#{p…` in `hot_file_refusals` → FAIL `hot-file arm: an unboarded merge verdict sharing a hot file refuses`
- `return v[1] if v and v[0] == "merge" else None` in `verdict_merge_head` → FAIL `hot-file reader: the verdict's head is the first line of VERDICT.md through proof_watch.parse_verdict`
- the `is edited by the diff` raise in `harness_source` → FAIL `independence: a harness the diff edits is refused as the fixer's`
- `pending |= not done` in `gate_digest` → FAIL `a head with checks still running dispatches, digest pending with run ids`

`bash tools/audit/seat/bus.sh --self-test` (`env -u BASH_ENV`) in a mutant worktree:

- the `review_packet.py check` call in `dispatch` replaced by `true` → `bus self-test: 91 checks, 1 failed` (FAIL `a packet naming another head is stale: dispatch refuses to name it and records nothing`)
- the render call replaced by `true render` → `bus self-test: 91 checks, 45 failed`

Restored: `review_packet.py --self-test` prints 21 checks, 0 failed; `bus.sh --self-test` prints 91 checks, 0 failed.

## Null control

`review_packet.py --self-test`: a clean head (no signal set) dispatches with zero refusals; the same required context with its latest run green renders; a head with checks still running dispatches with digest `pending`; the hot-file verdict once boarded passes, and a verdict at a stale head does not count; the verdict reader returns the merge head from a `VERDICT.md` first line and None for a verdict-ref commit subject; a base harness the diff leaves alone is accepted.

Live: `review_packet.py render --pr 2866 --head 6f42fc12…` rendered with `## Refusals` `none` at one reading, and the same command at a later reading refused on four named signals once `gate` and two units had concluded red — the packet reads the live facts, and the earlier render is the null control for the refusal. At the head that pull request carries now (`eb97437e…`) the same render, with this diff's code, again writes `## Refusals` `none` (950 lines, 98657 bytes, `## Gate digest: green`). `review_packet.py render --pr 2864 --head 30c940e5b…` twice, `cmp` byte-identical; `review_packet.py check` refuses an empty packet and a malformed one (rc 1) and a non-40-hex `--head` (rc 2); `--harness` naming a file the diff adds is refused as the fixer's.

## Figures

- Review packet self-test: `python3 -I tools/audit/seat/review_packet.py --self-test` → `review_packet self-test: 21 checks, 0 failed`.
- Verdict read on live refs: `verdict_merge_head` over `refs/heads/verdict/2865` (commit `33d6c5a4210138c6d5878a96cd653231d19f8e25`, subject `verdict: #2865 Fix review: merge 07bc8000…`) → `07bc8000cd85b894ae65905eee065f0e15c21a68`, its `VERDICT.md` first line; over `verdict/2864` (`b3d758ec72959b0c15133ea987acef3bfa6714f5`) → `30c940e5b5e009ebe95004235cbab8536ea14799`. The commit subject format varies across refs, so the verdict file, not the subject, is what the reader pins.
- Bus self-test: `env -u BASH_ENV bash tools/audit/seat/bus.sh --self-test` → `bus self-test: 91 checks, 0 failed` (86 at the base plus the 5 packet cases).
- Reviewer gather share, measured first: `python3 -I dev/audit/harnesses/r10_review_gather_share.py <agent-transcripts dir>` → `RESULT seats=14 calls=731 gather=361 share=49%`. Rule: a reviewer seat is a transcript whose first record names a reviewer brief; a gather call is a `Read`, a `gh api|pr` read, a check-run read, a git read, or a carry_audit/figure_lint/pr-body lint run. Transcripts carry no tool-result sizes, so it is a share of calls, not tokens, and an upper bound on what the packet removes (a `Read` that judges code counts as gather). Null control: `python3 -I dev/audit/harnesses/r10_review_gather_share.py --self-test` refuses a fixer's transcript as a reviewer's. The corpus is out of the tree, so the rule, not the path, is what a later seat re-runs.
- Packet size beside it: a live `review_packet.py render --pr 2866 --head eb97437e…` (the open PR's head at this reading) wrote `950` lines / `98657` bytes (`wc -l -c` on the packet), `## Refusals` `none`, `## Gate digest: green`, dominated by the three-dot diff.
- Byte identity: `python3 -I tools/audit/seat/review_packet.py render --pr 2864 --head 30c940e5b… --out a` and the same to `b`, then `cmp a b` → identical; the packet is `87` lines / `3591` bytes with `## Refusals` `none` and `## Gate digest: green`.
- Structure arm cost: `/usr/bin/time -p python3 -I tools/audit/seat/review_packet.py render --pr 2866 --head eb97437e…` → `real 29.97`s wall end to end, the structure run included.
- Refusals shown, not assumed: `review_packet.py check <empty file> --head …` and `check <malformed file> --head …` each print `REFUSE stale` and return 1; `render --head zzz` prints `--head takes a 40-hex sha` and returns 2; `render --harness tools/audit/seat/review_packet.py` prints `REFUSE independence` and returns 1, writing nothing; the later #2866 render printed `REFUSE red-unanswered` for `gate`, `governance / instrument-self-tests` and `pr-contract / pr-contract`, and `REFUSE required-red` for `gate`.
- Structure ratchet: `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`, every metric at or under its budget (`max_class_loc 8236 <= 8236`, `max_method_loc 373 <= 373`, `methods_over_150 16 <= 16`, `methods_over_200 9 <= 9`, `name_kept_members 38 <= 38`, `seam_cut_total 424 <= 424`).
- Closure self-test: `python3 tests/closure.py selftest` → `ALL 117 closure shrink pins PASSED` (this is the pin the first commit's `--name-only` rename-detecting diff had turned red; `--no-renames` is the repair).
- Scope predictor: `python3 -I tools/pr/ci_predict.py --base origin/main` → `CI PREDICT: no closures, fast, wave-script or instrument red predicted against bfc4a1e297fb (a data-file read is not seen)`, rc 0.
- Scoped gate: see `## Red checks`.

## Approval

This diff edits policy: `dev/governance/roles/fix-review.md`'s opening paragraph now starts the reviewer from the dispatch's `review-packet:` and pays for the sentence by cuts in the same paragraph, which the roster group `R10-ORCH-REVIEW-PACKET` carries under mandate `6329234399` (owner card 8, tvofi 2026-10-24). The policy approval is the orchestrator's approving review at the head under that mandate; this body claims none of its own and no owner approval has been given for this diff yet. The file's policy budget is unchanged: `node tools/policy/policy_lint.mjs --budgets` exits 0 and prints each cap beside its measurement; no cap moved.

## Red checks

The scoped gate (`GATE_SCOPE=auto`, `MODE: SCOPED -- 1 script(s) run, 32 scoped out`) runs `tests/entities.py`, and on this Darwin host four of its checks are red, all in the nightly hang-control self-test:

- `hb:positive_control survives one hung py-spy sample: a fresh spin answers on try 2, the hang cut at the sample's timeout with the spin held across it` — `pass=True calls=1 gaps=[0.6]; a 600 ms spin read as 600.4 ms; dump names the spin: True; py-spy rc=0 names it: True; try 1 of 1 (at most 3)`
- `and a try whose sample misses the spin, or names it at rc!=0, is retried, not accepted` — `idle first: pass=True calls=1; rc=1 first: pass=True calls=1`
- `the control rests between tries: two tries with a 1 s rest take at least the rest plus both spins` — `two tries took 0.80s against a 1.0s rest`
- `the control survives two hung samples, answering on try 3: HB_CONTROL_TRIES is at least 3` — `pass=True calls=1; a 600 ms spin read as 600.4 ms; dump names the spin: True; py-spy rc=0 names it: True; try 1 of 1 (at most 3)`

Root cause: on this loaded Darwin host the control's sample process does not answer inside its 0.5 s cut — the log records `py-spy did not run: TimeoutExpired: … 'dump', '--nonblocking', '--pid', 85058' timed out after 0.5 seconds` on one try, and `Thread 1 (idle)` for the spinning thread on others — so a single sample misses where the checks expect the retry path's second, and the two wall-clock arms read short. Both files are byte-identical to `origin/main` (`git diff origin/main -- tests/entities.py tests/nightly_ha.py` prints nothing), and `origin/main`'s tip `6fe5170cd7ce01e60ffebfc93e598c216e628fa3` carries the required `gate` check `completed success` (check run 121858691740, `gh api repos/tvofi/heatpump_optimizer/commits/6fe5170cd7ce01e60ffebfc93e598c216e628fa3/check-runs`), so the same bytes pass the same checks on CI's runner. Cheaper detector and standing cost: CI's own `gate`, already required on every head; no local instrument decides a sub-second wall-clock bound honestly on a host running four other gates, and a local re-run is the same measurement with the same load. The branch's own scripts are green: the packet self-test, the bus self-test, the closure self-test, the structure ratchet, the agreement lane and the scope predictor above.

## Forward-carry

- Roster carry [11], dispatch the reviewer at the handoff ref (topic-keyed record re-keyed by `open_pr.sh`, a relay posting a held verdict, `standing-dispatch.md` and `fix-review.md` step 7 text) is not built here: it moves the dispatch moment and needs its own policy diff, which `fix-review.md` at zero token headroom (`policy_lint.mjs --budgets`) could not carry beside this one. Its controls stand as the roster states them. Carry: #2717
- The `gather` I/O wiring has no mutant: a later instrument round over `tools/audit/seat/` should give `review_packet.gather` a fixture-driven test (gh stub plus throwaway repo). Carry: #2717

## Friction

none
