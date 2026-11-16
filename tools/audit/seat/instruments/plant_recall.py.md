# `plant_recall.py`

- `plant_recall.py` — planted-defect recall, decision 0018 section 5's first
  held-out check (R11-PRE-ROUND-METRICS). No seat is scored on it. Its rules,
  refusals and null control are the script's docstring; the commands are:
  - **Plant, after `audit-find.js`'s Prepare step and before its Finders
    phase** (the orchestrator runs it from the checkout; the plant list is the
    planting seat's, a seat that is neither finder, orchestrator nor
    evaluator, kept in `../audit-r<N>-plants/`, outside every tree a finder
    reads):

        python3 -I tools/audit/check_scopes.py --repo . --ref <baseline> --population \
          > ../audit-r<N>-plants/population.txt
        python3 -I tools/audit/seat/plant_recall.py plant --plants ../audit-r<N>-plants/P.json \
          --tree ../audit-r<N>-baseline --population ../audit-r<N>-plants/population.txt \
          --not <orchestrator> --not <evaluator> --not <each finder seat>

    It refuses, writing nothing, a planter among the `--not` names, a list
    inside the tree, a tree inside a git work tree (the tree or any ancestor
    holding `.git`, a linked worktree's `.git` file included, so neither the
    isolated dimensions' worktrees nor any subdirectory of one takes a plant),
    a list missing either the natural or the configuration space, a config
    cell that is no population level, an old text not in its file exactly
    once, and two plants in one file whose old texts overlap. Plants sharing a
    file land at their old text's place in the original file.
  - **Count, after `audit-verify.js`'s judge:**

        python3 -I tools/audit/seat/plant_recall.py recall --plants ../audit-r<N>-plants/P.json \
          --judge-input dev/audit/rounds/round<N>/JUDGE-INPUT.json --judge dev/audit/rounds/round<N>/JUDGE.json

    One `FOUND`, `LOST` (named only by findings refuted, unreproduced or
    never judged: a miss) or `MISSED` line per plant, under recall whole, per
    space and per kind. An empty plant list or no judge verdict prints
    `recall  unread (<why>)`.
  `--self-test`: one case per refusal and per count rule, the null controls,
  and one mutant per predicate.
