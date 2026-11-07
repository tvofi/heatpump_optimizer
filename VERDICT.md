Fix review: blocked c7c5cef52a49bed59ee4c8a42e495ef2dae30db5 ci-red: required gate is red at the head by mutual edit-run deferral (gate jobs 128296193620 and 128296198588, 04:08Z) and the body's Red checks predates both and reports the gate green; the code is otherwise approvable

bus-nonce: 68eaffc22bfcfcc9217089055287b881

Round 2. I reviewed from a detached worktree at c7c5cef52a49bed59ee4c8a42e495ef2dae30db5. The merge base is f2a015142714383722bf49d7ab20d8398ec9674c. The code head is aa5c0505b73c77d1ab5a650af2da58759b8b307a. The finder's harness: none is committed, because this is an owner-reported hotfix. The harness is therefore the owner's ruling plus the live plan. The enumeration, mutants and HTML parser below are my own, and they are copied to `ev/*.py`.

Owner ruling (tvofi 2026-11-06), verbatim: "The HTML plan seems to incorrectly place some instrument or CI fixes in the core model lane, fix that".

## Block

- Claim: `## Red checks` names every concluded red of the live head (brief item 6; fix-review.md step 11).
- Evidence: I read `get_check_runs` at c7c5cef52a49bed59ee4c8a42e495ef2dae30db5 at about 04:15Z. It returned total_count 81, all on one page. Three runs had concluded red (`ev/ci-state.txt`):
  - `gate` job 128296193620, from edit run 42332777827 attempt 5, failed at 04:08:17Z. Its log reads "FAIL run(s) [42333388705] at this head are still being judged; their gate decides".
  - `gate` job 128296198588, from edit run 42333388705 attempt 5, failed at 04:08:22Z. Its log reads "FAIL run(s) [42332777827] at this head are still being judged; their gate decides".
  - `governance / instrument-self-tests` job 128295162018 was `cancelled`. The body answers it: a 30-minute timeout owned by R10-HOTFIX-SELFTEST-TIMEOUT. I accept that answer.
- The two gate reds defer to each other. That is the open R10-HOTFIX-GATE-BUSY-DEFER, and no code run is in progress to break the deadlock.
- The code run 42332778588 has concluded. Its own `gate` job 128295163417 is `success` (04:06:09Z), and edit run 42336664899's `gate` job 128295636172 is `success`. Those runs decide. But the required `gate` context is now red.
- `merge_train.py classify` → `RED c7c5cef52a49bed59ee4c8a42e495ef2dae30db5 pending: none red: gate`, rc=1. I polled it every 2 min from 04:10Z (`ev/classify-history.txt`).
- The packet refuses `required-red` (`ev/packet-render.txt`).
- The body was last updated at 04:02:36Z, before both reds. It states "At `c7c5cef5` the gate jobs are `success`" and cites jobs 128291152776, 128291256420 and 128291967008. None of those is among the head's 81 check runs now.
- Metric: concluded gate reds at the head that the body names: 0 of 2.
- Perturbation: none is needed. These are CI facts read from the API, and the classifier flips to GREEN once one gate is re-run alone.
- Not a root-cause block: the last `pr-contract` run started at 04:04:26Z, before the last red concluded at 04:08:22Z. Under step 11, no `root-cause-*` class is posted yet.
- Remedy, with no code change:
  - The orchestrator re-runs one of the two edit-run `gate` jobs on its own, so it no longer sees the other in progress.
  - The body's `## Red checks` names both reds as the R10-HOTFIX-GATE-BUSY-DEFER mutual deferral, decided by code run 42332778588's gate 128295163417, and drops the job ids that are gone.
  - Everything else below holds at this head. A round 3 is a re-verdict of the same code; it is not a re-cut.

## Findings

- Follow-up: my extra mutant m13 survives the self-test. It narrows `work_class`'s `or k in INSTRUMENT_KINDS` to `("instrument", "policy")`. That clause is now reached only for a group that a name rule places in Learners, Product UX or Replay with a tool-landing kind, for example R10-DEEPLINK-CENSUS with `kind: rca`. Over all 351 live roster groups, the mutated `work_class` differs from the head's on 0 groups (`ev/m13-live.txt`). The line is pre-existing and was changed here only to reuse the tuple, so it is not one of `roster_lane`'s core lines (brief item 3). Carry: R10-HOTFIX-PLAN-LANES | dismissed: no live effect (0 of 351 groups) and outside the roster_lane predicates this fix owns; a work_class pin for a name-placed rca group would close it if the seam is ever touched

## Evidence

