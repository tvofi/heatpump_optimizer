# Review packet #3077
head: 32d880b3dee4e525d16ec270af83d867f7006431
base: 92588d581fde4ce287af3db5e8bb61461dc28015

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124821986921 neutral
arch-score / arch-score id=124821822682 success
arm id=124821708560 skipped
budget-raise-gate / budget-raise-gate id=124821822747 success
cancel-superseded id=124821714253 success
codeql / Analyze (actions) id=124821822651 success
codeql / Analyze (javascript-typescript) id=124821822638 success
codeql / Analyze (python) id=124821822645 in_progress
governance / delivery-status id=124821822858 success
governance / delivery-status-publish id=124821823704 skipped
governance / env-matrix id=124821822724 in_progress
governance / instrument-self-tests id=124821822711 in_progress
governance / policy-docs id=124821822751 success
governance / record id=124821823783 skipped
governance / wave-script id=124821822824 success
hassfest / hassfest id=124821822691 success
kernel-points id=124821824506 skipped
prelude id=124821714117 in_progress
refresh id=124821714307 success
tests / arch-instrument id=124821948929 success
tests / briefs id=124821822788 success
tests / browser id=124821949039 in_progress
tests / closure-scope id=124821822773 success
tests / closures id=124821949014 in_progress
tests / coverage id=124821949015 in_progress
tests / fast (3.14) id=124821948995 in_progress
tests / mutation id=124821822648 success
tests / mutation-autofix id=124821987780 skipped
tests / mutation-pins id=124821987997 skipped
tests / nightly-ha id=124821949741 skipped
tests / nightly-status id=124821822603 success
tests / replay id=124821949603 skipped
tests / typing id=124821948983 success
validate / validate-hacs id=124821822630 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 5aa3bd73: dismissed:the brief binds the row path to its subject's number, a row is no code a review measures, and the round-1 review (O2) found no use beyond a row
NOTE body item 8093796d: dismissed:this is the trust boundary the confinement check has always used. Round 2 narrows it from every driver file to each subject's own paths, and each of those paths is graded at every head by the check its bot repairs for (closures, the mutation ledger and budgets, the claim hygiene).
NOTE body item f2f195f6: dismissed:a sizing note for the orchestrator, no later stage owns it
NOTE body item b0106364: dismissed:#3055 is its fix
CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         tests/closure.py selftest
             `tests/closure.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only
             `tests/env_drift.py` is in the tree at this head
  ok         tests/layout.py --guard --base <merge base>
             `tests/layout.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         tools/pr/prepr.sh <body>
             `tools/pr/prepr.sh` is in the tree at this head
  unverified git patch-id --stable
             `git patch-id` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 11 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/governance/roles/fix-review.md b/dev/governance/roles/fix-review.md
