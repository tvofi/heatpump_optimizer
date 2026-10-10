A friction-issue triage read the literal `friction:` lines of every contributing
pull-request body in two windows and named three countermeasures it judged
genuinely owed: #2052, #2039 and #2020. This handoff carries them. Each premise
was re-measured before it was acted on, and the result is two delivered
countermeasures, one refused half, and one whole countermeasure refused: the
body says which measurement decided each.

**A (#2052) — the wait instruction is unactionable on a `DIRTY` head, and now
says so.** `dev/governance/rules/ci-autofix.md` opens by telling a seat to
**wait** for the autofix bot. Two measured facts make that unactionable on a
`DIRTY` head, and neither was where the instruction stands: `mutation-autofix`
is a `pull_request`-only lane (`.github/workflows/tests.yml:2645-2649` — the
job's `if:` requires `github.event_name == 'pull_request'`), and a `DIRTY` pull
request queues no `pull_request` run at all (`claim-files.md`, "GitHub is one
of those uninstalled clones"). The file's last section states the general fact,
but scoped to driver-file conflicts. The clause added states it in the wait
paragraph, in the file's own voice, and the payment is named below.

**B (#2039) — the seat shim reaches the pinned interpreter across state
roots.** `tools/audit/seat/shims/seat-python{,3}` exec'd
`$HPO_STATE_DIR/venv-ci/bin/python3` unconditionally, so a seat that pointed
`HPO_STATE_DIR` at a state of its own got `rc 126, cannot execute` — no
interpreter and no remedy. They now resolve the pinned interpreter the way
`prepr.sh`'s `recorder_python` resolves the recorder's (R9-FR-5): the seat's
own state root first, the documented default root (`$HOME/.local/state/hpo`)
second, and a refusal naming `tools/audit/seat/seat_venv.sh` when neither holds
one — never a fall-through to an unpinned interpreter.

**B (#2039), its second half — refused, already fixed: `fixer.md` step 5 names
`run_always`.** The countermeasure asked for an owed-work line against step 5
for omitting `tests/run.sh`'s `run_always` scripts (#2051's entry). Measured at
this head, step 5 says it: `dev/governance/roles/fixer.md:53-55`, "Run what
`scope.run` and `tests/run.sh`'s `run_always` lines name". One commit in its
history introduces the words, `a5054a3e6 "fixer.md step 5: run run.sh's
run_always lines too (#2039's #2051 entry)"`, and it merged in **#2059**. No
finding is owed; the entry is stale, and it is recorded as friction below rather
than filed.

**C (#2020) — refused, not added.** `claim-files.md` was the briefed home, and
the measurement says it cannot buy anything there: that rule's `paths:` is
`tests/golden/**` alone, while every `ledgermerge`-routed file is outside it
(`.gitattributes:22,23,24,29`), so a seat reading `tests/closures.json` never
loads it — the rule that does load is `ci-autofix.md`. The sentence's cost was
measured rather than guessed: 4 lines and 66 tokens, against a file already at
its 53-line cap and its 681-token cap. The route is also already named where
the refusal is printed (`tools/merge/ledger_merge.py:6` and `:426`), and the one
measured instance (#2065) self-resolved by merging `main`, which
`ci-autofix.md` already names. `#2020` is left open; if the route is to be
written into a rule, its loaded home is that file's driver-file section, and
that is a distinct, paid change this handoff does not make.

Neither key is closed here: each of `#2052` and `#2039` keys a whole window of
friction, and this diff disposes one entry of each. Precedent: `#2059` landed
`#2051`'s step-5 repair and left that key's issue open.

## Head

`a6fee4f29475c23be31ce884326c3fd92f4a7c8b` — one merge commit above the authored
`82e8d8a9b`, which merges `origin/main` `d3dbf2c3fc42b87e6aad71d3de0c0885a10c750e`
(main's #2083 also edits `tools/audit/seat/INSTRUMENTS.md`; the merge was clean,
and steps 2–8 were re-executed at this head). Measured 2026-10-10T15:10Z
(`date -u`), against that tip.

## Mutation proof

B is the only half with production lines; A is prose. Deleting the fix — both
shims restored to the merge base's copy, `git show <merge-base>:tools/audit/seat/shims/<s> > <s>` —
turns four arms red:

    bash tools/audit/seat/seat_venv.sh --self-test
      M0 (head):  seat_venv self-test: 20 checks, 0 failed
      mutant:     seat_venv self-test: 20 checks, 4 failed
        FAIL seat-python reaches the default root's venv-ci when the seat's state holds none
        FAIL seat-python3 reaches the default root's venv-ci when the seat's state holds none
        FAIL seat-python refuses naming the build command when no root holds a pinned interpreter
        FAIL seat-python3 refuses naming the build command when no root holds a pinned interpreter
      restored:   seat_venv self-test: 20 checks, 0 failed; `git status --short` prints nothing

The two null controls (`never falls through to an unpinned interpreter`) stay
green under the mutant, which is what they are for: the base does not fall
through either, it dies.

A's clause is prose no check reads, so it carries no mutant. What it states is
pinned by an enumerator instead (fixer.md step 8): every rule sentence that
tells a seat to *wait*, below, each with its disposition.

## Null control

- A: at the merge base, `git grep -n DIRTY $(git merge-base origin/main HEAD)
  -- dev/governance/rules/ci-autofix.md` names the last section only; at the
  head it also names the wait paragraph.
- B: at the merge base, `HPO_STATE_DIR=/private/tmp/nope
  tools/audit/seat/shims/seat-python3 --version` prints
  `.../venv-ci/bin/python3: cannot execute: No such file or directory` and exits
  126; at the head it prints `Python 3.14.7` and exits 0. With a root that holds
  a venv-ci the shim is byte-for-byte the behaviour it had — the seat's own root
  is still resolved first (the existing six export arms, unchanged).
- C: the refused sentence was applied and reverted to measure it (`diff` against
  the saved copy prints nothing); the file's budget row is back at 53/678.

## Figures

    python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
      MODE: SCOPED -- 0 script(s) run, 33 scoped out.  (scope.run empty; tools/audit/ is INERT)
    python3 tests/structure.py
      STRUCTURE RATCHET PASSED
    python3 -I tools/audit/seat/tmp_paths.py --self-test
      tmp_paths self-test: 50 checks, 0 failed
    python3 -I tools/audit/seat/tmp_paths.py --check --ref HEAD
      tmp_paths: 0 refused, 0 stale allow entries at HEAD, ledger lines added since d3dbf2c3fc42
    node tools/policy/policy_lint.mjs
      TOTAL: 0 error(s) across 40 policy file(s)
      FIXTURE ok: 92 error(s) hold 243 pins across 12 check classes on fixtures/policy-rot/ and fixtures/policy-loop/
    node tools/policy/rules_sync.mjs --check
      RULES-SYNC ok: every generated rule is the generated form of its source
    node tools/policy/policy_lint.mjs --budgets
      .claude/rules/ci-autofix.md   90  96  1465  1469   (was 1456/1469 before this diff)
      .claude/rules/claim-files.md  53  53   678   681   (untouched)
    bash tools/audit/seat/seat_venv.sh --self-test
      seat_venv self-test: 20 checks, 0 failed   (14 at the base; 6 arms added)
    PYTHONPATH=tests/hastub tools/audit/seat/shims/seat-python3 tests/env_drift.py --claims-only origin/main
      claims hygiene: origin/main ok
    PYTHONPATH=tests/hastub tools/audit/seat/shims/seat-python3 tests/closure.py selftest
      ALL 57 closure shrink pins PASSED
    PYTHONPATH=tests/hastub tools/audit/seat/shims/seat-python3 tests/harness_headers.py
      ALL 109 HARNESS HEADER CHECKS PASSED
    PYTHONPATH=tests/hastub tools/audit/seat/shims/seat-python3 tests/layout.py
      layout self-test: ok
    PYTHONPATH=tests/hastub tools/audit/seat/shims/seat-python3 tests/entities.py
      ALL 2250 ENTITY CHECKS PASSED
    PYTHONPATH=tests/hastub tools/audit/seat/shims/seat-python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)
      Architecture score: dS +0.0000 NULL

Those six are the four `tests/run.sh` `run_always` scripts plus `entities.py`
and `archscore`, each run through the shim — the pinned 3.14.7 the interpreter
figures below name, not the seat's ambient `python3`.

A's class, every rule sentence that instructs a wait, and its disposition:

    git grep -n -i wait -- dev/governance/rules/
      delivery-status-tracking.md:25  a "do NOT wait" -- not this class
      gate-scoping.md:24,35           the gate lease -- not a CI run, DIRTY is irrelevant
      ci-autofix.md:20                the wait's own condition, already stated
      ci-autofix.md:77                `action_required` on a bot push -- a run exists by construction
      ci-autofix.md:14                THIS seam: closed in this diff
    git grep -n 'mutation-autofix:' -- .github/workflows/tests.yml   (the lane's `if:` at 2647)
      mutation-autofix:  `github.event_name == 'pull_request'` -- pull_request-only, so a DIRTY head never queues it

C's class, every merge-driver route a rule names:

    git grep -n -E 'merge driver|--resolve|merge=union|merge=claimnotes' -- dev/governance/rules/
      ci-autofix.md:89     the `merge=union` prohibition and merge-main.yml's resolution
      claim-files.md:2     the rule's own description line
      claim-files.md:12,21 the `claimnotes` driver and `merge=union`
      (no rule names the `ledgermerge` route -- the seam this handoff leaves open, refused below)
    git grep -rln ledger_merge -- dev/governance/rules .claude/rules .cursor/rules
      (no output, exit 1 -- no rule names the route)
    git grep -n 'merge=ledgermerge' -- .gitattributes
      22,23,24,29 -- mutation_budgets.json, structure_budgets.json, closures.json, bugclasses.json
    git grep -n -- '--resolve' -- tools/merge/ledger_merge.py
      6, 426, 563, 591, 595 -- the module docstring's "after a refused merge", `resolve()`'s R9-CI-2b note, and its arms
    # cost of the refused sentence, applied then reverted:
    node tools/policy/policy_lint.mjs --budgets   (with it)  -> .claude/rules/claim-files.md 57 53 744 681
                                                  (reverted) -> .claude/rules/claim-files.md 53 53 678 681

The seat gap this diff does not close, measured on this box (owed, below):

    which -a python3   -> /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 first
    python3 --version  -> Python 3.11.5 ; python3 tests/entities.py -> SyntaxError: f-string: expecting '}'
    tools/audit/seat/shims/seat-python3 -c 'import sys;print(sys.version.split()[0])' -> 3.14.7
    [ -e "$HOME/hpo-seats/bin" ]  -> false (the PATH entry .zshrc puts first is absent)
    python3 -I tools/audit/seat/tmp_paths.py --self-test
      ok   an instrument run from $HOME is refused   # `home-instrument`, the class that refuses a
                                                     # tracked script naming $HOME/hpo-seats/bin

## Red checks

`none`. No check is red at this head: no production Python line is added or
modified, so `mutation` measures an empty scope; no budget leaf is raised over
the merge base; and `delivery-status` grades `main`.

## Forward-carry

The seat-install half of B is owed to the owner, not to a later stage's brief:
`tools/audit/seat/shims/` is the instrument, but nothing tracked installs it
where a seat's `PATH` looks (`[home-instrument]` in `tmp_paths.py` refuses a
tracked script that names `$HOME/hpo-seats/bin`, and it is right to), so a seat
whose bin directory is absent gets `python3` 3.11.5 and `tests/entities.py`'s
`SyntaxError`. Closing it needs a machine-config change or an owner ruling, not
a `tools/` change. Named here so the orchestrator can record it against #2039.

No later stage's brief is narrowed by this diff: no stage's inputs move.

## Friction

fixer.md-step-5: stale: the dispatch brief owes an owed-work line against step 5 for omitting `run_always`, but step 5 already names it -- `dev/governance/roles/fixer.md:53-55` "Run what `scope.run` and `tests/run.sh`'s `run_always` lines name" -- landed by `a5054a3e6` "fixer.md step 5: run run.sh's run_always lines too (#2039's #2051 entry)" in #2059, so #2051's entry is fixed and no finding is owed.

## Approval

Policy: `dev/governance/rules/ci-autofix.md`, canonical, with its generated
`.claude/rules/` and `.cursor/rules/` copies (`rules_sync.mjs --check` clean).
The clause adds one condition to an existing instruction, and it is paid from
the paragraph pair it sits in — the file measured 1456/1469 tokens at the merge
base and 1465/1469 here, so no budget is raised and no `*_budgets.json` is
touched. The `tools/audit/seat/` half is an instrument, not policy. This merges
only on tvofi's approving review.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
