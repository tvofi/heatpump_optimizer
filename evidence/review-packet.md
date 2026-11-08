# Review packet #3324
head: 7a85168ef3ce5112c145e3441567d5bf28c632d0
base: 4fe7d5934b0a4bc092c9398f29b579fbd2df8b50

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=128724630262 success
arch-score / arch-score id=128755340921 success
arm id=128724443247 skipped
budget-raise-gate / budget-raise-gate id=128755372702 success
cancel-superseded id=128755340062 success
codeql id=128755378697 skipped
codeql / Analyze (actions) id=128724587149 success
codeql / Analyze (javascript-typescript) id=128724587210 success
codeql / Analyze (python) id=128724587242 success
gate id=128755340122 success
governance id=128755363192 skipped
governance / delivery-status id=128724587282 success
governance / delivery-status-publish id=128724588738 skipped
governance / env-matrix id=128724587263 success
governance / instrument-self-tests id=128724587089 success
governance / policy-docs id=128724587119 success
governance / record id=128724588753 skipped
governance / wave-script id=128724587126 success
hassfest id=128755340496 skipped
hassfest / hassfest id=128724587253 success
kernel-points id=128755366365 skipped
pr-contract id=128755340744 skipped
pr-contract / pr-contract id=128730374977 success
prelude id=128755377869 success
refresh id=128755372978 success
tests id=128755341122 skipped
tests / arch-instrument id=128724723850 success
tests / briefs id=128724587160 success
tests / browser id=128724723803 success
tests / ci-ratchet id=128729627076 skipped
tests / claims-autofix id=128728088434 skipped
tests / closure-scope id=128724587105 success
tests / closures id=128724723750 success
tests / closures-autofix id=128727916041 skipped
tests / coverage id=128724723754 success
tests / coverage-ratchet id=128729625682 success
tests / fast (3.14) id=128724723757 success
tests / graders-head-copy id=128729625733 success
tests / lane-proofs id=128729625631 success
tests / mutation id=128724587146 success
tests / mutation-autofix id=128724785477 skipped
tests / mutation-pins id=128724784609 skipped
tests / nightly-ha id=128724725096 skipped
tests / nightly-status id=128724587202 success
tests / replay id=128724725186 skipped
tests / typing id=128724723922 success
validate id=128755340825 skipped
validate / validate-hacs id=128724587200 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash tools/audit/worktree_gc.sh --self-test
             `tools/audit/worktree_gc.sh` is in the tree at this head
  ok         python3 tools/audit/seat/closeout.py --self-test
             `tools/audit/seat/closeout.py` is in the tree at this head
  ok         python3 tools/audit/seat/prune_refs.py --self-test
             `tools/audit/seat/prune_refs.py` is in the tree at this head
  ok         python3 tools/audit/seat/roster_lib.py --self-test
             `tools/audit/seat/roster_lib.py` is in the tree at this head
  ok         python3 tools/plan/replan.py --self-test
             `tools/plan/replan.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head

FIGURES: 6 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3324.md b/dev/programme/delivery/3324.md
new file mode 100644
index 000000000..332bf8b0c
--- /dev/null
+++ b/dev/programme/delivery/3324.md
@@ -0,0 +1 @@
+- [#3324](https://github.com/tvofi/heatpump_optimizer/pull/3324) — **open**, R10-CLOSEOUT-INSTRUMENTS: closeout instruments (R10-CLOSEOUT-INSTRUMENTS)
diff --git a/tools/audit/seat/closeout.py b/tools/audit/seat/closeout.py
index d349f9068..1a8e720e5 100644
--- a/tools/audit/seat/closeout.py
+++ b/tools/audit/seat/closeout.py
@@ -100,8 +100,12 @@ STEPS = ("in-main", "refs", "local", "issues", "report")   # the order is the ga
 
 
 def roster_blockers(roster: dict, self_group: str = SELF_GROUP) -> list:
-    """Every group other than `self_group` whose stage is not done, sorted."""
-    return sorted(g for g in roster_lib.open_groups(roster) if g != self_group)
+    """Every group other than `self_group` whose stage is not done, sorted, less
+    the groups the roster exempts (`roster_lib.closeout_exempt`): the post-stamp
+    owner step, which starts only after this run's stamp, and a ruled group."""
+    exempt = roster_lib.closeout_exempt(roster)[0]
+    return sorted(g for g in roster_lib.open_groups(roster)
+                  if g != self_group and g not in exempt)
 
 
 class Ctx:
@@ -348,7 +352,9 @@ def step_issues(c: Ctx) -> list:
     issues = c.open_issues()
     if issues is None:
         return ["the open issues cannot be read; nothing is dispositioned unseen"]
-    rest = sorted(i["number"] for i in issues if i["number"] != c.successor)
+    exempt = roster_lib.closeout_exempt(c.roster)[1]
+    rest = sorted(i["number"] for i in issues
+                  if i["number"] != c.successor and i["number"] not in exempt)
     if rest:
         return [f"{len(rest)} open issue(s) beyond the successor "
                 f"{'#' + str(c.successor) if c.successor else '(none named)'} "
@@ -571,6 +577,36 @@ def self_test() -> int:
         check("roster_blockers names every other open group and skips this one",
               roster_blockers(roster({"X": "not-started", "Y": "done", SELF_GROUP: "not-started"}))
               == ["X"])
+        # the exemption (roster_lib.closeout_exempt): a post-stamp owner step, its wired
+        # issue, and a ruled group never block; an ordinary not-started group still does
+        def gr(name, stage, **kw):
+            return dict({"group": name, "resume": {"stage": stage}}, **kw)
+
+        cat = gr("CAT", "not-started", kind="owner-step", issues=[2965], after=[SELF_GROUP])
+        cat["resume"]["next_step"] = "after the v10.0.0 closeout stamp: open the catalog PR"
+        post_only = {"groups": [gr("A", "done"), gr(SELF_GROUP, "not-started"), cat]}
+        check("a fixture roster with only the post-stamp owner step open proceeds",
+              roster_blockers(post_only) == [])
+        check("a refused group (no open host) is not a blocker",
+              roster_blockers({"groups": [gr("R", "refused"), gr(SELF_GROUP, "not-started")]}) == [])
+        hosted = gr("R", "refuted")
+        hosted["resume"]["host"] = "H"
+        check("a ruled group whose host is still open blocks",
+              roster_blockers({"groups": [hosted, gr("H", "in-progress"),
+                                          gr(SELF_GROUP, "not-started")]}) == ["H", "R"])
+        check("null control: an ordinary not-started group still refuses beside the exempt ones",
+              roster_blockers({"groups": [cat, gr("N", "not-started"), gr("R", "refused"),
+                                          gr(SELF_GROUP, "not-started")]}) == ["N"])
+        check("a group after the post-stamp step is post-stamp too",
+              roster_blockers({"groups": [cat, gr("T", "queued", after=["CAT"]),
+                                          gr(SELF_GROUP, "not-started")]}) == [])
+        wired = mk(all_done, issues=[{"number": 7, "title": "s"}, {"number": 2965, "title": "c"}])
+        wired.roster = post_only
+        check("step 4 does not wait for an issue wired to a post-stamp group",
+              step_issues(wired) == [])
+        wired.issues = [{"number": 7, "title": "s"}, {"number": 9, "title": "x"}]
+        check("null control: step 4 still waits for an unwired issue",
+              step_issues(wired) != [])
         # null control: every other group done -> it proceeds into the steps
         lines = []
         c = mk(all_done, lint_rc=1)
diff --git a/tools/audit/seat/instruments/closeout.py.md b/tools/audit/seat/instruments/closeout.py.md
index 2cb2c708f..f19726ebe 100644
--- a/tools/audit/seat/instruments/closeout.py.md
+++ b/tools/audit/seat/instruments/closeout.py.md
@@ -15,3 +15,7 @@
   none); (5) the report with counts before and after under `--report-dir`.
   Archiving merged cloud sessions stays the orchestrator's. `--self-test` runs
   every control against a throwaway bare remote.
+  `--apply`'s roster refusal and step 4 exempt what `roster_lib.closeout_exempt`
+  returns: open post-stamp groups (the owner step that starts after this run's
+  stamp, and groups after it), the issues wired to them, and `refused`/`refuted`
+  groups whose `resume.host` is not an open group.
diff --git a/tools/audit/seat/instruments/prune_refs.py.md b/tools/audit/seat/instruments/prune_refs.py.md
index 77b8525aa..4116ab73c 100644
--- a/tools/audit/seat/instruments/prune_refs.py.md
+++ b/tools/audit/seat/instruments/prune_refs.py.md
@@ -26,3 +26,6 @@
   the plan to one topic's refs (`handoff/T`, `handoff-body/T`, `-rN`,
   `dispatch/*T*`) and refuses it whole when a `handoff/` tip has a `+` line in
   `git cherry` against main or any of its refs has an open pull request.
+  A tag the remote holds at another sha (a lease refusal moved the ref after
+  its tag went up) is not retargeted: the new tip is archived as
+  `archive/<name>.<sha12>` and the delete check accepts either spelling.
diff --git a/tools/audit/seat/instruments/worktree_gc.sh.md b/tools/audit/seat/instruments/worktree_gc.sh.md
index 74953127a..1b9fc2484 100644
--- a/tools/audit/seat/instruments/worktree_gc.sh.md
+++ b/tools/audit/seat/instruments/worktree_gc.sh.md
@@ -13,3 +13,10 @@
   the listing read (`update-ref --no-deref -d HEAD <head>`): one whose HEAD
   moved since is kept and the refusal reported. An orphaned seat's removal
   is leased the same way, at the HEAD read in its unregistered `wt/`.
+  Every removal arm, not only `on-remote`, keeps a worktree a process stands
+  in (`cwd-inside`, `cwd-unread`). A seat branch (`work/`, `scratch/`, `seat/`)
+  is judged by the pull request on `fix/<topic>`: merged or closed frees it
+  when clean and pushed. Class E removes `*mutant*`, `*null*` and `*head*`
+  copies without `.git` in a seat directory whose `fix/<topic>` PR merged.
+  `WORKTREE_GC_SEATS_ROOT` is a colon-separated list (seats live under
+  `~/hpo-seats/<round>`).
diff --git a/tools/audit/seat/prune_refs.py b/tools/audit/seat/prune_refs.py
index 339a91eb6..a72d61158 100644
--- a/tools/audit/seat/prune_refs.py
+++ b/tools/audit/seat/prune_refs.py
@@ -452,6 +452,12 @@ def remote_tags(remote: str, git=subprocess.run) -> dict:
     return out
 
 
+def sha_tag(tag: str, sha: str) -> str:
+    """The per-sha spelling of an archive tag: the same name with the tip's first
+    12 hex digits, for a ref whose plain name already tags a different tip."""
+    return f"{tag}.{sha[:12]}"
+
+
 def apply_plan_push(remote: str, actions: list, dry_run: bool,
                     untagged: frozenset = frozenset(), chunk: int = PUSH_CHUNK,
                     git=subprocess.run) -> list:
@@ -467,7 +473,10 @@ def apply_plan_push(remote: str, actions: list, dry_run: bool,
     chunk is `--atomic`: a ref that moved after the plan read it is not
     deleted, its whole chunk is refused (`delete-FAILED`) and the rest
     aborts, so no ref is ever deleted at a tip other than the one archived.
-    Zero GitHub API calls.
+    A tag name the remote already holds at ANOTHER sha (a lease refusal moved
+    the ref after its tag went up, or the name was reused) is not retargeted and
+    not refused: the new tip is archived under `sha_tag`, the old tag stays, and
+    the delete check accepts either spelling. Zero GitHub API calls.
     """
     tags = [(a, s) for v, a, s in actions if v == "tag"]
     deletes = [(a, s) for v, a, s in actions if v == "delete"]
@@ -482,6 +491,9 @@ def apply_plan_push(remote: str, actions: list, dry_run: bool,
         r = git(["git", "push", "-q", remote, *args], capture_output=True, text=True)
         return None if r.returncode == 0 else (r.stderr.strip()[:160] or "push refused")
 
+    if tags:
+        held = remote_tags(remote, git)
+        tags = [(sha_tag(a, s) if held.get(a, s) != s else a, s) for a, s in tags]
     for part in _chunks(tags, chunk):
         err = push([f"{s}:refs/tags/{a}" for a, s in part])
         if err:
@@ -490,7 +502,8 @@ def apply_plan_push(remote: str, actions: list, dry_run: bool,
         done += [("tag", f"{a}@{s}") for a, s in part]
     have = remote_tags(remote, git) if tags or deletes else {}
     missing = [n for n, s in deletes
-               if n not in untagged and have.get(archive_tag(n)) != s]
+               if n not in untagged
+               and s not in (have.get(archive_tag(n)), have.get(sha_tag(archive_tag(n), s)))]
     if missing:
         raise ApplyRefused(f"{len(missing)} ref(s) to delete lack their archive tag at "
                            f"the same sha on the remote, first {missing[0]}; nothing deleted")
@@ -749,15 +762,31 @@ def _self_test_git(results: list) -> None:
                apply_plan_push("origin", only_delete, False, frozenset({victim}),
                                git=runner) == [("delete", victim)]
                and victim not in heads(), results)
-        # a tag already on the remote at a DIFFERENT sha: the tag push is refused, abort
-        g("push", "-q", "origin", f"{plus_tip}:refs/tags/archive/fix/n1")
+        # the first refused tag push aborts the rest: no later chunk, no delete
         refs = heads()
         acts = [("tag", "archive/fix/n1", refs["fix/n1"]), ("tag", "archive/fix/n2", refs["fix/n2"]),
                 ("delete", "fix/n1", refs["fix/n1"]), ("delete", "fix/n2", refs["fix/n2"])]
-        out = apply_plan_push("origin", acts, False, chunk=1, git=runner)
+
+        def refusing(argv, **kw):
+            if "push" in argv and any("refs/tags/" in a for a in argv):
+                return subprocess.CompletedProcess(argv, 1, "", "refused")
+            return runner(argv, **kw)
+        out = apply_plan_push("origin", acts, False, chunk=1, git=refusing)
         _check("the first refused tag push aborts: no later chunk, no delete",
                out[-1][0] == "tag-FAILED" and len(out) == 1
                and "fix/n1" in heads() and "fix/n2" in heads(), results)
+        # a tag already on the remote at a DIFFERENT sha is not retargeted and not refused:
+        # the new tip is archived under its per-sha name, the old tag stays
+        g("push", "-q", "origin", f"{plus_tip}:refs/tags/archive/fix/n1")
+        out = apply_plan_push("origin", acts, False, chunk=1, git=runner)
+        have = remote_tags(origin)
+        _check("a tag held at another sha: the tip is archived under its per-sha name, then deleted",
+               ("tag", f"{sha_tag('archive/fix/n1', refs['fix/n1'])}@{refs['fix/n1']}") in out
+               and have.get(sha_tag("archive/fix/n1", refs["fix/n1"])) == refs["fix/n1"]
+               and "fix/n1" not in heads() and "fix/n2" not in heads(), results)
+        _check("...and the old tag is left at the old sha; the other tag keeps its plain name",
+               have.get("archive/fix/n1") == plus_tip
+               and have.get("archive/fix/n2") == refs["fix/n2"], results)
         _check("main is never deletable by the push arm",
                _refused(lambda: apply_plan_push("origin", [("delete", "main", base)], False,
                                                 git=runner), "never delete main", ApplyRefused),
@@ -779,6 +808,14 @@ def _self_test_git(results: list) -> None:
         _check("the moved ref's chunk is refused whole (atomic): its unmoved partner stays too",
                heads().get("fix/n4") == refs["fix/n4"]
                and not any(v == "delete" for v, _d in out), results)
+        # the re-plan at the moved tip: its plain tag name is held at the old sha
+        re_plan = [("tag", "archive/fix/n3", moved_tip), ("delete", "fix/n3", moved_tip)]
+        out = apply_plan_push("origin", re_plan, False, git=runner)
+        _check("a re-plan after a lease refusal archives the moved tip under a per-sha tag and deletes",
+               out == [("tag", f"{sha_tag('archive/fix/n3', moved_tip)}@{moved_tip}"), ("delete", "fix/n3")]
+               and "fix/n3" not in heads()
+               and remote_tags(origin).get("archive/fix/n3") == refs["fix/n3"]
+               and remote_tags(origin).get(sha_tag("archive/fix/n3", moved_tip)) == moved_tip, results)
         _check("null: the unmoved ref, planned alone at its live tip, archives and deletes",
                apply_plan_push("origin", lease[1:2] + lease[3:], False, git=runner)
                == [("tag", f"archive/fix/n4@{refs['fix/n4']}"), ("delete", "fix/n4")]
diff --git a/tools/audit/seat/roster_lib.py b/tools/audit/seat/roster_lib.py
index 4345df9a2..a510744c4 100644
--- a/tools/audit/seat/roster_lib.py
+++ b/tools/audit/seat/roster_lib.py
@@ -352,6 +352,46 @@ def open_groups(roster: dict) -> dict:
     return {k: g for k, g in groups_of(roster).items() if is_open(g)}
 
 
+#: The group that cuts the round's closing stamp; a group after it is post-closure.
+CLOSE_STAMP_MARK = "STAMP-ROUND-MAJOR"
+POST_CLOSE_STEP_RE = re.compile(r"after the .*\b(stamp|closeout)\b", re.I)
+#: A disposition that ends a group's claim on the round: a ruling closed it.
+#: `deferred` and `carries-open` still owe work and are not in it.
+RULED_STAGES = ("refused", "refuted")
+
+
+def post_closure_groups(G: dict, open_: set) -> set:
+    """Open groups that run after the round's closing stamp: an owner-step
+    whose next step is "after the ... stamp", a group whose `after` names the
+    closing-stamp group, and every group after one of those. The one owner of
+    the rule: the planner and the closeout instrument both read it."""
+    post = {n for n in open_
+            if (G[n].get("kind") == "owner-step"
+                and POST_CLOSE_STEP_RE.search(str((G[n].get("resume") or {}).get("next_step") or "")))
+            or any(CLOSE_STAMP_MARK in a for a in G[n].get("after") or [])}
+    grew = True
+    while grew:
+        grew = False
+        for n in open_ - post:
+            if any(a in post for a in G[n].get("after") or []):
+                post.add(n)
+                grew = True
+    return post
+
+
+def closeout_exempt(roster: dict) -> tuple:
+    """(groups, issues) the round's closeout run does not wait for: the open
+    post-closure groups and the issues wired to them, and every group whose
+    stage is a ruled disposition (`RULED_STAGES`) unless its `resume.host`
+    names a group still open. The roster keeps a ruled group open by design."""
+    G, open_ = groups_of(roster), set(open_groups(roster))
+    post = post_closure_groups(G, open_)
+    ruled = {n for n in open_
+             if (G[n].get("resume") or {}).get("stage") in RULED_STAGES
+             and (G[n]["resume"].get("host") not in open_)}
+    return post | ruled, {i for n in post for i in G[n].get("issues") or []}
+
+
 def run_refusing(tool: str, main, argv=None) -> int:
     """`main(argv)`, a missing roster printed as the one `<tool>: REFUSED ...`
     line and exit 2, never a traceback: the shared refusal of every reader
diff --git a/tools/audit/worktree_gc.sh b/tools/audit/worktree_gc.sh
index 02eded44a..97b72b88d 100755
--- a/tools/audit/worktree_gc.sh
+++ b/tools/audit/worktree_gc.sh
@@ -26,6 +26,11 @@
 #      branch, leased at the head the porcelain read (`git update-ref -d
 #      refs/heads/<branch> <head>`: a branch that moved since is kept and the
 #      refusal reported), then the seat scratch directory.
+#      A SEAT BRANCH (`work/<t>`, `scratch/<t>`, `seat/<t>`) has no pull request
+#      of its own: its PR sits on `fix/<t>`. A MERGED or CLOSED one there frees
+#      the seat, but only clean (uncommitted work is on no remote) and, as for
+#      every arm, with no unpushed commit and no process cwd inside it.
+#      Every removal arm keeps a worktree a process stands in (`cwd-inside`).
 #   B. a DETACHED worktree (reviewers check out merged pull request heads)
 #      whose HEAD sha is a PROPER ancestor of origin/main -- the tip itself is
 #      excluded, because reading live main is a running seat, not a leftover --
@@ -43,6 +48,11 @@
 #      A wt/ git can read is removed leased at the HEAD read in it (`git -C
 #      <wt> update-ref --no-deref -d HEAD <head>`, then rm -rf): a HEAD that
 #      moved since, or one that cannot be read, keeps the seat.
+#   E. a PLAIN COPY of the repository (a `*mutant*`, `*null*` or `*head*`
+#      directory without .git) directly inside a seat directory whose topic --
+#      the directory name less a leading `seat-` -- has a MERGED pull request
+#      on `fix/<topic>`, with nothing under the seat modified within the orphan
+#      age, no live worktree beneath the seat and no process cwd in the copy.
 #   D. a stale venv (a *-venv* directory under /tmp) untouched for 24 hours
 #      that no registered worktree symlinks into at depth <= 2.
 #
@@ -76,7 +86,8 @@
 # environment error (no checkout, unreadable worktree list).
 #
 # Environment, for the self-test and for seats on another machine:
-#   WORKTREE_GC_SEATS_ROOT (default /tmp/hpo-orch), WORKTREE_GC_TMP_ROOT
+#   WORKTREE_GC_SEATS_ROOT (default /tmp/hpo-orch; a colon-separated list --
+#   seats live under ~/hpo-seats/<round>), WORKTREE_GC_TMP_ROOT
 #   (default /tmp), WORKTREE_GC_MIN_AGE (3600, the detached guard),
 #   WORKTREE_GC_ORPHAN_AGE (7200), WORKTREE_GC_VENV_AGE (86400).
 set -uo pipefail
@@ -201,7 +212,7 @@ PY
     # null control pins the redirect itself.
     ( cd "$d/root"
       export STUB="$d" PATH="$W/bin:$PATH" TMPDIR="$d/tmp"
-      export WORKTREE_GC_SEATS_ROOT="$d/orch" WORKTREE_GC_TMP_ROOT="$d/tmp"
+      export WORKTREE_GC_SEATS_ROOT="$(cat "$d/seatsroot" 2>/dev/null || printf '%s' "$d/orch")" WORKTREE_GC_TMP_ROOT="$d/tmp"
       bash "$SELF" "$@" > "$d/out" 2> "$d/err" )
   }
   gots() { grep -c -- "$2" "$W/$1/out"; }
@@ -445,6 +456,71 @@ PY
   [ -d "$D/orch/seat-orph-fail" ]; st $? 0 "and the seat dir is kept"
   st "$(gots failed-move "keep  $D/orch/seat-orph-fail  nondisposable-contents (ev-9)")" 1 "kept naming nondisposable-contents"
 
+  # Carries 0 and 1 (R10-CLOSEOUT-INSTRUMENTS). Seat branches map to their topic's
+  # pull request on fix/<topic>; every removal arm keeps a worktree a process
+  # stands in; plain repo copies in a seat of a merged topic go; the seats root
+  # is a colon-separated list.
+  mkcase seatb; build seatb
+  D="$W/seatb"; mkdir -p "$D/orch2" "$D/live"
+  PH() { printf '%040d' 0 | tr 0 "$1"; }
+  seatwt() { # seat branch head: a registered branch worktree
+    printf 'worktree %s/orch/seat-%s/wt\nHEAD %s\nbranch refs/heads/%s\n\n' "$D" "$1" "$3" "$2" >> "$D/porcelain"
+    mkdir -p "$D/orch/seat-$1/wt"; age_old "$H3" "$D/orch/seat-$1"
+  }
+  seatwt tmerged work/merged-topic "$(PH 7)"; printf '[{"state":"MERGED"}]\n' > "$D/pr/fix_merged-topic.json"
+  seatwt tclosed work/closed-topic "$(PH 7)"; printf '[{"state":"CLOSED"}]\n' > "$D/pr/fix_closed-topic.json"
+  seatwt tunp scratch/unp-topic "$(PH 7)"; printf '[{"state":"MERGED"}]\n' > "$D/pr/fix_unp-topic.json"
+  printf '1\n' > "$D/unpushed/$(encpath "$D/orch/seat-tunp/wt")"
+  seatwt tcwd seat/cwd-topic "$(PH 7)"; printf '[{"state":"MERGED"}]\n' > "$D/pr/fix_cwd-topic.json"
+  seatwt tdirty work/dirty-topic "$(PH 7)"; printf '[{"state":"MERGED"}]\n' > "$D/pr/fix_dirty-topic.json"
+  printf 'M f\n' > "$D/status/$(encpath "$D/orch/seat-tdirty/wt")"
+  seatwt topen work/open-topic "$(PH 7)"; printf '[{"state":"OPEN"}]\n' > "$D/pr/fix_open-topic.json"
+  seatwt tnone work/none-topic "$(PH 7)"
+  seatwt aholder fix/aholder "$(PH 2)"; printf '[{"state":"MERGED"}]\n' > "$D/pr/fix_aholder.json"
+  printf 'worktree %s/orch/seat-bhold/wt\nHEAD 2222222222222222222222222222222222222223\ndetached\n\n' "$D" >> "$D/porcelain"
+  mkdir -p "$D/orch/seat-bhold/wt/sub"; age_old "$H3" "$D/orch/seat-bhold"
+  { printf '%s/orch/seat-tcwd/wt\n%s/orch/seat-aholder/wt\n%s/orch/seat-bhold/wt/sub\n' "$D" "$D" "$D"; cat "$D/cwds"; } > "$D/cwds.n"; mv "$D/cwds.n" "$D/cwds"
+  # class E: plain copies. seat-copy (merged topic, two copies and a non-copy), seat-copyopen
+  # (open topic), seat-copycwd (a process in a copy), seat-copyfresh (inside the age guard);
+  # the second one lives in the second root.
+  for sd in "$D/orch/seat-copy" "$D/orch/seat-copyopen" "$D/orch/seat-copycwd" "$D/orch2/seat-copy2"; do
+    mkdir -p "$sd/mutant-1" "$sd/null-run" "$sd/notes"; printf 'x\n' > "$sd/mutant-1/f"
+  done
+  mkdir -p "$D/orch/seat-copy/head-tree/.git" "$D/orch/seat-copyfresh/mutant-1"
+  for t in copy copycwd copy2; do printf '[{"state":"MERGED"}]\n' > "$D/pr/fix_$t.json"; done
+  printf '[{"state":"OPEN"}]\n' > "$D/pr/fix_copyopen.json"; printf '[{"state":"MERGED"}]\n' > "$D/pr/fix_copyfresh.json"
+  age_old "$H3" "$D/orch/seat-copy" "$D/orch/seat-copyopen" "$D/orch/seat-copycwd" "$D/orch2/seat-copy2"
+  printf '%s/orch/seat-copycwd/null-run/deep\n' "$D" >> "$D/cwds"; mkdir -p "$D/orch/seat-copycwd/null-run/deep"
+  age_old "$H3" "$D/orch/seat-copycwd"
+  printf '%s:%s\n' "$D/orch" "$D/orch2" > "$D/seatsroot"
+  run seatb --keep-dir "$D/ev" o/r; st $? 0 "the carry-0/1 sweep exits 0"
+  gone "$D/orch/seat-tmerged/wt"; st $? 0 "carry 0: a seat branch whose fix/<topic> PR merged, clean and pushed: removed"
+  gone "$D/orch/seat-tclosed/wt"; st $? 0 "carry 0: and one whose fix/<topic> PR is closed"
+  st "$(grep -c "^git update-ref -d refs/heads/work/merged-topic " "$D/log")" 1 "its branch deleted, leased"
+  [ -d "$D/orch/seat-tunp/wt" ]; st $? 0 "null control: one unpushed commit keeps the seat"
+  st "$(gots seatb "keep  $D/orch/seat-tunp/wt  unpushed")" 1 "naming unpushed"
+  [ -d "$D/orch/seat-tcwd/wt" ]; st $? 0 "null control: a live process cwd in a topic-merged seat keeps it"
+  st "$(gots seatb "keep  $D/orch/seat-tcwd/wt  cwd-inside")" 1 "naming cwd-inside"
+  [ -d "$D/orch/seat-tdirty/wt" ]; st $? 0 "null control: an uncommitted change keeps a topic-mapped seat"
+  st "$(gots seatb "keep  $D/orch/seat-tdirty/wt  dirty-topic-seat")" 1 "naming dirty-topic-seat"
+  [ -d "$D/orch/seat-topen/wt" ]; st $? 0 "null control: an open fix/<topic> PR keeps the seat"
+  st "$(gots seatb "keep  $D/orch/seat-topen/wt  open-pr")" 1 "naming open-pr"
+  st "$(gots seatb "keep  $D/orch/seat-tnone/wt  no-merged-pr")" 1 "null control: a seat branch with no topic PR at all stays no-merged-pr"
+  [ -d "$D/orch/seat-aholder/wt" ]; st $? 0 "carry 1 (c): class A with a holder keeps"
+  st "$(gots seatb "keep  $D/orch/seat-aholder/wt  cwd-inside")" 1 "naming cwd-inside"
+  [ -d "$D/orch/seat-bhold/wt" ]; st $? 0 "carry 1 (a): class B with a holder keeps"
+  st "$(gots seatb "keep  $D/orch/seat-bhold/wt  cwd-inside")" 1 "naming cwd-inside"
+  gone "$D/orch/seat-detached/wt"; st $? 0 "carry 1 (b): class B without a holder removes (null control)"
+  gone "$D/orch/seat-copy/mutant-1"; st $? 0 "carry 0: a plain mutant copy in a merged-topic seat: removed"
+  gone "$D/orch/seat-copy/null-run"; st $? 0 "and a null copy"
+  [ -d "$D/orch/seat-copy/head-tree/.git" ] && [ -d "$D/orch/seat-copy/notes" ]; st $? 0 "null control: a copy with a .git, and a directory not named like a copy, stay"
+  gone "$D/orch2/seat-copy2/mutant-1"; st $? 0 "a seat under the second root of the list is collected"
+  [ -d "$D/orch/seat-copyopen/mutant-1" ]; st $? 0 "null control: copies of an open topic stay"
+  st "$(gots seatb "keep  $D/orch/seat-copyopen  copies-unmerged-topic")" 1 "naming copies-unmerged-topic"
+  [ -d "$D/orch/seat-copycwd/null-run" ]; st $? 0 "null control: a process cwd in a copy keeps it"
+  gone "$D/orch/seat-copycwd/mutant-1"; st $? 0 "while the other copy of that seat goes"
+  [ -d "$D/orch/seat-copyfresh/mutant-1" ]; st $? 0 "null control: a seat modified within the age guard keeps its copies"
+
   # --dry-run over a rebuilt fixture: identical decisions, nothing moved.
   mkcase dry; build dry
   run dry --dry-run --keep-dir "$W/dry/ev" o/r; st $? 0 "--dry-run exits 0"
@@ -528,7 +604,7 @@ FETCH_OK=0
 git fetch --prune origin >/dev/null 2>&1 && FETCH_OK=1
 ORIGIN_MAIN_SHA=$(git rev-parse origin/main 2>/dev/null || printf '')
 
-# state: open | merged | none | error -- from the API, never from the local
+# state: open | merged | closed | none | error -- from the API, never from the local
 # branch's existence.
 pr_state_of() {
   local out
@@ -540,7 +616,7 @@ try:
 except ValueError:
     print("error"); raise SystemExit
 s = {(x.get("state") or "").upper() for x in d if isinstance(x, dict)}
-print("open" if "OPEN" in s else ("merged" if "MERGED" in s else "none"))'
+print("open" if "OPEN" in s else ("merged" if "MERGED" in s else ("closed" if "CLOSED" in s else "none")))'
 }
 
 # A merged pull request's head is a PROPER ancestor of origin/main under this
@@ -577,6 +653,28 @@ cwd_inside() { # real path of a worktree
   return 0
 }
 
+# 0 when no live process holds the worktree and it may go; otherwise prints the
+# keep line (cwd-inside, or cwd-unread when lsof cannot say) and returns 1. Every
+# removal arm asks it: a worktree a process stands in goes on no arm.
+cwd_free() { # wt-path real-path
+  cwd_inside "$2"
+  case $? in
+    1) printf 'keep  %s  cwd-inside\n' "$1"; KEPT_N=$((KEPT_N+1)); return 1 ;;
+    2) printf 'keep  %s  cwd-unread\n' "$1"; KEPT_N=$((KEPT_N+1)); return 1 ;;
+  esac
+  return 0
+}
+
+# A seat branch (`work/<topic>`, `scratch/<topic>`, `seat/<topic>`) never has a
+# pull request of its own: its pull request sits on `fix/<topic>`. Prints the
+# state of that one, or `none` for any other branch.
+topic_pr_state() { # branch
+  case "$1" in
+    work/?*|scratch/?*|seat/?*) pr_state_of "fix/${1#*/}" ;;
+    *) printf 'none' ;;
+  esac
+}
+
 # 0 iff something under dir was modified within the given seconds; the keep
 # side of every age guard reads rc 0 as recent.
 recently_modified() {
@@ -665,13 +763,23 @@ dispose_seat_dir() { # seat-dir, after its worktree was removed
 }
 
 seat_dir_of() { # a worktree's real path -> its seat dir when it is <seats>/<seat>/wt
-  case "$1" in
-    "$SEATS_REAL"/*/wt) dirname "$1" ;;
-    *) printf '' ;;
-  esac
+  local root
+  for root in ${SEATS_REALS[@]+"${SEATS_REALS[@]}"}; do
+    case "$1" in
+      "$root"/*/wt) dirname "$1"; return 0 ;;
+    esac
+  done
+  printf ''
 }
 