index 1301bd7e1..9e73fc38b 100644
--- a/dev/governance/roles/fix-review.md
+++ b/dev/governance/roles/fix-review.md
@@ -88,7 +88,8 @@ Long jobs and CI waits follow `fixer.md`'s preamble; rotate context between roun
 
     **A `merge` verdict attaches to the head its first line names and carries**
     (#1667; tvofi 2026-10-27) while `tools/audit/seat/review_carry.py
-    <verdicted> <new>` prints `CARRY`: no branch-only commit, not `head-moved`.
+    <verdicted> <new>` prints `CARRY`: the PR's patch is the one reviewed
+    (L6), not `head-moved`; a red CI never carries.
     Else a main merge is its **resolution delta**, alone yours; any other move is re-reviewed.
 
 13. **A conflict is a measurement, not a status field.** `mergeStateStatus:
diff --git a/dev/governance/roles/orchestrator.md b/dev/governance/roles/orchestrator.md
index 00cc225d6..a45507eb7 100644
--- a/dev/governance/roles/orchestrator.md
+++ b/dev/governance/roles/orchestrator.md
@@ -228,8 +228,8 @@ Through the roster seat, on `standing-roster.md`'s terms.
 - A `merge` verdict from a reviewer that measured **this** head, or a **carry**,
   with no reviewer turn (tvofi, 2026-10-01): `tools/pr/app_approve.sh --carry
   <verdict> <head>` reports carried, the files `git diff --name-only <verdict>
-  <head>` names miss the branch's own diff. Anything else is a resolution delta
-  for the same reviewer.
+  <head>` names miss the branch's own diff other than its own delivery row,
+  or keep its patch (L6). Else, a resolution delta for the same reviewer.
 - CI green at the verdicted head, landed onto a green `main` by
   `tools/audit/seat/merge_train.py batch` (tvofi, 2026-10-07), the only bypass:
   a proved batch merges while `main`'s tree equals its proof's; one entry merges
diff --git a/dev/governance/roles/standing-dispatch.md b/dev/governance/roles/standing-dispatch.md
index bf5b3b69f..173a8b1be 100644
--- a/dev/governance/roles/standing-dispatch.md
+++ b/dev/governance/roles/standing-dispatch.md
@@ -4,15 +4,15 @@ One of the four standing seats (`orchestrator.md` section 5); haiku, low
 effort. **Input:** the orchestrator's queue lines, each a pull request, head
 and role to dispatch or a relay to run; critical-path items first.
 
-**Dispatch**, per line: check the delivery row is in the pull request's
+**Dispatch**, per line: check the delivery row is in the PR's
 three-dot diff, then `tools/pr/approve_held_runs.sh`, `tools/audit/seat/bus.sh
 dispatch`, `tools/audit/seat/cloud_dispatch.py --role reviewer` at the printed
 head and nonce, and the `dispatch/reviewer-rev-<pr>` publish. Report
-`fire-owed <ref>`: a subagent cannot call RemoteTrigger, so the orchestrator
+`fire-owed <ref>`: a subagent cannot call RemoteTrigger; the orchestrator
 fires.
 
 **Relay:** run `tools/audit/seat/cloud_relay.sh --confirm`; on a merge verdict
-at the live head, `bus.sh confirm`. Report each `handoff-body/<topic>` return.
+carried to the live head, `bus.sh confirm`. Report each `handoff-body/<topic>` return.
 
 ## Read the ref, not the record
 
diff --git a/dev/programme/delivery/3077.md b/dev/programme/delivery/3077.md
new file mode 100644
index 000000000..fe7ccc089
--- /dev/null
+++ b/dev/programme/delivery/3077.md
@@ -0,0 +1 @@
+- [#3077](https://github.com/tvofi/heatpump_optimizer/pull/3077) — **open**, R10-FLY-CARRY-DOC-CONTEXT: fly carry doc context (R10-FLY-CARRY-DOC-CONTEXT)
diff --git a/tools/audit/seat/bus.sh b/tools/audit/seat/bus.sh
index 3338eaffb..1857831c7 100755
--- a/tools/audit/seat/bus.sh
+++ b/tools/audit/seat/bus.sh
@@ -31,11 +31,9 @@
 # THE ORDERING. `dispatch` refuses a head that carries no
 # `dev/programme/delivery/<pr>.md`, the pull request's own delivery row
 # (delivery-status-tracking.md). The row is the orchestrator's and lands
-# before the review: a row written after the verdict moves the head off the
-# one the reviewer measured, which `app_approve.sh --carry` refuses as a
-# commit of the branch's own, so it costs a re-review (R9-RCA-1990 class E).
-# A verdict posts only against a dispatch's nonce, so this is the one place
-# that can keep the row from landing late. `dispatch` also REFUSES TO MINT a
+# before the review, so the reviewer reads it at the head it measures; a row
+# written after the verdict, delivery_row.sh's own commit, carries the verdict
+# (`app_approve.sh --carry`, P123). `dispatch` also REFUSES TO MINT a
 # nonce for a head whose `review_carry.py <reviewed-head> <head>` answers
 # CARRY -- no branch-authored commit since the head the caller names with
 # --reviewed-head (tvofi, 2026-10-27: "if there are no code changes, the
@@ -913,7 +911,7 @@ bus-nonce: $N1b" ] && [ "$(grep -c " $N1b " "$W/state/dispatched")" = 2 ] \
   # THE REVIEW CARRY (R10-REVIEW-CARRY; tvofi, 2026-10-27). A fresh nonce over a
   # head whose range against the named reviewed head is clean starts a second
   # reviewer for a proof that did not move. `hm` is a merge-only move (main
-  # advances, the branch merges it); `h2` carries a non-merge commit. One
+  # advances, the branch merges it); `h2c` carries a code line. One
   # command, opposite answers: `review_carry.py` decides, dispatch refuses or
   # mints. origin/main is restored below so the orphans arms keep their base.
   cbase=$(git -C "$W/seat" rev-parse "origin/main")
@@ -935,9 +933,13 @@ bus-nonce: $N1b" ] && [ "$(grep -c " $N1b " "$W/state/dispatched")" = 2 ] \
     && ! python3 -I "$ROOT/tools/audit/seat/ledger.py" --log "$W/ledger/cloud-relay.log" board 2>/dev/null \
          | grep -q "reviewer-fire 31 "
   expect "dispatch refuses to mint a nonce over a clean range, naming the reviewed head, and records nothing" $?
-  out=$(seat dispatch 31 "$h2" cmsg_C2 --reviewed-head "$h1"); rc=$?
+  # `h2` alone is an empty commit, which carries (Lever L6): one code line on it.
+  git -C "$W/seat" checkout -q --detach "$h2"; printf 'code\n' > "$W/seat/carry-code.txt"
+  git -C "$W/seat" add carry-code.txt; git -C "$W/seat" -c user.name=t -c user.email=t@t commit -q -m "fix: one code line"
+  h2c=$(git -C "$W/seat" rev-parse HEAD)
+  out=$(seat dispatch 31 "$h2c" cmsg_C2 --reviewed-head "$h1"); rc=$?
   [ $rc = 0 ] && echo "$out" | grep -q '^bus-nonce: ' \
-    && [ "$(grep -c "^31 $h2 " "$W/state/dispatched")" = 1 ]
+    && [ "$(grep -c "^31 $h2c " "$W/state/dispatched")" = 1 ]
   expect "null control: dispatch mints at a head that does carry code" $?
   git -C "$W/seat" checkout -q main
   git -C "$W/seat" push -q -f origin "$cbase:refs/heads/main"
diff --git a/tools/audit/seat/instruments/review_carry.py.md b/tools/audit/seat/instruments/review_carry.py.md
index f2ac1bd7d..12eb2431d 100644
--- a/tools/audit/seat/instruments/review_carry.py.md
+++ b/tools/audit/seat/instruments/review_carry.py.md
@@ -4,19 +4,22 @@
   whether a moved head still needs its own review: `review_carry.py
   <reviewed> <new>` prints the branch-only commit count, their subjects and
   exactly one `CARRY`/`FRESH-REVIEW` (`git rev-list --count <reviewed>..<new>
-  --not origin/main`; CARRY needs zero, or every commit in it a merge, and
-  then `tools/pr/app_approve.sh --carry` carrying the range — each merge
-  git's automatic one, claim files a pure union or main's driver output, the branch's own diff equal
-  — asked, never copied, so the two cannot answer one range oppositely; a
-  merge of the branch's own previous head, update_pr.sh's re-cut, passes,
-  and a hand-resolved conflict does not). When: before
+  --not origin/main` counts and lists the range; CARRY is
+  `tools/pr/app_approve.sh --carry` carrying it — each merge git's automatic
+  one, claim files a pure union or main's driver output, each bot or
+  delivery-row commit inside its subject's paths, each commit of the branch's
+  own leaving the head the reviewed one merged onto main, each of main's
+  driver files at the head an automatic writer's (#3077), the branch's own
+  diff equal (Lever L6: the PR's patch is the one reviewed) — asked, never
+  copied, so the two cannot answer one range oppositely; a merge of the
+  branch's own previous head, update_pr.sh's re-cut, and a revert with its
+  re-apply pass, and a hand-resolved conflict does not). When: before
   dispatching a reviewer at a moved head, and in a verdict that re-issues a
   prior one — the owner's 2026-10-27 ruling, "if there are no code changes,
   the previous review can be carried", made mechanical. Refusal: an unknown
   sha, a missing main ref or a missing commit cannot be decided (exit 2, no
-  verdict line, so it is never read as CARRY); a force-push, a non-merge
-  commit — including the commits a merge of a non-main branch brings in — and
-  a `ci:`/`claims:` commit are all `FRESH-REVIEW`, and so is a range
-  `app_approve.sh --carry` refuses, with its reason.
+  verdict line, so it is never read as CARRY); a force-push is
+  `FRESH-REVIEW`, and so is a range `app_approve.sh --carry` refuses, with
+  its reason: a commit changing a line, a bot subject outside its paths.
   `--verdict-only` prints the token alone; `bus.sh dispatch --reviewed-head`
   is its caller, and `--self-test` grades the ranges.
diff --git a/tools/audit/seat/merge_train.py b/tools/audit/seat/merge_train.py
index f6e542967..ae73e9ac1 100644
--- a/tools/audit/seat/merge_train.py
+++ b/tools/audit/seat/merge_train.py
@@ -53,7 +53,7 @@ later pull request would be graded against a `main` the refused one never joined
                  one, which is why the refusal fires only where the head
                  already contains main;
   3. carry    -- `app_approve.sh --carry <verdict> <head>` must say `CARRY: yes`:
-                 the head differs from the verdicted one only by automatic merges;
+                 the pull request's patch at the head is the verdicted one's (L6);
   4. main     -- `origin/main` is still inside the head after CI (else main moved:
                  recovered up to --main-moved-tries times, below);
   5. policy   -- no changed file (`--no-renames`, so a rename names the path it
@@ -1797,7 +1797,7 @@ class Train:
         listed = ", ".join(f"`{p}`" for p in paths)
         body = (f"Agent approval for {what} {listed}, given by {self.role} under {under}, at head {h}.\n\n"
                 f"Basis: `Fix review: merge {item['verdict']}` (comment {item.get('verdict_comment', '?')}), carried to {h} "
-                f"by `app_approve.sh --carry` (automatic main merges only). CI at {h} is green"
+                f"by `app_approve.sh --carry` (the pull request's patch is the verdicted one's). CI at {h} is green"
                 + (f" apart from {', '.join('`%s`' % n for n in self.ignore)}, which grade main." if self.ignore else ".") + "\n")
         bf = self.state / f"{name}{pr}.md"
         bf.write_text(body)
@@ -6651,7 +6651,7 @@ def _add_self_test(check) -> None:
               "(app_approve.sh's own CARRY: no), nothing spooled",
               rc == 1 and lines[-1].startswith(f"ADD REFUSED #11 carry: the verdict {cv[:12]} does not carry to "
                                                f"head {cn[:12]}: CARRY: no")
-              and f": {cn} is a commit of the" in lines[-1]
+              and f"own commits {cn[:9]} change its content" in lines[-1]
               and [e["pr"] for e in spool_read(st)[0]] == [8, 10])
 
         st = Path(tempfile.mkdtemp(dir=tmp.name))
diff --git a/tools/audit/seat/ref_privacy.py b/tools/audit/seat/ref_privacy.py
index a3f68e58c..77832c0c2 100644
--- a/tools/audit/seat/ref_privacy.py
+++ b/tools/audit/seat/ref_privacy.py
@@ -389,6 +389,8 @@ PUSHERS = {
     ".github/workflows/nightly.yml": ("republishes", "on a runner, constant-message bot commits onto "
                                       "record/autofix or main (nightly kills), moved out of tests.yml"),
     "tools/pr/app_approve.sh": ("fixture", "its pushes are the self-test's, into a temp bare repository"),
+    "tools/pr/app_comment.sh": ("fixture", "its pushes are the self-test's, into a temp bare repository; "
+                                "the carry it tests only fetches"),
     "tools/audit/seat/ledger.py": ("fixture", "its pushes are the self-test's, into a temp bare repository; "
                                    "the ledger itself only reads refs (ls-remote, fetch)"),
     "tools/audit/seat/review_strength.py": ("fixture", "its one push is the --fetch self-test's, into a temp "
diff --git a/tools/audit/seat/review_carry.py b/tools/audit/seat/review_carry.py
index a37da51d8..77d5c8f6c 100755
--- a/tools/audit/seat/review_carry.py
+++ b/tools/audit/seat/review_carry.py
@@ -11,20 +11,22 @@ THE TEST IS A COMMIT RANGE, NOT AN OPINION:
 
     git rev-list --count <reviewed-head>..<new-head> --not origin/main
 
-Any non-merge commit in that range means the head carries code and takes a
-fresh review: this prints FRESH-REVIEW, and no subject is exempt -- a
-claim-file resolution or a `ci:`/`claims:` bot commit landing as a commit is a
-change. Zero, or a count whose commits are all merges, is no branch-authored
-commit; what a merge can still author is its resolution, so the range then
-carries only where `tools/pr/app_approve.sh --carry` carries it -- each merge
-git's own automatic merge of its parents outside main's driver files, each
-claim file the pure union of both sides or main's claim-driver output on
-them, and the branch's own diff equal at
-both heads -- and this prints CARRY. A merge of the branch's own previous
-head, the shape update_pr.sh re-cuts one into, passes all three. A
-hand-resolved conflict, a line a merge adds of its own, or a main change that
-rewrote the branch's hunk context is FRESH-REVIEW with app_approve.sh's
-reason. One predicate, asked rather than copied: two copies once answered the
+The range carries only where `tools/pr/app_approve.sh --carry` carries it,
+and this prints CARRY: each merge git's own automatic merge of its parents
+outside main's driver files, each claim file the pure union of both sides or
+main's claim-driver output on them, each bot or delivery-row commit confined
+to its subject's paths as its writer, each commit of the branch's own leaving
+the head's tree git's automatic merge of the reviewed head onto main, each of
+main's driver files at the head that merge, main's driver output, the claim
+union or what the newest carried bot commit left (#3077), and the
+branch's own diff equal at both heads (Lever L6, tvofi 2026-10-30: the PR's
+patch at the new head equals the reviewed one's). A merge of the branch's own
+previous head, the shape update_pr.sh re-cuts one into, and a revert with
+its re-apply both pass. A hand-resolved conflict, a line a merge or a commit
+adds of its own, or a main change that rewrote the branch's hunk context in
+code is FRESH-REVIEW with app_approve.sh's reason. Non-merge commits are
+counted and listed, never decided here. One predicate, asked rather than
+copied: two copies once answered the
 same range oppositely, and `bus.sh dispatch` then refused the re-review that
 app_approve.sh refused to carry. A body rewrite never by itself voids a
 verdict, because it is not a commit in the range. (This answers the
@@ -116,7 +118,8 @@ def app_approve_carry(repo, reviewed, new, main):
     """-> None when app_approve.sh --carry carries reviewed -> new, else its
     reason: each merge git's automatic one outside main's driver files, each
     claim file the pure union of both sides or main's claim-driver output on
-    them, the branch's own diff equal."""
+    them, each driver file at the head an automatic writer's, the branch's own
+    diff equal."""
     proc = subprocess.run(["bash", APP_APPROVE, "--carry", reviewed, new, main],
                           cwd=repo, capture_output=True, text=True)
     out = proc.stdout.strip()
@@ -164,19 +167,14 @@ def classify(repo, reviewed, new, main):
             reason += "; %d of %d branch-only commit(s) carry code" % (
                 len(carrying), count)
         return FRESH, reason, count, commits
-    if carrying:
-        return (FRESH,
-                "%d of %d branch-only commit(s) carry code"
-                % (len(carrying), count),
-                count, commits)
     why = app_approve_carry(repo, reviewed, new, main)
     if why:
         return FRESH, why, count, commits
     if count == 0:
         return CARRY, "no branch-only commit", 0, []
     return (CARRY,
-            "all %d branch-only commit(s) are automatic merges, and "
-            "app_approve.sh --carry carries the range" % count,
+            "%d of %d branch-only commit(s) are non-merge, and "
+            "app_approve.sh --carry carries the range" % (len(carrying), count),
             count, commits)
 
 
@@ -340,7 +338,27 @@ def self_test():
     check("head did not move answers CARRY", v, CARRY)
 
     v, _, _, _ = answer(reviewed, bot)
-    check("a bot-subject commit is a code move", v, FRESH)
+    check("a bot-subject commit after a code move answers FRESH-REVIEW", v, FRESH)
+
+    # L6: a commit of the branch's own that leaves the reviewed patch as it
+    # was -- a revert and its re-apply -- carries; a re-apply one byte away
+    # does not. Both are non-merge commits, so only app_approve.sh decides.
+    _t(seat, "checkout", "-q", "-b", "fix/reapply", merged)
+    _t(seat, "rm", "-q", "code.txt")
+    _commit(seat, "Revert: the code")
+    with open(os.path.join(seat, "code.txt"), "w") as fh:
+        fh.write("reviewed\n")
+    _t(seat, "add", "code.txt")
+    reapplied = _commit(seat, "Re-apply: the code")
+    v, why, n, _ = answer(reviewed, reapplied)
+    check("a revert and its re-apply answers CARRY (L6)", v, CARRY)
+    check("and counts its two non-merge commits", "2 of 3" in why, True)
+    _t(seat, "checkout", "-q", "-b", "fix/reapply-x", merged)
+    with open(os.path.join(seat, "code.txt"), "w") as fh:
+        fh.write("reviewed!\n")
+    _t(seat, "add", "code.txt")
+    v, _, _, _ = answer(reviewed, _commit(seat, "Re-apply: one byte away"))
+    check("a re-apply one byte away answers FRESH-REVIEW", v, FRESH)
 
     v, _, _, _ = answer(reviewed, feat_merge)
     check("a merge of a non-main branch answers FRESH-REVIEW", v, FRESH)
diff --git a/tools/pr/app_approve.sh b/tools/pr/app_approve.sh
index 43a4167e3..af8441192 100755
--- a/tools/pr/app_approve.sh
+++ b/tools/pr/app_approve.sh
@@ -54,33 +54,50 @@
 #     or empty CODEOWNERS refuses. Matching errs toward owning, which refuses;
 #   - the head is still <sha> when re-read after minting, just before the POST.
 #
-# THE CARRY (#1667, D13-s1-02; R10-REVIEW-CARRY). A verdict at V carries to a
-# later head H only when (1) V is an ancestor of H; (2) every commit
-# `git rev-list V..H --not main` returns is a merge, or a single-parent `ci:`/
-# bot commit confined to the files its subject names -- a merge authors no
-# code of its own, because what it joins is main's history (outside the
-# range) or branch commits (inside it, refused by this clause), so a merge of
-# the branch's own previous head, which is how update_pr.sh re-cuts a head,
-# is no change (tvofi, 2026-10-27: "if there are no code changes, the
-# previous review can be carried"); (3) each merge's tree is git's automatic
-# merge of its parents outside the driver files below, and it resolves each
+# THE CARRY (#1667, D13-s1-02; R10-REVIEW-CARRY; Lever L6). A verdict at V
+# carries to a later head H when the pull request's patch against its merge
+# base with main at H is the one reviewed at V (tvofi, 2026-10-30), read as:
+# (1) V is an ancestor of H; (2) each commit `git rev-list V..H --not main`
+# returns is a merge; a single-parent `ci:` or bot commit confined to main's
+# driver files and the paths its subject names, as that subject's writer --
+# `record: the delivery row for #<N>` (delivery_row.sh, as tvofi) names
+# `dev/programme/delivery/<N>.md` (P123); or a commit of the branch's own,
+# carried only where H's tree is git's automatic merge of V onto H's merge
+# base with main outside the files (4) leaves out, because (4) drops line
+# numbers and alone would pass a change moved to other code with the same
+# context. A merge authors no code of its own: what it joins is main's history
+# (outside the range) or branch commits (inside it, read by this clause), so a
+# merge of the branch's own previous head, how update_pr.sh re-cuts a head, is
+# no change (tvofi, 2026-10-27: "if there are no code changes, the previous
+# review can be carried"); (3) each merge's tree is git's automatic merge of
+# its parents outside the driver files below, and it resolves each
 # `merge=claimnotes` file to a pure union of its two parents' lines or to
 # exactly what main's claim driver writes on them (P290), because any other
 # resolution that drops, adds or rewrites a line is content no review
 # measured; and (4) the branch's own diff against its merge base with main is
-# byte-identical
-# at V and at H, read with two relaxations measured over round 9's window
-# (the literal byte rule carried 0 of its 22 re-verification rounds): each
-# hunk header (line numbers, and the function line git reads from above the
-# hunk) and each `index` line are dropped, so a hunk main's merge only shifted
-# still compares equal; and the files main's
-# `.gitattributes` gives a merge driver are left out, because stamps and CI
-# bots rewrite those on main and required checks grade them at every head.
-# Anything else -- a rewrite, a commit of the branch's own, one changed byte
-# in a hunk or its context -- keeps today's re-review. Condition (4) is the
-# guard; (1), (2) and (3) name the moves it applies to, and a `ci:` subject
-# buys nothing on its own. The evidence gate then reads V, the head the
-# reviewer measured.
+# byte-identical at V and at H -- `git patch-id --verbatim`'s reading, whose
+# `--stable` default would also strip whitespace a Python indent means --
+# read with three relaxations measured over round 9's window (the literal
+# byte rule carried 0 of its 22 re-verification rounds): each hunk header
+# (line numbers, and the function line git reads from above the hunk) and
+# each `index` line are dropped, so a hunk main's merge only shifted still
+# compares equal; the files main's `.gitattributes` gives a merge driver, and
+# what a carried bot or row commit wrote, are left out, because stamps and CI
+# bots rewrite those and required checks grade them at every head; and in a
+# `*.md` file each context line reads as a bare ` ` (P17), so main's rewrite
+# of prose beside the branch's lines carries while the hunk's context count
+# and its +/- lines still compare -- code keeps its context (P325). Anything
+# else -- a rewrite, one changed byte in a +/- line or a code hunk's context
+# -- keeps today's re-review. (5) What (3) and (4) leave out, main's
+# merge-driver files, is read at the head on its own (#3077): each holds git's
+# automatic merge of V onto H's merge base with main, main's own driver output
+# on the two, for a claim file their union, or what the newest carried
+# author-checked bot commit left -- so neither a commit of the branch's own, a
+# bare `ci:` subject nor a merge's hand resolution carries a budget, closure
+# or claim line no review measured. Condition (4) is the guard; (1), (2) and (3)
+# name the moves it applies to, and a `ci:` subject buys nothing on its own.
+# CI still runs at every head, and a red one is never carried. The evidence
+# gate then reads V, the head the reviewer measured.
 #
 # THE SECRETS. The key files are `$HPO_IDENTITY_DIR/identity-approver.appid`
 # and `identity-approver.pem` (default directory `~/.zcode`). The JWT and the
@@ -213,7 +230,7 @@ bot_author() { # subject -> the author email its writer commits as
   case "$1" in
     "ci: pin killed mutants"|"ci: re-record closures"|"ci: drop inherited claims")
       echo "41898282+github-actions[bot]@users.noreply.github.com" ;;
-    "claims: drop the claims main already carries after the main merge")
+    "claims: drop the claims main already carries after the main merge"|"record: the delivery row for #"[1-9]*)
       echo "70032254+tvofi@users.noreply.github.com" ;;
   esac
 }
