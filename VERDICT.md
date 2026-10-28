Fix review: blocked a2cd2f659883ce2e340f20b7c4aa5003ebc20fbf figures-unverified: body quotes 186 groups, 35 changed and done 112 then 114; the head measures 189, 34 and 115 then 117

bus-nonce: 56b8c3d83ee58f04799a06e009cef573

Round 1 of the fix review. Measured head: `a2cd2f659883ce2e340f20b7c4aa5003ebc20fbf`. I re-read it via ls-remote just before writing: refs/pull/2799/head and fix/audit-r10-roster-pr both still point at it. Main is `b89fea13e99f23cc75f01bb1604030cabea4ca66`, which is also the merge base.

## Block

- The body's **Null control** says "186 groups on each side, none removed, none new, 35 changed". Loading both roster files as JSON at main `b89fea13e` and at the head gives **189** groups on each side, none removed, none new, and **34** changed (`ev/roster_figures.txt`). Its stated rule, "comparing groups by id", cannot be run as written. No group carries an `id` key; the key is `group`. I keyed on `group` instead, which is a definition I chose myself (step 8).
- The body's **Figures** gives `done 112 then 114`. Main measures 115 and the head 117. The deltas (+2 done, -2 in-progress, -3 not-started, +3 absorbed) and the other stage counts (in-progress 12 then 10, not-started 50 then 47, queued 6, absorbed 1 then 4, carries-open 5) do match. The done totals are 3 too low on both sides, as is the group total. No nearby ref reproduces 186 or 112: origin/main^1, the merge base and the previous head e6f48a480 all have 189 groups, and their done counts are 115/115/116.
- The **Other changed groups** list is incomplete. It names an `issues` change only on R10-FLY-LEDGER-SAMPLE, R10-RCA-FRICTION-RESIDUE (plus the "issues field" on R10-ORCH-ROSTER-SCHEMA, and on FLY-POOL-INSTRUMENT and FLY-RECORD-BEAT, which it lists under `resume`). `issues` also changed on R10-FLOW-DESIGN-STAGES (+2800), R10-FLOW-POSTMERGE (+2801), R10-ORCH-LEDGER (+2265), R10-IMMERSION-LATCH (+2805) and R10-MERGE-SUBJECT-CASEARM (+2803). The ops list does show each of them as wire-issue.
- The title still says "roster ops ... through 00ceb9aa4". The body and head carry ops through 0574da74a.
- To clear it: correct the body (and the title) to the measured figures and state the key the comparison uses. A body-only edit does not move the head, so this verdict's other measurements carry.

## Findings

none

## Evidence

- RESULT parents: `git log -1 --format=%P` prints e6f48a48022ec8c06e5a015c8ec0dffe8b236d61 0574da74ae2f7ddf7c9250548f08c2f8b06d8775, as the body says.
- RESULT diff: two files against main, `dev/programme/delivery/2799.md` (+1) and `dev/programme/rosters/wave-r10-groups.json` (162 lines), as the body says.
- RESULT roster commits: 58 in `origin/main..head -- dev/programme/rosters/`. Two are not roster_edit: `5f94b943b` and `0574da74a`, as the body says.
- RESULT null-control hashes: main ae5988d3415d399099e4dae250a8380da56e3c78, head 91f41425e74d3ebe030ac5230bcd8408dee6f35b, as the body says.
- RESULT carry counts: all 21 moved carry counts the body quotes match (`ev/roster_figures.txt`), including R10-ORCH-ROSTER-SCHEMA 10 then 16.
- RESULT stage transitions: R10-CONFIG-NOTICES and R10-FLY-ENVMATRIX-NOREMOTE in-progress to done. R10-ROUTING-INVARIANTS, R10-FLY-POOL-INSTRUMENT and R10-FLY-RECORD-BEAT not-started to absorbed.
- RESULT merge: `git merge-tree --write-tree origin/main head` exits 0 (tree 6b07bef5b). No claim file is touched.
- RESULT VERSION, manifest version and RELEASE_NOTES.md are untouched.
- RESULT brief_lint: `node tools/policy/brief_lint.mjs` at the head prints `TOTAL: 0 error(s) across 48 file(s)`.
- Role drift: `git diff merge-base...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Mutation proof, finder's harness, null-control perturbation and the class rule do not apply. This is roster state only, with no production or test code, so there is no mutant to draw.
- CI at the head: 42 check-runs read, none failed. Several were still queued or in progress, and no pr-contract run was listed yet (`ev/checks.txt`). So the step-11 red-check question has nothing to answer at read time. The body's "Red checks" section defers the read to the orchestrator.
- Forward-carry: the body says none. The diff is itself the carry record (appended carries), so no later-stage brief is owed from this PR.