-SEATS_REAL=$(realpath_of "$SEATS_ROOT" 2>/dev/null || printf '%s' "$SEATS_ROOT")
+# WORKTREE_GC_SEATS_ROOT is a colon-separated list: seats live under one
+# directory per round (~/hpo-seats/<round>), not under one fixed root.
+SEATS_REALS=()
+IFS=: read -r -a SEATS_LIST <<<"$SEATS_ROOT"
+for r in ${SEATS_LIST[@]+"${SEATS_LIST[@]}"}; do
+  [ -n "$r" ] && SEATS_REALS+=("$(realpath_of "$r" 2>/dev/null || printf '%s' "$r")")
+done
+SEATS_ONE=""
 KEEP_REAL=$(realpath_of "$KEEP_DIR" 2>/dev/null || printf '%s' "$KEEP_DIR")
 ELIGIBLE=0; REMOVED_N=0; KEPT_N=0
 HANDLED_SEATS=""
@@ -719,7 +827,7 @@ flush() {
 }
 
 classify() {
-  local real state seat st_out st_rc up onremote c
+  local real state seat st_out st_rc up onremote topic
   real=$(realpath_of "$wt" 2>/dev/null || printf '%s' "$wt")
   printf '%s\n' "$real" >>"$LIVE_FILE"
 
@@ -732,18 +840,31 @@ classify() {
   if [ "$has_branch" -eq 1 ]; then
     # Class A: a branch worktree goes only on an API-read MERGED pull request.
     state=$(pr_state_of "$branch")
+    topic=0
     case "$state" in
       open) printf 'keep  %s  open-pr\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0 ;;
       merged) ;;
