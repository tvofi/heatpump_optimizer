R10-REF-PRIVACY: a ref name or commit message an instrument pushes never names the host, and a new pusher cannot skip the check.

Closes #2310.

`tools/audit/seat/wt_sync.sh` built `wip-sync/<slug>` from the worktree's absolute path and stripped only a `$HOME/` prefix. A worktree under a session temp root was outside `$HOME`, and that root's own name spells the home path with `/` turned into `-`. So the ref name and the snapshot message carried the account name and the uid. The owner's ruling is that this never recurs. This PR adds one owner for the concern, `tools/audit/seat/ref_privacy.py`, in three parts:

- **`slug(path, roots)`.** A path under a named root becomes `<name>-<rest>`; `wt_sync.sh` names the main checkout `repo`. Any other path becomes `ext-<leaf>-<8 hex of sha256(realpath)>`. If the candidate itself would leak, it falls back to `ext-<hash>`, so no input yields a leaking slug. Each run of characters outside `[A-Za-z0-9_]` becomes one `-`, so the result is always a valid ref component.
- **`refusal(ref, messages)` and the `guard` CLI.** These refuse a ref name or commit message that carries any of: the home directory, an account name as a whole word, `claude-<uid>`, any `tmp/claude-<digits>` temp root, or a host path (`/Users/<x>`, `/home/<x>`, `/var/folders/`, `Users-<x>`). A ref name with an unpublishable character is refused too. The refusal names the class and where it was found, never the matched text. `--commits <rev>` adds the message of every commit under `<rev>` that no remote-tracking ref already holds: the ones the push publishes for the first time. The CI runner's and cloud image's fixed accounts (`root`, `runner`, `user`) are not judged.
- **`--check`, a standing registry.** Every tracked file under `tools/`, `.claude/workflows/` and `.github/workflows/` with a push site must be in `PUSHERS`. Each entry is either `guarded`, in which case the file must call the guard, or carries the reason it composes nothing a host could leak into. The check refuses an unregistered pusher, a `guarded` entry that calls no guard, and a stale entry. `governance.yml` runs `--self-test` and `--check` beside `tmp_paths.py`.

The guard is wired before the push in all eight pushers that compose a ref or message from a value they do not fix themselves:
- `wt_sync.sh`: both pushes, with the slug from `slug()`;
- `body_push.sh`;
- `bus.sh` (`append_commit`);
- `state_docs.py`;
- `roster_edit.py`: before anything is written;
- `app_push.sh`: the branch and every newly published commit, before anything is minted;
- `push.sh`;
- `stamp.py`: its `--title`, before anything is written.

