R10-DISPATCH-AT-HANDOFF part 2, built locally by a seat that took the group over from two blocked cloud runs (BLOCKED.md of 07:31Z and the 11:57Z cloud return). It adds Carries 0, 4, 8, 11 and 12 of the roster group (0-based, as the orchestrator numbers them), on top of the two `review_packet.py` commits and the REPAIR-OWED commit the cloud seats already landed on this branch (head-note asks `policy_lint --pr-body --head`; the packet refuses a figure_lint red and a moved head; a required-context RED is a repair owed to the fixer, rc 5, never a retried REFUSE).

Rulings applied (orchestrator, mandate 6715477401, 2026-11-08), as the brief that dispatched this seat states them:
- First, The container's `tests/entities.py` red is the environment: it was run here at this head and at `origin/main`; both are red and the failing sets are the same (see Null control), so `PREPR_SKIP_CLOSURES=1` is used.
- Second: a pending (queued or in-progress) required context never holds a dispatch; WAIT dispatches and only RED holds. The REPAIR-OWED arm is on this branch; the roster item that would hold on a pending context is superseded by this ruling and stays unbuilt. The card-7 amendment of the owner's 2026-10-24 "dispatch never waits for CI" therefore applies to a red only.
- Third: Carries 0, 4, 8, 11, 12 are in this group's seam and are built (owner ruling 2026-11-08: no self-carry).
- Fourth: `bus.sh --self-test`'s failure that reproduces at `origin/main` is main's own red and is not fixed here (see Red checks).

## What each carry became

- Carry 0, dispatch at the handoff. `bus.sh dispatch-handoff <topic> <tip> <reviewer>` records `topic:<topic> <tip> ...` in the worker registry (no reader keys on it) when `handoff/<topic>` is at `<tip>` and `handoff-body/<topic>` exists; `bus.sh rekey <topic> <pr>`, called by `open_pr.sh` once #N exists, appends the record under the PR (rc 3 and silent when there is none, idempotent). `cloud_dispatch.py --role reviewer --topic <t>` (no `--pr`) renders a reviewer at the handoff: it reads `handoff-body/<t>`, renders no packet, waits on no CI, and returns `probe/revt-<t>-<nonce8>` with subject `verdict <t> <head>`. `cloud_relay.sh`'s probe arm holds such a verdict (`HELD-NOPR`, owed on the level as `handoff-verdict-held`, never posted) until the topic's PR exists; then it posts only when `review_carry.py` answers CARRY for handoff-tip..PR-head (the merge of main and the delivery row), else `HELD-STALE` names the `bus.sh dispatch <pr> <head>` that re-dispatches it. `bus.sh`'s `dispatch_binding` ignores a `topic:` record, so the nonce binds to no PR before the re-key. Policy text: `dev/governance/roles/standing-dispatch.md` and `fix-review.md` step 7.
- Carry 4, generated brief lines. `roster_lib.brief_lines` renders the live consumer groups (reverse after-edges and groups sharing files, closed groups excluded) as the only valid `Carry:` targets, and the group's optional `enumeration` command, into a fixer's brief (`cloud_dispatch.py group_brief`) and into `prepr.sh` (informational `carry targets` lines). A group with neither renders its brief byte-identically.
- Carry 8, model routing. `cloud_dispatch.py --group` with no `--model` reads the roster (`model.<role>`, then `<role>Model`) and prints the model and the field it read; a carry-only (`--carry-only`) or record-PR (`--record-pr`) review resolves sonnet; a role with no ruled model refuses rather than guessing.
- Carry 11, Dependabot body patch. `body_patch.sh` passes the PR's commit list to `policy_lint` as `--commits-file` for a `dependabot[bot]` PR, refusing when the list cannot be read.
- Carry 12, pending-ci. A reviewer whose review is complete while CI is pending returns `pending-ci: <contexts>` after the nonce line instead of waiting without bound (`cloud_dispatch.py` prompt); `cloud_relay.sh` posts it only when `merge_train.py classify` reads the head GREEN, holds it on WAIT (rc 75, one `HELD-PENDING-CI` line), refuses it over a RED, and refuses it when the PR head moved, naming both heads. The third clause of the carry (a fired session with no return after a bounded time gets one digest line) is the existing `noreturn_arm` (`SEAT ENDED NO RETURN`), cited, not rebuilt.

## Approval

