R10-FLY-GH-READ-RETRY, PR 1 of 2: `tools/pr/app_approve.sh`'s GitHub reads retry with a bounded backoff, and only on failures that a later read can ride out.

Train 8 stopped at 21:50:38Z on `app_approve: REFUSE: could not read pull request #2547`, after a 2667 s CI wait. That was one `gh api` call with no retry, and its stderr was not kept, so nothing recorded what kind of failure it was. The roster brief counts this as the third instance of the class "one unretried GitHub read kills an instrument".

What changes, in `tools/pr/app_approve.sh`:

- **`gh_read <var> <gh api args...>`** is the one entry for the four reads: the pull request (read twice by `check_pr`, before the mint and before the POST), the comments (`--paginate`), `.github/CODEOWNERS` at `ref=main`, and the changed files (`--paginate`). It sets `<var>` to the answer. On a refusal it returns 1 and leaves gh's stderr in `GH_ERR`, and every `die` at those sites names that error.
- **`gh_transient <stderr>`** classifies a failure from gh's stderr as it came, line by line. Retried: a status line `gh: <message> (HTTP NNN)` or `gh: HTTP NNN` whose status is 5xx or 429, or 403 with the phrase `secondary rate limit` in any case; with no status line, a transport line starting Go's `Get "http(s)://...": ` or gh's `error connecting to `. Everything else refuses after its one call.
- **The budget is `app_push.sh`'s read-back rule**: 4 reads, settling `READ_SLEEP * 3^(n-1)`, so 5/15/45 s, each settle printed. A spent budget refuses with the last error and `(after 4 attempts)`.
- **A wrong answer is never retried**: the callers judge a completed read after `gh_read` returns 0. **Writes are never retried**: the mint, the review POST and the revoke stay single `curl` calls.
- **The comments' python parse** keeps its own refusal, reworded to `could not parse the comments`.
- **`tools/audit/seat/INSTRUMENTS.md`**: the `app_approve.sh` entry states the rule.

This round clears the review of `6e4d2b5c` (blocked: `mutant-survives` on gh_transient's classification branches; `carry-missing`) and its three findings:

- **Every alternative of gh_transient is pinned from both sides.** The self-test derives the alternatives from gh_transient's own source (`ALTS`, the rule in `## Figures`) and keys a table of 43 inputs to exactly that set. Each key holds at least one input that must classify transient and one near-miss that must refuse, and each row goes through the production `gh_transient`. The table's own preconditions are checks: its keys equal the derived set, every key holds both classes, and gh_transient prints nothing on either stream. The review's probes are rows: `error connecting to` (transient), a primary-rate-limit 403 (refuse), a mixed-case `Secondary Rate Limit` 403 (transient), a 520 (transient), and an unanchored `post-step: Get "https://...": EOF` (refuse).
- **Three rows encode design choices**, stated in the self-test beside the table. Of two status lines the last decides, because it is the response gh read last, and only a whole line is a status line. A status line decides even beside a transport line. The `secondary rate limit` phrase rescues a 403 only, and only as the whole phrase.
- **The finding's X17** (classify the folded `GH_ERR`, not gh's stderr) gets an end-to-end arm, `rhint`: a 502 followed by a second stderr line, then an answer, is approved after one retry. The folded `GH_ERR` puts the status mid-line, where no rule reads it. **X13** (`tail -1` -> `head -1`) is killed by the two-status-line rows.
- **The sweep gains the classifier's rules.** `dev/audit/harnesses/r10_gh_read_retry_mutants.py` adds eight rules over each `case` label and each single-quoted sed/grep pattern of the region:
  - `alt`: drop each `|` alternative;
  - `glob`: each `?` of a label to `0`, and `?*` to `*`;
  - `anch`: drop each `^` and `$`;
  - `quant`: drop each `?` and `*` quantifier;
  - `word`: drop each word of an all-letter phrase;
  - `flag`: drop each sed/grep option letter;
  - `pipe`: `| tail -N` to `| head -N`, and deleted;
  - `src`: a `"$(cat "$F")"` argument to each variable the region assigns from `< "$F"`.

  A mutant that fails only the table's source-text preconditions reads SURVIVED, not KILLED. Dropping an alternative changes the set those checks derive, so they would otherwise kill every `alt` mutant with no input classified differently.