@@ -223,21 +240,38 @@ bot_paths() { # subject -> one pathspec per line, nothing for an unknown subject
     "ci: re-record closures") printf '%s\n' tests/closures.json ;;
     "ci: drop inherited claims"|"claims: drop the claims main already carries after the main merge")
       printf '%s\n' tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt ;;
+    # delivery_row.sh commit_row's subject, for an add and an edit alike: its
+    # one path is the row of the <N> it names, so a row commit under one
+    # pull request's number cannot write another's (P123).
+    "record: the delivery row for #"[1-9]*)
+      local n=${1#record: the delivery row for #}
+      [[ $n =~ ^[1-9][0-9]*$ ]] && echo "dev/programme/delivery/$n.md" ;;
   esac
 }
 
 # claim_driver_wrote <main ref> <merge> <parent 1> <parent 2> <path>: 0 only when
 # main's claim driver resolves <path> at (merge base, parent 1, parent 2) and its
 # output is byte-equal to <path> at <merge>. Quiet, like merge-tree in `carry`.
-claim_driver_wrote() {
-  local m=$1 c=$2 a=$3 b=$4 p=$5 o d r=1
+claim_driver_wrote() { driver_wrote "$@" claimnotes; }
+
+# driver_wrote <main> <commit> <a> <b> <path> <driver>: 0 when <commit>'s <path>
+# is byte-equal to what main's own <driver> (claimnotes or ledgermerge, as
+# main's .gitattributes names them) writes on (merge base, a, b). Main's copy
+# of the driver, never a head's: a branch's own driver would grade itself.
+driver_wrote() {
+  local m=$1 c=$2 a=$3 b=$4 p=$5 o d r=1 src flag
+  case $6 in
+    claimnotes) src=tests/env_drift.py flag=--merge-claim-file ;;
+    ledgermerge) src=tools/merge/ledger_merge.py flag=--merge ;;
+    *) return 1 ;;
+  esac
   o=$(git merge-base "$a" "$b" 2>/dev/null) || return 1
   d=$(mktemp -d) || return 1
