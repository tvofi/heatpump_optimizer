R10-FLY-CACHE-PROMPTS (size S; owner order tvofi 2026-10-28, "fix cache proposals 1-6 asap"; the prompt-cache gap seat's ranked gaps 1, 4, 6 and side defect 2). Four arms, one pull request:

1. **Gap 1, waits past the 5-minute cache TTL.** Every role's rendered prompt (`cloud_dispatch.py` `_prompt`'s setup line) now says `WAIT_LINE`: "Never wait in one tool call longer than 240 s; poll again instead." The two self-polling watchers a seat waits on, `seat/ci-watch.sh` (`POLL_S=240`, was a literal `sleep 300`) and `seat/proof_watch.py` (`POLL_S = 240.0`, was a `--poll` default of 300), poll at 240 s. `proof_watch.py` now refuses a `--poll` under the 60 s GitHub floor (`POLL_FLOOR_S`), which `fixer.md`'s preamble already attributes to it ("the 60 s API floor is theirs") and which it did not enforce.
2. **Gap 4, the payload echoed into the orchestrator.** A published seat's event is a pointer, not the prompt: `_pointer` renders who the seat is (role, repo, topic or PR, head, nonce) and "Your full brief is PROMPT.md at origin ref dispatch/<role>-<key> (`git fetch origin <ref> && git show FETCH_HEAD:PROMPT.md`); read it first and follow it exactly." `publish_seat` is the one publish path: it renders the whole prompt into PROMPT.md and the pointer into PAYLOAD.json's event, both through `render` before `_publish` (so every render refusal and `ref_privacy.refusal` still holds). `dispatch_group` calls it; the new flag-path `--publish` calls it with `dispatch_ref(role, topic, pr)` = `dispatch/<role>-<topic>`, else `dispatch/<role>-rev-<PR>`. Without `--publish` the flag path is byte-for-byte unchanged (a self-test arm pins it). `--group --publish` refuses (GROUP_FLAGS: the group path always publishes).
3. **Gap 6.** The fixer prompt reads `dev/governance/roles/fixer.md` only; CLAUDE.md is auto-loaded by the harness in the cloud clone.
4. **Side defect, the Stop hook.** `.claude/settings.json`'s Stop command resolves the hook: `$CLAUDE_PROJECT_DIR`'s, else the repository's found from the cwd (`git rev-parse --show-toplevel`), else exits 0, never a missing-file error. `policy_lint --hooks` still reads the script path out of the command (its regex finds `.claude/hooks/stop-selfcheck.sh`) and runs its self-test: `HOOKS ok: 3 wired hook(s)`. **`.claude/settings.json` is not a policy path** (`printf '.claude/settings.json\n' | node tools/policy/policy_lint.mjs --corpus-filter` prints nothing), **but it and `.claude/hooks/` are code-owned by @tvofi** (`.github/CODEOWNERS` lines for `/.claude/hooks/` and `/.claude/settings.json`), so this PR merges on the owner's review.

Alternatives considered: for arm 2, keeping the whole prompt in the event and publishing only on the group path (the status quo) loses the gap; a second, pointer-only renderer beside `render` would duplicate the refusals, so `render` takes `publish_ref` and `publish_seat` renders twice. For arm 4, a wrapper script under `.claude/hooks/` cannot be found from the very directory that lacks it, so the resolution has to live in the command line.

## Head

c9dfba0617d7a50ccd8d6f4f60a7462a59932979, merge base b0b2d7697f8c5baaef2c082d9bf3242b57249e68; origin/main tip 6493ea3625900f8361011e0c8f2a3c66885ce7b1 (2026-10-28T23:59Z), `git merge-tree --write-tree origin/main HEAD` clean, so no merge (fixer.md step 6).

Repair round 1 (review blocked 3d1c405d, `mutation-vacuous`: `ci-watch.sh` `sleep "$POLL_S"`->`sleep 300` survived). The one commit added, c9dfba06, adds a `ci-watch.sh --self-test` arm, "the loop sleeps POLL_S between cycles": one quiet cycle of the real watch loop without `CI_WATCH_ONCE` (the W2 null fixture, fake `gh`), with a stub `sleep` first on PATH that records its argument; the arm reads the first recorded argument and requires it to equal `POLL_S`. A loop that never sleeps leaves the record empty, and the self-test kills the watcher after ~10 s instead of hanging. Alternative considered: a grep for the loop's `sleep "$POLL_S"` line. It lost because it pins the text, not the behaviour, and a reworded call (`sleep ${POLL_S}`) would read as a regression.