- RESULT head self-test: `python3 -I tools/plan/replan.py --self-test` → `self-test: 0 failed`, rc=0 (`ev/selftest-head.txt`).
- RESULT mutants. These are my own, built with `ev/mut.py`: `git archive` of the head, one exact substitution that must match once, then `--self-test` (`ev/mutants-head.txt`).
  - m0 (null control, unmutated) passes with rc=0.
  - Every mutant below exits rc=1. Each is listed with the self-test checks that fail:
    - m1, deleting the `_owned_lane` call: 7 lane checks fail, including "a CI-only group is Instruments".
    - m2, deleting the kind/class fallback: "an RCA group with no files is Instruments", "a tooling group with no files is Instruments" and "a roster class instrument with no files is Instruments".
    - m3, dropping the `class == "instrument"` arm: "a roster class instrument with no files is Instruments".
    - m4, `not all(` → `not any(`: "a mixed group stays Core model" plus the three hot-file null controls.
    - m5, dropping the `not files` guard: "a group with no files stays Core model" and "a production group with no files stays Core model".
    - m6, dropping the user-docs tooling exclusion: "docs plus a tool is Instruments, not Docs".
    - m7, dropping the doc-kind arm: "a docs-only doc group is Docs".
    - **m8, dropping hot_files**: "an integration hot file keeps a tool group Core model", "a bare hot filename keeps a tool group Core model" and "a bare tool basename in hot_files stays Core model".
    - m9, removing the `docs/` prefix: 3 checks.
    - m10, emptying `_NON_PRODUCT_FILES`: 3 checks.
    - m11, removing `rca` from the kinds: "an RCA group with no files is Instruments".
    - m12, making `user_docs` always true: 4 checks.
  - Result: 12 of 12 killed, so the round-1 block (m8) is cured.
  - Failing-test-first: the same m8 substitution at the round-1 head 8ff3432a exits rc=0 with `self-test: 0 failed` (`ev/m8-at-r1head.txt`).
  - The body's mutation table lists all 12, each with its substitution, the red checks under the mutant and the green null control. Its check names match mine.
- RESULT live lanes (JSON), from my own enumeration (`ev/laneenum.py` → `ev/lane-enum.txt`).
  - Setup: plans built at base f2a015142 and at the head, with roster `origin/handoff/audit-r10-roster` at 22a80168786b0a0f04d1834daf71fb4807c674e5 and `--start 2026-11-06T22:00:00Z`.
  - Groups: 351 at both ends.
  - Base: Core model 126, Instruments 192, Docs 2, Learners 8, Product UX 14, Replay 9.
  - Head: Core model 62, Instruments 251, Docs 7, Learners 8, Product UX 14, Replay 9.
  - Open groups at the base: Core model 24, Instruments 39, Docs 1. At the head: Core model 10, Instruments 51, Docs 3.
  - Moved: 64, all from Core model (59 to Instruments, 5 to Docs), of which 14 are open. All of this equals the body.
  - The body's 64-row table is identical, group for group, to my moved list (`diff` empty; `ev/body-moved.txt` against `ev/my-moved.txt`).
- RESULT moved groups are correct under my own path classes. Of the 64, 0 are suspect: each owns only instrument or record paths, or owns no file and has a tool-landing kind or `class: instrument`. No moved group owns a `custom_components/` file or a bare filename.
- RESULT null control: every Core-model group at the head owns a `custom_components/` file, or owns no file without a tool kind or class. The 7 file-less ones match the body's list exactly: R10-CARD-VOICE, R10-CATALOG-PR, R10-COMBI-TANK, R10-NIGHTLY-SLOW-ROLLING, R10-RCA-HEADMOVED, R10-ROSTER-PUSH-RACE and R10-STORE-RACES. No group moved out of Learners, Product UX or Replay. The only Instruments or Docs group owning an integration file is R10-I5-DOCS, which a name rule places in Docs at both ends and which did not move.
- RESULT HTML: `plan_page.py` is unchanged in the three-dot diff. I rendered both plans offline (`ev/plan-base.html`, `ev/plan-rev.html`) and parsed each bar's y against the lane bands (`ev/htmllanes.py` → `ev/html-lanes.txt`).
  - Drawn lane ≠ JSON lane: 0 at both ends.
  - Drawn bars: 67 at both ends.
  - Core model 24 → 10, Instruments 39 → 51, Docs 1 → 3.
  - 14 open groups move in the drawing, all out of Core model.
- RESULT figures: at the body's roster cab343ebe891836ff776defccab9cb8ae9a9cbc7 (blob e7207ea34c7f), the summary is `CI 7537.5 min | batches 61 | stamps 6` at the base and `CI 6300.0 min | batches 53 | stamps 3` at the head (`ev/summary-cab343.txt`). That is exactly the body's figures. At today's roster 22a80168 it is 6862.5/55/6 → 6637.5/56/3, so the figures move with the roster, as the body discloses. `--check` on the head plan prints `PLAN OK`.
- RESULT scope (`ev/scope.txt`):
  - The three-dot diff touches only `tools/plan/replan.py` and `dev/programme/delivery/3265.md`, so the delivery row is in it.
  - No `custom_components/`, `VERSION`, manifest, `RELEASE_NOTES.md`, `*_budgets.json` or `plan_page.py` change.
  - `tests/closure.py select --diff f2a015142…` → `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`
  - `tests/structure.py` → `STRUCTURE RATCHET PASSED`.
  - `tests/entities.py` hit my 200 s timeout here (rc=124), so I cite CI instead: `tests / closures` and `tests / fast` are `success` in code run 42332778588.
- RESULT merge: `git merge-tree --write-tree origin/main c7c5cef52a49bed59ee4c8a42e495ef2dae30db5` → rc=0, tree 3c0b2c2522f29c40ad3a08bfdf337036e7a99305, with origin/main at 355d9965a7a14ec45ef8cd25fb9c75c5ced044f1. `dev/governance/roles/` is unchanged between the merge base and main.
- RESULT `## Head`: it names c7c5cef52a49bed59ee4c8a42e495ef2dae30db5 as the PR head and aa5c0505 as the code head, and both are current. The paragraph naming c7c5cef52a49bed59ee4c8a42e495ef2dae30db5 is duplicated word for word, which is cosmetic.
- CI: `merge_train.py classify` → RED, rc=1, red: gate, from 04:10Z through 04:59:05Z (head re-read at 05:00Z, still c7c5cef5) (`ev/classify.txt`, `ev/classify-history.txt`). See `## Block`.
