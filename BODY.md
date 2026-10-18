Delivers the last two arms of #2310 (group R10-REF-PRIVACY), after #2316 landed the ref-name and commit-message guard. Closes #2310.

Three parts, each its own commit range on this branch:

1. **The bus evidence path** (commit `153797cbe`, written earlier in the group and carried here unchanged, then merged with main). `bus.sh confirm` posted `evidence: <absolute state dir>/evidence`, so every verdict comment republished the home path. `ref_privacy.py` now owns the rendering (`home_relative`, CLI `path`): under `$HOME` a path is written `~/<rest>`. `bus.sh` and `tools/audit/seat/merge_pr.sh` post through it; `app_approve.sh`'s evidence gate accepts a `~/` token and resolves it against its own `$HOME` before every existing guard runs on the resolved path (two components, `/proc` `/dev` `/sys`, volume root, non-empty, names the head) — no refusal removed. `tools/pr/gh_comment.py`, which every `app_comment.sh` post and patch passes through, refuses a body naming this host's home, account name, uid or a session temp root (`ref_privacy.body_refusal`) without echoing the text: a reviewer's own `VERDICT.md` is covered too, not only the bus line.
2. **The tracked-content refusal** (new). Nothing refused a tracked file carrying a host path: `ref_privacy.py --check` read push sites only, and `tmp_paths.py` reads scripts, decision records and mutation-ledger lines, not the records under `dev/`. `--check` now also judges every line a diff adds since the merge base with origin/main (`tmp_paths.ledger_base`, its one owner) with the guard's own classes. A line the same diff removes elsewhere is a move and is not charged; main's stock is not charged. On a runner, whose identity is a public account, the host-path and scratch-root shapes judge; on a seat its own home, name and uid join them. A blob holding a NUL byte is judged too (round 2): its NULs are dropped and every other byte kept, so a path in a binary's ASCII or in UTF-16 text is seen; compressed content is not, and `WHAT IT DOES NOT CATCH` names it. `scrub [--write] <file>...` is the remedy the refusal names: it rewrites only this host's spans in place, so line counts and line numbers survive. CI already runs `ref_privacy.py --check` in `instrument-self-tests` (governance.yml, unchanged). Added lines are judged per changed file by line text at the two ends (a line whose text the file did not hold at the base), so no diff grammar is parsed and a reordered line is not charged.
3. **The tracked-file scrub**: `handoff/r10-ref-privacy-scrub` (`0855dad0f`, 128 files) merged, then the residual it left on current main scrubbed with `scrub --write` (9 records), and 31 mutation-ledger reasons the old scrub had turned into `~/hpo-seats/...` rewritten to `<seat-scratch>/...`, which `tmp_paths.py`'s ledger rule refuses as lines a branch adds.

Branch construction (fresh, not a re-cut): reset to `153797cbe`, `git merge origin/main`, `git merge origin/handoff/r10-ref-privacy-scrub` (clean), then this session's commits, then the PR head `ec773d944` (its delivery row) merged in, then `git merge origin/main` again, last at `811df3cf3`.

Owner gate: `dev/governance/roles/nudge.md` is code-owned (`/dev/governance/roles/`) and policy; the scrub rewrites four path spans in it (4 lines, each `<home>/...` to `~/...`) and changes no rule — tvofi's approving review is owed, under mandate 6175172275. `tools/pr/app_approve.sh`, `tools/pr/gh_comment.py` and `tools/audit/seat/merge_pr.sh` are outside the group's file list and not code-owned (`.github/CODEOWNERS`); `tests/closure.py`, `governance.yml` and `stamp.py` are untouched.

## Approval

Owed, not yet given: this diff rewrites four path spans in `dev/governance/roles/nudge.md` (policy, code-owned `/dev/governance/roles/`), a privacy correction that changes no rule. tvofi's approving review at the head is required before merge (`main-protect-checks`'s code-owner rule), sought by the orchestrator under mandate 6175172275.

## Head

1dd29ca8fe4e1b1f0308f124ee66a09a6dde13bf

## Mutation proof

Each production predicate reverted in place on a committed tree, the named self-test re-run, then restored (`git checkout --`; tree clean before and after). The `ref_privacy.py` arms ran at the head; the `bus.sh`, `app_approve.sh` and `gh_comment.py` arms ran at `0c589b6cf`, and none of those three files changed since:

Baseline `ref_privacy.py --self-test`: 64 checks, 0 failed.

