Fix review: blocked dd5faa50c0a87aec310975128c18b172e052af3a carry-missing: own-group

bus-nonce: 7b43b7bea027ca679b7cc3d6ff4cf21f
pending-ci: gate

Round 1. Measured at dd5faa50c0a87aec310975128c18b172e052af3a from a detached worktree; merge base and origin/main are both ee64358be7eeccaec5178a923cb3b83a18a924a0. Reviewer on cloud seat, interpreter without homeassistant.

## Block

`fix-review.md` step 10 and `fixer.md` ("`Carry: <own group>` only names a pending owner or orchestrator ruling, or a split part the approved plan names"). Two body items carry to the PR's own group and name neither exception, and one of them is in no tree:

1. `## Red checks`, item `scp2-raise-predict-needs-body` (`tools/pr/prepr.sh` prints no raise line without a body). Own-group, no ruling or plan part named, and `git grep scp2-raise-predict-needs-body origin/handoff/audit-r10-roster -- dev/programme` prints nothing at 17e9b6518c812f9c2f2e3c982b24239100fbd728: it exists only in the PR body. Its seam is `tools/pr/prepr.sh`, not this group's. Fix wanted: route it to that seam's owner (a live group, or a `dev/programme/carries/carry-<N>.json`), or `Carry: dismissed: <reason>`.
2. `## Friction`, item `scp2-layout-vs-citation` (the layout guard against policy_lint's citation-presence fixture). It is on the roster (P2 carry list, 17e9b6518c81) but own-group with neither exception; its seam is the layout guard and the fixture. Fix wanted: the same re-route or a dismissal.

Not blocking, same shape, say which exception: `scp2-handover-seats` is the orchestrator's record edit at the merge rather than a ruling; `scp2-unbuilt-seats` and `scp2-carries-21-23` each name the orchestrator's pending routing or ruling and pass. Carry: dismissed: a note on the block's scope

Both fixes are body or roster edits; nothing in the diff is asked to change by this block.

## Findings

- `tools/audit/seat/sweep_render.py --self-test` exits 1 at this head and at origin/main ee64358be7 alike: `Refused: unused: plan_coordinator_cap declared and never used by the sweep`, from main's c6c04f21b, which declares the placeholder in `sweep_template.md` and never uses it in the sweep text. The body's `NULL-sweep SURVIVED` and `S1 KILLED` lines were taken at 5a4161d57647, before c971bd5c3 merged that commit in; at the head the unmutated null is KILLED, so S1 proves nothing through the tracked self-test until main is repaired. With that one template row removed in the copy (my perturbation, disclosed), the null passes 35 checks and S1 is killed on the PR's own check. The commit reached main through fix/r10-tick-residue, whose group is live (carries-open); R10-ORCH-BEATD, the template's first owner, is done. Carry: R10-TICK-RESIDUE
- Sites that still name the roster seat as a live seat and are neither in the diff nor dispositioned in the body (my enumeration, `ev/residual_refs.txt`; the body names no enumeration rule): `dev/audit/README.md:40` (stage 5's contract column), `tools/audit/seat/roster_queue.py:2`, `tools/audit/seat/instruments/roster_queue.py.md:9`, `tools/audit/seat/outside_intake.py:25` and `:36`, `tools/audit/seat/roster_edit.py:1405`, `:1419` (a refusal message a seat reads) and `:3021`. `dev/programme/HANDOVER.md` is the body's own item. Triage, RCA and bugclass records are history and excluded. Carry: R10-STANDING-CONTRACTS-P2
- The entities check pins `## Wait`, `## Reads` and `## Recycle` by heading only: my mutants E8-rev and E9-rev empty the Wait and Recycle sections under their headings and the check prints `ok`. The check's comment claims the sentence-level pin for the autofix hold alone, which E2 and E3 confirm. Carry: dismissed: prose pinned by heading, as the check states
- `cloud_dispatch.py` pins whatever `design-verdict/<group>` holds, an `approve` included, with the text "answer every point ... do not restart"; and `_git show <tip>:verdict.md` on a verdict commit without that file is not exercised by the self-test. Neither was reproduced as a failure. Carry: dismissed: edge cases, not reproduced here

## Evidence

- RESULT lines: `ev/mutants.txt`, `ev/mutants_entities.txt`, driver `ev/rev_mutants.py` (the reviewer's instrument: a `git archive` copy of the head per mutant). P1, P2, C1, C2, C3, E1 to E6 KILLED on the checks the body names; NULL-pulse, NULL-cloud, NULL-entities SURVIVED. Mine: P3-rev, P4-rev, C5-rev, E7-rev KILLED; C4-rev SURVIVED and is equivalent (the verdict pair is read only in the designer branch of `_prompt`).
- The entities mutants ran on the check's own block, extracted from `tests/entities.py` and executed with a stub `R` (homeassistant is absent, so `tests/entities.py` does not import here). The full script was not run by me; CI's `tests / fast (3.14)` at this head is the citation.
- No finder's harness exists for this group (packet: "none named"); the group implements an approved design, so every instrument above is the fixer's or mine.
- Budgets, `node tools/policy/policy_lint.mjs --budgets` at the head: rc 0; `standing.md` 50/50 lines, 553/553 tokens; stubs 7/7, 92/92 and 6/6, 83/83 (`ev/budgets_head.txt`). Null control: with the two `standing.md` rows removed, full `policy_lint.mjs` exits 1 with `[budgets] ... no line cap recorded` and `[named-docs]` (`ev/policy_lint_null_nocap.txt`); `--budgets` alone exits 0 there, so the body's "refuses a new policy file without both caps" holds for the full lint only. Plant: restoring the stubs' old caps (27/368, 26/330) also exits 0, so the two lowered rows are a voluntary tightening.
- Aggregates, head against main (`ev/budgets_main.txt`): corpus ~68699 against ~68671, both over the 68618 cap inside the band; always-loaded 3600 against 3605; role fixer 6260 against 6265; role record 7423 against 7428. The body's payment (3) reads as fully paid; measured, the corpus rises 28 tokens inside the band and no aggregate cap is touched.
- Raise on its merits: no existing cap rises, the new row sits at the file's measure, and the mechanism (shared terms written once) survives its removal test: without the row the lint refuses. I found no payment the body missed that improves the code; `standing-dispatch.md` keeps 6 lines and 26 tokens of headroom under an untouched cap.
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL`, as the body states.
- `node tools/policy/policy_lint.mjs` rc 0; `rules_sync.mjs --check` ok; `brief_lint.mjs` rc 0.
- `git merge-tree --write-tree origin/main dd5faa50` exits 0 (tree 38456a0acff2).
- `python3 tests/env_drift.py --all` at the head: rc 0, `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main`, `NO STALE FIXTURE`; both claim files are untouched (`ev/env_drift.txt`).
- `VERSION`, `RELEASE_NOTES.md`, `tests/golden/` and `custom_components/` are untouched in the three-dot diff (0 paths).
- Citations in `standing.md` and the stubs resolve: `beatd.jobs.json` holds `tick-digest`, `owed-check`, `roster-drain`; `bus.sh` has `orphans`; `hooks/liveness.py` reads `HPO_ALIVE_STALE_MIN`; `dev/audit/README.md` holds the owner's quoted constraint; `ci_predict.py` prints `BOOTSTRAP` and names `fixer.md`.
- Red checks at the head: `budget-raise-gate / budget-raise-gate` and `gate` (the raise's owed approval); `governance / instrument-self-tests` and `tests / nightly-status`. None is in `merge_train.py owed-reds`' set (`tests / coverage-ratchet`, `tests / fast (3.14)`, `tests / mutation`, `tests / typing`, `validate / validate-hacs`), so none is owed an answer. I could not read `instrument-self-tests`' failing step from its log (the retrievable tail is the `selftest_scope` mutant step, which passes); the `sweep_render` crash above reproduces on main and is my candidate, not a verified cause.
- The body's gate records (`beatd status` for one cycle, the `roster-drain` seeded op and refusal) are the orchestrator's, owed before the stubs merge; I saw neither record.
- `merge_train.py classify dd5faa50 --pr 3464` printed `WAIT ... pending: gate red: none` on every poll from 12:52Z to 13:27Z (`ev/classify.txt`); the head was still dd5faa50c0a8 on origin at 13:28Z.
