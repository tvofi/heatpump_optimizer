Fix review: blocked 749a3161dbbc18db74050036f96bc40acea1e0d1 root-cause-unrecorded: governance / instrument-self-tests and governance / policy-docs are red at this head and unnamed in ## Red checks; pr-contract refuses the body

bus-nonce: 8c62c7fbc8c84fbdf6a762a514393f51

## Block

Round 1. Measured head `749a3161dbbc18db74050036f96bc40acea1e0d1`, re-read at 2026-11-05T08:19Z and still the head of `fix/r10-seat-identity-guards`.

Every workflow on this head has concluded. `pr-contract / pr-contract` (job 127127243614) started at 08:12:29Z, after the last red concluded, and refuses the body:
`check governance / instrument-self-tests is red and ## Red checks does not name it` and the same for `governance / policy-docs` (`PR-BODY: 2 error(s)`). The body's `## Red checks` says "none" because it was written before CI ran.

Cause, reproduced by this review. Both reds come from this branch predating main's #3208 (R10-MACHINERY-RATCHETS, merge 3ec5178c6 at 06:56:47Z). The code head c34c211dd was committed at 06:42Z, before that merge. CI runs the base's (dad3178d6) restored graders against a head tree that lacks `dev/governance/config/machinery_budgets.json`:
- `governance / policy-docs`: `machinery_ratchet: dev/governance/config/machinery_budgets.json is absent at 749a3161…`, exit 2.
- `governance / instrument-self-tests`: main's `tools/policy/budget_raise_gate.py --self-test` on this head's tree gives `FAIL the tree has budget files to read`, 267 checks, 1 failed (reproduced locally). On the tree `git merge-tree --write-tree origin/main 749a3161…` the same self-test gives 272 checks, 0 failed, and machinery_ratchet's self-test gives 54 checks, 0 failed.

No earlier detector existed: main moved after the handoff, and `ci_predict.py` predicts against the merge base, which it reports as 6777ec33337b, so it predicted nothing. These checks are themselves the cheapest detector, which makes the block `root-cause-unrecorded`, not `-detectable`.

Repair: merge origin/main (it merges cleanly), then name and answer both reds in `## Red checks`, or re-run until they are green and say so. After a main merge, step 12 re-reviews only the resolution delta; every other measurement below carries.

Everything else this review checked passes; see Evidence.

## Findings

