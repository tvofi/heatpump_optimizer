# Review packet #3262
head: aa5022f63cac715abe871d168d2ed250997261e7
base: 62bcca76ee043e68544a7f7042e9bb3ff5502aa7

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=128369601046 success
arch-score / arch-score id=128389122441 success
arm id=128369306520 skipped
budget-raise-gate / budget-raise-gate id=128389143809 success
cancel-superseded id=128389121965 success
codeql id=128389122554 skipped
codeql / Analyze (actions) id=128382847845 success
codeql / Analyze (javascript-typescript) id=128382869446 success
codeql / Analyze (python) id=128382878220 success
gate id=128389122431 success
governance id=128389146664 skipped
governance / delivery-status id=128382847881 success
governance / delivery-status-publish id=128382847626 skipped
governance / env-matrix id=128382847580 success
governance / instrument-self-tests id=128382846790 success
governance / policy-docs id=128382873578 success
governance / record id=128382847594 skipped
governance / wave-script id=128382847842 success
hassfest id=128389143035 skipped
hassfest / hassfest id=128382878043 success
kernel-points id=128389146805 skipped
pr-contract id=128389119164 skipped
pr-contract / pr-contract id=128389122891 success
prelude id=128389137181 success
refresh id=128389156452 success
tests id=128389122863 skipped
tests / arch-instrument id=128382848546 success
tests / briefs id=128382880318 success
tests / browser id=128382848131 success
tests / ci-ratchet id=128382848616 skipped
tests / claims-autofix id=128382848848 skipped
tests / closure-scope id=128382866113 success
tests / closures id=128382848141 success
tests / closures-autofix id=128382848724 skipped
tests / coverage id=128382848254 success
tests / coverage-ratchet id=128382848613 success
tests / fast (3.14) id=128382848268 success
tests / graders-head-copy id=128382849003 success
tests / lane-proofs id=128382848606 success
tests / mutation id=128382869628 success
tests / mutation-autofix id=128382849125 skipped
tests / mutation-pins id=128382848600 skipped
tests / nightly-ha id=128382848439 skipped
tests / nightly-status id=128382846793 failure
tests / replay id=128382848388 skipped
tests / typing id=128382848267 success
validate id=128389147784 skipped
validate / validate-hacs id=128382866434 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/audit/seat/outside_intake.py --self-test
             `tools/audit/seat/outside_intake.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  unverified git diff --name-only origin/main...HEAD | grep -c budgets.json
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/ref_privacy.py --check
             `tools/audit/seat/ref_privacy.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/tmp_paths.py --check
             `tools/audit/seat/tmp_paths.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/selftest_wiring.py --check
             `tools/audit/seat/selftest_wiring.py` is in the tree at this head
  unverified git diff --quiet origin/main HEAD -- <those> && echo BYTE-IDENTICAL
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         bash tools/audit/seat/cloud-setup.sh --check
             `tools/audit/seat/cloud-setup.sh` is in the tree at this head
  ok         tools/pr/prepr.sh <body>
             `tools/pr/prepr.sh` is in the tree at this head
  ok         tools/pr/prepr.sh --body-check <body>
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 14 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.github/workflows/governance.yml b/.github/workflows/governance.yml
index 759ec575e..018e7f43f 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -320,6 +320,16 @@ jobs:
       - name: Show the probe bridge deriving the reference and refusing without a probed run
         run: python3 tools/audit/seat/probe_bridge.py --self-test
 
+      # R10-OUTSIDE-INTAKE: the public plan page's stager (its refusal of a
+      # page carrying a host path or a tool's attribution) and the outside
+      # intake's owed lines, answers and mutants, offline over faked gh and
+      # git; the intake's projections run through the runner's own jq.
+      - name: Show the plan page stager refusing a page it may not publish
+        run: python3 -I tools/audit/seat/plan_public.py --self-test
+
+      - name: Show the outside intake owing, answering once and refusing its fixtures
+        run: python3 -I tools/audit/seat/outside_intake.py --self-test
+
       # The I3 barrier's own verdicts (BLIND, DEAD, REFUSED, unregistered) on a
       # synthetic registration, offline: `policy-docs` runs the base's copy,
       # which cannot answer for a change to this one.
diff --git a/.github/workflows/pages.yml b/.github/workflows/pages.yml
index 1bd18308a..048b2e70b 100644
--- a/.github/workflows/pages.yml
+++ b/.github/workflows/pages.yml
@@ -19,6 +19,16 @@ name: Pages
 #   is red. The deploy job runs in the `github-pages` environment, whose
 #   deployment rules (the owner's) decide which refs may deploy: a `v*` tag
 #   deploys only once that environment admits `v*` tags.
+# * It also serves the ongoing round's plan page at `plan/` (R10-OUTSIDE-INTAKE;
+#   tvofi, 2026-11-06): tools/audit/seat/plan_public.py, run from the
+#   dispatched ref's tree, stages PLAN.html from the newest
+#   `handoff/audit-r<N>-plan` state ref, refusing a page that carries a host
+#   path or a tool's attribution (a red run; nothing deployed), and the beat's
+#   `plan-beat` row dispatches this workflow on `main` after each state push
+#   that carried a page. Between rounds there is no page: the site deploys
+#   without one and warns. The docs are always the newest `v*` tag's -- on a
+#   dispatch the build checks that tag out after staging the plan -- so a plan
+#   refresh never serves main's unreleased documentation.
 #
 # tests/entities.py pins all of this, and runs the staging and guard steps by
 # their names in a scratch repository.
@@ -52,6 +62,8 @@ jobs:
       - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
         with:
           persist-credentials: false
+          fetch-depth: 0
+          fetch-tags: true
 
       - name: Ask whether Pages is enabled
         id: probe
@@ -75,6 +87,32 @@ jobs:
           echo "$msg" >> "$GITHUB_STEP_SUMMARY"
           echo "enabled=false" >> "$GITHUB_OUTPUT"
 
+      # From the dispatched ref's tree, before the release is checked out:
+      # rc 2 is no page to publish (warned), rc 1 a refused page (red).
+      - name: Stage the round's plan page
+        run: |
+          set -uo pipefail
+          git fetch --no-tags --quiet origin '+refs/heads/handoff/audit-r*-plan:refs/remotes/origin/handoff/audit-r*-plan' || exit 1
+          rc=0
+          python3 -I tools/audit/seat/plan_public.py stage --out "$RUNNER_TEMP/plan-site" || rc=$?
+          if [ "$rc" -eq 2 ]; then
+            echo "::warning title=No plan page::no round's plan page to publish; the site deploys without one"
+          elif [ "$rc" -ne 0 ]; then
+            exit "$rc"
+          fi
+
+      - name: Check out the release
+        if: github.ref_type != 'tag'
+        run: |
+          set -euo pipefail
+          tag=$(git tag -l 'v*' --sort=-v:refname | head -n 1)
+          if [ -z "$tag" ]; then
+            echo "::warning title=No release tag::no v* tag; the docs are the dispatched ref's"
+            exit 0
+          fi
+          git -c advice.detachedHead=false checkout --quiet "$tag"
+          echo "docs from $tag"
+
       - uses: actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1 # v7.1.0
         with:
           node-version: "22"
@@ -109,6 +147,14 @@ jobs:
           mkdir -p _site/site/mermaid
           cp tools/site/node_modules/mermaid/dist/mermaid.min.js _site/site/mermaid/mermaid.min.js
 
+      - name: Add the round's plan page
+        run: |
+          set -euo pipefail
+          if [ -f "$RUNNER_TEMP/plan-site/plan/index.html" ]; then
+            mkdir -p _site/plan
+            cp "$RUNNER_TEMP/plan-site/plan/index.html" _site/plan/index.html
+          fi
+
       - name: Refuse a published markdown file
         run: |
           set -euo pipefail
diff --git a/dev/governance/roles/orchestrator.md b/dev/governance/roles/orchestrator.md
index 0248c8586..4d0d219e2 100644
--- a/dev/governance/roles/orchestrator.md
+++ b/dev/governance/roles/orchestrator.md
@@ -6,10 +6,7 @@ report to the owner.
 
 **Your pull requests are reviewed. Your process is not.** Most of what you
 produce never meets a reviewer: merge-commit messages, issue bodies and
-comments, dispatch briefs, roster edits, and what you tell the owner. On
-2026-09-07 the orchestrator made a run of unmeasured claims, each
-caught by a review seat and none by itself, while writing the policy against
-them. **Not one was in a pull-request body.**
+comments, dispatch briefs, roster edits, and what you tell the owner.
 
 ## 0. Everything in the repository's policy binds you
 
@@ -110,6 +107,10 @@ whenever you merge.
   `standing-tick.md`, `standing-merge.md`, `standing-dispatch.md` and
   `standing-roster.md`. You send queue lines and act on their reports; the
   sweep restarts any that is absent or stopped with work owed.
+- **Each outside submission reaches a disposition** (tvofi, 2026-11-06): an
+  `OUTSIDE ... owed=triage` line (`tools/audit/seat/outside_intake.py`) is
+  triaged or designed, then wired into a roster group or refused
+  (`outside_intake.py refuse`); `owed=answer` goes to `standing-dispatch.md`.
 - **A proposal goes to `proposal-triage.md` before it is routed**: a process,
   tooling or instrument proposal from the sweep, a seat's result or a verdict.
   Where a mandate lets you act on a recommendation absent the owner, that means
@@ -261,11 +262,8 @@ session-local copy is a defect** (tvofi, 2026-10-03; ownership is 0013's). What
 carries, stamps, gates, watches CI or records state runs from the tree, never
 from scratch or `~/`.
 
-**Look the instrument up before you write one** (tvofi, 2026-10-19). Round 10
-hand-rolled a tick driver, relay, sweep prompt and merge loops beside
-`tick_loop.sh`, `cloud_relay.sh`, `sweep_render.py` and `merge_train.py`. The
-instruments guide in `tools/audit/seat/` lists them; read it before any loop,
-watcher, relay or helper.
+**Look the instrument up before you write one** (tvofi, 2026-10-19): read the
+instruments guide in `tools/audit/seat/` before any loop, watcher, relay or helper.
 
 - A new helper needs a stated reason and lives in `tools/` with a `--self-test`,
   never only in scratch or `/tmp`; a listed instrument that falls short is
diff --git a/dev/governance/roles/standing-dispatch.md b/dev/governance/roles/standing-dispatch.md
index 35ca31403..7d10678e3 100644
--- a/dev/governance/roles/standing-dispatch.md
+++ b/dev/governance/roles/standing-dispatch.md
@@ -8,18 +8,18 @@ and role to dispatch or a relay to run; critical-path items first.
 three-dot diff, then `tools/pr/approve_held_runs.sh`, `tools/audit/seat/bus.sh
 dispatch`, `tools/audit/seat/cloud_dispatch.py --role reviewer` at the printed
 head and nonce, and the `dispatch/reviewer-rev-<pr>` publish. Report
-`fire-owed <ref>`: a subagent cannot call RemoteTrigger; the orchestrator
-fires. A `record/autofix` pull request is never dispatched a reviewer.
+`fire-owed <ref>`: the orchestrator fires (a subagent cannot call
+RemoteTrigger). A `record/autofix` pull request is never dispatched a reviewer.
 
 **Relay:** `cloud_relay.sh pass --confirm`; `bus.sh confirm` merge verdicts
 carried to the live head; report each `handoff-body/<topic>`. A beat job takes
-over once a cycle's log agrees; never inline.
+over once a cycle's log agrees; never inline. **Answer** each queued `owed=answer`
+line: `tools/audit/seat/outside_intake.py answer --issue <n>`.
 
 ## Read the ref, not the record
 
 The roster's `resume.stage` and `resume.branch` are a seat's own claim;
-`roster_edit.py set-stage` refuses unknown stages; nothing verifies
-`branch` against the remote. Where `resume.commit` is set,
+nothing verifies `branch` against the remote. Where `resume.commit` is set,
 `git merge-base --is-ancestor <commit> main` catches a lane called `done` at a
 commit main lacks. Before a dispatch, ask the repository:
 
@@ -30,9 +30,8 @@ commit main lacks. Before a dispatch, ask the repository:
 A `handoff-body/<topic>` with a `handoff/<topic>` and no pull request at either
 `fix/` name **handed off and was never opened**: run
 `tools/audit/seat/open_pr.sh`, never a fresh implementer. A pull request whose
-head is an ancestor of the ref is `tools/audit/seat/update_pr.sh`'s; a ref and
-pull request that diverged go back to the orchestrator. `bus.sh orphans`
-answers it for every ref at once.
+head is an ancestor of the ref is `tools/audit/seat/update_pr.sh`'s; diverged,
+the orchestrator's. `bus.sh orphans` answers every ref at once.
 
 **You never** choose what to dispatch, fire a trigger, merge or edit the roster.
 **Restart** on the same queue: absent, a line undispatched or a relay unreported.
diff --git a/dev/programme/HANDOVER.md b/dev/programme/HANDOVER.md
index d0863f494..2838ab276 100644
--- a/dev/programme/HANDOVER.md
+++ b/dev/programme/HANDOVER.md
@@ -32,6 +32,11 @@ line (`git log --first-parent --format='%h %s' v7.0.0..origin/main | grep ' v7\.
   is a dated snapshot, not the path. The resume, plan table and next-session
   prompt under `handoff/round10/state/` on `origin/handoff/audit-r10-plan` are
   generated from the roster by `tools/audit/seat/state_docs.py`.
