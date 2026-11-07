# Review packet #3288
head: 35fc2646348b9c4d69a3b56b6452ff4075289807
base: b4ec2f332fe3ab8dcf169bd3066276d3bb8848ab

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=128448394662 success
arch-score / arch-score id=128498740990 success
arm id=128444264975 skipped
budget-raise-gate / budget-raise-gate id=128498773207 success
cancel-superseded id=128498773893 success
codeql id=128498770188 skipped
codeql / Analyze (actions) id=128492842024 success
codeql / Analyze (javascript-typescript) id=128492820154 success
codeql / Analyze (python) id=128492850145 success
gate id=128498740508 success
governance id=128498772353 skipped
governance / delivery-status id=128492853951 success
governance / delivery-status-publish id=128492856644 skipped
governance / env-matrix id=128492856590 success
governance / instrument-self-tests id=128492820087 success
governance / policy-docs id=128492848046 success
governance / record id=128492819648 skipped
governance / wave-script id=128492846409 success
hassfest id=128498763389 skipped
hassfest / hassfest id=128492855907 success
kernel-points id=128498777605 skipped
pr-contract id=128498741379 skipped
pr-contract / pr-contract id=128498295968 success
prelude id=128498740478 success
refresh id=128498740730 success
tests id=128498741027 skipped
tests / arch-instrument id=128492820578 success
tests / briefs id=128492819982 success
tests / browser id=128492820768 success
tests / ci-ratchet id=128495970644 skipped
tests / claims-autofix id=128492821208 skipped
tests / closure-scope id=128492846229 success
tests / closures id=128492820315 success
tests / closures-autofix id=128492820817 skipped
tests / coverage id=128492818833 success
tests / coverage-ratchet id=128495969221 success
tests / fast (3.14) id=128492820145 success
tests / graders-head-copy id=128495969147 success
tests / lane-proofs id=128495969241 success
tests / mutation id=128492819762 success
tests / mutation-autofix id=128492820603 skipped
tests / mutation-pins id=128492820954 skipped
tests / nightly-ha id=128492820663 skipped
tests / nightly-status id=128492818270 success
tests / replay id=128492820611 skipped
tests / typing id=128492820690 success
validate id=128498776355 skipped
validate / validate-hacs id=128492859933 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub python3 tools/audit/seat/merge_train.py --self-test
             `tools/audit/seat/merge_train.py` is in the tree at this head
  ok         bash tools/audit/seat/pr_args.sh --self-test
             `tools/audit/seat/pr_args.sh` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 3 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_codescan_wait_race.py b/dev/audit/harnesses/r10_codescan_wait_race.py
