R10-FLY-GH-READ-RETRY, PR 1 of 2: `tools/pr/app_approve.sh`'s GitHub reads retry with a bounded backoff, and only on failures that a later read can ride out.

Train 8 stopped on `app_approve: REFUSE: could not read pull request #2547` after a long CI wait: one `gh api` call with no retry, stderr not kept. The roster brief counts it as the third instance of "one unretried GitHub read kills an instrument".

What changes, in `tools/pr/app_approve.sh`:

- **`gh_read <var> <gh api args...>`** is the one entry for the four reads (the pull request, read twice by `check_pr`; the comments, `--paginate`; `.github/CODEOWNERS` at `ref=main`; the changed files, `--paginate`). On a refusal it returns 1 with gh's stderr in `GH_ERR`, and every `die` at those sites names it.
- **`gh_transient <stderr>`** classifies a failure from gh's stderr. The deciding line is the last whole status line, `gh: <message> (HTTP NNN)` or `gh: HTTP NNN`, kept whole as `<code> <line>` by one sed (`s/^gh: (.*\()?HTTP ([0-9]{3})\)?$/\2 &/p | tail -1`). Retried:
  - a 5xx or 429 status;
  - a 403 whose own status line holds `secondary rate limit`, in any case (`9b9770b34`: the phrase is read on that line alone, `printf '%s\n' "$status" | grep -qi`);
  - with no status line, a transport line anywhere in stderr starting `Get "http(s)://...": ` or `error connecting to `.

  Everything else refuses after its one call.
