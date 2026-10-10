tvofi's standing instruction of 2026-10-09 is that the resume, plan and handover
docs are regenerated **continuously**, not at session end.
`tools/audit/seat/state_docs.py` already ran one regeneration (the generators,
the guarded write set, the orphan-ref push, the mirror); the recurring half was
a loop the orchestrator kept in its own scratch directory. Decision 0013 calls
that a defect on its face -- an instrument the programme runs, living outside
the tree, which no later session can test and `worktree_gc.sh` can collect. This
lands the loop inside the instrument that already owns the write set and the
push, as `state_docs.py beat`, and pins it in the gate so a later seat finds it
by running one script rather than by reading this body.

Closes #2102.

## Head

`3dbbfcc01` (the branch tip on `handoff/r9-ro-14`; every figure below was taken
at it).

## Mutation proof

The acceptance is the new arms, driven twice: once directly, and once through
`tests/entities.py`, which is the check a reviewer sees.

| mutant | what was deleted | arms that went red |
|---|---|---|
| A | the memo check (`if tip == recorded: return 0, recorded`) | 5 |
| B | `return rc, recorded` → `return rc, tip` (record on refusal) | 2 |
| C | `run(["git", *spec])` (the roster re-fetch) | 5 |
| D | `if a.once:` → `if True:` (one pass and out) | 2 |

Mutation A through the gate:

    $ python3 tests/entities.py
      FAIL tools/audit/seat/state_docs.py --self-test passes, beat arms included
      1 of 2251 ENTITY CHECKS FAILED

and its five named arms, verbatim from `python3 tools/audit/seat/state_docs.py
--self-test`:

    5 self-test check(s) failed: arm 2: no push (got: 3), arm 2: and nothing
    at all is written (the mirror is not made) (got: ), arm 3: the refused push
    returns non-zero (got: 0), arm 3: the tip was NOT recorded (got: ), arm 3:
    exactly one push, on the retry (got: 3)

B: `2 self-test check(s) failed: arm 3: the tip was NOT recorded (got: ), arm 3:
exactly one push, on the retry (got: 2)`.
C: `5 self-test check(s) failed: arm 1: the pass re-fetched the roster ref …`.
D: `2 self-test check(s) failed: arm 4: and beats again for the next one (got:
), arm 4: and is still running, not one pass and out (got: )`.

Each arm is the null control for the one beside it. Arm 1 (a moved tip pushes
once) is what makes arm 2 (an unchanged tip pushes none) meaningful, and arm 2
is driven with the roster ref moved on **both** the remote and the driver, so
the bytes a memo-less beat would regenerate differ from the tip's -- without
that, a beat that ignored the memo would still be a no-op and arm 2 would pass
vacuously. Arm 3 asserts that the retry lands with nothing but the tip file
changed; D shows that is arm 4's subject too, since a beat that recorded the tip
on a refusal, or stopped after one pass, leaves the second change unlanded.

## Null control

At the merge base the deliverable is absent, and the tree cannot see the file at
all:

    $ git show c729bb32:tools/audit/seat/state_docs.py | grep -ciE 'beat'
    0
    $ git show c729bb32:tools/audit/seat/state_docs.py | grep -c 'ok("'
    17

`state_docs.py` sits under `tools/audit/`, which `tests/closure.py` declares
INERT, so a change to it selected **no** script -- the arms the issue names
would have been run by hand or never. The unmodified head is the other control:
`python3 tools/audit/seat/state_docs.py --self-test` prints `state_docs
self-test: all checks passed`, and the gate check is green.

One deliberate limit, named rather than left to be found: a pass is triggered by
the watched ref (`refs/heads/main`) alone, the shape the group's brief fixes, so
a roster edit that lands with no merge is picked up at the next merge rather
than at once. Watching the roster ref as well costs one more `ls-remote` pattern
and one more memo field; it is not here because the brief that specifies the
beat names one ref.

## Figures