+- **The round's plan page is public** at
+  `https://tvofi.github.io/heatpump_optimizer/plan/`: `.github/workflows/pages.yml`
+  publishes it through `tools/audit/seat/plan_public.py` after each state push
+  of the beat's `plan-beat` row. An outside submission on the roster is answered
+  with that link by `tools/audit/seat/outside_intake.py answer`.
 - **Done for round 10** (tvofi, 2026-10-25, verbatim): "run the full programme
   to completion (no owed handoffs, no deferred findings, no deferred leads, no
   open roster groups, no issues open except 201, nothing deferred to round
diff --git a/dev/programme/delivery/3262.md b/dev/programme/delivery/3262.md
new file mode 100644
index 000000000..9cdf482a1
--- /dev/null
+++ b/dev/programme/delivery/3262.md
@@ -0,0 +1 @@
+- [#3262](https://github.com/tvofi/heatpump_optimizer/pull/3262) — **open**, R10-OUTSIDE-INTAKE: the plan html public from the developer documentation, and the outside-contributor intake (R10-OUTSIDE-INTAKE)
diff --git a/tests/closures.json b/tests/closures.json
index 66cd59e7d..96fa7349d 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3878,9 +3878,12 @@
    "tools/audit/seat/open_driver.py",
    "tools/audit/seat/open_driver_selftest.py",
    "tools/audit/seat/orchestrator_tick.py",
+   "tools/audit/seat/outside_intake.py",
+   "tools/audit/seat/outside_intake_selftest.py",
    "tools/audit/seat/owed_unactioned.py",
    "tools/audit/seat/plan_audit.py",
    "tools/audit/seat/plan_page.py",
+   "tools/audit/seat/plan_public.py",
    "tools/audit/seat/postmerge.py",
    "tools/audit/seat/probe_bridge.py",
    "tools/audit/seat/proof_watch.py",
diff --git a/tests/entities.py b/tests/entities.py
index 935601311..6aa13ee3a 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -40889,6 +40889,78 @@ R.check(
     f"copy-all: {_PG_NULL_STAGE}; no-op guard: {_PG_NULL_GUARD}",
 )
 
+# The round's plan page (R10-OUTSIDE-INTAKE): three steps, pinned by RUNNING
+# the two that move files and by their order. The page is staged from the
+# dispatched ref's tree BEFORE the release is checked out (a tag older than
+# plan_public.py could not stage it), the release checkout is skipped on a tag
+# push and takes the newest `v*` tag by version, never by string order, and
+# the page reaches `_site/plan/` only when a page was staged.
+_PG_PLAN = ("Stage the round's plan page", "Check out the release", "Add the round's plan page")
+
+
+def _pg_plan_defects(text: str) -> "list[str]":
+    doc = _yaml.safe_load(text) or {}
+    steps = [s or {} for j in (doc.get("jobs") or {}).values() for s in ((j or {}).get("steps") or [])]
+    idx = {s.get("name"): i for i, s in enumerate(steps)}
+    if any(n not in idx for n in (*_PG_PLAN, _PG_STAGE, _PG_GUARD)):
+        return [f"a plan step is missing: {[n for n in _PG_PLAN if n not in idx]}"]
+    out: "list[str]" = []
+    st, co, add = (steps[idx[n]] for n in _PG_PLAN)
+    if not idx[_PG_PLAN[0]] < idx[_PG_PLAN[1]] < idx[_PG_STAGE] < idx[_PG_PLAN[2]] < idx[_PG_GUARD]:
+        out.append("plan steps out of order: stage the page, check out the release, "
+                   "stage the site, add the page, then the guard")
+    if "tools/audit/seat/plan_public.py stage" not in str(st.get("run", "")):
+        out.append("the plan page is not staged by plan_public.py")
+    if "ref_type != 'tag'" not in str(co.get("if", "")):
+        out.append("the release checkout is not skipped on a tag push")
+    with tempfile.TemporaryDirectory() as tmp:
+        repo = Path(tmp) / "repo"
+        repo.mkdir()
+        git = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
+        env = throwaway_git_init(repo, "-q")
+        for tag in ("v1.9.0", "v1.10.0", "x9"):
+            (repo / "f").write_text(tag)
+            subprocess.run(git + ["add", "f"], cwd=repo, check=True, env=env)
+            subprocess.run(git + ["commit", "-qm", tag], cwd=repo, check=True, env=env)
+            subprocess.run(git + ["tag", tag], cwd=repo, check=True, env=env)
+        rc = _pg_run(str(co.get("run", "")), repo)
+        if rc != 0 or (repo / "f").read_text() != "v1.10.0":
+            out.append(f"the release checkout took {(repo / 'f').read_text()!r} (rc={rc}), not v1.10.0")
+        (repo / "_site").mkdir()
+        if _pg_run(str(add.get("run", "")), repo) != 0 or (repo / "_site" / "plan").exists():
+            out.append("with no staged page, the add step put something at _site/plan")
+        # The stage step under the runner's own `-eo pipefail`, over a stub
+        # python3 and git: no page to publish (rc 2) warns and passes, a
+        # refused page (rc 1) is red.
+        stub = Path(tmp) / "bin"
+        stub.mkdir()
+        (stub / "git").write_text("#!/bin/sh\nexit 0\n")
+        for want_rc, py_rc in ((0, 2), (1, 1), (0, 0)):
+            (stub / "python3").write_text(f"#!/bin/sh\nexit {py_rc}\n")
+            for f in stub.iterdir():
+                f.chmod(0o755)
+            env = dict(os.environ, RUNNER_TEMP=tmp, GITHUB_OUTPUT=os.devnull, GITHUB_STEP_SUMMARY=os.devnull,
+                       PATH=f"{stub}{os.pathsep}{os.environ.get('PATH', '')}")
+            rc = subprocess.run(["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", str(st.get("run", ""))],
+                                cwd=repo, env=env, capture_output=True, text=True).returncode
+            if (rc != 0) != bool(want_rc):
+                out.append(f"the plan stage step exits {rc} when plan_public.py exits {py_rc}")
+        page = Path(tmp) / "plan-site" / "plan" / "index.html"
+        page.parent.mkdir(parents=True)
+        page.write_text("<!doctype html>plan")
+        if _pg_run(str(add.get("run", "")), repo) != 0 or not (repo / "_site/plan/index.html").is_file():
+            out.append("a staged page did not reach _site/plan/index.html")
+    return out
+
+
+_PG_PLAN_GOT = _pg_plan_defects(_PG_WF.read_text()) if _PG_WF.is_file() else ["no pages.yml"]
+R.check(
+    "the Pages workflow stages the round's plan page before it checks out the newest release, "
+    "and adds it under plan/ only when one was staged",
+    not _PG_PLAN_GOT,
+    "; ".join(_PG_PLAN_GOT[:4]),
+)
+
 # Classified as its siblings are (the `_NON_GATE_WORKFLOWS` loop above): this
 # script reads it, so an edit to it selects this script; it sets no gate
 # variable and runs no gate script, so it never forces FULL.
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index 57fcb0697..b6620aa2d 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -111,6 +111,8 @@ sweep's standing-seat liveness step keep them alive.
 - [`beatd_shims/git`](instruments/beatd_shims_git.md) — the beat jobs' `git`, reached only through the `PATH` `beatd.py` builds
 - [`train.sh`](instruments/train.sh.md) — one invocation shape for `merge_train.py batch`
 - [`state_docs.py`](instruments/state_docs.py.md) — one call regenerates the four state docs (`plan_table.py`, `merge_throughput.py flow`, `resume_doc.py`, `handover_prompt.py`), commits exactly their outputs to the orphan ref `handoff/audit-r<N>-plan` at `handoff/round<N>/state/`, N the roster's round
+- [`plan_public.py`](instruments/plan_public.py.md) — stages the ongoing round's plan page from the newest state ref for the public site, refusing a page that would publish a host path or a tool's attribution
+- [`outside_intake.py`](instruments/outside_intake.py.md) — lists submissions by outside users since a cursor with what each is owed (triage, answer, reply), and answers or refuses one, marked so none is answered twice
 - [`postmerge.py`](instruments/postmerge.py.md) — after a merge: the #201 line, the roster stage, the state docs and main's suite state; a failed step is printed OWED and opens the ledger's `postmerge-owed`
 - [`record_beat.py`](instruments/record_beat.py.md) — one merged pull request's #201 record line from a fixed template, the full merge sha, read back byte-identical
 - [`sweep_driver.py`](instruments/sweep_driver.py.md) — the probe PR's sweep, where `workflow_run` never fires (`gate-sweep.yml` runs only from the default branch)
diff --git a/tools/audit/seat/beat_jobs.py b/tools/audit/seat/beat_jobs.py
index 3e4be953b..24daa2182 100644
--- a/tools/audit/seat/beat_jobs.py
+++ b/tools/audit/seat/beat_jobs.py
@@ -55,7 +55,11 @@ ROWS (the job table's `interval_s` in brackets):
                      `S/roster-lint`, the orchestrator's to provision.
   plan-beat [1800]   replan.py `--out`, then state_docs.py `--push --mirror
                      --plan`; `plan-beat: PLAN UNAVAILABLE` on a replan failure
-                     or state_docs rc 1, `plan-beat: REFUSED` on its rc 2.
+                     or state_docs rc 1, `plan-beat: REFUSED` on its rc 2. A
+                     pass whose state push landed (`pushed ` on rc 0 or 1)
+                     dispatches `pages.yml` on main, which publishes the page
+                     at plan_public.PLAN_URL; `plan-beat: PAGES NOT DISPATCHED`
+                     when gh refuses.
   pulse [300]        pulse.py into `S/beatd/pulse.txt`; its STOPPED and
                      UNREADABLE lines to the digest.
   cancel-sweep [600] cancel_superseded.py `sweep --repo R`; failures only.
@@ -74,6 +78,10 @@ ROWS (the job table's `interval_s` in brackets):
                      dispatched again only after it reads `ok` or `insufficient`.
                      The guardrail's exit code is not read as a verdict; a failed run
                      is UNREADABLE until the next readable run clears it.
+  outside-intake [1800] outside_intake.py `list --since <intake_since>
+                     --cursor state/outside-cursor.json`: its `OUTSIDE` lines
+                     (submissions by outside users owed a triage, an answer or
+                     a reply this turn), `outside-intake: UNREADABLE` on rc 2.
 No row runs `git checkout`, `reset`, `pull` or `merge`; main is read as
 `git -C <repo> cat-file -e origin/main:<path>`. No row touches a seat's alive
 file. Every row exits 0 once its lines are written: the digest is the signal,
@@ -95,7 +103,7 @@ import time
 from pathlib import Path
 
 ROWS = ("tick-digest", "owed-check", "roster-drain", "plan-beat", "pulse",
-        "cancel-sweep", "disk", "opener", "head-watch", "audit-dispatch")
+        "cancel-sweep", "disk", "opener", "head-watch", "audit-dispatch", "outside-intake")
 HOLD_STALE_S = 24 * 3600  # gap 6: a hold line never expired
 #: The board's actionable family (carry 20's list), keyed on the texts
 #: orchestrator_tick.py and ledger.py print; the self-test pins each literal there.
@@ -355,20 +363,26 @@ def roster_drain(ctx: Ctx) -> None:
 
 
 def plan_beat(ctx: Ctx) -> None:
-    got = ctx.need("plan-beat", "plan_json", "plan_slots", "plan_seats", "state_mirror")
+    got = ctx.need("plan-beat", "plan_json", "plan_slots", "plan_seats", "state_mirror", "repo")
     if got is None:
         return
-    plan, slots, seats, mirror = got
+    plan, slots, seats, mirror, repo = got
     rc, _, err = ctx.py("tools/plan/replan.py", "--out", plan, "--slots", slots, "--seats", seats)
     if rc != 0:
         last = (err.strip().splitlines() or [""])[-1]
         return write_job(ctx, "plan-beat", [f"plan-beat: PLAN UNAVAILABLE replan rc={rc}: {last}"])
-    rc, _, err = ctx.py("tools/audit/seat/state_docs.py", "--push", "--mirror", mirror, "--plan", plan)
-    if rc == 0:
-        return write_job(ctx, "plan-beat", [])
-    said = [ln for ln in err.splitlines() if "UNAVAILABLE" in ln or "REFUSED" in ln]
-    word = "PLAN UNAVAILABLE" if rc == 1 else "REFUSED"
-    write_job(ctx, "plan-beat", [f"plan-beat: {word} rc={rc}: {(said or [''])[-1]}"])
+    rc, out, err = ctx.py("tools/audit/seat/state_docs.py", "--push", "--mirror", mirror, "--plan", plan)
+    lines = []
+    if rc != 0:
+        said = [ln for ln in err.splitlines() if "UNAVAILABLE" in ln or "REFUSED" in ln]
+        word = "PLAN UNAVAILABLE" if rc == 1 else "REFUSED"
+        lines.append(f"plan-beat: {word} rc={rc}: {(said or [''])[-1]}")
+    if rc in (0, 1) and re.search(r"^pushed ", out, re.M):  # the state ref moved: publish its page
+        drc, _, derr = ctx.run(["gh", "workflow", "run", "pages.yml", "--repo", repo, "--ref", "main"],
+                               ctx.repo, ctx.env)
+        if drc != 0:
+            lines.append(f"plan-beat: PAGES NOT DISPATCHED rc={drc}: {(derr.strip().splitlines() or [''])[-1]}")
+    write_job(ctx, "plan-beat", lines)
 
 
 def pulse(ctx: Ctx) -> None:
@@ -476,9 +490,22 @@ def audit_dispatch(ctx: Ctx) -> None:
     write_job(ctx, "audit-dispatch", kept + new)
 
 
+def outside_intake(ctx: Ctx) -> None:
+    got = ctx.need("outside-intake", "repo", "intake_since")
+    if got is None:
+        return
+    rc, out, err = ctx.py("tools/audit/seat/outside_intake.py", "list", "--repo", got[0], "--since", got[1],
+                          "--cursor", str(ctx.digest / "state" / "outside-cursor.json"))
+    if rc in (0, 1):
+        return write_job(ctx, "outside-intake", [ln for ln in out.splitlines() if ln.startswith("OUTSIDE ")])
+    why = next((ln for ln in out.splitlines() if ln.startswith("outside-intake: UNREADABLE")), None)
+    write_job(ctx, "outside-intake", [why or f"outside-intake: UNREADABLE rc={rc}: {(err.strip().splitlines() or [''])[-1]}"])
+
+
 RUN = {"tick-digest": tick_digest, "owed-check": owed_check, "roster-drain": roster_drain,
        "plan-beat": plan_beat, "pulse": pulse, "cancel-sweep": cancel_sweep, "disk": disk,
-       "opener": opener, "head-watch": head_watch, "audit-dispatch": audit_dispatch}
+       "opener": opener, "head-watch": head_watch, "audit-dispatch": audit_dispatch,
+       "outside-intake": outside_intake}
 
 
 def main(argv: list[str]) -> int:
diff --git a/tools/audit/seat/beat_jobs_selftest.py b/tools/audit/seat/beat_jobs_selftest.py
index 7487a63dc..1647e8466 100644
--- a/tools/audit/seat/beat_jobs_selftest.py
+++ b/tools/audit/seat/beat_jobs_selftest.py
@@ -70,7 +70,8 @@ def cases(bj) -> dict[str, bool]:
         (s / "beatd").mkdir(parents=True)
         ov = {"repo": "o/r", "seat_ledger": str(s / "ledger"), "plan_json": str(s / "p.json"),
               "plan_slots": 10, "plan_seats": 99, "state_mirror": str(s / "mirror"),
-              "disk_floor_gib": 20, "seat_queues": "--seat-queue merge=" + str(s / "q")}
+              "disk_floor_gib": 20, "seat_queues": "--seat-queue merge=" + str(s / "q"),
+              "intake_since": "2026-11-01T00:00:00Z"}
         if overlay is not None:
             ov = overlay
         (s / "sweep-overlay.json").write_text(json.dumps(ov))
@@ -323,6 +324,38 @@ def cases(bj) -> dict[str, bool]:
     res["plan-beat: replan is handed the plan, slots and seats"] = (
         arg(a, "--out") == str(c.state.parent / "p.json") or arg(a, "--out").endswith("p.json")) and (
         arg(a, "--slots") == "10" and arg(a, "--seats") == "99")
+    c, f = fresh(answers={"state_docs.py": (0, "pushed handoff/audit-r10-plan at abc\n", "")})
+    bj.plan_beat(c)
+    gh = [x for x in f.calls if x[0] == "gh"]
+    res["plan-beat: a state push that landed dispatches the Pages deploy on main, once"] = (
+        not files(c) and len(gh) == 1 and gh[0][1:4] == ["workflow", "run", "pages.yml"]
+        and arg(gh[0], "--ref") == "main" and arg(gh[0], "--repo") == "o/r")
+    c, f = fresh(answers={"state_docs.py": (0, "already current: handoff/audit-r10-plan at abc carries it\n", "")})
+    bj.plan_beat(c)
+    res["plan-beat null: an already-current state ref dispatches nothing"] = not any(x[0] == "gh" for x in f.calls)
+    c, f = fresh(answers={"state_docs.py": (0, "pushed handoff/audit-r10-plan at abc\n", ""),
+                          "gh": (1, "", "HTTP 403: Resource not accessible\n")})
+    bj.plan_beat(c)
+    res["plan-beat: a refused Pages dispatch reaches the digest"] = digest(c).startswith(
+        "plan-beat: PAGES NOT DISPATCHED rc=1")
+
+    # outside-intake
+    c, f = fresh(answers={"outside_intake.py": (0, "", "")})
+    bj.outside_intake(c)
+    oi = next((x for x in f.calls if any(a.endswith("outside_intake.py") for a in x)), [])
+    res["outside-intake null: nothing owed writes nothing"] = not files(c) and f.ran("outside_intake.py") == 1
+    res["outside-intake: the instrument is handed the repo, the overlay's since and a cursor under state/"] = (
+        arg(oi, "--repo") == "o/r" and arg(oi, "--since") == "2026-11-01T00:00:00Z"
+        and (arg(oi, "--cursor") or "").endswith("state/outside-cursor.json") and "list" in oi)
+    line = "OUTSIDE #3226 owed=triage pr by=Bankaifan since=2026-11-05T11:36:11Z"
+    c, f = fresh(answers={"outside_intake.py": (1, "noise\n" + line + "\n", "")})
+    absent = "OUTSIDE #3226" not in digest(c)
+    bj.outside_intake(c)
+    res["outside-intake: each OUTSIDE line reaches the digest, nothing else"] = (
+        absent and digest(c).splitlines() == ["OUTSIDE #3226 owed=triage pr by=Bankaifan since=<t>"])
+    c, f = fresh(answers={"outside_intake.py": (2, "outside-intake: UNREADABLE Unreadable: gh api rc=1\n", "")})
+    bj.outside_intake(c)
+    res["outside-intake: rc 2 is UNREADABLE, never clean"] = digest(c).startswith("outside-intake: UNREADABLE")
 
     # pulse
     ok = "PULSE opener ok fine\npulse: 1 arms, 0 stopped, 0 unreadable at 2026-11-01T09:00:00Z\n"
@@ -564,9 +597,19 @@ MUTANTS = {
                        "roster-drain: a queue line drains once, is marked, and is not re-run"),
     "roster_hold_ignored": ("            if not on_main(ctx, parts[1]):", "            if False:",
                             "roster-drain: a hold waits for main, is HOLD-STALE past 24 h, then releases"),
-    "plan_rc1_silent": ('    if rc == 0:\n        return write_job(ctx, "plan-beat", [])',
-                        '    if rc in (0, 1):\n        return write_job(ctx, "plan-beat", [])',
+    "plan_rc1_silent": ("    if rc != 0:\n        said = ", "    if rc not in (0, 1):\n        said = ",
                         "plan-beat: state_docs rc 1 is PLAN UNAVAILABLE"),
+    "pages_never_dispatched": ('re.search(r"^pushed ", out, re.M)', "False",
+                               "plan-beat: a state push that landed dispatches the Pages deploy on main, once"),
+    "pages_always_dispatched": ('    if rc in (0, 1) and re.search(r"^pushed ", out, re.M):', "    if rc in (0, 1):",
+                                "plan-beat null: an already-current state ref dispatches nothing"),
+    "pages_refusal_silent": ("        if drc != 0:\n", "        if False:\n",
+                             "plan-beat: a refused Pages dispatch reaches the digest"),
+    "outside_lines_dropped": ('if ln.startswith("OUTSIDE ")]', 'if ln.startswith("OUTSIDEX ")]',
+                              "outside-intake: each OUTSIDE line reaches the digest, nothing else"),
+    "outside_rc2_clean": ("    if rc in (0, 1):\n        return write_job(ctx, \"outside-intake\"",
+                          "    if rc in (0, 1, 2):\n        return write_job(ctx, \"outside-intake\"",
+                          "outside-intake: rc 2 is UNREADABLE, never clean"),
     "pulse_stopped_dropped": ('(?:STOPPED|UNREADABLE) ', '(?:UNREADABLE) ', "pulse: a STOPPED line reaches the digest"),
     "cancel_failure_dropped": ('r"could not cancel| rc=', 'r"could not cancelX| rc=',
                                "cancel-sweep: a failure reaches the digest"),
diff --git a/tools/audit/seat/beatd.jobs.json b/tools/audit/seat/beatd.jobs.json
index 7e68ada02..6bff549a8 100644
--- a/tools/audit/seat/beatd.jobs.json
+++ b/tools/audit/seat/beatd.jobs.json
@@ -201,6 +201,26 @@
       ],
       "class": null,
       "kind": "periodic"
+    },
+    {
+      "name": "outside-intake",
+      "argv": [
+        "python3",
+        "-I",
+        "tools/audit/seat/beat_jobs.py",
+        "outside-intake",
+        "--state",
+        "$S"
+      ],
+      "cwd": "orch",
+      "interval_s": 1800,
+      "timeout_s": 300,
+      "heartbeat_s": null,
+      "env_pass": [
+        "GH_TOKEN"
+      ],
+      "class": null,
+      "kind": "periodic"
     }
   ]
 }
