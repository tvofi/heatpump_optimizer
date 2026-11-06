R10-POLICY-ROLE-PACK (#2717, owner ruling tvofi 2026-10-24, recommendation (b)). Adds a per-role policy pack, the SessionStart line that names it, and the `nudge.md` step 3 carry. It is a partial delivery of #2717, so this pull request does not close the issue: `cloud_dispatch.py` cannot set the role variable (see Departures), and that residual stays carried on #2717.

**This is a POLICY pull request: it merges only on the owner's approving review at its head** (see Approval).

**Repair of the red at 9478bca5.** `governance / instrument-self-tests` failed: `pr_args self-test: 174 checks, 1 failed`, on the check "the pusher census: the rule returns exactly the dispositioned paths, and every runner reaps" (`tools/audit/seat/pr_args.sh`, function `pr_pushers`).

- Cause, measured: the census rule `PR_PUSHER_RULE='(^|[^A-Za-z0-9_])(app_)?push\.sh'` returns `tools/policy/role_pack.py`, and `PR_PUSHERS` gives it no entry. At 9478bca5, `bash -c '. tools/audit/seat/pr_args.sh; pr_pushers' | grep -v '^ok'` printed `OPEN tools/policy/role_pack.py: undispositioned -- it names a pusher; give it an entry in PR_PUSHERS`. The same census at `origin/main` printed no `OPEN` line.
- The matching lines are 46, 272 and 275 of `role_pack.py`: the docstring's "so `push.sh` does not match inside `app_push.sh`" and the `named_entries` self-test, which uses the two names as sample instrument names.
- `role_pack.py` is a non-pusher. It imports only `argparse`, `fnmatch`, `re`, `sys` and `pathlib`. `grep -nE 'subprocess|os\.system|Popen|exec' tools/policy/role_pack.py` exits 1 (no line matches). The positive control for the pattern is the same `grep -cE` on `tools/audit/seat/merge_train.py`, the census's `runner-py`, which counts 27 matching lines.
- The fix gives it the census's existing disposition for a file that names a pusher and runs none: one `mention:` entry in `PR_PUSHERS`, beside the ten `mention` siblings (`head_note.py`, `gh_read.py` and others). The rule itself is unchanged, so the census still refuses every new file that names a pusher.
- Departure from the brief: the brief suggested "a rule that recognises a real push site rather than any mention". Not taken. A push site has no syntactic shape across `.sh`, `.py` and `.mjs` (an argv built from a variable), so a narrower rule would let a new runner pass undispositioned. That is the weakening the brief forbids. The census is deliberately over-inclusive, and every mention is dispositioned by hand.

What lands:

- `tools/policy/role_pack.py`: renders one role's pack (`fixer`, `fix-review`, `designer`, `design-review`, `root-cause`, `verifier`, `judge`, and `finder` for `COMMON.md`). A pack holds three things, each framed and byte-equal to its file:
  - the role's contract under `dev/governance/roles/`;
  - every rule under `dev/governance/rules/` whose `paths:` globs match the contract or `INSTRUMENTS.md`, derived at each render and never listed;
  - the `INSTRUMENTS.md` entry lines whose instrument the contract names as a whole token.
- `role_pack.py check`: refuses a paraphrased line, a block that is missing, outside the role's plan or required but absent, a line outside every frame, and a pack larger than the files it frames. `sizes` prints the figures below. `--self-test` runs every role plus one mutant per rule. Each mutant must be refused by its own rule's message, so a mutant that some other rule catches does not count.
- `.claude/hooks/session-start.sh`: when `HPO_SEAT_ROLE` names a role, the hook writes the pack to `git rev-parse --git-path role-pack-<role>.md` and prints one `role pack:` line after the clone-fact lines. When the variable is unset, its output is byte-equal to the base hook's. Its `--self-test`, which `policy_lint.mjs --hooks` runs in CI, adds seven arms: unset equals `report()` exactly; set is that output plus exactly one line; the named file checks clean; an unknown role prints a REFUSE line and the session still starts; `role_pack.py --self-test` passes.
- The `INSTRUMENTS.md` entry with its `instruments/role_pack.py.md` page, and a line in `governance.yml`'s `instrument-self-tests`, which `selftest_wiring.py --check` requires.
- `tools/audit/seat/pr_args.sh`: the `PR_PUSHERS` entry for `tools/policy/role_pack.py` (the repair above).
- `dev/governance/roles/nudge.md` steps 3 and 7 (Carry 4), covered under Forward-carry.

Brief carries, in the review packet's 1-based numbering (the payload's 0-based `Carry <i>` is `Carry <i+1>` here):