- **Budget is `app_push.sh`'s read-back rule**: 4 reads, settling `READ_SLEEP * 3^(n-1)` = 5/15/45 s, each printed; a spent budget refuses with the last error and `(after 4 attempts)`. A wrong answer is never retried (callers judge a completed read). Writes are never retried: the mint, the review POST and the revoke stay single `curl` calls.
- **`tools/audit/seat/INSTRUMENTS.md`** states the rule; **`dev/audit/harnesses/r10_gh_read_retry_mutants.py`** runs every rule-generated one-line mutant of the retry path (region `READ_TRIES=` to `gh_read`'s closing `}`) against the self-test; a mutant killed only by a source-text precondition reads SURVIVED.

**How round 3's block is cleared.** Round 3 blocked on F13: the 403 branch read `printf "$1" | tail -1 | grep`, the last line of stderr, which loses the phrase whenever gh adds a hint line, and the sweep had no rule that could generate it (3 survivors at `74a18df9`). Cleared at `9b9770b34` in two parts: the phrase is read on the deciding status line, whose code and text come from one response line; and the sweep gains a `copy` rule (which copy of stderr each pattern reads). The block's second item, the roster carry, is under `## Forward-carry`.

**Which copy of stderr the phrase is read from is a design choice, pinned from both sides** by four rows under the self-test's `403` key, each through production `gh_transient`: phrase on a status line then a hint line → transient (kills the last-line reading); permission 403 then a hint line naming the phrase → refuse (kills whole stderr and the last line); phrase on its own line then a separate 403 status line → refuse (kills whole stderr); single-line permission 403 → refuse. `grep -qi`, not `-qiw`, is also a design choice and a row: `secondary rate limits` on a 403 status line still rescues it.
A transport line counts on any line of stderr, because gh prints its update notice there (row: `A new release of gh is available: ...` then `Get "https://...": EOF` → transient).

**The `copy` rule**: for every `printf '%s\n' "$V" |` feeding a sed or grep in the region it inserts ` | tail -1`, ` | head -1`, and swaps `"$V"` for each other such operand. Nine mutants. Two (M53, M54: `+tail -1`, `+head -1` on `"$status"` at the phrase grep) are EQUIVALENT because `status` is one line by construction.

Alternatives, and why each lost (fixer.md step 17):

- **Phrase on all of stderr**: retries a permission 403 because a later hint line mentions the phrase.
- **Phrase on stderr's last line**: refuses a secondary-limit 403 whenever gh adds a hint line.
- **A second sed or grep for the status line**: one sed yields code and line; `${status%% *}` reads the code; a second pattern adds an alternative the table must key with no behaviour change.
- **Shared helper with `app_push.sh`**: its reads use `curl -f` (every status ≥400 is exit 22), a different signal; sharing the settle loop needs a new sourced file, a closure classification and an `app_push.sh` edit. The rule is shared instead.
- **Retry on any non-zero exit**: retries a 404 and a 401.
- **Honour `Retry-After`**: `gh api` exposes headers only on stdout under `--include`, mixed into paginated JSON this script parses.
- **Hand-picked classifier mutants**: a hand list missed the budget branch (round 1), the classifier's branches (round 2) and the stderr copy (round 3); the rules regenerate the list.

## Head

`53f24912dee67629b3bc383f91031627c995d520`. `git merge-base origin/main 53f24912dee67629b3bc383f91031627c995d520` is `b787c7d45951243a05b6522437b60a01288f0dfd`. Every figure below was taken at this SHA, in a detached worktree of it, with `origin/main` at `01cf1398a9cfa3dcae5945221afd0c1dae9cf682` (2026-10-22T08:24Z); none is a function of main's tip except where a row says so.

## Mutation proof

One-line edits of the 403 line of `tools/pr/app_approve.sh` at the head, each `bash tools/pr/app_approve.sh --self-test`, file restored after:

| perturbation | result | first failed check |
|---|---|---|
| none (null) | `225 checks, 0 failed` | |
| `"$status"` -> `"$1" \| tail -1` (the F13 shape) | `225 checks, 1 failed` | `every alternative's inputs and near-misses classify as the table needs (production gh_transient)` (got '2', want '0') |
| `"$status"` -> `"$1" \| head -1` | `225 checks, 1 failed` | same check (got '1', want '0') |
| `"$status"` -> `"$1"` (all of stderr) | `225 checks, 1 failed` | same check (got '2', want '0') |
| `grep -qi` -> `grep -qiw` | `225 checks, 1 failed` | same check (got '1', want '0') |

The check is behavioural (it runs production `gh_transient`), not a source-text precondition.

**The sweep**: `python3 dev/audit/harnesses/r10_gh_read_retry_mutants.py --jobs 4` at the head prints `RESULT mutants=128 killed=116 equivalent=12 survivors=0`, rc=0 (same as the review's reading; M0 is the unmutated null). The `copy` rule's M26-M28, M55 and M72-M74 are KILLED; M53 and M54 are EQUIVALENT. At `74a18df9` the round-3 review measured 3 survivors, all `copy` (F13 is M52 there); that run is not repeated here.

**The 12 equivalents** (the harness's `EQUIVALENT` table, each keyed on line text and mutated text): `GH_ERR=""` deleted; `local status` deleted; `?*) return 1` -> `return 2` and `-> return 999`; the mktemp refusal `return 1` -> `2` and `-> 999`; `[ "$_try" -ge "$READ_TRIES" ]` -> `-eq`; `-eq 1` -> `-le 1` on the `(after N attempts)` suffix; `return 1` -> `2` and `-> 999` at the end of `gh_read`'s refusal; and the two `ONELINE` entries, M53 and M54. Reasons are in the table (callers test zero against non-zero only; `_try` starts at 1 and steps by 1; `status` is one line).

## Null control

`bash tools/pr/app_approve.sh --self-test` at the head prints `225 checks, 0 failed`, rc=0; the null row above is the same run. The unmutated sweep baseline M0 is `NULL-OK`. Self-test arms:

- One transient failure, then an answer, approves: the comments, 429 and secondary-403 arms make exactly 2 calls; the pull-request arms (`r502`, `rhint`) make 3 (the pre-POST re-read is the third).
- No retry on a refusal: a 404, a permission 403, a 401, a 422 or an empty stderr refuses after exactly 1 call with no `sleep`.
- Four transient failures spend the budget (`rspent`): exactly 4 calls, `sleep 5 sleep 15 sleep 45`, `(after 4 attempts)`; the fifth queued line stays unread.

`sleep` is a logging stub on the self-test's PATH.

## Figures

- **Self-test**: `bash tools/pr/app_approve.sh --self-test` -> `225 checks, 0 failed`. The review's "48" is the alternatives table's row count below, not this.
- **Alternatives' enumeration rule**: `sed -n '/^gh_transient() {/,/^}/p' tools/pr/app_approve.sh | grep -v '^ *#' | grep -oE "^ +[^ ()]+\)|(sed|grep) -[a-zA-Z]+ '[^']*'" | sed -E "s/^ +//; s/\)$//; s/^[a-z]+ -[a-zA-Z]+ '(.*)'$/\1/" | tr '|' '\n'` prints 8 lines; with the fall-through `default`, 9 alternatives. The self-test runs the same pipeline as `ALTS` and asserts set and count.
- **Rows per alternative**: `sed -n "/^cat > \"\$W\/alts\" <<'ALT'/,/^ALT$/p" tools/pr/app_approve.sh | sed '1d;$d' | cut -f1,2 | sort | uniq -c`; `... | wc -l` prints 48.

  | alternative | transient | refused |
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
- **Sweep total by rule**: `python3 dev/audit/harnesses/r10_gh_read_retry_mutants.py --list | awk -F'\t' '{split($3,a," "); print a[1]}' | sort | uniq -c` prints 129 entries: `null` 1 (M0) and 128 mutants. The 128 are 89 from the loop rules (`num` 45, `rel` 10, `opnd` 3, `or` 4, `not` 1, `ret` 2, `del` 24) and 39 from the classifier rules (`alt` 4, `glob` 4, `anch` 5, `quant` 5, `word` 3, `flag` 6, `pipe` 2, `src` 1, `copy` 9). That is nine classifier rules, `copy` the ninth.
- **Scope**: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `git diff --quiet b787c7d45...HEAD -- VERSION 'custom_components/*/manifest.json' RELEASE_NOTES.md tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt && echo NONE-TOUCHED` prints `NONE-TOUCHED`.
- **Not re-taken here, cited**: `score.py --diff` and `entities.py` are cited from CI's green `arch-score`, `closures` and `fast (3.14)` at the head (`## Red checks`); the no-budget-raise claim follows from `STRUCTURE RATCHET PASSED` with no `*_budgets.json` in `git diff --name-only $(git merge-base origin/main HEAD)...HEAD` (that diff names five files: the harness, `dev/programme/delivery/2589.md`, `tests/closures.json`, `INSTRUMENTS.md`, `app_approve.sh`).
- **The class's seams**: `awk '/^# --self-test: .gh./{exit} /(gh api|gh_read [a-z]|curl -|git fetch)/ && !/^ *#/' tools/pr/app_approve.sh` returns 10 lines:

  | seam | disposition |
  |---|---|
  | `gh api` inside `gh_read` | this diff; every branch swept |
  | `gh_read js` in `check_pr` (twice), `comments`, `owners`, `files` | closed in this diff |
  | `curl -X DELETE .../installation/token` | write, never retried; warns only |
  | `curl -X POST .../access_tokens` | the mint, a write, never retried |
  | `curl -X POST .../reviews` | a write, never retried; `post502` pins it |
  | `curl .../repos/$repo/installation` and `git fetch ... refs/pull/$pr/head` | one distinct seam, already in the group's roster carry (item 0e5922c7) |

## Red checks

`GET repos/tvofi/heatpump_optimizer/commits/53f24912dee67629b3bc383f91031627c995d520/check-runs` (one call, via the PR's check-runs read): `total_count` 49 — 33 success, 16 skipped, 0 failure, 0 other. Zero red at the head.

Red in the branch's history (`b787c7d45951243a05b6522437b60a01288f0dfd..53f24912dee67629b3bc383f91031627c995d520` is 15 commits; the branch's own commits since `git merge-base origin/main HEAD` are those plus main's earlier merges):

- The check-runs of `74a18df9`, `9b9770b3`, `841b2fea` and `37cffb09` were re-read by the review at the head and show no non-success run. I did not re-read the earlier heads (`d42bda80f` through `21307f6fc`), to spare the API.
- Earlier bodies recorded two reds, both answered: `pr-contract` `BAD-DEST` on an early head (CI checks carries against main's roster, where this group existed only on `handoff/audit-r10-roster`). Cheaper detector: `carry_audit.py check` run without `--roster-ref`, about a second, already in `## Figures`' carry audit; and `nightly-status` at `74a18df9` (grades main's nightly lanes; this diff touches nothing it reads; the latest read shows it success). Main's own red 02:52Z-04:35Z (`policy_lint.mjs` token cap, fixed by #2595, `dcf12f490` is in the head's ancestry) reached no check here. Carry: dismissed: main's own red and a main-graded check, neither this branch's

## Forward-carry

- The roster carry for PR 2/3 was written at `5620151813e03a5916c375554dd57c977f6d8097` (`roster_edit append-carry R10-FLY-GH-READ-RETRY`). It is on `origin/handoff/audit-r10-roster` (`git merge-base --is-ancestor 5620151813e03a5916c375554dd57c977f6d8097 origin/handoff/audit-r10-roster && echo ON-ROSTER-BRANCH` prints `ON-ROSTER-BRANCH`) and on main: #2598 merged it, `git merge-base --is-ancestor 5620151813e03a5916c375554dd57c977f6d8097 origin/main && echo ON-MAIN-ANCESTRY` prints `ON-MAIN-ANCESTRY`, and `origin/main:dev/programme/rosters/wave-r10-groups.json` holds three carry items for the group (`jq`, group `R10-FLY-GH-READ-RETRY`, `.carry | length` = 3), the third being "From #2589 (PR 1): PR 2 and PR 3 of this group owe PR 1's proof". Its item (e), which copy of the failure text each pattern reads, is what the `copy` rule implements. Carry: R10-FLY-GH-READ-RETRY
- The roster brief asks for `Retry-After` to be honoured; `gh api` exposes headers only on stdout under `--include`, mixed into the paginated JSON this script parses; the fixed 5/15/45 s budget stands, as `app_push.sh`'s does. Carry: dismissed: gh exposes no Retry-After header without mixing headers into paginated stdout
- Review finding G7 (`\2 &/p` -> `\2 \1/p` in the status sed) is killed only by the table-key precondition and reads SURVIVED by the harness's own rule; it is behaviourally equivalent, since `\1` holds the whole message the phrase can occur in. Carry: dismissed: \1 holds the whole message the phrase can occur in, so the 403 branch classifies identically on every gh status line

## Friction

none

## Lint results

`node tools/policy/policy_lint.mjs --pr-body <body> --head 53f24912dee67629b3bc383f91031627c995d520 --title <title>` prints `PR-BODY: 0 error(s)`, rc=0; its red-history row reads 15 commits and names `nightly-status`, answered under `## Red checks`. `python3 tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <body>` prints `CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)`, rc=0.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01FnkqgMwEtyePst4dyJYpKz

