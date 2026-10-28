Fix review: blocked 74a18df941939cd87c11280ec216531148015b46 mutant-survives: the 403 branch's phrase grep reads all of gh's stderr and no row pins which copy, so inserting tail -1 passes all 225 checks; the round-2 carry is still not in the roster

bus-nonce: 6e8a9955f9546912dd2c5fb1a571a1e5

Round: third review (round 3), of the cloud fixer round on the round-2 block at `6e4d2b5c`. The next block owes `fixer.md`'s re-cut, not a repair.

How I worked:
- I reviewed from detached worktrees at `74a18df941939cd87c11280ec216531148015b46` (the head) and at `fd1e3f6c4` (the body's other end: round 2's tests with main merged).
- The merge base is `1602f934261958321b6e7dfaceb749188705c7b5`, which is origin/main's tip.
- `git diff <merge base>...origin/main -- dev/governance/roles/` is empty, so the contract I followed is current.
- The finder's harness is round 2's mutant runner and list (`origin/review/2589:evidence/my-mutants-runner.py`), copied as `ev/finder-runner.py`.
- The fixer's authored delta since `6e4d2b5c` is `21307f6fc` and `37cffb09c`. Both change only the self-test, the gh stub and the sweep harness. Production `gh_transient` and `gh_read` are byte-identical to `6e4d2b5c` (`git diff 6e4d2b5c 74a18df9 -- tools/pr/app_approve.sh` touches only the stub and the self-test).

## Block

1. **mutant-survives: the 403 branch classifies on every line of stderr, and nothing pins that.**
   - **The survivor (F13).** `403) printf '%s\n' "$1" | grep -qi 'secondary rate limit'` -> `403) printf '%s\n' "$1" | tail -1 | grep -qi 'secondary rate limit'` survives with `225 checks, 0 failed`, rc=0 (`ev/fresh-mutants.txt`; the runner is `ev/fresh-mutants-runner.py`, and the worktree was restored clean).
   - **Why it survives.** The status code comes from the last whole status line (`tail -1`, pinned by the two-status rows). The phrase that rescues a 403, though, is searched across all of stderr. Every 403 row in the table is a single line, so which copy the phrase is read from is unpinned.
   - **What it changes** (`ev/f13-probe.txt`):
     - `gh: You have exceeded a secondary rate limit.\ngh: Forbidden (HTTP 403)` classifies transient at the head and refuse under F13.
     - `gh: Resource not accessible by integration (HTTP 403)\nsee secondary rate limit docs` classifies **transient** at the head. That is a permission 403 retried because a later line mentions the phrase.
   - **Why this blocks.** It is the case the body's own forward-carry (d) names: "which copy of stderr is classified". It also sits beside the body's stated design that the phrase "rescues a 403 only, and only as the whole phrase". Either reading may be the intended one, but whichever it is, one row must pin it.
   - **Fix.** Add a two-line 403 row for each class the design chooses, for example a permission 403 followed by a line holding the phrase. Then confirm that F13, and its converse (grep only the status line), are killed by a behavioural check and not only by the table-key precondition.
   - **Sweep gap.** The sweep's `pipe` rule only rewrites an existing `| tail -N`. It never inserts one, so it cannot generate this mutant. The rule set needs a rule for "which line a pattern reads" (insert `| tail -1` before each phrase/transport grep that reads `"$1"`), or the carry's item (d) is unmet for this branch.

2. **carry-missing: not carried to R10-FLY-GH-READ-RETRY (PR 2 and PR 3). Round 2's block 2 is not cleared.**
   - The body's fenced `roster_edit append-carry R10-FLY-GH-READ-RETRY` text is the carry, but it is in the PR body only.
   - At every roster ref, the group's `carry` holds the same two items as at round 2: the fourth-instance note and item 0e5922c7. Neither the census nor the "every alternative ... pinned from both sides" text is there. The refs checked (`ev/roster-carry.txt`):
     - `origin/handoff/audit-r10-roster` at `306a96d5f`
     - #2588's head `ad10fd215`
     - origin/main `1602f934`, which has no such group
   - finding-propagation.md says: "The producing PR does not merge until the carry is in the tree". fix-review.md step 10 blocks one held only in the PR.
   - The body gives the cause: the roster branch is frozen until #2588 merges. That is not the fixer's to remove, so this item is not a repair owed by the fixer.
   - **The remedy is the orchestrator's.** Once #2588 merges, apply the fenced edit and read it back with `brief_lint.mjs`. Add block 1's rule to item (d) when doing so. Then name the roster SHA in the body. A merge verdict cannot be given until that SHA exists.