index 983168c62..34b25ef6b 100644
--- a/dev/audit/harnesses/r10_codescan_wait_race.py
+++ b/dev/audit/harnesses/r10_codescan_wait_race.py
@@ -48,17 +48,25 @@ def pr_of(run):
 
 def pages(get, path, params):
     """Every item, paged by `page=` rather than the Link header (whose
-    repositories/<id> form some proxies refuse); ghapi.paginate's one-list rule."""
-    out = []
-    for n in range(1, ghapi.MAX_PAGES + 1):
-        st, _, doc = get(path, dict(params, per_page=100, page=n))
-        if st != 200 or not isinstance(doc, dict):
-            raise ghapi.ApiError(path, st, "")
-        items = next(v for v in doc.values() if isinstance(v, list))
-        out += items
-        if len(items) < 100:
-            return out
-    raise ghapi.ApiError(path, 200, "too many pages")
+    repositories/<id> form some proxies refuse); ghapi.paginate's one-list rule.
+    ghapi.get already retries a 5xx twice with backoff; one that persists
+    (run 40126133450: page 2 of per_page=100 answered 502, per_page=30 answered
+    200) restarts the listing at the next smaller page size; a 4xx raises."""
+    for size in (100, 30):
+        out = []
+        for n in range(1, ghapi.MAX_PAGES + 1):
+            st, _, doc = get(path, dict(params, per_page=size, page=n))
+            if st >= 500 and size != 30:
+                break
+            if st != 200 or not isinstance(doc, dict):
+                raise ghapi.ApiError(path, st, "")
+            items = next(v for v in doc.values() if isinstance(v, list))
+            out += items
+            if len(items) < size:
+                return out
+        else:
+            raise ghapi.ApiError(path, 200, "too many pages")
+    raise AssertionError("unreachable")
 
 
 def jobs_all(get, rid):
@@ -134,8 +142,33 @@ def selftest():
     want = dict(inverted=2, ordered=1, red_inverted=1, red_ordered=0, red_attempts=3, rerun=2, fresh=1, carried=1)
     bad = [k for k, v in want.items() if o[k] != v]
     rows_ok = [r[6] for r in o["rows"]] == [True, False]
-    print(f"selftest: {len(want) + 1} checks, {len(bad) + (not rows_ok)} failed{' ' + str(bad) if bad else ''}")
-    return 1 if bad or not rows_ok else 0
+    calls = []
+
+    def fake(fail_p2_at):
+        def get(path, params):
+            calls.append((params["per_page"], params["page"]))
+            n, size = params["page"], params["per_page"]
+            if size == fail_p2_at and n == 2:
+                return 502, {}, {}
+            if path == "404":
+                return 404, {}, {}
+            total = 150
+            return 200, {}, {"jobs": list(range((n - 1) * size, min(n * size, total)))}
+        return get
+    got = pages(fake(100), "x", {})
+    pages_ok = got == list(range(150)) and calls == [(100, 1), (100, 2)] + [(30, i) for i in range(1, 7)]
+    calls.clear()
+    clean_ok = pages(fake(0), "x", {}) == list(range(150)) and calls == [(100, 1), (100, 2)]
+    calls.clear()
+    try:
+        pages(fake(0), "404", {})
+        null_ok = False
+    except ghapi.ApiError as e:
+        null_ok = e.status == 404 and len(calls) == 1
+    pg = pages_ok and clean_ok and null_ok
+    print(f"selftest: {len(want) + 4} checks, {len(bad) + (not rows_ok) + (not pg)} failed{' ' + str(bad) if bad else ''}"
+          f"{'' if pg else f' pages(fallback {pages_ok}, clean {clean_ok}, 4xx {null_ok})'}")
+    return 1 if bad or not rows_ok or not pg else 0
 
 
 def main(argv):
diff --git a/dev/programme/delivery/3288.md b/dev/programme/delivery/3288.md
new file mode 100644
index 000000000..52e82810f
--- /dev/null
+++ b/dev/programme/delivery/3288.md
@@ -0,0 +1 @@
+- [#3288](https://github.com/tvofi/heatpump_optimizer/pull/3288) — **open**, R10-TRAIN-MERGE-LOOP-2: train merge loop 2 (R10-TRAIN-MERGE-LOOP-2)
diff --git a/tools/audit/seat/merge_train.py b/tools/audit/seat/merge_train.py
index 3361fce26..f2582291a 100644
--- a/tools/audit/seat/merge_train.py
+++ b/tools/audit/seat/merge_train.py
@@ -778,6 +778,13 @@ class Stop(Exception):
 # "Base branch was modified", the GraphQL "is not up to date" family).
 BASE_MOVED = re.compile(r"base branch was modified|not up to date|head branch is behind|is behind the base", re.I)
 HOLDER = "HOLDER"                    # the recarry's branch is checked out in another worktree
+def runs_approved(listing: str) -> bool:
+    """True when a head's pull_request runs listing (status<TAB>conclusion
+    lines) has at least one run and none still held action_required."""
+    rows = [ln.split("\t") for ln in listing.splitlines() if ln.strip()]
+    return bool(rows) and not any("action_required" in r for r in rows)
+
+
 BOT_HEAD = "BOT-HEAD"                # a GITHUB_TOKEN push is the head: its pull_request runs are held
 STALE_VERDICT_CARRY = "STALE-VERDICT-CARRY"  # the verdict sha no longer carries: the branch moved post-verdict
 ROW_MISSING = "ROW-MISSING"          # no delivery row in the three-dot diff
@@ -1131,6 +1138,81 @@ def launch_detached(argv: "list[str]", state: Path) -> "tuple[int, str]":
     return 0, f"rc {p.poll()}: {tail[:200]}"
 
 
+def is_draft(t: "Train", pr: int) -> bool:
+    return t.out("gh", "pr", "view", str(pr), "--repo", t.repo, "--json", "isDraft", "--jq", ".isDraft") == "true"
+
+
+def undraft(t: "Train", pr: int, h: str, item: dict) -> None:
+    """Merge step, after the verdict carry, CI, row, tree grade and approval:
+    undraft a head RECORDED AS A DRAFT AT ADMISSION (`item["draft"]`, set by
+    `add`). A head drafted after admission is left alone. Stops, never
+    continues, when `gh pr ready` fails or the head is a draft again."""
+    if not item.get("draft") or not is_draft(t, pr):
+        return
+    t.log(f"UNDRAFT #{pr} {h[:12]}")
+    code, said = t.run(["gh", "pr", "ready", str(pr), "--repo", t.repo])
+    if code:
+        raise Stop("undraft", f"gh pr ready #{pr} failed: {said.strip()[-160:]}")
+    if is_draft(t, pr):
+        raise Stop("undraft", f"#{pr} is a draft again after gh pr ready")
+
+
+APPROVER_BOT = "hpo-approver[bot]"
+WAIT_GATES = (GATE, RAISE_GATE)
+
+
+def post_approval_wait(t: "Train", pr: int, head: str, poll: float, budget_s: float) -> int:
+    """`add --wait-post-approval`: block until <head> may be added. Polls every
+    <poll> s (t.sleep) for the approver App's `Fix review: merge <head>` comment
+    and its APPROVED review at <head>; `refs/pull/<pr>/head` must still be
+    <head> (else `HEAD MOVED, not adding`, rc 1); then every `gate` /
+    RAISE_GATE run started at or after the approval's submitted_at must have
+    completed -- a run that started before it does not count, and none yet is
+    a wait. Red (failure/cancelled) -> `GATE RED AFTER APPROVAL`, rc 2. Green:
+    `gh pr ready` on a draft, rc 0. <budget_s> spent (t.clock) -> `WAIT BUDGET
+    SPENT`, rc 3."""
+    start = t.clock()
+    while True:
+        code, ref = t.run(["gh", "api", f"repos/{t.repo}/git/ref/pull/{pr}/head", "--jq", ".object.sha"])
+        if code == 0 and ref.strip() != head:
+            t.log(f"HEAD MOVED, not adding #{pr}: refs/pull/{pr}/head is {ref.strip()[:12]}, not {head[:12]}")
+            return 1
+        why = "the ref could not be read" if code else ""
+        if not why:
+            try:
+                revs = t._reviews(pr, "the post-approval wait")
+            except Stop as s:
+                revs, why = [], s.why
+            at = max((r.get("submitted_at") or "" for r in revs if (r.get("user") or {}).get("login") == APPROVER_BOT
+                      and r.get("state") == "APPROVED" and r.get("commit_id") == head), default="")
+            code, raw = t.run(["gh", "api", "--paginate", "--slurp", f"repos/{t.repo}/issues/{pr}/comments?per_page=100"])
+            try:
+                said = code == 0 and any((c.get("user") or {}).get("login") == APPROVER_BOT
+                                         and (c.get("body") or "").startswith(f"Fix review: merge {head}")
+                                         for page in json.loads(raw) for c in page)
+            except (ValueError, TypeError):
+                said = False
+            runs = t._check_runs(head) or []
+            mine = [c for c in runs if c.get("name") in WAIT_GATES and at and (c.get("started_at") or "") >= at]
+            if not (at and said):
+                why = why or "no approval review and verdict comment at the head yet"
+            elif any(c.get("status") == "completed" and c.get("conclusion") in ("failure", "cancelled") for c in mine):
+                t.log(f"GATE RED AFTER APPROVAL, not adding #{pr}")
+                return 2
+            elif not mine or any(c.get("status") != "completed" for c in mine):
+                why = "the gate re-run after the approval has not completed"
+            else:
+                if is_draft(t, pr) and t.run(["gh", "pr", "ready", str(pr), "--repo", t.repo])[0]:
+                    t.log(f"gh pr ready #{pr} failed, not adding")
+                    return 2
+                return 0
+        if t.clock() - start >= budget_s:
+            t.log(f"WAIT BUDGET SPENT for #{pr}: {why}; not adding")
+            return 3
+        t.log(f"WAIT #{pr}: {why}")
+        t.sleep(poll)
+
+
 def train_add(t: "Train", item: dict, train_argv: "list[str]", launch=launch_detached,
               settle: float = ADD_SETTLE_SECONDS, front: bool = False, ready: "list[dict] | None" = None) -> int:
     """`add`: load one verdicted pull request into the state dir's live train,
