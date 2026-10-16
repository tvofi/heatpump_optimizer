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

**Round 2: the class the review found open, closed in this diff.**
- **`tools/audit/seat/prune_refs.py`** writes `archive/<branch>` tags through `gh api repos/{repo}/git/refs`, which are permanent names built from branches it does not fix. Its `plan()` now refuses, before anything is written, any plan whose archive tag would name the host, and the refusal does not echo the name. It is registered `guarded`.
- **`--check`'s site rule** now also sees:
  - a `gh api` ref write: `git/refs` or `git/tags` with a field (`-f`, `-F`, `--field`, `--input`) or a POST, PATCH or PUT method, or a `createRef`/`updateRef` mutation;
  - `git` spelled through a variable (`"$GIT"`, `$GIT`, `${GIT}`), but not `$GIT_DIR`.

  A `gh api` ref read or DELETE is not a site. `grep()`'s prefilter widens to match. The registry reads 16 files, 9 of them guarded.
- **The guard judges text URL-decoded as well as raw,** so `%2FUsers%2F<name>` is refused.
- **The guard judges identities.** With `--commits`, it judges the author and committer email of every commit the push publishes for the first time. A private-use domain (`.local`, `.localdomain`, `.lan`, `.internal`, `.localhost`, `.home.arpa`), or this host's own name in short or full form, is `host-email`. A public domain passes, so every noreply address does.
- **One owner for what spells a home directory.** `ref_privacy.py` now owns `HOME_DIR`, `PUBLIC_ACCOUNTS`, `CLOUD_ACCOUNT` and `CLOUD_ROOTS`, and `tmp_paths.py` imports them for its `home-abs` class, its `cloud` rule and its ledger `MACHINE` pattern. The two still answer different questions over the one grammar. Here, a public account's home publishes nothing. There, any home is a machine dependency of a tracked script, bar the cloud image's two fixed roots. `ref_privacy.py --check` imports `tmp_paths.py` for `scope()` and `tmp_paths.py` imports `ref_privacy.py`; the cycle is benign because neither import runs the other's code at module level.
- **The review's survivors:**
  - **stamp.py:** the title guard is factored into `title_refusal()`. stamp's own `--self-test` now pins it with three checks: a planted title is refused, an ordinary title passes, and `main()` refuses through it before rule 1. This replaces the out-of-tree probe.
  - **bus.sh:** gains a `push-verdict` arm. A blocked verdict whose first line names a host path is refused and `review/7` does not move; the same verdict with a clean tail proposes. The `true ||` bypass (M14) is now killed.
  - **The site rule's Python-call arm (M29) is kept, not deleted.** It is the only arm that matches `merge_train.py`'s `g(wt, "push", ...)`, which has no `git` word. The review's mutant survived only because the file is registered through its other site. A plant only this arm matches now kills it.
  - **M13 (the orchestrator-scratch guard in `wt_sync.sh`) survives, justified.** That push's ref (`wip-sync/orchestrator-scratch`) and message (`wip-sync orchestrator scratch <date>`) are constants, so no input reaches the guard to be refused. It stays as the file's contract, so a future edit that composes either value is judged.
  - **M16 (`push.sh` without `--commits`) survives, justified.** push.sh is the retired author path (decision 0011). Its commit half is the same CLI that `app_push.sh` drives, which its own arm pins (M25 killed). The branch half is pinned by `--check`.
- **Out of scope by the owner's ruling:** file contents (the 77 `wip-sync` trees and 125 files on main). The 9 main commits that already carry a host-email identity are published history; the guard judges only what a push publishes for the first time.

## Head

24bae248548fbce945241cabc85466145df18b11. Merge base: 7215e39df7a122a319be0f6ab2d3e49853325b21.