-      none) printf 'keep  %s  no-merged-pr\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0 ;;
+      none|closed)
+        # A seat branch's pull request sits on fix/<topic>; a merged or closed
+        # one there frees the seat, on the stricter terms below.
+        case "$(topic_pr_state "$branch")" in
+          merged|closed) topic=1 ;;
+          open) printf 'keep  %s  open-pr\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0 ;;
+          *) printf 'keep  %s  no-merged-pr\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0 ;;
+        esac ;;
       *) printf 'keep  %s  gh-error\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0 ;;
     esac
     up=$(unpushed_of "$wt")
     if [ "$up" != 0 ]; then
       printf 'keep  %s  unpushed (%s commit(s) on no remote ref)\n' "$wt" "$up"; KEPT_N=$((KEPT_N+1)); return 0
     fi
-    ELIGIBLE=$((ELIGIBLE+1))
     st_out=$(git -C "$wt" status --porcelain 2>/dev/null); st_rc=$?
+    if [ "$topic" -eq 1 ] && { [ -n "$st_out" ] || [ "$st_rc" -ne 0 ]; }; then
+      # Not proved merged by its own branch: uncommitted work is on no remote.
+      printf 'keep  %s  dirty-topic-seat\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0
+    fi
+    cwd_free "$wt" "$real" || return 0
+    ELIGIBLE=$((ELIGIBLE+1))
     if [ -n "$st_out" ] || [ "$st_rc" -ne 0 ]; then print_uncommitted "$wt"; fi
     remove_worktree "$wt" "$head" || return 0
     if [ "$DRY" -eq 0 ]; then
