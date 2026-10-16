Fix review: merge c777f855b9d87f8218ed3650aead1e92537f51e1

bus-nonce: d8023917c443c8a931bbfce4a8140e4a

Round 3 (resolution delta). Round 1 was `blocked c777f855 … harness: class-rule-missing`, body-only; this review judges the body alone. **The head is unmoved** — `c777f855b9d87f8218ed3650aead1e92537f51e1`, same six commits, tree `529ddf2644211c4917a550cdb0751f6a1bcd8d4b`, `git ls-remote origin refs/heads/fix/r10-registry-leak` agreeing with the PR API at post time (`ev/r3_remote_head.txt`, `ev/HEAD.txt`). So the code is byte-identical to the tree I measured: **every round-1 number survives, and says so rather than being re-reported as fresh**. What I re-took for this round is the cheap part — the body, the checks it re-triggered, the conflict, and the two arms of the rule I had not run at the base. Round-1 measurements and the mutation proof stand unchanged: `ev/finder_base_r5.txt`, `ev/finder_head_r5.txt`, `ev/finder_base_{r1,r8}.txt`, `ev/finder_head_{r1,r8}.txt`, `ev/finder_{base,head}_perturb.txt`, `ev/enum_base_default.txt`, `ev/enum_head_{default,clean,plant}.txt`, `ev/M_{0,A,B,C,D,E,F}*`, published at `review/2329 a6d45ec579d623901ec421c431636c2e363f0001`.

## The delta is exactly what my block asked for

`diff -u` of the body I blocked and the live body is 28 lines, in two hunks, plus a trailing newline (`ev/r3_body_delta.diff`, `ev/r3_body_round1.md`, `ev/r3_body_round3.md`):

1. The intro sentence now **names the rule**: "The class's enumeration rule, `dev/audit/rounds/round10/D14/N-registry-leak/registry_leak.py`, returns four more module-level containers that no function keys by a coordinator (`const.INPUT_MAX_AGE_MINUTES`, `coordinator._FENCED_CAUSES`, `coordinator._WORKER_FALLBACK_CAUSES`, `store._NEWER_ON_DISK`), each reading `held=0` and `pins_key=0` at both ends."
2. `## Figures` gains a **`Seam rule (fixer.md step 8)`** block with the command and a disposition for **every** seam the rule returns — the one closed in this diff, the four already guarded, and the four formerly absent — plus a `--plant` sensitivity control.

Nothing else moved: `## Mutation proof`, `## Null control`, `## Unpinned sites`, `## Closures`, `## Red checks`, `## Forward-carry`, `## Friction` and the `## Head` line are byte-identical to round 1.

**Each of the four seams my round-1 block named is now in the body, twice** (the intro and the disposition list), and `grep -c` reads 2 for each of `INPUT_MAX_AGE_MINUTES`, `_FENCED_CAUSES`, `_WORKER_FALLBACK_CAUSES`, `_NEWER_ON_DISK`, where round 1 read 0. All nine returned seams are dispositioned.

## The added figures, re-derived (step 8)

Rule `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/N-registry-leak/registry_leak.py`, the issue's own, in tree at both ends.

- **"returns nine `SEAM` lines"** — nine at the head (`ev/r3_enum_head_static.txt`) and nine at the base (`ev/enum_base_static.txt`), and the two lists differ in exactly one field: `early_cutoff.py:134` at the base is `early_cutoff.py:137` at the head, the three comment lines the diff adds. The rule's population is derived from the tree, not hand-listed, which is the whole point of the clause. Confirmed.
- **"at the head `torn_alive=0` and every `pins_key=0`"** — round 1, `ev/enum_head_default.txt`. Confirmed, and it stands.
- **`early_cutoff._STATES`: `pins_key=3` at the base `dec1a2645534`, `0` at the head `c777f855b`** — `ev/enum_base_default.txt` and `ev/enum_head_default.txt`. Confirmed.
- **the four already-guarded registries read `pins_key=0` at both ends** — `ev/enum_base_default.txt` (`boost._STATES`, `boost._PLAN_BASES`, `pump_arbiter._STATES` each `held=3 pins_key=0`; `debugger._COLLECTORS` `held=0`), `ev/enum_head_default.txt` (all 0). Confirmed.
- **the four formerly-absent containers read `held=0` and `pins_key=0` at both ends** — the same two files, one row each, 0 on both fields at both ends. Confirmed.
- **Sensitivity control: "`--plant` re-introduces one line at the head and reads `boost._PLAN_BASES pins_key=3`, `torn_alive=3`"** — `ev/enum_head_plant.txt`, exactly. Confirmed; this is what makes the head's zero a measurement rather than a blind path, and it is the figure I would have missed.
- **"the base arm reads `torn_alive=3` with `early_cutoff._STATES pins_key=3`"** — `ev/enum_base_default.txt`, exactly. Confirmed.