The chain, oldest first, with each merge's direction stated by its parents:
- 20b642bb3 is the fix.
- 6e951709d merges origin/main into it.
- 29091251a takes `--check`'s file scope from `tmp_paths.py`.
- 1e522a71b, the orchestrator's, merges origin/main 12cf1764d into 29091251a.
- ad400657b, on 1e522a71b, fixes the CI red below.
- 639797353, the orchestrator's, merges ad400657b into 1e522a71b.
- 6f1a0f0e9 is the delivery row.
- 9d7beec3b merges origin/main 25afc1c77 into 6f1a0f0e9. This was the round-1 review head.
- **101a57725 is round 2:** the items above, as one commit on 9d7beec3b.
- **24bae2485 merges origin/main 7215e39df into 101a57725.** Main touched `tests/closure.py`, `tests/closures.json` (merged as a set by the ledger driver) and `tools/audit/seat/INSTRUMENTS.md`, plus three files outside this diff: `merge_train.py`, `queue_pre_flight.py` and `train.sh`. `merge_train.py` is a registered pusher. Its sites are still the branch delete and the self-test stub, so its `republishes` disposition holds.

Every figure below was taken at 24bae2485 unless it names another SHA.

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


**Round 2.** `mutate2.py` (scratch, one-off) commits each mutant, runs its checks and resets. All 11 below are red:
- **R1, the prune_refs guard neutered:** FAIL `refuses an archive tag naming a host path, without echoing it`.
- **R2, the gh api write arm dropped:**
  - FAIL `a gh api ref write is a site: -f, -F, -X PATCH, a createRef mutation (round 2)`;
  - `--check` REFUSE `prune_refs.py: registered in PUSHERS but holds no push site`.
- **R3, the `$GIT` arm dropped:** FAIL `git spelled through a variable is a site, and $GIT_DIR is not (round 2)`.
- **R4, the decoded text not judged:** FAIL `a URL-escaped home path is refused, judged decoded (round 2)`.
- **R5, `host-email` never returned:** three FAILs, the identity arms and the CLI arm.
- **R6, `published()` drops the emails:** FAIL `the guard CLI refuses an unpushed commit whose author email names a machine, exit 3`.
- **R7, `main()` bypasses `title_refusal`:** `stamp.py --self-test` FAIL `title: main refuses through title_refusal before rule 1`.
- **R8, `title_refusal` returns None:** FAIL `title: a title naming a host path is refused (#2310)`.
- **R9, the bus guard bypassed with `true ||`:** `bus.sh --self-test` FAIL `push-verdict refuses a first line naming a host path, and review/7 does not move (#2310)`.
- **R10, the Python-call site arm dropped:** FAIL `a Python wrapper call with no git word is a site (the g(...) arm alone: merge_train.py's shape)`.
- **R11, `HOME_DIR` without `/home`:** `tmp_paths.py --self-test` FAIL `refused: /home/user outside the cloud checkout`. This shows that tmp_paths.py's grammar is now this module's.

R12 was an explicit fail-closed branch for a malformed `git log` record. It survived, because git never writes such a record, so I deleted the branch. A malformed record still raises, which exits non-zero and refuses the push.

**The review's own driver**, its `evidence/scripts/mutate.py` copied out of its scripts directory, was run at 101a57725 in a detached worktree. The copy was needed because a sibling `enum.py` in that directory shadows the stdlib under a plain `python3`.
- **Killed:** 26 of its 30 mutants, now including M10, M14 and M29.
- **Survived:** M13 and M16, justified above.
- **M12 and M17 no longer apply** (SETUP-FAIL), because their lines moved:
  - M12's guard is now `title_refusal`, covered by R7 and R8, and its M15 is killed.
  - M17's `Users-` arm, restated on the new text, is FAIL `the old wt_sync slug of a scratch path is refused`.

## Null control

- **The clean name and message pass.** `ref_privacy.py --self-test` holds a null arm for every refusal: a clean ref and message, a clean `body_push` topic, the same branch one commit earlier, `/home/runner` and `/home/user`, `exampleusers` as a non-word, and `PR #4242` as a non-uid.
- **The guard does not over-fire on the live record.** `leaks()` was run with this host's identity over the last 3000 commit messages on origin/main and over the tip message of every verdict, review and handoff-body ref fetched (533 messages). Every class read 0 on both sets. A planted ref in the old-slug shape built from this host's identity is refused (`True`).
- **The stamp title guard.** `stamp.py --title "ordinary title" --dry-run` passes the title guard and stops at rule 1 (`HEAD ... is not origin/main`). A title naming `/Users/exampleuser/y` stops at `rule title`.