@@ -1180,6 +1262,8 @@ def train_add(t: "Train", item: dict, train_argv: "list[str]", launch=launch_det
             return 1
         entry = {k: item[k] for k in ("pr", "verdict", "verdict_comment", "issues", "priority") if item.get(k) is not None}
         entry["pr"] = int(pr)
+        if is_draft(t, int(pr)):
+            entry["draft"] = True
         if front:
             entry["front"] = True
         if live:
@@ -1218,6 +1302,34 @@ def train_add(t: "Train", item: dict, train_argv: "list[str]", launch=launch_det
         return 0
 
 
+GIT_TRIES = 3
+#: git's own stderr, measured: smart-HTTP and socket failures a later call rides out.
+GIT_TRANSIENT = re.compile(
+    r"returned error: 5\d\d|RPC failed; HTTP 5\d\d|unexpected disconnect while reading sideband"
+    r"|early EOF|the remote end hung up unexpectedly|Connection reset by peer|Could not resolve host"
+    r"|Failed to connect|Operation timed out|GnuTLS recv error|SSL_ERROR_SYSCALL|unable to access.*timed? ?out")
+#: A refusal or a rejected update: never retried, whatever else the output says.
+GIT_REFUSED = re.compile(
+    r"non-fast-forward|\[rejected\]|Permission denied|Authentication failed|\b40[34]\b"
+    r"|couldn't find remote ref|protected branch hook declined|stale info|remote rejected")
+
+
+def git_transient(output: str) -> bool:
+    """git's stderr on a failed fetch/push -> True when another call may ride it out."""
+    return not GIT_REFUSED.search(output) and bool(GIT_TRANSIENT.search(output))
+
+
+def run_git_retry(run, argv, sleep, log=lambda line: None, **kw):
+    """`run(argv)` for a git fetch/push, repeated up to GIT_TRIES times (settling 5/15 s)
+    while the failure is git_transient; a rejection or a success answers at once."""
+    for n in range(1, GIT_TRIES + 1):
+        code, o = run(argv, **kw)
+        if not code or n == GIT_TRIES or not git_transient(o):
+            return code, o
+        log(f"merge_train: {' '.join(argv)[:120]}: git {n}/{GIT_TRIES}: {' '.join(o.split())[:120]}")
+        sleep(5 * 3 ** (n - 1))
+
+
 class Train:
     def __init__(self, repo: str, state: Path, mandate: str | None, role: str,
                  ignore: tuple[str, ...], min_runs: int, run=None, sleep=time.sleep,
@@ -1292,6 +1404,8 @@ class Train:
         failure with the attempt count. Train 8 stopped on one unretried read
         of a head commit. Every other call, and every write, is `run`'s alone."""
         def retried(argv, **kw):
+            if argv[:2] in (["git", "fetch"], ["git", "push"]):  # transport, idempotent: a rejection is never retried
+                return run_git_retry(run, argv, self.sleep, self.log, **kw)
             if not gh_read.is_read(argv):
                 return run(argv, **kw)
 
@@ -1327,8 +1441,9 @@ class Train:
     # 2026-10-09 no such run was created at all (63084989/#2066 and
     # a9ba0b88/#2070: 4 dispatched runs each, the same 5 of the 17 required
     # contexts of main-protect-checks absent). The autofix job's approve step
-    # approves the held runs, fail-soft while its secrets are absent; this
-    # train does not read whether it did, so it still refuses such a tip.
+    # approves the held runs, fail-soft while its secrets are absent; bot_tip
+    # reads the head's pull_request runs and refuses only while none exists or
+    # one is still held action_required (an unreadable listing refuses too).
     # Dispatch cannot write those contexts: governance.yml answers
     # workflow_dispatch, but pr-contract.yml and budget-raise-gate.yml take
     # pull_request/merge_group only. An App push is a follow-up that does, and
@@ -1345,7 +1460,12 @@ class Train:
         if code or "\t" not in o:
             raise Stop("ci", f"the head commit at {h[:8]} could not be read: {o.strip()[-160:]}")
         who, _, subject = o.strip().partition("\t")
-        return subject if who in ("github-actions", "github-actions[bot]") else None
+        if who not in ("github-actions", "github-actions[bot]"):
+            return None
+        code, o = self.run(["gh", "api", "--paginate", "--jq",
+                            '.workflow_runs[] | [.status, (.conclusion // "")] | @tsv',
+                            f"repos/{self.repo}/actions/runs?head_sha={h}&event=pull_request&per_page=100"])
+        return subject if code or not runs_approved(o) else None
 
     def bot_refusal(self, pr: int, h: str, subject: str) -> Stop:
         return Stop("ci", f"#{pr} head {h[:8]} is a GITHUB_TOKEN push (github-actions[bot]: "
@@ -1516,6 +1636,29 @@ class Train:
         except ValueError:
             return None
 
+    def gate_deferred(self, h: str, red: "list[str]") -> "list[int]":
+        """The ids of the other workflow runs at <h> still unfinished when the
+        only red is GATE, else []. An edit run's gate fails by design while a
+        code run at the same head is unfinished ("still being judged; their
+        gate decides", gate.py `deferral`), and that run's own gate check-run
+        does not exist until every unit finishes (ci.yml: gate needs
+        pr-contract, which needs every unit), so the check-runs alone show a
+        final red. The sibling is read from actions/runs?head_sha, never from
+        check-run presence. A failed or unparseable read is [] (the red
+        stands, today's skip); `wait_ci`'s polls bound the wait."""
+        if red != [GATE]:
+            return []
+        code, o = self.run(["gh", "api", "--paginate", "--jq", ".workflow_runs[] | [.id, .status] | @tsv",
+                            f"repos/{self.repo}/actions/runs?head_sha={h}&per_page=100"])
+        if code:
+            return []
+        out = []
+        for ln in o.splitlines():
+            rid, _, st = ln.partition("\t")
+            if rid.strip().isdigit() and st.strip() not in ("completed", "action_required", ""):
+                out.append(int(rid))
+        return sorted(out)
+
     def wait_ci(self, h: str, only: "list[str] | None" = None,
                 beat: "str | None" = None) -> list[str]:
         """The names whose latest run at <h> is not green, once every run completed.
@@ -1540,13 +1683,24 @@ class Train:
         start = self.clock()
         due = start + HEARTBEAT_SECONDS
         what = beat or f"CI at {h[:8]}"
+        graced = False
         for k in range(1, self.polls + 1):
             runs = self._check_runs(h)
             last = latest_runs(runs or ())
             if only is not None and runs is not None:
                 _, pending, red = classify(last, only)
                 if not pending:
-                    return red
+                    sib = self.gate_deferred(h, red)
+                    if sib:
+                        graced = True
+                    elif graced and red == [GATE]:
+                        # the deciding run finished: gate.py re-runs the deferring gates
+                        # (its rerun cascade), which lists a beat later -- one more poll
+                        graced = False
+                    else:
+                        return red
+                    if sib:
+                        self.log(f"wait: gate red at {h[:8]} is a deferral while run(s) {sib} at this head are unfinished; waiting")
             if only is None and runs and len(runs) >= self.min_runs and all(
                     c.get("status") == "completed" for c in runs):
                 return sorted(n for n, c in last.items() if c["conclusion"] not in GREEN)
@@ -2201,7 +2355,7 @@ class Train:
             if under:
                 self.log(f"#{pr} policy head lands under {under}")
             self.log(f"#{pr} approved ({self.approve(pr, h, item, files)})")
-        self.run(["gh", "pr", "ready", str(pr), "--repo", self.repo])
+        undraft(self, pr, h, item)
         title = self.out("gh", "pr", "view", str(pr), "--repo", self.repo, "--json", "title", "--jq", ".title")
         pf = self.run(["bash", tool("preflight"), *map(str, item.get("issues", []))], stdin=title + "\n")[1]
         if re.search(r"(?m)^\s*REFUSE\b", pf) or not re.search(r"(?m)^\s*clean\b", pf):
@@ -3659,6 +3813,14 @@ def _self_test() -> int:
                 return world.get("hold_create", (0, "{}"))
             if argv[:3] == ["gh", "auth", "token"]:
                 return 0, "tok"
+            if argv[:3] == ["gh", "pr", "ready"]:
+                world.setdefault("readied", []).append(argv[3])
+                if "ready_rc" in world:
+                    return world["ready_rc"]
+                world["is_draft"] = world.get("redraft", False)
+                return 0, ""
+            if "isDraft" in argv:
+                return 0, "true" if world.get("is_draft") else "false"
             if argv[:3] == ["gh", "pr", "view"] and argv[3] == "9":  # the record PR
                 return 0, ("e" * 40 if "headRefOid" in a else
                            "MERGED " + "9" * 40 if 9 in world.get("bot_merged", ()) else "OPEN None")
@@ -3705,6 +3867,8 @@ def _self_test() -> int:
                 if reads <= world.get("pending_reads", 0):
                     runs = [dict(c, status="in_progress") for c in runs]
                 return 0, "\n".join(json.dumps(c) for c in runs)
+            if argv[:2] == ["gh", "api"] and "event=pull_request" in a:  # bot_tip's runs read, post-jq
+                return world.get("bot_runs", (0, ""))
             if argv[:2] == ["gh", "api"] and "/commits/" in a:  # bot_tip's read, post-jq
                 sha = a.split("/commits/")[1].split()[0].split("?")[0].split("/")[0]
                 subj = world.get("bot_tips", {}).get(sha)
@@ -3810,6 +3974,29 @@ def _self_test() -> int:
     def approved(calls) -> bool:
         return any(c[:3] == ["gh", "pr", "review"] for c in calls)
 
+    D = dict(item, draft=True)
+    ud = lambda ln: [x for x in ln if x.startswith("UNDRAFT")]
+    rc, lines, calls = go({"is_draft": True}, q=[dict(D)])
+    check("a head recorded as a draft at admission is undrafted once and merges",
+          rc == 0 and merged(calls) and ud(lines) == [f"UNDRAFT #7 {H0[:12]}"])
+    rc, lines, calls = go({}, q=[dict(D)])
+    check("undraft null: a non-draft head at the same step merges with no UNDRAFT line",
+          rc == 0 and merged(calls) and not ud(lines) and not any(c[:3] == ["gh", "pr", "ready"] for c in calls))
+    rc, lines, calls = go({"is_draft": True}, q=[dict(item)])
+    check("undraft null: a head drafted after admission (no draft:true in the item) is not undrafted",
+          not ud(lines) and not any(c[:3] == ["gh", "pr", "ready"] for c in calls))
+    rc, lines, calls = go({"is_draft": True, "carry": "CARRY: no"}, q=[dict(D)])
+    check("undraft null: a draft whose verdict does not carry to the head is not undrafted",
+          rc == 1 and not ud(lines) and not merged(calls))
+    rc, lines, calls = go({"is_draft": True, "runs": [{"name": "fast", "status": "in_progress", "started_at": "1"}],
+                           "pending_reads": 99}, q=[dict(D)])
+    check("undraft null: a draft with a pending required context is not undrafted",
+          rc == 1 and not ud(lines) and not merged(calls))
+    rc, lines, calls = go({"is_draft": True, "ready_rc": (1, "boom")}, q=[dict(D)])
+    check("a failed gh pr ready is an undraft Stop, no merge", rc == 1 and "undraft:" in lines[-1] and not merged(calls))
+    rc, lines, calls = go({"is_draft": True, "redraft": True}, q=[dict(D)])
+    check("a head re-drafted after the call stops the run before the merge",
+          rc == 1 and "undraft:" in lines[-1] and not merged(calls))
     rc, lines, calls = go({})
     check("a green, carried, non-policy pull request merges (null control)", rc == 0 and merged(calls) and lines[-1] == "TRAIN DONE")
     check("a wait that settles on its first poll beats nothing (heartbeat null control)",
@@ -4630,6 +4817,15 @@ def _self_test() -> int:
           "and the train goes on at the new head (null control for the refusal above)",
           rc == 0 and merged(calls) and any("recarry" in ln for ln in lines)
           and any(c[:3] == ["gh", "pr", "merge"] and c[-1] == H1 for c in calls))
+    for what, runs, merges in (("approved (completed/success)", (0, "completed\tsuccess\n"), True),
+                               ("still held action_required", (0, "completed\taction_required\n"), False),
+                               ("held, status form", (0, "action_required\t\n"), False),
+                               ("absent (no pull_request run)", (0, ""), False),
+                               ("unreadable listing", (1, "gh: HTTP 502"), False)):
+        rc, lines, calls = go({"bot_tips": {H0: BOT}, "bot_runs": runs})
+        check(f"carry 3: a bot head whose pull_request runs are {what} is "
+              + ("merged" if merges else "refused with the BOT-HEAD line"),
+              (rc == 0 and merged(calls)) if merges else (rc == 1 and "[BOT-HEAD]" in lines[-1] and not merged(calls)))
     # The route the stubs cannot see: the real remerge_main.sh pushes with --recarry.
     rm = (ROOT / TOOLS["remerge_main"][0]).read_text()
     check("remerge_main.sh pushes the recarry with app_push.sh --recarry and passes its RECARRY line on",
@@ -4898,7 +5094,9 @@ def _self_test() -> int:
           not any("/git/refs" in " ".join(c) or "/git/commits" in " ".join(c) for c in calls0))
     _stop_self_test(check)
     _read_retry_self_test(check)
+    _git_retry_self_test(check)
     _review_settle_self_test(check)
+    _gate_race_self_test(check)
     _state_self_test(check, go, merged, throwaway_git_init)
     _infra_self_test(check)
     _batch_self_test(check)
@@ -5349,6 +5547,63 @@ def _queue_self_test(check) -> None:
     tmp.cleanup()
 
 
+def _gate_race_self_test(check) -> None:
+    """The train gate race (2026-11-06, #3248's scene): the edit run's gate
+    failed at 14:55:47Z by design (gate.py `deferral`) while the code run
+    42237558473 was unfinished, its gate check-run listed only at 15:25:55Z.
+    `wait_ci` must wait while a sibling run at the head is unfinished and
+    still return a red gate once none is."""
+    H = "e" * 40
+    edit_gate = {"name": "gate", "status": "completed", "conclusion": "failure", "started_at": "2026-11-06T14:55:00Z",
+                 "id": 1, "check_suite": {"id": 11}}
+    code_gate = {"name": "gate", "status": "completed", "conclusion": "success", "started_at": "2026-11-06T15:25:00Z",
+                 "id": 2, "check_suite": {"id": 22}}
+
+    def world(checks, sibs):
+        calls: list = []
+
+        def run(argv, cwd=ROOT, stdin=None):
+            a = " ".join(argv)
+            calls.append(a)
+            if "check-runs" in a:
+                cur = checks[min(len(calls_cr), len(checks) - 1)]
+                calls_cr.append(1)
+                return 0, "\n".join(json.dumps(c) for c in cur)
+            if "actions/runs?head_sha=" in a:
+                cur = sibs[min(len(calls_sb), len(sibs) - 1)]
+                calls_sb.append(1)
+                return (cur if isinstance(cur, tuple) else (0, cur))
+            return 0, ""
+        calls_cr: list = []
+        calls_sb: list = []
+        return run, calls, calls_sb
+
+    def wait(checks, sibs, polls=4):
+        run, calls, calls_sb = world(checks, sibs)
+        with tempfile.TemporaryDirectory() as d:
+            t = Train("o/r", Path(d), None, "", (), 1, run=run, sleep=lambda s: None, log=lambda s: None, polls=polls)
+            return t.wait_ci(H, only=[GATE]), calls_sb
+    busy = "42237558473\tin_progress\n42237558635\tcompleted\n"
+    done = "42237558473\tcompleted\n42237558635\tcompleted\n"
+    rerun_green = dict(edit_gate, conclusion="success", started_at="2026-11-06T15:26:00Z")
+    red, _ = wait([[edit_gate], [edit_gate], [rerun_green, code_gate]], [busy, done, done], polls=5)
+    check("a failed gate beside an unfinished sibling run is waited on, then through the cascade re-run's lag, "
+          "not returned red (the #3248 scene)", red == [])
+    red, _ = wait([[edit_gate]], [busy], polls=3)
+    check("a sibling run that never finishes ends as TIMEOUT, bounded by the polls", red == ["TIMEOUT"])
+    red, sb = wait([[edit_gate]], [done])
+    check("null control: a red gate with no unfinished sibling run still returns red on the first poll",
+          red == [GATE] and len(sb) == 1)
+    red, sb = wait([[edit_gate]], [(1, "boom")])
+    check("an unreadable runs listing leaves the red standing (today's skip)", red == [GATE] and len(sb) == 1)
+    unit = {"name": "fast", "status": "completed", "conclusion": "failure", "started_at": "1"}
+    run, calls, sb = world([[unit]], [busy])
+    with tempfile.TemporaryDirectory() as d:
+        r = Train("o/r", Path(d), None, "", (), 1, run=run, sleep=lambda s: None, log=lambda s: None,
+                  polls=3).wait_ci(H, only=["fast"])
+    check("a failed unit beside an unfinished sibling is final: only the gate defers", r == ["fast"] and not sb)
+
+
 def _review_settle_self_test(check) -> None:
     """P331: the `CI review` wait is bounded by time, and a BLOCKED/APPROVED
     refusal beside a settling review run is a wait, not a park.
@@ -5411,6 +5666,40 @@ def _review_settle_self_test(check) -> None:
     check("P331 (2) null: a required context red parks, never waits", got[1] is False and "red" in got[0])
 
 
+def _git_retry_self_test(check) -> None:
+    """R10 carry 7: git fetch/push ride out git's own transient stderr, and nothing else."""
+    for s in ("fatal: unable to access 'u': The requested URL returned error: 503", "error: RPC failed; HTTP 502 curl 22",
+              "error: RPC failed; HTTP 500", "fatal: the remote end hung up unexpectedly", "error: RPC failed; HTTP 504",
+              "fatal: unexpected disconnect while reading sideband packet", "fatal: early EOF",
+              "Connection reset by peer", "Could not resolve host: github.com", "Failed to connect to github.com",
+              "Operation timed out", "GnuTLS recv error (-54)", "OpenSSL SSL_ERROR_SYSCALL", "returned error: 502",
+              "fatal: unable to access 'u': Connection timed out"):
+        check(f"git transient: {s[:50]}", git_transient(s))
+    for s in (" ! [rejected] main -> main (non-fast-forward)", "Permission denied (publickey)", "Authentication failed",
+              "returned error: 403", "returned error: 404", "fatal: couldn't find remote ref x",
+              "remote: error: protected branch hook declined", "! [rejected] (stale info)", "! [remote rejected] x",
+              "RPC failed; HTTP 502 but remote rejected"):
+        check(f"git not transient: {s[:50]}", not git_transient(s))
+
+    def go(outs):
+        calls, sleeps = [], []
+
+        def run(argv, **kw):
+            calls.append(argv)
+            return outs.pop(0) if len(outs) > 1 else outs[0]
+        t = Train("o/r", Path("."), None, "", (), 1, run=run, sleep=sleeps.append, log=lambda s: None)
+        return t.run(["git", "fetch", "-q", "origin", "main"]), len(calls), sleeps
+    bad = (1, "error: RPC failed; HTTP 502")
+    r, n, sl = go([bad, (0, "")])
+    check("git retry: a 502 then success -> success after 2 calls, settling 5 s", r[0] == 0 and n == 2 and sl == [5])
+    r, n, sl = go([(1, "! [rejected] main -> main (non-fast-forward)")])
+    check("git retry null: a rejection is 1 call, no settle", r[0] == 1 and n == 1 and sl == [])
+    r, n, sl = go([bad])
+    check("git retry: permanent failure returns the failure after 3 calls", r == bad and n == 3 and sl == [5, 15])
+    r, n, sl = go([(0, "")])
+    check("git retry null: a success is 1 call", r[0] == 0 and n == 1)
+
+
 def _read_retry_self_test(check) -> None:
     """R10-FLY-GH-READ-RETRY: the train's GitHub reads retry on gh_read's rule.
 
@@ -7273,6 +7562,8 @@ def _add_self_test(check) -> None:
             got = budget_fixture(w.get("budgets"), argv, B)
             if got is not None:
                 return got
+            if "isDraft" in argv:
+                return 0, "true" if w.get("is_draft") else "false"
             if argv[:2] == ["git", "ls-remote"]:  # verdict/<pr>'s confirmed tip
                 return w.get("ls", (0, f"{T}\t{argv[-1]}\n"))
             if argv[:2] == ["gh", "api"] and "/comments" in a:  # its posting: merge at the added verdict
@@ -7375,6 +7666,13 @@ def _add_self_test(check) -> None:
         check("add, a train live: the entry is spooled for its NEXT batch, nothing started (ADDED)",
               rc == 0 and len(got) == 1 and [e["pr"] for e in spool_read(st)[0]] == [8]
               and lines[-1].startswith("ADDED #8 to the live train"))
+        rc9, _ = add(st, 31, launch, is_draft=True)
+        rc10, _ = add(st, 32, launch)
+        sp = {e["pr"]: e for e in spool_read(st)[0]}
+        check("add records draft:true for a draft head at admission, and nothing for a non-draft",
+              sp[31].get("draft") is True and "draft" not in sp[32])
+        (st / QUEUE_SPOOL).unlink(missing_ok=True)
+        spool_append(st, {"pr": 8, "verdict": H, "verdict_comment": "42"})
         rc8, l8 = add(st, 8, launch)
         rc7, l7 = add(st, 7, launch)
         check("add is idempotent: a pull request spooled, or in the live train's batches, is ALREADY -- rc 0, "
@@ -7495,6 +7793,7 @@ def _add_self_test(check) -> None:
             p.wait()
         tmp.cleanup()
     _spool_edit_self_test(check, stub, H)
+    _post_approval_self_test(check)
 
 
 def _spool_edit_self_test(check, stub, H: str) -> None:
@@ -7671,6 +7970,67 @@ def _spool_edit_self_test(check, stub, H: str) -> None:
         tmp.cleanup()
 
 
+def _post_approval_self_test(check) -> None:
+    """`add --wait-post-approval`: a fake gh, a fake clock; sleeping advances it."""
+    H, OLD, AT, NEW = "a" * 40, "2026-01-01T10:00:00Z", "2026-01-01T11:00:00Z", "2026-01-01T11:05:00Z"
+
+    def wait(runs_by_poll, ref=H, budget=10000.0):
+        clk, slept = [0.0], []
+
+        def run(argv, **kw):
+            j = " ".join(argv)
+            if "git/ref/pull" in j:
+                return 0, ref
+            if "/reviews" in j:
+                return 0, json.dumps([[{"user": {"login": APPROVER_BOT}, "state": "APPROVED", "commit_id": H,
+                                       "submitted_at": AT}]])
+            if "/comments" in j:
+                return 0, json.dumps([[{"user": {"login": APPROVER_BOT}, "body": f"Fix review: merge {H}\nn"}]])
+            if "check-runs" in j:
+                rs = runs_by_poll[min(len(slept), len(runs_by_poll) - 1)]
+                return 0, "\n".join(json.dumps(r) for r in rs)
+            if "isDraft" in j:
+                return 0, "false"
+            return 0, ""
+
+        def sleep(s):
+            slept.append(s)
+            clk[0] += s
+        lines: list = []
+        t = Train("o/r", Path("."), None, "", (), 1, run=run, sleep=sleep, log=lines.append, clock=lambda: clk[0])
+        return post_approval_wait(t, 7, H, 240, budget), slept, lines
+
+    def cr(at, status="completed", conclusion="success", name="gate"):
+        return {"name": name, "started_at": at, "status": status, "conclusion": conclusion}
+    old_green = cr(OLD)
+    rc, slept, _ = wait([[old_green, cr(NEW, "in_progress", None)], [old_green, cr(NEW)]])
+    check("post-approval wait: a gate run green BEFORE the approval plus one in progress after it waits "
+          "(slept), then adds when the new run completes", rc == 0 and len(slept) == 1)
+    rc, slept, _ = wait([[old_green]])
+    check("post-approval wait: only a pre-approval run is no re-run: it waits to the budget (rc 3)",
+          rc == 3 and bool(slept))
+    rc, slept, lines = wait([[old_green]], ref="b" * 40)
+    check("post-approval wait: a moved head exits 1 (HEAD MOVED), nothing slept",
+          rc == 1 and not slept and "HEAD MOVED" in lines[-1])
+    for conc in ("failure", "cancelled"):
+        rc, _, lines = wait([[cr(NEW, conclusion=conc, name=RAISE_GATE)]])
+        check(f"post-approval wait: a post-approval {conc} exits 2 (GATE RED AFTER APPROVAL)",
+              rc == 2 and "GATE RED AFTER APPROVAL" in lines[-1])
+    rc, slept, lines = wait([[cr(NEW, "in_progress", None)]], budget=500)
+    check("post-approval wait: past the budget it stops, rc 3, WAIT BUDGET SPENT",
+          rc == 3 and "WAIT BUDGET SPENT" in lines[-1] and len(slept) == 3)
+    import io
+    seen: list = []
+    real = globals()["train_add"]
+    globals()["train_add"] = lambda t_, item, argv, **kw: seen.append(item) or 0
+    try:
+        with contextlib.redirect_stdout(io.StringIO()):
+            rc = main(["add", "7", H, "--state-dir", ".", "--repo", "o/r", "--auto"])
+    finally:
+        globals()["train_add"] = real
+    check("post-approval wait null: without the flag add never waits, it adds", rc == 0 and len(seen) == 1)
+
+
 def _parser() -> argparse.ArgumentParser:
     """The CLI parser, built apart from `main` so the self-test can pin the
     defaults a caller actually gets: both new flags off without the flag."""
@@ -7744,6 +8104,11 @@ def _parser() -> argparse.ArgumentParser:
                     help="HOTFIX: the spool's drain puts this entry before critical-path and arrival order (P312)")
     ad.add_argument("--stamp", action="store_true",
                     help="a stamp's add: a record pull request is added, not HELD-FOR-STAMP (carry 15)")
+    ad.add_argument("--wait-post-approval", action="store_true",
+                    help="first wait for the approver's verdict and approval at <verdict> and the gate re-run "
+                         "after it (rc 1 head moved, 2 red, 3 budget spent); then add")
+    ad.add_argument("--poll", type=float, default=240, help="--wait-post-approval: seconds between reads")
+    ad.add_argument("--budget-hours", type=float, default=3, help="--wait-post-approval: give up after this")
     ad.add_argument("--auto", action="store_true",
                     help="a started train is a bare train.sh launch (RECOMMENDED by default) with --mandate, "
                          "as the sweep's is: bus.sh's post calls this")
@@ -7803,6 +8168,10 @@ def main(argv: list[str]) -> int:
             return 2
         if a.remove:
             return spool_edit(t, a.pr, "remove")
+        if a.wait_post_approval and a.verdict:
+            rc = post_approval_wait(t, a.pr, a.verdict, a.poll, a.budget_hours * 3600)
+            if rc:
+                return rc
         if a.verdict is None:
             if a.front:
                 return spool_edit(t, a.pr, "front")
diff --git a/tools/audit/seat/pr_args.sh b/tools/audit/seat/pr_args.sh
index 164eea228..e52581687 100644
--- a/tools/audit/seat/pr_args.sh
+++ b/tools/audit/seat/pr_args.sh
@@ -1470,6 +1470,21 @@ GH
   rmrun - rc; ! grep -qF "MERGE CONFLICT" "$t/out" && [ "$(git -C "$t/rmw" rev-parse HEAD^2)" = "$(git -C "$t/rmm" rev-parse origin/main)" ] \
     && [ "$(git -C "$t/rmw" rev-parse HEAD^1)" = "$(git -C "$t/rmm" rev-parse origin/rc)" ]
   ck "null control: remerge_main on a clean merge keeps that merge (HEAD's parents origin/rc and origin/main), nothing aborted" $?
+  # The push's FAIL lines and prepr's `full log:` line reach the train's Stop message, and a push that
+  # printed no PUSHED keeps its log (carry 16): the old grep kept only RECARRY|REFUSE|PUSHED and the trap
+  # deleted the log, so a prepr refusal named neither its failing arm nor its log.
+  rmstub() { printf '#!/bin/bash\n%s\n' "$1" > "$t/rmm/tools/pr/app_push.sh"; }
+  rmstub 'echo "app_push: REFUSE: prepr step self-test"; echo "  FAIL arm-x (got 1, wanted 0)"; echo "PRE-PR: self-test deadbeef rc=1; full log: prepr-log.zz (PREPR_VERBOSE=1 prints it on stdout)"; exit 1'
+  rm -f "$t/body.md.push.log"; rmrun - rc
+  grep -qF "REFUSE: prepr step self-test" "$t/out" && grep -qF "FAIL arm-x (got 1, wanted 0)" "$t/out" && grep -qF "full log: prepr-log.zz" "$t/out" \
+    && grep -qxF "remerge: push log kept: $t/body.md.push.log" "$t/out" && [ -f "$t/body.md.push.log" ]
+  ck "remerge_main: a push that pushed nothing prints its REFUSE, FAIL and full-log lines and names its kept log, which exists after exit" $?
+  rmrun remergegrep rc; ! { grep -qF "FAIL arm-x" "$t/out" && grep -qF "full log: prepr-log.zz" "$t/out" && [ -f "$t/body.md.push.log" ]; }
+  ck "  mutant mut:remergegrep (its line deleted): the FAIL and full-log lines are lost" $?
+  rmstub 'echo "app_push: PUSHED abc"; exit 0'; rm -f "$t/body.md.push.log"; rmrun - rc
+  grep -qF "PUSHED abc" "$t/out" && ! grep -qF "push log kept" "$t/out" && [ ! -e "$t/body.md.push.log" ]
+  ck "null control: a push that printed PUSHED prints as before, keeps no log and names none" $?
+  rmstub 'echo stub-push-refused; exit 1'
   # The push's auto-maintenance runs in the foreground (#2825 round 1: a `git fetch` in the push
   # daemonized `git gc --auto`, which kept the push's fd 9, and so its lock, after the push). The
   # fixture's git has auto-maintenance off (throwaway_git); fix/g's stub push turns gc.auto back on
diff --git a/tools/audit/seat/remerge_main.sh b/tools/audit/seat/remerge_main.sh
index 7597f0889..1a8cb33ce 100755
--- a/tools/audit/seat/remerge_main.sh
+++ b/tools/audit/seat/remerge_main.sh
@@ -16,7 +16,7 @@ set -uo pipefail
 # trap reaps it, and the push runs asynchronously so an INT does not wait behind it.
 . "$(dirname -- "$0")/pr_args.sh"
 PR=$1; W=$2; BR=$3; B=$4; shift 4
-PL=$B.push.log; pr_exit_trap 'rm -f "$PL"'
+PL=$B.push.log; pr_exit_trap 'test -n "${KEEP:-}" || rm -f "$PL"'
 cd "$(git -C "$(dirname -- "$0")" rev-parse --show-toplevel)" || exit 1
 export GIT_AUTHOR_NAME=tvofi GIT_AUTHOR_EMAIL=70032254+tvofi@users.noreply.github.com GIT_COMMITTER_NAME=tvofi GIT_COMMITTER_EMAIL=70032254+tvofi@users.noreply.github.com
 # A failed merge is aborted before the stop (P276: #2935, #2936): left conflicted, the worktree kept
@@ -36,5 +36,8 @@ ISS=$(grep -oiE '\b(fixes|closes|resolves) #[0-9]+' "$B" | grep -oE '[0-9]+' | s
 if test -f tools/audit/app_push.sh; then _push=tools/audit/app_push.sh; else _push=tools/pr/app_push.sh; fi
 PYTHONPATH=tests/hastub PREPR_SKIP_CLOSURES=1 bash "$_push" --recarry tvofi/heatpump_optimizer "$W" "$BR" "$B" $ISS > "$PL" 2>&1 &
 wait $! || :; push_out=$(cat "$PL")
-printf '%s\n' "$push_out" | grep -E 'RECARRY|REFUSE|PUSHED' || true
+# FAIL lines name the failing arms and prepr's `full log:` line names its log (carry 16).
+printf '%s\n' "$push_out" | grep -E 'RECARRY|REFUSE|PUSHED|^ *FAIL |full log:' || true  # mut:remergegrep
+# No PUSHED: keep the log, as pr_push_failed does, and name it.
+case $push_out in *PUSHED*) ;; *) KEEP=1; echo "remerge: push log kept: $PL" ;; esac
 sleep 5; echo "RESULT pr=$PR head=$(gh pr view "$PR" --json headRefOid --jq .headRefOid)"

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
