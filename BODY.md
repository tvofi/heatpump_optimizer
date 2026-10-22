R10-FLY-GH-READ-RETRY, PR 1 of 2: `tools/pr/app_approve.sh`'s GitHub reads retry with a bounded backoff, and only on failures that a later read can ride out.

Train 8 stopped on `app_approve: REFUSE: could not read pull request #2547` after a long CI wait. That was one `gh api` call with no retry, and its stderr was not kept, so nothing recorded what kind of failure it was. The roster brief counts this as the third instance of the class "one unretried GitHub read kills an instrument".

What changes, in `tools/pr/app_approve.sh`:

- **`gh_read <var> <gh api args...>`** is the one entry for the four reads: the pull request (read twice by `check_pr`), the comments (`--paginate`), `.github/CODEOWNERS` at `ref=main`, and the changed files (`--paginate`). It sets `<var>` to the answer. On a refusal it returns 1 with gh's stderr in `GH_ERR`, and every `die` at those sites names that error.
- **`gh_transient <stderr>`** classifies a failure from gh's stderr as it came. The deciding line is the last whole status line, `gh: <message> (HTTP NNN)` or `gh: HTTP NNN`, kept whole as `<code> <line>`. These are retried:
  - a 5xx or 429 status;
  - a 403 whose own status line holds `secondary rate limit`, in any case;
  - with no status line, a transport line anywhere in stderr that starts with Go's `Get "http(s)://...": ` or gh's `error connecting to `.

  Everything else refuses after its one call.
- **The budget is `app_push.sh`'s read-back rule**: 4 reads, settling `READ_SLEEP * 3^(n-1)`, so 5/15/45 s, each settle printed. A spent budget refuses with the last error and `(after 4 attempts)`.
- **A wrong answer is never retried**: the callers judge a completed read after `gh_read` returns 0. **Writes are never retried**: the mint, the review POST and the revoke stay single `curl` calls.
- **The comments' python parse** keeps its own refusal, reworded to `could not parse the comments`.
- **`tools/audit/seat/INSTRUMENTS.md`**: the `app_approve.sh` entry states the rule.
- **`dev/audit/harnesses/r10_gh_read_retry_mutants.py`** runs every rule-generated one-line mutant of the retry path against the self-test. The region runs from `READ_TRIES=` to `gh_read`'s closing `}`. A mutant killed only by the self-test's source-text preconditions reads SURVIVED.

**Which copy of stderr the secondary-limit phrase is read from** is a design choice, pinned from both sides. The phrase is read on the deciding status line alone. The alternatives lose:

- **All of stderr** retries a permission 403 because a later hint line mentions the phrase (`gh: Resource not accessible by integration (HTTP 403)` then `see the secondary rate limit docs`). It also retries a line holding the phrase followed by a separate 403 status line.
- **Stderr's last line** loses the phrase whenever gh adds a hint line after the status line. The `rhint` arm shows gh can add such a line after a 502.

The deciding status line is the line the status code itself comes from, so a 403's class and its code come from one response line. Four rows under the self-test's `403` key pin it, each through the production `gh_transient`:

- The phrase on a status line followed by a hint line classifies transient. This row kills reading stderr's last line, the review's F13.
- A permission 403 followed by a hint line naming the phrase classifies refuse. This row kills both whole stderr (F13's converse) and the last line.
- The phrase on its own line, followed by a separate 403 status line, classifies refuse. This row kills whole stderr.
- The single-line permission 403 classifies refuse (an existing row).

**`grep -qi`, not `-qiw`** (the review's F14), is a design choice and now a row. The phrase is matched as a substring, so an inflected `secondary rate limits` on a 403 status line still rescues it. The row `gh: Request blocked by secondary rate limits (HTTP 403)` classifies transient, and `-qiw` fails it.

**A transport line counts on any line of stderr.** The row `A new release of gh is available: ...` then `Get "https://...": EOF` classifies transient. gh prints its update notice on stderr.

**The sweep gains a `copy` rule**, for which line a pattern reads. For every `printf '%s\n' "$V" |` that feeds a sed or grep in the region, it generates:

- ` | tail -1` inserted after `"$V"`;
- ` | head -1` inserted after `"$V"`;
- `"$V"` swapped for each other such operand in the region (`"$1"` <-> `"$status"`).

At the reviewed head the rule generates the review's F13, which survives there (`## Mutation proof`). At this head, its two mutants on the phrase grep are equivalent by construction: `status` is one line, because `| tail -1` assigns it. They are listed in the harness's `EQUIVALENT` table with that reason.

Alternatives, and why each lost (fixer.md step 17):

- **Read the phrase on all of stderr**, the reviewed head's behaviour. It retries a permission 403 on unrelated text.
- **Read the phrase on stderr's last line** (`| tail -1`). It refuses a secondary-limit 403 whenever gh adds a hint line.
- **A second sed or grep to pull out the status line.** One sed now yields both the code and the line (`\2 &`), and `${status%% *}` reads the code. A second pattern would add an alternative the table must key, with no change in behaviour.
- **Factor a shared helper with `app_push.sh`.** Its reads go through `curl -f`, which reports every status of 400 and over as exit 22, so its classifier works on a different signal. Sharing the settle loop needs a new sourced file, a closure classification and an `app_push.sh` edit, all outside this PR's scope. The rule is shared instead.
- **Retry on any non-zero exit.** That retries a 404 and a 401, so a refusal reads as slow success.
- **Honour `Retry-After`.** `gh api` exposes headers only on stdout under `--include`, mixed into the paginated JSON this script parses.
- **Hand-pick the classifier's mutants.** A hand list missed the budget branch in round 1, the classifier's branches in round 2, and the stderr-copy branch in round 3. The rules regenerate the list from the code.

Architecture score: `score.py --diff` prints `dS +0.0000 NULL`. No ratchet row moves and no budget is raised.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01HQPACZGUngPBgCXbgwvG9m

## Head

`a457acaf4ad3ddf1c3195e5d3fa1c6aced0d1ff4`. It merges `origin/main` at `b787c7d45951243a05b6522437b60a01288f0dfd` into `9b9770b34a7bbeaa64abb805b445bfb497474659`. That merge base was `origin/main`'s tip when re-read at 2026-10-22T07:08:30Z.

The branch's commits since the reviewed head, oldest first:

- `9b9770b34a7bbeaa64abb805b445bfb497474659`: the 403 phrase read on the deciding status line, the new rows, and the sweep's `copy` rule. Its parent is `74a18df941939cd87c11280ec216531148015b46`, the reviewed head.
- `a457acaf4ad3ddf1c3195e5d3fa1c6aced0d1ff4`: the merge of `origin/main` at `b787c7d4`, which carries #2588's merge. It changes neither `tools/pr/app_approve.sh` nor the harness: `git diff --quiet 9b9770b3 HEAD -- tools/pr/app_approve.sh dev/audit/harnesses/r10_gh_read_retry_mutants.py && echo UNCHANGED` prints `UNCHANGED`.

`origin/main` moved after this head was pushed. At 2026-10-22T08:08:48Z it is `c61659318691d8f11085453534a434f3025876b1`, which adds #2577, #2585, #2591 and #2596 (46 files, among them `tools/pr/prepr.sh`, `tools/pr/ci_predict.py` and `tests/closures.json`). `git merge-tree --write-tree origin/main HEAD` exits 0, with `tests/closures.json`'s `inert_reads` merged as a set by its ledger driver. No figure below was taken against that tip.

The other end is `74a18df9`, the reviewed head. Every figure below was taken at `a457acaf` unless its row names `74a18df9`.

## Mutation proof

**The sweep at both ends.** The command is `python3 dev/audit/harnesses/r10_gh_read_retry_mutants.py`. At `74a18df9` it ran in a scratch worktree of that commit, with this round's harness copied in. The harness's `EQUIVALENT` table there was adjusted to that tree's text: the `local code` entry instead of `local status`, and no `PHRASE` entries. Without that change, the harness's stale-entry check refuses the run.

| tree | self-test | mutants | killed | equivalent | survivors | rc |
|---|---|---|---|---|---|---|
| `74a18df9` (reviewed head) | 225 checks | 125 | 112 | 10 | 3 | 1 |
| `a457acaf` (this round) | 225 checks | 128 | 116 | 12 | 0 | 0 |

M0, the unmutated tree, is `NULL-OK` at both ends.

The three survivors at `74a18df9` all come from the `copy` rule:

- M52, `403) printf '%s\n' "$1" | tail -1 | grep -qi ...`, which is the review's F13;
- M53, the same with `| head -1`;
- M71, `printf '%s\n' "$1" | head -1 | grep -qE '^Get ...|^error connecting to '`.

At `a457acaf` the `copy` rule generates nine mutants:

- M26, M27 and M28 on the status sed (`+tail -1`, `+head -1`, `"$1"` -> `"$status"`): KILLED.
- M53 and M54 on the phrase grep (`+tail -1`, `+head -1` on `"$status"`): EQUIVALENT, because `status` is one line by construction.
- M55, the phrase grep reading `"$1"` (all of stderr, the reviewed head's behaviour): KILLED.
- M72, M73 and M74 on the transport grep: KILLED.

The harness counts a mutant that fails only a source-text precondition as SURVIVED. Each KILLED above therefore failed a behavioural check.

**One sweep reading was not stable.** The same command was run three times on `9b9770b3`'s tree, which holds the same `app_approve.sh` and harness as `a457acaf`. Two runs printed `RESULT mutants=128 killed=116 equivalent=12 survivors=0`. The third, run with `--jobs 6` beside two `entities.py` runs, printed `killed=117 equivalent=11`.

- In that run, M58 (`?*) return 1` -> `return 999`, listed as equivalent because every caller tests only zero against non-zero) read KILLED. One alternatives-table row had misclassified: `(got '1', want '0')`. The output does not name the row.
- It did not reproduce. M58 re-run alone read EQUIVALENT. Thirty self-tests of the M58 mutant, run ten at a time, each printed `225 checks, 0 failed`, and so did thirty of the unmutated tree.
- Its cause is not established. A self-test that misreads one row only under load would be a flake in the table's check. This is stated, not dismissed.

**The review's harnesses, at this head.** These are `evidence/finder-runner.py` (round 2's runner) and `evidence/fresh-mutants-runner.py` (round 3's) from `origin/review/2589`. Each runs as `python3 <runner> <dir>` against a detached worktree. Three targets name the reviewed head's text, so a copy of each runner was edited for this head:

- X6 and F13 name the 403 line's `"$1"` where this head has `"$status"`.
- X13, F10 and the `SED` constant name `\2/p` where this head has `\2 &/p`.

One mutant was added to the copy: F13c, the converse of F13 (`"$status"` -> `"$1"`).

| runner | null | killed | survived |
|---|---|---|---|
| finder's (X1-X22, 24 mutants) | `225 checks, 0 failed` | 24 | none |
| round 3's (F2-F18 and F13c, 18 mutants) | `225 checks, 0 failed` | 18 | none |

The review's block and finding each fail a behavioural check, not a source-text precondition. The check is `every alternative's inputs and near-misses classify as the table needs (production gh_transient)`:

- F13 (the phrase on stderr's last line) fails it with `(got '2', want '0')`.
- F13c (the phrase on all of stderr) fails it with `(got '2', want '0')`.
- F14 (`-qiw`) fails it with `(got '1', want '0')`.

**Hand probes.** Each is a one-line edit of `9b9770b3`'s tree in a scratch worktree, then `bash tools/pr/app_approve.sh --self-test`. `9b9770b3` and `a457acaf` hold the same `tools/pr/app_approve.sh` (`## Head`).

| perturbation | result | the rows that separate it |
|---|---|---|
| none | `225 checks, 0 failed` | |
| `"$status"` -> `"$1"` on the 403 line | `225 checks, 1 failed` | the permission-403-then-phrase row and the phrase-then-403 row, each `classifies transient, want refuse` |
| `"$status"` -> `"$1" \| tail -1` | `225 checks, 1 failed` | the phrase-then-hint row `classifies refuse, want transient`; the permission-403-then-phrase row `classifies transient, want refuse` |
| `grep -qi` -> `grep -qiw` | `225 checks, 1 failed` | `secondary rate limits` `classifies refuse, want transient` |

## Null control

`bash tools/pr/app_approve.sh --self-test` prints `225 checks, 0 failed`, rc=0, at both `74a18df9` and `a457acaf`. This round adds table rows, not checks, so the count is unchanged.

The self-test's arms at this head:

- **One transient failure, then an answer, approves.** The comments, 429 and secondary-403 arms make exactly 2 calls. The pull-request arms (`r502`, `rhint`) make 3, because the pre-POST re-read is the third.
- **No retry on a refusal.** A 404, a permission 403, a 401, a 422 or an empty stderr refuses `after exactly 1 call`, with no `sleep`.
- **Four transient failures spend the budget** (`rspent`). It makes exactly 4 calls, logs `sleep 5 sleep 15 sleep 45`, and refuses with `(after 4 attempts)`. The fifth queued line stays unread.

`sleep` is a logging stub on the self-test's PATH.

## Figures

- **The alternatives' enumeration rule**, re-derivable from the source:

  `sed -n '/^gh_transient() {/,/^}/p' tools/pr/app_approve.sh | grep -v '^ *#' | grep -oE "^ +[^ ()]+\)|(sed|grep) -[a-zA-Z]+ '[^']*'" | sed -E "s/^ +//; s/\)$//; s/^[a-z]+ -[a-zA-Z]+ '(.*)'$/\1/" | tr '|' '\n'`

  It prints 8 lines. Adding `default`, the fall-through no rule matches, gives 9 alternatives. The self-test runs the same pipeline as `ALTS` and asserts both the set and the count.
- **Rows per alternative**, counted by `sed -n "/^cat > \"\$W\/alts\" <<'ALT'/,/^ALT$/p" tools/pr/app_approve.sh | sed '1d;$d' | cut -f1,2 | sort | uniq -c`:

  | alternative | transient rows | refused rows |
  |---|---|---|
  | `s/^gh: (.*\()?HTTP ([0-9]{3})\)?$/\2 &/p` | 6 | 5 |
  | `5??` | 3 | 1 |
  | `429` | 1 | 2 |
  | `403` | 2 | 3 |
  | `secondary rate limit` | 2 | 4 |
  | `?*` | 1 | 5 |
  | `^Get "https?://[^"]*": ` | 3 | 4 |
  | `^error connecting to ` | 1 | 2 |
  | `default` | 1 | 2 |

  The same pipeline ending in `wc -l` instead of `cut ... | uniq -c` prints 48 rows.
- **The sweep's mutant total** is the number of rule applications over the region. `python3 dev/audit/harnesses/r10_gh_read_retry_mutants.py --list` enumerates them. Counted per rule with `--list | awk -F'\t' '{split($3,a," "); print a[1]}' | sort | uniq -c`, the total is 128:
  - 89 from the seven loop rules: `num` 45, `rel` 10, `opnd` 3, `or` 4, `not` 1, `ret` 2, `del` 24;
  - 39 from the nine classifier rules: `alt` 4, `glob` 4, `anch` 5, `quant` 5, `word` 3, `flag` 6, `pipe` 2, `src` 1, `copy` 9.
- **The scoped gate**: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, and `scope.run` names `tests/entities.py`.
- **`tests/entities.py`** (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 tests/entities.py`) prints `ALL 2382 ENTITY CHECKS PASSED`, rc=0, at `a457acaf`. Two runs on `9b9770b3`'s tree disagreed. One, run while eight mutant self-tests ran beside it, printed `1 of 2382 ENTITY CHECKS FAILED`, and its output was not kept, so the failing check is not named. The other, run alone, printed `ALL 2382 ENTITY CHECKS PASSED`.
- **The `run_always` lines**, each with `PYTHONPATH=tests/hastub` under `/opt/hpo/venv-ci`, rc=0:
  - `tests/closure.py selftest`: `ALL 124 closure shrink pins PASSED`
  - `tests/layout.py`: `layout self-test: ok`
  - `tests/harness_headers.py`: `ALL 109 HARNESS HEADER CHECKS PASSED`
  - `tests/env_drift.py --claims-only b787c7d45951243a05b6522437b60a01288f0dfd`: `claims hygiene: b787c7d45951243a05b6522437b60a01288f0dfd ok`
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, rc=0.
- `node tools/policy/policy_lint.mjs --budgets`: rc=0. `node tools/policy/policy_lint.mjs`: rc=0.
- `python3 tools/audit/archscore/score.py --diff b787c7d45 HEAD`: `Architecture score: dS +0.0000 NULL`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `CI PREDICT: no closures or fast red predicted against b787c7d45951 (a data-file read is not seen)`.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `tmp_paths: 0 refused, 0 stale allow entries at HEAD`.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>` prints `PRE-PR: a457acaf4ad3ddf1c3195e5d3fa1c6aced0d1ff4 00000000000000000000000000`, rc=0.
- `git diff --quiet b787c7d45...HEAD -- VERSION 'custom_components/*/manifest.json' RELEASE_NOTES.md tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt && echo NONE-TOUCHED` prints `NONE-TOUCHED`.
- **The carry audit.** Both `python3 tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <body>` and the same command without `--roster-ref` (main's roster) print `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)`, rc=0.
- **The class's seams in this file.** Two rules enumerate them:
  - **The GitHub calls outside the self-test**: `awk '/^# --self-test: .gh./{exit} /(gh api|gh_read [a-z]|curl -|git fetch)/ && !/^ *#/' tools/pr/app_approve.sh`. It returns 10 lines, each dispositioned in the table below.
  - **The branches inside the retry path, classifier included**: the sweep above.

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
  | `git fetch ... refs/pull/$pr/head` | the same distinct seam, in the same carry item |

## Red checks

The check-runs API on `74a18df9` (`gh api 'repos/tvofi/heatpump_optimizer/commits/74a18df941939cd87c11280ec216531148015b46/check-runs?per_page=100'`), read at 2026-10-22T06:25:45Z, gives 32 success, 16 skipped and 1 failure. `9b9770b3` and `a457acaf` are not on the pull request yet, so they have no runs.

- **`nightly-status`** is the one failure. It grades `main`'s nightly lanes, and this diff touches nothing it reads. Carry: dismissed: grades main's nightly lanes, not this branch
- **`main` was red from 2026-10-22 02:52Z to 04:35Z.** `policy_lint.mjs` found `tools/audit/briefs/orchestrator.md` over its token cap. #2595 fixed it on `main`, and its merge `dcf12f490` is in this head's ancestry (`git merge-base --is-ancestor dcf12f490 HEAD && echo ANCESTOR` prints `ANCESTOR`). At this head, `policy_lint.mjs` exits 0, so the red reaches no check here. Carry: dismissed: main's own red, fixed on main by #2595 and merged into this head
- **`pr-contract`** failed `BAD-DEST` on an earlier head. CI checks carries against `main`'s roster, and at that time this fly-in group existed only on `handoff/audit-r10-roster`. The cheaper detector is `carry_audit.py check` without `--roster-ref`, which takes about a second. Both runs are in `## Figures`.

## Forward-carry

- The fenced block below lands in R10-FLY-GH-READ-RETRY's `carry` at the roster unfreeze; the orchestrator applies it and reads it back with `brief_lint.mjs`, and this seat writes no roster, so no roster SHA is named. #2588 has since merged: at `origin/main` `b787c7d4`, `jq` over `dev/programme/rosters/wave-r10-groups.json` shows the group's `carry` with two entries (the fourth-instance note and item 0e5922c7) and not this block. Carry: R10-FLY-GH-READ-RETRY

```
# roster_edit append-carry R10-FLY-GH-READ-RETRY, at the roster unfreeze; read it back with brief_lint.mjs
From #2589 (PR 1): PR 2 and PR 3 of this group owe PR 1's proof, both for the retry loop and for the classifier that feeds it:
(a) a spent-budget fixture whose queued failures are all transient, with one more queued than the budget, so only the budget can stop it;
(b) a census sending every fixture line through the production classifier;
(c) every alternative of the classifier, derived from its source by a written rule rather than listed by hand, pinned from both sides by an input it must retry and a near-miss it must refuse, with the derived set and both-classes-per-key asserted as preconditions;
(d) a rule-generated sweep of the retry loop AND the classifier (alternatives, anchors, quantifiers, glob narrowing, phrase words, grep/sed flags, tail/head), in which a mutant killed only by a source-text precondition counts as surviving;
(e) which copy of the failure text each pattern reads, decided in writing and pinned from both sides by multi-line rows: a rescue phrase is read on the line its status code comes from, never on all of the text and never on its last line. The sweep generates this as a `copy` rule: insert `| tail -1` and `| head -1` before each pattern's operand, and swap the operand for each other one the classifier reads.
Control: dev/audit/harnesses/r10_gh_read_retry_mutants.py at 74a18df9 gives 3 survivors (all `copy`), and at a457acaf gives 0. A hand-picked mutant list missed the budget branch in round 1, the classifier's branches in round 2, and which copy of stderr is classified in round 3.
```

- The roster brief asks for `Retry-After` to be honoured. `gh api` exposes response headers only on stdout, under `--include`, which mixes them into the paginated JSON this script parses. The fixed 5/15/45 s budget stands, as `app_push.sh`'s does. Carry: dismissed: gh exposes no Retry-After header without mixing headers into paginated stdout

## Friction

none
