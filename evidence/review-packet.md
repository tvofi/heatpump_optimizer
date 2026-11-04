# Review packet #3200
head: c46a9c6abe46e17a30fcfd9add85390dc9c603ac
base: d7582ed404a87603bd02fefda610d7ebbe4181e1

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=126796696961 neutral
arch-score / arch-score id=126795972416 success
arm id=126794732757 skipped
budget-raise-gate / budget-raise-gate id=126795972332 success
cancel-superseded id=126795654718 success
codeql id=126795116406 skipped
codeql / Analyze (actions) id=126795972452 success
codeql / Analyze (javascript-typescript) id=126795972732 success
codeql / Analyze (python) id=126795973725 in_progress
gate id=126801513121 in_progress
governance id=126795116568 skipped
governance / delivery-status id=126795972556 success
governance / delivery-status-publish id=126795975024 skipped
governance / env-matrix id=126795972327 success
governance / instrument-self-tests id=126795972268 in_progress
governance / policy-docs id=126795972609 success
governance / record id=126795975153 skipped
governance / wave-script id=126795972284 success
hassfest id=126795115023 skipped
hassfest / hassfest id=126795972227 success
kernel-points id=126795974533 skipped
pr-contract / pr-contract id=126795759554 failure
prelude id=126795654921 success
refresh id=126795655173 success
tests id=126795115233 skipped
tests / arch-instrument id=126796579179 success
tests / briefs id=126795972446 success
tests / browser id=126796579028 success
tests / claims-autofix id=126801713789 skipped
tests / closure-scope id=126795971923 success
tests / closures id=126796579012 in_progress
tests / coverage id=126796578713 in_progress
tests / fast (3.14) id=126796579040 success
tests / mutation id=126795972081 success
tests / mutation-autofix id=126796477871 skipped
tests / mutation-pins id=126796476927 skipped
tests / nightly-ha id=126796581961 skipped
tests / nightly-status id=126795972071 failure
tests / replay id=126796581671 skipped
tests / typing id=126796579043 success
validate id=126795115960 skipped
validate / validate-hacs id=126795971954 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/audit/seat/orchestrator_tick.py --self-test
             `tools/audit/seat/orchestrator_tick.py` is in the tree at this head
  ok         python3 tools/audit/seat/r10_ledger_mutants.py --self-test
             `tools/audit/seat/r10_ledger_mutants.py` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py --self-test
             `tools/pr/ci_predict.py` is in the tree at this head
  unverified python3 /tmp/ev/hosts_diff2.py .
             `/tmp/ev/hosts_diff2.py` resolves outside this repository, so whether it is in the tree at this head is not a question this check can answer
  ok         tests/lane_skip.py <- tests/entities.py
             `tests/lane_skip.py` is in the tree at this head
  ok         python -I -S tests/nightly_status.py
             `tests/nightly_status.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head

FIGURES: 8 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/governance/roles/standing-dispatch.md b/dev/governance/roles/standing-dispatch.md
index ebcf685f9..35ca31403 100644
--- a/dev/governance/roles/standing-dispatch.md
+++ b/dev/governance/roles/standing-dispatch.md
@@ -9,7 +9,7 @@ three-dot diff, then `tools/pr/approve_held_runs.sh`, `tools/audit/seat/bus.sh
 dispatch`, `tools/audit/seat/cloud_dispatch.py --role reviewer` at the printed
 head and nonce, and the `dispatch/reviewer-rev-<pr>` publish. Report
 `fire-owed <ref>`: a subagent cannot call RemoteTrigger; the orchestrator
-fires.
+fires. A `record/autofix` pull request is never dispatched a reviewer.
 
 **Relay:** `cloud_relay.sh pass --confirm`; `bus.sh confirm` merge verdicts
 carried to the live head; report each `handoff-body/<topic>`. A beat job takes
@@ -19,8 +19,7 @@ over once a cycle's log agrees; never inline.
 
 The roster's `resume.stage` and `resume.branch` are a seat's own claim;
 `roster_edit.py set-stage` refuses unknown stages; nothing verifies
-`branch` against the remote (measured 2026-10-10: three of five orphaned lanes
-named refs the remote lacked). Where `resume.commit` is set,
+`branch` against the remote. Where `resume.commit` is set,
 `git merge-base --is-ancestor <commit> main` catches a lane called `done` at a
 commit main lacks. Before a dispatch, ask the repository:
 
diff --git a/dev/programme/delivery/3200.md b/dev/programme/delivery/3200.md
new file mode 100644
index 000000000..4a498b5da
--- /dev/null
+++ b/dev/programme/delivery/3200.md
@@ -0,0 +1 @@
+- [#3200](https://github.com/tvofi/heatpump_optimizer/pull/3200) — **open**, R10-TICK-LEVELS part 1: tick board severity levels (R10-TICK-LEVELS)
diff --git a/tools/audit/seat/ledger.py b/tools/audit/seat/ledger.py
index 13064feb3..b5e3424db 100644
--- a/tools/audit/seat/ledger.py
+++ b/tools/audit/seat/ledger.py
@@ -104,6 +104,8 @@ KINDS = {
     "design-build": "derived", "review-owed": "derived",
     "probe-refused": "derived", "confirm-owed": "derived", "push-stuck": "derived",
     "seat-no-return": "derived",
+    "fixer-round": "derived", "recut": "derived", "train-parked": "derived", "dirty": "derived",
+    "red-unowned": "derived", "body-ahead": "derived", "fire-owed": "derived",
     "reviewer-fire": "event", "verdict-unposted": "event", "approve-held-runs": "event",
     "dispatch": "event", "train-stop": "event", "postmerge-owed": "event",
 }
@@ -616,15 +618,17 @@ def design_builds(verdicts: dict, designs: dict, stage_of, disp: dict) -> list[s
     return out
 
 
-def review_owed(prs: list, readback: dict, dispatched: set, carries=None) -> list[str]:
+def review_owed(prs: list, readback: dict, dispatched: set, carries=None, skip_branch=None) -> list[str]:
     """`REVIEW OWED: #N <head12>` per open non-draft PR whose comments were
     read, no verdict names its head, no dispatch record is at that head, and
     -- with `carries(verdict_head, head)` -- the newest verdict is not a merge