`dev/governance/roles/standing-dispatch.md` (a dispatch-at-the-handoff clause and the pending-versus-red rule) and `dev/governance/roles/fix-review.md` step 7 (a parenthesis: a handoff review's head is the handoff tip) are policy edits; they merge on the owner's approving review or under the mandate that covers code-owned policy (mandate 6715477401, as the brief states). Both files sit at zero headroom, so no cap is raised: `standing-dispatch.md` stays inside its line and token caps by condensing its own prose (the cited path prefixes `tools/audit/seat/`, the `roster_edit.py set-stage` aside, and the `bus.sh orphans` sentence of the ref-reading section are dropped; no rule is), and `fix-review.md` drops the parenthetical `(a script routes on it)`. `node tools/policy/policy_lint.mjs` reads `TOTAL: 0 error(s)` with `policy_budgets.json` untouched; the first attempt, which added text without cutting, was refused at 47 lines against a cap of 39.

Main moved during the work and its own condensing of `standing-dispatch.md` conflicted with this branch's; the conflict was resolved by merging `origin/main` (16f3d9cc3a) and re-applying the clause inside the caps (`policy_lint` reads `TOTAL: 0 error(s)` at the merged head). The merge touched `prepr.sh` and `pr_args.sh` by automatic merge only.

## Head

089f1da017e98a697a24e70c308f79beee9b8607

## Mutation proof

The commits were re-authored as tvofi after the proofs below were run (the identity pin of 2026-11-07); the tree is identical (`git rev-parse HEAD^{tree}` equals that of the pre-re-author head e8c1197612b72c29e71df8833e88e5e4e569c8b5), so the measurements below describe that tree; the later merge of `origin/main` (see above) changed only `standing-dispatch.md` by hand and `prepr.sh`, `pr_args.sh` and files unrelated to this diff by automatic merge, and `policy_lint`, `structure.py` and the prepr run named in Figures were taken at the merged head.

Each mutant deletes or flips the production predicate, not a tail; the self-test names the check that reddens, and the restored tree passes. The results:

- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_relay-50 cloud_relay-51 cloud_relay-52 cloud_relay-53 cloud_relay-54 cloud_dispatch-21 cloud_dispatch-22 cloud_dispatch-23`: all eight KILLED (rc=1; `cloud_dispatch self-test: 142 checks, 1 failed` for -21, `2 failed` for -22, `3 failed` for -23). They are the relay's `relaytopic` (the `revt-` ref and subject), `topicheld` (held until the PR exists), `topiccarry` (post only on CARRY), `pendingci` (the pending-ci branch) and `pendinghead` (the moved-head refusal) lines, and `cloud_dispatch.py`'s light-review resolver, generated brief lines and handoff reviewer prompt.
- The harness grades `bus.sh` mutants NOT RUN because its governance-step environment has `bus.sh --self-test` red unmutated (4 failures there, the case-collision arm among them, also at `origin/main`). The four `bus.sh` sites were therefore mutated by hand in a scratch worktree, one at a time, and `bash tools/audit/seat/bus.sh --self-test` run on each; the failing arms below are over the one baseline case-collision failure. `mut:handofftip` (the tip equality `[ "$tip" = "$h" ]` replaced by `true`): reddens `a head that is not the handoff tip is refused`, `a topic with no handoff ref is refused` and `rekey appends the topic's record under the pull request`. `mut:handoffdup` (the duplicate-record `if` replaced by `if false`): reddens `a second reviewer at the same handoff head is refused and records nothing`. `mut:rekeyfilter` (the topic filter replaced by `/dev/null`): reddens `rekey appends the topic's record`, `a second rekey is idempotent` and `after the re-key the handoff-dispatched verdict proposes on #55`. `mut:bindtopic` (`dispatch_binding` no longer ignoring a `topic:` record): reddens `before the re-key, the topic's nonce binds to no pull request` and `after the re-key the handoff-dispatched verdict proposes on #55 at the handoff head`.
- `body_patch.sh --self-test` carries its own mutant arms for the Dependabot commit list: `MUTANT --commits-file dropped` and `MUTANT commit-list read check deleted` both read red against their paired controls (the tally says 0 failed because each mutant arm asserts the mutant's wrong behaviour). `pr_args.sh --self-test`'s `mut:rekey` arm: deleting the re-key line leaves the stub bus.sh uncalled.
- Failing test first: every arm above was written against the production symbol before or with it; the `dispatch_binding` defect itself was found by the first bus run (`nonce ... belongs to pull request #topic:ht1`), reddened the two re-key arms, and was fixed by the `$1 !~ /^topic:/` filter.

## Null control

- `tests/entities.py` at `origin/main` (`git worktree` of `origin/main`) and at this head, same interpreter and `PYTHONPATH=tests/hastub`: both exit 1 with 44 FAIL lines; `diff` of the FAIL names (first 60 columns, sorted) is empty apart from one timing figure (`hb:positive_control` reads 769.5 ms at main and 766.3 ms here), so the red is the stubbed Home Assistant environment and not this diff.
- `bus.sh --self-test` at `origin/main` fails the APFS case-collision arm (`push-verdict refuses evidence names that differ only by case`) and, in one run, `the content arm is load-bearing`; at this head the same case-collision arm is the only failure. The cloud container's "an ordinary append with no intervening fetch" failure is main's own red there; it did not reproduce on this Mac. Named, not fixed here.
- `pr_args.sh --self-test` at `origin/main` fails the three `a runner ...` arms (`without pr_exit_trap`, `push runs in the foreground`, `holds no push lock`); the same three fail at this head, and the three `pr_bounded` arms fail at both trees alike (six failures at each). The new open_pr re-key arms pass.
- Every new behaviour has its null arm in its self-test: a topic with no handoff dispatch re-keys nothing (rc 3, silent); a PR-keyed reviewer prompt is unchanged (`probe/rev-<pr>`, packet, CI wait); a verdict with no `pending-ci:` line never asks classify; a fixer group with no consumers renders byte-identically; a non-Dependabot PR is given no `--commits-file`; a first-round review resolves the roster's opus.

## Figures

- `bash tools/audit/seat/body_patch.sh --self-test`: 0 failed (instrument tally line).
- `python3 -I tools/audit/seat/cloud_dispatch.py --self-test`: 0 failed.
- `bash tools/audit/seat/cloud_relay.sh --self-test`: 0 failed.
- `bash tools/audit/seat/bus.sh --self-test`: one failed arm, the case-collision arm that also fails at `origin/main` (Null control).
- `bash tools/audit/seat/pr_args.sh --self-test`: the failing arms are those named in Null control; none is a re-key arm.
- `python3 -I tools/audit/seat/roster_lib.py --self-test`: 0 failed.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, no metric moved.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D`: `MODE: SCOPED`; it names `tests/doc_claims.py` (0 failed) and `tests/entities.py` (same failing set as main, Null control).
- Mutant harness: `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py <id>...` for the ids this PR adds to the ledger (Mutation proof).

## Unpinned sites

The added sites are pinned by the mutants above and by the in-tree ledger entries this PR adds to `dev/audit/harnesses/r10_seat_selftests_mutants.py`. The diff-mutant step of `prepr.sh` is report-only here; its outcome is recorded in Figures when it ran.

## Carry dispositions

- Carry 0 (0-based; re-key and held verdict): built, with policy text.
- Carry 4: built.
- The hold-on-a-pending-context item (roster index 6): superseded by the second ruling above; nothing was written for it.
- Carry 8: built.
- Carry 11: built.
- Carry 12: built; its third clause is the existing `noreturn_arm`.
- Carry 17 (REPAIR-OWED on RED; WAIT dispatches) and Carry 16 (head-note asks `policy_lint --pr-body --head`): already on this branch from the cloud seats.
- Carries 1, 2, 3, 5, 7, 9, 10, 13, 14, 15: delivered at main by earlier pull requests, no re-fix (the survey the cloud seat's BLOCKED.md cites, afc1586a4).

## Red checks

Each of these also fails at `origin/main`, so none is this diff's; comparison command for all: run the named self-test in a `git worktree add --detach <dir> origin/main` and in this checkout, with `PYTHONPATH=tests/hastub`, and compare the `FAIL` names.

- `bash tools/audit/seat/bus.sh --self-test`, arm `push-verdict refuses evidence names that differ only by case, naming both`: fails at `origin/main` on this APFS host (a case-insensitive filesystem cannot hold the colliding names). Carry: dismissed: baseline red at origin/main.
- `bash tools/audit/seat/pr_args.sh --self-test`, arms `a runner without pr_exit_trap is refused`, `a runner whose push runs in the foreground is refused`, `a runner under the branch lock whose push holds no push lock is refused`: fail at `origin/main` identically. Carry: dismissed: baseline red at origin/main.
- `python3 tests/entities.py` (44 FAIL lines, the same names at `origin/main` and here, the stubbed Home Assistant). Carry: dismissed: baseline red at origin/main.
- `pr_args.sh --self-test`, arms `pr_bounded: ...` (three): they fail identically at `origin/main` (182 checks, 6 failed there; 186 checks, 6 failed here, the four extra checks being the new re-key arms), in a full `pr_args.sh --self-test` run alone at each tree. Carry: dismissed: baseline red at origin/main.

## Forward-carry

none

## Friction

none
