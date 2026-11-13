# BLOCKED: r10-hotfix-train-context-pages (repair of the second mutation-survivor block, #3516)

Question: `handoff/r10-hotfix-train-context-pages` moved to 7090e74587bbebe2371d01be682b57b1512c9d93 during this run (another seat's repair of the same block, body at cd41e1eea5), and this seat's head f52985b40053ef00cb8b741d02bcfe6df9f4719f does not descend it; which is taken — and, if this one, may it be handed off on a `tools/pr/prepr.sh` run whose only refusal is the `closures` step, which refuses `origin/main` itself in this container?

Nothing of this seat is on `handoff/r10-hotfix-train-context-pages` or `handoff-body/…`. The code is the parent of this commit; the body is on `handoff-wip/r10-hotfix-train-context-pages-body`.

## What this head has that 7090e745 may not

Both descend 853c9f47. This head answers the dispatch's "close the class": a full `mutant_run.py --diff` pass over the whole delta, every survivor killed or dispositioned, not only M5, M8 and M9. cd41e1eea5's body names no such pass; whether 7090e745 survives the mutants below was not measured here.

Killed here beyond the verdict's three (each printed `SURVIVED` by the diff pass at e7e5ecdfc0, the step head with only M5, M8 and M9 answered):
- `rollup_walk`'s `return payload` under `except` deleted, and its final `return merged` deleted;
- the Train's `if code:` guard off, its `raise OSError(...)` deleted, and `[-160:]` made `[-161:]`;
- M6 (the `except` returns `merged`), which the verdict dismissed as equivalent: it changes the object returned, and a row now asserts it by identity;
- M8b, `$after` used in `ROLLUP_Q` and not declared;
- five fixture literals no row read, removed.

## Mutation evidence

- `python3 tools/audit/seat/mutant_run.py --diff f44e761c19dc...HEAD --cmd 'python3 tools/audit/seat/merge_train.py --self-test' --report-only` at f52985b40053: nine `SURVIVED` lines, all equivalent. Eight are `STMT_DEL` of a `check(...)` statement the delta adds (lines 7561, 7568, 7573, 7580, 7602, 7612, 7628, 7634): a deleted assertion leaves nothing to fail. One is `7601 CONST_SWAP`, a faked `gh` exit code `1` made `2`: any nonzero exit is the same failed read to `if code:`.
- `mutant_run.py --spec` (NULL survives) at fa1e82e816, whose `merge_train.py` is byte-identical to this head's (`git diff --quiet fa1e82e816 f52985b40053 -- tools/audit/seat/merge_train.py`): M2, M4, M5, M6, M8, M8b, M9, M11 KILLED; M10 SURVIVED, equivalent (at the page cap either object carries `hasNextPage` true, so `platform_gate` gives the same `unread` and the same reason). The re-run at f52985b40053 was cut off by a container restart after `KILLED M5`.
- M2 and M11 each turn one check red, "a later page whose oid differs from the first page's is unread"; the earlier body's "2 checks" and "NameError" were wrong.
- `python3 tools/audit/seat/merge_train.py --self-test` at fa1e82e816: 666 checks, 0 failed.

## The prepr refusal

`REFUSE closures -- run ./tests/derive_closures.sh --single <script> …`. The line names no script because the failure is not `UNDER-SCOPED`. By hand, on a kept recording at f52985b40053:

    ./tests/derive_closures.sh --scripts-from <list> --record-only --out-dir <rec>     # exit 0, entities.py rc 0
    PYTHONPATH=tests/hastub python3 tests/closure.py check --in-dir <rec> --partial     # exit 1

prints `INERT READS UNDER-APPROXIMATED` for `tests/entities.py` over 4261 files.

Null control: the same two commands in a detached worktree of `origin/main` at f44e761c19dc, with none of this branch: exit 1, the same heading, 4197 files. The refusal is not a function of this delta.

Cause, as far as measured: `strace -f -y -e trace=openat,execve` over `python3 tests/entities.py` shows the opens are `git reset --hard --no-recurse-submodules` populating the temporary baseline checkouts `tests/env_drift.py` creates (`baseline-<pid>-<n>` under a temp directory), each file opened `O_WRONLY|O_CREAT|O_EXCL` by a path relative to that checkout; the recording counts them as reads of the repository's files of the same relative path. `tests/closures.json` lists 77 inert reads for `tests/entities.py` and `tests / closures` was green on #3516, so CI's recording does not see them. Why this container's does is not established.

Not done, each being outside this group: committing a `tests/closures.json` that lists those files (a false recording), editing `tests/closure.py` or `tests/env_drift.py`, or setting a `PREPR_SKIP_*` switch to obtain a clean line.

Every other prepr step at f52985b40053 is `ok` or `skip`, the body check included (`pr-body` 0 errors, `figures` 0 refused, `carry` 0 unrouted, `push order` ok against the pull-request branch as it then stood, `ci predict` no closures red predicted).

## Two earlier refusals of the same step, both resolved by merge

- `failed while being recorded: tests/entities.py (exit 1)`: prepr exports `HPO_GATE_PRIORITY=2` on a hotfix branch, and the two "gate lease priority" rows then order both waiters alike. `origin/main` carries the fix in `tests/gate_lock.py`; f52985b40053 merges it.
- `push order`: `origin/fix/r10-hotfix-train-context-pages` had moved (main merged, #3516's delivery row); fa1e82e816 merges it. That branch has moved again since, to fbda69ef77, which this head does not hold.

## Scoped gate, run directly at fa1e82e816

`env -u BASH_ENV python3 tests/entities.py`: 2709 checks pass. `tests/doc_claims.py` and `python3 tests/structure.py` pass (structure also at f52985b40053, in prepr's merged-structure step).