Rule for the two counts: the number of lines matching the pattern, at that ref,
in that one file. Rule for every measurement below: the instrument's own summary
line, quoted, at the head named above.

| figure | command |
|---|---|
| `0` → `47` `beat` lines, base → head | `git show c729bb32:tools/audit/seat/state_docs.py \| grep -ciE 'beat'` |
| `17` → `40` self-test arms, base → head | `grep -c 'ok("' tools/audit/seat/state_docs.py` |
| `ALL 2251 ENTITY CHECKS PASSED` (head), `1 of 2251 ENTITY CHECKS FAILED` (mutant A) | `tools/audit/seat/shims/seat-python3 tests/entities.py` |
| `MODE: FULL` — "tests/closure.py changes the gate itself, so every closure is suspect" | `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D` |
| `closure: committed closures cover every file this run touched` (rc 0) | `python3 tests/closure.py record tests/entities.py --out-dir $D && python3 tests/closure.py check --in-dir $D --partial` |
| `STRUCTURE RATCHET PASSED` | `python3 tests/structure.py` |
| `Architecture score: dS +0.0000 NULL` | `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` |
| `NO UNCLAIMED DRIFT: 56 scenario(s) checked against c729bb32`, `NO STALE FIXTURE` | `GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) python3 tests/golden.py` |
| `claims hygiene: origin/main ok` | `python3 tests/env_drift.py --claims-only origin/main` |
| `0 refused, 0 stale allow entries` | `python3 tools/audit/seat/tmp_paths.py --check` |
| `TOTAL: 0 error(s) across 40 policy file(s)`; corpus `~59899`, unmoved | `node tools/policy/policy_lint.mjs --budgets` |
| `109 HARNESS HEADER CHECKS PASSED`, `57 closure shrink pins PASSED`, `layout self-test: ok` | the `run_always` lines of `tests/run.sh` |

`MODE: FULL` is the gate scoping this diff, not a failure: it touches
`tests/closure.py` and `tests/closures.json`, both GATE_FILES.

The closure recording above is Darwin, so it carries the hook and the spawn
argv but no `strace`: the child-open class a Linux recording adds is not in it.
What it does show is that the four paths this diff adds to `tests/entities.py`'s
closure are exactly the four the recording names (`handover_prompt.py`,
`plan_table.py`, `resume_doc.py`, `state_docs.py`, beside the `record_row.py`
and `roster_lib.py` already listed), and that nothing is UNDER-scoped; the one
over-scoped entry, `tests/golden/card_claimed_drift.txt`, is main's, not this
diff's.

## Unpinned sites

none.

## Red checks

`closure.py no-copies` refused under this workstation's bare `python3` (3.11),
which cannot parse a 3.12 f-string at `tests/entities.py:3935`, and it refuses
there identically at the merge base:

    $ git worktree add --detach <scratch>/base c729bb32
    $ cd <scratch>/base && PYTHONPATH=tests/hastub python3 tests/closure.py no-copies
    File "<unknown>", line 3935
      ([f'{h[0]}:{h[1]} in {h[2] or chr(60) + 'module>'}' for h in _p2_stray])
    SyntaxError: f-string: f-string: expecting '}'

The cheaper detector exists and costs nothing: the pinned interpreter the tree
already ships, `tools/audit/seat/shims/seat-python3` (venv-ci, 3.14), which is
what the `PRE-PR:` line below was taken with. Under it `no-copies` passes, so
this is the workstation's `python3` on `PATH`, not a repair the tree owes. The
other refusal this branch saw was `'Closes #2102' closes #2102; not in the
intended list` -- `preflight.sh` refusing a closing keyword the caller had not
declared intended; it is the wrong invocation, not a defect, and `prepr.sh
<BODY.md> 2102` is the right one.

## Forward-carry

`none`. The beat's own instructions are in the instrument it lives in
(`state_docs.py`'s docstring, its `--help`) and in the tree's inventory,
`tools/audit/seat/INSTRUMENTS.md`, in this same diff; no later stage's brief
owes a change for it.

## Friction

`none`.