Round 2's mutant-survives block is otherwise cleared at this head:
- The finder's harness gives 24 killed and 0 survived at `74a18df9`.
- At `fd1e3f6c4` it gives 17 killed and 7 survived, the same seven round 2 named: X4b, X7, X13, X14, X17, X20 and X22.
- Each of the seven now fails a behavioural check, not only a source-text precondition:
  - X4b, X7, X13, X14, X20 and X22 fail `every alternative's inputs and near-misses classify as the table needs (production gh_transient)`.
  - X17 fails `a 502 followed by a second stderr line, then an answer, is approved`.
- Round 2's two findings, X13 and X17, are settled the same way.

## Findings

- F14 (`grep -qi 'secondary rate limit'` -> `grep -qiw`) survives with `225 checks, 0 failed` (`ev/fresh-mutants.txt`). It differs only when the phrase is glued to further letters (`secondary rate limiting`). GitHub's message uses the words whole (`You have exceeded a secondary rate limit.`), so no input gh emits separates the two. Carry: dismissed: -w differs only on a phrase run into further letters, which GitHub's secondary-limit message never has
- Seven fresh mutants are killed only by the table-key precondition, `(the table keys exactly the alternatives gh_transient's source holds)`:
  - F2 (`{3}` -> `{3,}`) and F4 (`[0-9]{3}` -> `[0-9]+`);
  - F5 (`5??` -> `5*`) and F15 (`?*` -> `???`);
  - F8 (`[^"]*` -> `.*`);
  - F11 and F12 (each transport pattern's trailing space dropped).

  By the harness's own rule these would read SURVIVED. They are not in its rule set, though: no rule widens a brace count, a character class, or a trailing literal.

  They are behaviourally equivalent on what gh prints:
  - F5 and F15 are exactly equivalent, because the sed only ever yields three digits.
  - F2 and F4 differ only on a four-or-more-digit status beside a transport line (`ev/edge-probe.txt`).
  - F8 differs only on a quote inside the URL (`Get "https://a" x": EOF`).
  - F11 and F12 differ only on `error connecting tox` or `Get "...":EOF`.

  Carry: dismissed: each differs only on a 4+-digit HTTP status, a quote inside the URL or a missing separator space, none of which gh emits (ev/edge-probe.txt)

## Evidence

- RESULT sweep at head `74a18df9`: `python3 dev/audit/harnesses/r10_gh_read_retry_mutants.py` gives `RESULT mutants=119 killed=109 equivalent=10 survivors=0`, rc=0, M0 `NULL-OK` with 225 checks (`ev/sweep-head-74a18df9.txt`). Re-derived; matches the body's `37cffb09` row.
- RESULT sweep at `fd1e3f6c4`, with this round's harness: `RESULT mutants=119 killed=92 equivalent=10 survivors=17`, rc=1, M0 `NULL-OK` with 218 checks (`ev/sweep-base-fd1e3f6c.txt`). Re-derived. The survivors are M17 M21 M24 M25 M37 M45 M47 M48 M49 M53 M54 M58 M59 M60 M63 M64 M93, exactly the body's list.
- RESULT finder's harness (round 2's runner):
  - Head: X0 `225 checks, 0 failed`; 24 KILLED, 0 SURVIVED (`ev/finder-harness-head-74a18df9.txt`).
  - `fd1e3f6c4`: X0 `218 checks, 0 failed`; 17 KILLED, 7 SURVIVED (`ev/finder-harness-base-fd1e3f6c.txt`).
  - Both re-derived, matching the body's table.
- RESULT fresh mutants (`ev/fresh-mutants.txt`): F0 null `225 checks, 0 failed`.
  - Killed behaviourally: F3 (9 failed), F6 (2), F7 (5), F9 (8), F10 (1), F16 (4), F17 (19), F18 (5).
  - Killed only by the table-key precondition: F2, F4, F5, F8, F11, F12, F15 (see Findings).
  - Survived: F13 (Block 1) and F14 (Findings).