`dev/audit/rounds/round10/D14/N-registry-leak/registry_leak.py` is in the tree at the head, so the new figure command resolves: the post-edit `pr-contract` run prints `ok PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/N-registry-leak/registry_leak.py --rounds 3` and `FIGURES: 8 resolved, 0 not verified, 0 refused` (`ev/r3_pr_contract_1507.txt`).

## Checks after the body edit (step 11)

The body edit re-ran three workflows at the same SHA, all at 15:07Z: `arch-score`, `budget-raise-gate`, `pr-contract`, all `success` (`ev/r3_head_checks.txt`). Across all 45 runs at the head, **no run is red** — the same reading as round 1, re-taken rather than carried. The post-edit `pr-contract` prints `PR-BODY: 0 error(s)` and `record red-history: 6 commit(s) between origin/main and this head, every failure conclusion across them: mutation`, so the range's only failure conclusion is still `mutation` and `## Red checks` still names and answers it. No trigger.

## Conflicts (step 13), and the rest, re-taken

`git merge-tree --write-tree origin/main c777f855b9d87f8218ed3650aead1e92537f51e1` exits **0**, stderr `LEDGER-MERGE: resolved tests/closures.json` (`ev/r3_merge_tree.txt`); the branch still touches neither claim file. The head's own `pr-contract` prints `no version edit: origin/main...c777f855b9d87f8218ed3650aead1e92537f51e1 moves none of VERSION, the manifest version or a notes heading`. Drift, claim files, `claims-for: 7.0.0`, structure, archscore, `tmp_paths`, the closure scope (21 scripts), `tests/features.py` at 4138, the mutants and the null control are round-1 measurements on this same tree and I did not re-run them; step 12's rule is that I say which survive, and all of them do.

## Two things recorded, neither a block

1. **A figure I could not re-derive, unchanged from round 1.** The autofix ledger entry `tests/mutation_ledger/killed_by/early_cutoff.py/arm.GUARD_OFF.d460246f.json` records `failed=4` for its `if False:` mutant. The pin holds — rc 0 -> 1, killed by `tests/features.py` — but my run of that exact substitution measures **3** failures (`ev/M_B_guard_if_false_features.log`). Reported as unverified, not as confirmed, and not a block: the entry's substance re-derives and the body does not quote the count.
2. **Pre-flight noise in the CI invocation, not this PR's defect.** The post-edit run's pre-flight step prints `REFUSE 'Closes #2231' closes #2231; not in the intended list`. `tools/pr/preflight.sh` takes the intended-issue list as **arguments** and `.github/workflows/pr-contract.yml:304` invokes it with none (`… < /tmp/pr-body.md; fi|| true`), so that arm REFUSEs every `Closes #N` on every pull request in this repository and its non-zero exit is swallowed. `Closes #2231` is correct here — `#2231` is this group's sole issue and sole `fixes` entry in `wave-r10-groups.json` — so nothing is owed by this branch. Filed as a separate suggestion, not as a block on #2329.

## Verdict

The block is cleared, the code has not moved, and every figure the body now quotes is one I have re-derived myself. **`merge`** at `c777f855b9d87f8218ed3650aead1e92537f51e1`, which is the head I measured in round 1 and the head the body names under `## Head`.
