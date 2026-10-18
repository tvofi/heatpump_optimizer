Delivers the last two arms of #2310 (group R10-REF-PRIVACY), after #2316 landed the ref-name and commit-message guard. Closes #2310.

Three parts, each its own commit range on this branch:

1. **The bus evidence path** (commit `153797cbe`, written earlier in the group and carried here unchanged, then merged with main). `bus.sh confirm` posted `evidence: <absolute state dir>/evidence`, so every verdict comment republished the home path. `ref_privacy.py` now owns the rendering (`home_relative`, CLI `path`): under `$HOME` a path is written `~/<rest>`. `bus.sh` and `tools/audit/seat/merge_pr.sh` post through it; `app_approve.sh`'s evidence gate accepts a `~/` token and resolves it against its own `$HOME` before every existing guard runs on the resolved path (two components, `/proc` `/dev` `/sys`, volume root, non-empty, names the head) — no refusal removed. `tools/pr/gh_comment.py`, which every `app_comment.sh` post and patch passes through, refuses a body naming this host's home, account name, uid or a session temp root (`ref_privacy.body_refusal`) without echoing the text: a reviewer's own `VERDICT.md` is covered too, not only the bus line.
2. **The tracked-content refusal** (new). Nothing refused a tracked file carrying a host path: `ref_privacy.py --check` read push sites only, and `tmp_paths.py` reads scripts, decision records and mutation-ledger lines, not the records under `dev/`. `--check` now also judges every line a diff adds since the merge base with origin/main (`tmp_paths.ledger_base`, its one owner) with the guard's own classes. A line the same diff removes elsewhere is a move and is not charged; main's stock is not charged. On a runner, whose identity is a public account, the host-path and scratch-root shapes judge; on a seat its own home, name and uid join them. `scrub [--write] <file>...` is the remedy the refusal names: it rewrites only this host's spans in place, so line counts and line numbers survive. CI already runs `ref_privacy.py --check` in `instrument-self-tests` (governance.yml, unchanged). Its unified-diff hunk-header pattern is the one `tests/mutation_table.py` reads, so it is registered in `tools/policy/agreement.mjs` as `identical` (the agreement lane refused it unregistered).
3. **The tracked-file scrub**: `handoff/r10-ref-privacy-scrub` (`0855dad0f`, 128 files) merged, then the residual it left on current main scrubbed with `scrub --write` (9 records), and 31 mutation-ledger reasons the old scrub had turned into `~/hpo-seats/...` rewritten to `<seat-scratch>/...`, which `tmp_paths.py`'s ledger rule refuses as lines a branch adds.

Branch construction (fresh, not a re-cut): reset to `153797cbe`, `git merge origin/main`, `git merge origin/handoff/r10-ref-privacy-scrub` (clean), then this session's commits, then `git merge origin/main` again, last at `60c315a09`.

Owner gate: `dev/governance/roles/nudge.md` is code-owned (`/dev/governance/roles/`) and policy; the scrub rewrites two path spans in it and changes no rule — tvofi's approving review is owed, under mandate 6175172275. `tools/pr/app_approve.sh`, `tools/pr/gh_comment.py`, `tools/audit/seat/merge_pr.sh` and `tools/policy/agreement.mjs` are outside the group's file list and not code-owned (`.github/CODEOWNERS`); `tests/closure.py`, `governance.yml` and `stamp.py` are untouched.

## Approval

Owed, not yet given: this diff rewrites two path spans in `dev/governance/roles/nudge.md` (policy, code-owned `/dev/governance/roles/`), a privacy correction that changes no rule. tvofi's approving review at the head is required before merge (`main-protect-checks`'s code-owner rule), sought by the orchestrator under mandate 6175172275.

## Head

5424c293013d3f3f494d6c4aa6e16f1b596caa35

## Mutation proof

