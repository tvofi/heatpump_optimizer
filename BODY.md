<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Part of #201

Round-9 process change PROC-4: item 9 of the process review tvofi adopted on 2026-10-01 (git refs as the message bus), plus three follow-ups the roster brief carries.

Before: every handoff, verdict and new head crossed the coordinator twice (fixer, coordinator, orchestrator, coordinator, reviewer). A reviewer handed its verdict text to the orchestrator through relays, and `app_approve.sh`'s evidence gate needed a directory on the orchestrator's machine, which a cloud reviewer's evidence is not. `orchestrator.md` still said seats are "LOCAL-ONLY, hand off, the orchestrator pushes". `policy_lint.mjs` claimed `fixer.md` and `fix-review.md` cite `docs/decisions/0011-app-authored-identity.md`; neither did, and nothing read that claim.

After: `tools/audit/seat/bus.sh push-verdict <pr> <verdict file> <evidence dir>` proposes a reviewer's verdict and its evidence as one commit on the append-only ref `review/<pr>` (fast-forward per round, like `body_push.sh`, so no force-push), refusing a first line outside `fix-review.md`'s grammar, a verdict without its dispatch's `bus-nonce:` line, or an evidence directory where no file names the head. `bus.sh watch --post`, run by the orchestrator as a background task, lists `handoff/*`, `handoff-body/*`, `review/*` and `verdict/*` on the remote, prints `BUS <kind> <name> <sha|gone>` for each ref that appeared, moved or went, and exits on the first change so the exit wakes the orchestrator (item 4). Every cloud seat pushes with one credential, so no ref proves a reviewer, and the orchestrator's confirmation is what does, with or without a coordinator:

- `bus.sh dispatch <pr> <head> <reviewer>`, run by the orchestrator when the reviewer starts, records the dispatch and prints a fresh `bus-nonce:` for the reviewer's brief; a nonce binds only that PR and head.
- `watch --post` reports a new `review/<pr>` tip as `BUS undispatched` (no record for its PR, head and nonce) or `BUS unconfirmed`, naming the reviewer and the command.
- `bus.sh confirm <pr> <review commit>`, after the orchestrator has read that commit in the reviewer's own thread, re-publishes the commit's tree on `verdict/<pr>` signed with the `hpo-approver` App's private key (`$HPO_IDENTITY_DIR/identity-approver.pem`, default `~/.zcode`, the file `app_comment.sh` already signs with), then posts it. The signature is over `hpo-bus verdict <pr> <tree>`, in a `bus-signature:` line, so it binds the pull request and the whole tree, VERDICT.md and evidence; `confirm` refuses on a machine without the key.
- `watch --post` and `bus.sh post <pr>` post a `verdict/<pr>` tip only when that signature verifies against the same key; any other verdict ref prints `BUS unsigned` and posts nothing.

Posting unpacks the tip to `$HPO_BUS_STATE/verdicts/<pr>/<commit>/`, re-checks the grammar and that `evidence/` (not VERDICT.md) names the head, and posts VERDICT.md plus one `bus:` line naming the reviewer, the proposal and the local `evidence/` directory through `app_comment.sh`, which keeps its own refusals (open PR, `merge` at exactly the live head, `hpo-approver[bot]` read-back). A signed tree is posted at most once per pull request (`$HPO_BUS_STATE/posted-signed`), whatever commit or signature encoding carries it; a signature line that is not canonical base64 does not verify; and a commit at most once, both recorded before the poster runs and withdrawn on a refusal, so a kill cannot post twice; a refused one prints `BUS refused` and is not retried by `watch`; `bus.sh post <pr>` retries by hand.

The key never leaves the orchestrator's machine (tvofi, 19:33Z). What a posted verdict proves: it was confirmed on that machine. The nonce ties a proposal to a dispatch at one head, not to a seat (a brief is readable project-wide); authorship rests on the confirmation, as it did on the relay before this change.