- **Round 2, the null arms:** a clean archive tag still plans; a clean verdict tail proposes; a noreply identity passes, even when it names the account; a URL escape that decodes to nothing private passes; and a `gh api` ref read or DELETE is not a site.
- **Round 2, the record of main** (all 6221 commits on origin/main at 24bae2485's parent 7215e39df):
  - `email_leaks()` with this host's identity refuses 9 identities. These are the review's 9 `.local` commits.
  - The 5778 commits with a noreply identity are refused 0 times.
  - URL-decoding changes the verdict on 0 of the 6221 messages.
## Figures

Run at 24bae2485 with the seat venv's python3, except where a line names another SHA:

- `python3 -I tools/audit/seat/ref_privacy.py --self-test`: `ref_privacy self-test: 45 checks, 0 failed`. At 101a57725 it also read 45 checks, 0 failed under `TMPDIR=/tmp` and under `TMPDIR=/tmp HOME=/home/runner USER=runner LOGNAME=runner`. It drives `slug()`, `refusal()`, the `guard` CLI over a throwaway repository, `wt_sync.sh` end to end under a planted `HOME`/`USER` and temp root, `body_push.sh`, and the registry over planted lines.
- `python3 -I tools/audit/seat/ref_privacy.py --check`: `16 file(s) with a push site, 9 guarded, 0 refused`. **This is the class rule (fixer.md step 8)**, and every seam it returns is dispositioned below:
  - **guarded:**
    - `tools/audit/seat/wt_sync.sh`
    - `tools/audit/seat/body_push.sh`
    - `tools/audit/seat/bus.sh`
    - `tools/audit/seat/state_docs.py`
    - `tools/audit/seat/roster_edit.py`
    - `tools/pr/app_push.sh`
    - `tools/pr/push.sh`
    - `tools/release/stamp.py`
    - `tools/audit/seat/prune_refs.py` (round 2)
  - **republishes a name the remote already holds, under a constant message:**
    - `tools/pr/merge_main_bot.py`: a PR's own branch, `SUBJECT`;
    - `tools/audit/seat/merge_train.py`: deletes merged branches; its other site, the `g(...)` call, is the self-test's stub;
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
  - `python3 tools/audit/seat/prune_refs.py --self-test`: `SELF-TEST PASS (24 checks)`;
  - `bash tools/pr/app_push.sh --self-test`: 127 checks, 0 failed;
  - `bash tools/pr/push.sh --self-test`: 77 passed, 0 failed;
  - `bash tools/audit/seat/bus.sh --self-test`: 63 checks, 0 failed;
  - `python3 tools/release/stamp.py --self-test`: `RESULT stamp_self_test=pass`.
- **Scoped gate.** `python3 tests/closure.py select --diff 7215e39df` prints `MODE: FULL`, because `tests/closure.py` changes the gate itself. The scripts this diff reaches were run locally:
  - `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2329 ENTITY CHECKS PASSED`, rc 0;
  - `python3 tests/closure.py selftest`: `ALL 115 closure shrink pins PASSED`;
  - `PYTHONPATH=tests/hastub python3 tests/doc_claims.py`: `ALL 169 checks PASSED` (at 6e951709d);
  - `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s)`.

  The rest is CI's. The `closures` job checks the hand-added entities.py entry, which is a Python lane recorded by audit hook.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. No budget moved.
- **No host identity in this diff.** `leaks()` with this host's identity over `git diff 7215e39df...HEAD`, this round's commit messages and this body finds 0 lines with the home-directory, account-name or uid class. A planted line carrying the host's name is flagged (`True`).

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
