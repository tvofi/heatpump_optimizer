Fix review: blocked 8ff3432a965df930fb54e7aa6ffd52bf210e5f3f mutation-vacuous: dropping hot_files from _owned_lane survives the self-test and moves a custom_components group out of Core model

bus-nonce: c69f2b2f30f4a04a12cfa21cd9ef4474

Round 1. Reviewed from a detached worktree at 8ff3432a965df930fb54e7aa6ffd52bf210e5f3f, merge base 80016a71f567d936450d8708abcbb79d9e8071d7. The finder's harness: none is committed. This is an owner-reported hotfix, so the harness is the owner's ruling plus the live plan. I built the enumeration below myself and disclose it as mine.

Owner ruling (tvofi 2026-11-06), verbatim: "The HTML plan seems to incorrectly place some instrument or CI fixes in the core model lane, fix that".

## Block

- Claim: the PR's predicates in `_owned_lane`/`roster_lane` are each pinned by a named self-test check (brief item 3; body `## Mutation proof`).
- Evidence: mutant m8 replaces `list(group.get("files") or []) + list(group.get("hot_files") or [])` with `list(group.get("files") or [])` in `tools/plan/replan.py` `_owned_lane`. On a `git archive` copy of the head, `python3 tools/plan/replan.py --self-test` then exits rc=0 (`ev/mutants-all.txt`, line `MUTANT m8-hotfiles rc=0`).
- Metric: the probe group `{"kind": "fix", "files": ["tools/ci/gate.py"], "hot_files": ["custom_components/heatpump_optimizer/coordinator.py"]}` is drawn as `Core model` at the head and as `Instruments` under m8 (`ev/m8-probe.txt`). The same holds with a bare `hot_files: ["coordinator.py"]`, and `work_class` flips to `instrument` with it. So the arm that keeps a group touching the integration in the core lane, which is the brief's item-1 null control, is unpinned. The self-test's controls put the bare filename and the `custom_components/` path in `files` only. Yet on the live roster, bare names occur in `hot_files` (for example R10-FAHRENHEIT `hot_files: ["coordinator.py"]`).
- Perturbation: m8 itself; the harness (`--self-test`) does not move under it, which is the defect.
- Live effect today: none. All 11 roster groups whose `files` are all non-product but whose `hot_files` are not are `kind: instrument`, so the kind rule places them before `_owned_lane` (`ev/m8-live.txt`). The block concerns the pin, not the current plan.
- Remedy (small): add self-test cases such as `_lane(["tools/x.py"])` with `hot_files=["custom_components/heatpump_optimizer/x.py"]` and with `hot_files=["coordinator.py"]`, each expecting `Core model`, then re-run m8 and show it killed.
- Second item for the same re-cut: `## Red checks` says `none`, but at this head `gate` concluded `failure` twice. Both were edit runs: run 42317750046 (job 128235103524, 00:24:12Z) and run 42318557432 (job 128237840805, 00:32:01Z). Job 128235103524's log reads "FAIL run(s) [42317750091] at this head are still being judged; their gate decides". That is the mutual edit-run deferral of the open R10-HOTFIX-GATE-BUSY-DEFER, and code run 42317750091 decides. The body must name it so (the packet refuses `red-unanswered`). The body predates both reds (body updated 00:21:40Z).

## Findings

- Follow-up: a CI or instrument hotfix whose roster entry is `kind: fix`/`hotfix`, has no `class: instrument`, and lists a bare tool basename in `hot_files` (for example `merge_train.py`, `gate.py`) stays Core model under this rule. That is because a bare filename is treated as possible integration code. Today no open group hits this (my enumeration of every Core-model group at the head finds each owns a `custom_components/` file or is product or owner work with no files), and the brief's rule (1) prescribes this conservatism. The residual risk sits in roster data: the roster seat writing `hot_files` as bare names. Carry: R10-HOTFIX-PLAN-LANES | dismissed: brief rule (1) mandates bare filename stays Core model; not a defect of this PR, recorded so the re-cut's self-test pins it in hot_files

## Evidence

- RESULT head self-test: `python3 tools/plan/replan.py --self-test` → `self-test: 0 failed` (`ev/selftest-head.txt`).
- RESULT mutants (my own, on `git archive` copies of the head; `ev/mutants-all.txt`):
  - m1, deleting `if owned := _owned_lane(group): return owned`: rc=1, with 6 lane checks failing.
  - m2, deleting the `INSTRUMENT_KINDS`/`class` fallback: rc=1, 3 checks.
  - m3, dropping the `class == "instrument"` arm: rc=1, `lane: a roster class instrument with no files is Instruments`.
  - m4, `not all(` → `not any(`: rc=1, `lane null control: a mixed group stays Core model`.
  - m5, dropping the `not files` guard: rc=1, both no-files controls.
  - m6, dropping the tooling exclusion from `user_docs`: rc=1, `docs plus a tool is Instruments, not Docs`.
  - m7, dropping the `kind == "doc"` arm: rc=1, `a docs-only doc group is Docs`.
  - **m8, dropping `hot_files`: rc=0 (survives)**.
  - m9, removing `docs/` from the prefixes: rc=1, 3 checks.
  - m10, emptying `_NON_PRODUCT_FILES`: rc=1, 3 checks.
  - m11, removing `rca` from `INSTRUMENT_KINDS`: rc=1, `an RCA group with no files is Instruments`.
  - m12, setting `user_docs` to always true: rc=1, `a tests-and-tools group is Instruments`.
  - The body's 5 mutants (my m1, m2, m3, m4 and the user-docs rule) reproduce as killed.