Each production predicate reverted in place on a committed tree (at `0c589b6cf`; the head adds only main's record merges and one registry line in `agreement.mjs`, and every self-test below re-ran green at the head), the named self-test re-run, then restored (`git checkout --`; tree clean before and after):

- `content_refusals`: `why = leaks(text, ident)` → `why = []`. `ref_privacy.py --self-test`: 3 failed — "a diff adding a line naming the host's scratch path is refused, by line and class", "and one naming another machine's home, by the host-path shape a runner can see", "a line the diff moves from another file is not charged (the null control)".
- `check()`'s wiring: `base, added, refused = content_check(ref)` → `base, added, refused = None, [], []`. `ref_privacy.py --self-test`: 1 failed — "and check() runs it (a pin by text: check() itself needs the real tree's pushers)". A source pin: `check()` reads the real tree's pushers, so the throwaway repository drives `content_check` and the pin ties `check()` to it.
- `bus.sh` `post_verdict`: `"$(home_rel "$d")"` → `"$d"`. `bus.sh --self-test`: 2 failed — "the posted body cites its evidence directory home-relative (~/), and it names the head (#2310)", "and the posted body carries no home path at all".
- `app_approve.sh`: the `~/` resolution line → `:`. `app_approve.sh --self-test`: 1 failed — "a verdict citing ~/-relative evidence is approved, ~ resolved against $HOME at read time (#2310)".
- `gh_comment.py` `run`: `privacy_check(body)` → `pass`. `gh_comment.py self-test`: 1 failed — `arm_privacy_post_dry_run_refuses_this_hosts_home (the wiring)`.

## Null control

The content arm at the merge base and at the head, over one planted commit `X` = the merge base `6e5753a4a` plus `dev/audit/plant.log` holding one line naming a home under another account (built in the shell, never spelled):

- base code (a detached worktree at `6e5753a4a`), `python3 -I tools/audit/seat/ref_privacy.py --check --ref X`: rc 0, `0 refused` — the base does not look at content.
- head code, same command: rc 1, `REFUSE dev/audit/plant.log:1: host-path in an added line of a tracked file`.
- head code on the merge base itself: rc 0, `0 refused` — the arm does not fire on an unplanted tree.

That demonstration ran before the final `git merge origin/main`; the merge changed none of the four production files.

Within the self-tests every refusal arm has its pass twin: the moved line is not charged; the scrubbed tree's diff is refused nothing; `scrub` leaves another account's home and a public one alone; a `~/` body passes `body_refusal`, as does a quoted other home; a `~/` evidence dir that does not exist is still refused by `app_approve.sh`.

## Figures

Rules, all at the head unless named: the account name is `basename "$HOME"` at run time, never written here; a "file" is one tracked at the ref; B is `git merge-base origin/main HEAD` = `60c315a09`.