- Carry 1 (owner recommendation (b); after-edges): this group is the pack's home.
  - Both after-groups have merged: R10-POLICY-FIXER-MD as #2704; R10-FLOW-DESIGN-STAGES as #2994, #3012 and #3002 (`dev/programme/delivery/`).
  - So every pack renders `main`'s final `fixer.md` and `fix-review.md`, read at each render and never copied.
  - The role is not named at dispatch, because the cloud payload has no per-seat environment: departure 3, carried on #2717.
- Carry 2 (verbatim, never paraphrased; owner review read at the base):
  - Every byte between a pack's frames is a byte of the file the frame names.
  - `check` refuses a paraphrased line, and its mutant is in Mutation proof.
  - The owner question was read from `.github/CODEOWNERS` and `policy_lint.mjs`'s `POLICY_GLOBS`: see Approval.
- Carry 3 (classify the new module):
  - `tools/policy/role_pack.py` is on `tests/closure.py`'s INERT prefix `"tools/policy/"`, deliberately: no gate script opens it, and its self-test runs in `instrument-self-tests` and through the hook's self-test.
  - `tools/audit/seat/instruments/role_pack.py.md` is under the INERT prefix for `tools/audit/` prose.
  - `tests/entities.py` passes at the head, so neither file "forces the FULL suite when touched".
- Carry 4 (R10-FLOW-AUTOTRAIN item 1, `nudge.md` step 3): closed in this diff; see Forward-carry.

Departures from the brief, each measured, with the alternatives and why each lost (fixer step 17):

1. **The pack is a file, not the hook's stdout.** Claude Code 2.1.318's bundle (`hke`, threshold `1e4`) keeps at most 10,000 characters of hook stdout in context. Longer output is saved to disk, and the context gets a preview whose path is replaced by `<persisted>`.
   - Every pack is over that limit (`role_pack.py sizes`, column `pack`), so a printed pack would reach the seat as a preview it cannot follow.
   - Alternative: split the pack below the cap. Lost, because the cap applies to the hook's whole stdout and there is one hook.
   - Alternative: `additionalContext` JSON. Lost, because the cap is applied to raw stdout before any JSON parsing.
2. **CLAUDE.md is not in the pack.** The harness injects CLAUDE.md into every Claude Code session, and this hook is Claude Code's.
   - In the first fixer's transcript, CLAUDE.md arrived as a system-reminder before any hook output, and no tool result re-read it.
   - Carrying it would put the same text in context twice. The rendered header says it was left out and why.
3. **`cloud_dispatch.py` does not set the variable.** The cloud payload has no per-session environment field. `cloud_dispatch.py`'s own self-test pins `session_context` to exactly `{allowed_tools, model, sources}` (its check "the ccr carries environment_id, session_context and one user event").
   - Inventing a field risks a payload the runner rejects.
   - The cloud environment's variables are per environment, not per seat.
   - So cloud seats get no pack from this pull request; the residual is carried below.
   - Alternative: rewrite the Role lines in the cloud prompt to `role_pack.py render`. Not taken, because it is no saving for the cloud fixer, which reads through Bash: see Figures, `read_set(Bash)` against `pack`.
4. **Agent-tool subagents run no SessionStart hook**, measured at the base by the first fixer:
   - Its session's transcript held 4 SessionStart hook attachments.
   - The transcript of a `frugal:scout` subagent it launched held 0, and no "shallow clone:" line.
   - So the hook's saving is not claimed for local Agent-tool seats. A local seat brief must name `python3 tools/policy/role_pack.py render <role> --out <path>` itself.

Whether this needs the owner: `.github/CODEOWNERS` gives `/.claude/hooks/` and `/dev/governance/roles/` to `@tvofi`. `policy_lint.mjs`'s `POLICY_GLOBS` holds the roles directory (`nudge.md` is policy) but not `.claude/hooks/` or `tools/policy/`. The roster's `owner_gate` is "mandated approval under 6329234399".

## Approval

Owed, not yet given. The diff touches policy: `dev/governance/roles/nudge.md` (`policy_lint.mjs` POLICY_GLOBS). It also touches code-owned paths: `.claude/hooks/session-start.sh` (`/.claude/hooks/ @tvofi`) and `dev/governance/roles/` (`@tvofi`). It merges only on the owner's approving review at its head, or under mandate 6329234399, which the roster's `owner_gate` names for this group.

## Head

842987e20a4ebcfd508bdc41b77ffbfff5efb29d. It descends from the PR head 9478bca58c43bc4067e6e5599491cd03c03e1cf8 by two commits:

- the repair commit, `pr_args: disposition tools/policy/role_pack.py in the pusher census as a mention`;
- a merge of `origin/main` at 30638cf0c8a7114019682f87051a4a282d2981ff, stamped 2026-11-06 (UTC), which `git merge-tree --write-tree origin/main HEAD` reported clean. Main's delta is 14 files: delivery rows, `carry-201.json` and the `beat_jobs` instrument. None is a file of this diff. `git grep -nE '(^|[^A-Za-z0-9_])(app_)?push\.sh' origin/main -- tools/audit/seat/beat_jobs.py tools/audit/seat/beat_jobs_selftest.py` exited 1 (no match), so main's delta adds no census seam.