- **One equivalent left the harness.** Deleting `?*) return 1` was listed as equivalent "for one stderr holding a status and a transport line". That stderr is now a row, so the mutant is killed and the entry is gone.
- **The carry-missing block.** The roster branch is frozen until #2588 merges, so the item is in `## Forward-carry` as a fenced `roster_edit append-carry R10-FLY-GH-READ-RETRY` text, for the orchestrator to apply. It extends the item to the classifier rules of this round. No roster write was made, so there is no roster SHA to name. The roster read is `origin/handoff/audit-r10-roster` at `306a96d5f21f7876070d48c194fd4be99b64022c`, where the group's `carry` holds the fourth-instance note and item 0e5922c7, and not this item.

Alternatives, and why each lost (fixer.md step 17):

- **Factor a shared helper with `app_push.sh`.** Its reads go through `curl -f`, which reports every status of 400 and over as exit 22, so its classifier works on a different signal. Sharing the six-line settle loop needs a new sourced file, a `tests/closure.py` classification and an `app_push.sh` edit, all outside this PR's scope. The rule is shared instead.
- **Retry on any non-zero exit.** That retries a 404 and a 401, so a refusal reads as slow success. The sweep's `?*) return 1` -> `return 0` mutant is killed.
- **Honour `Retry-After`.** `gh api` exposes headers only on stdout under `--include`, mixed into the paginated JSON this script parses.
- **Hand-pick the classifier's mutants** (the review's X list). A hand list was what missed these branches. The rules regenerate the list from the code, and the review's 23 named mutants are re-run below as the finder's harness.
- **Simplify gh_transient to drop the anchors or `tail -1`.** That changes which stderr refuses, with no gain in code. The anchors are what keep a status line from matching mid-line.

Architecture score: `score.py --diff` prints `dS +0.0000 NULL`. No ratchet row moves and no budget is raised.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_013tC9Y1rUeYSc7kdayWDLao

## Head

`37cffb09c1bffa3a35af13ba9bee3f7c7f6445a1`. The branch's commits, oldest first:

- `d42bda80f0477a72f41cc1588352b4f48e7ff046`: the retry.
- `e4b3e01abb48644841202e7d7b0ae93107258bd3`: the delivery row.
- `f84fa6b2ee17023b032e87bd4df779cd529ccda9`: merge of `origin/main`.
- `0f2fa660b07f9a4e039abb6e8cb38de06f53bdaf`: the budget pin, the queue census and the first sweep.
- `1063eb3a4ef69f924932b4159a67fd55dbb37c1a`: the INERT READS entry.
- `14eda530b4b24b7620b21970564c825778e9537d`: merge of `1063eb3a`.
- `6e4d2b5cf5e9580e20198e2ea282bdb6ef597516`: merge of `origin/main` (the reviewed head).
- `fd1e3f6c47c878fd7014a8a241bb1dd919ea84ac`: merge of `origin/main` at `07fcbee2ed9e38e71d8ca497e1b2470b16baf09f`. That is `origin/main`'s tip and the merge base, re-read at 2026-10-22T04:14:20Z.
- `21307f6fc8e0b81ae03565604c3b6aeeed505496`: the alternatives table, the `rhint` arm, the multi-line stub, and the sweep's eight classifier rules.
- `37cffb09c1bffa3a35af13ba9bee3f7c7f6445a1`: three two-line rows, and the stale equivalent removed.

Every figure below was taken at `37cffb09` unless a row names another tree. The other end is `fd1e3f6c`: this round's base, with main merged and round 2's tests.

## Mutation proof

**The sweep at both ends.** Command: `python3 dev/audit/harnesses/r10_gh_read_retry_mutants.py`, with this round's harness at both ends, so both ends sweep the same 119 rule-generated mutants. At `fd1e3f6c` the harness file was copied into a scratch worktree of that commit.

