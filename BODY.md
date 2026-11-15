R11-PRE-NEW-DIMENSIONS, p1 of 2: `tools/audit/prepare_baseline.sh`'s `ISOLATED_DIMS` gains D16, alone. One file, seven lines; no policy file, no brief, no budget. Finder-critical: p2 cannot go green before this is on main.

Why it is split. p2 (the two dimension briefs D16 and D17, their universes, scopes, rotation and the driver's schedule) adds D16 to `audit-find.js`'s `ISOLATED`, and `check-wave-script.mjs` requires that set to equal this file's `ISOLATED_DIMS`. CI's `wave-script` job restores the base's copy of this file before it grades (it is on the job's pinned list), so in one pull request the two lists are graded unequal: `python3 tools/pr/ci_predict.py` on p2's head predicts `governance / wave-script` red, quoting `prepare_baseline.sh ISOLATED_DIMS [D0,D3,D9,D11,D13,D14,D15] != audit-find.js ISOLATED [D0,D3,D9,D11,D13,D14,D15,D16]`. The grader names the route: the list may lead the driver by a dimension with no brief and no DIMS entry, and by nothing else. So the entry merges first (`fixer.md` step 5, decision 0013 Consequences; the design note at `a9377bcf47` says to report such a refusal as the split).

Why D16 is isolated: its finders owe two one-line perturbations in the write path, which `COMMON.md` allows only in an isolated worktree, and its `upgrade` state reads the previous tag's package from `.git` (design note section 3.4, `Design review: approve` at `daa950c68c`). D17 perturbs configuration only and stays in the export.

p2 waits at `refs/heads/handoff-wip/r11-pre-new-dimensions`, a WIP handoff until this is on main: its code head is `4f73a0c5e8`, under the commit that adds the BLOCKED note and p2's draft body. It is stacked on `handoff/r11-pre-briefs-census` (#3625) by the orchestrator's ruling of 2026-11-15T19:50Z; this p1 is cut from `origin/main` alone and needs neither. p2's copy of this file differs from this head's in one comment line (the export's dimension list gains D17), so main merges into p2 without a conflict here.

The comment added says the entry led the driver and the brief by one merge; it is worded to be true at this head and at p2's.

## Head

4d381a338f9bca214ad14c91713b18352da401f1

## Mutation proof

The line this pull request adds is what p2's CI goes red without. p2's tree (`910986a0bc`) graded by `node tools/policy/check-wave-script.mjs`, the file being main's in both trees:

- with main's copy of `tools/audit/prepare_baseline.sh` (what CI restores today): 221 passed, 2 failed: `every dimension brief is in the round driver's DIMS, and its worktree lists agree`, naming the two lists unequal, and `ISOLATED_DIMS may lead the driver only by a dimension with no brief and no DIMS entry`.
- with this head's copy (what CI restores once this is on main): 223 passed, 0 failed.

## Null control

- At this head the grader prints `ISOLATED_DIMS may lead the driver only by a dimension with no brief and no DIMS entry (pending: D16)` as `ok`; at `origin/main` (98847b99d7bb3238686efd6869f805c89c6d1ff1) the same line reads `(pending: none)`. The tolerance is the grader's own, with its own controls on that line: a list leading by D2, a declared dimension, is refused, and one leading by a dimension that also has a brief and a DIMS entry is compared.
- `bash -n tools/audit/prepare_baseline.sh` exits 0. The script loops over `ISOLATED_DIMS` to create one worktree per entry at the baseline, so a round prepared between this merge and p2's gets a D16 worktree no seat is dispatched to: unused, and removed with the others.

## Figures

- `node tools/policy/check-wave-script.mjs` at 4d381a338f9bca214ad14c91713b18352da401f1: 223 passed, 0 failed; at 98847b99d7bb3238686efd6869f805c89c6d1ff1: 223 passed, 0 failed.
- `git diff --stat origin/main 4d381a338f9bca214ad14c91713b18352da401f1`: 1 file changed, 5 insertions, 2 deletions, `tools/audit/prepare_baseline.sh`.
- `tools/pr/prepr.sh` at 4d381a338f9bca214ad14c91713b18352da401f1 with `PREPR_SKIP_CLOSURES=1`: rc 0: every step `ok` or `skip`, none refused, among them `ci predict` (no closures, fast, governance or instrument red predicted against 98847b99d7bb), `merged structure` (`STRUCTURE RATCHET PASSED`, HEAD merged with origin/main), `wave-script` and `carry`; the diff adds no `.py` line, so the diff-mutant step drew no mutant.

<!-- figure-block: scope-line mb=98847b99d7bb3238686efd6869f805c89c6d1ff1 head=4d381a338f9bca214ad14c91713b18352da401f1 -->
~~~text
MODE: SCOPED -- 0 script(s) run, 33 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none: this head has no CI run of its own, and no check in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints has gone red on a commit of this branch.

## Forward-carry

- p2, the group's artifact, waits on this merge at `refs/heads/handoff-wip/r11-pre-new-dimensions` (code head `4f73a0c5e8`): after it, merge `origin/main` into p2 (and the census once #3625 merges), re-run `tools/pr/prepr.sh` there, and hand p2 off on the same refs. The step ref is therefore not deleted by this handoff. Carry: R11-PRE-NEW-DIMENSIONS
- Carry 0 (the actuator-write half of intake carry 175: a cell ledger over write and hold sites times plan states, the target the plan's computed value and never a document): p2's, not this file's. Built there as `enumerate.py d16-writes --cells` with `--ledger` and the actuator-write brief's oracle section. Carry: R11-PRE-NEW-DIMENSIONS
- Carry 1 (from r11-pre-briefs-census, item dcd38e1b: the two universes ported under the prototype's names for the new briefs to cite, with `rotation.json` and `scopes.json` on distinct keys): p2's. Both briefs cite them there and `enumerate.py --briefs` runs them. Carry: R11-PRE-NEW-DIMENSIONS
- R11-PRE-FINDER-CONTRACT's p2 is not on main either (#3621 is its grader alone); this group's p2 was built against main's driver and schema as they are, and its body states the three places that differs from the approved design. decision: orchestrator, which of the two p2s merges last. Carry: R11-PRE-NEW-DIMENSIONS

## Friction

- designer: unclear: the design note names `tools/audit/prepare_baseline.sh` among the files the driver commit edits and says no p1/p2 split is needed while `check-wave-script.mjs` is untouched; the file is on the `wave-script` job's pinned list, so the split is forced by it and was found only at the pre-handoff `ci_predict.py` run, after p2 was built. Cheaper detector: `ci_predict.py --only graders` at the commit that touched the file. Carry: dismissed: one occurrence; the predictor caught it before any push to a handoff ref, which is its job