Every figure below was re-taken at 842987e2.

`tools/pr/prepr.sh` ran clean on 842987e2 (`PRE-PR: 842987e2... rc=0`). `origin/main` was still 30638cf0 when the code was pushed, so no second run was owed.

- Step ref not moved: `handoff-wip/r10-policy-role-pack` still holds the first fixer's pre-rewrite e4c841444, which is not an ancestor of the PR head. A fast-forward push to it was refused, and this seat does not force-push, so no step was pushed there. The first body already reported that its delete failed. The final delete after this handoff is attempted, and the result is reported by the seat.

## Mutation proof

The repair, from a detached worktree at the repair commit with its one production line deleted (`sed -i '\#^tools/policy/role_pack.py mention:#d' tools/audit/seat/pr_args.sh`):

- `pr_pushers` printed `OPEN tools/policy/role_pack.py: undispositioned -- it names a pusher; give it an entry in PR_PUSHERS` and exited 1.
- `bash tools/audit/seat/pr_args.sh --self-test` printed `FAIL the pusher census: the rule returns exactly the dispositioned paths, and every runner reaps` and `pr_args self-test: 174 checks, 1 failed`. That is CI's red at 9478bca5, check for check. Restored, it is `174 checks, 0 failed`.

The pack, from the first fixer's run at 452394cb (none of those files changed since). Each mutant edits one predicate, then runs `python3 -I tools/policy/role_pack.py --self-test` and `bash .claude/hooks/session-start.sh --self-test`, then restores the file. 10 of 10 mutants were killed. The first FAIL line of each:

- `check` byte-equality (`elif text != source` -> `elif False`): `FAIL mutant refused by its rule -- one contract line paraphrased: not refused`
- `check` required file (`if rel not in got_paths` -> `if False`): `FAIL mutant refused by its rule -- INSTRUMENTS.md dropped from the role's list: not refused`
- `check` subset size (`if body > whole` -> `if False`): `FAIL mutant refused by its rule -- the contract framed twice (each copy byte-equal): not refused`
- `check` named entries (`text != expect` -> `False`): `FAIL mutant refused by its rule -- an entry the contract does not name added: not refused`
- `check` stray line (its `errs +=` emptied): `FAIL mutant refused by its rule -- a line outside every frame: not refused`
- `plan` rule selection (`if hits` -> `if False`): `FAIL the fixer's plan carries at least one rule, so the rule mutant has a target`
- `named_entries` whole-token match (regex -> `name in contract`): `FAIL `push.sh` is not named by `app_push.sh``
- `glob_match` `**` spans segments (`any(go(i+1,k) ...)` -> `go(i+1,j+1)`): `FAIL `**` spans segments`
- hook prints the line when set (call -> `:`): `FAIL set, the output is the unset output plus one role pack line`
- hook unset output gains a line (`report; echo extra`): `FAIL unset, the hook prints the clone-fact report and not a byte more`

## Null control

- The census is not weakened. At 842987e2, the self-test's census arms all pass, including "a new script that runs app_push.sh is refused as undispositioned", "a runner without pr_exit_trap is refused", and the arm "null control: the same runner without its branch lock needs no push lock". A rule that had been narrowed would fail the first of these.
- The census at `origin/main` (`pr_pushers "" origin/main`) printed no `OPEN` line, so the red was this diff's, not main's.
- At 842987e2, `pr_pushers` exits 0 and prints no `OPEN` line. Its `ok` lines and `PR_PUSHERS`'s non-empty lines are equal in number, which is the self-test's own equality.
- Unset, the base hook against the head hook: byte-equal (first fixer, 452394cb; the hook is unchanged since). The hook's self-test at 842987e2 holds the same assertion: `24 passed, 0 failed`.
- `role_pack.py check` with no argument checks every role's rendered pack clean at 842987e2. That is the null control for every pack mutant above.

## Figures

