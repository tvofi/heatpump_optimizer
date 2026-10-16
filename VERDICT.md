Fix review: blocked 353f7f3c4dafe94b1eb3b152af79024eb0af368f class-open: the absolute self-import spelled `import <pkg>.m`, the `m._x` binding an absolute self-import makes, and `import_module(name=..., package=__package__)` are not edges; each keeps the runtime import and reads IMPROVES (dS +0.1466 / +0.0825 / +0.1466) at the repaired instrument

bus-nonce: 0493fa2dc273df844deca944ca40130c

PR #2320, R10-ARCHSCORE-COVERAGE part 3, **round 2**. Reviewer: rev-2320-r2, detached worktree at the head. Contract: fix-review.md from origin/main `81ae048e8`; the preamble diff over `dev/governance/roles/` is empty.
Measured head: `353f7f3c4dafe94b1eb3b152af79024eb0af368f`, re-read before posting and unchanged.
Round-1 instrument for every before/after: `4a4107fcde80e55b5b9a24748554f0d4491b6b59`. Merge base `81ae048e8`; `git merge-tree --write-tree origin/main HEAD` exits 0.

Part 3's own delta is judged as the tree diff `134810973...HEAD` (origin/main is merged in, so the merge-base diff covers it). Instruments I did not build and did not re-run: CI's arch-score, mutation, closures, fast, composed-proof and coverage lanes, cited from the head's check-runs.

## Blocking

**1. harness: class-open (step 6 / step 14).** The repair closed all four round-1 seams — I reproduce that — but it closed exactly the four *spellings* it was shown, and the rule's own enumerator names three further spellings, which I carry as four plants, that the diff does not handle and the body does not disposition. Two of the three rows are ones the body's `## Figures` table asserts, in its own words, are closed.

Each plant replaces `silent_mode.py`'s module-level `from .optimizer import _utc_step_starts` with another spelling of the same runtime coupling, leaves every other score metric alone, and reads IMPROVES at the repaired instrument:

| plant | spelling | head instrument | dS |
|---|---|---|---|
| `c1_import_abs` | `import custom_components.heatpump_optimizer.optimizer as _o` + `_o._utc_step_starts` | 22/17 -> **21/16** | **+0.1466 IMPROVES** |
| `c2_import_abs_plain` | `import <pkg>.optimizer` + the full dotted attribute read | 22/17 -> **21/16** | **+0.1466 IMPROVES** |
| `c3_from_abs_mod` | `from custom_components.heatpump_optimizer import optimizer as _o` + `_o._utc_step_starts` | 22/17 -> 22/**16** | **+0.0825 IMPROVES** |
| `c6_im_name_kw` | `importlib.import_module(name=".optimizer", package=__package__)._utc_step_starts` | 22/17 -> **21/16** | **+0.1466 IMPROVES** |

- **`import <pkg>.m` (`c1`, `c2`).** The body's table states `| `import <pkg>.m` | closed here (27) |`. Attempt 27 plants only the *from* form (`from custom_components.heatpump_optimizer.optimizer import _utc_step_starts`), and `metrics/layering.py` reaches `cross()` only from an `ast.ImportFrom`: an `ast.Import` goes to `_roots`, where `_self_module` returns not-None and the name is dropped "*so it is no longer counted as an external root either*" — and no edge takes its place. The coupling is therefore invisible in both arms. Nothing runs it: `silent_mode` reaches the optimizer for its private `_utc_step_starts` at module level, and the reach leaves `layer_violations` and `private_cross_module` together.
- **`c3`.** `_targets` resolves the absolute self-import to the `optimizer` module (so the edge survives and `layer_violations` stays 22), but `modalias`, which drives every `m._x` crossing, is built from `mod.imports` entries recorded as `("mod", name)`; an absolute self-import is not one, so the private read off `_o` is not a crossing. The body's C18 row ("`m._x` through a module binding ... counted (counter C18, attempt 22)") and ABOUT.md's C18 row ("the same respelled with the package's full path (27)") do not qualify the *binding's* provenance, and attempt 27 does not plant an attribute read at all.
- **`c6`.** `_dynamic_name` reads the anchor from `node.args[1]` or the `package` keyword, but returns `None` when `not node.args` — and `importlib.import_module`'s first parameter is named `name`, so calling it by keyword is the same constant-name call with the same static anchor. Attempt 26 plants only the positional form, `importlib.import_module(".optimizer", __package__)`.

**Behaviour is unchanged, not argued.** I executed the spellings against a stand-in package (`optimizer.py` defines `_utc_step_starts`, `silent_mode` spelled five ways) and imported it for real: the module-relative form and `c1`, `c3`, `c6` all bind *the same object* (`same_object=True`, evidence `exec_identity.txt`). A fifth candidate, `__import__(".optimizer", fromlist=[...], level=1)` (`c9`), also reads IMPROVES +0.1466 but is **refused as a plant**: it raises `KeyError: "'__name__' not in globals"` in CPython 3.14.7, so it is not code a seat can ship.

**The fixer's own enumerator names the first seam and cannot see that it is open.** `dev/audit/harnesses/archscore_layering_seam_census.py` (the census this round added, and the closest thing the body has to "the rule's own enumerator") classes `ast.ImportFrom` of the package *and* plain `ast.Import` of it under the one counter `absolute_self_import` (lines 47-50), while its docstring says it counts "the instances of each spelling the new rule **resolves**". Its planted precondition tree (lines 92-99) plants only the from form, so `planted_absolute_self_import=1` and the census cannot distinguish the resolved spelling from the unresolved one. It reported `absolute_self_import=0` over the corpus, which is what the agent's note "my grep found no hits" says — so the corpus is untouched by all four seams today. That is the same status round 1 gave its own four: latent, but a seat that moves an import into one takes the score.

**None of the four occurs in today's package** (`git grep` finds no `import custom_components.heatpump_optimizer`, no `from custom_components`, no `import_module(name=`, no `__import__(` with `level=`). The repair is local to `metrics/layering.py`: an `ast.Import` arm in `graph()`, `modalias` grown to the absolute self-import's binding, and `_dynamic_name` reading the `name` keyword. A calibration case or attempt for each would pin it, as round 1 asked for the else/not branch.

**2. carry-missing (step 10).** The body names the destination and states it as a precondition: "**`dev/governance/dimensions/D7.md`, via R10-BRIEFS-FOLD** ... this pull request does not merge until that carry is on main." Opened, it is not there:
- `git grep -n -i layer_violations origin/main -- dev/governance/` -> no hits; nothing on main outside `tools/audit` names `private_cross_module`.
- `dev/governance/dimensions/D7.md` on `origin/main` carries none of the five blind spots, the attempt ids or the C19 precondition.
- `dev/programme/rosters/wave-r10-groups.json` `groups[47]` (R10-BRIEFS-FOLD) carries 5 entries; `carry[4]` is part 1's (#2293) and **none is part 3's**. This PR's diff does not touch the roster.
- The practice is measurable: part 1's carry landed at `ffcf1a46a` (2026-10-15 23:38:33 +0200), **before** #2293 merged (2026-10-16T00:10:50Z). The R10-BRIEFS-FOLD entry also landed before R10-GATE-YIELD.

Counter-argument I record rather than hide: the roster sets `groups[47].after = ["R10-ARCHSCORE-COVERAGE", ...]` and `groups[25].carry[1]` says "This group runs BEFORE R10-BRIEFS-FOLD, so the folded D7 brief can cite the new counters" — so the programme's own ordering puts the fold *after* this group, and round 1 treated the analogous item as non-blocking. What blocks here is narrower and is the body's own sentence: it declares the carry a merge precondition, and at this head the carry exists nowhere in the tree. Either land the carry, or drop the precondition sentence and let the roster's ordering say it.

## Red checks at the head (step 11)

`pr-contract` is **red** at the head (`117083222814`, started 2026-10-16T16:38:32Z, after the body edit) and the body's silence is the reason:

    record   red-history  21 commit(s) between origin/main and this head, every failure conclusion across them: budget-raise-gate, closures, coverage-ratchet
    ERROR   [pr-body] /tmp/pr-body.md: check `coverage-ratchet` is red and `## Red checks` does not name it.

`coverage-ratchet` (`117074952157`, 16:19:56Z) is red on `every module >= 95.0 %` — `early_cutoff.py: 81.53 %` — a `custom_components` module this diff does not touch, so the red is main's own; the omission is still the body's. `## Red checks` names pr-contract, closures, `tests/entities.py` and budget-raise-gate and does not name it. I state my reading of step 11's timing clause because it decides the class, not the fact: a `pr-contract` run *did* start after the last red concluded and *did* check the body, and the class its wording maps to when the answer is recorded is `root-cause-unrecorded` — but the clause "while it refuses, wait or hand back unverdicted" reads as a bar on posting, so **I do not rest this verdict's class on it**; the class above is `class-open`, which is independent of the body contract. Round 1 blocked on this same check being red at its head, so posting is the established practice in this PR's history.

Minor, and not part of either block: `## Head` names `7a8244a8ed078249e844ac6de70ecd1bc0c50bd4` with the *same* paragraph it gives `353f7f3c4`, and `git merge-base --is-ancestor 7a8244a8e HEAD` is false — it is a sibling merge of the same code head made a minute earlier (`18:07:34` vs `18:08:14`) that is not in this head's history. The rest of the chain is correct and `pr-contract`'s walk accepted it.

## Verified

- **Finder's harness at both ends** (ARCH2-s4 export from `b202335e2`, sha1 `score_delta.py` `35570991`, `layering.py` `314f35a4` — both match the body). Copied into a throwaway worktree of `4a4107fcd` and of the head, `PYTHONPATH=tests/hastub`:
  - `RESULT base(round-1 instrument) P1 delta_S=+0.4460 IMPROVES`; `RESULT base(head instrument) P1 delta_S=+0.4460 IMPROVES`; both `layer_violations 21->18 +0.2115`, `private_cross_module 19->16 +0.2345`, `unused_boundary_imports 1->1`. The patch spells its imports the ordinary way, so it is flat across the repair, exactly as the body says.
  - `RESULT --revert delta_S=+0.0000 NULL`, no metric moved, at **both** instruments.
  - Finder's census `layering.py` at both: `closure_store=28 modules (optimizer IN)`, `closure_snapshots=29`, `closure_setpoint_check=22`, `closure_quiet_windows=21`, `closure_silent_mode=20`, `private_cross_module_names=17` — byte-identical between the two runs but for `load1`. Its `--ref` default is the round's baseline, so this is stated as *flat*, not as agreement, which is how the body states it too.
- **Round-1's four plants, re-run** with the round-1 reviewer's own `plant.sh` + `lay2.py` (from `origin/verdict/2320`) at *its* instrument and at the head's — the positive control for my plant harness:
  - round-1 instrument: `p1_tc_else`, `p2_not_tc`, `p3_import_module_const`, `p4_absolute` each `21/16`; `p0_none` `22/17`. **All twelve lines reproduce round 1's `plants.txt` byte-for-byte.**
  - head instrument: `p1`..`p4` each `22/17/1` — **unmoved**; `p9_lazy_control` `22/17` (C17 works), `p10_tc_only_control` `21/16` (the by-design exclusion).
  - full vector, `plantscore.py`: at the round-1 instrument `p1`..`p4` each `dS=+0.1466 IMPROVES moved={'layer_violations': '22->21', 'private_cross_module': '17->16'}`; at the head `dS=+0.0000 verdict=NULL moved={}`. The repair is confirmed at the metric and at the score.
  - `p5` (`+0.0641 IMPROVES`), `p5b` (`WORSENS`, tripwire 1->2), `p6` (`WORSENS`, computed_attr_access 32->33), `p7`, `p8` are unmoved by the repair and remain the OPEN items ABOUT.md now lists.
- **Ablations, re-derived with the switch that is real** (the body's own disclosure that M2/M3 are no-ops because `vector.py` assigns `layering.PRIVATE_ATTRS`/`UNUSED_IMPORTS` from `ARCHSCORE_ABLATE` on every measurement). On the thirteen cases: `M0` (no mutation) moves nothing and prints `RED TEAM 7/7 attempts read NULL or inadmissible; IMPROVES: none` — the body's enumerator line, reproduced. `A1=C17` MOVED `rt_21` only. `A2=C18` MOVED `rt_22` **and `rt_26`**. `A3=C19` MOVED `rt_23` only. This matches the body's table, including the round-2 change that A2 now reopens `rt_26` as well.
- **The mutants that pin this round's repair are killed** (`mut_repair.py`, mine, named as mine). Each is an in-place predicate edit on the committed head, restored with `git checkout`, over the same thirteen cases:
  - `M7` the guard read as the whole `If` (`return [node]`): `RED TEAM 6/7 ... IMPROVES: rt_24_layer_guarded_else` — MOVED `rt_24` (NULL -> IMPROVES). Matches the body.
  - `M9` `_dynamic_name` returns None: `RED TEAM 6/7 ... IMPROVES: rt_26_layer_import_module`. Matches.
  - `M10` `_self_module` returns None: `RED TEAM 5/7 ... IMPROVES: rt_26..., rt_27...` — MOVED `rt_26` **and** `rt_27`. Matches, including the body's note that M10 is the coarser of the two.
  - `M8` the guard read from `ast.unparse(node.test).endswith("TYPE_CHECKING")` (which matched a *negated* test): `RED TEAM 6/7 ... IMPROVES: rt_25_layer_negated_guard`. Matches.
  My first mutant run emitted literal `\n` in two edit strings, so its `M7` and `M8` arms measured an unmutated tree and are void; they are re-run here and this verdict is the re-run's. That is my harness defect, disclosed rather than dropped, and it is the same failure shape the body discloses for its own M2/M3.
- **`expected.json` and the corpus.** `corpus_vectors.json` is **byte-identical** to `4a4107fcd`'s (`git diff --numstat` empty), confirming the body's `cmp` claim; the 435-line change in the merge-base diff is part 3 adding the `layering` job, not a re-record. `tests/ci_budgets.json` is untouched in round 2 (`git diff 4a4107fcd...HEAD` empty) and its three new rows are the *only* change to it against main — `archscore.layer_violations 22`, `archscore.private_cross_module 17`, `archscore.unused_boundary_imports 1`, no existing row moved, `hub_solve_writes` still 41. `ci_ratchet.archscore_metrics()` at the head derives exactly `22 / 17 / 1`, so the rows are at the derived value and no number the diff moves is the instrument's.
- **The fixer's census, re-run** at the head (their instrument, named as theirs): `planted_absolute_self_import=1`, `planted_constant_dynamic_import=2`, `planted_guard_not_body=4`, `planted_guard_not_body_imports=2`, `PRECONDITION ok` — the body's `1 / 2 / 4 / 2` and its `PRECONDITION ok`, reproduced. `dynamic_names=['threadpoolctl']` matches too. The corpus arm I did not re-run (87 trees); its `absolute_self_import=0` is what my grep found independently.
- `git merge-tree --write-tree origin/main HEAD` exits 0, no `MERGE-CLAIM` marker needed: no conflict. `VERSION` (7.0.0), the manifest version and the notes heading are untouched. Neither claim file is in the diff, so there is no claim to reconcile (`tests/env_drift.py --claims-only origin/main` -> `claims hygiene: origin/main ok`). `tests/structure.py` -> `STRUCTURE RATCHET PASSED`. `score.py --diff origin/main` -> the body's `dS +0.0000 NULL` (no package file changes).
- Head check-runs: 45, all concluded; 28 success, 15 skipped, 2 failure (`pr-contract`, `coverage-ratchet`). `closures`, `arch-score`, `mutation`, `fast (3.14)`, `coverage`, `composed-proof`, `budget-raise-gate`, `delivery-status`, `nightly-status` all success — the round-1 `closures` red and the `budget-raise-gate` red are cleared at this head.
- **Disclosed as mine, not the finder's**: the seam probe `classprobe.py` (16 plants, head instrument, run twice — once against the working tree and once against a `git archive HEAD` copy frozen before any mutant ran, identical), the `contoso` identity probe, and `mut_repair.py`. The round-1 reviewer's `plant.sh`/`lay2.py`/`plantscore.py`/`mut.sh` are named as the round-1 reviewer's, read from `origin/verdict/2320`.

## RESULT lines

    RESULT head 353f7f3c4dafe94b1eb3b152af79024eb0af368f measured; unchanged at post
    RESULT finder score_delta P1 round1_instrument=+0.4460 IMPROVES head_instrument=+0.4460 IMPROVES
    RESULT finder score_delta P1 --revert round1_instrument=+0.0000 NULL head_instrument=+0.0000 NULL
    RESULT finder layering closure_store=28 (optimizer IN) private_cross_module_names=17 at BOTH instruments
    RESULT round1_plants round1_instrument: p1..p4=21/16 each; head_instrument: p1..p4=22/17 unmoved
    RESULT round1_plants dS round1_instrument=+0.1466 IMPROVES each; head_instrument=+0.0000 NULL each
    RESULT class_open c1_import_abs=+0.1466 IMPROVES c2_import_abs_plain=+0.1466 IMPROVES c3_from_abs_mod=+0.0825 IMPROVES c6_im_name_kw=+0.1466 IMPROVES c9_dunder_rel_level=refused(raises in CPython 3.14)
    RESULT class_open c0_none=+0.0000 NULL (baseline control, no plant)
    RESULT ablation M0=nothing_moves A1(C17)=rt_21 A2(C18)=rt_22+rt_26 A3(C19)=rt_23
    RESULT ablation M0 RED TEAM 7/7 attempts read NULL or inadmissible; IMPROVES: none
    RESULT mutants M7=rt_24 M8=rt_25 M9=rt_26 M10=rt_26+rt_27 (each NULL -> IMPROVES, matching the body's table)
    RESULT merge_tree rc=0
    RESULT structure STRUCTURE RATCHET PASSED; env_drift claims hygiene: origin/main ok
    RESULT ci_ratchet derived 22 / 17 / 1 == the three new rows, no existing row moved
    RESULT head check-runs 45 concluded: 28 success, 15 skipped, 2 failure (pr-contract, coverage-ratchet)
    RESULT forward_carry D7.md on origin/main carries nothing; R10-BRIEFS-FOLD carry list has no part-3 entry

## Friction

- `fix-review.md` step 11 cannot be executed as written when the refusal *is* the trigger. This head's `pr-contract` refuses because `## Red checks` omits `coverage-ratchet`; that same refusal is, on the clause's literal reading, the "while it refuses, wait or hand back unverdicted" bar on posting. Either the clause means "no pr-contract run has *evaluated* this body yet", or a `root-cause-*` block on that very omission can never be posted. I posted keying on `class-open`, which the clause does not touch, and said which reading I used; a later seat should adjudicate the clause rather than this verdict.
- `pr-contract`'s `## Head` walk accepted a head chain containing a commit that is not an ancestor of the head (`7a8244a8e`). The walk keys on the *shape* of the chain, so a stray sibling merge with a plausible paragraph passes.