A verdict is a comment, never a review: the bus posts only through `app_comment.sh` and approves nothing, so a pull request touching code-owned paths still needs tvofi's own approving review (`main-protect-checks`'s code-owner rule), which the orchestrator gives under the mandate, separately (tvofi, 19:36Z). The self-test pins the poster to `app_comment.sh`; `orchestrator.md` and `fix-review.md` say the review is still owed.

The three role contracts state the refs; `orchestrator.md`'s identity bullet states the split (seats push refs, the orchestrator opens, rows, confirms, posts, approves and merges). `EXCLUDED_BECAUSE_CITED` pins 0011, and `fixer.md` cites it again where the author identity is stated.

How: `watch` diffs `git ls-remote --heads` against `$HPO_BUS_STATE/refs` (default `~/.zcode/bus`); a first pass with no state records a baseline and reports nothing. `push-verdict` builds its tree from a private index over a scratch work tree (`git add -A -f`, so a global excludes file cannot drop a log), never touching the caller's checkout. The signature is `openssl dgst -sha256` with the App's RSA key, not `git commit -S`: `openssl` is what `app_comment.sh` already needs on that machine. `governance.yml`'s `instrument-self-tests` job runs `bus.sh --self-test` beside the `app_approve.sh` and `app_comment.sh` self-tests.

**Settings for tvofi.** None are needed for the proof: the signature verifies whoever pushed the ref, so the bus works as merged. One optional ruleset keeps verdict history intact: on `refs/heads/verdict/**`, restrict deletions and block force pushes, with yourself as the bypass actor. A ruleset restricting updates to the App would refuse the orchestrator's own pushes, which use its normal git credential, so that one is not recommended.

**Policy files.** `tools/audit/briefs/orchestrator.md`, `fixer.md`, `fix-review.md` and `.claude/workflows/policy_lint.mjs`. All are paid for inside their own caps, and no cap is raised. `orchestrator.md`'s identity bullet points at `CLAUDE.md`'s identity section instead of restating which identity makes each write, and section 2's closing clause and section 10b's `brief_lint.mjs` reading note stay. `fixer.md` keeps step 5's scoped-gate cost sentence, cites `body_push.sh` by its shorter resolvable path and drops one justification clause in the budget section ("a list here would be a carried number"). `fix-review.md`'s preamble drops "SHA" after "names the head". `orchestrator.md`'s identity bullet drops "names them" after the `bus.sh` path and shortens "can vanish and purge retroactively" to "vanish retroactively", drops "your" before `bus.sh confirm`, and puts the key as "yours alone": after main d536fb4d grew the file's merge fast-path passage, these keep it inside its cap.

## Head

7231ed14a7e6a640b865dad2b3b48fc45f89c668

Round 4. Round 1 at 73d8d962cc0220d92c18b4d759ebec9205578c91 was blocked on provenance: a hand-made `verdict/<pr>` ref, pushed with the credential every cloud seat shares, posted as `hpo-approver` through `watch --post`. Each later commit answers the next constraint or block: 8b0aff48 gated a post on a coordinator's confirmation and restored the three policy passages round 1 cut to fit the caps; 30914080 moved the gate to whichever role dispatched the reviewer (tvofi, 19:29Z: some environments have only the orchestrator); a6bb0d63 let a reviewer holding the approver key sign (tvofi, 19:32Z); e773c070 keeps the key on the orchestrator's machine (tvofi, 19:33Z) and states that code-owned paths still need tvofi's review (19:36Z). Round 2's review blocked e773c070 on a same-PR replay: a keyless seat re-committed round 1's confirmed merge, tree and signed message, after round 2's block, and `watch --post` posted it because posting deduplicated on the commit sha. ec166685 recorded each posted signature per pull request and refused a second post of it as a replay. The signed payload is the pull request and tree, and each round's fresh nonce makes its tree distinct, so a genuine later round is never refused. Round 3's review blocked ec166685: the check compared the signature line's text, so the same signature with an extra `=` or a trailing space still verified and posted again. c9fedbd1 keys the check on what was signed, `<pr> <tree>`, and `signed_by_approver` refuses a signature line that does not re-encode to itself. b58bf00b merges main d536fb4d64a9a4c27cd49bf63328f9bf8d2e0262 (a merge, no rebase); main's own edit to `orchestrator.md` put it 2 tokens over its cap, and 7231ed14 pays that inside the identity bullet.