-    that carries to the head (the train's predicate, app_approve_carries)."""
+    that carries to the head (the train's predicate, app_approve_carries). A PR whose
+    `headRefName` is `skip_branch` (the record branch, passed in) is never owed one."""
     out = []
     for pr in sorted(prs, key=lambda p: p["number"]):
         n, head = pr["number"], pr.get("headRefOid") or ""
-        if pr.get("isDraft") or str(n) not in readback or not head:
+        if pr.get("isDraft") or str(n) not in readback or not head \
+                or (skip_branch and pr.get("headRefName") == skip_branch):
             continue
         lines = readback[str(n)]
         if any(verdict_head(l) == head for l in lines) or (str(n), head) in dispatched:
diff --git a/tools/audit/seat/orchestrator_tick.py b/tools/audit/seat/orchestrator_tick.py
index 3a9d43a0d..c605a1601 100644
--- a/tools/audit/seat/orchestrator_tick.py
+++ b/tools/audit/seat/orchestrator_tick.py
@@ -123,6 +123,12 @@ SELF = "tools/audit/seat/orchestrator_tick.py"
 SEAT = Path(__file__).resolve().parent
 ROOT = Path(__file__).resolve().parents[3]
 RULESET = "main-protect-checks"
+STUCK_FACTOR = 2  # a lane pending past this many critical-path medians is stuck (ETA and WAITING share it)
+RECUT_BLOCKED = 3          # the owner's three-round rule: the third blocked verdict owes a re-cut
+SEAT_WINDOW_MIN = 120      # "a seat is on it": a fire or a handoff ref move inside this window
+FIRE_GRACE_MIN = 15        # a rendered payload this old with no FIRED line is FIRE-OWED
+FIRED_STAMP = re.compile(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d)?Z?)")
+GATE_CONTEXTS = {"gate", "pr-contract"}  # the contexts an early-gate race reddens
 STALL_MINUTES = 90  # P328: p95 dispatch-to-verdict is 70 min; 90 fires on ~2.6% of reviews
 #: Per merge_train.py (its self-test pins the two equal): under the umbrella
 #: the one required context, `gate`, is written by a dispatch too, so nothing
@@ -243,6 +249,12 @@ def _module(name: str, *candidates: str):
 mt = _module("merge_train_tick", "tools/audit/seat/merge_train.py")
 
 
+def verdict_kind(line: str, head: str) -> "str | None":
+    """'merge' or 'blocked' when the approver verdict line names exactly `head`."""
+    m = re.match(r"^Fix review: (merge|blocked) ([0-9a-f]{40})(?: |$)", line)
+    return m.group(1) if m and m.group(2) == head else None
+
+
 class Tick:
     """One heartbeat. Every read goes through the injected runners, so the
     self-test drives every arm offline against stubbed gh/git/pgrep."""
@@ -260,7 +272,9 @@ class Tick:
                  bus_state: str | None = None,
                  now: datetime.datetime | None = None,
                  gh=None, git=None, proc=None, bus=None, carry=None,
-                 carry_last: int = CARRY_LAST) -> None:
+                 carry_last: int = CARRY_LAST, fired_log: "str | None" = None,
+                 payload_dir: "str | None" = None) -> None:
+        self.fired_log, self.payload_dir = fired_log, payload_dir
         self.repo, self.checkout = repo, checkout
         self.queues = ([queue] if isinstance(queue, str) else list(queue or []))
         self.policy_state = policy_state
@@ -383,12 +397,13 @@ class Tick:
             return None
 
     def stuck(self, started, med) -> bool:
-        """A lane pending past 2x the median: the ETA check's own threshold."""
+        """A lane pending past STUCK_FACTOR x the median: the ETA check's own threshold.
+        A null or unparseable `started_at` cannot be bounded, so it reads stuck."""
         try:
             st = datetime.datetime.fromisoformat(str(started).replace("Z", "+00:00"))
         except ValueError:
-            return False
-        return (self.now - st).total_seconds() / 60 > 2 * med
+            return True
+        return (self.now - st).total_seconds() / 60 > STUCK_FACTOR * med
 
     def split_absent(self, absent: list[str], latest: dict) -> "tuple[list[str], list[str]]":
         """(waiting, absent): a required job with no check run yet is only
@@ -475,7 +490,7 @@ class Tick:
         otherwise counts twice: the zsh -c parent and the child)."""
         out = []
         for pid, cmd in entries:
-            if needle not in cmd or "orchestrator_tick" in cmd:
+            if needle not in cmd or "orchestrator_tick" in cmd or "--self-test" in cmd:
                 continue
             if python_only and not re.match(r"\S*python3?\S*\s", cmd):
                 continue
@@ -552,7 +567,7 @@ class Tick:
         S = "PRS"
         code, o = self.gh(["pr", "list", "--repo", self.repo, "--limit", "200",
                            "--json", "number,headRefOid,headRefName,isDraft,"
-                           "mergeStateStatus,reviewDecision,title,createdAt,updatedAt,author"])
+                           "mergeStateStatus,reviewDecision,title,createdAt,updatedAt,author,body"])
         if code:
             self.unreadable(S, "open pull requests", o.strip()[-120:])
             return
@@ -578,6 +593,7 @@ class Tick:
         self.body_staleness(S, prs)
         self.cap_levels(S, prs)
         self.verdict_levels(S, prs)
+        self.owed_levels(S, prs)
         self.relay_owed(S)
         for head, ns in sorted(by_head.items()):
             if len(ns) > 1:
@@ -684,6 +700,7 @@ class Tick:
             return
         authors, vid = allow
         self._readback = {}  # {pr: [approver verdict first lines]}, the PRs whose comments were read
+        self._verdict_at = {}  # {pr: newest approver verdict created_at}
         lg, dispatched = _module("ledger_tick", "tools/audit/seat/ledger.py"), self._dispatched(S)
         for pr in sorted(prs, key=lambda p: p["number"]):
             n, head = pr["number"], pr.get("headRefOid") or ""
@@ -700,6 +717,8 @@ class Tick:
                   and (c.get("user") or {}).get("id") == vid
                   and (c.get("body") or "").startswith("Fix review:")]
             self._readback[str(n)] = [(c.get("body") or "").split("\n", 1)[0].rstrip("\r") for c in vs]
+            if vs:
+                self._verdict_at[n] = max(c.get("created_at") or "" for c in vs)
             if dispatched and (str(n), head) in dispatched and not any(
                     (pw.parse_verdict(f) or ("", ""))[1] == head for f in self._readback[str(n)]):
                 age = self._reviewer_ref_age(n)
@@ -733,9 +752,221 @@ class Tick:
         if lg is None:
             self.unreadable(S, "REVIEW OWED", "tools/audit/seat/ledger.py absent")
         elif dispatched is not None:
-            for text in lg.review_owed(prs, self._readback, dispatched, self._carries):
+            rr = _module("record_row_tick", "tools/audit/seat/record_row.py")
+            for text in lg.review_owed(prs, self._readback, dispatched, self._carries,
+                                       getattr(rr, "RECORD_BRANCH", None)):
                 self.line(S, text, flag=True)
 