diff --git a/tools/audit/seat/instruments/beat_jobs.py.md b/tools/audit/seat/instruments/beat_jobs.py.md
index f399272d5..505a36255 100644
--- a/tools/audit/seat/instruments/beat_jobs.py.md
+++ b/tools/audit/seat/instruments/beat_jobs.py.md
@@ -9,11 +9,12 @@
   `S/roster-drain.queue`, each exact line marked done, a refusal never
   retried, `hold <tree-path> <op>` released once main carries the path and
   `HOLD-STALE` after 24 h), `plan-beat` (`replan.py` then `state_docs.py
-  --push --mirror --plan`), `pulse` (into `S/beatd/pulse.txt`), `cancel-sweep`,
+  --push --mirror --plan`, then a `pages.yml` dispatch after a state push that
+  landed, so `plan_public.py` republishes the public page), `pulse` (into `S/beatd/pulse.txt`), `cancel-sweep`,
   `disk` (`worktree_gc.sh` under the floor), `opener` (one `open_driver.py
   --board` pass, its refusals and `STUCK` forwarded) `head-watch`
   (`HEAD-MOVED` events) and `audit-dispatch` (one `DISPATCH: planted-defect-audit
-  arm=<arm> cut=<span>` line per sustained `would-trip` of a guardrail arm, never twice while the arm stays tripped; a failed run's `UNREADABLE` clears on the next readable run). Each writes only actionable lines to
+  arm=<arm> cut=<span>` line per sustained `would-trip` of a guardrail arm, never twice while the arm stays tripped; a failed run's `UNREADABLE` clears on the next readable run) and `outside-intake` (`outside_intake.py list` from the overlay's `intake_since`, with a cursor under `state/`: its `OUTSIDE` lines). Each writes only actionable lines to
   `S/digest/jobs/<row>`; `fold` concatenates them into `S/digest/digest.txt`,
   diffs `new.txt` and `gone.txt`, and touches `new.stamp` only on a new line,
   so the orchestrator's one wake reads `new.stamp` and `events.txt`. A null
