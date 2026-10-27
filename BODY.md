R10-ORCH-REVIEW-PACKET (owner card 8, tvofi 2026-10-24). `bus.sh dispatch` now renders, at the frozen head, a review packet (`tools/audit/seat/review_packet.py`) and names it in the reviewer's brief as `review-packet: <path>`; `fix-review.md` starts the reviewer from it. The packet holds the three-dot diff against the merge base, the head's check runs as read (state red, pending, `none` or green, each run's id; card 5's rejection stands, so nothing waits on the gate and the reviewer re-reads live checks before a verdict), `carry_audit.py check` and `figure_lint.mjs --pr-body --at <head>` at the head, the finder's harness output at the base and at the head, and the `tests/mutation_ledger/` three-dot diff. The renderer reads no clock, so the same facts render byte-identical.

What changes:

- **`tools/audit/seat/review_packet.py`** (new): `render`, `check` and `--self-test`. Every git read runs in the checkout the working directory is in (`repo()`, `git rev-parse --show-toplevel`), never the tool's install, so a dispatch from a throwaway clone resolves its own head. A refusal states a fact about the head and the packet is still written, except `host-path`, which writes nothing because the packet carries the diff verbatim; a head whose check runs were not read digests as `none`, never `green`.
- **`tools/audit/seat/bus.sh`**: `dispatch` renders the packet to `$S/packets/<pr>-<head>.md`, names it, and refuses (recording nothing) when the renderer refuses or the packet does not name the dispatched head. `--harness`/`--harness-file` passes the finder's harness through.
- **`tools/audit/seat/cloud_dispatch.py`**: a cloud reviewer renders its own packet at the dispatched head, because the dispatcher's copy is a path on the dispatcher's machine; the dispatcher's self-test stubs the renderer (`HPO_BUS_PACKER`) and checks that a refused packet holds the dispatch and records nothing; the relay's nonce is found by search on its own line, not by stripping a prefix from a line the packet now precedes.
- **`.github/workflows/governance.yml`**: one `instrument-self-tests` step, "Show the review packet refusing its own fixtures", runs `review_packet.py --self-test` and greps its verdict line.
- **`tools/pr/ci_predict.py`**: the `instrument` job gains a WIRING arm (`wiring_preds`) — a self-testing file the diff adds that no workflow `run:` line names is predicted `UNWIRED <path>` — and `plant_self_test` pins its call site in `predict()`, so deleting the call site fails a check instead of leaving the arm dead (#1591).
- **`dev/governance/roles/fix-review.md`**: the reviewer starts from the dispatch's packet and re-reads live checks before a verdict. Paid by cuts in the same paragraph; the file's policy budget is unchanged.
- **`tools/audit/seat/INSTRUMENTS.md`**: the entry for the packet and its refusal signals, including that a refusal still writes.
- **`dev/audit/harnesses/r10_review_gather_share.py`** (new): the reviewer gather-share measurement the body's figure comes from.
- **`tests/closures.json`**: inert reads for both new files, written by `ci_predict.py --apply-inert`.

Refs #2717 (not closed: roster carry [11], dispatch at the handoff ref, is not built here; see `## Forward-carry`).

The render refuses (rc 1, `## Refusals` names each signal, `dispatch` records nothing and names no packet), each by its signal: `carry-audit` (`carry_audit.py check` returns 1), `head-note` (`## Head` does not name the dispatched head), `structure` (`tests/structure.py` refuses the head merged with main via `git merge-tree --write-tree`), `red-unanswered` (a CONCLUDED red `policy_lint.mjs --pr-body --red` reports unnamed in `## Red checks`), `required-red` (carry [6]: the latest run of the ruleset's required context, `gate`, concluded failure), `host-path` (`ref_privacy.body_refusal` on the body, `content_refusals` on the added lines), `hot-file` (carry [7]: the diff shares a `HOT_FILES` path with an open pull request whose `verdict/<pr>` commit's `VERDICT.md` first line, read by `proof_watch.parse_verdict` — the one Python reader of the verdict grammar, which `agreement` refuses a copy of — is a merge verdict at that PR's head and which is not in the train's spool or pending set under `HPO_BUS_TRAIN_STATE`). A pending check never refuses. Independence: `--harness` must exist at the merge base and be untouched by the diff, and runs from the base's bytes at both ends; `--harness-file` must be outside the tree and is cited by sha1; a diff-edited or base-absent harness is refused as the fixer's. `dispatch` then runs `review_packet.py check <packet> --head <head>` and refuses to name a packet that does not name its head.

Caveats a reviewer should weigh:

- The structure arm runs `tests/structure.py` on the merged tree, so a dispatch costs that run; a live render at #2864's head measured `real 44.72` wall end to end on this loaded host (`/usr/bin/time -p`, below). It is the brief's signal as specified; a cheaper read was not found. Carry: #2717
- With `HPO_BUS_TRAIN_STATE` unset nothing reads as boarded, so a shared hot file with any merge verdict at its head refuses; the packet prints an advisory saying so. Carry: #2717
- The rule functions are unit-pinned in `review_packet.py --self-test`; the verdict read (`verdict_merge_head`, first line of `VERDICT.md` through `proof_watch.parse_verdict`) is fixture-pinned and mutated; the remaining `gather` I/O wiring (the gh reads, the `policy_lint` message match, the `ref_privacy` calls) is pinned only by the live renders below, not by a mutant. Carry: #2717

## Head

The authored code head is `627f44cfee56756ee4a97277204bd320423b9d33`, six commits over the previous head `410d3988fd2ae01ea6ec281174e470b4f5540bcb`: the packet's dispatched-checkout read, its self-test wired into the instrument job, the cloud reviewer's own render and its two fixtures, the throwaway-checkout helper, and the predictor's call-site pin.

Every three-dot read below is against the merge base with `origin/main` at this reading, `484d9902222031f8e081df9f53b52ffd50fcc0af`; `origin/main` tip `524c1896b6943b3da03d6cad61420ced31e14c9c` merges the code head cleanly (`git merge-tree --write-tree origin/main HEAD` exits 0).

## Mutation proof

Each refusal line in `review_packet.build`, each new rule line, and each new check below was replaced one at a time and its own self-test re-run; every mutant drew the FAILs named, and each file was restored byte-identical (`diff -q` against a backup, `review_packet.py --self-test` back to 0 failed).

`review_packet.py --self-test`:

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
- `repo()` returning `Path(__file__).resolve().parents[3]` (the install) → FAIL `repo(): a git read runs in the checkout the working directory is in, not the tool's install`
- `writes_packet` returning `True` always → 2 FAILs: `write-on-refusal: a host path writes nothing` and `write-on-refusal: one host path beside other refusals still writes nothing`
- the digest's `else "none"` dropped (green) → FAIL ``a head with no run read is `none`, never `green` ``

`cloud_dispatch.py --self-test`:

- the packet-render sentence deleted from `_prompt` → FAIL `the reviewer's brief carries the packet render at the dispatched head for the seat's own machine`
- `re.search(r"^bus-nonce: …")` reverted to `relay.removeprefix("bus-nonce: ").strip()` → 3 FAILs, the first `a relay dispatch at a second pull request mints its nonce` (the two below it consume the nonce it fails to mint)

`ci_predict.py`:

- `preds += wiring_preds(root, changed)` replaced by `pass` in `predict()` → FAIL `a self-testing tool the diff adds with no workflow run line is predicted red` (`ci_predict self-test: 6 failed` against the 5 pre-existing host FAILs measured identically at `origin/main` tip `524c1896b`, below); the case passes with the line present.
- `wiring_preds` returning `[]` → FAIL `an unwired self-testing tool the diff adds is predicted red`
- the governance step deleted is the red tree itself: at `410d3988f` (no step) `selftest_wiring.py --check` prints `98 self-testing, 97 wired, 1 unwired` and the CI step exits 1; at this head it prints `0 unwired`.

`bash tools/audit/seat/bus.sh --self-test` (`env -u BASH_ENV`) in a mutant worktree:

- the `review_packet.py check` call in `dispatch` replaced by `true` → `bus self-test: 91 checks, 1 failed` (FAIL `a packet naming another head is stale: dispatch refuses to name it and records nothing`)
- the render call replaced by `true render` → `bus self-test: 91 checks, 45 failed`

Restored: `review_packet.py --self-test` prints 28 checks, 0 failed; `cloud_dispatch.py --self-test` prints 76 checks, 0 failed; `bus.sh --self-test` prints 91 checks, 0 failed.

## Null control

`review_packet.py --self-test`: a clean head (no signal set) dispatches with zero refusals; the same required context with its latest run green renders; a head with checks still running dispatches with digest `pending`; a head whose check runs were not read digests `none`; the hot-file verdict once boarded passes, and a verdict at a stale head does not count; the verdict reader returns the merge head from a `VERDICT.md` first line and None for a verdict-ref commit subject; a base harness the diff leaves alone is accepted; a clean render writes, and a concluded red writes beside a host path that does not.

Live: `review_packet.py render --pr 2864 --head 30c940e5b…` twice, `cmp` byte-identical, `## Refusals` `none`; `check` refuses an empty packet and a malformed one (rc 1) and a non-40-hex `--head` (rc 2); `--harness` naming a file the diff adds is refused as the fixer's.

`ci_predict.py`: the five FAILs it prints on this host are the agreement lane's `raise-justification` divergence on bodies 20 and 24 inside the plant's throwaway clone, and they are the same five case names, in the same order, at `origin/main` tip `524c1896b` (`ci_predict self-test: 5 failed`, `EXIT=5` there): a host-dependent reading, not this branch's. `origin/main`'s own CI is green on `governance / wave-script`, and the lane run outside the clone reports `divergent=0`. The WIRING arm's null control is its own third case: a tool main already carries is not this branch's.

## Figures

- Review packet self-test: `python3 -I tools/audit/seat/review_packet.py --self-test` → `review_packet self-test: 28 checks, 0 failed`; `/usr/bin/time -p` on it → `real 0.38`.
- Cloud dispatcher self-test: `python3 -I tools/audit/seat/cloud_dispatch.py --self-test` → `cloud_dispatch self-test: 76 checks, 0 failed`; `/usr/bin/time -p` → `real 14.12`.
- Wiring reader: `python3 -I tools/audit/seat/selftest_wiring.py --check` → `selftest_wiring: 98 self-testing, 98 wired, 0 unwired`; `/usr/bin/time -p` → `real 0.21`.
- Scope predictor: `PYTHONPATH=tests/hastub python3 -I tools/pr/ci_predict.py --base origin/main` → `CI PREDICT: no closures, fast, wave-script or instrument red predicted against 484d99022220 (a data-file read is not seen)`, rc 0; `/usr/bin/time -p` → `real 6.92`.
- The predictor on the defect: the same command, with this head's `ci_predict.py`, in a worktree at `410d3988f` → `PREDICT governance / instrument-self-tests UNWIRED tools/audit/seat/review_packet.py: no workflow run line names its self-test`, `CI PREDICT: 1 predicted red(s) …`, rc 1.
- Predictor self-test: `python3 -I tools/pr/ci_predict.py --self-test` → `ci_predict self-test: 5 failed` (the host-dependent agreement cases above); at `origin/main` tip `524c1896b` the same 5 case names and `EXIT=5`.
- Bus self-test: `env -u BASH_ENV bash tools/audit/seat/bus.sh --self-test` → `bus self-test: 91 checks, 0 failed` (86 at the base plus the 5 packet cases).
- Verdict read on live refs: `verdict_merge_head` over `refs/heads/verdict/2865` (commit `33d6c5a4210138c6d5878a96cd653231d19f8e25`, subject `verdict: #2865 Fix review: merge 07bc8000…`) → `07bc8000cd85b894ae65905eee065f0e15c21a68`, its `VERDICT.md` first line; over `verdict/2864` (`b3d758ec72959b0c15133ea987acef3bfa6714f5`) → `30c940e5b5e009ebe95004235cbab8536ea14799`. The commit subject format varies across refs, so the verdict file, not the subject, is what the reader pins.
- Reviewer gather share, measured first: `python3 -I dev/audit/harnesses/r10_review_gather_share.py <agent-transcripts dir>` → `RESULT seats=14 calls=731 gather=361 share=49%`. Rule: a reviewer seat is a transcript whose first record names a reviewer brief; a gather call is a `Read`, a `gh api|pr` read, a check-run read, a git read, or a carry_audit/figure_lint/pr-body lint run. Transcripts carry no tool-result sizes, so it is a share of calls, not tokens, and an upper bound on what the packet removes (a `Read` that judges code counts as gather). Null control: `python3 -I dev/audit/harnesses/r10_review_gather_share.py --self-test` refuses a fixer's transcript as a reviewer's. The corpus is out of the tree, so the rule, not the path, is what a later seat re-runs.
- Packet size and byte identity: `python3 -I tools/audit/seat/review_packet.py render --pr 2864 --head 30c940e5b… --out a` and the same to `b`, then `cmp a b` → identical; the packet is `87` lines / `3591` bytes with `## Refusals` `none` and `## Gate digest: green`.
- Packet cost: `/usr/bin/time -p python3 -I tools/audit/seat/review_packet.py render --pr 2864 --head 30c940e5b… --out a` → `real 44.72` wall end to end, the structure run included, on this host under four other gates.
- Refusals shown, not assumed: `review_packet.py check <empty file> --head …` and `check <malformed file> --head …` each print `REFUSE stale` and return 1; `render --head zzz` prints `--head takes a 40-hex sha` and returns 2; `render --harness tools/audit/seat/review_packet.py` prints `REFUSE independence` and returns 1, writing nothing.
- Structure ratchet: `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`, every metric at or under its budget (`max_class_loc 8236 <= 8236`, `max_method_loc 373 <= 373`, `methods_over_150 16 <= 16`, `methods_over_200 9 <= 9`, `name_kept_members 38 <= 38`, `seam_cut_total 424 <= 424`).
- Closure self-test: `python3 tests/closure.py selftest` → `ALL 117 closure shrink pins PASSED`.
- Red history: `gh api --paginate "repos/tvofi/heatpump_optimizer/commits/410d3988fd2ae01ea6ec281174e470b4f5540bcb/check-runs" --jq '.check_runs[] | select(.status=="completed" and .conclusion=="failure") | select(.name!="pr-contract / pr-contract" and .name!="gate") | .name'` → `governance / instrument-self-tests`, the one name this branch's ancestry owes; the earlier head `d0087e3ad…` adds none under the same filter.
- Instrument job: `gh api repos/tvofi/heatpump_optimizer/actions/jobs/122007070159 --jq '{started:.started_at,completed:.completed_at}'` → `2026-10-27T04:18:39Z` to `2026-10-27T04:36:41Z`, 1082 s.
- Scoped gate: see `## Red checks`.

## Approval

This diff edits policy: `dev/governance/roles/fix-review.md`'s opening paragraph now starts the reviewer from the dispatch's `review-packet:` and pays for the sentence by cuts in the same paragraph, which the roster group `R10-ORCH-REVIEW-PACKET` carries under mandate `6329234399` (owner card 8, tvofi 2026-10-24). The policy approval is the orchestrator's approving review at the head under that mandate; this body claims none of its own and no owner approval has been given for this diff yet. The file's policy budget is unchanged: `node tools/policy/policy_lint.mjs --budgets` exits 0 and prints each cap beside its measurement; no cap moved.

## Red checks

`governance / instrument-self-tests` is red at `410d3988fd2ae01ea6ec281174e470b4f5540bcb`, the previous head, six commits below this one and inside the branch's ancestry. Job `122007070159` failed two of its steps, each read from that step's own output:

- step 27, "Refuse a self-testing seat instrument that no step runs": `UNWIRED tools/audit/seat/review_packet.py: no workflow run line names its self-test`; `selftest_wiring: 98 self-testing, 97 wired, 1 unwired`; exit 1.
- step 33, "Show the cloud dispatcher refusing its own fixtures": `Refusal: bus.sh dispatch refused: review_packet: REFUSED git merge-base origin/main 7f4eed19e877c4bdfdddf20399e9a4723741cdb1: fatal: Not a valid commit name 7f4eed19…`, from `_bus_dispatch` into `bus.sh dispatch` — the renderer read its own install directory, not the throwaway checkout it was dispatching for.

Both are real, both were this pull request's, and both are repaired in this head: the packet's self-test is a step in that same job (`Show the review packet refusing its own fixtures`), and `review_packet.repo()` reads `git rev-parse --show-toplevel` of the working directory. Measured at `627f44cfee…`: `selftest_wiring.py --check` → `98 self-testing, 98 wired, 0 unwired`; `cloud_dispatch.py --self-test` → `76 checks, 0 failed`; `review_packet.py --self-test` → `28 checks, 0 failed`.

Cheaper detector and its standing cost. For step 27 the cheaper detector is the predictor `prepr.sh` step 6d already runs (`tools/pr/ci_predict.py --base origin/main`, 6.9 s on this host) and `body_push.sh` runs again; this pull request gives it the WIRING arm, which runs `selftest_wiring.py --check` (0.21 s) over the changed paths. It is shown detecting: run against the red tree at `410d3988f` it prints `PREDICT governance / instrument-self-tests UNWIRED tools/audit/seat/review_packet.py: no workflow run line names its self-test` and exits 1, and against this head it predicts no red (rc 0). Standing cost: 0.2 s on every prepr run, plus the new 0.38 s governance step that pins the packet's own self-test; the red it replaces cost a 1082 s job round trip plus the fix-and-push round. The process state was (c): prepr ran, and its predictor had no arm for an unwired self-test, so the process was followed and did not produce the intended result; the arm is the repair. For step 33 the cheapest detector is `cloud_dispatch.py --self-test` itself (14.1 s, in the tree, part of that same CI job), which failed at the red head and passes here; the process state was (a) — nothing local ran it before the handoff. Its standing cost is already paid by the job, so no new check is added for it inside this fix; the dispatcher's own self-test now also holds a refused packet.

The scoped gate (`GATE_SCOPE=auto`) runs `tests/entities.py`, and on this Darwin host four of its checks are red, all in the nightly hang-control self-test:

- `hb:positive_control survives one hung py-spy sample: a fresh spin answers on try 2, the hang cut at the sample's timeout with the spin held across it` — `pass=True calls=1 gaps=[0.6]; a 600 ms spin read as 600.4 ms; dump names the spin: True; py-spy rc=0 names it: True; try 1 of 1 (at most 3)`
- `and a try whose sample misses the spin, or names it at rc!=0, is retried, not accepted` — `idle first: pass=True calls=1; rc=1 first: pass=True calls=1`
- `the control rests between tries: two tries with a 1 s rest take at least the rest plus both spins` — `two tries took 0.80s against a 1.0s rest`
- `the control survives two hung samples, answering on try 3: HB_CONTROL_TRIES is at least 3` — `pass=True calls=1; 600 ms spin read as 600.4 ms; try 1 of 1 (at most 3)`

Root cause: on this loaded Darwin host the control's sample process does not answer inside its 0.5 s cut, so a single sample misses where the checks expect the retry path's second, and the two wall-clock arms read short. Both files are byte-identical to `origin/main` (`git diff origin/main -- tests/entities.py tests/nightly_ha.py` prints nothing), and `origin/main`'s tip `524c1896b` carries the required `gate` check `completed success`, so the same bytes pass the same checks on CI's runner. Cheaper detector and standing cost: CI's own `gate`, already required on every head; no local instrument decides a sub-second wall-clock bound honestly on a host running four other gates. The branch's own scripts are green: the packet, dispatcher, wiring, bus, closure and structure instruments above, and the predictor.

## Forward-carry

- Roster carry [11], dispatch the reviewer at the handoff ref (topic-keyed record re-keyed by `open_pr.sh`, a relay posting a held verdict, `standing-dispatch.md` and `fix-review.md` step 7 text) is not built here: it moves the dispatch moment and needs its own policy diff, which `fix-review.md` at zero token headroom (`policy_lint.mjs --budgets`) could not carry beside this one. Its controls stand as the roster states them. Carry: #2717
- The `gather` I/O wiring has no mutant: a later instrument round over `tools/audit/seat/` should give `review_packet.gather` a fixture-driven test (gh stub plus throwaway repo). Carry: #2717

## Friction

prepr: unenforced: step 6d's predictor had no arm for an unwired self-test, so the branch was green locally and red in the instrument job after 1082 s; the WIRING arm this pull request adds runs the same check in 0.21 s. Carry: #2717