Merge base: main d536fb4d. The body travels on `handoff-body/r9-proc-4`, built by `body_push.sh`; the code head carries no transport.

## Approval

Owed before merge: tvofi's approving review at this head. The three role contracts and `policy_lint.mjs` are policy, and `.github/workflows/governance.yml` is code-owned.

## Mutation proof

`bus.sh`: each mutant applied to the committed script, then `bash tools/audit/seat/bus.sh --self-test`, then restored (`git diff` empty after). At c9fedbd1, 45 checks:

- signature check returns success unconditionally: 16 fail, starting with "watch --post posts neither a forged proposal nor a forged verdict ref" and "confirm promotes no proposal that was never dispatched".
- signature payload takes the pull request from the commit subject instead of the ref: 5 fail, including "a signed verdict moved to another pull request does not post".
- signature payload drops the tree on both sides: 6 fail, including "a signature over another tree does not post".
- dispatch gate off: 15 fail, including both forged arms.
- dispatch record matched without the nonce: 1 fails ("another dispatch's nonce does not count").
- dispatch record keyed on the pull request without the head: 1 fails ("round 1's nonce does not count at another head").
- `confirm` skips the dispatch record: 15 fail, starting with "confirm promotes no proposal that was never dispatched".
- the replay check (`posted-signed`) replaced by `false`: 5 fail, "a confirmed verdict replayed after a later round does not post again", both re-encoded arms, and the two raw-ref arms whose call count moves.
- the canonical-base64 comparison removed: 1 fails ("a signature line that is not canonical base64 does not verify"); the re-encoded replays still stop at the tree-keyed check.
- the canonical comparison removed and the replay check keyed on the signature line's text, round 3's code: 5 fail, both "a replay with its signature line re-encoded does not post again" arms among them.
- the replay check keyed on the signature text alone, canonical check kept: 0 fail. The two layers are redundant by design: RSA PKCS#1 v1.5 is deterministic, so for a canonical line the text and the payload key the same verdict, and either layer alone closes the class.
- `watch --post` posts a `review/` tip directly: 5 fail, starting with "watch --post posts neither a forged proposal nor a forged verdict ref".

Red first for round 4: this head's self-test grafted onto ec166685's script fails 5 of 45, both re-encoded replays and the canonical arm among them. For round 3, the self-test grafted onto e773c070's script failed 3 of 42. For round 2, the self-test grafted onto a6bb0d63's script failed 25 of 41, among them "watch --post posts neither a forged proposal nor a forged verdict ref" (that script has no `review/` family and no `BUS unsigned` refusal, and posted a dispatched, confirmed ref that no orchestrator signed) and every `review/` and `confirm` arm. Round 2's forged-ref arms grafted onto round 1's script failed there too: round 1 posted the hand-made ref.

Round-1 mutants, re-run at round 1's head (25 checks then):

- `post_verdict`'s evidence check replaced by `false`: FAIL "watch refuses a raw ref whose only naming file is VERDICT.md"; 25 checks, 1 failed.
- `push_verdict`'s grammar check bypassed (`verdict_sha ... || echo x`): FAIL "push-verdict refuses a first line outside the grammar"; 1 failed.
- the posted-ledger check replaced by `false`: FAIL "post refuses a commit already posted", "the second round is posted", and both raw-ref refusals (the call count moves); 4 failed.
- `push_verdict`'s evidence check replaced by `true`: FAIL "push-verdict refuses evidence that names no head", "no refused push left a verdict ref", "a first pass records a baseline and posts nothing"; 3 failed.

