R10-RAISE-GATE-SHIM (issue 3128): closes the three gaps the R10-FLY-MANDATE-REVOKE-GUARD fixer stated after #3064, and the value check re-routed from #3045 round 1.

Closes #3128

## Head

Code head `dc321a18b484bed8bc5e4c247330cad788e6a7ec` (`handoff/r10-raise-gate-shim`), cut from `6125b263d94e7ea8c43d31eb483869f8d8c83019` (origin/main at the run, unmoved since: `git rev-parse origin/main`, so no second `prepr.sh` run was owed).

What changed, per carry (Carry 1 is the R10-FLY-MANDATE-REVOKE-GUARD fixer's gaps (a)-(c); Carry 2 is the re-routed #3045 round-1 value check, built as (b)'s `justified` read):
- (a) `tools/audit/seat/shims/seat-gh` refuses a comment write on the tracking issue (`gh issue comment 201`, or `gh api` at `.../issues/201/comments` with a field, `--input` or a non-GET method) unless the parent is python running `gh_comment.py`. The number is `budget_raise_gate.MANDATE_ISSUE`; `gh_calls.py --self-test` pins the shim's literal equal to it.
- (b) The train (`merge_train.py` `raise_hold`) and `budget_raise_gate.py --check-body --base --head` now judge a mandated raise's body with `budget_raise_gate.justified`, i.e. the shape and the dS value against `measured_score`, the same reader the `budget-raise-gate` job already runs at the head. Before this diff only the CI job read the value; the train and the body check read the shape alone. A diff that raises nothing is never mandated, so its section stays shape-checked alone.
- (c) **Not done: the `budget-raise-gate` job's 5-minute `timeout-minutes` is unchanged.** The brief asks for a measurement on CI's runner; this seat has no CI runner, and a local figure is not that measurement. It waits for a CI run of the job at this head; nothing here moves the timeout. Cost added by (b): `--check-body` with a diff now runs the scorer once when the diff raises a cap and a well-formed section is present (the scorer needs about 59 s of CPU on the mandated path per the carry, not re-measured here).

## Mutation proof

- Train: replacing `g.justified(self._body(pr), lambda: self._measured_score(g, h))` with `g.justification(self._body(pr))` turns red: `FAIL a mandated raise whose body quotes a dS the scorer did not measure stops, as budget-raise-gate refuses it ...` (`merge_train.py --self-test`, 443 checks, 1 failed).
- `--check-body`: replacing `justified(body, score_fn) if raises else justification(body)` with `justification(body)` turns red: `FAIL e2e: --check-body: a raise whose body quotes a dS the scorer did not measure exits 1 and says so` (`budget_raise_gate.py --self-test`, 260 checks, 1 failed).
- Shim: changing the shim's `tracker=201` to `tracker=0` makes the planted post reach the stub (rc 7) instead of being refused (rc 1); the check `mutant: the guard's issue number changed lets the planted post through` pins that the mutant differs from the shim and passes the post, so the refusal arms above are the ones that fail on the mutant.

## Null control

- Unmodified shim at the base: the planted `gh api -X POST repos/o/r/issues/201/comments -f body=...` reaches the real gh (stub rc 7); with the diff it exits 1 and the stub is never run.
- Controls that must still pass, all in `gh_calls.py --self-test`: the same post made by a python running `gh_comment.py` reaches the real gh; a shell that only names `gh_comment.py` is refused; a GET of #201's comments, a post to #202, a post to #2011 and `gh issue comment 202` reach the real gh.
- Train and check-body: a body quoting the measured figure passes (existing arms `#2209's shape ... lands with nothing re-posted` and `--check-body: a raise with a well-formed section exits 0`, now run against a fixed scorer line); the same planted body (`dS +0.0012 IMPROVES` against a measured `+0.0000 NULL`, the #3045 round-1 shape) on a diff that raises nothing exits 0.
- Not run: the #3045 round-1 body at `0ec244aa` itself. Its figure is the one planted in the arms above; the live scorer was not re-run against it here.

## Figures

- `python3 tools/audit/seat/gh_calls.py --self-test` : last line `gh_calls self-test: N checks, 0 failed` (the count is the instrument's).
- `python3 tools/policy/budget_raise_gate.py --self-test` : 0 failed.
- `python3 tools/audit/seat/merge_train.py --self-test` : 0 failed.
- `python3 tests/structure.py` : `STRUCTURE RATCHET PASSED`, no budget raised or re-recorded.
- `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"; cat "$D/scope.txt"` : `MODE: SCOPED`; `scope.run` named `tests/entities.py`, which passed.
- `tools/pr/prepr.sh` : run on the committed tree; the first run predicted `governance / instrument-self-tests UNWIRED tools/audit/seat/shims/seat-gh` because my shim comment contained the literal `--self-test`; the comment was reworded and `python3 -I tools/audit/seat/selftest_wiring.py --check` re-run.
- Toolchain: `cloud-setup.sh --check` read OK; numpy/scipy were not compared against `tests/requirements-ci.txt` and no golden or solver measurement is in this diff (CI remains the authority).

## Red checks

none known at this head. The one predicted red (`governance / instrument-self-tests` UNWIRED) was my own, repaired before the handoff; the cheaper detector is `prepr.sh` step `ci predict`, which already caught it, standing cost nil.

## Forward-carry

- Carry (c), the unmeasured `budget-raise-gate` job timeout: Carry: dismissed: not measurable by a seat with no CI runner; the orchestrator reads the job's duration from a CI run at this head and decides, this seat landing no roster write (it may push only its return refs).
- The shim's residual (PATCH of `issues/comments/<id>`, graphql): Carry: dismissed: names no issue, so no local rule can tell a #201 write from another; `gh_comment.py` guards its own patch path.

## Friction

none