**Item 4 (`tmp_paths.py`) is declined, on soundness.** `tmp_paths.py` judges literal path spellings one line at a time. The defect was a value computed on one line and pushed from another. A spelling rule would pin this instance and miss the class (fixer.md 17, #1874). The property is now owned at the one point where it matters, the push, for every input, and `--check` makes a pusher that skips it a red check.

**Alternatives considered:**
- **A git `pre-push` hook.** `wt_sync.sh` pushes with `--no-verify`, and a hook is not installed per clone, so it is not where every push passes.
- **A wrapper replacing `git push`.** It rewrites the argv that `stamp.py` and `app_push.sh` self-tests pin, for no added coverage.

**Classification.** The module is read by `tests/entities.py` through `state_docs.py`, so it leaves the `tools/audit/` INERT prefix in `tests/closure.py`'s `INERT_EXCEPT`, and it joins entities.py's recorded closure in `tests/closures.json` (the R9-RO-14 route). Code-owned paths in this diff: `.github/workflows/governance.yml`, `tests/closure.py`, `tools/release/stamp.py`.

## Head

ad400657b07b5f9a506800e821d39107cee4a573. Merge base: 8087e8576d99c2e1e74cb85e4c4206861d610ccf.

- 20b642bb3 is the fix.
- 6e951709d merges origin/main. Of the files this PR touches, main changed only `tests/closures.json`, merged as a set by the ledger driver. `git diff --quiet 20b642bb3 HEAD -- <every other file this PR touches>` exits 0 at 6e951709d, so the mutation proof, which ran on 20b642bb3's tree, describes that head's code. 29091251a then changes only `scope()` in `ref_privacy.py`, which no mutant touches.
- The merge also brought main's rewrite of `tools/pr/merge_main_bot.py`, a registered pusher that this PR does not touch. Its push still carries the constant `SUBJECT` (`ci: merge main`) onto the PR's own branch, so its `republishes` disposition holds.
- 29091251a makes `--check`'s file scope `tmp_paths.py`'s `scope()` (narrowed to the three pushing trees), which removes a workflow-path grammar written twice that the agreement lane refused (`AGREEMENT ok` after). `--check` returns the same 15 files, and the self-test still passes.
- 1e522a71b is the orchestrator's merge of origin/main into 29091251a: delivery rows and the roster only.
- ad400657b fixes the CI red below. It changes only the wt_sync arm of `ref_privacy.py --self-test`: the planted worktree, and one new precondition check.
- Every check below was re-run at 6e951709d after that merge. `--self-test`, `--check`, `tmp_paths.py --check` and the agreement lane were re-run at 29091251a, and `--self-test` again at ad400657b.

## Mutation proof

A scratch probe (`mutate.py`, one-off, not in the tree) committed each mutant, ran its checks, and reset after each. The script is a one-off probe, so it stays in scratch. Every mutant went red:

- **M1, the old slug** `${w#$HOME/}` restored in `wt_sync.sh`: `--self-test` FAIL `wt_sync pushed a snapshot of the dirty scratch worktree`. The guard, still present, refused `account-name, host-path in the ref name`, so nothing was pushed.
- **M2, `wt_sync.sh`'s guard deleted:** FAIL `the worktree whose unpushed commit names its path is refused, not pushed` (2 refs).
- **M3, `refusal()` returns None:** FAIL `the old wt_sync slug of a scratch path is refused`, `a planted leaking ref name is refused` and two more.
- **M4, the slug fallback deleted:** FAIL `a leaf carrying the account name falls back to ext-<hash>`, `a leaf named after the temp root falls back too`, `--root naming the home directory still yields no leak`.
- **M5, the account-name predicate deleted:** FAIL `the account name is judged as a word, not a substring` and two more.
- **M6, `body_push.sh`'s guard deleted:**
  - FAIL `body_push refuses a topic naming a host path, and pushes nothing`;
  - `--check` REFUSE `tools/audit/seat/body_push.sh: registered guarded but calls no ref_privacy guard`.
- **M7, `state_docs.py`'s guard deleted:** `state_docs.py --self-test` FAIL `a message naming a host path refuses and pushes nothing`.
- **M8, `roster_edit.py`'s guard deleted:** FAIL `a branch naming a host path refuses`, `and pushes nothing`.
- **M9, `app_push.sh`'s guard deleted:**
  - FAIL `REFUSE: a commit message naming a host path (#2310)`, `naming the reason`, `and nothing was minted or pushed`;
  - `--check` REFUSE for `tools/pr/app_push.sh`.
- **M10 to M12, the guard deleted from `bus.sh`, `push.sh` or `stamp.py`:** `--check` REFUSE `<file>: registered guarded but calls no ref_privacy guard`. These three are pinned by the registry only. No behavioural arm drives them, so a guard kept by name but bypassed in their flow would pass.

**Failing first.** The new self-test was run against the unfixed `wt_sync.sh`, and its two wt_sync assertions were red:
- `no wip-sync ref name or message it pushed leaks the planted host` refused `account-name, uid, host-path in the ref name`;
- `the worktree whose unpushed commit names its path is refused` (2 refs pushed).

## Null control

- **The clean name and message pass.** `ref_privacy.py --self-test` holds a null arm for every refusal: a clean ref and message, a clean `body_push` topic, the same branch one commit earlier, `/home/runner` and `/home/user`, `exampleusers` as a non-word, and `PR #4242` as a non-uid.
- **The guard does not over-fire on the live record.** `leaks()` was run with this host's identity over the last 3000 commit messages on origin/main and over the tip message of every verdict, review and handoff-body ref fetched (533 messages). Every class read 0 on both sets. A planted ref in the old-slug shape built from this host's identity is refused (`True`).
- **The stamp title guard.** `stamp.py --title "ordinary title" --dry-run` passes the title guard and stops at rule 1 (`HEAD ... is not origin/main`). A title naming `/Users/exampleuser/y` stops at `rule title`.

## Figures

Run at 6e951709d, and the `ref_privacy.py`, `tmp_paths.py` and agreement lines again at 29091251a, with the seat venv's python3:

- `python3 -I tools/audit/seat/ref_privacy.py --self-test`: at ad400657b, `ref_privacy self-test: 34 checks, 0 failed` under each of three shapes: macOS `TMPDIR`; `TMPDIR=/tmp`; and `TMPDIR=/tmp HOME=/home/runner USER=runner LOGNAME=runner`. It drives `slug()`, `refusal()`, the `guard` CLI over a throwaway repository, `wt_sync.sh` end to end under a planted `HOME`/`USER` and temp root, `body_push.sh`, and the registry over planted lines.
- `python3 -I tools/audit/seat/ref_privacy.py --check`: `15 file(s) with a push site, 8 guarded, 0 refused`. **This is the class rule (fixer.md step 8)**, and every seam it returns is dispositioned below:
  - **guarded:**
    - `tools/audit/seat/wt_sync.sh`
    - `tools/audit/seat/body_push.sh`
    - `tools/audit/seat/bus.sh`
    - `tools/audit/seat/state_docs.py`
    - `tools/audit/seat/roster_edit.py`
    - `tools/pr/app_push.sh`
    - `tools/pr/push.sh`
    - `tools/release/stamp.py`
  - **republishes a name the remote already holds, under a constant message:**
    - `tools/pr/merge_main_bot.py`: a PR's own branch, `SUBJECT`;
    - `tools/audit/seat/merge_train.py`: deletes merged branches; its other site is the self-test's stub;
    - `.github/workflows/tests.yml`: six sites, all on a runner, all with constant `ci: ...` messages, onto the PR branch, `record/autofix` or `main`.
  - **fixture:**
    - `tools/pr/app_approve.sh`
    - `tools/audit/seat/r9_rc_bus_fetchhead.sh`
    - `tools/policy/fragments_sync.mjs`: a lint string.
  - **prompt:** `.claude/workflows/audit-find.js`, whose refs come from round and box numbers.
- `git grep -nE '\$HOME|\$\{HOME|\$USER|\$\{USER|LOGNAME|\$PWD|\$\(pwd\)|&& pwd\)|Path\.home|expanduser|getcwd|getuser|environ[^ ]*(HOME|USER)' -- <the 15 PUSHERS files>` gives the host-derived values inside the pushers. Every hit is dispositioned, and none reaches a ref name or commit message:
  - **Instrument locations:** `$(cd ... && pwd)` resolving a script or worktree directory in `wt_sync.sh`, `bus.sh`, `app_push.sh`, `push.sh`, `app_approve.sh` and `r9_rc_bus_fetchhead.sh`. `wt_sync.sh`'s `R` is the root `slug()` strips, and its `S` feeds file content only.
  - **Identity and key paths:** `$HOME/.zcode` in `bus.sh`, `app_push.sh` and `app_approve.sh`; `expanduser` of the deploy key in `stamp.py`; `~/.local/state/hpo` in `merge_train.py`.
  - **Others:** `$PWD` in a fixture git shim (`bus.sh`, `r9_rc_bus_fetchhead.sh`), `os.getcwd()` in `roster_edit.py`'s self-test, and the Playwright cache in `tests.yml`.
  - **The one hit that did reach a ref,** `${w#$HOME/}` in `wt_sync.sh`, is gone.
- **The finder's measurement.** `git ls-remote origin`, judged by `refusal()` with this host's identity (2026-10-15T23:25:18Z):
  - 2331 lines, 77 of them `wip-sync/` refs;
  - 0 refused for any identity or path class;
  - 2 refused as `unpublishable`, which are `ls-remote`'s peeled-tag lines (`^{}`), not refs.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: 0 refused. The planted paths are built at run time from `/Users/exampleuser`, never spelled.
- `python3 -I tests/throwaway_git.py --check`: 0 refused.
- **Pushers' own self-tests:**
  - `python3 tools/audit/seat/state_docs.py --self-test`: all checks passed;
  - `python3 tools/audit/seat/roster_edit.py --self-test`: 47 checks, 0 failed;
  - `bash tools/pr/app_push.sh --self-test`: 127 checks, 0 failed;
  - `bash tools/pr/push.sh --self-test`: 77 passed, 0 failed;
  - `bash tools/audit/seat/bus.sh --self-test`: 61 checks, 0 failed;
  - `python3 tools/release/stamp.py --self-test`: `RESULT stamp_self_test=pass`.
- **Scoped gate.** `python3 tests/closure.py select --diff 8087e8576` prints `MODE: FULL`, because `tests/closure.py` changes the gate itself. The scripts this diff reaches were run locally:
  - `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2325 ENTITY CHECKS PASSED`, rc 0;
  - `python3 tests/closure.py selftest`: `ALL 115 closure shrink pins PASSED`;
  - `PYTHONPATH=tests/hastub python3 tests/doc_claims.py`: `ALL 169 checks PASSED`;
  - `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s)`.

  The rest is CI's. The `closures` job checks the hand-added entities.py entry, which is a Python lane recorded by audit hook.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. No budget moved.
- **No host identity in this diff.** `leaks()` with this host's identity over `git diff 8087e8576...HEAD` finds 0 lines with the home-directory, account-name or uid class. A planted line carrying the host's name is flagged (`True`).

## Red checks

- **`instrument-self-tests` on #2316 at 1e522a71b.** The log printed `ref_privacy self-test: 33 checks, 1 failed`, with `FAIL the worktree whose unpushed commit names its path is refused, not pushed: 2 ref(s)`.
  - **Cause.** The planted commit message named a worktree under the temp root, so it was a leak only where that root is a host path. On macOS `TMPDIR` is a per-user `/var/folders/...`, which is the `host-path` class. On the Linux runner it is `/tmp/...`, which is no class. So wt_sync's guard rightly passed it, and the assertion was wrong, not the guard.
  - **Fix (ad400657b).** The worktree now lives under the planted home, so the message carries `/Users/exampleuser` and the planted home directory on every host. A new check, `the planted message is itself a leak under the planted identity (the plant's precondition)`, asserts that the plant leaks before the push is judged, so the arm cannot pass vacuously on any host. The arm is not weakened: with `wt_sync.sh`'s guard line deleted (`grep -vF`), it is red under both temp shapes, `2 ref(s)`.
  - **Cheaper detector.** Run the self-test locally under a Linux-shaped environment: `TMPDIR=/tmp HOME=/home/runner USER=runner LOGNAME=runner <venv python3> -I tools/audit/seat/ref_privacy.py --self-test`. `TMPDIR=/tmp` alone reproduces this red on the Mac at 29091251a (`33 checks, 1 failed`), and its absence would have caught it before the handoff. Its standing cost is one more self-test run, 1.9 s wall here. The venv interpreter is called directly because the seat shim resolves its venv under `$HOME`.
  - **Countermeasure, not built.** The countermeasure is for a planted value to leak by construction and to carry a precondition check, which this arm now does. A second local run under the Linux shape is a seat habit rather than a check, and CI already runs the Linux shape on every PR. So the residual cost of this class is one CI round-trip, and no gate is added for it.

## Forward-carry

none

## Friction

- fixer-step-18: cost: the shared `.git/info/exclude` carries a `seat/` pattern. It ignores every new file under `tools/audit/seat/`, so `git add -A` dropped `ref_privacy.py` from the first commit with no message. The file needed `git add -f`, and the next seat adding a seat instrument will hit the same silence.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
