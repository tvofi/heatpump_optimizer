Discharges R10-DEPENDABOT-3414-COMPAT's two open carries (one text twice) from r10-rca-dependabot-stale-hash: no lock comment spells a hash-pinned package `name==`, `.github/dependabot.yml` names that cause, and `tests/entities.py` runs the harness's `--tree` reader so a re-apply cannot reintroduce the shape.

The cause, from `dev/audit/rca/r10-rca-dependabot-stale-hash.md` section 2: Dependabot rewrites the version at every `name==` match in a lock, the comment included, and leaves the hash lines of a pin it matched twice at the old version (9 of 9 stale pins of #3088, #3323 and #3414 had that shape, 0 of 61 fresh ones). The typing lock's own header repeated the old reading ("Dependabot rewrites only the version line of an overridden pin"); that sentence is replaced too.

What changed, and the design choice in it:
- `tests/requirements-typing.txt`: the `<overrides>` paragraph names its six overrides without versions ("each at its pin line's version") and says why the spelling is refused; the stale-cause sentence is dropped. `tests/requirements-coverage.txt`: the regenerate recipe reads the version from the pin line (`grep -m1 -E '^coverage=' ... | cut -d' ' -f1`) and does not spell it. Comment lines only: hash and pin lines are byte-identical (Figures).
- `tests/entities.py`, beside the #1548 hash-pin barrier (the block that reads every lock a workflow installs): loads `dev/audit/harnesses/dependabot_stale_hash.py` by `spec_from_file_location` (the U5 idiom) and drives its own `tree(None)` and `exposed`, rather than re-implementing the match. The check refuses `exposed>0` and also a read of `files=0`, so a reader that stopped finding the locks cannot pass by seeing nothing. A second arm plants one `name==` comment over the committed `tests/requirements-ci.txt` and requires exactly one hit, and zero on the committed text.
- `tests/closure.py` `INERT_EXCEPT` + `tests/closures.json`: the harness leaves the INERT `dev/audit/` prefix the way `record_burst_replay.py` and `r10_demand_overbook.py` did, and is in the `tests/entities.py` and `tests/harness_headers.py` closures as those siblings are, so an edit to it selects the check that reads it.

Alternatives not taken: wiring into `tests/typing_ruler.py` reads only the typing lock, and the coverage lock is one of the two exposed files. A subprocess call to `--tree` reads the same function through an exit code and loses the `files=0` precondition. Pointing each comment at its pin line by line number goes stale on the next compile.

Carry 1 (from r10-rca-dependabot-stale-hash): built in this diff. Every lock comment `--tree` listed is reworded (exposed=7 at the parent, exit 1; exposed=0 at the head, exit 0), the `.github/dependabot.yml` sentence names the cause, and `tests/entities.py` runs `--tree`. Figures and Null control carry the runs.
Carry 2 (the same text, second roster index): built by the same diff, and answered by the same runs.

## Head

`d4252d0068b23323610ae4e31e9bc94faeabf83e` (code head; base `a7628041dc02e298c5399003d4c0576391dd5c4e` = `origin/main` at `2026-11-11T07:34Z`).

## Mutation proof

`tools/audit/seat/mutant_run.py --in-place --spec <spec> --cmd "bash -c 'PYTHONPATH=tests/hastub python3 tests/entities.py > <log>'"` at `d4252d0068`, one full `tests/entities.py` per mutant (the spec's three entries are {name, file, old, new} text edits, each named below):

```
SURVIVED NULL
KILLED REEXPOSE_ASTRAL
KILLED HARNESS_COMMENT_FILTER_OFF
SURVIVED NULL                     (second run, spec of the last entry alone: the first run hit its 30 min wall)
KILLED HARNESS_READS_NO_LOCK
```

- `REEXPOSE_ASTRAL`: `tests/requirements-typing.txt` `uv, astral and sqlalchemy` -> `uv, astral==3.2 and sqlalchemy`. Red check: `FAIL no lock comment names a hash-pinned package as \`name==\` (Dependabot stale hashes)`.
- `HARNESS_COMMENT_FILTER_OFF`: `exposed()`'s `if not line.lstrip().startswith("#"):` -> `if True:` (reads no comment). Red check: `stale-hash barrier arm: one planted \`name==\` comment reads exactly one pin`.
- `HARNESS_READS_NO_LOCK`: `tree()`'s `tests/requirements[^/]*\.txt` -> `tests/no-such-lock[^/]*\.txt` (reads no lock). Red check: `FAIL no lock comment names a hash-pinned package as \`name==\`` with `summary tree=worktree files=0 exposed=0`, the `files=0` guard.

Failing test first: the check landed at `35269de654` before the rewording. `PYTHONPATH=tests/hastub python3 tests/entities.py` there: `2 of 2709 ENTITY CHECKS FAILED`, rc=1. The two failures were `FAIL no lock comment names a hash-pinned package as \`name==\`` (listing the 7 pins) and the classification check `every tracked file is either measured or deliberately classified`, which the closures commit `d4252d0068` repairs. At the head, NULL above is the whole suite green.

## Null control

The carry's null control: re-expose ONE pin (`REEXPOSE_ASTRAL` above, restored by `mutant_guard` after the run). The suite fails on that check and only that one: `1 of 2709 ENTITY CHECKS FAILED`, and its detail reads `exposed tests/requirements-typing.txt astral: ...` and `summary tree=worktree files=5 exposed=1`. The planted-comment arm stays `ok` in the same run. The unmodified head is NULL: `SURVIVED`, 0 failed.

## Figures

- `python3 dev/audit/harnesses/dependabot_stale_hash.py --tree a7628041dc02e298c5399003d4c0576391dd5c4e` -> `summary tree=a7628041dc02e298c5399003d4c0576391dd5c4e files=5 exposed=7`, exit 1. The 7 lines are `tests/requirements-typing.txt` homeassistant, astral, sqlalchemy, uv, acme, python-dateutil and `tests/requirements-coverage.txt` coverage.
- `python3 dev/audit/harnesses/dependabot_stale_hash.py --tree d4252d0068b23323610ae4e31e9bc94faeabf83e` -> `summary tree=d4252d0068b23323610ae4e31e9bc94faeabf83e files=5 exposed=0`, exit 0. The class rule is the harness's own `--tree` enumerator over every tracked `tests/requirements*.txt` (files=5), so every seam it returns is closed in this diff. It is the instrument `tests/entities.py` now runs.
- Hashes unchanged: `for f in tests/requirements-typing.txt tests/requirements-coverage.txt; do diff <(git show a7628041dc02e298c5399003d4c0576391dd5c4e:$f | grep -v '^#') <(git show d4252d0068:$f | grep -v '^#') >/dev/null && echo "$f: every non-comment line byte-identical parent->head"; done` printed both lines.
- The reworded coverage recipe resolves as before: `grep -m1 -E '^coverage=' tests/requirements-coverage.txt | cut -d' ' -f1 | uv pip compile - --python-version 3.13.15 --python-platform x86_64-manylinux_2_28 --generate-hashes --no-header --no-annotate -o $D/body`, then `cmp` against the committed body below the header, printed `RECIPE REPRODUCES committed coverage body byte-identically`.
- `python3 dev/audit/harnesses/dependabot_stale_hash.py --self-test` -> `self-test OK`, rc 0. Harness sha1 `11714849f90e5c0532138e5cb05cd201b842c90e`, unchanged by this diff.
- `PYTHONPATH=tests/hastub python3 tests/typing_ruler.py` (reads the typing lock) -> `ALL 9 typing-ruler checks PASSED`, `ALL 12 typing-ruler source checks PASSED`, rc 0.
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`.
- Scope: `python3 tests/closure.py select --diff a7628041dc02e298c5399003d4c0576391dd5c4e` -> `MODE: FULL -- every test script runs` (`tests/closure.py changes the gate itself`). Run locally: `tests/entities.py`, `tests/typing_ruler.py` and `tests/structure.py`; the rest is CI's.

## Red checks

none

## Forward-carry

none

## Friction

none