The self-test also caught a real defect while it was written: `watch`'s diff keyed the old snapshot on `NR == FNR`, which treats every current ref as old when the baseline file is empty, so the first changes after an empty baseline printed as `gone`. It keys on `FILENAME == ARGV[1]` now.

`policy_lint.mjs`: with this head's `fixer.md` citation put back to the prose "(decision 0011)", `node .claude/workflows/policy_lint.mjs` exits 1 with `ERROR [citation-presence] docs/decisions/0011-app-authored-identity.md: no policy file cites it any more`. The same error is what the new map entry printed on the tree before `fixer.md` was edited: the check is red first.

## Null control

`bus.sh`'s M0 at round 1, a whitespace edit to the `kind_of` comment line: 25 checks, 0 failed. At c9fedbd1, the restored script after the mutants: 45 checks, 0 failed. Every refusal arm has a passing twin in the same throwaway bare repository: a dispatched proposal confirmed for its own tip is signed and posts once; a second round fast-forwards both refs; an unchanged pass prints nothing. The keys are two fresh `openssl genrsa` keys per run, the approver's in the orchestrator's identity directory and one a fixer made itself under the same file name.

`policy_lint.mjs` at the merge base 25e5b9cc, where no policy file cites the 0011 path either: `node .claude/workflows/policy_lint.mjs` prints TOTAL 0 errors, rc 0. That is the blindness this pin removes.

## Figures

- `bash tools/audit/seat/bus.sh --self-test` at 7231ed14: 45 checks, 0 failed.
- `node .claude/workflows/policy_lint.mjs`: TOTAL 0 errors; `--budgets` prints every capped file within its cap.
- `node .claude/workflows/policy_lint_mutants.mjs`: MUTANTS ok.
- `node .claude/workflows/rules_sync.mjs --check`: RULES-SYNC ok.
- `node .claude/workflows/brief_lint.mjs`: rc 0.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED -- 2 script(s) run`, naming `tests/entities.py` and `tests/harness_headers.py`.
- `PYTHONPATH=tests/hastub python tests/entities.py` (Python 3.14.7, `venv-ci`): ALL ENTITY CHECKS PASSED, rc 0.
- `PYTHONPATH=tests/hastub python tests/harness_headers.py`: ALL HARNESS HEADER CHECKS PASSED, rc 0.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `bash tools/audit/prepr.sh <this body>`: no refusal, rc 0 (figures all resolved).

No production Python changed, so the typing census and real-HA `ha_contract` have nothing to grade here.

## Red checks

- `delivery-status`, red at this head. It grades `main`'s delivery record (the plan's table and `docs/delivery/`), and this diff writes no row, no plan and no `HANDOVER.md`; it is owed an answer here only because the diff touches `governance.yml`, which the exemption lists. The `governance.yml` change adds one step to `instrument-self-tests` (`bus.sh --self-test`) and does not touch the `delivery-status` job or its inputs, so the red is `main`'s record, not this pull request's. Cheaper detector: none; the record is graded where it lives.

## Forward-carry

`tools/audit/briefs/fixer.md` step 6, the `fix-review.md` preamble and `orchestrator.md` section 5 carry the ref conventions to every fixer, reviewer and orchestrator seat. The coordinator's out-of-tree brief add-ons that route handoffs and verdicts through relays are sent to the coordinator to replace with the refs: the orchestrator runs `bus.sh dispatch` when a reviewer starts and puts the printed `bus-nonce:` line in that reviewer's brief, then runs `bus.sh confirm` after reading the reviewer's thread.

One constraint for the orchestrator, measured from this cloud seat: a push that creates a ref under `verdict/` succeeds, and a push that deletes one is refused by the session's git proxy. Seats can therefore never clean a bus ref up; deletion is the orchestrator's.

## Friction

none
