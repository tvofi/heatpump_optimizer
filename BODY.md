R11-PRE-TOOLCHAIN-PIN part 3 as dispatched (carries 10-12), at the approved design `a37706d599ca28414378bda7813068b79fd716d6`. Two carries are built and one is re-measured and carried:

- Carry 10. `tools/audit/seat/cloud_dispatch.py` `dispatch_group` required an approved design for an L or XL group and then rendered a fixer payload that named no design, and for a group over five pending carries a part line cut by carry index, while the design cuts by seam. `design_approved` now returns the approved tip and the new `design_line` renders it as one generated brief line with its fetch command. Beside a part line it adds that the design's parts are not the part line's: the part line is what the seat builds, in the shape the design gives it.
- Carry 11. `tools/audit/seat/cloud-setup.sh` gains `--kernels <command>`: the command once per OpenBLAS kernel class of `KERNELS`, the seat's pin lifted for it. A class OpenBLAS does not report loading is named as not run, never green; no class run is exit 2. `--check`'s OK line names the pinned class and the verb, so each seat reads it at start.
- Carry 12 is an orchestrator action and an open owner decision: re-measured under `## Figures`, its line under `## Forward-carry`.

For the owner's review, because it states what a seat does: the sentence the part's design line adds (the part line is the seat's scope, the design its shape) is the reading the seats of parts 1 and 2 each took for themselves, now written in the payload. No policy file is changed: a sentence for `tests/README.md`'s BLAS kernels section naming `--kernels` was written and taken out again, because that file is the owner's to change and sits nine tokens under its `files_tokens` cap.

Also repaired, found while re-measuring carry 11: `dev/audit/harnesses/r11_honest_starts_runs.py kernels` exited 1 on main under every kernel class, because the header it ended its second block at was named in the harness and #3616's block has since landed in front of it; the run crossed into that block and raised `NameError: name '_r9f12_seed_cfg' is not defined`. The block now ends at the first `# --- ` header after it on the tree read.

Alternatives that lost. Carry 10: *the split follows the design's parts* needs a machine-readable part list in the design note (a change to the designer's and design reviewer's contracts) and has no answer for a carry that lands after the approval, as carries 9-12 of this group did. *Only name the design, say nothing of the cuts*: leaves the contradiction the carry reports for the next seat to resolve by itself a third time. Carry 11: *lift the pin* (leave `OPENBLAS_CORETYPE` unset in the seat) trades one fixed class for whichever the container's processor selects, and the golden fixtures' floats need the fixed one (`cloud-setup.sh --check`). *A new instrument file*: the pin's owner is `cloud-setup.sh`, and the verb is the pin's own exception. *A `prepr.sh` step running the scoped scripts under each class*: four times the scoped run on every handoff, for a defect class that needs a check of a solve in the diff; the verb is run when the diff adds one. *Reuse `r11_honest_starts_runs.py kernels`*: it drives two named blocks of one group.

## Head

35077969fab7cd6f60183711e6de3dd5595d9f3e, merge base 38bf516bdd73f926ee9639ffda7b9ca5163fd50e with origin/main.

## Mutation proof

Predicates mutated, never tails. `python3 dev/audit/harnesses/r11_toolchain_mutants.py`, the group's harness, makes each mutant as one exact one-occurrence replacement in a copy of `tools/` and runs the mutated file's own self-test there; a mutant is killed only on a `FAIL` row. This diff adds eleven to it:

- `cloud_dispatch.py`, each `verdict=killed`: `D-design-line` (the payload names no design), `D-part-clause` (a part's design line says nothing of the two cuts), `D-part-always` (an unsplit group's line speaks of parts), `D-order` (the design line after the part line), `D-stale-approval` (an approval of a design that has since moved returns its tip), `D-no-verdict` (a design with no verdict ref reads the verdict fetched last; `prepr.sh`'s diff-mutant step found this one alive, and the row `a design with no verdict ref is not approved by another group's verdict of the same commit, fetched just before` was added for it).
- `cloud-setup.sh`, each `verdict=killed`: `K-pin-kept` (the command runs under the seat's pinned class every time), `K-probe` (a class OpenBLAS does not load is run and counted), `K-red` (a red class is not counted red), `K-none` (no class run exits 0), `K-list` (`KERNELS` is the pinned class alone).
- Failing test first, carry 10: with the new self-test rows over the merge base's `design_approved` and `dispatch_group`, `python3 -I tools/audit/seat/cloud_dispatch.py --self-test` printed `FAIL a fixer of a group with an approved design is given the design's ref and SHA in one generated line, its last` and `FAIL a part of a designed group names both cuts: ...`. Carry 11's rows were written beside the verb, not before it; the five `K-` mutants are their proof.

## Null control

- Carry 10: a fixer dispatched `--design-exempt`, and one of a group that takes no design, is given no design line; an unsplit designed group's line carries no word of parts; five or fewer pending carries with no design still render byte-identically (the existing row).
- Carry 11: a command green under every class exits 0 naming each; the same red-under-SkylakeX command run under the pinned class alone is green, which is the defect.
- `M0` of each of the harness's five files, nothing mutated, prints `failed=0 verdict=null-ok`.
- The detector on the defect it was written for, under `## Figures`: red at the tree before #3602 restated its two clauses, green at the tree after.

## Figures

- `python3 -I tools/audit/seat/cloud_dispatch.py --self-test`: `cloud_dispatch self-test: 181 checks, 0 failed`.
- `bash tools/audit/seat/cloud-setup.sh --self-test`: `cloud_setup self-test: 30 checks, 0 failed`.
- `python3 dev/audit/harnesses/r11_toolchain_mutants.py`: `RESULT mutants=37`, `RESULT survived=0`.
- The detector on the defect it was written for. In a detached worktree at `5d9f00db01` (the parent of `303e10f8c8`, the commit of #3602 that restated the two kernel-dependent clauses), with `PYTHONPATH=tests/hastub` and one thread, `bash <this head>/tools/audit/seat/cloud-setup.sh --kernels python3 tools/audit/seat/features_block.py <start marker> <end marker>` over that pull request's two blocks: the duty-switch block closes `red on SkylakeX`, exit 1; the starts-and-runs block closes `red on SkylakeX Sandybridge Nehalem`, exit 1; both read `Haswell exit 0`, the seat's pinned class. The same two commands at `303e10f8c8`: `red on none`, exit 0, every class run. The markers are the harness's `_BLOCKS` in `dev/audit/harnesses/r11_honest_starts_runs.py`.
- `bash tools/audit/seat/cloud-setup.sh --kernels sh -c 'OPENBLAS_VERBOSE=2 python3 -c "import numpy" 2>&1 | grep -qx "Core: $OPENBLAS_CORETYPE"'`, on the real BLAS with the seat pinned to Haswell: `ran SkylakeX Haswell Sandybridge Nehalem; red on none; not run none`, so each run loaded the class it was given and not the pin.
- Carry 11's own re-measurement, `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r11_honest_starts_runs.py kernels`. At the carry's merge base `e352724335` the tree does not hold that group's section (its marker occurs 0 times in `tests/features.py`) and every run prints `did not complete`, so the figure is unreadable there. At this head's merge base, with the harness as it was: the replaced clause of the duty-switch block reads `REPLACED False` under SkylakeX and True under the other three; the replaced clause of the starts-and-runs block reads False under SkylakeX, Sandybridge and Nehalem and True under Haswell; and the mode exits 1 with `blocks that failed a check or did not complete 4`, the stale end marker. At this head: the same four False readings under the same classes, every block completes (`ALL 103 FEATURES BLOCK PASSED`, `ALL 51 FEATURES BLOCK PASSED`) and the mode exits 0 with `blocks that failed a check or did not complete 0`. The carry's control holds: the clauses #3602 replaced read False under three classes and True under the seat's.
- Carry 12, re-measured 2026-11-17T01:17Z: `git ls-remote origin 'refs/heads/toolchain/*'` prints nothing, and `python3 -I tools/audit/seat/toolchain.py behind . --fetch` exits 1 with `toolchain: REFUSED origin/toolchain/stable is absent: it is never read as main; create it once with ...`, the line the beat row's digest repeats. The init has not been run.
- The roster's count behind carry 10, at `handoff/audit-r10-roster` f223cd88f6: `roster_lib.pending_carries` over this group returns all thirteen indices, and `cloud_dispatch.part_split` of them `0-4, 5-9, 10-12`, after #3645 (carries 0-4) and #3654 merged.
- Gate scope: `python3 tests/closure.py select --diff 38bf516bdd --workdir <dir>` names `tests/doc_claims.py` and `tests/entities.py`; both exit 0 at this head with `PYTHONPATH=tests/hastub`, beside `tests/env_drift.py --claims-only`, `tests/harness_headers.py`, `python3 tests/structure.py` (`STRUCTURE RATCHET PASSED`) and `node tools/policy/policy_lint.mjs` (0 errors).
- `python3 tools/pr/ci_predict.py`: no closures, fast, governance or instrument red predicted against the merge base.
- Step 8, the class's seams. Carry 10's class is a generated brief line that leaves a seat to choose between two sources: `git grep -n 'parts +=\|pline\|dline' -- tools/audit/seat/cloud_dispatch.py` returns every site that appends a generated line to a fixer's brief: `roster_lib.brief_lines` (the consumers line and the enumeration line, neither of which names a second source of scope: already guarded), and the part line and the design line (closed in this diff). Carry 11's class is a variable the seat's environment fixes and CI's does not: `bash tools/audit/seat/cloud-setup.sh --variables` prints eight, of which `OPENBLAS_CORETYPE` is the one whose value CI draws per runner (closed in this diff); `PATH` and `HPO_TYPING_PYTHON` select the interpreters CI pins alike, the four `GIT_` names are identity and `RUNNER_TEMP` a directory.

<!-- figure-block: scope-line mb=38bf516bdd73f926ee9639ffda7b9ca5163fd50e head=35077969fab7cd6f60183711e6de3dd5595d9f3e -->
~~~text
MODE: SCOPED -- 2 script(s) run, 31 scoped out.
~~~
<!-- /figure-block -->

## Unpinned sites

`prepr.sh`'s diff-mutant step, its command `python3 -I tools/audit/seat/cloud_dispatch.py --self-test` in place, left these alive after the row above was added:

- tools/audit/seat/cloud_dispatch.py:604 RETURN_DEL: equivalent. With the return for an absent design tip dropped, the function goes on with an empty tip and returns "" at its last line unless a verdict reads `Design review: approve ` with nothing after it, a line `bus.sh push-design-verdict` does not write; the self-test run with this line replaced by `pass` prints 0 failed.
- tools/audit/seat/cloud_dispatch.py:907 STMT_DEL: deletes a self-test row, not production code; the production line the row pins dies as `D-design-line` in the harness.
- tools/audit/seat/cloud_dispatch.py:909 STMT_DEL: the same; the row is the null control of 907's.
- tools/audit/seat/cloud_dispatch.py:912 CALL_DEL: the same; its production line dies as `D-part-always`.
- tools/audit/seat/cloud_dispatch.py:992 STMT_DEL: the same; its production line dies as `D-no-verdict`.
- tools/audit/seat/cloud_dispatch.py:997 STMT_DEL: the same; its production lines die as `D-part-clause` and `D-order`.

## Red checks

none

## Forward-carry

- Carry 12, not built. The orchestrator's `python3 -I tools/audit/seat/toolchain.py promote --init --repo tvofi/heatpump_optimizer` is still owed (figure above), and who may push `refs/heads/toolchain/stable`, and under which ruleset, is the design's open owner decision; until both, carry 9's sites part has no ref to read. One option for that ruling, raised and not made because the design has the init run by hand: the beat's `toolchain-promote` row passes `--init` while the ref is absent, which creates it at the newest machinery-green commit of main by the same walk and the same credentials as every later promotion. Carry: dismissed: not a finding of this diff but that group's roster carry 12, which this part leaves open for the orchestrator's init and the owner's ruling
- `KERNELS` holds the four classes the tree already measures; which classes CI's runners have loaded was not read from CI's logs here (`tests/run.sh` prints the class as each run's `blas` line). Asked for `Zen`, OpenBLAS on this processor reports loading Haswell, so that class is not separable in this seat. Carry: dismissed: `KERNELS` is the union of the pin and the classes `.github/workflows/kernel-points.yml` measures; a class added there is added here by the diff that adds it

## Friction

- fixer.md: contradiction: the roster still counts as pending the carries a merged part built or dismissed (figure above), so the next part's generated line re-cuts them: the dispatch at `2d7161a4b7` named carries 0-4 a second time (the `BLOCKED.md` at tag `archive/handoff-wip/r11-pre-toolchain-pin-p3`), and this part's carries were named by hand. The design line of this diff does not reach that: the marks are the roster's. Carry: dismissed: the marks are the orchestrator's record step at each part's merge and change no stage's brief; the group is closed to carries on the round's roster