## Mutation proof

Failing tests first, each importing or running the production artifact. Before the fix (tests committed, fix absent): `cloud_dispatch.py --self-test` died with `NameError: name 'WAIT_LINE' is not defined` after 14 ok lines; `stop-selfcheck.sh --self-test`: `FAIL WIRED: a project dir without the hook runs the repository's, found from the cwd (got 127, wanted 3)`, `FAIL WIRED: no hook anywhere exits 0, never a missing-file error (got 127, wanted 0)`, 27 passed, 2 failed; `ci-watch.sh --self-test`: `FAIL the poll is inside [60 s, 240 s] (POLL_S=unset)`; `proof_watch.py --self-test`: `NameError: name 'POLL_S' is not defined`.

Mutants at the head, each applied alone and restored (predicates, not tails):

- `dev/audit/harnesses/r10_flow_dispatch_mutants.py` (in tree; extended here): `pointer-ref-dropped` (the ref name dropped from the pointer, the brief's named mutant) failed=4 killed; `pointer-off` failed=4 killed; `publish-ignored` (flag path ignores `--publish`) failed=2 killed; `publish-ref-rev-dropped` failed=2 killed; `wait-line-dropped` failed=1 killed; `claude-md-reread` failed=1 killed; the re-aimed `nonce-altered` failed=4, `topic-to-id` CRASHED, `prompt-wrong` failed=12, `flag-unlisted` failed=2 killed.
- One-off (scratch), `ci-watch.sh` `POLL_S=240`→`300`: `FAIL the poll is inside [60 s, 240 s] (POLL_S=300)`, 15 checks, 1 failed.
- The blocked mutant, `ci-watch.sh` loop `sleep "$POLL_S"`→`sleep 300`: at 3d1c405d (test absent) `ci-watch self-test: 14 checks, 0 failed`, survived; at c9dfba06 `FAIL the loop sleeps POLL_S between cycles (slept 300)`, 15 checks, 1 failed, killed. The loop's `sleep "$POLL_S"` line deleted: survived at 3d1c405d (14 checks, 0 failed), killed at c9dfba06 (`FAIL the loop sleeps POLL_S between cycles (slept never)`, 15 checks, 1 failed).
- `proof_watch.py` `POLL_S = 240.0`→`300.0`: `FAIL the default poll is inside [60 s, 240 s]`; `if a.poll < POLL_FLOOR_S:`→`if False:`: `FAIL --poll 59 is refused at --poll (got (2, False), want (2, True))`.
- `.claude/settings.json` without the `git rev-parse` fallback: `FAIL WIRED: a project dir without the hook runs the repository's, found from the cwd (got 0, wanted 3)`; without `[ -f "$f" ] || exit 0`: `FAIL WIRED: no hook anywhere exits 0, never a missing-file error (got 127, wanted 0)`.

## Null control

`python3 dev/audit/harnesses/r10_flow_dispatch_mutants.py` M0 (unmutated) `failed=0 verdict=null-ok` at the head and at the base. The unmutated `ci-watch.sh` passes the new sleep arm (`ok   the loop sleeps POLL_S between cycles (slept 240)`), the null control for its two kills. The flag path without `--publish` keeps the whole prompt in its event (self-test: "without --publish the flag path is unchanged"). `proof_watch --poll 60` passes the poll guard and is refused at `--head` instead (self-test arm). The Stop command with the hook in `$CLAUDE_PROJECT_DIR` runs it (`WIRED: the project dir's hook runs`, rc 3 from the stub).

## Figures

- `python3 -I tools/audit/seat/cloud_dispatch.py --self-test`: 87 checks, 0 failed at the head.
- `python3 dev/audit/harnesses/r10_flow_dispatch_mutants.py`: `RESULT mutants=33 survived=1` at the head; the survivor is `reviewer-head-off`, which also survives at the base (`... M0 parent-drop head-ignored roster-repo-ignored reviewer-head-off` at b6f6ceca: `RESULT mutants=4 survived=1`), so it is pre-existing, not this diff's (Forward-carry). At the base the full run aborted at `nonce-altered`, whose pattern already matched nothing there (`git show origin/main:tools/audit/seat/cloud_dispatch.py | grep -cF 'pr=pr, topic=topic, nonce=nonce,'` prints 0); this PR re-aims it.
- `bash .claude/hooks/stop-selfcheck.sh --self-test`: 29 passed, 0 failed. `node tools/policy/policy_lint.mjs --hooks`: `HOOKS ok: 3 wired hook(s) exist and pass their own --self-test`.
- `bash tools/audit/seat/ci-watch.sh --self-test`: 15 checks, 0 failed. `python3 tools/audit/seat/proof_watch.py --self-test`: 43 checks, 0 failed.
- Pointer length: the self-test asserts each published event under 600 chars (rule: `len(content) < 600`, for a fixer and a reviewer, flag and group paths).
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`; `scope.run` names `tests/entities.py`, run with `PYTHONPATH=tests/hastub` under `/opt/hpo/venv-ci/bin/python3` (see Friction). `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2467 ENTITY CHECKS PASSED`. `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh`: rc 0 at c9dfba06 (`ci predict`: no red predicted). Every figure in this list was re-taken at c9dfba06.

Class enumeration (fixer.md step 8), rule: `git grep -nEi "sleep +[0-9]{3}|default=[0-9]{3}\b|(POLL|INTERVAL|WAIT)[A-Z_]*\s*[:=]\s*[0-9]+|five.minute|300 ?s\b" -- tools/audit/seat tools/pr dev/governance .claude` at the base. Seams and dispositions:
- `ci-watch.sh` `sleep 300`, `proof_watch.py` `--poll` 300: closed here; each pinned on value and on use (ci-watch: the loop's recorded sleep argument; proof_watch: "(l) the wait polls at the configured cadence").
- `tick_loop.sh` `--interval` 300, `state_docs.py` `BEAT_INTERVAL`, `merge_train.py` `POLL_SECONDS` 300 (owner ruling 2026-10-07: one read per head per five minutes, a shared API quota), `orchestrator_tick.py`'s five-minute cadence: daemons run detached (`daemonize.py`), not waited on by a seat's turn, so no cache wake follows their poll; left as they are.
- `prepr.sh` `( sleep 300 ) &` (two sites): self-test lane stubs, not a wait; not applicable.
- `codeql-triage-poll.sh` `sleep 600`/`120`: an owner-run poll, not seat-facing; left.
- `cloud_relay --watch` default 120: already under.

Gap 6 seams, rule: `git grep -niE "read[^.]{0,40}CLAUDE\.md" -- .claude tools dev/governance`: `cloud_dispatch.py` fixer line, closed; `handover_prompt.py` (an orchestrator handover, a local session) and `sweep_template.md` step (0) (a deliberate re-read of origin/main's policy for a delta), not cloud-seat read lists, left; roster briefs under `dev/programme/rosters/` are records, left.

## Red checks

none

## Forward-carry

- `reviewer-head-off` survives `r10_flow_dispatch_mutants.py` at the base and at this head: `dispatch_group`'s "a reviewer needs --head" refusal is not pinned by the self-test (the arm that should kill it, `refused(role="reviewer", pr="7")`, is refused for another reason). Carry: R10-FRICTION-MUTATION-SURVIVOR
- The SessionStart and PreToolUse hook commands share the Stop command's `bash "$CLAUDE_PROJECT_DIR/..."` shape; no failure of theirs was measured (the gap seat counted Stop's 107), and resolving `pre-edit.sh` from another repository's cwd would guard edits in a workspace it was not written for. Carry: dismissed: unmeasured, and the fallback is not obviously right for an edit guard; the orchestrator may open it if a measurement shows it.

## Friction

- cloud-fixer-prompt: stale: the prompt says the toolchain (venv python) is on PATH from the environment; here python3 was /usr/bin/python3 3.11 and /opt/hpo/venv-ci/bin was not on PATH, so tests/entities.py failed with a 3.12 f-string SyntaxError until run under /opt/hpo/venv-ci/bin/python3. Carry: R10-FLY-SUITE-ENV-FLAKES
