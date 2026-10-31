# Review packet #3029
head: a3faaacbef0bbac9cda2d83b10bca2f33ac3122d
base: 861f949ae85884801bee7cd94e9307bf546c9046

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=124420160633 skipped
cancel-superseded id=124420160702 queued
prelude id=124420160619 queued
refresh id=124420160597 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git log --no-merges --format='%an <%ae>' origin/main --since=7.days | sort | uniq -c
             `git log` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git log --no-merges --format='%an' origin/main..origin/<branch>
             `git log` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git log -1 --format='%h %cI %s' -S'pin the seat identity' origin/main -- tools/audit/seat/cloud_dispatch.py
             `git log` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git log -1 --format='%an <%ae>' 1670b98d7
             `git log` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 1 resolved, 4 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3029.md b/dev/programme/delivery/3029.md
new file mode 100644
index 000000000..9cc54aabf
--- /dev/null
+++ b/dev/programme/delivery/3029.md
@@ -0,0 +1 @@
+- [#3029](https://github.com/tvofi/heatpump_optimizer/pull/3029) — **open**, triage: s8 batch 83 (P320 ruling) (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch83.md b/dev/programme/triage/s6-batch83.md
new file mode 100644
index 000000000..72d444e0e
--- /dev/null
+++ b/dev/programme/triage/s6-batch83.md
@@ -0,0 +1,78 @@
+# Proposal triage, session s8, batch 83 (P320)
+
+The rolling batch (V182) after batch 82 (handoff `triage-s8-batch82`). Facts were read at
+origin/main `861f949ae`, on the roster branch, on every open pull request's `fix/*` branch, and in
+`git log` of main.
+
+## P320: seat commits carry a wrong author (`Claude`, or the owner's name), and nothing refuses them
+
+Verdict: ACCEPT as already carried, narrowed, with one amendment and a priority flag, on
+**R10-FLY-NO-FOOTERS** (`carries-open`). That group already holds both halves of this class.
+- **The refusal: P253** (`s6-batch51.md#P253`, 2026-10-28). `ref_privacy.py`'s `email_leaks` gains
+  an `anthropic-identity` class, run by `handoff_push.sh` and `app_push.sh` on every commit not
+  under `--over`.
+- **The detector at `body_push.sh` and the prevention: P274** (`s6-batch59.md#P274`). The cloud
+  fixer's setup text pins its identity with `git config`.
+- **Priority flag.** P253's refusal is the barrier that binds, and it is still unbuilt. Its
+  self-test at main still asserts `email_leaks("noreply@anthropic.com", fid) == []`
+  (`ref_privacy.py:717`). The roster op raises it to be dispatched first.
+- **Amendment to P274's prevention: export, not config.** P274(1) landed as a `git config` pin in
+  the fixer prompt (`cloud_dispatch.py:187`, `066bbfabe`, 2026-10-30T16:18Z). Commits made after it
+  are still authored `Claude`: #3016's at 21:03Z and 21:17Z. An author in the environment overrides
+  `git config`, which this very seat demonstrates: its own commit `1670b98d7` is authored `tvofi`
+  under a `git config user.name hpo-fixer`.
+  - So `tools/audit/seat/cloud-setup.sh` exports `GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL`,
+    `GIT_COMMITTER_NAME` and `GIT_COMMITTER_EMAIL` as the seat identity for the session.
+  - It currently sets neither: `grep -n 'GIT_AUTHOR\|git config' tools/audit/seat/cloud-setup.sh`
+    is empty.
+- **REJECTED: (a) as filed, "refuse a branch commit whose author is not hpo-fixer or the App".** It
+  would refuse the owner's own commits (`tvofi`), `github-actions[bot]`, `hpo-ledger[bot]` and
+  `hpo-author[bot]`, all legitimate on these branches. P253's class refuses exactly the forbidden
+  attribution.
+- **Out of tree, to the orchestrator.** The local seat launcher's environment sets
+  `GIT_AUTHOR_NAME=tvofi` and `GIT_COMMITTER_NAME=tvofi`, read in this seat's shell. That is why
+  local seats commit as the owner. Export the hpo-fixer identity there instead.
+- **Not proposed, and not ruled:** rewriting pushed history. That is the owner's call.
+
+Source: the orchestrator s8's message of 2026-10-31 (a slip, PR #3016).
+
+Instances, measured:
+- **Main, non-merge commits.** In the last 7 days, 195 are authored `Claude <noreply@anthropic.com>`
+  (`git log --no-merges --format='%an <%ae>' origin/main --since=7.days | sort | uniq -c`). In the
+  last 2 days, 38. So the class is live after P274's pin landed.
+- **Open pull requests (12).** Three branches carry Claude-authored commits ahead of main: #3016
+  `fix/r10-wood-notify` 8, #3009 `fix/r10-cop-gate-vent-fix` 2, #3004 `fix/r10-fly-cancel-sweep` 2.
+  That is 12 commits.
+- **The owner's name on seat commits.** Main's 7-day authors include 1718 non-merge commits as
+  `tvofi`, most of them seat commits under the launcher's environment. That count cannot be split
+  from the owner's own commits by author alone, which is why (a) is rejected and prevention is the
+  remedy for it.
+
+Cost:
+- P253 is about 10 lines plus fixtures (as carried).
+- The amendment is about 4 export lines in `cloud-setup.sh` plus one self-test assertion. No new
+  file or check.
+- `ref_privacy.py` and `cloud-setup.sh` are not capped files.
+
+Binding: 38 forbidden-attribution commits on main in 2 days, and 12 on open branches. The
+prevention already landed has been measured not to hold, and the refusal that would hold has been
+carried since 2026-10-28 and is unbuilt. Raising the refusal's priority and replacing a config pin
+the environment overrides costs a few lines. That is clearly positive.
+
+Carry text (for `roster_edit.py append-carry R10-FLY-NO-FOOTERS`, citing
+`triage: dev/programme/triage/s6-batch83.md#P320`): "P320 (orchestrator 2026-10-31, slip, PR #3016).
+PRIORITY: build P253's `anthropic-identity` refusal first, alone if needed.
+- At 861f949ae, `ref_privacy.py:717` still asserts `noreply@anthropic.com` passes.
+- Measured: 195 `Claude <noreply@anthropic.com>` non-merge commits on main in 7 days, 38 in 2 days.
+  Open branches #3016 (8), #3009 (2) and #3004 (2) carry them.
+- Amends P274(1): the identity pin in `cloud_dispatch.py:187` (`066bbfabe`, 2026-10-30T16:18Z) did
+  not hold. #3016's commits at 21:03Z and 21:17Z are still authored Claude, because an author in
+  the environment overrides `git config`.
+- `tools/audit/seat/cloud-setup.sh` exports `GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL`,
+  `GIT_COMMITTER_NAME` and `GIT_COMMITTER_EMAIL` as the seat identity (hpo-fixer, the noreply
+  address) for the session.
+- Its self-test asserts the four exports.
+- Null: a commit made in that environment is authored hpo-fixer even with a conflicting
+  `user.name` in config.
+- Do not refuse every non-hpo-fixer author: owner, github-actions, ledger and App commits are
+  legitimate."