diff --git a/tools/audit/seat/instruments/outside_intake.py.md b/tools/audit/seat/instruments/outside_intake.py.md
new file mode 100644
index 000000000..afeae98b3
--- /dev/null
+++ b/tools/audit/seat/instruments/outside_intake.py.md
@@ -0,0 +1,23 @@
+# `outside_intake.py`
+
+- `outside_intake.py` — lists the submissions outside users make (issues, pull
+  requests, issue and review comments, discussions, by any author that is
+  neither ours nor a bot) since a cursor, and what each is owed this turn
+  (R10-OUTSIDE-INTAKE; tvofi, 2026-11-06). `list` prints `OUTSIDE #N
+  owed=triage|answer|reply ...` lines, read from the roster and the thread and
+  never from memory: on no roster group and not refused is `triage`; wired into
+  a group's `issues` or `fixes` (`roster_edit.py wire-issue`) and unanswered is
+  `answer` once the plan page answers; an outside comment newer than every one
+  of ours on a disposed thread is `reply`. `answer --issue N` posts the plan
+  page link (`plan_public.PLAN_URL`) through `tools/pr/gh_comment.py` with its
+  read-back; `refuse --issue N --reason-file F` posts a recorded refusal. Both
+  mark the thread, and only a mark in a comment of ours counts. When: the beat's
+  `outside-intake` row runs `list` each pass with `--cursor`, and the sweep acts
+  on its lines; `answer` is the dispatch seat's, `refuse` the orchestrator's.
+  Refusals: a failed read is `outside-intake: UNREADABLE`, rc 2, never a clean
+  board; `answer` refuses a thread already answered or refused (none is
+  answered twice), one on no roster group, one while the plan page does not
+  answer, and a discussion (answered by hand). `--self-test` drives the
+  round's three submissions (#3224, #3225, #3226) and their neighbours through
+  the real `jq` over faked API answers, and one mutant per predicate
+  (`outside_intake_selftest.py`).
diff --git a/tools/audit/seat/instruments/plan_public.py.md b/tools/audit/seat/instruments/plan_public.py.md
new file mode 100644
index 000000000..402d34ff2
--- /dev/null
+++ b/tools/audit/seat/instruments/plan_public.py.md
@@ -0,0 +1,17 @@
+# `plan_public.py`
+
+- `plan_public.py` — stages the ongoing round's plan page for the public site
+  (R10-OUTSIDE-INTAKE). `stage --out DIR` takes `PLAN.html` from the newest
+  `origin/handoff/audit-r<N>-plan` state ref (the layout `state_docs.state_of`
+  owns) and writes it as `DIR/plan/index.html`; `.github/workflows/pages.yml`
+  runs it from the dispatched ref's tree, then checks out the newest `v*` tag
+  for the docs, so the page is served at `plan/` beside the product page.
+  `url` prints `PLAN_URL`, the one spelling of the public address. When: inside
+  the Pages workflow, which the beat's `plan-beat` row dispatches after each
+  state push that landed; by hand, to see what would be published. Refusals:
+  rc 2 and nothing written when there is no state ref or no page at the newest
+  one (the workflow deploys without a plan and warns); rc 1 and nothing written
+  for a page that is not an HTML document or that `ref_privacy` reads a host
+  path, account name, uid, session scratch root or a tool's attribution in --
+  the deploy goes red rather than publish it. `--self-test` drives every arm
+  offline over a faked git.
diff --git a/tools/audit/seat/outside_intake.py b/tools/audit/seat/outside_intake.py
new file mode 100644
index 000000000..9e092aa90
--- /dev/null
+++ b/tools/audit/seat/outside_intake.py
@@ -0,0 +1,370 @@
+#!/usr/bin/env python3
+"""outside_intake.py -- the submissions outside users make, and what each is owed.
+
+    python3 -I tools/audit/seat/outside_intake.py list   [--repo O/R] --since ISO [--cursor FILE] [--roster FILE]
+    python3 -I tools/audit/seat/outside_intake.py answer [--repo O/R] --issue N [--roster FILE] [--dry-run]
+    python3 -I tools/audit/seat/outside_intake.py refuse [--repo O/R] --issue N --reason-file F [--dry-run]
+    python3 -I tools/audit/seat/outside_intake.py --self-test
+
+WHY THIS EXISTS (R10-OUTSIDE-INTAKE). The owner's ruling, tvofi 2026-11-06:
+"During future audit rounds, issues, PRs or other posts from outside users
+should be regularly checked, triaged/designed and planned. [...] When the plan
+html is done, and any outside submission is on the roster, the plan HTML should
+be linked in an answer to the outside submission." Three outside submissions
+(#3224, #3225, #3226) reached the round in one day and were found by hand.
+
+OUTSIDE is any author not in OURS and not a bot account (`user.type` Bot):
+a bot is not an outside user, ours or a third party's. THIS ENCODES A DESIGN
+CHOICE. A submission is one thread -- issue, pull request or discussion, one
+number space -- with outside activity at or after the cursor: the thread
+itself, an issue comment, a review comment, or a discussion comment.
+
+DISPOSITION, read from the roster and the thread, never from memory:
+  refused   a comment by OURS carrying REFUSED_MARK (posted by `refuse`);
+  on roster the number is in a roster group's `issues` or `fixes` (wired by
+            the roster seat's `roster_edit.py wire-issue`, the existing
+            mechanism -- a carry onto a group is wired the same way);
+  answered  on roster, and a comment by OURS carrying ANSWER_MARK.
+A marker in a comment by anyone else is not read: an outsider cannot dispose
+of their own submission, nor a third-party bot (one quoting a submitter's text)
+of anyone's; such a bot's comment is neither ours nor outside activity.
+
+LIST prints one line per submission owed this turn, rc 1 when any is, rc 0
+when none, rc 2 when a read failed (nothing printed but the UNREADABLE line):
+  OUTSIDE #N owed=triage <kind> by=<login> since=<utc>   on no roster group and
+      not refused: triage or design it (`proposal-triage.md`, `designer.md`),
+      then the roster seat wires it into a group, or `refuse`;
+  OUTSIDE #N owed=answer group=<G> ...  on the roster, unanswered, and the
+      plan page answers 200: the dispatch seat runs `answer`;
+  OUTSIDE #N owed=reply ...   answered or refused, and an outside comment is
+      newer than every comment of ours: read it and reply;
+  OUTSIDE plan-page UNAVAILABLE <why>; <k> answer(s) wait   once, while the
+      plan page does not answer and a submission on the roster waits for it.
+With `--cursor`, the scan starts at the cursor's `since` (else `--since`), and
+a readable pass moves it to the earliest activity of any submission still
+owed, else to the pass's start: a submission never drops out while owed.
+
+ANSWER posts, through `tools/pr/gh_comment.py post` (its read-back is the
+proof), the plan page link to a submission on the roster. Refusals, rc 1 and
+nothing posted: the thread has no outside activity, it is already answered or
+refused (so none is answered twice), it is on no roster group, the plan page
+does not answer, or it is a discussion (answered by hand: gh_comment posts
+issue comments only). REFUSE posts the reason file under REFUSED_MARK, with
+the same already-disposed refusal.
+"""
+from __future__ import annotations
+
+import argparse
+import json
+import os
+import subprocess
+import sys
+import tempfile
+import time
+import urllib.request
+from pathlib import Path
+
+HERE = Path(__file__).resolve().parent
+sys.path.insert(0, str(HERE))
+import plan_public  # noqa: E402
+import roster_lib  # noqa: E402
+
+#: Our accounts (CLAUDE.md, Identity): the owner, the retired seat account, and
+#: the Apps, though every bot is already not outside by its type.
+OURS = frozenset({"tvofi", "tvofi-seat-author", "hpo-author[bot]", "hpo-approver[bot]",
+                  "hpo-runs[bot]", "github-actions[bot]"})
+ANSWER_MARK = "<!-- outside-intake:answered -->"
+REFUSED_MARK = "<!-- outside-intake:refused -->"
+REPO_ROOT = HERE.parents[2]
+DEFAULT_REPO = "tvofi/heatpump_optimizer"
+
+_ISSUE = ('.[] | {n: .number, login: (.user.login // "ghost"), type: (.user.type // "User"), '
+          'at: .created_at, kind: (if .pull_request then "pr" else "issue" end)}')
+_COMMENT = ('.[] | {n: (.{url} | split("/") | last | tonumber), login: (.user.login // "ghost"), '
+            'type: (.user.type // "User"), at: .created_at}')
+_THREAD = ('.[] | {login: (.user.login // "ghost"), type: (.user.type // "User"), at: .created_at, '
+           f'answered: (.body | contains("{ANSWER_MARK}")), refused: (.body | contains("{REFUSED_MARK}"))}}')
+_DISCUSSIONS = """query($owner: String!, $name: String!) { repository(owner: $owner, name: $name) {
+  discussions(first: 100, orderBy: {field: UPDATED_AT, direction: DESC}) { nodes {
+    number createdAt author { login __typename }
+    comments(first: 100) { nodes { createdAt body author { login __typename } } } } } } }"""
+
+
+class Unreadable(Exception):
+    pass
+
+
+def gh(argv: list[str]) -> tuple[int, str]:
+    p = subprocess.run(["gh", *argv], capture_output=True, text=True)
+    return p.returncode, p.stdout
+
+
+def plan_live(url: str = plan_public.PLAN_URL) -> tuple[bool, str]:
+    try:
+        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=20) as r:
+            return r.status == 200, f"HTTP {r.status}"
+    except Exception as e:  # any failure to read is "not live", said with its reason
+        return False, type(e).__name__
+
+
+def outside(login: str, typ: str) -> bool:
+    return login not in OURS and typ != "Bot"
+
+
+def rows(run, argv: list[str]) -> list[dict]:
+    rc, out = run(argv)
+    if rc != 0:
+        raise Unreadable(f"gh {' '.join(argv[:2])} rc={rc}")
+    return [json.loads(ln) for ln in out.splitlines() if ln.strip()]
+
+
+class Thread:
+    def __init__(self, n: int, kind: str = "comment"):
+        self.n, self.kind, self.by, self.first, self.last_out = n, kind, set(), "", ""
+        self.answered = self.refused = self.last_ours = ""
+
+    def saw(self, login: str, at: str) -> None:
+        self.by.add(login)
+        self.first = min(self.first or at, at)
+        self.last_out = max(self.last_out, at)
+
+    def mark(self, c: dict) -> None:
+        """A comment of the thread: ours marks it, and no other moves anything here.
+
+        Outside activity reaches `last_out` through `saw` alone: `one_thread` passes it
+        every outside comment, and one `scan` skips predates the activity that opened
+        the thread, so cannot raise its maximum. A third-party bot's is neither."""
+        if c["login"] not in OURS:
+            return
+        self.last_ours = max(self.last_ours, c["at"])
+        if c.get("answered"):
+            self.answered = max(self.answered, c["at"])
+        if c.get("refused"):
+            self.refused = max(self.refused, c["at"])
+
+
+def discussions(run, repo: str) -> list[dict]:
+    """Each discussion as {n, at, login, type, comments: [...]}, [] when the repository has none."""
+    rc, out = run(["api", f"repos/{repo}", "--jq", ".has_discussions"])
+    if rc != 0:
+        raise Unreadable(f"gh api repos/{repo} rc={rc}")
+    if out.strip() != "true":
+        return []
+    owner, name = repo.split("/", 1)
+    rc, out = run(["api", "graphql", "-f", f"query={_DISCUSSIONS}", "-F", f"owner={owner}", "-F", f"name={name}"])
+    if rc != 0:
+        raise Unreadable(f"gh api graphql rc={rc}")
+    def who(a: dict | None) -> tuple[str, str]:
+        """(login, type) as the REST API spells them: GraphQL names a bot without its `[bot]` suffix."""
+        login, typ = (a or {}).get("login") or "ghost", "Bot" if (a or {}).get("__typename") == "Bot" else "User"
+        if typ == "Bot":
+            login = f"{login}[bot]"
+        return login, typ
+
+    res = []
+    for d in json.loads(out)["data"]["repository"]["discussions"]["nodes"]:
+        login, typ = who(d.get("author"))
+        cs = [{"login": who(c.get("author"))[0], "type": who(c.get("author"))[1], "at": c["createdAt"],
+               "answered": ANSWER_MARK in c["body"], "refused": REFUSED_MARK in c["body"]}
+              for c in d["comments"]["nodes"]]
+        res.append({"n": d["number"], "at": d["createdAt"], "login": login, "type": typ, "comments": cs})
+    return res
+
+
+def scan(run, repo: str, since: str) -> dict[int, Thread]:
+    """Every thread with outside activity at or after `since`, its comments read for our marks."""
+    threads: dict[int, Thread] = {}
+
+    def saw(n: int, kind: str | None, login: str, typ: str, at: str) -> None:
+        if at >= since and outside(login, typ):
+            t = threads.setdefault(n, Thread(n))
+            if kind:
+                t.kind = kind
+            t.saw(login, at)
+
+    q = f"since={since}&per_page=100"
+    for r in rows(run, ["api", "--paginate", f"repos/{repo}/issues?state=all&{q}", "--jq", _ISSUE]):
+        saw(r["n"], r["kind"], r["login"], r["type"], r["at"])
+    for path, url in (("issues/comments", "issue_url"), ("pulls/comments", "pull_request_url")):
+        for r in rows(run, ["api", "--paginate", f"repos/{repo}/{path}?{q}", "--jq",
+                            _COMMENT.replace("{url}", url)]):
+            saw(r["n"], None, r["login"], r["type"], r["at"])
+    disc = {d["n"]: d for d in discussions(run, repo)}
+    for d in disc.values():
+        saw(d["n"], "discussion", d["login"], d["type"], d["at"])
+        for c in d["comments"]:
+            saw(d["n"], None, c["login"], c["type"], c["at"])
+    for t in threads.values():
+        cs = disc[t.n]["comments"] if t.n in disc else rows(
+            run, ["api", "--paginate", f"repos/{repo}/issues/{t.n}/comments?per_page=100", "--jq", _THREAD])
+        if t.n in disc:
+            t.kind = "discussion"
+        for c in cs:
+            t.mark(c)
+    return threads
+
+
+def one_thread(run, repo: str, n: int) -> Thread | None:
+    """Thread n read whole (its opening post and every comment), or None without outside activity.
+
+    A number the issues API does not know is a discussion (or nothing): it is
+    returned as a discussion when it has outside activity, so `dispose` refuses it."""
+    rc, out = run(["api", f"repos/{repo}/issues/{n}", "--jq", _ISSUE.replace(".[] | ", "")])
+    if rc != 0:
+        d = next((d for d in discussions(run, repo) if d["n"] == n), None)
+        if d is None:
+            return None
+        t = Thread(n, "discussion")
+        if outside(d["login"], d["type"]):
+            t.saw(d["login"], d["at"])
+        cs = d["comments"]
+    else:
+        r = json.loads(out)
+        t = Thread(n, r["kind"])
+        if outside(r["login"], r["type"]):
+            t.saw(r["login"], r["at"])
+        cs = rows(run, ["api", "--paginate", f"repos/{repo}/issues/{n}/comments?per_page=100", "--jq", _THREAD])
+        if r["kind"] == "pr":
+            cs += rows(run, ["api", "--paginate", f"repos/{repo}/pulls/{n}/comments?per_page=100", "--jq", _THREAD])
+    for c in cs:
+        if outside(c["login"], c["type"]):
+            t.saw(c["login"], c["at"])
+        t.mark(c)
+    return t if t.by else None
+
+
+def wired(roster: dict) -> dict[int, str]:
+    """Issue or pull-request number -> the first roster group whose `issues` or `fixes` holds it."""
+    out: dict[int, str] = {}
+    for g in roster.get("groups", []):
+        for n in [*(g.get("issues") or []), *(g.get("fixes") or [])]:
+            out.setdefault(n, g["group"])
+    return out
+
+
+def owed(t: Thread, groups: dict[int, str], live: bool) -> str | None:
+    """The thread's owed word this turn ('wait' while only the plan page holds it), or None."""
+    disposed = max(t.answered, t.refused)
+    if disposed:
+        return "reply" if t.last_out > max(disposed, t.last_ours) else None
+    if t.n in groups:
+        return "answer" if live else "wait"
+    return "triage"
+
+
+def load_roster(path: str | None) -> dict:
+    if path:
+        return roster_lib.load_roster_file(path)
+    repo = str(REPO_ROOT)
+    ref, _ = roster_lib.default_roster_ref(roster_lib.git_in(repo))
+    return roster_lib.show_roster(repo, ref)
+
+
+def listing(run, repo: str, since: str, roster: dict, live: tuple[bool, str], now: str) -> tuple[list[str], str]:
+    """(lines, next cursor)."""
+    threads, groups = scan(run, repo, since), wired(roster)
+    lines, waiting, keep = [], 0, now
+    for n in sorted(threads):
+        t = threads[n]
+        word = owed(t, groups, live[0])
+        if word is None:
+            continue
+        keep = min(keep, t.first)
+        if word == "wait":
+            waiting += 1
+            continue
+        group = f" group={groups[n]}" if n in groups else ""
+        lines.append(f"OUTSIDE #{n} owed={word}{group} {t.kind} by={','.join(sorted(t.by))} since={t.first}")
+    if waiting:
+        lines.append(f"OUTSIDE plan-page UNAVAILABLE {live[1]}; {waiting} answer(s) wait")
+    return lines, keep
+
+
+def post(repo: str, n: int, body: str, dry: bool, runner=subprocess.run) -> int:
+    d = tempfile.mkdtemp(prefix="outside-intake-")
+    f = Path(d) / "body.md"
+    f.write_text(body)
+    argv = [sys.executable, "-I", str(REPO_ROOT / "tools/pr/gh_comment.py"), "post", "--repo", repo,
+            "--issue", str(n), "--body-file", str(f)] + (["--dry-run"] if dry else [])
+    return runner(argv).returncode
+
+
+def answer_body(group: str) -> str:
+    return (f"{ANSWER_MARK}\nThank you for this submission. It is on the current round's plan as "
+            f"`{group}`. The plan page shows where that group stands and when it is expected to land, "
+            f"and is refreshed as the round runs: {plan_public.PLAN_URL}\n")
+
+
+def dispose(run, repo: str, n: int, roster: dict | None, live, body: str | None, dry: bool, poster=post) -> tuple[int, str]:
+    """Answer (body None) or refuse (body given) thread n; (rc, message)."""
+    t = one_thread(run, repo, n)
+    if t is None:
+        return 1, f"outside_intake: REFUSED: #{n} has no outside activity"
+    group = wired(roster or {}).get(n)
+    if t.refused or t.answered:
+        return 1, f"outside_intake: REFUSED: #{n} is already {'refused' if t.refused else 'answered'}"
+    if t.kind == "discussion":
+        return 1, f"outside_intake: REFUSED: #{n} is a discussion; answer it by hand"
+    if body is None:
+        if group is None:
+            return 1, f"outside_intake: REFUSED: #{n} is on no roster group; triage it first"
+        ok, why = live()
+        if not ok:
+            return 1, f"outside_intake: REFUSED: the plan page does not answer ({why})"
+        body = answer_body(group)
+    else:
+        body = f"{REFUSED_MARK}\n{body}"
+    rc = poster(repo, n, body, dry)
+    return rc, f"outside_intake: #{n} {'answered' if REFUSED_MARK not in body else 'refused'} rc={rc}"
+
+
+def utc(t: float | None = None) -> str:
+    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))
+
+
+def main(argv: list[str]) -> int:
+    if argv[:1] == ["--self-test"]:
+        import outside_intake_selftest  # the fixtures and cases live beside this file
+        return outside_intake_selftest.run()
+    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
+    sub = ap.add_subparsers(dest="cmd", required=True)
+    for name in ("list", "answer", "refuse"):
+        s = sub.add_parser(name)
+        s.add_argument("--repo", default=DEFAULT_REPO)
+        s.add_argument("--roster", help="a roster file; default: the round's roster ref (roster_lib)")
+        if name == "list":
+            s.add_argument("--since", required=True)
+            s.add_argument("--cursor", type=Path)
+        else:
+            s.add_argument("--issue", required=True, type=int)
+            s.add_argument("--dry-run", action="store_true")
+        if name == "refuse":
+            s.add_argument("--reason-file", required=True, type=Path)
+    a = ap.parse_args(argv)
+    try:
+        roster = load_roster(a.roster)
+        if a.cmd == "list":
+            since = a.since
+            if a.cursor and a.cursor.exists():
+                since = json.loads(a.cursor.read_text()).get("since") or since
+            lines, keep = listing(gh, a.repo, since, roster, plan_live(), utc())
+        else:
+            reason = a.reason_file.read_text() if a.cmd == "refuse" else None
+            if reason is not None and not reason.strip():
+                print("outside_intake: REFUSED: the reason file is empty", file=sys.stderr)
+                return 1
+            rc, msg = dispose(gh, a.repo, a.issue, roster, plan_live, reason, a.dry_run)
+            print(msg, file=sys.stderr if rc else sys.stdout)
+            return rc
+    except (Unreadable, roster_lib.RosterNotFound, OSError, ValueError, KeyError) as e:
+        print(f"outside-intake: UNREADABLE {type(e).__name__}: {e}")
+        return 2
+    if a.cursor:
+        a.cursor.parent.mkdir(parents=True, exist_ok=True)
+        a.cursor.write_text(json.dumps({"since": keep}) + "\n")
+    print("".join(ln + "\n" for ln in lines), end="")
+    return 1 if lines else 0
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/tools/audit/seat/outside_intake_selftest.py b/tools/audit/seat/outside_intake_selftest.py
new file mode 100644
index 000000000..6912e54df
--- /dev/null
+++ b/tools/audit/seat/outside_intake_selftest.py
@@ -0,0 +1,370 @@
+"""The fixtures, cases and mutants of outside_intake.py's self-test, kept beside it.
+
+Run through `outside_intake.py`'s own flag, which CI's governance workflow
+names. Offline: `gh` is a fake answering each endpoint from raw API-shaped
+fixtures, projected through the real `jq` with the instrument's own `--jq`
+expressions, so a projection that misreads the API fails here. The fixtures
+are the round's three outside submissions (tvofi 2026-11-06): #3224 (adopted
+via #3231, on the roster and answered), #3225 (design R10-COMBI-TANK, on the
+roster and unanswered) and #3226 (adopted via #3232, here on no roster group),
+plus the shapes around them: our own thread, a bot's pull request, an outside
+comment on our issue, a review comment, a forged marker, a third-party bot's marker
+and its later comment on an answered thread,
+our App's marker in a discussion, a refusal with and
+without a later outside reply, and a discussion. MUTANTS plants one edit per
+predicate in a temp copy and expects its named case to fail.
+"""
+from __future__ import annotations
+
+import contextlib
+import importlib.util
+import io
+import json
+import shutil
+import subprocess
+import sys
+import tempfile
+from pathlib import Path
+
+HERE = Path(__file__).resolve().parent
+SINCE = "2026-11-05T00:00:00Z"
+NOW = "2026-11-07T00:00:00Z"
+OUT = {"login": "Bankaifan", "type": "User"}
+ME = {"login": "tvofi", "type": "User"}
+
+
+def load(path: Path, name: str):
+    spec = importlib.util.spec_from_file_location(name, path)
+    mod = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(mod)
+    return mod
+
+
+def issue(n, user, at, pr=False):
+    d = {"number": n, "user": user, "created_at": at, "title": f"t{n}"}
+    if pr:
+        d["pull_request"] = {"url": f"x/pulls/{n}"}
+    return d
+
+
+def comment(n, user, at, body="", review=False):
+    key = "pull_request_url" if review else "issue_url"
+    return {key: f"https://api.github.com/repos/o/r/{'pulls' if review else 'issues'}/{n}",
+            "user": user, "created_at": at, "body": body}
+
+
+def world(m):
+    """The fixture repository, as raw API objects; m is the module under test (its markers)."""
+    issues = [
+        issue(3224, OUT, "2026-11-05T09:45:08Z", pr=True),
+        issue(3225, OUT, "2026-11-05T10:29:13Z"),
+        issue(3226, OUT, "2026-11-05T11:36:11Z", pr=True),
+        issue(3250, ME, "2026-11-05T12:00:00Z"),
+        issue(3251, {"login": "dependabot[bot]", "type": "Bot"}, "2026-11-05T12:30:00Z", pr=True),
+        issue(3252, {"login": "someone", "type": "User"}, "2026-11-05T13:00:00Z"),
+        issue(3253, {"login": "other", "type": "User"}, "2026-11-05T14:00:00Z"),
+        issue(3100, {"login": "old", "type": "User"}, "2026-10-01T00:00:00Z"),
+        issue(3240, {"login": "hpo-author[bot]", "type": "Bot"}, "2026-11-05T15:00:00Z", pr=True),
+    ]
+    comments = [
+        comment(3224, ME, "2026-11-06T05:07:57Z", m.ANSWER_MARK + "\nlanded through #3231"),
+        comment(3225, ME, "2026-11-06T21:11:33Z", "being investigated"),
+        comment(3226, OUT, "2026-11-06T06:00:00Z", m.ANSWER_MARK + " forged by the submitter"),
+        comment(3250, {"login": "visitor", "type": "User"}, "2026-11-06T07:00:00Z", "a question on our issue"),
+        comment(3252, ME, "2026-11-06T01:00:00Z", m.REFUSED_MARK + "\nout of scope"),
+        comment(3252, {"login": "someone", "type": "User"}, "2026-11-06T02:00:00Z", "but why?"),
+        comment(3253, ME, "2026-11-06T01:00:00Z", m.REFUSED_MARK + "\nout of scope"),
+        comment(3253, {"login": "other", "type": "User"}, "2026-11-06T02:00:00Z", "ok"),
+        comment(3253, ME, "2026-11-06T03:00:00Z", "noted"),
+        comment(3100, ME, "2026-11-06T04:00:00Z", "an old thread we touched"),
+    ]
+    reviews = [comment(3240, {"login": "reviewer-x", "type": "User"}, "2026-11-06T08:00:00Z", "nit", review=True)]
+    return {"issues": issues, "comments": comments, "reviews": reviews, "discussions": []}
+
+
+def roster():
+    return {"groups": [
+        {"group": "R10-ADOPTED-3231", "issues": [3224], "fixes": []},
+        {"group": "R10-COMBI-TANK", "issues": [3225]},
+        {"group": "R10-OTHER", "issues": ["3226"], "fixes": None},  # a string is not a wiring
+    ]}
+
+
+def jq(expr: str, data) -> str:
+    p = subprocess.run(["jq", "-c", expr], input=json.dumps(data), capture_output=True, text=True, check=True)
+    return p.stdout
+
+
+class Fake:
+    """`gh`, answering from a world; records every argv; `fail` names an endpoint fragment that errors."""
+
+    def __init__(self, w, fail: str | None = None):
+        self.w, self.fail, self.calls = w, fail, []
+
+    def __call__(self, argv):
+        self.calls.append(list(argv))
+        path = argv[1] if argv[1] != "--paginate" else argv[2]
+        if self.fail and self.fail in " ".join(argv):
+            return 1, ""
+        expr = argv[argv.index("--jq") + 1] if "--jq" in argv else None
+        w = self.w
+        if path == "graphql":
+            nodes = [{"number": d["n"], "createdAt": d["at"], "author": {"login": d["login"], "__typename": d["type"]},
+                      "comments": {"nodes": [{"createdAt": c["at"], "body": c["body"],
+                                              "author": {"login": c["login"], "__typename": c["type"]}}
+                                             for c in d["comments"]]}} for d in w["discussions"]]
+            return 0, json.dumps({"data": {"repository": {"discussions": {"nodes": nodes}}}})
+        if path == "repos/o/r":
+            return 0, jq(expr, {"has_discussions": bool(w["discussions"])})
+        tail = path.split("?")[0][len("repos/o/r/"):]
+        if tail == "issues":
+            return 0, jq(expr, w["issues"])
+        if tail == "issues/comments":
+            return 0, jq(expr, w["comments"])
+        if tail == "pulls/comments":
+            return 0, jq(expr, w["reviews"])
+        parts = tail.split("/")
+        n = int(parts[1])
+        if parts[0] == "issues" and len(parts) == 2:
+            hit = [i for i in w["issues"] if i["number"] == n]
+            return (0, jq(expr, hit[0])) if hit else (1, "")
+        if parts[0] == "issues" and parts[2] == "comments":
+            return 0, jq(expr, [c for c in w["comments"] if c.get("issue_url", "").endswith(f"/{n}")])
+        if parts[0] == "pulls" and parts[2] == "comments":
+            return 0, jq(expr, [c for c in w["reviews"] if c["pull_request_url"].endswith(f"/{n}")])
+        raise AssertionError(f"unexpected gh call {argv}")
+
+
+class Poster:
+    def __init__(self):
+        self.posts = []
+
+    def __call__(self, repo, n, body, dry):
+        self.posts.append((n, body))
+        return 0
+
+
+LIVE, DOWN = (lambda: (True, "HTTP 200")), (lambda: (False, "URLError"))
+
+
+class Ran:
+    """subprocess.run for post(): records each argv and the body file's text, answers rc."""
+
+    def __init__(self, rc: int):
+        self.rc, self.argv, self.body = rc, [], None
+
+    def __call__(self, argv):
+        self.argv = list(argv)
+        self.body = Path(argv[argv.index("--body-file") + 1]).read_text()
+        return subprocess.CompletedProcess(argv, self.rc)
+
+
+def main_list(m, w, d: Path, since: str) -> tuple[int, list[str]]:
+    """m.main(["list", ...]) over world w with the cursor in d: (rc, printed lines). `gh` and the
+    plan probe are swapped on the module for the fake, the only seam main() reads them through."""
+    (d / "roster.json").write_text(json.dumps(roster()))
+    m.gh, m.plan_live = Fake(w), LIVE
+    out = io.StringIO()
+    with contextlib.redirect_stdout(out):
+        rc = m.main(["list", "--repo", "o/r", "--since", since, "--cursor", str(d / "c" / "cursor.json"),
+                     "--roster", str(d / "roster.json")])
+    return rc, out.getvalue().splitlines()
+
+
+def cases(m) -> dict[str, bool]:
+    res: dict[str, bool] = {}
+    w = world(m)
+    lines, keep = m.listing(Fake(w), "o/r", SINCE, roster(), LIVE(), NOW)
+    want = [
+        "OUTSIDE #3225 owed=answer group=R10-COMBI-TANK issue by=Bankaifan since=2026-11-05T10:29:13Z",
+        "OUTSIDE #3226 owed=triage pr by=Bankaifan since=2026-11-05T11:36:11Z",
+        "OUTSIDE #3240 owed=triage comment by=reviewer-x since=2026-11-06T08:00:00Z",
+        "OUTSIDE #3250 owed=triage comment by=visitor since=2026-11-06T07:00:00Z",
+        "OUTSIDE #3252 owed=reply issue by=someone since=2026-11-05T13:00:00Z",
+    ]
+    res["list: the fixture world gives exactly its owed lines (answered, bot, ours, old and replied-to threads silent)"] = (
+        lines == want)
+    res["list: a marker in the submitter's own comment disposes of nothing (#3226 owes triage)"] = any(
+        ln.startswith("OUTSIDE #3226 owed=triage") for ln in lines)
+    res["list: the cursor stays at the earliest owed submission's first outside activity"] = (
+        keep == "2026-11-05T10:29:13Z")
+    lines, keep = m.listing(Fake(w), "o/r", SINCE, roster(), DOWN(), NOW)
+    res["list: with the plan page down, an answer waits behind one UNAVAILABLE line and still holds the cursor"] = (
+        not any("#3225" in ln for ln in lines) and lines[-1] == "OUTSIDE plan-page UNAVAILABLE URLError; 1 answer(s) wait"
+        and keep == "2026-11-05T10:29:13Z")
+    empty = {"issues": [], "comments": [], "reviews": [], "discussions": []}
+    lines, keep = m.listing(Fake(empty), "o/r", SINCE, roster(), LIVE(), NOW)
+    res["list null: no outside activity prints nothing and moves the cursor to now"] = lines == [] and keep == NOW
+    lines, _ = m.listing(Fake(w), "o/r", "2026-11-06T09:00:00Z", roster(), LIVE(), NOW)
+    res["list: activity before the cursor is not re-read"] = lines == []
+    with tempfile.TemporaryDirectory() as d:
+        rc1, l1 = main_list(m, w, Path(d), SINCE)
+        cur = json.loads((Path(d) / "c" / "cursor.json").read_text())
+        rc2, l2 = main_list(m, w, Path(d), "2026-11-06T09:00:00Z")  # a later --since: the cursor must win
+        rc3, l3 = main_list(m, empty, Path(d), SINCE)
+    res["main list: rc 1 with owed lines, the cursor persisted at the earliest owed activity and read back next pass"] = (
+        rc1 == 1 and l1 == want and cur == {"since": "2026-11-05T10:29:13Z"} and rc2 == 1 and l2 == want)
+    res["main list null: no owed submission is rc 0 and prints nothing"] = rc3 == 0 and l3 == []
+    w4 = world(m)
+    w4["comments"].append(comment(3225, {"login": "renovate[bot]", "type": "Bot"}, "2026-11-06T22:00:00Z",
+                                  m.ANSWER_MARK + " quoted by a third-party App"))
+    lines, _ = m.listing(Fake(w4), "o/r", SINCE, roster(), LIVE(), NOW)
+    res["identity: a third-party bot's marker disposes of nothing (#3225 still owes the answer)"] = (
+        lines == want)
+    try:
+        m.listing(Fake(w, fail="issues/comments"), "o/r", SINCE, roster(), LIVE(), NOW)
+        res["list: a failed read is UNREADABLE, never a clean board"] = False
+    except m.Unreadable:
+        res["list: a failed read is UNREADABLE, never a clean board"] = True
+
+    p = Poster()
+    rc, msg = m.dispose(Fake(w), "o/r", 3225, roster(), LIVE, None, False, p)
+    body = p.posts[0][1] if p.posts else ""
+    res["answer: an unanswered submission on the roster gets the plan page link once, marked"] = (
+        rc == 0 and len(p.posts) == 1 and p.posts[0][0] == 3225 and body.startswith(m.ANSWER_MARK)
+        and m.plan_public.PLAN_URL in body and "`R10-COMBI-TANK`" in body)
+    w2 = world(m)
+    w2["comments"].append(comment(3225, {"login": "hpo-approver[bot]", "type": "Bot"}, "2026-11-06T22:00:00Z", body))
+    p = Poster()
+    rc, msg = m.dispose(Fake(w2), "o/r", 3225, roster(), LIVE, None, False, p)
+    lines, _ = m.listing(Fake(w2), "o/r", SINCE, roster(), LIVE(), NOW)
+    after = {}
+    for who in ({"login": "renovate[bot]", "type": "Bot"}, {"login": "Bankaifan", "type": "User"}):
+        w5 = world(m)
+        w5["comments"] += [w2["comments"][-1], comment(3225, who, "2026-11-06T23:00:00Z", "a later comment")]
+        after[who["type"]] = ([ln for ln in m.listing(Fake(w5), "o/r", SINCE, roster(), LIVE(), NOW)[0] if "#3225" in ln],
+                              m.owed(m.one_thread(Fake(w5), "o/r", 3225), m.wired(roster()), True))
+    res["identity: a third-party bot's comment after our answer owes nothing; an outsider's owes a reply"] = (
+        after["Bot"] == ([], None) and len(after["User"][0]) == 1 and " owed=reply " in after["User"][0][0]
+        and after["User"][1] == "reply")
+    for dry in (True, False):
+        r = Ran(0)
+        got = m.post("o/r", 3225, "the body\n", dry, r)
+        res[f"post: gh_comment.py post is run with the body file, --dry-run {'passed' if dry else 'absent'}, rc 0 kept"] = (
+            got == 0 and Path(r.argv[2]).relative_to(m.REPO_ROOT).as_posix() == "tools/pr/gh_comment.py"
+            and r.argv[3:9] == ["post", "--repo", "o/r", "--issue", "3225", "--body-file"]
+            and r.body == "the body\n" and (r.argv[10:] == ["--dry-run"] if dry else len(r.argv) == 10))
+    res["post: a failed gh_comment read-back (rc 1) is a non-zero answer"] = m.post("o/r", 3225, "b", False, Ran(1)) == 1
+    res["answer: an answered submission is refused and no longer listed (never answered twice)"] = (
+        rc == 1 and "already answered" in msg and not p.posts and not any("#3225" in ln for ln in lines))
+    for n, why, live in ((3226, "on no roster group", LIVE), (3225, "does not answer", DOWN),
+                         (3252, "already refused", LIVE), (3251, "no outside activity", LIVE),
+                         (9999, "no outside activity", LIVE)):
+        p = Poster()
+        rc, msg = m.dispose(Fake(w), "o/r", n, roster(), live, None, False, p)
+        res[f"answer: #{n} is refused ({why}) and nothing is posted"] = rc == 1 and why in msg and not p.posts
+    p = Poster()
+    rc, msg = m.dispose(Fake(w), "o/r", 3226, roster(), LIVE, "Not in scope: reason.\n", False, p)
+    res["refuse: the reason is posted under the refusal marker, and the thread is then silent"] = (
+        rc == 0 and p.posts and p.posts[0][1].startswith(m.REFUSED_MARK) and "reason" in p.posts[0][1])
+    pr = Poster()
+    rc, msg = m.dispose(Fake(w), "o/r", 3240, roster(), LIVE, "Not in scope: reason.\n", False, pr)
+    res["refuse: a pull request whose only outside activity is a review comment is refused, marked (#3240)"] = (
+        rc == 0 and len(pr.posts) == 1 and pr.posts[0][0] == 3240 and pr.posts[0][1].startswith(m.REFUSED_MARK))
+    w3 = world(m)
+    w3["comments"].append(comment(3226, ME, "2026-11-06T23:00:00Z", p.posts[0][1] if p.posts else ""))
+    lines, _ = m.listing(Fake(w3), "o/r", SINCE, roster(), LIVE(), NOW)
+    res["refuse: a refused submission owes nothing until the submitter writes again"] = not any(
+        "#3226" in ln for ln in lines)
+    wd = dict(empty, discussions=[{"n": 3260, "at": "2026-11-06T10:00:00Z", "login": "asker", "type": "User",
+                                   "comments": []}])
+    lines, _ = m.listing(Fake(wd), "o/r", SINCE, roster(), LIVE(), NOW)
+    p = Poster()
+    rc, msg = m.dispose(Fake(wd), "o/r", 3260, {"groups": [{"group": "G", "issues": [3260]}]}, LIVE, None, False, p)
+    res["discussions: an outside discussion is listed, and answering one is refused (by hand)"] = (
+        lines == ["OUTSIDE #3260 owed=triage discussion by=asker since=2026-11-06T10:00:00Z"]
+        and rc == 1 and "discussion" in msg and not p.posts)
+    wd = dict(empty, discussions=[{"n": 3261, "at": "2026-11-06T10:00:00Z", "login": "asker", "type": "User",
+                                   "comments": [{"login": "hpo-approver", "type": "Bot", "at": "2026-11-06T11:00:00Z",
+                                                 "body": m.REFUSED_MARK + " by our App"}]}])
+    lines, _ = m.listing(Fake(wd), "o/r", SINCE, roster(), LIVE(), NOW)
+    res["discussions: our App's marker is read (GraphQL names a bot without its [bot] suffix)"] = lines == []
+    res["identity: every account of ours and every bot is not outside; a stranger is"] = (
+        not any(m.outside(a, "User") for a in m.OURS) and not m.outside("renovate[bot]", "Bot")
+        and m.outside("Bankaifan", "User"))
+    return res
+
+
+#: (old, new, the case that must fail). Each old string appears once in outside_intake.py.
+MUTANTS = {
+    "bots_outside": ('return login not in OURS and typ != "Bot"', "return login not in OURS",
+                     "identity: every account of ours and every bot is not outside; a stranger is"),
+    "forged_marker_read": ('        if c["login"] not in OURS:\n            return\n', '        if c["login"] not in OURS:\n            pass\n',
+                           "list: a marker in the submitter's own comment disposes of nothing (#3226 owes triage)"),
+    "since_ignored": ("        if at >= since and outside(login, typ):", "        if outside(login, typ):",
+                      "list: activity before the cursor is not re-read"),
+    "answer_twice": ("    if t.refused or t.answered:", "    if t.refused:",
+                     "answer: an answered submission is refused and no longer listed (never answered twice)"),
+    "unwired_answered": ("        if group is None:\n", "        if False:\n", "answer: #3226 is refused (on no roster group) and nothing is posted"),
+    "plan_down_answers": ('        return "answer" if live else "wait"', '        return "answer"',
+                          "list: with the plan page down, an answer waits behind one UNAVAILABLE line and still holds the cursor"),
+    "reply_never": ('        return "reply" if t.last_out > max(disposed, t.last_ours) else None', "        return None",
+                    "list: the fixture world gives exactly its owed lines (answered, bot, ours, old and replied-to threads silent)"),
+    "cursor_jumps": ("        keep = min(keep, t.first)\n", "",
+                     "list: the cursor stays at the earliest owed submission's first outside activity"),
+    "review_comments_unread": ('(("issues/comments", "issue_url"), ("pulls/comments", "pull_request_url"))',
+                               '(("issues/comments", "issue_url"),)',
+                               "list: the fixture world gives exactly its owed lines (answered, bot, ours, old and replied-to threads silent)"),
+    "one_thread_pr_reviews_drop": ('        if r["kind"] == "pr":\n', "        if False:\n",
+                                   "refuse: a pull request whose only outside activity is a review comment is refused, marked (#3240)"),
+    "unreadable_swallowed": ('        raise Unreadable(f"gh {\' \'.join(argv[:2])} rc={rc}")', "        return []",
+                             "list: a failed read is UNREADABLE, never a clean board"),
+    "marker_any_bot": ('        if c["login"] not in OURS:\n', '        if outside(c["login"], c["type"]):\n',
+                       "identity: a third-party bot's marker disposes of nothing (#3225 still owes the answer)"),
+    "thirdbot_moves_out": ('        if c["login"] not in OURS:\n            return\n',
+                           '        if c["login"] not in OURS:\n            self.last_out = max(self.last_out, c["at"])\n            return\n',
+                           "identity: a third-party bot's comment after our answer owes nothing; an outsider's owes a reply"),
+    "graphql_bot_suffix": ('        login = f"{login}[bot]"\n', "        pass\n",
+                           "discussions: our App's marker is read (GraphQL names a bot without its [bot] suffix)"),
+    "main_cursor_unread": ('                since = json.loads(a.cursor.read_text()).get("since") or since\n',
+                           "                pass\n",
+                           "main list: rc 1 with owed lines, the cursor persisted at the earliest owed activity and read back next pass"),
+    "main_cursor_now": ('json.dumps({"since": keep})', 'json.dumps({"since": utc()})',
+                        "main list: rc 1 with owed lines, the cursor persisted at the earliest owed activity and read back next pass"),
+    "main_list_rc0": ("    return 1 if lines else 0\n", "    return 0\n",
+                      "main list: rc 1 with owed lines, the cursor persisted at the earliest owed activity and read back next pass"),
+    "post_rc_dropped": ("    return runner(argv).returncode\n", "    runner(argv)\n    return 0\n",
+                        "post: a failed gh_comment read-back (rc 1) is a non-zero answer"),
+    "post_dry_dropped": (' + (["--dry-run"] if dry else [])', "",
+                         "post: gh_comment.py post is run with the body file, --dry-run passed, rc 0 kept"),
+    "post_wrong_script": ('"tools/pr/gh_comment.py"', '"tools/pr/gh_comment_missing.py"',
+                          "post: gh_comment.py post is run with the body file, --dry-run absent, rc 0 kept"),
+    "discussion_answered": ('        return 1, f"outside_intake: REFUSED: #{n} is a discussion; answer it by hand"', "        pass",
+                            "discussions: an outside discussion is listed, and answering one is refused (by hand)"),
+}
+
+
+def run(mutants: bool = True) -> int:
+    if not shutil.which("jq"):
+        print("outside_intake self-test: REFUSED: no jq on PATH; the projections cannot be driven")
+        return 1
+    import outside_intake as m
+    res = cases(m)
+    for name, ok in res.items():
+        print(f"{'ok  ' if ok else 'FAIL'} {name}")
+    fails = [n for n, ok in res.items() if not ok]
+    if mutants:
+        src = (HERE / "outside_intake.py").read_text()
+        for mid, (old, new, case) in MUTANTS.items():
+            if src.count(old) != 1 or case not in res:
+                fails.append(f"mutant {mid} is stale (old string x{src.count(old)}, case known={case in res})")
+                print(f"FAIL mutant {mid}: stale")
+                continue
+            with tempfile.TemporaryDirectory() as d:
+                p = Path(d) / "tools" / "audit" / "seat" / "outside_intake.py"  # the module's own depth
+                p.parent.mkdir(parents=True)
+                p.write_text(src.replace(old, new))
+                try:
+                    killed = not cases(load(p, f"oi_mutant_{mid}"))[case]
+                except Exception as e:  # a crash is reported, never counted as a kill
+                    print(f"FAIL mutant {mid}: crashed the cases ({type(e).__name__})")
+                    fails.append(f"mutant {mid} crashed")
+                    continue
+            print(f"{'ok  ' if killed else 'FAIL'} mutant {mid} killed by: {case}")
+            if not killed:
+                fails.append(f"mutant {mid} survived")
+    if fails:
+        print(f"{len(fails)} self-test check(s) failed: " + "; ".join(fails))
+        return 1
+    print("outside_intake self-test: all checks passed")
+    return 0
diff --git a/tools/audit/seat/plan_public.py b/tools/audit/seat/plan_public.py
new file mode 100644
index 000000000..a40047893
--- /dev/null
+++ b/tools/audit/seat/plan_public.py
@@ -0,0 +1,200 @@
+#!/usr/bin/env python3
+"""plan_public.py -- stage the ongoing round's plan page for the public site.
+
+    python3 -I tools/audit/seat/plan_public.py stage --out DIR [--repo DIR]
+    python3 -I tools/audit/seat/plan_public.py url
+    python3 -I tools/audit/seat/plan_public.py --self-test
+
+WHY THIS EXISTS (R10-OUTSIDE-INTAKE; tvofi, 2026-11-06: "the plan html for an
+ongoing round should be made publically available from a suitable place in the
+developer documentation"). `state_docs.py --plan` commits the round's plan page
+as `PLAN.html` to the orphan state ref, where GitHub serves it only as source.
+The Pages workflow (`.github/workflows/pages.yml`) runs `stage` from the
+dispatched ref's tree before it checks out the release, and copies what it
+writes into the site, so the page is served at PLAN_URL beside the product
+page. The beat's `plan-beat` row dispatches that workflow after each push of
+the state ref that carried a new page, so the public page refreshes at each
+sweep that moved the plan.
+
+STAGE reads the remote-tracking state refs (`origin/handoff/audit-r<N>-plan`,
+the layout `state_docs.state_of` owns), takes the highest round N's PLAN.html
+and writes it as `<out>/plan/index.html`. Nothing to publish, rc 2 and nothing
+written: no state ref, or no PLAN.html at the newest one (between rounds: the
+workflow deploys the site without a plan and warns). Refusals, rc 1 and nothing
+written, which turn the deploy red: a page that is not an HTML document, and a page `ref_privacy` reads a host path, account name, uid or
+session scratch root in, or a tool's attribution -- a public page carries
+none of them. The UNAVAILABLE page `plan_page.py` writes over a stale plan is
+an HTML document and is published as it is: the honest page, never the last
+good one dressed as current.
+
+URL prints PLAN_URL, the one place the public address is spelled; the
+developer documentation and `outside_intake.py`'s answers link it.
+"""
+from __future__ import annotations
+
+import argparse
+import re
+import subprocess
+import sys
+import tempfile
+from pathlib import Path
+
+sys.path.insert(0, str(Path(__file__).resolve().parent))
+import ref_privacy  # noqa: E402
+import state_docs  # noqa: E402
+
+PAGES_URL = "https://tvofi.github.io/heatpump_optimizer/"
+PLAN_DIR = "plan"
+PLAN_URL = f"{PAGES_URL}{PLAN_DIR}/"
+_STATE_REF = re.compile(r"^refs/remotes/origin/handoff/audit-r(\d+)-plan$")
+_HTML = re.compile(r"^\s*<!doctype html", re.I)
+
+
+def git(repo: Path, *args: str) -> tuple[int, str]:
+    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
+    return p.returncode, p.stdout
+
+
+def newest_round(refnames: list[str]) -> int | None:
+    rounds = [int(m[1]) for r in refnames if (m := _STATE_REF.match(r.strip()))]
+    return max(rounds) if rounds else None
+
+
+def refusal(text: str, ident=None) -> str | None:
+    """Why `text` may not be published as the public plan page, or None."""
+    if not _HTML.match(text):
+        return "not an HTML document"
+    why = ref_privacy.leaks(text, ident or ref_privacy.Identity.of_host()) + ref_privacy.attribution(text)
+    return f"{', '.join(why)} in the page" if why else None
+
+
+def stage(repo: Path, out: Path, run=git, ident=None) -> tuple[int, str]:
+    rc, refs = run(repo, "for-each-ref", "--format=%(refname)", "refs/remotes/origin/handoff/")
+    n = newest_round(refs.splitlines()) if rc == 0 else None
+    if n is None:
+        return 2, "plan_public: NOTHING TO PUBLISH: no origin/handoff/audit-r<N>-plan ref; fetch the state refs first"
+    st = state_docs.state_of(n)
+    rc, text = run(repo, "show", f"refs/remotes/origin/{st.ref}:{st.dir}/{state_docs.PLAN_PAGE}")
+    if rc != 0 or not text:
+        return 2, f"plan_public: NOTHING TO PUBLISH: no {state_docs.PLAN_PAGE} at origin/{st.ref}"
+    why = refusal(text, ident)
+    if why:
+        return 1, f"plan_public: REFUSED: round {n} {state_docs.PLAN_PAGE}: {why}"
+    dest = out / PLAN_DIR / "index.html"
+    dest.parent.mkdir(parents=True, exist_ok=True)
+    dest.write_text(text)
+    return 0, f"plan_public: round {n} {state_docs.PLAN_PAGE} from origin/{st.ref} -> {PLAN_DIR}/index.html"
+
+
+#: (old, new, the check that must fail). Each old string appears once in this file.
+MUTANTS = {
+    "string_order": ("    rounds = [int(m[1]) for r", "    rounds = [m[1] for r",
+                     "the newest round is the highest N, by number, never by string order (10 > 9)"),
+    "leak_published": ("    why = refusal(text, ident)\n", "    why = None\n",
+                       "refused, rc 1 and nothing written: a page naming a home directory"),
+    "attribution_published": (" + ref_privacy.attribution(text)\n", "\n",
+                              "refused, rc 1 and nothing written: a page carrying a tool's attribution"),
+    "absent_refused_red": ('        return 2, f"plan_public: NOTHING TO PUBLISH: no {state_docs', '        return 1, f"plan_public: NOTHING TO PUBLISH: no {state_docs',
+                           "nothing to publish, rc 2 and nothing written: no PLAN.html at the newest ref (an older round's is never taken)"),
+}
+
+
+def self_test(mutants: bool = True) -> int:
+    fails: list[str] = []
+
+    def check(name: str, ok: bool) -> None:
+        print(f"{'ok  ' if ok else 'FAIL'} {name}")
+        if not ok:
+            fails.append(name)
+
+    page = "<!doctype html><html><body>plan</body></html>\n"
+    refs = ("refs/remotes/origin/handoff/audit-r9-plan\nrefs/remotes/origin/handoff/audit-r10-plan\n"
+            "refs/remotes/origin/handoff/audit-r10-roster\nrefs/remotes/origin/handoff/audit-r11-planx\n")
+    ident = ref_privacy.Identity.made({"/ho" + "me/alice"}, {"alice"}, 1234, {"box"})
+
+    def fake(pages: dict, refs_out: str = refs):
+        def run(repo, *args):
+            if args[0] == "for-each-ref":
+                return 0, refs_out
+            return (0, pages[args[1]]) if args[1] in pages else (128, "")
+        return run
+
+    want = f"refs/remotes/origin/handoff/audit-r10-plan:handoff/round10/state/{state_docs.PLAN_PAGE}"
+    check("the newest round is the highest N, by number, never by string order (10 > 9)",
+          newest_round(refs.splitlines()) == 10)
+    with tempfile.TemporaryDirectory() as d:
+        out = Path(d)
+        rc, msg = stage(out, out, fake({want: page}), ident)
+        got = (out / "plan" / "index.html").read_text() if (out / "plan" / "index.html").exists() else None
+        check("a clean page at the newest state ref is staged as plan/index.html, rc 0", rc == 0 and got == page)
+    for name, (pages, refs_out) in {
+            "no state ref at all": ({}, "refs/remotes/origin/main\n"),
+            "no PLAN.html at the newest ref (an older round's is never taken)":
+                ({want.replace("r10", "r9").replace("round10", "round9"): page}, refs)}.items():
+        with tempfile.TemporaryDirectory() as d:
+            out = Path(d)
+            rc, msg = stage(out, out, fake(pages, refs_out), ident)
+            check(f"nothing to publish, rc 2 and nothing written: {name}",
+                  rc == 2 and "NOTHING TO PUBLISH" in msg and not (out / "plan").exists())
+    cases = {
+        "a page that is not an HTML document": ({want: "plan: 3 groups\n"}, refs),
+        "a page naming a home directory": ({want: page.replace("plan", "/ho" + "me/alice/wt/plan")}, refs),
+        "a page naming a session scratch root": ({want: page.replace("plan", "/t" + "mp/claude-" + "1234/x")}, refs),
+        "a page carrying a tool's attribution": ({want: page + "Co-Authored-By: " + "Claude <x@y>\n"}, refs),
+    }
+    for name, (pages, refs_out) in cases.items():
+        with tempfile.TemporaryDirectory() as d:
+            out = Path(d)
+            rc, msg = stage(out, out, fake(pages, refs_out), ident)
+            check(f"refused, rc 1 and nothing written: {name}",
+                  rc == 1 and "REFUSED" in msg and not (out / "plan").exists())
+    check("PLAN_URL is under the Pages site and ends in the staged directory",
+          PLAN_URL.startswith(PAGES_URL) and PLAN_URL.endswith(f"/{PLAN_DIR}/"))
+    if mutants:
+        import importlib.util
+        # the code under mutation sits above the table, which spells every old string again
+        code, mark, rest = Path(__file__).read_text().partition("#: (old, new, the check")
+        for mid, (old, new, case) in MUTANTS.items():
+            if code.count(old) != 1:
+                check(f"mutant {mid} applies (old string x{code.count(old)})", False)
+                continue
+            with tempfile.TemporaryDirectory() as d:
+                mp = Path(d) / "plan_public.py"
+                mp.write_text(code.replace(old, new) + mark + rest)
+                spec = importlib.util.spec_from_file_location(f"pp_mutant_{mid}", mp)
+                mod = importlib.util.module_from_spec(spec)
+                spec.loader.exec_module(mod)
+                out = __import__("io").StringIO()
+                saved, sys.stdout = sys.stdout, out
+                try:
+                    mod.self_test(mutants=False)
+                finally:
+                    sys.stdout = saved
+            check(f"mutant {mid} killed by: {case}", f"FAIL {case}" in out.getvalue())
+    if fails:
+        print(f"{len(fails)} self-test check(s) failed: " + ", ".join(fails))
+        return 1
+    print("plan_public self-test: all checks passed")
+    return 0
+
+
+def main(argv: list[str]) -> int:
+    if argv[:1] == ["--self-test"]:
+        return self_test()
+    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
+    sub = ap.add_subparsers(dest="cmd", required=True)
+    s = sub.add_parser("stage")
+    s.add_argument("--out", required=True, type=Path)
+    s.add_argument("--repo", type=Path, default=Path.cwd())
+    sub.add_parser("url")
+    a = ap.parse_args(argv)
+    if a.cmd == "url":
+        print(PLAN_URL)
+        return 0
+    rc, msg = stage(a.repo, a.out)
+    print(msg, file=sys.stderr if rc else sys.stdout)
+    return rc
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/tools/audit/seat/sweep_template.md b/tools/audit/seat/sweep_template.md
index 139293ef5..f39b9d02e 100644
--- a/tools/audit/seat/sweep_template.md
+++ b/tools/audit/seat/sweep_template.md
@@ -48,6 +48,7 @@ rendered text that no overlay value supplied.
 | `disk_floor_gib` | free GiB on `/` below which finished worktrees are cleaned |
 | `seat_queues` | `pulse.py`'s `--seat-queue SEAT=FILE` arguments, one per standing seat's session queue file |
 | `seat_alives` | optional: `SEAT=FILE[:MIN]` entries, one per standing seat the session runs, whitespace-separated or a JSON list; each renders as `pulse.py --seat-alive ENTRY` (`FILE.d/<id>` holds the per-process entries). A seat listed with no alive file reads `UNREADABLE`, never skipped; none listed leaves the flag out |
