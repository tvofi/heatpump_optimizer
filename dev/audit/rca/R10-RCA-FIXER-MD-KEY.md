# R10-RCA-FIXER-MD-KEY: the recurring-friction key `tools/audit/briefs/fixer.md`

Root-cause seat for #2895, the governance cron's third filing of the friction
key `tools/audit/briefs/fixer.md` (#2378, disposed by R10-POLICY-FIXER-MD, PR
#2704, was the second). It ran beside any fix, never as the fixer
(`dev/governance/roles/root-cause.md`). Measured at origin/main `88c6ad5bb`
(2026-10-29 15:06Z).

**The rule that produced every count here.** For each merge commit on
`git log --first-parent v7.0.4..origin/main` whose subject is `Merge pull
request #N`, the pull request's body, its `## Friction` section parsed by
`policy_lint.mjs`'s exported `frictionEntries`, and each entry's id folded by
`frictionKey`'s rule for this key: strip backticks and `#...`, then the
id, the id less `.md`, or a `-`-separated prefix of it, equal to `fixer.md`,
`tools/audit/briefs/fixer.md` or `dev/governance/roles/fixer.md`. The
instrument that owns the count is `node tools/policy/policy_lint.mjs --stats
--since <tag>`; the per-entry table below is a re-derivation of what it reads,
and the PR body puts the instrument's own line beside it.

## 1. Cause

### 1.1 What the key is

`frictionKey` canonicalises a moved file to its OLD spelling (`canon()` in
`tools/policy/counts.mjs`, which reverses `tests/layout.json`'s moves), so
`dev/governance/roles/fixer.md` keys as `tools/audit/briefs/fixer.md`. The key
is therefore not a stale alias of a retired file: it is the fixer contract
itself, all eighteen steps and the preamble, under one name. Two corrections
to the brief that dispatched this seat:

- `fixer-step-N`, `fixer-env`, `fixer-handoff` and `fixer-instrument` do
  **not** fold into the key. `policyKeyIndex` claims no role contract's bare
  name (its comment, "It costs `fixer-step-5`"), so they stay verbatim keys.
  `fixer.md-step17` does fold, through the `-` prefix loop.
- `#N` is stripped, so every step of the contract shares the key.

### 1.2 The instances, grouped by the step they name

v7.0.4 window: 285 merged pull requests; 11 folded entries over 8 pull requests.
v7.0.5 window: 59; 4 entries over 3 (#2873, #2903, #2947) -- the issue's
current body. The bot's 2026-10-28 03:16Z comment, "no pull request at all",
was true then: #2903 merged at 10:58Z that day, #2873 at 17:31Z, #2947 on
the 29th.

| group | folded entries (PR: id, event) | siblings under verbatim keys |
|---|---|---|
| A. step 5: `python3` on PATH is not the seat venv | #2671 `fixer.md#5` stale; #2683 `…/fixer.md#5` unclear (x2) | #2631 `fixer-env`; #2937 `cloud-fixer-prompt` stale |
| A'. step 5: the seat venv cannot be built | #2947 `…/fixer.md` cost (uv offers no cpython 3.14.7) | -- |
| B. step 2: mutation of `exit $?` | #2709 `fixer.md#2` cost | -- |
| C. re-cut round count (cited as step 2) | #2873 `…/fixer.md#2` unclear | -- |
| D. step 3 / 16: a harness the fix deletes; a verdict at an unknowable age | #2683 `…/fixer.md#3` stale; #2873 `…/fixer.md#3` unclear | -- |
| E. step 17: payment at zero headroom | #2620 `fixer.md-step17` contradiction | -- |
| F. seat environment, not the contract | #2889 `fixer.md` cost (`.git/info/exclude` `seat/`); #2903 `fixer.md` cost (host reboot mid-census) | #2704 `fixer-env` (BASH_ENV, #2452) |

Only group A recurs: three folded entries and two verbatim siblings, five
bodies over four pull requests. Every other group is one cause, one body.

### 1.3 Group A is not repaired

R10-FLY-CLOUD-SETUP-TOOLCHAIN (#2709, merged 2026-10-24 19:16Z) found the
mechanism and wrote it into `tools/audit/seat/cloud-setup.sh`: a seat's Bash
call inherits the agent's environment, which no profile and no BASH_ENV
reaches, so the toolchain arrives only through environment variables the
owner sets beside the setup script. It added `--check` to say whether they
are set. Nothing runs `--check`, and the dispatch prompt
(`cloud_dispatch.py`'s `_prompt`) kept telling every seat "the toolchain is
on PATH from the environment".

Reproduced in this seat, 2026-10-29, five days after #2709:

    $ bash tools/audit/seat/cloud-setup.sh --check; echo "exit=$?"
    cloud-setup check: REFUSE python3 is /usr/local/bin/python3, HPO_TYPING_PYTHON is unset, OPENBLAS_CORETYPE is unset; ...
    exit=1

and the null control, the same check under the variables it names, reads `OK
python3 is /opt/hpo/venv-ci/bin/python3`, exit 0. `python3 --version` here is
3.11.17; the installed `/etc/profile.d/hpo-toolchain.sh` lacks the
`case ":$PATH:"` guard `write_profile` has written since #2709, so the
environment still runs a pre-#2709 paste of the setup script. #2937 (merged
2026-10-29 02:52Z) paid the same cause under a verbatim key, after #2709.

## 2. Process state

**Group A: (d).** The process -- dispatch tells the seat the toolchain is on
PATH -- was sound while the environment put it there. Its precondition was
found false (#2709: no route but the environment's variables reaches the
shell) and stays unmet, and neither the prompt nor the seat's session start
notices. Not (b): every citing seat followed step 5 and reported the
divergence. Not a firmer instruction, which `root-cause.md` warns against for
(d): the countermeasure makes the process see its own precondition.

**Groups B-F: no process defect owed here.** B is already repaired: step 2
carries "write `|| true; exit 0`; #2709" (R10-POLICY-FIXER-MD). C, D and E
are single instances, each dismissed or ruled in its own body (C: a re-cut
satisfies both counts; D: a round record recounts, step 10; E: ruled under
mandate 6329234399). F is environment cost cited as `fixer.md` because the
contract is a fixer's default id; the contract governs none of it.

**The key.** It keeps counting because it is a bucket for every step of the
most-cited contract, not because one cause stays unrepaired: with group A
removed, the v7.0.4 window still holds 7 pull requests (#2620, #2683, #2709,
#2873, #2889, #2903, #2947) and the v7.0.5 window 3 (#2873, #2903, #2947), each at or
over the threshold of 3, over causes that do not recur. See section 4 for
splitting it.

## 3. How far the class reaches

The class is "a seat's shell lacks the toolchain the prompt promises". Its
seams, with the rule that enumerates them:

- the prompt's claim: `git grep -n "on PATH from the environment"` returns one
  site, `tools/audit/seat/cloud_dispatch.py`'s `_prompt`; closed in this diff.
- the detector: `git grep -n "cloud-setup.sh --check" -- .claude/` returned
  nothing at the merge base; this diff adds the session-start hook's
  `toolchain:` line.
- the friction entries naming it: the group A row above, from the rule at the
  top of this file run with ids matched on `fixer` -- 5 bodies.
- the venv build itself (A'): `seat_venv.sh` pins a cpython the container's uv
  does not offer -- a distinct cause, carried in section 5, not closed here.

## 4. Cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

**cost(defect).** Each group A body records one lost run before the cause was
found: a harness run on the system python discarded and re-taken (#2631), a
`--pin-killed` drive dead on a 3.12 f-string (#2683), a hand-prepended PATH
(#2671), an `entities.py` SyntaxError (#2937). Estimate 5 to 15 min of seat
time per seat, the run plus its diagnosis; no seat timed it. A refiled key
costs a root-cause seat on top.

**P(recurrence).** 1 per cloud seat while the variables are unset: the cause
is environmental and reproduced in the next seat dispatched (this one). Four
pull requests in the v7.0.4 window reported it; a seat that stumbled and did
not write a Friction line is not counted.

### Built here: the session-start `toolchain:` line (state d)

`.claude/hooks/session-start.sh` runs `cloud-setup.sh --check` in a cloud seat
(one with `$HPO_PREFIX/venv-ci`). On refusal it appends `cloud-setup.sh
--env-lines` (the profile's guarded lines) to `CLAUDE_ENV_FILE`, which the
harness sources before each Bash call, re-checks under that file, and prints
`EXPORTED`; where no such file takes them it prints `REFUSE` and the per-call
remedy. `cloud_dispatch.py`'s prompt now points at that line instead of
asserting the toolchain. Standing cost: 8-10 ms of `--check` per session
start (hook 34-43 ms against 26-29 ms at the merge base, five runs each).
8-10 ms per session against 5-15 min per seat: built.

Demonstrated in this seat. At the merge base the hook prints no `toolchain:`
line (`grep -c` 0). At the head: `REFUSE` with no `CLAUDE_ENV_FILE`;
`EXPORTED` with one, and a shell sourcing that file reads `Python 3.14.7` and
`--check` OK. Null control: under the variables set, `OK`, and the file it was
handed stays 0 bytes. The hook's self-test drives the four answers on a stub
prefix; three mutants (the append deleted, the `--check` predicate forced
true, `--env-lines` deleted) each fail it, and the last also fails
`cloud-setup.sh --self-test`. What this seat cannot show is a live harness
sourcing `CLAUDE_ENV_FILE`: the hook that started it is the merge base's.
The next cloud seat's first `toolchain:` line is that run; `REFUSE` there
means the harness gave no file, and the remedy it prints still works (shown
here: `eval` of `--env-lines`, then `--check` OK).

### Refused: keying friction by step

Folding `#N` into the key, so `fixer.md#5` and `fixer.md#2` count apart,
would not have stopped this filing: by step, the v7.0.4 window holds #5: 2
pull requests, #2: 2, #3: 2, and the bare `fixer.md`: 3 (#2889, #2903,
#2947), at threshold. The cost is a keying change in `frictionKey`, its
pins and the issue titles in `friction_issues.mjs`, for a bucket that still
fires. Not built.

### Refused: a policy edit to `fixer.md`

No group is the contract being unclear or wrong at a step that recurs. A
firmer step 5 would be the (b) answer to a (d) state.

## 5. Owner and carries

- **The owner** (tvofi): set the environment variables
  `cloud-setup.sh --variables` prints beside the setup script, and re-paste the
  current `cloud-setup.sh`; the hook's `OK` line is how a seat will see it
  done. Outside the tree, so no seat can.
- **R10-FLY-SUITE-ENV-FLAKES** (named by #2937's carry): group A' -- the venv
  pin `seat_venv.sh` asks uv for (cpython 3.14.7) is not in this container's uv
  index (#2947).
- The key will refile while fixers cite the contract as their default id for
  environment cost (group F); that is the threshold working, and a seat
  disposing a future filing should start from section 1.2's grouping rule,
  not from this file's counts.