| tree | self-test | killed | equivalent | survivors | rc |
|---|---|---|---|---|---|
| `fd1e3f6c` (round 2's tests) | 218 checks | 92 | 10 | 17 | 1 |
| `37cffb09` (this round) | 225 checks | 109 | 10 | 0 | 0 |

M0, the unmutated tree, is `NULL-OK` at both ends.

The 17 survivors at `fd1e3f6c`, each killed at `37cffb09`. The separating row was measured by evaluating each mutated `gh_transient` over the 43 table rows (a scratch probe):

| mutant | rule | killed by at `37cffb09` |
|---|---|---|
| M17 | sed `anch ^` | the table (`warning: gh: ... (HTTP 404)` after a 502) |
| M21 | sed `anch $` | the table (`... (HTTP 404) see the docs` after a 502) |
| M24 | `pipe tail->head` | the table (the two-status rows) |
| M25 | `pipe -tail` | the table |
| M37 | `glob 5??->50?` (the review's X4b) | the table (`HTTP 520`, `HTTP 599`) |
| M45 | `word -secondary` (X20) | the table (the primary-limit 403) |
| M47 | `word -limit` | the table (`secondary rate exceeded`) |
| M48 | 403 grep `flag -q` | `and gh_transient prints nothing on either stream` |
| M49 | `flag -i` (X14) | the table (`Secondary Rate Limit`) |
| M53 | `del ?*) return 1` | the table (a 404 beside `error connecting to`) |
| M54 | `glob ?*->0*` | the same row |
| M58 | `alt '^error connecting to '` (X7) | the table |
| M59 | transport `anch ^` (X22) | the table (`post-step: Get ...`) |
| M60 | `quant ?` in `https?` | the table (`Get "http://..."`) |
| M63 | `anch ^error` | the table (`proxy: error connecting to ...`) |
| M64 | transport grep `flag -q` | `and gh_transient prints nothing on either stream` |
| M93 | `src -> $GH_ERR` (X17) | `a 502 followed by a second stderr line, then an answer, is approved` |

The 10 equivalents each carry their reason in the harness's `EQUIVALENT` table:

- six are `return 1` to `return 2` or `999`, which no caller can tell apart;
- `-ge` to `-eq` on the budget: `_try` steps by 1 from 1;
- `-eq 1` to `-le 1`: `_try` is never below 1;
- deleting `GH_ERR=""` or `local code`: neither has another reader.

**The finder's harness at both ends.** This is the review's own mutant runner and list, `evidence/my-mutants-runner.py` on `origin/review/2589`, run against a detached worktree. Command: `python3 my-mutants-runner.py <dir>`.

| tree | X0 null | killed | survived |
|---|---|---|---|
| `fd1e3f6c` | `218 checks, 0 failed` | 17 | X4b, X7, X13, X14, X17, X20, X22 |
| `37cffb09` | `225 checks, 0 failed` | 24 | none |

At `37cffb09`, each of the seven fails a behavioural check, not only a source-text precondition:

- X4b, X7, X13, X14, X20 and X22 fail `every alternative's inputs and near-misses classify as the table needs (production gh_transient)`;
- X17 fails `a 502 followed by a second stderr line, then an answer, is approved`.

**Null controls for the table's preconditions**, each in a scratch worktree of `37cffb09`, with `bash tools/pr/app_approve.sh --self-test`:

| perturbation | result |
|---|---|
| none | `225 checks, 0 failed` |
| a table-less alternative added: `5??\|429)` -> `5??\|429\|418)` | `225 checks, 2 failed`: `FAIL (the table keys exactly the alternatives ...)` and `FAIL (nine alternatives ...) (got '10', want '9')` |
| the 403 key's refused row deleted | `225 checks, 1 failed`: `FAIL (and every alternative holds both a transient input and a refused near-miss) (got '1', want '0')` |

## Null control

All runs are `bash tools/pr/app_approve.sh --self-test`:

| tree | result | rc |
|---|---|---|
| `fd1e3f6c` | `218 checks, 0 failed` | 0 |
| `37cffb09` | `225 checks, 0 failed` | 0 |

The brief's controls at the head:

- **One transient failure, then an answer, approves**:
  - the comments, 429 and secondary-403 arms make exactly 2 calls;
  - the pull-request arms (`r502`, `rhint`) make 3, because the pre-POST re-read is the third.
- **No retry on a refusal.** A 404, a permission 403, a 401, a 422 or an empty stderr refuses `after exactly 1 call` with no `sleep`. A readable wrong head, and a readable answer with no verdict, each refuse after 1 read.
- **Four transient failures spend the budget** (`rspent`). Five transient lines are queued, and the read stops after exactly 4 calls with `sleep 5 sleep 15 sleep 45`. The fifth line stays queued, and the refusal names the fourth with `(after 4 attempts)`. The queue census proves every queued line transient.
- **The budget's last read can still succeed** (`rlast`).

`sleep` is a logging stub on the self-test's PATH.

## Figures

- **The alternatives' enumeration rule**, re-derivable from the source:

  `sed -n '/^gh_transient() {/,/^}/p' tools/pr/app_approve.sh | grep -v '^ *#' | grep -oE "^ +[^ ()]+\)|(sed|grep) -[a-zA-Z]+ '[^']*'" | sed -E "s/^ +//; s/\)$//; s/^[a-z]+ -[a-zA-Z]+ '(.*)'$/\1/" | tr '|' '\n'`

  It prints 8 lines. With `default`, the fall-through no rule matches, that makes 9 alternatives. The self-test runs the same pipeline as `ALTS` and asserts both the set and the count. Rows per alternative, counted by `sed -n "/^cat > \"\$W\/alts\" <<'ALT'/,/^ALT$/p" tools/pr/app_approve.sh | sed '1d;$d' | cut -f1,2 | sort | uniq -c`:

  | alternative | transient rows | refused rows |
  |---|---|---|
  | `s/^gh: (.*\()?HTTP ([0-9]{3})\)?$/\2/p` | 6 | 5 |
  | `5??` | 3 | 1 |
  | `429` | 1 | 2 |
  | `403` | 1 | 1 |
  | `secondary rate limit` | 1 | 4 |
  | `?*` | 1 | 5 |
  | `^Get "https?://[^"]*": ` | 2 | 4 |
  | `^error connecting to ` | 1 | 2 |
  | `default` | 1 | 2 |

  That is 43 rows in all. Each row's class is asserted against the production `gh_transient`, and the two precondition checks would fail on a missing class (the null controls above).
- **The sweep's mutant total** is the number of rule applications the harness header lists over the region, from `READ_TRIES=` to `gh_read`'s closing `}`. `--list` enumerates them: 89 from the seven loop rules and 30 from the eight classifier rules.
- **The scoped gate**: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, and `scope.run` names `tests/entities.py`.
- **`tests/entities.py`** (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 tests/entities.py`) prints `1 of 2382 ENTITY CHECKS FAILED` at `37cffb09`, and the same at the merge base `07fcbee2` from a detached worktree.
  - The one failure is the same check at both: `the template arm turns the acceptance red ... (and the real template keeps it green)`.
  - The cause is that `node tools/policy/policy_lint.mjs` exits 1 on main itself. At `07fcbee2` it prints `ERROR [budgets] tools/audit/briefs/orchestrator.md: about 4515 tokens across its lines exceeds its cap of 4513 tokens`.
  - This diff touches no policy file. See `## Red checks`.
- **The `run_always` lines**, each with `PYTHONPATH=tests/hastub` under `/opt/hpo/venv-ci`, rc=0:
  - `tests/closure.py selftest`: `ALL 124 closure shrink pins PASSED`
  - `tests/layout.py`: `layout self-test: ok`
  - `tests/harness_headers.py`: `ALL 109 HARNESS HEADER CHECKS PASSED`
  - `tests/env_drift.py --claims-only 07fcbee2ed9e38e71d8ca497e1b2470b16baf09f`: `claims hygiene: ... ok`
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, rc=0.
- `node tools/policy/policy_lint.mjs --budgets`: rc=0.
- `python3 tools/audit/archscore/score.py --diff 07fcbee2e HEAD`: `Architecture score: dS +0.0000 NULL`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `CI PREDICT: no closures or fast red predicted against 07fcbee2ed9e`.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `tmp_paths: 0 refused, 0 stale allow entries at HEAD`.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>` exits 1 at `37cffb09`, printing `PRE-PR: 37cffb09c1bffa3a35af13ba9bee3f7c7f6445a1 000110000001000000000000000`.
  - `pr-body` is clean: `node tools/policy/policy_lint.mjs --pr-body <body>` gives `PR-BODY: 0 error(s)`.
  - Three steps refuse: `policy_lint`, `mutants` (`the entry point exited 1 on the corpus as it stands`) and `field coverage` (`1 capped file(s) already red unperturbed`). The same command with the same body, in a detached worktree of `07fcbee2`, prints the same three refusals. They are `main`'s `policy_lint` red, not this diff's (`## Red checks`).
  - The `push order` WARN is expected: the head goes to `handoff/r10-fly-gh-read-retry`, not the pull request.
- `git diff --quiet 07fcbee2e...HEAD -- VERSION 'custom_components/*/manifest.json' RELEASE_NOTES.md tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt && echo NONE-TOUCHED` prints `NONE-TOUCHED`.
- **The class's seams in this file.** Two rules enumerate them:
  - **The GitHub calls outside the self-test**: `awk '/^# --self-test: .gh./{exit} /(gh api|gh_read [a-z]|curl -|git fetch)/ && !/^ *#/' tools/pr/app_approve.sh`. It returns 10 lines, unchanged from the reviewed head, each dispositioned below.
  - **The branches inside the retry path, classifier included**: the sweep above, with 0 survivors.

  | seam | disposition |
  |---|---|
  | `gh api` inside `gh_read` | this diff; every branch swept |
  | `gh_read js` in `check_pr` (called twice) | closed in this diff |
  | `gh_read comments` | closed in this diff |
  | `gh_read owners` | closed in this diff |
  | `gh_read files` | closed in this diff |
  | `curl -X DELETE .../installation/token` | a write, never retried; it only warns on failure |
  | `curl -X POST .../access_tokens` | the mint, a write, never retried |
  | `curl -X POST .../reviews` | a write, never retried; `post502` pins it |
  | `curl .../repos/$repo/installation` | a distinct seam, already in the group's roster `carry` (item 0e5922c7) |
  | `git fetch ... refs/pull/$pr/head` | the same distinct seam, the same carry |

## Red checks

From the check-runs API (`gh api repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs`), per commit, read at 2026-10-22T03:19Z:

- **`d42bda80`**: `nightly-status` and `pr-contract` failed; 18 runs were cancelled by the push of `e4b3e01a`.
- **`e4b3e01a`**: `nightly-status` failed, and `pr-contract` failed twice (jobs 119527655690 and 119538432191).
- **`6e4d2b5c`**: `nightly-status` failed, and `pr-contract` failed twice (jobs 119605965880 and 119606114810). `closures` was still `in_progress`, started 02:47:51Z.
- **`f84fa6b2`, `0f2fa660`, `1063eb3a`, `14eda530`**: no check runs.
- **`fd1e3f6c`, `21307f6f`, `37cffb09`**: not yet on the pull request, so not run.

The two red checks:

- **`pr-contract`** fails `BAD-DEST` on round 2's `Carry: R10-FLY-GH-READ-RETRY` items.
  - The cause: CI runs `carry_audit.py check` against `main`'s roster, and this fly-in group exists only on `handoff/audit-r10-roster`.
  - The cheaper detector is the same command without `--roster-ref`. It takes about a second, and round 2's body was checked only with `--roster-ref`.
  - This body carries nothing to a group missing from `main`'s roster. Both `carry_audit` runs below report 0 bad.
- **`nightly-status`** grades `main`'s nightly lanes, and this diff touches nothing it reads. Carry: dismissed: grades main's nightly lanes, not this branch

**Predicted, not this diff's.** `main` at the merge base `07fcbee2` is itself red on `policy-docs`, `fast (3.14)`, `instrument-self-tests` and `env-matrix`. That is `gh api .../commits/07fcbee2ed9e.../check-runs`, pages 1 and 2. The local cause of the `policy-docs` and `entities` red is in `## Figures`: `policy_lint.mjs` exits 1 on a 2-token overrun of `orchestrator.md`'s `files_tokens` cap (4515 > 4513), and it reproduces at the merge base. A red on these checks at `37cffb09` is `main`'s until it reproduces off the base. Carry: dismissed: red on main's own push at the merge base, the orchestrator's on main

## Forward-carry

```
# roster_edit append-carry R10-FLY-GH-READ-RETRY, once #2588 unfreezes the roster; read it back with brief_lint.mjs
From #2589 (PR 1): PR 2 and PR 3 of this group owe PR 1's proof, both for the retry loop and for the classifier that feeds it:
(a) a spent-budget fixture whose queued failures are all transient, with one more queued than the budget, so only the budget can stop it;
(b) a census sending every fixture line through the production classifier;
(c) every alternative of the classifier, derived from its source by a written rule rather than listed by hand, pinned from both sides by an input it must retry and a near-miss it must refuse, with the derived set and both-classes-per-key asserted as preconditions;
(d) a rule-generated sweep of the retry loop AND the classifier (alternatives, anchors, quantifiers, glob narrowing, phrase words, grep/sed flags, tail/head, and which copy of stderr is classified), in which a mutant killed only by a source-text precondition counts as surviving.
Control: dev/audit/harnesses/r10_gh_read_retry_mutants.py at fd1e3f6c gives 17 survivors and at 37cffb09 gives 0. A hand-picked mutant list missed exactly the budget branch in round 1 and the classifier's branches in round 2.
```

- The roster brief asks for `Retry-After` to be honoured. `gh api` exposes response headers only on stdout, under `--include`, which mixes them into the paginated JSON this script parses. The fixed 5/15/45 s budget stands, as `app_push.sh`'s does. Carry: dismissed: gh exposes no Retry-After header without mixing headers into paginated stdout

## Friction

none
