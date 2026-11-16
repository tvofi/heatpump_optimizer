# BLOCKED: r11-outside-contributor-cycle-p3

Question: both carries of this dispatch are already discharged or owner-held at base 367c3b9cac (origin/main); should the orchestrator mark R11-OUTSIDE-CONTRIBUTOR-CYCLE-P3 done and route carry 0 to the owner, or hand a seat a test fork and a minted hpo-author token for the three live checks?

Base measured: 367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c (origin/main tip at dispatch). No code was written: there is no diff a pull request could carry.

## Carry 1 (guides and decision 0017): on main

- Guides, by #3619 (merged 755b7f5): `grep -n -i "head-repo\|\[OUTSIDE\]\|refs/remotes/pull" tools/audit/seat/instruments/remerge_main.sh.md tools/audit/seat/instruments/merge_train.py.md` returns remerge_main.sh.md's `--head-repo <owner/repo>` entry, its `[OUTSIDE]` park and the sentence "No tool of ours pushes a fork's head to a branch of origin: the train fetches it to `refs/remotes/pull/<pr>/head` only", and merge_train.py.md's `[OUTSIDE]` class with the recarry worktree detached at `refs/remotes/pull/<pr>/head`.
- Decision 0017, by #3653 (merged 824a016, the owner's merge): the same grep over `dev/governance/decisions/0017-outside-contributors-are-adopted-on-our-machine.md` returns `refs/remotes/pull/<pr>/head`, `remerge_main.sh --head-repo` and the `[OUTSIDE]` class in `## Decision`.
- The group brief's code items (the contract on every merge path including merge_pr.sh app mode, `Train.fork_head`'s main-blob comparison, `Train.land` on a batch base, the selftest_closures re-record): #3619's commits 7ea5279071, c5ccecbda0, 2edfd5bd47, 436ee9878e, 0e21330c64, all on main.

## Carry 0 (the three live checks on a test fork): not runnable by a seat

- Needs the hpo-author installation token: `tools/pr/app_push.sh`'s header states minting is orchestrator-central and seats never hold the App's key.
- Needs a fork pull request on a test fork: this session's GitHub scope is tvofi/heatpump_optimizer only, and creating a fork is an outward action no brief item authorizes.
- Decision 0017's `## Before the first allowlist entry` already records all three checks as owed on the owner's credential and a fork before any entry is added; control: if (a) is refused, the train parks `[OUTSIDE] ... no personal token is tried without the owner`.
- The previous dispatch's body (handoff-body/r11-outside-contributor-cycle-p3 at 1cc6a19) disposed this carry `dismissed: owner-held checks`; the roster re-dispatched it, so that disposition did not close it there.