- RESULT live lanes (JSON), with my own enumeration (`ev/lane-enum.txt`).
  - Setup: plans were built at main 80016a71f and at the head. Both used roster `origin/handoff/audit-r10-roster` at 1f11980fa7cfbe23767975b332ea4bb52dfb336d (roster blob 9ed12e88f758) and `--start 2026-11-06T22:00:00Z`.
  - Plans: `ev/plan-base.json`, `ev/plan-wt.json`.
  - Groups: 351 at both ends. The body says 350, because the roster gained R10-HOTFIX-SELFTEST-TIMEOUT after the body's measurement.
  - Main: Core model 126, Instruments 192, Docs 2, Learners 8, Product UX 14, Replay 9.
  - Head: Core model 62, Instruments 251, Docs 7, Learners 8, Product UX 14, Replay 9.
  - Moved: 64, all from Core model (59 to Instruments, 5 to Docs). The body says 63 (58 + 5); the difference is exactly R10-HOTFIX-SELFTEST-TIMEOUT, whose only file is `.github/workflows/governance.yml`. After that adjustment, the body's 63-row table matches my list group for group.
  - No group moved in any other direction.
- RESULT moved groups are correctly moved. Under my own path classification (custom_components/ = integration; tools/, tests/, .github/, .claude/, dev/, docs/ and root records = instrument), none of the 64 owns a `custom_components/` file or a bare filename. Three own no file and move by kind or class: R10-CARRY-RESIDUE-2 (`class: instrument`), R10-PLAN-PRIO (`kind: tooling`) and R10-RCA-RELEASE-TAG (`kind: rca`). R10-MARKETPLACE-EXTRAS (`kind: production`) owns only `.github/workflows/*`, `tests/*` and `dev/governance/dimensions/D10.md`, so Instruments is correct.
- RESULT null control: every group still Core model at the head owns a `custom_components/` file, or owns no file and is product or owner work. Those are R10-CARD-VOICE, R10-CATALOG-PR, R10-COMBI-TANK and R10-STORE-RACES, plus the three done groups the body itself discloses: R10-RCA-HEADMOVED, R10-ROSTER-PUSH-RACE and R10-NIGHTLY-SLOW-ROLLING. No Core-model group at the head owns only instrument paths.
- RESULT HTML: `tools/audit/seat/plan_page.py` is unchanged in the three-dot diff and reads `pg["lane"]` (plan_page.py:241). I rendered both plans (`ev/plan-base.html`, `ev/plan-wt.html`, offline snapshot `{"open_prs":[],"merged_prs":[],"issues":[]}`) and parsed each drawn bar's y against the lane bands (`ev/html-lanes.txt`).
  - Drawn lane ≠ JSON lane: 0 at both ends.
  - Drawn bars: 67 at both ends.
  - Core model drawn: 24 at main, 10 at the head. Instruments: 39 → 51. Docs: 1 → 3.
  - 14 open groups move in the drawing. The body says 13; the extra is R10-HOTFIX-SELFTEST-TIMEOUT.
- RESULT summary: main `stamps 6 | CI 7762.5 min | batches 63`; head `stamps 3 | CI 7087.5 min | batches 60`, at this roster. The body's 6→3 / 7875.0→6975.0 / 64→59 were at an older roster blob, so the stamps figure reproduces and CI and batches move with the roster. The duration change flows through `work_class`, which reads `roster_lane`, and the body discloses it.
- RESULT scope: `python3 tests/closure.py select --diff 80016a71f…` → `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` `tests/entities.py` could not run in this container (`ModuleNotFoundError: homeassistant`, `ev/entities.txt`), so CI's run of it is cited.
- RESULT protected paths: the three-dot diff touches only `tools/plan/replan.py` and `dev/programme/delivery/3265.md`. No `custom_components/`, `VERSION`, manifest, `RELEASE_NOTES.md` or `*_budgets.json` change, and the delivery row is in the diff.
- RESULT merge: `git merge-tree --write-tree origin/main 8ff3432a…` → rc=0, tree 7500ec8b1266729b3f9eee3be04090eaa5de38e6, with origin/main at 80016a71f (the merge base).
- RESULT `## Head`: it names 8ff3432a965df930fb54e7aa6ffd52bf210e5f3f, which is the head measured. `origin/fix/r10-hotfix-plan-lanes` was still 8ff3432a… at verdict time.
- RESULT role-file currency: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- CI at verdict: `merge_train.py classify` → `RED 8ff3432a… pending: none red: gate` (`ev/classify.txt`, `ev/classify-history.txt`). The only reds are the two edit-run `gate` deferrals named above. Code run 42317750091 was still running jobs at verdict time (`tests / claims-autofix` at 00:33:45Z), so its gate has not decided. This verdict does not block on CI.