+| `intake_since` | the UTC time the outside intake starts from (the round's opening); the beat's `outside-intake` row keeps its own cursor past it |
 | `launch_ledger` | optional: the launch ledger file (`<ts> <nonce> <role> ...` and `<ts> <nonce> stop` lines) for `pulse.py --launch-ledger`; empty leaves the flag out |
 
 <!-- sweep:begin -->
@@ -75,6 +76,8 @@ ORCHESTRATOR SWEEP, round {{round}}, repository {{repo}}. Read {{seat_ledger}} f
 
 (5) Tick watcher. If {{tick_alive}} is missing or older than {{tick_stale_min}} minutes, the tick seat has died: start a new one in the background on `dev/governance/roles/standing-tick.md`, whose prompt is the contents of {{tick_brief}}; it runs `tools/audit/seat/orchestrator_tick.py`. Log the restart in {{seat_ledger}}. Read {{digest}}/digest.txt whole, never truncated: the beat's `tick-digest` row writes there the board {{tick_log}}'s actionable family, every `OWED`, `REVIEW OWED`, `DISPATCH:`, `OWNER FLAG:` and `DESIGN-BUILD:` line among it, and its `owed-check` row the `UNACTIONED` lines of `tools/audit/seat/owed_unactioned.py`, which runs there once per sweep and never by hand (it counts every run as a sweep). Give every line an action this sweep, and print `grep -c '^-> ' {{tick_log}}` and `grep -c 'OWED' {{tick_log}}` beside the actions taken: an `OWED` line is a level re-printed every pass, not a diff (`dev/governance/roles/standing-tick.md`); the tick only lists, the sweep acts (`tools/audit/seat/INSTRUMENTS.md`, `orchestrator_tick.py`). A disposition that defers a line to a seat names that seat's ledger id or PID, and the next sweep re-checks it; one naming no seat is not a disposition. The `pulse.py` lines step (1b) printed name each consumer whose owed input is waiting on it (opener, verdict router or train, state beat, a standing seat's queue): drive that consumer before the rest of the sweep, and log it in {{seat_ledger}}; `UNREADABLE` is not a clean board. Each `UNACTIONED` line gets its action this sweep, or an `OWED-ACK` line in {{seat_ledger}} naming its next action and what it waits on; an acknowledgement lapses after its ttl, so the next sweep re-checks the handling. The sweep is not done while the digest holds an `UNACTIONED` line, and `owed-check: UNREADABLE` is never clean (`dev/audit/rca/R10-RCA-OWED-UNACTIONED.md`).
 