- Files whose bytes carry the account name, case-insensitively, text and binary alike: 128 at B, 0 at the head: `U=$(basename "$HOME"); git grep -al -i "$U" <ref> | wc -l`.
- Files naming this host's session temp root (uid 501): 13 at B, 2 at the head: `git grep -lI -E 'tmp[/-]+claude-501' <ref> | wc -l`. Kept: `tools/pr/gh_comment.py` (`DEFECT_BODY`, the literal #541 defect path the poster's self-test must refuse) and `tools/audit/seat/tmp_paths.py` (its `ALLOW` entry for that same fixture, keyed on the text) — a fixture pair; changing one breaks the other's key.
- Files naming a macOS per-user temp: 5 at B, 1 at the head: `git grep -lI '/var/folders/' <ref> | wc -l`. Kept: `tools/audit/seat/ref_privacy.py`, the grammar's own `_HOST_PATH` pattern.
- Files naming `/Users/<x>` or the dashed `Users-<x>` form at the head: `git grep -lI -E '/Users/[A-Za-z0-9._-]|(^|[^A-Za-z0-9])Users-[A-Za-z0-9._]' HEAD`: `tools/audit/seat/ref_privacy.py` and `tools/audit/seat/tmp_paths.py`, both stock self-test fixtures and grammar text (another account's home, `exampleuser` / `someone` / `me`), kept.
- Kept by rule, not by file: `/home/claude` in 417 files and `tmp/claude-0` in 9 (`git grep -lI '/home/claude' HEAD | wc -l`; `git grep -lI -E 'tmp[/-]+claude-0([^0-9]|$)' HEAD | wc -l`) — round 8–9 evidence from a container sandbox whose fixed account and uid 0 publish no person. Stock, so not charged; a new such line is refused (host-path, scratch-root): a deliberate strictness, since a sandbox path is also a dead path to every other reader.
- sha citations of the 9 newly scrubbed files: 0 — a 10-hex prefix of each file's sha1, git blob id and sha256 at the pre-scrub tree, each `git grep -lI <prefix> HEAD`, all empty. The 128 files of `0855dad0f` were checked the same way by its own body.
- Diff shape: `git diff --stat B HEAD`: 139 files, 1224 insertions, 981 deletions. Files whose added and removed counts differ (`git diff --numstat B HEAD | awk '$1!=$2'`): exactly the five code files, `tools/audit/seat/bus.sh`, `tools/audit/seat/ref_privacy.py`, `tools/policy/agreement.mjs`, `tools/pr/app_approve.sh`, `tools/pr/gh_comment.py` — every scrubbed record kept its line count.
- `python3 -I tools/audit/seat/ref_privacy.py --check`: 0 refused, judging every line the branch adds since B (the count is printed on the summary line).
- `python3 -I tools/audit/seat/tmp_paths.py --check`: 0 refused, 0 stale allow entries, ledger lines added since B.
- Self-tests at the head, each `0 failed`: `ref_privacy.py --self-test`, `bus.sh --self-test`, `app_approve.sh --self-test`, `tmp_paths.py --self-test`; `gh_comment.py self-test`: `SELF-TEST PASSED`.
- Ledger: `python3 tests/mutation_table.py --normalize` retires 0 keys and leaves the tree clean (`git status --short | wc -l` 0 after it); `python3 tools/merge/ledger_merge.py --self-test`: all passed. The JSON records rewritten are valid (`json.load`); `prescreen_r4.py` passes `py_compile`.
- Gate scope (`python3 tests/closure.py select --diff B`): `MODE: SCOPED -- 2 script(s) run, 31 scoped out`; `scope.run` names `tests/entities.py` (`ALL 2346 ENTITY CHECKS PASSED`) and `tests/harness_headers.py`.
- `tests/harness_headers.py` (`PYTHONPATH=tests/hastub:custom_components:tests`): `12 of 109 HARNESS HEADER CHECKS FAILED` at the head and the same 12 at B, run side by side (`grep -i fail` of each log, numbers stripped, `diff` empty): all twelve are `dev/audit/rounds/round4/D7/sysid_estimator_frontier.py`, a file this branch does not touch, hitting the script's 900 s wall limit (rc 124) on a loaded seat machine; a solo run on an earlier head failed 13, the extra one load-dependent the same way. CI's run is the authority.
- Agreement lane (`python3 -I tools/policy/agreement_py.py --out <f>` then `node tools/policy/agreement.mjs --py-json <f>`): `AGREEMENT ok`, `divergent=0 unregistered=0 dead=0 refused=0`; `--self-test`: 13 of 13 probes held.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `python3 tests/layout.py`: ok. `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 41 policy file(s)`, fixture tally ok; `--budgets` rc 0. `node tools/policy/brief_lint.mjs`: `TOTAL: 0 error(s) across 47 file(s)`.
- Architecture score: dS +0.0000 NULL (`python3 tools/audit/archscore/score.py --diff 6e5753a4a HEAD` at `fc64fb4e3`; after it only main's merges, which touched none of these files, and the one registry line in `agreement.mjs`).

## Red checks

none

## Forward-carry

none

## Friction

- defect-root-cause.md: unenforced: the bus evidence arm sat on a `wip-sync/` snapshot ref only (`153797cbe`), reachable from no handoff ref, so a fixer dispatched for the same arm began re-deriving it; the orchestrator caught it by message. `bus.sh orphans` enumerates handoff refs, not wip-sync snapshots.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