- Null controls for the table's preconditions, at the head (`ev/nullctl.txt`). All re-derived:
  - None: `225 checks, 0 failed`.
  - `5??|429)` -> `5??|429|418)`: `225 checks, 2 failed`, the table-keys check and `(got '10', want '9')`.
  - The 403 key's refused row deleted: `225 checks, 1 failed`, `(got '1', want '0')`.
- Figures re-derived at this head (`ev/figs-alts.txt`, `ev/figures.txt`):
  - The ALTS enumeration rule prints 8 lines (9 with `default`).
  - The per-alternative row counts equal the body's table: 43 rows.
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`, rc=0.
  - `score.py --diff 1602f9342 HEAD`: `Architecture score: dS +0.0000 NULL`.
  - `closure.py select --diff <merge base>`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`
  - `policy_lint.mjs --budgets`: rc=0.
  - `tmp_paths.py --check`: `0 refused, 0 stale allow entries`.
  - `harness_headers.py` (venv-ci): `ALL 109 HARNESS HEADER CHECKS PASSED`.
  - `closure.py selftest`: `ALL 124 closure shrink pins PASSED`.
  - `layout.py`: `layout self-test: ok`.
  - `env_drift.py --claims-only 1602f9342`: `claims hygiene: ... ok`.
  - `ci_predict.py --base origin/main`: `no closures or fast red predicted`.
- Figures that differ at this head. The body took them at `37cffb09` against merge base `07fcbee2`, so they were not re-derived at that tree. At `74a18df9`, which carries #2595's fix of main's `orchestrator.md` cap overrun:
  - `entities.py` (venv-ci) prints `ALL 2382 ENTITY CHECKS PASSED`, where the body had `1 of 2382 ... FAILED` from main's red.
  - `node tools/policy/policy_lint.mjs` prints `TOTAL: 0 error(s)`.
  - `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>` prints `PRE-PR: 74a18df941939cd87c11280ec216531148015b46 00000000000000000000000000`, rc=0 (`ev/prepr-head.txt`).
  - Each of these is consistent with the body's attribution of the earlier red to main.
- Not re-derivable here: the 2667 s train 8 wait, which comes from train logs not in this container.
- Merge: `git merge-tree --write-tree origin/main 74a18df9` gives clean tree `5ea912ab21cf0ed75a29a39245cae50db394058f`, rc=0 (`ev/merge-tree.txt`). No main absorb is owed.
- Version and claim files: `VERSION`, the manifest, the `RELEASE_NOTES.md` heading and both claim files are untouched (`NONE-TOUCHED`, three-dot against the merge base).
- Carry audit over the PR body (`ev/carry-audit-body.txt`): `1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`, rc=0, both with `--roster-ref origin/handoff/audit-r10-roster` and without it (main's roster).
- `## Red checks`: check-runs API on `74a18df9`, read 2026-10-22T05:25Z (`ev/checkruns-head.tsv`):
  - 31 success, 16 skipped, 1 failure, 1 in progress.
  - The failure is `nightly-status` (job 119644921228). It grades main's nightly lanes, and this diff reaches nothing it reads, so it is not this pull request's (fix-review.md step 11). It is not a gate check and does not block.
  - Two `pr-contract` runs concluded success. A third, started 05:24:48Z after the `nightly-status` red, was in progress at the read.
  - `instrument-self-tests` (which runs this self-test), `fast (3.14)`, `coverage`, `typing`, `mutation`, `arch-score`, `budget-raise-gate`, `policy-docs`, `env-matrix`, `browser` and CodeQL passed.
  - The intermediate commits `37cffb09`, `21307f6f`, `fd1e3f6c` and `b21fb4c9` have no check runs (`ev/checkruns-commits.tsv`).
  - Round 2's `pr-contract` BAD-DEST red, on `6e4d2b5c`, is answered in the body's `## Red checks`. That body's carry items now route clean.
- Head: `74a18df941939cd87c11280ec216531148015b46` is the PR head (re-read via the API at 05:25Z) and the head the body's `## Head` names (`ev/HEAD.txt`).