- `content_refusals`: `why = leaks(text, ident)` → `why = []`: 5 failed — the scratch-path line, another machine's home, the NUL file, the UTF-16 file, and the null control's count.
- `added_lines`' move rule: `return [... if t.strip() not in removed]` → `return added`: 2 failed — "a line the diff moves from another file is not charged (the null control)" and the count.
- The stock filter (round 2): `... for n, t in enumerate(new, 1) if t.strip() not in was]` → `... for n, t in enumerate(new, 1)]`: 3 failed — "main's stock line in a changed file is not charged (the null control)", the count, and the scrubbed-tree arm.
- Binary content (round 2), the skip restored: `blob_text`'s NUL branch → `return ""`: 3 failed — "a NUL-bearing file adding a host line is refused: binary content is judged (round 2)", the UTF-16 arm, and the count.
- The NUL drop: `if b"\0" in data:` → `if False:`: 2 failed — "and so is UTF-16 text naming one, its NULs dropped" and the count.
- `check()`'s wiring: `base, added, refused = content_check(ref)` → `base, added, refused = None, [], []`. `ref_privacy.py --self-test`: 1 failed — "and check() runs it (a pin by text: check() itself needs the real tree's pushers)". A source pin: `check()` reads the real tree's pushers, so the throwaway repository drives `content_check` and the pin ties `check()` to it.
- `bus.sh` `post_verdict`: `"$(home_rel "$d")"` → `"$d"`. `bus.sh --self-test`: 2 failed — "the posted body cites its evidence directory home-relative (~/), and it names the head (#2310)", "and the posted body carries no home path at all".
- `app_approve.sh`: the `~/` resolution line → `:`. `app_approve.sh --self-test`: 1 failed — "a verdict citing ~/-relative evidence is approved, ~ resolved against $HOME at read time (#2310)".
- `gh_comment.py` `run`: `privacy_check(body)` → `pass`. `gh_comment.py self-test`: 1 failed — `arm_privacy_post_dry_run_refuses_this_hosts_home (the wiring)`.

## Null control

The content arm at the merge base and at the head, over one planted commit `X` = the merge base `811df3cf3` plus `dev/audit/plant.log` holding one line naming a home under another account (built in the shell, never spelled):

