<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Part of #201

Round-9 process change PROC-4: item 9 of the process review tvofi adopted on 2026-10-01 (git refs as the message bus), plus three follow-ups the roster brief carries.

Before: every handoff, verdict and new head crossed the coordinator twice (fixer, coordinator, orchestrator, coordinator, reviewer). A reviewer handed its verdict text to the orchestrator through relays, and `app_approve.sh`'s evidence gate needed a directory on the orchestrator's machine, which a cloud reviewer's evidence is not. `orchestrator.md` still said seats are "LOCAL-ONLY, hand off, the orchestrator pushes". `policy_lint.mjs` claimed `fixer.md` and `fix-review.md` cite `docs/decisions/0011-app-authored-identity.md`; neither did, and nothing read that claim.

After: `tools/audit/seat/bus.sh push-verdict <pr> <verdict file> <evidence dir>` publishes a reviewer's verdict and its evidence as one commit on the append-only ref `verdict/<pr>` (fast-forward per round, like `body_push.sh`, so no force-push), refusing a first line outside `fix-review.md`'s grammar or an evidence directory where no file names the head. `bus.sh watch --post`, run by the orchestrator as a background task, lists `handoff/*`, `handoff-body/*` and `verdict/*` on the remote, prints `BUS <kind> <name> <sha|gone>` for each ref that appeared, moved or went, and exits on the first change so the exit wakes the orchestrator (item 4). For a verdict it unpacks the tip to `$HPO_BUS_STATE/verdicts/<pr>/<commit>/`, re-checks the grammar and that `evidence/` (not VERDICT.md) names the head, and posts VERDICT.md plus one `bus:` line citing that local `evidence/` directory through `app_comment.sh`, which keeps its own refusals (open PR, `merge` at exactly the live head, `hpo-approver[bot]` read-back). A commit is posted at most once; a refused one prints `BUS refused` and is not retried by `watch`, so it cannot wake the orchestrator every pass; `bus.sh post <pr>` retries by hand. The three role contracts state the refs; `orchestrator.md`'s identity bullet states the current split (seats push refs, the orchestrator opens, rows, posts, approves and merges) and that the coordinator relays no head or verdict. `EXCLUDED_BECAUSE_CITED` pins 0011, and `fixer.md` cites it again where the author identity is stated.

How: `watch` diffs `git ls-remote --heads` against `$HPO_BUS_STATE/refs` (default `~/.zcode/bus`); a first pass with no state records a baseline and reports nothing. `push-verdict` builds its tree from a private index over a scratch work tree (`git add -A -f`, so a global excludes file cannot drop a log), never touching the caller's checkout. `governance.yml`'s `instrument-self-tests` job runs `bus.sh --self-test` beside the `app_approve.sh` and `app_comment.sh` self-tests.

**Policy files.** `tools/audit/briefs/orchestrator.md`, `fixer.md`, `fix-review.md` and `.claude/workflows/policy_lint.mjs`. All are paid for inside their own caps, and no cap is raised: `orchestrator.md` drops section 10b's restatement of which files `brief_lint.mjs` reads (`brief-citations.md` carries it) and section 2's closing clause; `fixer.md` drops step 5's restatement of the scoped gate's cost (`tests/README.md` carries it, and its "forty minutes" was a carried number) and a justification clause in the budget section.

## Head

73d8d962cc0220d92c18b4d759ebec9205578c91

Merge base: main 25e5b9cc. The body travels on `handoff-body/r9-proc-4`, built by `body_push.sh`; the code head carries no transport.

## Approval

Owed before merge: tvofi's approving review at this head. The three role contracts and `policy_lint.mjs` are policy, and `.github/workflows/governance.yml` is code-owned.

## Mutation proof

`bus.sh`: each mutant applied to the committed script, then `bash tools/audit/seat/bus.sh --self-test`, then restored (byte-compared after):

- `post_verdict`'s evidence check replaced by `false`: FAIL "watch refuses a raw ref whose only naming file is VERDICT.md"; 25 checks, 1 failed.
- `push_verdict`'s grammar check bypassed (`verdict_sha ... || echo x`): FAIL "push-verdict refuses a first line outside the grammar"; 1 failed.
- the posted-ledger check replaced by `false`: FAIL "post refuses a commit already posted", "the second round is posted", and both raw-ref refusals (the call count moves); 4 failed.
- `push_verdict`'s evidence check replaced by `true`: FAIL "push-verdict refuses evidence that names no head", "no refused push left a verdict ref", "a first pass records a baseline and posts nothing"; 3 failed.

The self-test also caught a real defect while it was written: `watch`'s diff keyed the old snapshot on `NR == FNR`, which treats every current ref as old when the baseline file is empty, so the first changes after an empty baseline printed as `gone`. It keys on `FILENAME == ARGV[1]` now.

`policy_lint.mjs`: with this head's `fixer.md` citation put back to the prose "(decision 0011)", `node .claude/workflows/policy_lint.mjs` exits 1 with `ERROR [citation-presence] docs/decisions/0011-app-authored-identity.md: no policy file cites it any more`. The same error is what the new map entry printed on the tree before `fixer.md` was edited: the check is red first.

## Null control

`bus.sh`'s M0, a whitespace edit to the `kind_of` comment line: 25 checks, 0 failed. Each refusal arm has a passing twin in the same throwaway bare repository (a verdict with evidence publishes and posts; an unchanged pass prints nothing; a second round fast-forwards).

`policy_lint.mjs` at the merge base 25e5b9cc, where no policy file cites the 0011 path either: `node .claude/workflows/policy_lint.mjs` prints TOTAL 0 errors, rc 0. That is the blindness this pin removes.

## Figures

- `bash tools/audit/seat/bus.sh --self-test` at 73d8d962: 25 checks, 0 failed.
- `node .claude/workflows/policy_lint.mjs`: TOTAL 0 errors; `--budgets` prints every capped file within its cap.
- `node .claude/workflows/policy_lint_mutants.mjs`: MUTANTS ok.
- `node .claude/workflows/rules_sync.mjs --check`: RULES-SYNC ok.
- `node .claude/workflows/brief_lint.mjs`: rc 0.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED -- 2 script(s) run`, naming `tests/entities.py` and `tests/harness_headers.py`.
- `PYTHONPATH=tests/hastub python tests/entities.py` (Python 3.14.7, `venv-ci`): ALL ENTITY CHECKS PASSED, rc 0.
- `PYTHONPATH=tests/hastub python tests/harness_headers.py`: ALL HARNESS HEADER CHECKS PASSED, rc 0.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `bash tools/audit/prepr.sh <this body>`: no refusal, rc 0 (pr-body 0 errors, figures all resolved).

No production Python changed, so the typing census and real-HA `ha_contract` have nothing to grade here.

## Red checks

none

## Forward-carry

`tools/audit/briefs/fixer.md` step 6, the `fix-review.md` preamble and `orchestrator.md` section 5 carry the ref conventions to every fixer, reviewer and orchestrator seat. The coordinator's out-of-tree brief add-ons that route handoffs and verdicts through relays are sent to the coordinator to replace with the refs.

One constraint for the orchestrator, measured from this cloud seat: a push that creates a ref under `verdict/` succeeds, and a push that deletes one is refused by the session's git proxy ("the remote end hung up unexpectedly"; the ref stayed, read back with `git ls-remote`). Seats can therefore never clean a bus ref up; deletion is the orchestrator's. The probe left `verdict/0` (an empty tree) on origin for it to delete.

## Friction

none