- Follow-up: the `email_leaks` docstring added at tools/audit/seat/ref_privacy.py:245-247 says "(a seat commits as hpo-fixer)", but the identity this PR exports is `seat` / `seat@users.noreply.github.com` (the body's DEVIATION). The docstring should name the identity actually used, or the owner's ruling. Carry: R10-SEAT-IDENTITY-GUARDS
- Residual: the DEVIATION (`seat` instead of the brief's `hpo-fixer`) waits on the owner's ruling, which the body asks for. Carry: dismissed: surfaced in the PR body for the owner, who rules at the merge review; not this reviewer's to settle
- Out of scope: five guarded push sites guard only the message of a `commit-tree` commit, never its author or committer: bus.sh:333-334, heartbeat.sh:31-33, wt_sync.sh:41-42, state_docs.py:584, roster_edit.py:940. Carry: dismissed: they publish orchestrator-side refs (bus, heartbeat, wip-sync, state, roster) under the orchestrator's identity. A commit only reaches main through app_push.sh's `--commits` guard, whose identity check this diff extends, and on a cloud seat the new profile exports set the identity
- Residual: the P317 call-site row in `prepr.sh --self-test` matches source text; it is not a driven `--body-check` run. Carry: dismissed: the carry's own named mutant (drop the call) is killed by that row (489 passed, 1 failed), and this review drove `--body-check` end to end. The head refuses a planted host path and the mutant passes it (ev/bodycheck-and-carry5.txt)

## Evidence

- Head reviewed: 749a3161dbbc18db74050036f96bc40acea1e0d1 (ev/HEAD.txt). Merge base 6777ec33337b256d29ea145d98da413dbf076a2a; origin/main dad3178d6c81cfe2bb410e7045de28f686a6f845. The diff to roles/ since the base touches only proposal-triage.md, so this contract is current.
- Finder's harness: none is committed (the packet says "none named"). This review built its own: ev/plant.sh, run at both ends with output in ev/plant-harness.txt. It plants commits in a throwaway repository and runs `ref_privacy.py guard --commits HEAD --over refs/remotes/origin/main`.
  - RESULT head: author-only Claude rc=3, committer-only rc=3, both rc=3 (all three `anthropic-identity`), trailer-only `Co-Authored-By: Claude <noreply@anthropic.com>` rc=3 (`co-author-trailer`); each passes rc=0 once re-authored.
  - RESULT head: the hpo-fixer@users.noreply.github.com null control rc=0. A Claude-authored commit already on main, under a clean top, rc=0, so main's history is not judged.
  - RESULT base: author/committer/both rc=0, so the class is new; the trailer arm was already rc=3 at the base.
- Mutation proofs, my own targeted mutants (tree restored after each):
  - Drop the `anthropic-identity` branch of `email_leaks`: ref_privacy self-test 109 checks, 4 failed. The plant harness then gives author/committer/both rc=0.
  - body_push guard call replaced with `true ||`: 1 failed (the runner-default arm).
  - `--over` dropped from body_push's guard: 1 failed.
  - The cloud-setup profile's `GIT_AUTHOR` export dropped: 1 failed. The four `GIT_*` entries dropped from `variables`: 2 failed.
  - `RUNNER_TEMP` export dropped: 1 failed.
  - SEAT_EMAIL changed in cloud-setup.sh: cloud_dispatch self-test 1 failed (the agreement check).
  - The send-pack site pattern dropped: 1 failed. The graphql `query=@` pattern dropped: 1 failed.
  - `bline=$(true)` in prepr `--body-check`: prepr self-test 489 passed, 1 failed (ev/prepr-selftest-mutant.txt), which matches the body.
- Figures re-derived at this head:
  - ref_privacy self-test 109 checks, 0 failed.
  - cloud_dispatch 126 checks, 0 failed.
  - cloud_setup 19 checks, 0 failed.
  - prepr self-test 490 passed, 0 failed.
  - structure ratchet passed.
  - `closure.py select --files <three-dot names>`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out` at both c34c211dd and 749a3161. Bare `closure.py select` in a detached worktree prints FULL ("no changed files could be determined"), so the body's figure needs the file list.
  - The 2622 entities checks were not re-derived; that is CI's heavy run.
- Under the head's exported variables (`GIT_*=seat`, `RUNNER_TEMP=/opt/hpo/runner-temp`; ev/exported-vars.txt), these self-tests all pass: ref_privacy, cloud_dispatch, bus (128), handoff_push (6), heartbeat (7), wt_sync (ev/selftests-under-exports.txt). No self-test that asserts an author from `-c` config was found.
- Carry 5: with HOME=/root, `body-lines` passes `dev/governance/roles/root-cause.md` (rc 0, both at the head and at the base) and refuses `/root/x`. This agrees with the body's re-measurement.
- `ref_privacy.py --check` at the head: 30 files with a push site, 12 guarded, 0 refused. The diff only adds refusals. The only edit to an existing assertion turns the `noreply@anthropic.com` null control into the new refusal arm, as the carry asked.
- Merges:
  - `git merge-tree --write-tree origin/main 749a3161…` exits 0 (tree 021ea6feac…).
  - Against PR #3221's head 20d5aab00a01cb3bf3738e1e78a13273089bc523 it exits 0 (ev/merge-tree-3221.txt). #3221 edits body_push.sh's prepr receipt trailer, a different region with no semantic coupling.
  - The prepr.sh edit is the `body_privacy_line` function, its call in `--body-check`, and its self-test rows only.
- Claim files, VERSION, the manifest, RELEASE_NOTES, `*_budgets.json`, tests/structure.py, closures.json and closure.py are byte-identical to origin/main and untouched three-dot. There is no budget raise.
- CI on this head: merge_train classify rc=1, `RED … red: gate` (ev/classify.txt). 42 check runs over all pages (ev/check-runs.txt); the failures are gate, pr-contract, instrument-self-tests, policy-docs, delivery-status and nightly-status.
  - delivery-status is red on other PRs' OVERDUE rows (#3206, #3189 …); this diff only adds its own open row.
  - nightly-status is programme-wide. pr-contract does not charge it to this PR.
- Forward-carry: the body says none, and its carries are all settled in-diff. Its `carry_audit` reads 0 items.
