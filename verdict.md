Fix review: blocked 722037e783eff1d55d04ca575ae39bb8366c98c2 claim-refuted: the body says the push after the merge clears ci-ratchet without a re-record, but the head's replay.py section 6 and the reviewer's harness both read it GREW at 25.644 and 25.993 against 23.283

bus-nonce: 120430195f9cd6cb5461e6e78921d827

## Block

Round 1. Head measured: 722037e783eff1d55d04ca575ae39bb8366c98c2 (base d7582ed404a87603bd02fefda610d7ebbe4181e1, origin/main unmoved).

The body states three things the head refutes:

1. `## Red checks` says: "Predicted: the merge commit's own `tests / ci-ratchet` reads GREW once more ... The next push clears it without a re-record." The head's own `replay.py` section 6 reads the first push after the merge as GREW: 25.644 and 25.993, with each of the two green probed runs, 41862133797 and 41862145105, standing in for the merge run. The PR's own carry entry in `dev/programme/carries/carry-201.json` says the same ("predicted to keep reading GREW near 25.6-26.0 ... not to clear") and puts a re-record or a payment to the owner under CLAUDE.md rule 2. So the body and the carry contradict each other. The body is what the merge seat and the owner read.
2. The bullet "The unit is kept ... So 21.983 + 1.3 keeps its meaning and nothing is re-recorded" is false in effect. The budget was recorded with each heavy lane at its fastest draw, which is the minimum of a noisy class. Probed pricing takes the median of that class. On real fleet data, `tests / closures` prices at about 1394–1407 reference seconds (23.2–23.4 min), against the 1117 s fastest draw it priced at before. Section 3's "probed 20.35" leaves closures at its fastest draw, because that lane has no host history, and so hides this.
3. The `## Figures` section-4 numbers do not re-derive at this head. The body has a slow fleet at -0.108 (bound 0.802) and growth of +2.23 at k=9 and +2.56 at k=12. The head prints +0.026 (bound 0.624), +2.30 and +2.46. Section 6 is not listed under Figures at all.

What clears this: a body that matches the head. It should state that main stays red after the merge until the owner decides on a re-record of critical_path_minutes in the probed unit, or a payment on the closures path, and it should carry the head's section 4 and 6 figures. As a hotfix for the red at 8e90d8144, the PR does not turn main green by itself. Merging it is still sound if the owner takes that decision with open eyes, because the instrument change itself passed every check below.

## Findings

- Follow-up: `window_work_minutes` builds its graph from the union of timing-inferred need edges across the window (`_walk`'s pred is "the job that ended last before this one was created"). One run's coincidence therefore becomes an edge for all 16 runs. In main's 60 push runs I found 20 such non-`needs:` edges, for example `tests / graders-head-copy <- codeql / Analyze (javascript-typescript)` in run 41513537435. In the branch's probed runs, the grade's path carries `refresh`, `validate-hacs` and `budget-raise-gate` ahead of `tests / closures`. The pull_request run 41854976917 has `ci-ratchet <- codeql / Analyze (python)`, which puts codeql's 25–40 min on the path (reviewer harness: 28.25 with that run plus main's 15). On push, the same race against codeql would price codeql into the grade. A fix: keep only edges the workflow's declared `needs:` allow. Already carried by the PR itself, in its carry-201 entry. Carry: #201
- Follow-up: the post-merge red is owed an owner decision (re-record in the probed unit, or a payment on the closures / ci-ratchet path) before or at the merge. The PR's carry-201 entry already states this. Carry: #201

## Evidence

- RESULT reviewer harness (own instrument, `ev/W_harness.py`, which runs the tree's `window_work_minutes` on main's runs.json mixed with fleet.json, jobs cut to push-run names): main newest window 29.067; probed 41862133797 + main's 15: 25.627; probed 41862145105 + main's 15: 25.993; 16 copies of 41862133797: 24.327; 16 copies of 41862145105: 24.193. Every value is over the limit 23.283. Paths (`ev/decomp.py`, `ev/decomp_out.txt`): `tests / closures` probed at 23.23–23.44 min sets the grade.
- RESULT the head's replay.py: `RESULT holds=1`. Section 6 reads 25.644 and 25.993 GREW (`ev/replay_head.txt`).
- RESULT null control, unprobed: across all 45 sliding windows of the 60 push runs, the head's grader minus main's grader = 0.0 in every window. So the change moves nothing until a probe step exists, as the body claims.
- RESULT real-fleet separation (fleet.json, three probed runs, own computation). `tests / fast (3.14)` walls ran 1228..2044 s (+66 %), and its reference work 1112..1174 s (5.5 %). `tests / closures` walls ran 1386..2360 s, reference 1339..1407 s. `tests / coverage` reference 1060..1116 s. `tests / arch-instrument` reference 1011..1181 s: one mid-class probe of 32 s, 15 % spread. So the probe does separate runner speed from work on the real fleet. The self-test and section 4 plant +300 s of growth and it reads.
- RESULT mutation proof, re-run (`ev/mut.txt`). `seen = reference or walls` -> `walls`: 3 failed. Median -> min: 1 failed. Need edge -> `pass`: 15 failed. `reference_work` -> None: 5 failed. These match the body. The entities.py pin mutants were not re-run (they need a heavy script).
- RESULT `python3 tests/ci_ratchet.py --self-test`: 65 checks, 0 failed. `probe_bridge.py --self-test`: 8 checks, 0 failed (the body says 4; this is the head's count). `probe_bridge.py` on fleet.json gives 3.14 22.4 and 3.13 22.12, which agree with the tree.
- RESULT gaming. `tests / ci-ratchet` runs only on push to main (`tests.yml:2287-2289`). `tests/host_probe.py`, `tests/ci_ratchet.py`, `probe_bridge.py`, fleet.json and `.github/workflows/` are all owned by @tvofi in CODEOWNERS. A pull request's own copy cannot reach the grade without the owner's review.
- RESULT budgets: no `*_budgets.json` change in the three-dot diff. `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched.
- RESULT `git merge-tree --write-tree origin/main 722037e78`: rc 0, no conflict.
- RESULT CI: `merge_train.py classify 722037e78... --pr 3201` rc 0: `GREEN 722037e783eff1d55d04ca575ae39bb8366c98c2 pending: none red: none` (18:30 UTC). No red gate check at this head, so step 11 owes nothing new.