+(5b) Outside intake. The beat's `outside-intake` row runs `tools/audit/seat/outside_intake.py list --since {{intake_since}}` with its cursor and writes its `OUTSIDE` lines to {{digest}}/digest.txt (`dev/governance/roles/orchestrator.md` section 5): an `owed=triage` line gets a triage or design seat this sweep and ends wired into a roster group through the roster seat or refused with `outside_intake.py refuse`; an `owed=answer` line is queued to the dispatch seat, which runs `outside_intake.py answer`; an `owed=reply` line is read and answered; `OUTSIDE plan-page UNAVAILABLE` is the public plan page not answering (the `plan-beat` row's Pages dispatch, `tools/audit/seat/plan_public.py`).
+
 (6) Verdicts and CI. Read any moved `review/*` or `probe/*` refs and the cloud runs; confirm each verdict at its exact head with `tools/audit/seat/bus.sh confirm` (`dev/governance/roles/nudge.md` step 1). A red required check at an open head goes back to its fixer with the line `tools/audit/seat/failure_logs.sh` prints (`dev/governance/roles/nudge.md` steps 4 and 15).
 
 (7) Proposals. A process, tooling or instrument proposal this sweep met (a seat's result, a verdict's optimisation note, your own) is sent to triage on `dev/governance/roles/proposal-triage.md`, never implemented or routed before its ruling; an ACCEPT reaches the roster through the roster seat, citing its ruling.

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
