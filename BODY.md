R10-POLICY-ROLE-PACK (#2717, owner ruling tvofi 2026-10-24, recommendation (b)). Adds a per-role policy pack, the SessionStart line that names it, and the `nudge.md` step 3 carry. It is a partial delivery of #2717, so this pull request does not close the issue: `cloud_dispatch.py` cannot set the role variable (see Departures), and that residual stays carried on #2717.

What lands:

- `tools/policy/role_pack.py`: renders one role's pack (`fixer`, `fix-review`, `designer`, `design-review`, `root-cause`, `verifier`, `judge`, and `finder` for `COMMON.md`). A pack holds three things, each framed and byte-equal to its file:
  - the role's contract under `dev/governance/roles/`;
  - every rule under `dev/governance/rules/` whose `paths:` globs match the contract or `INSTRUMENTS.md`, derived at each render and never listed;
  - the `INSTRUMENTS.md` entry lines whose instrument the contract names as a whole token.
- `role_pack.py check`: refuses a paraphrased line, a block that is missing, outside the role's plan or required but absent, a line outside every frame, and a pack larger than the files it frames. `sizes` prints the figures below. `--self-test` runs every role plus one mutant per rule. Each mutant must be refused by its own rule's message, so a mutant that some other rule catches does not count.
- `.claude/hooks/session-start.sh`: when `HPO_SEAT_ROLE` names a role, the hook writes the pack to `git rev-parse --git-path role-pack-<role>.md` and prints one `role pack:` line after the seven clone-fact lines. When the variable is unset, its output is byte-equal to the base hook's. Its `--self-test`, which `policy_lint.mjs --hooks` runs in CI, adds seven arms: unset equals `report()` exactly; set is that output plus exactly one line; the named file checks clean; an unknown role prints a REFUSE line and the session still starts; `role_pack.py --self-test` passes.
- The `INSTRUMENTS.md` entry with its `instruments/role_pack.py.md` page, and a line in `governance.yml`'s `instrument-self-tests`, which `selftest_wiring.py --check` requires.
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
   - In this seat's own transcript, CLAUDE.md arrived as a 14,693-character system-reminder before any hook output, and no tool result re-read it.
   - Carrying it would put the same 14,358 characters in context twice. The rendered header says it was left out and why.
3. **`cloud_dispatch.py` does not set the variable.** The cloud payload has no per-session environment field. `cloud_dispatch.py`'s own self-test pins `session_context` to exactly `{allowed_tools, model, sources}` (its check "the ccr carries environment_id, session_context and one user event").
   - Inventing a field risks a payload the runner rejects.
   - The cloud environment's variables are per environment, not per seat.
   - So cloud seats get no pack from this pull request; the residual is carried below.
   - Alternative: rewrite the Role lines in the cloud prompt to `role_pack.py render`. Not taken, because it is no saving for the cloud fixer, which reads through Bash: see Figures, `read_set(Bash)` against `pack`.
4. **Agent-tool subagents run no SessionStart hook**, measured at the base:
   - This session's transcript holds 4 SessionStart hook attachments (3 `hook_success`, 1 `hook_non_blocking_error`).
   - The transcript of a `frugal:scout` subagent it launched holds 0, and no "shallow clone:" line.
   - So the hook's saving is not claimed for local Agent-tool seats. A local seat brief must name `python3 tools/policy/role_pack.py render <role> --out <path>` itself.

Whether this needs the owner: `.github/CODEOWNERS` gives `/.claude/hooks/` and `/dev/governance/roles/` to `@tvofi`. `policy_lint.mjs`'s `POLICY_GLOBS` holds the roles directory (`nudge.md` is policy) but not `.claude/hooks/` or `tools/policy/`. The roster's `owner_gate` is "mandated approval under 6329234399".

## Approval

Owed, not yet given. The diff touches policy: `dev/governance/roles/nudge.md` (`policy_lint.mjs` POLICY_GLOBS). It also touches code-owned paths: `.claude/hooks/session-start.sh` (`/.claude/hooks/ @tvofi`) and `dev/governance/roles/` (`@tvofi`). It merges only on the owner's approving review at its head, or under mandate 6329234399, which the roster's `owner_gate` names for this group.

## Head

452394cb23d1a5c9f3fd1cd802ba0b684ecb98f0, merge base b36679ceaa65a08a67a84f0d934c93aa15f7c7f3 (= `origin/main` at the time of measurement, 2026-11-06T13:40Z).

- `main` moved twice during the work, from 7e8939d38 to 5421413b5 (#3243: `tests/gate_lock.py`, a delivery row) and then to b36679ce (#3238: a triage record, its harness, `tests/closures.json`). Neither touches a file of this diff. Each was merged, and `git merge-tree` reported each clean.
- Re-taken at this head:
  - the mutation proof, 10 of 10 killed;
  - the unset byte-equality against `origin/main`'s hook;
  - `role_pack.py sizes`, `--self-test` and `check`;
  - the hook's self-test;
  - the gate scope, `tests/entities.py` and `tests/harness_headers.py`;
  - `tests/structure.py`, the architecture score and `prepr.sh`.
- The cloud environment exports `GIT_AUTHOR_*`/`GIT_COMMITTER_*` as `seat`. The branch's own commits were re-authored as `hpo-fixer` before the second merge, with the tree unchanged (`git diff --quiet e4c841444374 5918f3f522fa && echo TREE IDENTICAL` printed `TREE IDENTICAL`).

## Mutation proof

Run from a detached worktree at the head. Each mutant edits one predicate, then runs `python3 -I tools/policy/role_pack.py --self-test` and `bash .claude/hooks/session-start.sh --self-test`, then restores the file. 10 of 10 mutants were killed. The first FAIL line of each:

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

The last mutant survived the first version of the hook self-test. That version compared the set run only with the unset run, so a line added to both runs passed. Commit 3 added the exact comparison with `report()`. Restored, both self-tests are green: `35 passed, 0 failed` and `24 passed, 0 failed`.

## Null control

- Unset, the base hook against the head hook: `git show origin/main:.claude/hooks/session-start.sh > base-hook.sh`. Both are run with `CLAUDE_PROJECT_DIR` set to the worktree and `env -u HPO_SEAT_ROLE`, then `cmp base.out head.out && echo BYTE-EQUAL` printed `UNSET: BYTE-EQUAL (7 lines)`. The same head with `HPO_SEAT_ROLE=fixer` differs from the base output, as it must (8 lines), so the comparison can see a difference.
- `role_pack.py check` with no argument checks every role's rendered pack clean. That is the null control for every mutant above.
- `tests/entities.py`: at the first merge base 7e8939d38 it read `ALL 2632 ENTITY CHECKS PASSED`, and at this head it reads `ALL 2637 ENTITY CHECKS PASSED` (#3243 added checks). The FAIL lines that differ between runs are fixtures or timing that the summary does not count: `a8:register_once`'s fixture names, and `hb:positive_control`'s 600 ms spin reading.

## Figures

- The pack against the read set it replaces, in characters (`python3 -I tools/policy/role_pack.py sizes`). The rule: `read_set(Read)` is the contract, plus the rules a Read of it loads, plus the whole `INSTRUMENTS.md`. `read_set(Bash)` is the contract plus `INSTRUMENTS.md`, because a Bash read loads no rule. `pack` is the rendered pack. Tokens are not counted; characters are the unit.
  - Against a Read-tool opening, the pack is smaller for every role: fixer 42,744 against 55,676; judge 22,824 against 36,737. The saving is `INSTRUMENTS.md` less the entries a contract names (fixer 8, fix-review 3, judge 1, the rest 0), less the frames.
  - Against a Bash opening, the pack is larger: fixer 42,744 against 36,004. The pack carries the four rules (19,672 characters) that a seat bound by them would otherwise not have in context.
  - So the tokens fall only for a seat that opens with the Read tool. This pull request claims nothing for the rest.
- The pack's own size per role: `python3 -I tools/policy/role_pack.py check`. Every pack is over the 10,000-character hook cap, which is departure 1.
- The policy re-read at the base, from local transcripts. There is no token reader: R10-FLOW-BOARD's `merge_throughput.py flow` has no token section, by `grep -n "token\|transcript" tools/audit/merge_throughput.py`, which printed nothing. The sample is this session, n=1, a cloud fixer:
  - one Bash tool result of `fixer.md`, 20,807 characters;
  - one Bash tool result carrying the hook and the head of `INSTRUMENTS.md`, 17,996 characters;
  - CLAUDE.md loaded by the harness, 14,693 characters, and not re-read.
  - No reviewer or designer transcript exists in this container. Those two numbers are not measured here.
- The rules a contract's read loads (`role_pack.py plan`, through `sizes`): `brief-citations.md`, `defect-root-cause.md`, `finding-propagation.md` and `writing-for-agents.md`. All four match `dev/governance/**`. No rule glob matches `tools/audit/seat/INSTRUMENTS.md`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out`. It runs `tests/entities.py` and `tests/harness_headers.py`; both pass at the head (`ALL 2637 ENTITY CHECKS PASSED`, `ALL 112 HARNESS HEADER CHECKS PASSED`).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`.
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: `118 self-testing, 118 wired, 0 unwired` and `0 index gap(s)`.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- Classification: `tools/policy/role_pack.py` falls under `tests/closure.py`'s INERT prefix `"tools/policy/"` (R9-RO-6). It is deliberately inert: no gate script opens it. Its self-test runs in `instrument-self-tests`, and again through the hook's self-test in `policy-docs`' `--hooks` step.

## Architecture score

`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`.

## Red checks

- No CI check has run on this head yet.
- Locally, `tests/entities.py`'s check "the template arm turns the acceptance red ... (and the real template keeps it green)" went red at an intermediate head. The cause was the first `nudge.md` wording, about 35 tokens over its `files_tokens` cap, so the full `policy_lint.mjs` exited 1.
- The cheaper detector exists: `node tools/policy/policy_lint.mjs` names the cap in one line, and `prepr.sh` runs it. I ran `entities.py` first. The overrun was paid by cutting the wording (commit bba1d9528), not by a raise.

## Forward-carry

- R10-FLOW-AUTOTRAIN's item 1 is closed here. `nudge.md` step 3 had left budget-file and policy-path heads out of the queue, and step 7 direct-merged them. Now:
  - step 3 says they stay in, `Train.admit` routes them serial, and `--pre-flight` parks one the owner has not approved at that head (`Train.raise_hold`, `Train.policy_gate`);
  - step 3's hand command carries `--bot-prs --pre-flight`;
  - step 7 direct-merges what `--pre-flight` parked.
  - Control: step 3 now says what `sweep_template.md` item (3) says ("A budget-file or policy head goes the batch's serial route, where `--pre-flight` parks ..."). `admit_verdict` routes nothing: it only refuses the record branch, an unreadable head and a verdict that does not carry, which step 3's "Leave out a `record:` pull request" matches. No contradiction remains.
  - Carry: dismissed: closed in this diff (nudge.md steps 3 and 7)
- The cloud seats get no pack from this pull request. A cloud trigger's payload has no per-session environment field, so `HPO_SEAT_ROLE` can reach a cloud seat only through an environment per role (an overlay `environment_id` per role) or a runner field the tree does not yet know. That choice is the orchestrator's, with the owner. Carry: #2717
- Agent-tool subagents run no SessionStart hook (departure 4), so a local seat's brief names `python3 tools/policy/role_pack.py render <role> --out <path>` and the seat reads that file once. That changes how the orchestrator writes a local seat brief. Carry: #2717

## Friction

R10-POLICY-ROLE-PACK: contradiction: the brief has the pack printed by the SessionStart hook and set from the cloud payload. The 10,000-character hook-output cap and the payload's fixed `session_context` keys make both impossible as written; departures 1 and 3 above. Carry: #2717