- The pusher census, the class rule that enumerates this red's seams: `bash -c '. tools/audit/seat/pr_args.sh; pr_pushers'`. Every path `PR_PUSHER_RULE` returns under `tools/` gets a disposition. At 842987e2 it prints no `OPEN` line, so every returned seam is dispositioned. `tools/policy/role_pack.py` is closed in this diff, and the rest were already guarded by their `PR_PUSHERS` entries.
- `bash tools/audit/seat/pr_args.sh --self-test`: `pr_args self-test: 174 checks, 0 failed`.
- The pack against the read set it replaces, in characters (`python3 -I tools/policy/role_pack.py sizes`). The rule: `read_set(Read)` is the contract, plus the rules a Read of it loads, plus the whole `INSTRUMENTS.md`. `read_set(Bash)` is the contract plus `INSTRUMENTS.md`, because a Bash read loads no rule. `pack` is the rendered pack. Tokens are not counted; characters are the unit.
  - Against a Read-tool opening, the pack is smaller for every role: fixer 42,744 against 55,676; judge 22,824 against 36,737. The saving is `INSTRUMENTS.md` less the entries a contract names (fixer 8, fix-review 3, judge 1, the rest 0), less the frames.
  - Against a Bash opening, the pack is larger: fixer 42,744 against 36,004. The pack carries the rules that a seat bound by them would otherwise not have in context.
  - So the tokens fall only for a seat that opens with the Read tool. This pull request claims nothing for the rest.
- The pack's own size per role: `python3 -I tools/policy/role_pack.py check`. Every pack is over the 10,000-character hook cap, which is departure 1.
- `python3 -I tools/policy/role_pack.py --self-test`: `35 passed, 0 failed`. `bash .claude/hooks/session-start.sh --self-test`: `24 passed, 0 failed`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out`. It runs `tests/entities.py` and `tests/harness_headers.py`; both pass at 842987e2: `PYTHONPATH=tests/hastub python3 tests/entities.py` printed `ALL 2637 ENTITY CHECKS PASSED`, and `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` printed `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` at 842987e2.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`.
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: `118 self-testing, 118 wired, 0 unwired` and `0 index gap(s)`.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- Classification: `tools/policy/role_pack.py` falls under `tests/closure.py`'s INERT prefix `"tools/policy/"` (R9-RO-6). It is deliberately inert: no gate script opens it. Its self-test runs in `instrument-self-tests`, and again through the hook's self-test in `policy-docs`' `--hooks` step.

## Architecture score

`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`.

## Red checks

CI has not run on 842987e2. These are the concluded reds of the previous head, 9478bca5, across all of its check runs (68, one page):

- `governance / instrument-self-tests` (127946437283): failure, the pusher census, repaired in this diff.
  - Class: a new file named a pusher, and the census was not run before the handoff.
  - The cheaper detector exists: `bash -c '. tools/audit/seat/pr_args.sh; pr_pushers'` runs in under a second and names the file. Its standing cost is nil; it was not run because nothing that a fixer runs on a `tools/policy/` diff calls it. The first fixer's prepr did not run it, and `tools/policy/` is INERT, so no scoped gate script selects it.
  - This job may also cancel at its 30-minute job timeout. That is main-wide, not this diff, and is cured by R10-PROCESS-SLIM #3245. The cheaper detector is the job's own duration on main.
- `codeql / Analyze (python)` (127946437423): cancelled at its job limit. It is runner-side, not this diff: the diff adds one Python file, and `codeql / Analyze (javascript-typescript)` and `codeql / Analyze (actions)` passed. No cheaper detector exists for a runner-side time limit.
- `pr-contract / pr-contract` (127970407299): failure. The body's `## Red checks` did not name `governance / instrument-self-tests`. This body is re-taken whole from `.github/PULL_REQUEST_TEMPLATE.md` and names every red. The cheaper detector is `tools/pr/prepr.sh --body-check`, run on this body before the handoff.
- `gate` (127970744270, 127950388315, 127948146507): failure, the aggregate of the reds above. It has no cause of its own.

## Forward-carry

- R10-FLOW-AUTOTRAIN's item 1 is closed here. `nudge.md` step 3 had left budget-file and policy-path heads out of the queue, and step 7 direct-merged them. Now:
  - step 3 says they stay in, `Train.admit` routes them serial, and `--pre-flight` parks one the owner has not approved at that head (`Train.raise_hold`, `Train.policy_gate`);
  - step 3's hand command carries `--bot-prs --pre-flight`;
  - step 7 direct-merges what `--pre-flight` parked.
  - Carry: dismissed: closed in this diff (nudge.md steps 3 and 7)
- The cloud seats get no pack from this pull request. A cloud trigger's payload has no per-session environment field, so `HPO_SEAT_ROLE` can reach a cloud seat only through an environment per role (an overlay `environment_id` per role) or a runner field the tree does not yet know. That choice is the orchestrator's, with the owner. Carry: #2717
- Agent-tool subagents run no SessionStart hook (departure 4), so a local seat's brief names `python3 tools/policy/role_pack.py render <role> --out <path>` and the seat reads that file once. That changes how the orchestrator writes a local seat brief. Carry: #2717

## Friction

R10-POLICY-ROLE-PACK: contradiction: the brief has the pack printed by the SessionStart hook and set from the cloud payload. The 10,000-character hook-output cap and the payload's fixed `session_context` keys make both impossible as written; departures 1 and 3 above. Carry: #2717