- base code (a detached worktree at `811df3cf3`), `python3 -I tools/audit/seat/ref_privacy.py --check --ref X`: rc 0, `0 refused` — the base does not look at content.
- head code, same command: rc 1, `REFUSE dev/audit/plant.log:1: host-path in an added line of a tracked file`.
- the reviewer's P4 replayed on the head: `dev/audit/nul.log` = `bin\0\nran at <another account's /Users home>/w`: rc 1, `REFUSE dev/audit/nul.log:2: host-path` (it passed, rc 0, at round 1's head).
- head code on the merge base itself: rc 0, `0 refused` — the arm does not fire on an unplanted tree.


Within the self-tests every refusal arm has its pass twin: the moved line is not charged; main's stock line kept in a changed file is not charged; a NUL-bearing file naming no host passes; the scrubbed tree's diff is refused nothing; `scrub` leaves another account's home and a public one alone; a `~/` body passes `body_refusal`, as does a quoted other home; a `~/` evidence dir that does not exist is still refused by `app_approve.sh`.

## Figures

Rules, all at the head unless named: the account name is `basename "$HOME"` at run time, never written here; a "file" is one tracked at the ref; B is `git merge-base origin/main HEAD` = `811df3cf3`.

- Files whose bytes carry the account name, case-insensitively, text and binary alike: 128 at B, 0 at the head: `U=$(basename "$HOME"); git grep -al -i "$U" <ref> | wc -l`.
- Files naming this host's session temp root (uid 501): 13 at B, 2 at the head: `git grep -lI -E 'tmp[/-]+claude-501' <ref> | wc -l`. Kept: `tools/pr/gh_comment.py` (`DEFECT_BODY`, the literal #541 defect path the poster's self-test must refuse) and `tools/audit/seat/tmp_paths.py` (its `ALLOW` entry for that same fixture, keyed on the text) — a fixture pair; changing one breaks the other's key.
- Files naming a macOS per-user temp: 5 at B, 1 at the head: `git grep -lI '/var/folders/' <ref> | wc -l`. Kept: `tools/audit/seat/ref_privacy.py`, the grammar's own `_HOST_PATH` pattern.
- Files naming `/Users/<x>` or the dashed `Users-<x>` form at the head: `git grep -lI -E '/Users/[A-Za-z0-9._-]|(^|[^A-Za-z0-9])Users-[A-Za-z0-9._]' HEAD`: `tools/audit/seat/ref_privacy.py` and `tools/audit/seat/tmp_paths.py`, both stock self-test fixtures and grammar text (another account's home, `exampleuser` / `someone` / `me`), kept.
- Kept by rule, not by file: `/home/claude` in 417 files and `tmp/claude-0` in 9 (`git grep -lI '/home/claude' HEAD | wc -l`; `git grep -lI -E 'tmp[/-]+claude-0([^0-9]|$)' HEAD | wc -l`) — round 8–9 evidence from a container sandbox whose fixed account and uid 0 publish no person. Stock, so not charged; a new such line is refused (host-path, scratch-root): a deliberate strictness, since a sandbox path is also a dead path to every other reader.
- sha citations of the 9 newly scrubbed files: 0 — a 10-hex prefix of each file's sha1, git blob id and sha256 at the pre-scrub tree, each `git grep -lI <prefix> HEAD`, all empty. The 128 files of `0855dad0f` were checked the same way by its own body.
- Diff shape: `git diff --stat B HEAD`: 139 files, 1255 insertions, 981 deletions. Files whose added and removed counts differ (`git diff --numstat B HEAD | awk '$1!=$2'`): the four code files, `tools/audit/seat/bus.sh`, `tools/audit/seat/ref_privacy.py`, `tools/pr/app_approve.sh`, `tools/pr/gh_comment.py`, and this PR's own delivery row `dev/programme/delivery/2366.md` — every scrubbed record kept its line count.
- `python3 -I tools/audit/seat/ref_privacy.py --check`: 0 refused, judging every line the branch adds since B (the count is printed on the summary line).
- `python3 -I tools/audit/seat/tmp_paths.py --check`: 0 refused, 0 stale allow entries, ledger lines added since B.
- Self-tests at the head, each `0 failed`: `ref_privacy.py --self-test`, `bus.sh --self-test`, `app_approve.sh --self-test`, `tmp_paths.py --self-test`; `gh_comment.py self-test`: `SELF-TEST PASSED`.
- Ledger: `python3 tests/mutation_table.py --normalize` retires 0 keys and leaves the tree clean (`git status --short | wc -l` 0 after it); `python3 tools/merge/ledger_merge.py --self-test`: all passed. The JSON records rewritten are valid (`json.load`); `prescreen_r4.py` passes `py_compile`.
- Gate scope (`python3 tests/closure.py select --diff B`): `MODE: SCOPED -- 2 script(s) run, 31 scoped out`; `scope.run` names `tests/entities.py` (`ALL 2346 ENTITY CHECKS PASSED`) and `tests/harness_headers.py`.
- `tests/harness_headers.py` (`PYTHONPATH=tests/hastub:custom_components:tests`): `12 of 109 HARNESS HEADER CHECKS FAILED` at `0c589b6cf` and the same 12 at its merge base `bad6f7a51`, run side by side (`grep -i fail` of each log, numbers stripped, `diff` empty): all twelve are `dev/audit/rounds/round4/D7/sysid_estimator_frontier.py`, a file this branch does not touch, hitting the script's 900 s wall limit (rc 124) on a loaded seat machine; a solo run on an earlier head failed 13, the extra one load-dependent the same way. CI's run is the authority.
- Agreement lane (`python3 -I tools/policy/agreement_py.py --out <f>` then `node tools/policy/agreement.mjs --py-json <f>`, `agreement.mjs` byte-identical to origin/main): `AGREEMENT ok`, `divergent=0 unregistered=0 dead=0 refused=0`.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `python3 tests/layout.py`: ok. `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 41 policy file(s)`, fixture tally ok; `--budgets` rc 0. `node tools/policy/brief_lint.mjs`: `TOTAL: 0 error(s) across 47 file(s)`.
- Architecture score: dS +0.0000 NULL (`python3 tools/audit/archscore/score.py --diff 6e5753a4a HEAD` at `fc64fb4e3`; since then `added_lines` was rewritten in place, so CI's `arch-score` is the current figure).

## Red checks

- `wave-script` (run on the PR's first head, `78dbdbda6`): its agreement lane printed `UNREGISTERED "@@ -\\S+ \\+(\\d+)" in tests/mutation_table.py, tools/audit/seat/ref_privacy.py`. A real defect of this diff: `added_lines` parsed the unified-diff hunk header with the same pattern `tests/mutation_table.py` owns, a grammar written twice. Registering it in `tools/policy/agreement.mjs` (the first attempt, `85c6c1c35`) could not work: CI restores the lane's readers from the base, so a branch-side entry is not read. Fixed in `58b81a064` by removing the parse: `added_lines` now compares each changed file's lines by text at the two ends, the entry is withdrawn, and the lane reads `AGREEMENT ok` locally with `agreement.mjs` identical to main. Cheaper detector: `prepr.sh`'s own `agreement lane` step, which refused this before the push and was answered by the registration that CI cannot see. The standing gap is that prepr runs the lane with the branch's registry while CI pins the base's; that difference costs one CI round per registration a branch adds, and I found no case where a branch-side entry is the right fix, so I am naming it here rather than changing prepr.sh, which is outside this group.
- `pr-contract`: `[pr-body] check wave-script is red and ## Red checks does not name it` — a consequence of the red above, answered by this section. No separate detector: it is the detector.

## Forward-carry

none

## Friction

- fixer.md: unenforced: round 1 found the binary skip and an unpinned stock filter; my mutation list mutated only the predicates I had written arms for, so a branch with no arm was never mutated. Answered by mutating every filter in `added_lines` this round.
- gate-scoping.md: contradiction: `prepr.sh`'s agreement lane reads the branch's `agreement.mjs`, CI's restores the base's, so a registration passes locally and refuses in CI (this PR's `wave-script` red).
- defect-root-cause.md: unenforced: the bus evidence arm sat on a `wip-sync/` snapshot ref only (`153797cbe`), reachable from no handoff ref, so a fixer dispatched for the same arm began re-deriving it; the orchestrator caught it by message. `bus.sh orphans` enumerates handoff refs, not wip-sync snapshots.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