+    # ------------------------------------------------------- OWED buckets
+    def _parked(self) -> "dict[int, str]":
+        """{pr: 'step: why'} for the `PARK #N <step>: <why>` lines after the train log's
+        last `STARTED` (the latest run only); the log the TRAIN pass already reads."""
+        try:
+            with open(self.train_log, encoding="utf-8", errors="replace") as fh:
+                lines = [l.rstrip() for l in fh]
+        except (OSError, TypeError):
+            return {}
+        start = max((i for i, l in enumerate(lines) if "STARTED" in l), default=-1)
+        out = {}
+        for l in lines[start + 1:]:
+            m = re.search(r"\bPARK #(\d+) (\S+?): (.*)$", l)
+            if m:
+                out[int(m.group(1))] = f"{m.group(2)}: {m.group(3)}"
+        return out
+
+    def _heads(self) -> "dict[str, str] | None":
+        """One `ls-remote` over the handoff families: {ref: sha}; None when it fails."""
+        if getattr(self, "_handoff_heads", False) is not False:
+            return self._handoff_heads
+        got = {}
+        for fam in ("handoff", "handoff-wip", "handoff-body"):
+            code, o = self.git(["ls-remote", "origin", f"refs/heads/{fam}/*"])
+            if code:
+                got = None
+                break
+            for l in o.splitlines():
+                f = l.split()
+                if len(f) == 2:
+                    got[f[1].removeprefix("refs/heads/")] = f[0]
+        self._handoff_heads = got
+        return got
+
+    def _age_min(self, ref: str, sha: str) -> "int | None":
+        """Minutes since `sha` (the tip of `ref`) was committed; None: a read failed."""
+        if self.git(["fetch", "-q", "origin", f"refs/heads/{ref}"])[0]:
+            return None
+        code, ct = self.git(["log", "-1", "--format=%ct", sha])
+        try:
+            return int((self.now.timestamp() - int(ct.strip())) // 60) if code == 0 else None
+        except ValueError:
+            return None
+
+    def _fired(self) -> "list[tuple]":
+        """[(utc or None, line)] for each FIRED line of the dispatch seat's ledger."""
+        try:
+            with open(self.fired_log, encoding="utf-8", errors="replace") as fh:
+                rows = [l.strip() for l in fh if "FIRED" in l]
+        except (OSError, TypeError):
+            return []
+        out = []
+        for l in rows:
+            m = FIRED_STAMP.match(l)
+            when = None
+            if m:
+                when = datetime.datetime.fromisoformat(m.group(1).rstrip("Z")).replace(
+                    tzinfo=datetime.timezone.utc)
+            out.append((when, l))
+        return out
+
+    def _fire_names(self, n: int, topics: list, line: str) -> bool:
+        """A FIRED line names a PR by number, topic or its payload file
+        (`payload-fix-<n>-r<k>.json`, `payload-<n>-r<k>.json`)."""
+        return bool(re.search(rf"#{n}(?!\d)|payload-(?:fix-)?{n}-r\d+\.json", line)) or any(
+            t and re.search(rf"(?<![\w-]){re.escape(t)}(?![\w-])", line, re.I) for t in topics)
+
+    def _seat_on(self, n: int, topics: list, heads: dict, kinds=("handoff-wip", "handoff", "handoff-body")) -> bool:
+        """A seat is on a PR when, inside SEAT_WINDOW_MIN, a FIRED line names it, or a
+        handoff-wip/, handoff/ or handoff-body/<topic> ref moved (`kinds` narrows the refs)."""
+        cutoff = self.now - datetime.timedelta(minutes=SEAT_WINDOW_MIN)
+        for when, l in self._fired():
+            if (when is None or when >= cutoff) and self._fire_names(n, topics, l):
+                return True
+        for t in topics:
+            for fam in kinds:
+                sha = heads.get(f"{fam}/{t}")
+                age = self._age_min(f"{fam}/{t}", sha) if sha else None
+                if age is not None and age <= SEAT_WINDOW_MIN:
+                    return True
+        return False
+
+    @staticmethod
+    def _topics(branch: str) -> list:
+        t = branch[4:] if branch.startswith("fix/") else branch
+        return list(dict.fromkeys([t, t[:-3] if t.endswith("-pr") else t]))
+
+    def owed_levels(self, S: str, prs: list) -> None:
+        """Every open pull request this pass can read in exactly one bucket (a draft, a PR with
+        no head, the record branch and one whose comments were not read are counted on the
+        count line's `not bucketed:` tail instead), from data the pass already read
+        (head, checks, mergeable state, the --queue file, the train log, the verdict
+        comments) plus git refs; no new GitHub call. Buckets: train | verdict-pending |
+        fixer-round | waiting-on #M | owed | verdicted (MERGE-READY and its levels own it)
+        | review-owed (REVIEW OWED owns it). `owed` prints one `OWED <kind> #N <head12>
+        <reason>` line (kinds in ledger.KINDS, derived each pass, so a moved head closes
+        it), the critical-path groups' PRs first, then one count line."""
+        heads = self._heads()
+        if heads is None:
+            self.unreadable(S, "owed buckets", "git ls-remote of the handoff refs failed")
+            return
+        queue = {int(i["pr"]): i.get("verdict") for i in (self._queue() or []) if i.get("pr")}
+        parked = self._parked()
+        readback = getattr(self, "_readback", {}) or {}
+        dispatched = self._dispatched(S) or set()
+        rl, roster = self._roster(S, announce=False)
+        crit = (set(rl.critical_path(roster)) if rl is not None else set()) if roster else set()
+        files = getattr(self, "_files", {}) or {}
+        open_n = {p["number"]: p for p in prs}
+        counts: dict = {}
+        skipped: dict = {}
+        owed: list = []
+        rr = _module("record_row_tick", "tools/audit/seat/record_row.py")
+        record = getattr(rr, "RECORD_BRANCH", None)
+        for pr in sorted(prs, key=lambda p: p["number"]):
+            n, head = pr["number"], pr.get("headRefOid") or ""
+            branch = pr.get("headRefName") or ""
+            why = ("draft" if pr.get("isDraft") else "no head" if not head else "record branch"
+                   if branch == record else "comments unread" if str(n) not in readback else "")
+            if why:
+                skipped[why] = skipped.get(why, 0) + 1
+                continue
+            topics, lines = self._topics(branch), readback[str(n)]
+            last = lines[-1] if lines else ""
+            ms = (pr.get("mergeStateStatus") or "").upper()
+            bucket, reason, kind = self._bucket(n, head, pr, topics, lines, last, ms, queue, parked,
+                                                dispatched, heads, files, open_n, roster, rl)
+            counts[bucket] = counts.get(bucket, 0) + 1
+            if bucket == "unreadable":
+                self.unreadable(S, "owed buckets", f"#{n}: {reason}")
+            if bucket == "owed":
+                group = rl.group_for_branch(roster, branch) if rl is not None and roster else None
+                owed.append((0 if group in crit else 1, n, f"OWED {kind} #{n} {head[:12]} {reason}"))
+        for _, _, text in sorted(owed):
+            self.line(S, text, flag=True)
+        self.line(S, "buckets: " + (", ".join(f"{k} {v}" for k, v in sorted(counts.items())) or "none")
+                  + ("; not bucketed: " + ", ".join(f"{k} {v}" for k, v in sorted(skipped.items()))
+                     if skipped else ""))
+        self.payloads(S)
+
+    def _bucket(self, n, head, pr, topics, lines, last, ms, queue, parked, dispatched, heads, files,
+                open_n, roster, rl):
+        """(bucket, reason, kind) for one open PR; the first arm that holds wins."""
+        if n in parked:
+            return "owed", f"train-parked {parked[n]}", "train-parked"
+        v = queue.get(n)
+        if v and (v == head or self.git(["merge-base", "--is-ancestor", v, head])[0] == 0):
+            return "train", "", ""
+        blocked = sum(1 for l in lines if l.startswith("Fix review: blocked "))
+        if blocked >= RECUT_BLOCKED and "## Re-cut" not in (pr.get("body") or ""):
+            return "owed", f"{blocked} blocked verdicts, head is not a re-cut or a split", "recut"
+        topic = next((t for t in topics if f"handoff/{t}" in heads), None)
+        body = next((t for t in topics if f"handoff-body/{t}" in heads), None)
+        if topic and body:
+            body_age = self._age_min(f"handoff-body/{body}", heads[f"handoff-body/{body}"])
+            code, ct = self.git(["log", "-1", "--format=%ct", head])
+            try:
+                head_age = int((self.now.timestamp() - int(ct.strip())) // 60) if code == 0 else None
+            except ValueError:
+                head_age = None
+            in_head = self.git(["merge-base", "--is-ancestor", heads[f"handoff/{topic}"], head])[0] == 0
+            if (body_age is not None and head_age is not None and body_age < head_age and in_head
+                    and not self._seat_on(n, topics, heads, kinds=("handoff-wip", "handoff"))):
+                return "owed", f"handoff-body/{body} is newer than the head, repair done and unapplied", "body-ahead"
+        if verdict_kind(last, head) == "blocked":
+            newer = self._handoff_newer(pr.get("headRefName") or "", self._verdict_at.get(n) or "")
+            if newer is None:
+                return "unreadable", "git read of the handoff ref failed", ""
+            if newer:
+                return "fixer-round", "", ""
+            at =self._verdict_at.get(n)
+            try:
+                age_h = (self.now - datetime.datetime.fromisoformat(at.replace("Z", "+00:00"))).total_seconds() / 3600
+            except (ValueError, AttributeError):
+                return "fixer-round", "", ""
+            if age_h >= self.stall_hours:
+                return "owed", f"blocked at head, no repair in {age_h:.0f}h", "fixer-round"
+            return "fixer-round", "", ""
+        if verdict_kind(last, head) == "merge":
+            return "verdicted", "", ""
+        if (str(n), head) in dispatched:
+            return "verdict-pending", "", ""
+        mine = {f for f in (files.get(n) or []) if not f.startswith(ROW_DIR) and f not in CLAIM_FILES}
+        for m, other in sorted(open_n.items()):
+            if m < n and mine & {f for f in (files.get(m) or []) if not f.startswith(ROW_DIR)}:
+                return "waiting-on", f"#{m}", ""
+        if rl is not None and roster:
+            g = rl.group_for_branch(roster, pr.get("headRefName") or "")
+            grp = next((x for x in roster.get("groups", []) if x.get("group") == g), None)
+            for a in (grp or {}).get("after") or []:
+                for m, other in open_n.items():
+                    if rl.group_for_branch(roster, other.get("headRefName") or "") == a:
+                        return "waiting-on", f"#{m}", ""
+        if ms == "DIRTY":
+            return "owed", "DIRTY, no repair under way", "dirty"
+        if getattr(self, "_red", {}).get(n) and not self._seat_on(n, topics, heads):
+            return "owed", f"red {','.join(self._red[n])}, no verdict at head, no seat on it", "red-unowned"
+        return "review-owed", "", ""
+
+    def payloads(self, S: str) -> None:
+        """FIRE-OWED: a rendered payload file older than FIRE_GRACE_MIN that no FIRED line names."""
+        if not self.payload_dir:
+            return
+        fired = self._fired()
+        for f in sorted(Path(self.payload_dir).glob("payload-*.json")):
+            age = (self.now.timestamp() - f.stat().st_mtime) / 60
+            if age > FIRE_GRACE_MIN and not any(f.name in l for _, l in fired):
+                self.line(S, f"OWED fire-owed {f.name} rendered {int(age)}m ago, no FIRED line "
+                             "(firing is a RemoteTrigger call: the orchestrator's turn)", flag=True)
+
     def _reviewer_ref_age(self, n: int) -> "int | None":
         """Minutes since the tip of `dispatch/reviewer-rev-<n>` (cloud_dispatch.py's
         dispatch_ref, re-pushed per dispatch) was committed; git only, never a
@@ -870,6 +1101,8 @@ class Tick:
             latest = self.latest(runs)
             _, run, red = self.judge(latest)
             self._unsettled[n] = bool(run or red or not runs)
+            self._red = getattr(self, "_red", {})
+            self._red[n] = list(red)
             if not runs:
                 self.line(S, f"#{n}: ZERO check runs at head (the bot-push "
                              "shape: run approve_held_runs.sh, not a fixer)",
@@ -901,6 +1134,12 @@ class Tick:
                 self.line(S, f"#{n}: RAISE APPROVAL OWED at {head[:8]}: review it, then approve "
                              "under the owner or the mandate (0013) -- not its fixer (K15 (d)): "
                              f"{owed}", flag=True)
+            elif req_red and run and set(req_red) <= GATE_CONTEXTS:
+                gt = _module("gate_tick", "tools/ci/gate.py")
+                self.line(S, f"#{n}: gate race at {head[:8]}: {', '.join(req_red)} red while "
+                             f"{', '.join(run)} still run -- rerun the failed jobs once siblings settle "
+                             f"(the gate defers up to {getattr(gt, 'GATE_WAIT_MAX_S', '?')}s, GATE_WAIT_MAX_S)",
+                          flag=True)
             elif req_red:
                 self.line(S, f"#{n}: NOT REVIEWABLE at {head[:8]}: required "
                              f"{', '.join(req_red)} concluded red -- back to its "
@@ -2160,7 +2399,7 @@ class Tick:
                     except ValueError:
                         continue
                     mins = (self.now - st).total_seconds() / 60
-                    if mins > 2 * med:
+                    if mins > STUCK_FACTOR * med:
                         self.line(S, f"lane {name} at #{n} pending "
                                      f"{mins:.0f}m vs median {med} -- "
                                      "re-run or diagnose", flag=True)
@@ -3518,6 +3757,204 @@ def self_test() -> int:
                  (len(owed) == 1 and f"{bud}: m: 3 -> 4" in owed[0]) if want else not owed),
                 ("NOT REVIEWABLE " + ("absent" if want else "present"), bool(nr) != want)])
             total, failed = total + a, failed + f
+        # Carry 8 (P82): an early-gate race (gate red while a sibling still runs) is a gate-race
+        # line naming GATE_WAIT_MAX_S; null: the same red with nothing running stays NOT REVIEWABLE.
+        for label, sib, want in (("gate red beside a running sibling", True, True),
+                                 ("null: gate red, nothing running", False, False)):
+            runs = [run_obj("gate", conclusion="failure")] + (
+                [run_obj("coverage", status="in_progress", conclusion=None, started=NOW)] if sib else [])
+            t = tick(prs=[pr_obj(76, H1)], required_names=("gate",), runs_at={H1: runs},
+                     bodies={76: "## Red checks\n\ngate: x\n"})
+            t.one_pr("PRS", pr_obj(76, H1), None, t.required("PRS"))
+            txt = [x["text"] for x in t.findings]
+            gr = [x for x in txt if x.startswith("#76: gate race at")]
+            nr = [x for x in txt if x.startswith("#76: NOT REVIEWABLE")]
+            a_, f_ = check(f"P82 {label}", [
+                ("gate race line " + ("names GATE_WAIT_MAX_S" if want else "absent"),
+                 (len(gr) == 1 and "GATE_WAIT_MAX_S" in gr[0]) if want else not gr),
+                ("NOT REVIEWABLE " + ("absent" if want else "present"), bool(nr) != want)])
+            total, failed = total + a_, failed + f_
+        # Carry 8: a reviewer's `merge_train.py --self-test` is not a second train; a null
+        # started_at cannot bound a run, so stuck() reads True (split_absent then reads ABSENT).
+        t = tick(procs=lambda pattern: [(11, "python3 merge_train.py"),
+                                        (12, "python3 tools/audit/seat/merge_train.py --self-test")])
+        t.train()
+        a_, f_ = check("carry 8 train self-test", [
+            ("a self-test beside one train is no merge race", not any("merge race" in x["text"] for x in t.findings)),
+            ("a null started_at is stuck, not live", t.stuck(None, 61.0)),
+            ("a fresh started_at is not stuck", not t.stuck(iso(NOW), 61.0))])
+        total, failed = total + a_, failed + f_
+
+        # ---- OWED buckets (carries 2-6): one bucket per open PR, one OWED line per owed one ----
+        h = lambda n: f"{n:040x}"
+        def oboard2(specs, red=None, fired=None, refs=(), cts=None, files=None, queue_v=None,
+                    train=None, body=None, bodies=None, disp=(), newer=None, newer_fail=(),
+                    extra=(), roster=None, extra_read=(), ancestor=True, via_prs=False):
+            """specs [(n, ms, [verdict lines], verdict_age_min)] -> (tick, owed lines).
+            disp: PR numbers on bus.sh's dispatch record at their head; newer {n: minutes ago}: a
+            handoff/<n> tip committed that long ago; newer_fail: PRs whose handoff ls-remote fails;
+            extra: PR objects beside the specs, whose comments the pass did not read."""
+            od = tmp / f"ob{len(list(tmp.iterdir()))}"
+            od.mkdir()
+            bus = od / "bus"
+            bus.mkdir()
+            (bus / "dispatched").write_text("".join(f"{n} {h(n)} thread {'0' * 32}\n" for n in disp))
+            qf = od / "q.json"
+            qf.write_text(json.dumps([{"pr": n, "verdict": v} for n, v in (queue_v or {}).items()]))
+            tl = None
+            if train is not None:
+                tl = str(od / "train.log")
+                Path(tl).write_text(train)
+            fl = None
+            if fired is not None:
+                fl = str(od / "fired.log")
+                Path(fl).write_text(fired)
+            board = [dict(pr_obj(n, h(n), ms=ms), body=(bodies or {}).get(n, "")) for n, ms, _, _ in specs]
+            board += list(extra)
+            t = tick(prs=board, queue=str(qf), train_log=tl, fired_log=fl, bus_state=str(bus), roster=roster)
+            t._git.h[:0] = [(("ls-remote", "origin", ref.rsplit("/", 1)[0] + "/*"), 0, f"{sha}\trefs/heads/{ref}\n")
+                            for ref, sha in refs] + [(("ls-remote",), 0, "")]
+            t._git.h[:0] = [(("log", "-1", "--format=%ct", sha), 0, f"{int((NOW - timedelta(minutes=m)).timestamp())}\n")
+                            for sha, m in (cts or {}).items()] + [(("fetch", "-q"), 0, ""), (("merge-base", "--is-ancestor"), 0, "")]
+            t._git.h[:0] = ([(("ls-remote", f"refs/heads/handoff/{n}"), 1, "fatal") for n in newer_fail]
+                            + [(("ls-remote", f"refs/heads/handoff/{n}"), 0, f"{n:x}".rjust(40, "d") + f"\trefs/heads/handoff/{n}\n")
+                               for n in (newer or {})]
+                            + [(("log", "-1", "--format=%ct", f"{n:x}".rjust(40, "d")), 0,
+                                f"{int((NOW - timedelta(minutes=m)).timestamp())}\n") for n, m in (newer or {}).items()])
+            if not ancestor:
+                t._git.h.insert(0, (("merge-base", "--is-ancestor"), 1, ""))
+            t._readback = {str(n): ls for n, _, ls, _ in specs}
+            t._readback.update({str(n): [] for n in extra_read})
+            t._verdict_at = {n: iso(NOW - timedelta(minutes=a)) for n, _, ls, a in specs if ls}
+            t._red = red or {}
+            t._files = files or {}
+            if via_prs:  # the whole PRS pass: the level must run in a real tick, not only when called
+                t.prs(["tests", "closures"])
+            else:
+                t.owed_levels("PRS", board)
+            return t, [x["text"] for x in t.sections.get("PRS", []) if x["flag"] and x["text"].startswith("OWED ")]
+        from datetime import timedelta
+        blk = lambda n: f"Fix review: blocked {h(n)}"
+        # P265: #2906 (blocked at head, ~9 h, no repair), #2917 (DIRTY), #2919 (red, no seat): one OWED line each
+        t_o, o1 = oboard2([(80, "BLOCKED", [blk(80)], 540), (81, "DIRTY", [], 0), (82, "BLOCKED", [], 0)],
+                          red={82: ["gate"]})
+        _, o_null = oboard2([(80, "BLOCKED", [blk(80)], 60)])
+        _, o_a = oboard2([(82, "BLOCKED", [], 0)], red={82: ["gate"]},
+                         fired=f"{iso(NOW - timedelta(minutes=40))} FIRED payload-fix-82-r5.json\n")
+        _, o_b = oboard2([(82, "BLOCKED", [], 0)], red={82: ["gate"]},
+                         refs=[("handoff-wip/82", "e" * 40)], cts={"e" * 40: 5})
+        _, o_c = oboard2([(82, "BLOCKED", [], 0)], red={82: ["gate"]},
+                         fired=f"{iso(NOW - timedelta(hours=9))} FIRED payload-fix-82-r5.json\n")
+        # P279: PARK lines after the last STARTED; P265 train bucket; card 8 re-cut
+        pk = "STARTED train.sh pid 1 over #83\nPARK #83 preflight: policy\nTRAIN DONE\n"
+        _, o_pk = oboard2([(83, "CLEAN", [f"Fix review: merge {h(83)}"], 5)], queue_v={83: h(83)}, train=pk)
+        _, o_pk0 = oboard2([(83, "CLEAN", [f"Fix review: merge {h(83)}"], 5)], queue_v={83: h(83)},
+                           train="PARK #83 preflight: policy\nSTARTED train.sh pid 1 over #83\nTRAIN DONE\n")
+        _, o_r3 = oboard2([(84, "CLEAN", [blk(84)] * 3, 5)])
+        _, o_r2 = oboard2([(84, "CLEAN", [blk(84)] * 2, 5)])
+        _, o_rc = oboard2([(84, "CLEAN", [blk(84)] * 3, 5)], bodies={84: "## Re-cut\nx"})
+        _, o_rm = oboard2([(84, "CLEAN", [f"Fix review: merge {h(84)}"] * 3, 5)])
+        # carry 5: BODY-AHEAD (handoff-body newer than the head, code handoff in the head)
+        ba = dict(refs=[("handoff/85", "c" * 40), ("handoff-body/85", "b" * 40)], cts={h(85): 100, "b" * 40: 30})
+        _, o_ba = oboard2([(85, "BLOCKED", [], 0)], **ba)
+        _, o_ba0 = oboard2([(85, "BLOCKED", [], 0)], refs=ba["refs"], cts={h(85): 20, "b" * 40: 30})
+        _, o_baf = oboard2([(85, "BLOCKED", [], 0)], fired=f"{iso(NOW - timedelta(minutes=10))} FIRED #85 r2\n", **ba)
+        # R10-TICK-LEVELS null controls: a DIRTY and red PR a bucket already owns prints no OWED line
+        rec = getattr(_module("record_row_tick", "tools/audit/seat/record_row.py"), "RECORD_BRANCH", "record")
+        bk_of = lambda t: t.sections["PRS"][-1]["text"]
+        gate_red = lambda n: {n: ["gate"]}
+        t_tr, o_tr = oboard2([(87, "DIRTY", [], 0)], red=gate_red(87), queue_v={87: h(87)},
+                             train="STARTED train.sh pid 1 over #87\n")
+        t_vd, o_vd = oboard2([(88, "DIRTY", [f"Fix review: merge {h(88)}"], 5)], red=gate_red(88))
+        t_vp, o_vp = oboard2([(89, "DIRTY", [], 0)], red=gate_red(89), disp=(89,))
+        t_vp0, o_vp0 = oboard2([(89, "DIRTY", [], 0)], red=gate_red(89))
+        t_wf, o_wf = oboard2([(90, "CLEAN", [], 0), (91, "DIRTY", [], 0)], red=gate_red(91),
+                             files={90: ["a.py"], 91: ["a.py"]})
+        _, o_wf0 = oboard2([(90, "CLEAN", [], 0), (91, "DIRTY", [], 0)], red=gate_red(91),
+                           files={90: ["a.py"], 91: ["b.py"]})
+        t_nw, o_nw = oboard2([(92, "BLOCKED", [blk(92)], 540)], newer={92: 30})
+        t_nf, o_nf = oboard2([(93, "BLOCKED", [blk(93)], 540)], newer_fail=(93,))
+        _, o_nw0 = oboard2([(92, "BLOCKED", [blk(92)], 540)], newer={92: 600})
+        _, o_na = oboard2([(85, "BLOCKED", [], 0)], refs=ba["refs"], cts={h(85): 100, "b" * 40: 30}, ancestor=False)
+        t_rc, o_rc2 = oboard2([(94, "CLEAN", [], 0)], extra=[pr_obj(95, h(95), ms="DIRTY", branch=rec),
+                                                              pr_obj(96, h(96), ms="DIRTY", draft=True),
+                                                              pr_obj(97, h(97), ms="DIRTY")],
+                              extra_read=(95, 96), red={95: ["gate"], 96: ["gate"], 97: ["gate"]})
+        t_pr, o_pr = oboard2([(98, "DIRTY", [], 0)], via_prs=True)
+        orf = tmp / "owed-roster.json"  # GB is after GA; GZ stands alone: the critical path is GA, GB
+        orf.write_text(json.dumps({"groups": [
+            {"group": "GA", "resume": {"stage": "not-started"}},
+            {"group": "GB", "resume": {"stage": "not-started"}, "after": ["GA"]},
+            {"group": "GZ", "resume": {"stage": "not-started"}}]}))
+        gpr = lambda n, g, ms="DIRTY": pr_obj(n, h(n), ms=ms, branch=f"fix/{g}")
+        t_ae, o_ae = oboard2([], extra=[gpr(90, "ga", "CLEAN"), gpr(91, "gb")], extra_read=(90, 91),
+                             red=gate_red(91), roster=str(orf))
+        _, o_ae0 = oboard2([], extra=[gpr(91, "gb")], extra_read=(91,), red=gate_red(91), roster=str(orf))
+        _, o_co = oboard2([], extra=[gpr(99, "gz"), gpr(100, "gb")], extra_read=(99, 100), roster=str(orf))
+        pd = tmp / "payloads"
+        pd.mkdir()
+        pf = pd / "payload-fix-86-r1.json"
+        pf.write_text("{}")
+        os.utime(pf, ((NOW - timedelta(minutes=60)).timestamp(),) * 2)
+        def fire_owed(fired):
+            fl = tmp / "fired-fo.log"
+            fl.write_text(fired)
+            tf = tick(prs=[], fired_log=str(fl), payload_dir=str(pd))
+            tf.payloads("PRS")
+            return [x["text"] for x in tf.sections.get("PRS", []) if x["text"].startswith("OWED fire-owed")]
+        fo, fo0 = fire_owed(""), fire_owed("FIRED payload-fix-86-r1.json\n")
+        pd2 = tmp / "payloads-young"
+        pd2.mkdir()
+        pf2 = pd2 / "payload-fix-86-r2.json"
+        pf2.write_text("{}")
+        os.utime(pf2, ((NOW - timedelta(minutes=FIRE_GRACE_MIN - 5)).timestamp(),) * 2)
+        tfy = tick(prs=[], fired_log=os.devnull, payload_dir=str(pd2))
+        tfy.payloads("PRS")
+        fo_young = [x["text"] for x in tfy.sections.get("PRS", []) if x["text"].startswith("OWED fire-owed")]
+        bk = t_o.sections["PRS"][-1]["text"]
+        a, f = check("OWED buckets", [
+            ("#2906 / #2917 / #2919 shapes each print one OWED line naming the reason",
+             len(o1) == 3 and "fixer-round #80" in o1[0] + o1[1] + o1[2] and any("dirty #81" in x for x in o1)
+             and any("red-unowned #82" in x and "red gate" in x for x in o1)),
+             ("null: blocked at head for 1 h (inside the round) prints nothing", o_null == []),
+            ("every open PR has exactly one bucket (count line sums to the PRs read)",
+             bk.startswith("buckets: ") and sum(int(x.rsplit(" ", 1)[1]) for x in bk[9:].split(", ")) == 3),
+            ("carry 6 arm (a): a payload-file FIRED line inside the window is a seat on it", o_a == []),
+            ("carry 6 arm (b): handoff-wip moved inside the window is a seat on it", o_b == []),
+            ("carry 6 null (c): neither, or a fire outside the window, is RED-UNOWNED",
+             len(o_c) == 1 and "red-unowned" in o_c[0]),
+            ("P279: a PARK after the last STARTED is owed naming the step; a PARK before it is in train",
+             len(o_pk) == 1 and "train-parked preflight: policy" in o_pk[0] and o_pk0 == []),
+            ("card 8: the third blocked verdict owes a re-cut; two, a recorded re-cut, and merges owe none",
+             len(o_r3) == 1 and "recut #84" in o_r3[0] and "3 blocked" in o_r3[0]
+             and o_r2 == [] and o_rc == [] and o_rm == []),
+            ("carry 5 BODY-AHEAD: a body ref newer than the head owes; an older one, or a fire, does not",
+             len(o_ba) == 1 and "body-ahead #85" in o_ba[0] and o_ba0 == [] and o_baf == []),
+            ("carry 5 FIRE-OWED: a rendered payload with no FIRED line owes; one a FIRED line names does not",
+             len(fo) == 1 and "payload-fix-86-r1.json" in fo[0] and fo0 == [] and fo_young == []),
+            ("null: a DIRTY, red PR in train (a queue verdict, no merge verdict) prints no OWED, names the bucket",
+             o_tr == [] and "train 1" in bk_of(t_tr)),
+            ("null: a DIRTY, red PR with a merge verdict at its head is verdicted, owed nothing",
+             o_vd == [] and "verdicted 1" in bk_of(t_vd)),
+            ("null: a DIRTY, red PR on the dispatch record is verdict-pending; off it, it is owed",
+             o_vp == [] and "verdict-pending 1" in bk_of(t_vp) and len(o_vp0) == 1 and "dirty #89" in o_vp0[0]),
+            ("null: a DIRTY, red PR sharing a file with a lower open PR is waiting-on it; a disjoint one is owed",
+             o_wf == [] and "waiting-on 1" in bk_of(t_wf) and len(o_wf0) == 1 and "dirty #91" in o_wf0[0]),
+            ("blocked arm: a handoff tip newer than the verdict is a fixer-round, an older one is owed",
+             o_nw == [] and "fixer-round 1" in bk_of(t_nw) and len(o_nw0) == 1 and "fixer-round #92" in o_nw0[0]),
+            ("O3: an unreadable handoff ref is UNREADABLE and no OWED line, never a stalled fixer-round",
+             o_nf == [] and "unreadable 1" in bk_of(t_nf)
+             and any(x["text"].startswith("UNREADABLE: owed buckets") and "#93" in x["text"] for x in t_nf.sections["PRS"])),
+            ("BODY-AHEAD: a code handoff that is not in the head is no repair done", o_na == []),
+            ("O4: the count line names what it leaves out (record branch, draft, comments unread) beside the buckets",
+             o_rc2 == [] and bk_of(t_rc) == "buckets: review-owed 1; not bucketed: comments unread 1, draft 1, record branch 1"),
+            ("a tick's PRS pass runs the level: a DIRTY PR prints its OWED line from prs(), not only from owed_levels()",
+             len(o_pr) == 1 and "dirty #98" in o_pr[0]),
+            ("null: a DIRTY, red PR whose group is after an open group is waiting-on it; with no open PR there it is owed",
+             o_ae == [] and "waiting-on 1" in bk_of(t_ae) and len(o_ae0) == 1 and "dirty #91" in o_ae0[0]),
+            ("the critical-path group's OWED line prints before a lower-numbered PR's outside it",
+             len(o_co) == 2 and "#100" in o_co[0] and "#99" in o_co[1])])
+        total, failed = total + a, failed + f
         # PRS (c): DIRTY names the conflicted files from git merge-tree first;
         # the claimnotes repair only for claim files alone (#2569's shape).
         claim = CLAIM_FILES[0]
@@ -4161,6 +4598,13 @@ def self_test() -> int:
         t_cr._carries = lambda v, hd: asked.append((v, hd)) or hd == h(64)
         t_cr.verdict_levels("PRS", cr_board)
         cr = [x for x in flagged(t_cr.sections.get("PRS", [])) if x.startswith("REVIEW OWED")]
+        # Carry 1 (P322): the record branch is never owed a review; a fix/ PR in the same state is.
+        rec_board = [dict(pr_obj(66, h(66)), headRefName="record/autofix"), pr_obj(67, h(67))]
+        rec_extra = [((f"issues/{n}/comments?per_page=100",), 0, json.dumps([[]])) for n in (66, 67)]
+        t_rec = tick(prs=rec_board, gh_extra=rec_extra, bus_state=str(tmp / "bus-ro"))
+        t_rec._git.on(("ls-remote",), out="")
+        t_rec.verdict_levels("PRS", rec_board)
+        rec = [x for x in flagged(t_rec.sections.get("PRS", [])) if x.startswith("REVIEW OWED")]
         (tmp / "bus-dir").mkdir()
         (tmp / "bus-dir" / "dispatched").mkdir()
         t_rb = tick(prs=ro_board, gh_extra=ro_extra, bus_state=str(tmp / "bus-dir"))
@@ -4171,6 +4615,8 @@ def self_test() -> int:
              ro == [f"REVIEW OWED: #62 {h(62)[:12]}"]),
             ("a head the newest merge verdict carries to owes no review; one it does not carry to does",
              cr == [f"REVIEW OWED: #65 {h(65)[:12]}"] and asked == [(h(70), h(64)), (h(70), h(65))]),
+            ("P322: a record/autofix PR at an unverdicted head prints no REVIEW OWED; the fix/ PR beside it does",
+             rec == [f"REVIEW OWED: #67 {h(67)[:12]}"]),
             ("an unreadable dispatch record is UNREADABLE and owes nothing it cannot know",
              any("UNREADABLE: bus dispatch record" in x for x in rb)
              and not any(x.startswith("REVIEW OWED") for x in rb)),
@@ -4324,6 +4770,8 @@ def main() -> int:
                          "CARRY (opt-in, weekly and at closure) runs only when named")
     ap.add_argument("--carry-last", type=int, default=CARRY_LAST,
                     help="CARRY: the merged pull requests the sweep reads")
+    ap.add_argument("--fired-log", help="the dispatch seat's FIRED ledger (OWED levels' seat-on-it test)")
+    ap.add_argument("--payload-dir", help="rendered cloud payloads (FIRE-OWED)")
     ap.add_argument("--json", action="store_true")
     ap.add_argument("--self-test", action="store_true")
     a = ap.parse_args()
@@ -4342,7 +4790,7 @@ def main() -> int:
              mandate_id=a.mandate_id,
              mandate_since_days=a.mandate_since_days,
              stall_hours=a.stall_hours, behind_max=a.behind_max,
-             carry_last=a.carry_last)
+             carry_last=a.carry_last, fired_log=a.fired_log, payload_dir=a.payload_dir)
     rep = t.run(only)
     print(json.dumps(rep, indent=1) if a.json else render(rep))
     return 0
diff --git a/tools/audit/seat/r10_ledger_mutants.py b/tools/audit/seat/r10_ledger_mutants.py
index 331858f75..84256aaf9 100644
--- a/tools/audit/seat/r10_ledger_mutants.py
+++ b/tools/audit/seat/r10_ledger_mutants.py
@@ -88,8 +88,8 @@ PLANTS = {
     # the tick reads the ledger
     "T1_unkinded_printed": (TICK, "            if len(f) > 2 and f[2] in lg.KINDS:", "            if True:"),
     "T2_no_reads_fold": (TICK, 'lg.fold(rows, getattr(self, "_live", None), getattr(self, "_readback", None))', "lg.fold(rows)"),
-    "T3_review_owed_silent": (TICK, "            for text in lg.review_owed(prs, self._readback, dispatched, self._carries):\n                self.line(S, text, flag=True)",
-                              "            for text in lg.review_owed(prs, self._readback, dispatched, self._carries):\n                pass"),
+    "T3_review_owed_silent": (TICK, '                                       getattr(rr, "RECORD_BRANCH", None)):\n                self.line(S, text, flag=True)',
+                              '                                       getattr(rr, "RECORD_BRANCH", None)):\n                pass'),
     "T4_no_escalation": (TICK, "                                aging, group_of):\n            self.line(S, text, flag=True)",
                          "                                aging, group_of):\n            pass"),
     "T5_no_design_build": (TICK, "        self.design_builds(S, rl, roster)\n", ""),
diff --git a/tools/pr/ci_predict.py b/tools/pr/ci_predict.py
index 702402563..450810418 100644
--- a/tools/pr/ci_predict.py
+++ b/tools/pr/ci_predict.py
@@ -329,9 +329,17 @@ def no_recording(root, base, changed, closure):
 # state_docs.py spawns. Recording the changed file's own self-test with CI's
 # recorder, then grading that record as its host's with CI's own `check`,
 # took 4.7 s and named both pairs CI named. A host counts only when its source
-# names the file within SELF_TEST_WINDOW lines of a self-test mention: a
-# script that lists a file as text (harness_headers' scan) does not run it.
+# names the file within SELF_TEST_WINDOW lines of a run of its self-test, by
+# the `--self-test` flag or the quoted `"self-test"` subcommand (tests/entities.py
+# runs tests/lane_skip.py that way): a script that lists a file as text
+# (harness_headers' scan) does not run it, and neither does one whose comment
+# nearby only says "self-test" (tests/entities.py spells a fixture `ledger.py
+# landed` twelve lines under such a comment).
 SELF_TEST_WINDOW = 12
+# The two spellings a script really runs a self-test by: the `--self-test` flag, and
+# the `self-test` subcommand as a quoted argv element (tests/entities.py runs
+# tests/lane_skip.py as `[sys.executable, ..., "self-test"]`).
+_RUNS_SELF_TEST = re.compile(r"--self[-_]test|[\"']self-test[\"']")
 SELF_TEST_TIMEOUT = 180
 _RECORD_DRIVER = ("import sys; sys.path.insert(0, 'tests'); import closure; "
                   "sys.exit(closure._exec_record(sys.argv[1], sys.argv[2], ['--self-test']))")
@@ -354,7 +362,7 @@ def self_test_hosts(root: Path, f: str, closures: dict) -> list[str]:
         except OSError:
             continue
         w = SELF_TEST_WINDOW
-        if any(re.search(r"self[-_]test", ln) for i, line in enumerate(lines) if name in line
+        if any(_RUNS_SELF_TEST.search(ln) for i, line in enumerate(lines) if name in line
                for ln in lines[max(0, i - w):i + w + 1]):
             hosts.append(script)
     return hosts
@@ -1383,7 +1391,7 @@ def self_test_reads_self_test(root: Path) -> int:
         far = "\n" * (SELF_TEST_WINDOW + 1)
         i = "tests/doc_claims.py"  # lists the file under inert_reads alone, and names its self-test
         (t / h).write_text("# runs throwaway_git.py\n# through its --self-test\n")
-        (t / n).write_text(f"# lists throwaway_git.py as text{far}# its own --self-test\n")
+        (t / n).write_text(f"# lists throwaway_git.py as text; the self-tests run elsewhere{far}# its own --self-test\n")
         (t / i).write_text("# throwaway_git.py --self-test\n")
         (t / f).write_text("# throwaway_git.py --self-test\n")
         listed = {h: [f, h], n: [f, n], f: [f]}
@@ -1425,6 +1433,21 @@ def self_test_reads_self_test(root: Path) -> int:
             good = ok(*got)
             print(f"  {'ok  ' if good else 'FAIL'} {label}{'' if good else ' -- ' + repr(got[0])}")
             bad += not good
+        # which source spellings make a host: a run by flag or by the `self-test` subcommand, not prose
+        sub = "tests/lane_skip.py"
+        spell = {
+            "tests/h_flag.py": f"r = run(['python3', '{sub}', '--self-test'])\n",
+            "tests/h_sub.py": f"subprocess.run([sys.executable, 'x/{Path(sub).name}', \"self-test\"])\n",
+            "tests/h_prose.py": f"# {Path(sub).name} has a self-test the gate runs elsewhere\n",
+            "tests/h_table.py": f"T = {{('{sub}', 'self_test'): 'a function name'}}\n",
+        }
+        for s, src in spell.items():
+            (t / s).write_text(src)
+        got = self_test_hosts(t, sub, {s: [sub] for s in spell})
+        good = got == ["tests/h_flag.py", "tests/h_sub.py"]
+        print(f"  {'ok  ' if good else 'FAIL'} a host runs the self-test by `--self-test` or the quoted `self-test` "
+              f"subcommand (lane_skip's shape); a comment, or a `self_test` table key, is no host{'' if good else ' -- ' + repr(got)}")
+        bad += not good
     return bad
 
 

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