-  git show "$m:tests/env_drift.py" > "$d/driver.py" 2>/dev/null \
+  git show "$m:$src" > "$d/driver.py" 2>/dev/null \
     && { git show "$o:$p" > "$d/O" 2>/dev/null || :; } \
     && { git show "$a:$p" > "$d/A" 2>/dev/null || :; } \
     && { git show "$b:$p" > "$d/B" 2>/dev/null || :; } \
-    && python3 -I "$d/driver.py" --merge-claim-file "$d/O" "$d/A" "$d/B" 7 "$p" >/dev/null 2>&1 \
+    && python3 -I "$d/driver.py" "$flag" "$d/O" "$d/A" "$d/B" 7 "$p" >/dev/null 2>&1 \
     && git show "$c:$p" 2>/dev/null | cmp -s - "$d/A" && r=0
   rm -rf "$d"
   return $r
@@ -245,7 +279,7 @@ claim_driver_wrote() {
 
 # carry <verdict sha> <head sha> <main ref>: prints the reason; 0 only on a carry.
 carry() {
-  local v=$1 h=$2 main=$3 c ps ae subj p mv mh t x y b ba bt e cp got want
+  local v=$1 h=$2 main=$3 c ps ae subj p mv mh t x y b ba bt e cp got want own="" botc="" drv lb
   git merge-base --is-ancestor "$v" "$h" 2>/dev/null || { echo "$v is not an ancestor of $h"; return 1; }
   # Read at main, never at a head: a branch that gave a file a driver would
   # otherwise take it out of the comparisons itself.
@@ -316,7 +350,9 @@ carry() {
           || { echo "$c resolves $p to something other than the union of its parents or main's driver output on them"; return 1; }
       done <<<"$cp"
     elif [[ $subj != ci:* ]] && [ -z "$(bot_paths "$subj")" ]; then
-      echo "$c is a commit of the branch's own ($subj)"; return 1
+      # A commit of the branch's own: carried only where the head's content is
+      # the reviewed head's, merged onto the main it now sits on (below, L6).
+      own="$own${c:0:9} "
     else
       # Anyone who can push can write the subject, and the header-free
       # comparison below cannot see a change moved to other code with the
@@ -332,9 +368,11 @@ carry() {
         y=(${x[@]+"${x[@]}"})
         while IFS= read -r p; do [ -z "$p" ] || y[${#y[@]}]=":(exclude)$p"; done <<<"$b"
         git diff --quiet "$c^" "$c" -- . ${y[@]+"${y[@]}"} \
-          || { echo "$c is a ci: commit that changes files outside main's merge-driver files and the paths of its subject"; return 1; }
+          || { echo "$c is a commit under a bot's or the delivery row's subject that changes files outside main's merge-driver files and the paths of its subject"; return 1; }
         [ "$ae" = "$(bot_author "$subj")" ] \
           || { echo "$c is authored by $ae, not the writer of its subject ($subj)"; return 1; }
+        # Newest first: what its writer left in one of its own paths stands (below).
+        while IFS= read -r e; do [ -z "$e" ] || botc="$botc$c $e"$'\n'; done <<<"$b"
         case "$subj" in *claims*)
           [ "$(git diff --numstat "$c^" "$c" | awk '{s+=$1} END {print s+0}')" = 0 ] \
             || { echo "$c adds claim lines, and its subject only drops them"; return 1; } ;;
@@ -385,12 +423,66 @@ carry() {
   # never exposed to a forged commit choosing its own filenames this way.)
   while IFS= read -r p; do [ -z "$p" ] || x[${#x[@]}]=":(exclude,literal)$p"; done <<<"$(printf '%s' "$bots" | sort -u)"
   mv=$(git merge-base "$main" "$v") && mh=$(git merge-base "$main" "$h") || { echo "no merge base with $main"; return 1; }
+  # The branch's own commits (Lever L6, tvofi 2026-10-30): a revert and its
+  # re-apply, or an empty commit, leaves the reviewed change where it was. The
+  # comparison below drops each hunk's line numbers, so it alone would also
+  # pass a commit moving the change to other code with the same context; the
+  # head's tree must therefore be git's automatic merge of the reviewed head
+  # onto the main it now sits on, outside the files the comparison leaves out.
+  if [ -n "$own" ]; then
+    t=$(git merge-tree --write-tree --no-messages "$v" "$mh" 2>/dev/null | head -1)
+    case $t in
+      ""|*[!0-9a-f]*)
+        echo "the branch's own commits ${own% } follow a reviewed head that does not merge automatically onto $mh"; return 1 ;;
+    esac
+    git diff --quiet "$t" "$h" -- . ${x[@]+"${x[@]}"} \
+      || { echo "the branch's own commits ${own% } change its content: $h is not the reviewed head $v merged onto $mh"; return 1; }
+  fi
+  # The driver files' end state (#3077 round 1). Every comparison above leaves
+  # main's merge-driver files out, so a budget, closure or claim line written
+  # by a commit of the branch's own, by a `ci:` subject anyone can write, or by
+  # a merge's hand resolution would otherwise carry unreviewed. What each holds
+  # at the head must be what an automatic writer produced: git's merge of the
+  # reviewed head onto main as this clone's drivers write it; main's own
+  # driver on the two, for a clone without them; for a claim file, the union
+  # of both sides, the resolution the merge check above also takes; or the
+  # file as the newest carried bot commit to change it left it, a bot being
+  # an author-checked subject (`bot_author`), never a bare `ci:`, and the file
+  # one of that subject's own paths (`bot_paths`): a closures bot rewriting a
+  # budget is not that budget's writer.
+  t=$(git merge-tree --write-tree --no-messages "$v" "$mh" 2>/dev/null | head -1)
+  case $t in *[!0-9a-f]*) t="" ;; esac
+  while read -r p drv; do
+    [ -n "$p" ] || continue
+    [ -n "$t" ] && [ "$(git rev-parse -q --verify "$t:$p")" = "$(git rev-parse -q --verify "$h:$p")" ] && continue
+    driver_wrote "$main" "$h" "$v" "$mh" "$p" "$drv" && continue
+    if [ "$drv" = claimnotes ]; then
+      got=$(git show "$h:$p" 2>/dev/null | awk 'NF' | sort -u)
+      want=$({ git show "$v:$p" 2>/dev/null; git show "$mh:$p" 2>/dev/null; } | awk 'NF' | sort -u)
+      [ "$got" = "$want" ] && continue
+    fi
+    lb=""
+    while read -r c e; do
+      [ "$e" = "$p" ] || continue
+      git diff --quiet "$c^" "$c" -- ":(literal)$p" || { lb=$c; break; }
+    done <<<"$botc"
+    [ -n "$lb" ] && [ "$(git rev-parse -q --verify "$lb:$p")" = "$(git rev-parse -q --verify "$h:$p")" ] && continue
+    echo "$p at $h is not the reviewed head $v merged onto $mh, main's driver output on them, nor what a carried bot commit wrote"; return 1
+  done <<<"$(git show "$main:.gitattributes" 2>/dev/null \
+    | awk '!/^#/ {for (i = 2; i <= NF; i++) if ($i ~ /^merge=/) {print $1, substr($i, 7); break}}')"
   local d=(git -c core.quotepath=off diff --binary --no-renames --no-color --no-ext-diff --no-textconv
     --diff-algorithm=myers -U3)
-  norm() { "${d[@]}" "$1" "$2" -- . ${x[@]+"${x[@]}"} | sed -e '/^index /d' -e 's/^@@ .*/@@/'; }
+  # In a `*.md` file each context line reads as a bare ` ` (P17): prose main
+  # rewrote beside the branch's lines changes no line the branch wrote, and
+  # the hunk's shape -- its context count, its +/- lines -- still compares.
+  # Code files keep their context: there the lines beside a change are
+  # behaviour (P325).
+  norm() { "${d[@]}" "$1" "$2" -- . ${x[@]+"${x[@]}"} | sed -e '/^index /d' -e 's/^@@ .*/@@/' \
+    | awk '/^diff --git / { md = /\.md$/ } md && /^ / { print " "; next } { print }'; }
   cmp -s <(norm "$mv" "$v") <(norm "$mh" "$h") \
     || { echo "the branch's own diff differs: $mv..$v against $mh..$h"; return 1; }
-  echo "no branch-authored commit in the range, every merge the automatic one with its claim files a pure union of both sides or main's driver output on them, and the branch's own diff compares equal"
+  [ -z "$own" ] || own="the branch's own commits ${own% } leaving the head the reviewed one merged onto main, "
+  echo "every merge in the range the automatic one with its claim files a pure union of both sides or main's driver output on them, every bot or row commit inside its paths, ${own}and the branch's own diff compares equal"
 }
 
 cleanup() {
@@ -762,7 +854,8 @@ g() { git -C "$W/clone" -c push.negotiate=false "$@"; }
 throwaway_git_init "$W/remote.git" -q --bare && throwaway_git_init "$W/clone" -q -b main && g remote add origin "$W/remote.git"
 ed1() { sed -i.bak "$1" "$W/clone/$2" && rm "$W/clone/$2.bak"; }
 seq 1 40 > "$W/clone/a.txt"; echo b > "$W/clone/b.txt"; seq -f 'l%g' 1 10 > "$W/clone/led.json"
-echo 'led.json merge=ledgermerge' > "$W/clone/.gitattributes"; g add -A; g commit -qm m0
+mkdir -p "$W/clone/tests"; seq -f 'c%g' 1 10 > "$W/clone/tests/closures.json"
+printf 'led.json merge=ledgermerge\ntests/closures.json merge=ledgermerge\n' > "$W/clone/.gitattributes"; g add -A; g commit -qm m0
 g checkout -qb fixa; ed1 's/^5$/five/' a.txt; echo 'a.txt merge=ledgermerge' >> "$W/clone/.gitattributes"
 g commit -qam "fix: own, with a driver for its own file"; V_A=$(g rev-parse HEAD)
 g checkout -q main; g checkout -qb fix; ed1 's/^5$/five/' a.txt; ed1 's/^l1$/L1/' led.json; g commit -qam "fix: own"
@@ -778,7 +871,8 @@ H_EVIL=$(mkmerge "$V" "$M1" "Merge origin/main into fix" evil)
 g checkout -q --detach "$V"; echo x >> "$W/clone/b.txt"; g commit -qam "fix: more"; H_OWN=$(g rev-parse HEAD)
 g checkout -q --detach "$V"; echo rec > "$W/clone/c.json"; g add c.json; g commit -qm "ci: re-record closures"; H_CI=$(g rev-parse HEAD)
 g checkout -q --detach "$V"; g commit -q --allow-empty -m "ci: empty"; H_CIEMPTY=$(g rev-parse HEAD)
-g checkout -q --detach "$V"; ed1 's/^l9$/L9/' led.json; GIT_AUTHOR_EMAIL="41898282+github-actions[bot]@users.noreply.github.com" g commit -qam "ci: re-record closures"; H_CILED=$(g rev-parse HEAD)
+g checkout -q --detach "$V"; ed1 's/^c9$/C9/' tests/closures.json; GIT_AUTHOR_EMAIL="41898282+github-actions[bot]@users.noreply.github.com" g commit -qam "ci: re-record closures"; H_CILED=$(g rev-parse HEAD)
+g checkout -q --detach "$V"; ed1 's/^l9$/L9/' led.json; GIT_AUTHOR_EMAIL="41898282+github-actions[bot]@users.noreply.github.com" g commit -qam "ci: re-record closures"; H_CIOUT=$(g rev-parse HEAD)
 g checkout -q --detach "$V"; g commit -q --allow-empty -m "fix: nothing"; H_OWNEMPTY=$(g rev-parse HEAD)
 # R9-CI-2b: each bot's own paths. mutation-autofix writes the ledger, which
 # is no merge-driver file; remerge_main.sh drops inherited claims under a
@@ -1520,11 +1614,16 @@ carried "$H_MERGE"; st $? 0 "CARRY: a merge from main that leaves the branch's o
 carried "$H_CIEMPTY"; st $? 0 "CARRY: a ci: commit that changes nothing"
 carried "$H_EVIL"; st $? 1 "NO CARRY: the same merge with one byte of a.txt changed in its resolution (null control)"
 st "$(grep -c "not the automatic merge" "$W/carry.out")" 1 "refused as a hand-resolved merge"
-carried "$H_OWN"; st $? 1 "NO CARRY: a commit of the branch's own"
-carried "$H_OWNEMPTY"; st $? 1 "NO CARRY: an empty commit of the branch's own, which the byte comparison alone would pass"
+carried "$H_OWN"; st $? 1 "NO CARRY: a commit of the branch's own that changes a code line"
+st "$(grep -c "own commits ${H_OWN:0:9} change its content" "$W/carry.out")" 1 "refused naming that commit"
+# Lever L6 (tvofi, 2026-10-30): a commit of the branch's own that leaves the
+# reviewed change as it was carries; before L6 this one refused.
+carried "$H_OWNEMPTY"; st $? 0 "CARRY: an empty commit of the branch's own (L6)"
 carried "$H_CI"; st $? 1 "NO CARRY: a ci: commit that changes the branch's diff"
 st "$(grep -c "outside main's merge-driver files" "$W/carry.out")" 1 "refused as a ci: commit outside the driver files"
-carried "$H_CILED"; st $? 0 "CARRY: a ci: commit that rewrites only a merge-driver file"
+carried "$H_CILED"; st $? 0 "CARRY: a bot commit that rewrites only its own merge-driver file"
+carried "$H_CIOUT"; st $? 1 "NO CARRY: the same bot subject rewriting a merge-driver file outside its own paths (#3077)"
+st "$(grep -c "led.json at $H_CIOUT is not" "$W/carry.out")" 1 "refused naming the driver file"
 carried "$H_PIN_BADMSG"; st $? 1 "NO CARRY: the bot's confined additions, under a ci: subject no writer uses"
 st "$(grep -c "outside main's merge-driver files" "$W/carry.out")" 1 "refused by the generic ci: guard, not the bot one"
 # The narrowing that `bot_paths`' whole-subtree exclusion alone does not give:
@@ -1579,6 +1678,12 @@ st "$(grep -c "not the automatic merge" "$W/carry.out")" 1 "refused for the hand
   bash "$SELF" --carry "$(cat ../reloc.v)" "$(git rev-parse HEAD)" main ) > "$W/carry.out" 2>&1
 st $? 1 "NO CARRY: a ci: commit that moves the branch's change to another function with the same context"
 st "$(grep -c "outside main's merge-driver files" "$W/carry.out")" 1 "refused by the ci: guard"
+( cd "$W/reloc" || exit 2; git checkout -q --detach "$(cat ../reloc.v)"
+  git show main~1:f.py > f.py; sed -i.bak '14s/limit(a)/limit(a, safe=True)/' f.py; rm f.py.bak
+  git commit -qam "fix: move the guard"
+  bash "$SELF" --carry "$(cat ../reloc.v)" "$(git rev-parse HEAD)" main ) > "$W/carry.out" 2>&1
+st $? 1 "NO CARRY: a commit of the branch's own that moves its change to another function with the same context (L6)"
+st "$(grep -c "change its content" "$W/carry.out")" 1 "refused by the re-merge tree check, which the header-free comparison cannot replace"
 carried "$H_PIN"; st $? 0 "CARRY: mutation-autofix's ledger commit, inside its own paths (R9-CI-2b)"
 carried "$H_PINOUT"; st $? 1 "NO CARRY: the same subject touching one more file outside its paths"
 carried "$H_PINELSE"; st $? 1 "NO CARRY: the ledger under another bot's subject, whose paths do not hold it"
@@ -1590,7 +1695,10 @@ st $? 0 "CARRY: remerge_main.sh's inherited-claims commit, only dropping a claim
 st $? 1 "NO CARRY: the same subject adding a claim line"
 H_MERGEPIN=$(pin_commit "$H_MERGE" "ci: pin killed mutants" tests/mutation_ledger/killed_by/b.json)
 carried "$H_MERGEPIN"; st $? 0 "CARRY: a merge from main, then the ledger commit it set off (#2024's shape)"
-carried "$H_SIDE"; st $? 1 "NO CARRY: a merge of a branch that is not main"
+carried "$H_SIDE"; st $? 0 "CARRY: a merge of a side branch whose one commit is empty (L6: no PR line changed)"
+g checkout -q -b side2 "$V"; echo side >> "$W/clone/b.txt"; g commit -qam side2; SIDE2=$(g rev-parse HEAD)
+H_SIDE2=$(mkmerge "$V" "$SIDE2" "Merge side2 into fix")
+carried "$H_SIDE2"; st $? 1 "NO CARRY: a merge of a branch that is not main, its one commit changing a line"
 g checkout -q --detach "$V"; g merge -q --no-ff --no-edit -m "octopus" "$M1" "$SIDE" >/dev/null; H_OCTO=$(g rev-parse HEAD)
 carried "$H_OCTO"; st $? 1 "NO CARRY: one merge of main and another branch at once"
 # A seat merges main into the head and hands that off as a code head, which
@@ -1705,6 +1813,127 @@ H_DF=$( cd "$RD" && git checkout -q --detach "$VF" && git merge -q --no-ff --no-
 ( cd "$RD" && bash "$SELF" --carry "$VF" "$H_DF" main ) > "$W/carry.out" 2>&1
 st $? 1 "NO CARRY: main's side dropped by hand, which only the head's own driver would write"
 st "$(grep -c "union of its parents" "$W/carry.out")" 1 "refused on main's driver, not the head's"
+# The claim-file twin (#3077 round 1): an own commit after the driver's merge.
+H_DROWN=$( cd "$RD" && git checkout -q --detach "$H_DR" && printf 'c9 # own\n' >> tests/golden/claimed_drift.txt \
+  && git commit -qam "fix: tidy wording" && git rev-parse HEAD )
+( cd "$RD" && bash "$SELF" --carry "$VD" "$H_DROWN" main ) > "$W/carry.out" 2>&1
+st $? 1 "NO CARRY: a commit of the branch's own that adds a claim line after main's driver resolved the merge"
+st "$(grep -c "claimed_drift.txt at $H_DROWN is not" "$W/carry.out")" 1 "refused naming the claim file"
+H_DREMPTY=$( cd "$RD" && git checkout -q --detach "$H_DR" && git commit -q --allow-empty -m "fix: nothing" && git rev-parse HEAD )
+( cd "$RD" && bash "$SELF" --carry "$VD" "$H_DREMPTY" main ) > "$W/carry.out" 2>&1
+st $? 0 "CARRY: an empty commit of the branch's own after main's driver resolved the claim file (null control)"
+# A clone without the drivers configured (CI's, or a fresh checkout) has
+# git's text merge where the driver wrote, so main's own driver is run on the
+# two: once for the claim file above, once for a ledger.
+( cd "$RD" && git config --remove-section merge.claimnotes && bash "$SELF" --carry "$VD" "$H_DREMPTY" main ) > "$W/carry.out" 2>&1
+st $? 0 "CARRY: the same in a clone with no claim driver configured, read by main's own driver"
+( cd "$RD" && git config merge.claimnotes.name claims \
+  && git config merge.claimnotes.driver 'python3 tests/env_drift.py --merge-claim-file %O %A %B %L %P' )
+RL="$W/ledgerdrv"; throwaway_git_init "$RL" -q -b main
+( cd "$RL" || exit 2
+  git config merge.ledgermerge.name ledgers
+  git config merge.ledgermerge.driver 'python3 tools/merge/ledger_merge.py --merge %O %A %B %L %P'
+  mkdir -p tests tools/merge
+  cp "$(cd "$(dirname "$SELF")/../.." && pwd)/tools/merge/ledger_merge.py" tools/merge/ledger_merge.py
+  printf 'tests/structure_budgets.json merge=ledgermerge\n' > .gitattributes
+  printf '{\n  "a": 1,\n  "b": 1\n}\n' > tests/structure_budgets.json
+  git add -A; git commit -qm main0
+  git checkout -qb fix; sed -i.bak 's/"a": 1/"a": 2/' tests/structure_budgets.json; rm -f tests/*.bak
+  git commit -qam "fix: own"; git rev-parse HEAD > ../ledgerdrv.v
+  git checkout -q main; sed -i.bak 's/"b": 1/"b": 3/' tests/structure_budgets.json; rm -f tests/*.bak; git commit -qam "main: b"
+  git checkout -q --detach "$(cat ../ledgerdrv.v)"; git merge -q --no-ff --no-edit main >/dev/null 2>&1
+  git commit -q --allow-empty -m "fix: nothing"; git rev-parse HEAD > ../ledgerdrv.h
+  sed -i.bak 's/"b": 3/"b": 4/' tests/structure_budgets.json; rm -f tests/*.bak; git commit -qam "fix: tidy wording"
+  git rev-parse HEAD > ../ledgerdrv.x; git config --remove-section merge.ledgermerge ) || exit 2
+VL=$(cat "$W/ledgerdrv.v"); HL=$(cat "$W/ledgerdrv.h"); HLX=$(cat "$W/ledgerdrv.x")
+st "$( cd "$RL" && git show "$HL:tests/structure_budgets.json" | tr -d ' \n')" '{"a":2,"b":3}' \
+  "the fixture's ledger driver resolved the merge both sides changed"
+( cd "$RL" && bash "$SELF" --carry "$VL" "$HL" main ) > "$W/carry.out" 2>&1
+st $? 0 "CARRY: a ledger main's driver resolved, in a clone with no ledger driver configured"
+( cd "$RL" && bash "$SELF" --carry "$VL" "$HLX" main ) > "$W/carry.out" 2>&1
+st $? 1 "NO CARRY: the same ledger with one value then changed by a commit of the branch's own"
+st "$(grep -c "structure_budgets.json at $HLX is not" "$W/carry.out")" 1 "refused naming the ledger"
+# The delivery row (P123): delivery_row.sh commit_row's subject, author and
+# one path, for an add and an edit; each refusal names its commit.
+TV=70032254+tvofi@users.noreply.github.com
+rowc() { # base N author subject-N path... -> sha: the row commit's shape, varied by one field
+  local b=$1 n=$2 ae=$3 sn=$4; shift 4; g checkout -q --detach "$b"
+  for f in "$@"; do mkdir -p "$W/clone/$(dirname "$f")"; echo "row $n" >> "$W/clone/$f"; g add "$f"; done
+  GIT_AUTHOR_EMAIL=$ae GIT_COMMITTER_EMAIL=$ae g commit -qm "record: the delivery row for #$sn"; g rev-parse HEAD
+}
+H_ROWADD=$(rowc "$V" 7 "$TV" 7 dev/programme/delivery/7.md)
+carried "$H_ROWADD"; st $? 0 "CARRY: the verdict head plus its delivery-row add"
+carried "$V"; st $? 0 "CARRY: the verdict head itself, no commit after it (null control)"
+H_ROWEDIT=$(rowc "$H_ROWADD" 7 "$TV" 7 dev/programme/delivery/7.md)
+( cd "$W/clone" && bash "$SELF" --carry "$H_ROWADD" "$H_ROWEDIT" origin/main ) > "$W/carry.out" 2>&1
+st $? 0 "CARRY: a verdict head holding its row plus a row-edit commit"
+carried "$H_ROWEDIT"; st $? 0 "CARRY: the add and the edit in one range"
+H_ROWMORE=$(rowc "$V" 7 "$TV" 7 dev/programme/delivery/7.md b.txt)
+carried "$H_ROWMORE"; st $? 1 "NO CARRY: a row-subject commit that also touches one other file"
+st "$(grep -c "^CARRY: no $V -> $H_ROWMORE: $H_ROWMORE is a commit under" "$W/carry.out")" 1 "refused naming that commit"
+H_ROWSEAT=$(rowc "$V" 7 seat@users.noreply.github.com 7 dev/programme/delivery/7.md)
+carried "$H_ROWSEAT"; st $? 1 "NO CARRY: a row commit authored by anyone but tvofi"
+st "$(grep -c "$H_ROWSEAT is authored by seat@" "$W/carry.out")" 1 "refused naming that commit and its author"
+H_ROWX=$(rowc "$V" 8 "$TV" 7 dev/programme/delivery/8.md)
+carried "$H_ROWX"; st $? 1 "NO CARRY: a row commit for #7 writing another pull request's row"
+st "$(grep -c "$H_ROWX is a commit under" "$W/carry.out")" 1 "refused on the path its subject binds"
+H_TESTLINE=$(pin_commit "$H_ROWADD" "fix: one test line" tests/t_x.py)
+carried "$H_TESTLINE"; st $? 1 "NO CARRY: an ordinary commit changing one test line after the row"
+st "$(grep -c "own commits ${H_TESTLINE:0:9} change its content" "$W/carry.out")" 1 "refused naming that commit"
+H_BUDGET=$(pin_commit "$H_ROWADD" "fix: one budget value" tests/structure_budgets.json)
+carried "$H_BUDGET"; st $? 1 "NO CARRY: an ordinary commit changing one budget value after the row"
+st "$(grep -c "own commits ${H_BUDGET:0:9} change its content" "$W/carry.out")" 1 "refused naming that commit"
+# The driver files' end state (#3077 round 1): the comparisons above leave
+# main's merge-driver files out, so what they hold at the head is read on its
+# own -- git's automatic merge of the reviewed head onto main, main's driver
+# output on the two, or what a carried bot commit wrote -- whoever wrote the
+# commit: a branch's own, a `ci:` subject, or a merge's resolution.
+H_OWNLED=$(pin_commit "$H_ROWADD" "fix: tidy wording" led.json)
+carried "$H_OWNLED"; st $? 1 "NO CARRY: a commit of the branch's own that edits a merge-driver file (a budget raise)"
+st "$(grep -c "led.json at $H_OWNLED is not" "$W/carry.out")" 1 "refused naming the driver file"
+H_CITIDY=$(AUTHOR_EMAIL=seat@e pin_commit "$V" "ci: tidy" led.json)
+carried "$H_CITIDY"; st $? 1 "NO CARRY: a ci: subject by a seat that edits a merge-driver file"
+st "$(grep -c "led.json at $H_CITIDY is not" "$W/carry.out")" 1 "refused naming the driver file"
+H_MERGELED=$(g checkout -q --detach "$V"; g merge -q --no-ff --no-edit -m "Merge origin/main into fix" "$M1" >/dev/null
+  echo k >> "$W/clone/led.json"; g commit -q --amend -a --no-edit; g rev-parse HEAD)
+carried "$H_MERGELED"; st $? 1 "NO CARRY: a merge from main whose merge-driver file is resolved by hand"
+st "$(grep -c "led.json at $H_MERGELED is not" "$W/carry.out")" 1 "refused naming the driver file"
+H_AFTERBOT=$(pin_commit "$H_CILED" "fix: after the bot" tests/closures.json)
+carried "$H_AFTERBOT"; st $? 1 "NO CARRY: a commit of the branch's own that edits the driver file a carried bot commit wrote"
+st "$(grep -c "closures.json at $H_AFTERBOT is not" "$W/carry.out")" 1 "refused naming the driver file"
+g checkout -q --detach "$H_CILED"; g commit -q --allow-empty -m "fix: nothing after the bot"; H_BOTEMPTY=$(g rev-parse HEAD)
+carried "$H_BOTEMPTY"; st $? 0 "CARRY: an empty commit of the branch's own after a carried bot commit's driver-file write (null control)"
+g checkout -q --detach "$H_MERGE"; g commit -q --allow-empty -m "fix: nothing after the merge"; H_MERGEEMPTY=$(g rev-parse HEAD)
+carried "$H_MERGEEMPTY"; st $? 0 "CARRY: an empty commit of the branch's own after a merge from main (null control)"
+# L6: a revert and its re-apply around an absorb of main has the reviewed
+# change's patch at the new head; one that re-applies a different line does not.
+g checkout -q --detach "$V"; g revert --no-edit HEAD >/dev/null; _rv=$(g rev-parse HEAD)
+_rvm=$(mkmerge "$_rv" "$M1" "Merge origin/main into fix")
+g checkout -q --detach "$_rvm"; g revert --no-edit "$_rv" >/dev/null; H_REAPPLY=$(g rev-parse HEAD)
+carried "$H_REAPPLY"; st $? 0 "CARRY: a revert, an absorb of main and the re-apply (L6)"
+g checkout -q --detach "$_rvm"; ed1 's/^5$/FIVE/' a.txt; ed1 's/^l1$/L1/' led.json; g commit -qam "fix: re-apply, differently"; H_REAPPLYX=$(g rev-parse HEAD)
+carried "$H_REAPPLYX"; st $? 1 "NO CARRY: the same with a re-apply one byte away"
+# P17: a context-only difference main made carries in a *.md file, never in
+# code; the +/- lines and the context count still compare.
+( R="$W/mdctx"; throwaway_git_init "$R" -q -b main && cd "$R" || exit 2
+  seq -f 'p%g' 1 12 > doc.md; seq -f 'x = %g' 1 12 > f.py; seq -f 'q%g' 1 12 > top.md
+  git add -A; git commit -qm m0
+  git checkout -qb fix; sed -i.bak -e 's/^p6$/P6/' -e 's/^p9$/P9/' doc.md; sed -i.bak 's/^x = 6$/x = 66/' f.py
+  sed -i.bak 's/^q2$/Q2/' top.md; rm -f ./*.bak; git commit -qam "fix: own"; git rev-parse HEAD > ../md.v
+  side() { git checkout -q main; git checkout -q -B "m$1"; sed -i.bak "$2" "$3"; rm -f ./*.bak; git commit -qam "main $1"
+    git checkout -q --detach "$(cat ../md.v)"; git merge -q --no-ff --no-edit "m$1" >/dev/null; git rev-parse HEAD > "../md.$1"; }
+  side ctx 's/^p4$/p4 reworded/' doc.md
+  side py 's/^x = 4$/x = 44/' f.py
+  side plus 's/^p6$/P6/' doc.md
+  side count '1i\
+q0
+' top.md ) || exit 2
+mdcarry() { ( cd "$W/mdctx" && git branch -qf main "m$1" && bash "$SELF" --carry "$(cat ../md.v)" "$(cat "../md.$1")" main ) > "$W/carry.out" 2>&1; }
+mdcarry ctx; st $? 0 "CARRY: main rewrote a context line beside the branch's lines in a .md file (P17)"
+mdcarry py; st $? 1 "NO CARRY: the same context rewrite in a .py file (code stays strict)"
+st "$(grep -c "the branch's own diff differs" "$W/carry.out")" 1 "refused by the branch's own comparison"
+mdcarry plus; st $? 1 "NO CARRY: a .md file where main made one of the branch's + lines its own"
+mdcarry count; st $? 1 "NO CARRY: a .md hunk whose context count main changed"
 EVV="$W/ev-v"; mkdir -p "$EVV"; printf 'fix review at head %s\n' "$V" > "$EVV/verdict.md"
 CARRYV="[$(comment 2 "Fix review: merge $V" "$APPR" NONE "evidence: $EVV")]"
 setpr "$H_MERGE"; mkcase carry open false "$H_MERGE" "$CARRYV"
diff --git a/tools/pr/app_comment.sh b/tools/pr/app_comment.sh
index 7b2416f22..a1d742954 100755
--- a/tools/pr/app_comment.sh
+++ b/tools/pr/app_comment.sh
@@ -25,10 +25,15 @@
 #     exactly `Fix review: merge <40-hex>`, or `Fix review: blocked <40-hex>
 #     <class>: <why>`. This is a verdict poster, not a general App voice;
 #   - the pull request is open, and for a `merge` verdict its live head is
-#     exactly the verdict's SHA -- read before the mint and again just before
-#     the POST (`fix-review.md` step 12). A `blocked` verdict may name a head
-#     that moved (`head-moved: measured <sha>, head is <other>`), so it is
-#     not held to the live head.
+#     the verdict's SHA or a head the verdict carries to -- read before the
+#     mint and again just before the POST (`fix-review.md` step 12). A carry is
+#     `app_approve.sh --carry <verdict sha> <live head>` answering `CARRY: yes`
+#     against `origin`'s main and the pull request's head fetched into this
+#     checkout, the one carry rule `app_approve.sh` and `merge_train.py` read
+#     (P264); the posted body then gains one last line, `carry: <verdict sha>
+#     -> <live head>, app_approve.sh --carry: yes`, printed here too. A
+#     `blocked` verdict may name a head that moved (`head-moved: measured
+#     <sha>, head is <other>`), so it is not held to the live head.
 #
 # AFTER THE POST it refuses (exit non-zero) unless the created comment's user
 # is `hpo-approver[bot]` of type `Bot`, and unless `gh_comment.py verify`
@@ -57,16 +62,25 @@ else
 fi
 die() { printf 'app_comment: REFUSE: %s\n' "$*" >&2; exit 1; }
 
-check_pr() { # repo pr [sha] -> refuses unless open (and, given a sha, at exactly it)
-  local js info state head
+check_pr() { # repo pr [sha] -> refuses unless open (and, given a sha, at it or a head it carries to); sets CARRIED
+  local js info state head why
+  CARRIED=""
   js=$(gh api "repos/$1/pulls/$2") || die "could not read pull request #$2 on $1"
   info=$(printf '%s' "$js" | python3 -c 'import sys,json
 d=json.load(sys.stdin); print(d["state"], d["head"]["sha"])') \
     || die "pull request #$2's JSON has no state or head"
   read -r state head <<<"$info"
   [ "$state" = "open" ] || die "pull request #$2 is $state; a verdict posts only on an open one"
-  [ -z "${3:-}" ] || [ "$head" = "$3" ] \
-    || die "head moved: the merge verdict names $3, the live head of #$2 is $head"
+  [ -z "${3:-}" ] || [ "$head" = "$3" ] && return 0
+  [[ $head =~ ^[0-9a-f]{40}$ ]] || die "head moved: the merge verdict names $3, and the live head of #$2 reads as '$head'"
+  git fetch -q --no-tags origin "+refs/heads/main:refs/hpo-comment-carry/main" "+refs/pull/$2/head:refs/hpo-comment-carry/head" 2>/dev/null \
+    || die "head moved: the merge verdict names $3, the live head of #$2 is $head, and fetching main and the head to test a carry failed"
+  [ "$(git rev-parse refs/hpo-comment-carry/head)" = "$head" ] \
+    || die "head moved: the merge verdict names $3, the live head of #$2 is $head, and the fetched head is not it"
+  why=$(bash "$_root/tools/pr/app_approve.sh" --carry "$3" "$head" refs/hpo-comment-carry/main 2>&1) \
+    && [[ $why == "CARRY: yes "* ]] \
+    || die "head moved: the merge verdict names $3, the live head of #$2 is $head, and it does not carry: ${why#CARRY: no }"
+  CARRIED=$head
 }
 
 cleanup() {
@@ -131,6 +145,13 @@ open(sys.argv[1], "w").write("Authorization: Bearer %s\n" % t)' "$PRIV/token.h"
   chmod 600 "$PRIV/token.h"
 
   check_pr "$repo" "$pr" "$want"
+  if [ -n "$CARRIED" ]; then
+    { cat -- "$body"; [ -z "$(tail -c 1 -- "$body")" ] || echo
+      printf 'carry: %s -> %s, app_approve.sh --carry: yes\n' "$sha" "$CARRIED"; } > "$PRIV/body.md" \
+      || die "could not write the carried body"
+    body=$PRIV/body.md
+    printf 'app_comment: CARRY %s -> %s: carry: %s -> %s, app_approve.sh --carry: yes\n' "$sha" "$CARRIED" "$sha" "$CARRIED"
+  fi
   python3 -c 'import sys,json
 json.dump({"body": open(sys.argv[1], encoding="utf-8").read()}, open(sys.argv[2], "w"))' "$body" "$PRIV/comment.json" \
     || die "could not write the comment payload"
@@ -212,6 +233,17 @@ case "$url" in
 esac
 STUB
 chmod +x "$W/bin/gh" "$W/bin/openssl" "$W/bin/curl"
+# Every run is from a throwaway repository whose `origin` is a local bare one,
+# so a moved head's carry test (P264: app_approve.sh --carry, real) fetches
+# and reads git for real and no case reaches the network.
+. "$(dirname -- "$SELF")/../../tests/throwaway_git.sh" && throwaway_git_env
+R="$W/repo"; throwaway_git_init "$W/origin.git" -q --bare && throwaway_git_init "$R" -q -b main
+gr() { git -C "$R" "$@"; }
+gr remote add origin "$W/origin.git"; seq 1 9 > "$R/a.txt"; gr add a.txt; gr commit -qm m0; gr push -q origin main
+gr checkout -qb fix; sed -i.bak 's/^5$/five/' "$R/a.txt"; rm "$R/a.txt.bak"; gr commit -qam "fix: own"; CV=$(gr rev-parse HEAD)
+mkdir -p "$R/tests/mutation_ledger/killed_by"; echo '{}' > "$R/tests/mutation_ledger/killed_by/a.json"; gr add -A
+GIT_AUTHOR_EMAIL="41898282+github-actions[bot]@users.noreply.github.com" gr commit -qm "ci: pin killed mutants"; CPIN=$(gr rev-parse HEAD)
+gr checkout -q --detach "$CV"; echo 10 >> "$R/a.txt"; gr commit -qam "fix: one more code line"; CCODE=$(gr rev-parse HEAD)
 
 MERGE="Fix review: merge $SHA"
 BLOCKED="Fix review: blocked $SHA head-moved: measured $SHA, head is $OTHER"
@@ -223,6 +255,7 @@ mkcase() { # name head first-line
 run() { # name args... ; the last arg defaults to the case's own verdict file
   local d="$W/$1"; shift
   ( export STUB="$d" PATH="$W/bin:$PATH" TMPDIR="$d/tmp" HPO_IDENTITY_DIR="${IDDIR:-$W/id}"
+    cd "$R" || exit 2
     if [ "${BASHX:-}" = 1 ]; then bash -x "$SELF" "$@"; else bash "$SELF" "$@"; fi > "$d/out" 2> "$d/err" )
 }
 calls() { grep -c "^$2" "$W/$1/log"; }
@@ -300,5 +333,20 @@ st "$(calls dry openssl)" 0 "and signs nothing"
 mkcase drymoved "$OTHER" "$MERGE"
 run drymoved --dry-run o/r 7 "$W/drymoved/seat/verdict.md"; st $? 1 "--dry-run still refuses what a real run would"
 
+crun() { # name live-head -> app_comment run from the repository, the PR's head ref at live-head
+  gr push -q -f origin "$2:refs/pull/7/head"; mkcase "$1" "$2" "Fix review: merge $CV"
+  run "$1" o/r 7 "$W/$1/seat/verdict.md"; }
+# A pin-only head the verdict carries to (P264).
+crun pin "$CPIN"; st $? 0 "a merge verdict posts at a pin-only head it carries to (P264)"
+st "$(tail -n 1 "$W/pin/posted.body")" "carry: $CV -> $CPIN, app_approve.sh --carry: yes" "with the carry as the body's last line"
+st "$(head -n 3 "$W/pin/posted.body" | cmp -s - "$W/pin/seat/verdict.md" && echo same)" same "under the verdict file, byte for byte"
+st "$(grep -c "^app_comment: CARRY $CV -> $CPIN: carry: $CV -> $CPIN, app_approve.sh --carry: yes$" "$W/pin/out")" 1 "printing the carry line"
+st "$(grep -c '^READBACK id=55 .* identical=True' "$W/pin/out")" 1 "and the carried body reads back identical"
+crun code "$CCODE"; st $? 1 "REFUSE: a merge verdict at a head moved by a commit of the branch's own changing code"
+st "$(grep -c "head moved: .*does not carry: .*${CCODE:0:9} change its content" "$W/code/err")" 1 "refused 'head moved', with the carry's reason"
+st "$(calls code curl)" 0 "and nothing was minted or posted"
+st "$(grep -c '^carry:' "$W/ok/posted.body")" 0 "an unmoved head posts with no carry line (null control)"
+st "$(grep -c 'CARRY' "$W/ok/out")" 0 "and prints none"
+
 echo "app_comment self-test: $N checks, $FAILS failed"
 [ "$FAILS" -eq 0 ]
diff --git a/tools/pr/app_push.sh b/tools/pr/app_push.sh
index 9b336b114..dd33bad78 100644
--- a/tools/pr/app_push.sh
+++ b/tools/pr/app_push.sh
@@ -112,8 +112,9 @@
 # every one of these holds, each read here and failing closed:
 #   (a) HEAD has exactly one parent, the pull request's live head from the
 #       open-pull-request listing;
-#   (b) `git diff --name-status <live> HEAD` is exactly one added file,
-#       delivery_row.sh's `$ROW_DIR/<N>.md` for the listing's number <N>;
+#   (b) `git diff --name-status <live> HEAD` is exactly one added or modified
+#       file, delivery_row.sh's `$ROW_DIR/<N>.md` for the listing's number <N>
+#       (commit_row writes an add and an edit alike, P123);
 #   (c) that file is one line, an open row anchored on <N>, as
 #       tests/delivery_status.py's `anchored` reads a row;
 #   (d) the body file is the live body under one new `## Head` note, the
@@ -214,7 +215,7 @@ d = json.load(sys.stdin)[0]; print(d["head"]["sha"], int(d["number"]), " ".join(
   row=$ROW_DIR/$num.md
   d=$(git -C "$wt" diff --no-renames --name-status "$live" "$RV_HEAD" 2>/dev/null) \
     || { _rv_no "the diff against the live head could not be read"; return 1; }
-  [ "$d" = "$(printf 'A\t%s' "$row")" ] \
+  [ "$d" = "$(printf 'A\t%s' "$row")" ] || [ "$d" = "$(printf 'M\t%s' "$row")" ] \
     || { _rv_no "the head adds or changes more than this pull request's own row $row (git diff --name-status: $(printf '%s' "$d" | tr '\t' ' ' | paste -sd';' - | sed 's/;/; /g'))"; return 1; }
   git -C "$wt" show "$RV_HEAD:$row" 2>/dev/null | python3 -I -c 'import sys
 sys.path.insert(0, sys.argv[2] + "/tests")
@@ -231,7 +232,7 @@ i = head_offset(b)
 j = b.find("\n\n", i) if i >= 0 else -1
 sys.exit(not (j > i and prefix(live, b[i:j]).rstrip("\n") == b.rstrip("\n")))' "$body" "$(dirname -- "$0")" 2>/dev/null \
     || { _rv_no "the body file is not the live pull-request body under one new \`## Head\` note"; return 1; }
-  _rv_no "HEAD ${RV_HEAD:0:8} is the live head ${live:0:8} plus one commit adding only $row, one open row for #$num, and the body is the live one under one new \`## Head\` note"
+  _rv_no "HEAD ${RV_HEAD:0:8} is the live head ${live:0:8} plus one commit adding or editing only $row, one open row for #$num, and the body is the live one under one new \`## Head\` note"
 }
 
 # What --row-only runs in prepr's place: two of the body checks pr-contract runs,
@@ -1052,7 +1053,7 @@ print(json.dumps([{"number": 7, "title": "the title", "head": {"sha": sys.argv[1
 }
 rocase ook
 run ook --row-only o/r "$W/tool-wt" "$BR" "$W/ook/body.md"; st $? 0 "--row-only: the live head plus one commit adding only its own open row, the live body under one new note: pushed (prepr-fails set)"
-st "$(calls ook prepr)$(grep -c '^app_push: ROW-ONLY: prepr SKIPPED: HEAD 11111111 is the live head 55555555 plus one commit adding only dev/programme/delivery/7.md' "$W/ook/out")" 01 "and prepr was skipped, naming the path and why in one line"
+st "$(calls ook prepr)$(grep -c '^app_push: ROW-ONLY: prepr SKIPPED: HEAD 11111111 is the live head 55555555 plus one commit adding or editing only dev/programme/delivery/7.md' "$W/ook/out")" 01 "and prepr was skipped, naming the path and why in one line"
 st "$(grep -c "^node tools/policy/policy_lint.mjs --pr-body $W/ook/body.md --head $SHA --title the title --paths-file .* --existing-file " "$W/ook/log")" 1 "the body contract ran in its place, pr-contract's command at the head, with the pull request's own title"
 st "$(grep -c "^carry_audit check --body $W/ook/body.md$" "$W/ook/log")" 1 "and the carry check pr-contract runs (carry_audit.py check), on the same body"
 st "$(grep -c '^curl PATCH repos/o/r/pulls/7$' "$W/ook/log")$(cmp -s "$W/ook/live-body" "$W/ook/body.md" && echo same)" 1same "the open pull request is re-bodied with the body file unchanged: --row-only writes no note of its own"
@@ -1064,7 +1065,10 @@ rorefused() { # name want-reason -- prepr runs once, as without the flag, and pa
 rocase omore; printf 'A\tdev/programme/delivery/7.md\nM\ttools/x.py\n' > "$W/omore/namestatus"
 rorefused omore "the head adds or changes more than"
 rocase oother; printf 'A\tdev/programme/delivery/8.md\n' > "$W/oother/namestatus"; rorefused oother "the head adds or changes more than"
-rocase oedit; printf 'M\tdev/programme/delivery/7.md\n' > "$W/oedit/namestatus"; rorefused oedit "the head adds or changes more than"
+rocase oedit; printf 'M\tdev/programme/delivery/7.md\n' > "$W/oedit/namestatus"
+run oedit --row-only o/r "$W/tool-wt" "$BR" "$W/oedit/body.md"; st $? 0 "--row-only: one commit editing only its own row is pushed with prepr skipped (P123)"
+st "$(calls oedit prepr)" 0 "... prepr skipped for the edit"
+rocase oeditmore; printf 'M\tdev/programme/delivery/7.md\nA\ty\n' > "$W/oeditmore/namestatus"; rorefused oeditmore "the head adds or changes more than"
 rocase otwo; printf '%s\n%s\n' "$P1_STUB" "$P2_STUB" > "$W/otwo/parents"; rorefused otwo "HEAD has 2 parent(s), not one commit on the live head"
 rocase olive "$W/body.md"; printf '%s\n' "$OTHER" > "$W/olive/parents"; rorefused olive "parent 1 22222222 is not the live pull-request head 55555555"
 rocase orow; printf -- '- [#8](https://github.com/o/r/pull/8) — **open**, t\n' > "$W/orow/row"; rorefused orow "dev/programme/delivery/7.md is not one open row anchored on #7"
@@ -1117,7 +1121,9 @@ st "$(qv live)" "the head adds or changes more than this pull request's own row
 reset_q; (cd "$Q/wt" && ensure_row . 8 "$(row_line 8 o/r t)" >/dev/null)
 st "$(qv live)" "the head adds or changes more than this pull request's own row dev/programme/delivery/7.md (git diff --name-status: A dev/programme/delivery/8.md)" "real git: another pull request's row runs prepr"
 reset_q; (cd "$Q/wt" && ensure_row . 7 "$(row_line 7 o/r t)" >/dev/null && rgit tag -f live2 && row_line 7 o/r u > dev/programme/delivery/7.md && rgit commit -qam edit)
-st "$(qv live2)" "the head adds or changes more than this pull request's own row dev/programme/delivery/7.md (git diff --name-status: M dev/programme/delivery/7.md)" "real git: a rewrite of a row the live head carries runs prepr"
+st "$(qv live2 >/dev/null; echo $?)" 0 "real git: commit_row's edit of a row the live head carries skips prepr (P123)"
+(cd "$Q/wt" && printf 'y\n' > y && rgit add y && rgit commit -q --amend --no-edit)
+st "$(qv live2)" "the head adds or changes more than this pull request's own row dev/programme/delivery/7.md (git diff --name-status: M dev/programme/delivery/7.md; A y)" "real git: the same edit with one more file runs prepr"
 reset_q; (cd "$Q/wt" && rgit merge -q --no-edit main && ensure_row . 7 "$(row_line 7 o/r t)" >/dev/null)
 st "$(qv live >/dev/null; echo $?)" 0 "real git: an up-to-date main merge (no commit) then the row skips prepr"
 reset_q; (cd "$Q/wt" && rgit commit -q --allow-empty -m empty && ensure_row . 7 "$(row_line 7 o/r t)" >/dev/null)