@@ -774,13 +895,7 @@ classify() {
   if recently_modified "$real" "$MIN_AGE_DETACHED"; then
     printf 'keep  %s  young\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0
   fi
-  if [ "$onremote" -eq 1 ]; then
-    cwd_inside "$real"; c=$?
-    case "$c" in
-      1) printf 'keep  %s  cwd-inside\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0 ;;
-      2) printf 'keep  %s  cwd-unread\n' "$wt"; KEPT_N=$((KEPT_N+1)); return 0 ;;
-    esac
-  fi
+  cwd_free "$wt" "$real" || return 0
   ELIGIBLE=$((ELIGIBLE+1))
   if [ "$onremote" -eq 1 ]; then remove_worktree "$wt" "$head" on-remote || return 0
   else remove_worktree "$wt" "$head" || return 0; fi
@@ -806,8 +921,10 @@ is_registered() { awk -v p="$1" 'BEGIN{f=1} index(p, $0)==1 {f=0} END{exit f}' "
 # handled" and the seat is judged a second time (R9-RCA-prepr-tmp).
 handled_seat() { printf '%b' "$HANDLED_SEATS" | grep -x "$1" >/dev/null; }
 
-if [ -d "$SEATS_REAL" ]; then
-  for seat in "$SEATS_REAL"/*/; do
+C_SEATS=""
+for SEATS_ONE in ${SEATS_REALS[@]+"${SEATS_REALS[@]}"}; do
+  [ -d "$SEATS_ONE" ] || continue
+  for seat in "$SEATS_ONE"/*/; do
     [ -d "$seat" ] || continue
     seat="${seat%/}"
     seat_real=$(realpath_of "$seat")
@@ -852,6 +969,7 @@ if [ -d "$SEATS_REAL" ]; then
       printf 'keep  %s  live-worktree (%s)\n' "$seat" "$nested"; KEPT_N=$((KEPT_N+1)); continue
     fi
     ELIGIBLE=$((ELIGIBLE+1))
+    C_SEATS="$C_SEATS$seat_real\n"
     printf 'remove  %s (orphaned seat)\n' "$seat"
     preserve_evidence "$seat_real"
     if [ "$DRY" -eq 0 ]; then
@@ -874,7 +992,54 @@ if [ -d "$SEATS_REAL" ]; then
         || printf 'worktree_gc: FAILED to remove %s\n' "$seat" >&2
     fi
   done
-fi
+done
+
+# --- class E: plain repo copies in a seat dir ---------------------------------
+# A mutant, null or head tree a seat copied out of the repository carries no
+# .git, so classes A-C never see it and a seat directory holding one is kept as
+# nondisposable-contents. It goes when the seat's topic (the directory name less
+# a leading `seat-`) has a MERGED pull request on `fix/<topic>`, nothing under
+# the seat was modified within the orphan age, no live worktree remains beneath
+# the seat and no process has its cwd inside the copy.
+for SEATS_ONE in ${SEATS_REALS[@]+"${SEATS_REALS[@]}"}; do
+  [ -d "$SEATS_ONE" ] || continue
+  for seat in "$SEATS_ONE"/*/; do
+    [ -d "$seat" ] || continue
+    seat_real=$(realpath_of "${seat%/}")
+    case "$seat_real" in "$KEEP_REAL"|"$KEEP_REAL"/*) continue ;; esac
+    printf '%b' "$C_SEATS" | grep -x "$seat_real" >/dev/null && continue
+    copies=()
+    for cp in "$seat_real"/*/; do
+      cp="${cp%/}"
+      [ -d "$cp" ] && [ ! -e "$cp/.git" ] || continue
+      case "$(basename "$cp")" in
+        wt) continue ;;
+        *mutant*|*null*|*head*) copies+=("$cp") ;;
+      esac
+    done
+    [ "${#copies[@]}" -gt 0 ] || continue
+    topic=$(basename "$seat_real"); topic=${topic#seat-}
+    if [ "$(pr_state_of "fix/$topic")" != merged ]; then
+      printf 'keep  %s  copies-unmerged-topic\n' "$seat_real"; KEPT_N=$((KEPT_N+1)); continue
+    fi
+    if recently_modified "$seat_real" "$ORPHAN_AGE"; then
+      printf 'keep  %s  fresh\n' "$seat_real"; KEPT_N=$((KEPT_N+1)); continue
+    fi
+    nested=$(live_under "$seat_real")
+    if [ -n "$nested" ]; then
+      printf 'keep  %s  live-worktree (%s)\n' "$seat_real" "$nested"; KEPT_N=$((KEPT_N+1)); continue
+    fi
+    for cp in ${copies[@]+"${copies[@]}"}; do
+      cwd_free "$cp" "$cp" || continue
+      ELIGIBLE=$((ELIGIBLE+1))
+      printf 'remove  %s (plain copy)\n' "$cp"
+      if [ "$DRY" -eq 0 ]; then
+        rm -rf "$cp" && printf 'removed  %s\n' "$cp" && REMOVED_N=$((REMOVED_N+1)) \
+          || printf 'worktree_gc: FAILED to remove %s\n' "$cp" >&2
+      fi
+    done
+  done
+done
 
 # --- class D: stale venvs ----------------------------------------------------
 venv_referenced() { # vdir -> 0 when a live worktree symlinks into it (depth <= 2)
diff --git a/tools/plan/replan.py b/tools/plan/replan.py
index 9805ff334..5520a5401 100644
--- a/tools/plan/replan.py
+++ b/tools/plan/replan.py
@@ -206,10 +206,6 @@ def groups_of(roster: dict) -> dict:
 #: work lives in the group its resume note names.
 ABSORBED_RE = re.compile(r"absorbed into ([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+)")
 
-#: The group that cuts the round's closing stamp; a group after it is post-closure.
-CLOSE_STAMP_MARK = "STAMP-ROUND-MAJOR"
-POST_CLOSE_STEP_RE = re.compile(r"after the .*\b(stamp|closeout)\b", re.I)
-
 
 def is_done(group: dict) -> bool:
     return not roster_lib.is_open(group)
@@ -231,24 +227,6 @@ def absorbers(G: dict) -> dict:
     return out
 
 
-def post_closure_groups(G: dict, open_: set) -> set:
-    """Open groups that run after the round's closing stamp: an owner-step
-    whose next step is "after the ... stamp", a group whose `after` names the
-    closing-stamp group, and every group after one of those."""
-    post = {n for n in open_
-            if (G[n].get("kind") == "owner-step"
-                and POST_CLOSE_STEP_RE.search(str((G[n].get("resume") or {}).get("next_step") or "")))
-            or any(CLOSE_STAMP_MARK in a for a in G[n].get("after") or [])}
-    grew = True
-    while grew:
-        grew = False
-        for n in open_ - post:
-            if any(a in post for a in G[n].get("after") or []):
-                post.add(n)
-                grew = True
-    return post
-
-
 #: Paths that are instruments, CI or records, never the integration (tvofi
 #: 2026-11-06: the plan placed instrument and CI fixes in the core lane).
 _NON_PRODUCT_PREFIXES = ("tools/", "tests/", ".github/", ".claude/", "dev/", "docs/")
@@ -916,7 +894,7 @@ def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
     deps, open_, done = dependency_graph(G)
     # Groups after the round's closing stamp are scheduled after it and are
     # neither inside closure nor in any stamp's carries (carries 10, 11).
-    post = post_closure_groups(G, open_)
+    post = roster_lib.post_closure_groups(G, open_)
     open_all = open_
     open_ = open_all - post
     deps_post = {n: deps[n] for n in post}

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
