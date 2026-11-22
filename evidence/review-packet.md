# Review packet #3868
head: 273e5ece996438c799c6d246dc54f89e3f888e93
base: 1207ee13b0e439a4acefccabace691785af2ebad

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=137337824332 skipped
cancel-superseded id=137337829433 queued
prelude id=137337829262 queued
refresh id=137337829165 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified python3 -I -c "import sys; sys.path.insert(0, 'tools/audit/seat'); import corpus_mirror as m; d = lambda n: m.ITEM_QUERY % chr(10).join(m.ITEM_FIELDS % (k, k) for k in range(1, n + 1)); print([(n, m.formula_cost(d(n))) for n in (1, 30, 32, 33, 50)])"
             python3 runs an inline script rather than a file
  unverified git diff 1207ee13b0...HEAD -- tools/audit/seat/corpus_mirror.py | grep -c '^[-+]ITEM_FIELDS'
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         gh api -X GET search/issues -f q='repo:tvofi/heatpump_optimizer is:issue' --jq .total_count
             gh api: every long flag accepted
  ok         python3 -I tools/audit/seat/corpus_mirror.py --self-test
             `tools/audit/seat/corpus_mirror.py` is in the tree at this head
  ok         D=$(mktemp -d); python3 tests/closure.py select --diff 1207ee13b0 --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 4 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3868.md b/dev/programme/delivery/3868.md
new file mode 100644
index 0000000000..05fda45f87
--- /dev/null
+++ b/dev/programme/delivery/3868.md
@@ -0,0 +1 @@
+- [#3868](https://github.com/tvofi/heatpump_optimizer/pull/3868) — **open**, corpus_mirror: pace GraphQL item batches by query cost (owner tooling fix) (R11-OWNER-CORPUS-MIRROR-PACING)
diff --git a/tools/audit/seat/corpus_mirror.py b/tools/audit/seat/corpus_mirror.py
index 13f379873e..30908c33ca 100755
--- a/tools/audit/seat/corpus_mirror.py
+++ b/tools/audit/seat/corpus_mirror.py
@@ -54,6 +54,15 @@ repeating no page. Every page is cached with its ETag and re-read with
 If-None-Match: a 304 costs nothing against the primary limit, so a later round
 pays for what changed. It never calls a search endpoint and never writes: every
 call it issues passes gh_read.is_read or gh_read.is_query, or it stops.
+GraphQL is paced by cost on top (owner request, 2026-11-22): every query asks
+`rateLimit{cost remaining limit resetAt}`, and the next query waits until
+c*3600/limit seconds have passed after one of cost c, so the scan spends at most
+the hourly limit an hour; when the last cost would take what remains under the
+floor it sleeps until resetAt, a reset RESET_WAIT_CAP_S or more away pauses. A
+query of GRAPHQL_BATCH items costs at most QUERY_COST_CAP by formula_cost. A
+secondary limit naming a Retry-After up to SECONDARY_WAIT_CAP_S is waited out
+and the query asked once more; a longer one, a second one, or a spent bucket
+pauses. `cost` prints the costs the API answered.
 `cost` prints the calls per bucket this scan made (its own count; `gh_calls.py
 --top --since <scan start>` prints the shim's, from the log).
 
@@ -91,7 +100,15 @@ import gh_read  # noqa: E402 -- the read rule, the budget and its constants have
 
 REPO = "tvofi/heatpump_optimizer"
 NAMESPACES = ("refs/heads/", "refs/tags/", "refs/pull/")
-GRAPHQL_BATCH = 50
+#: Items per GraphQL query. By GitHub's documented formula (`formula_cost`) one item asks 308 requests -- each
+#: comment's and review's edit list is one request per parent node -- so 50 items cost 154 points and 30 cost 92:
+#: at most QUERY_COST_CAP, a query the secondary limit's compute budget is not fed in one call.
+GRAPHQL_BATCH = 30
+QUERY_COST_CAP = 100
+#: A secondary limit naming a Retry-After up to this is waited out and the query asked once more; past it, a pause.
+SECONDARY_WAIT_CAP_S = 300
+#: A GraphQL reset this far away or more is a pause at the cursor, never a sleep.
+RESET_WAIT_CAP_S = 3600
 RUN_WINDOW = 1000          # the run list serves at most this many rows per filter
 MAX_MEMBER = 64 * 2**20    # one extracted member
 MAX_ARCHIVE = 512 * 2**20  # one archive, extracted
@@ -104,7 +121,7 @@ SAVE_EVERY = 20
 UNSERVED = {"S5": ["a job's step summary: no endpoint (removal route: deleting the run)"],
             "S3": ["status contexts of commits that head no pull request: cost (enumerator: git rev-list --count --all)"]}
 
-ITEM_QUERY = """query($o:String!,$n:String!){repository(owner:$o,name:$n){%s}}"""
+ITEM_QUERY = """query($o:String!,$n:String!){rateLimit{cost remaining limit resetAt} repository(owner:$o,name:$n){%s}}"""
 ITEM_FIELDS = """i%d: issueOrPullRequest(number:%d){__typename
  ... on Issue{userContentEdits(first:50){nodes{editedAt diff}} comments(first:100){pageInfo{hasNextPage} nodes{databaseId userContentEdits(first:20){nodes{editedAt diff}}}}}
  ... on PullRequest{userContentEdits(first:50){nodes{editedAt diff}} comments(first:100){pageInfo{hasNextPage} nodes{databaseId userContentEdits(first:20){nodes{editedAt diff}}}}
@@ -124,6 +141,35 @@ def answered(state: str) -> bool:
     return state in ANSWERED or state.startswith("refused: ")
 
 
+def formula_cost(doc: str) -> int:
+    """GitHub's documented rate-limit cost of a query document: each connection (a field taking `first` or `last`)
+    asks one request per node of its parent, the parent's node count being the product of the first/last values of
+    the connections above it; the requests over 100, rounded, at least 1. Both arms of an inline fragment are
+    counted, so on a union field this is an upper bound; the API's own figure is each answer's `rateLimit.cost`."""
+    requests, scale, pending = 0, [1], None
+    for tok in re.finditer(r"\((?P<args>[^)]*)\)|(?P<open>\{)|\}", doc):
+        if tok.group("args") is not None:
+            n = re.search(r"\b(?:first|last)\s*:\s*(\d+)", tok.group("args"))
+            pending = int(n.group(1)) if n else None
+            requests += scale[-1] if n else 0
+        elif tok.group("open"):
+            scale.append(scale[-1] * (pending or 1))
+            pending = None
+        else:
+            scale.pop()
+    return max(1, round(requests / 100))
+
+
+def epoch(stamp) -> "float | None":
+    """An ISO 8601 UTC stamp (`2026-11-22T20:00:00Z`) -> seconds since the epoch; None when it is not one."""
+    import datetime
+    try:
+        t = datetime.datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
+    except ValueError:
+        return None
+    return t.timestamp() if t.tzinfo else None
+
+
 class Paused(Exception):
     """The scan stops at its cursor: the budget floor, or a rate-limit answer."""
 
@@ -264,6 +310,7 @@ class Mirror:
         self.cur = self._load("cursor.json", {"lists": {}, "items": {}, "calls": {}, "pass": 0, "state": "new"})
         self.man = self._load("MANIFEST.json", {"sources": {}})
         self.since_budget = gh_read.BATCH  # the first call is preceded by a budget read
+        self.gql: dict = {}  # the last GraphQL answer's rateLimit, and when the next query may start
         self.dirty = 0
 
     # ---- state -------------------------------------------------------------------
@@ -303,18 +350,55 @@ class Mirror:
     def _gate(self, argv, bucket: str):
         """Before every call: it is a read, it is no search, the budget holds, the gap has passed."""
         path = argv[3] if argv[2:3] == ["-i"] else (argv[2] if len(argv) > 2 else "")
-        if not (gh_read.is_read(argv) or gh_read.is_query(argv)) or path.lstrip("/").split("?")[0].split("/")[0] == "search":
+        query = argv[:2] + argv[3:] if argv[2:3] == ["-i"] else argv  # -i adds the headers to the output, nothing to the call
+        if not (gh_read.is_read(argv) or gh_read.is_query(query)) or path.lstrip("/").split("?")[0].split("/")[0] == "search":
             raise AssertionError("corpus_mirror issues only reads, and no search: " + " ".join(argv[:3]))
         if self.since_budget >= gh_read.BATCH:
             low = gh_read.below_floor(gh_read.budget(self.run), self.floor)
             if low:
                 raise Paused(f"budget: {', '.join(low)} below {self.floor:.0%} of its limit")
             self.since_budget = 0
-        if sum(self.cur["calls"].values()):
-            self.sleep(gh_read.MIN_GAP_S)
+        gap = gh_read.MIN_GAP_S if sum(self.cur["calls"].values()) else 0.0
+        if bucket == "graphql":
+            gap = max(gap, self.graphql_wait())
+        if gap > 0:
+            self.sleep(gap)
         self.since_budget += 1
         self.cur["calls"][bucket] = self.cur["calls"].get(bucket, 0) + 1
 
+    def graphql_wait(self) -> float:
+        """The wait before the next GraphQL query, from the last answer's rateLimit: a token bucket spending at most
+        limit/3600 points a second (a query of cost c holds the next one c*3600/limit s), and, when the last cost
+        would take what remains under the floor, the time to resetAt. A reset RESET_WAIT_CAP_S or more away pauses."""
+        g, now = self.gql, self.now()
+        if not g:
+            return 0.0
+        if g["remaining"] - g["cost"] < self.floor * g["limit"]:
+            wait = g["reset"] - now
+            if wait >= RESET_WAIT_CAP_S:
+                raise Paused(f"budget: graphql would go below {self.floor:.0%} of its limit, and its reset is {wait:.0f} s away")
+            return max(wait, g["next"] - now, 0.0)
+        return max(g["next"] - now, 0.0)
+
+    def observe(self, rate):
+        """Keep a GraphQL answer's `rateLimit{cost remaining limit resetAt}` for `graphql_wait`, and the costs seen."""
+        try:
+            cost, remaining, limit, reset = int(rate["cost"]), int(rate["remaining"]), int(rate["limit"]), epoch(rate["resetAt"])
+        except (TypeError, KeyError, ValueError):
+            return
+        if limit <= 0 or reset is None:
+            return
+        self.gql = {"cost": cost, "remaining": remaining, "limit": limit, "reset": reset, "next": self.now() + cost * 3600 / limit}
+        seen = self.cur.setdefault("graphql_cost", {"last": 0, "max": 0})
+        seen["last"], seen["max"] = cost, max(seen["max"], cost)
+
+    def secondary_wait(self, out: str) -> "float | None":
+        """The Retry-After (s) of a secondary-limit answer when it is at most SECONDARY_WAIT_CAP_S; else None."""
+        after = gh_read.parse_included(out)[1].get("retry-after", "")
+        if gh_read.SECONDARY in out.lower() and after.isdigit() and int(after) <= SECONDARY_WAIT_CAP_S:
+            return float(after)
+        return None
+
     def get(self, path: str, etag: str = ""):
         """A conditional REST read -> (state, body, etag): fresh, unchanged, gone or error:<what>."""
         self._gate(["gh", "api", "-i", path], "core")
@@ -328,24 +412,33 @@ class Mirror:
         return ("gone" if status in (404, 410) else f"error: HTTP {status or 'unread'}"), "", etag
 
     def query(self, doc: str, **fields):
-        """A GraphQL query -> (data or None, why)."""
-        argv = ["gh", "api", "graphql", "-f", "query=" + doc]
+        """A GraphQL query, read with its headers -> (data or None, why). A secondary limit naming a short
+        Retry-After is waited out and the query asked once more."""
+        argv = ["gh", "api", "-i", "graphql", "-f", "query=" + doc]
         for k, v in fields.items():
             argv += ["-f", f"{k}={v}"]
         self._gate(argv, "graphql")
 
         def attempt():
             code, out = self.run(argv)
-            return (out, None) if code == 0 else (None, out)
-        value, failure, _, _ = gh_read.retry(attempt, gh_read.gh_wait, self.sleep)
+            status, _, body = gh_read.parse_included(out)
+            return (body, None) if code == 0 and status is not None and 200 <= status < 300 else (None, out)
+        value, failure, _, _ = gh_read.retry(attempt, lambda f: gh_read.included_wait(f, self.now), self.sleep)
+        wait = None if failure is None else self.secondary_wait(failure)
+        if wait is not None:
+            self.sleep(wait)
+            value, failure, _, _ = gh_read.retry(attempt, lambda f: gh_read.included_wait(f, self.now), self.sleep)
         if failure is not None:
             if gh_read.RATE_LIMIT in failure.lower():
                 raise Paused("rate limit: a GraphQL answer names one")
             return None, gh_read.one_line(failure)[-80:]
         try:
-            return json.loads(value).get("data"), ""
+            data = json.loads(value).get("data")
         except (ValueError, AttributeError):
             return None, "not JSON"
+        if isinstance(data, dict):
+            self.observe(data.pop("rateLimit", None))
+        return data, ""
 
     def download(self, path: str, accept: str = ""):
         """A binary read -> (bytes or None, why)."""
@@ -463,6 +556,9 @@ class Mirror:
         numbers = sorted(i["number"] for i in issues if isinstance(i, dict) and isinstance(i.get("number"), int))
         owner, repo = self.repo.split("/", 1)
         batches = {f"{b[0]}-{b[-1]}": b for b in (numbers[k:k + GRAPHQL_BATCH] for k in range(0, len(numbers), GRAPHQL_BATCH))}
+        kept = self.cur["items"].setdefault("item batches", {})
+        for key in [key for key in kept if key not in batches]:
+            del kept[key]  # a batch of another partition (an earlier GRAPHQL_BATCH, a last batch since grown) is no unit of this one
 
         def batch(key):
             data, why = self.query(ITEM_QUERY % "\n".join(ITEM_FIELDS % (n, n) for n in batches[key]), o=owner, n=repo)
@@ -687,7 +783,8 @@ def main(argv: list[str]) -> int:
         return 2
     if a.cmd == "cost":
         cur = json.loads((root / "corpus" / "cursor.json").read_text())
-        print(f"corpus_mirror: pass {cur['pass']} ({cur['state']}), calls per bucket {json.dumps(cur['calls'], sort_keys=True)}")
+        print(f"corpus_mirror: pass {cur['pass']} ({cur['state']}), calls per bucket {json.dumps(cur['calls'], sort_keys=True)}, "
+              f"GraphQL cost per query as answered {json.dumps(cur.get('graphql_cost', {}), sort_keys=True)}")
         return 0
     if a.token_fd is None:
         print("corpus_mirror: REFUSED --token-fd names the descriptor the read credential is on (never a variable or an argument)")
@@ -724,6 +821,44 @@ class Stub:
         self.limit_download = 0  # the nth download answers a rate limit, once
         self.down: set[str] = set()  # a read whose path holds one of these answers 502, every time
         self.downloads: list[str] = []
+        self.events: list[tuple] = []  # ("call", argv) and ("sleep", s), in order
+        # GraphQL's own bucket, as each answer's rateLimit reports it: one query spends gql_cost, the reset refills it
+        self.gql_cost, self.gql_limit, self.gql_remaining, self.gql_min = 1, 5000, 5000, 5000
+        self.gql_reset = int(self.clock) + 1800
+        self.gql_fail: list[str] = []  # the next GraphQL calls answer these outputs, in order
+        self.gql_clocks: list[float] = []  # the clock at each GraphQL call
+
+    def sleep(self, s):
+        self.sleeps.append(s)
+        self.events.append(("sleep", s))
+        self.clock += s
+
+    def graphql(self, included: bool):
+        self.gql_clocks.append(self.clock)
+        if self.gql_fail:
+            return 1, self.gql_fail.pop(0)
+        while self.clock >= self.gql_reset:
+            self.gql_remaining, self.gql_reset = self.gql_limit, self.gql_reset + 3600
+        self.gql_remaining -= self.gql_cost
+        self.gql_min = min(self.gql_min, self.gql_remaining)
+        import datetime
+        reset = datetime.datetime.fromtimestamp(self.gql_reset, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
+        body = json.dumps({"data": {"rateLimit": {"cost": self.gql_cost, "remaining": self.gql_remaining, "limit": self.gql_limit, "resetAt": reset},
+                                    "repository": {"i1": {"__typename": "Issue"}}}})
+        return 0, (self.inc(200, [], body) if included else body)
+
+    def gql_gaps(self):
+        """The sleep just before each GraphQL call (None: no sleep)."""
+        out, last = [], None
+        for kind, x in self.events:
+            if kind == "sleep":
+                last = x
+            elif x[:2] == ["gh", "api"] and "graphql" in x[2:4]:
+                out.append(last)
+                last = None
+            elif x != ["gh", "api", "rate_limit"]:
+                last = None
+        return out
 
     @staticmethod
     def inc(status, headers=(), body="", tail=""):
@@ -745,13 +880,14 @@ class Stub:
 
     def run(self, argv):
         self.calls.append(list(argv))
+        self.events.append(("call", list(argv)))
         if argv == ["gh", "api", "rate_limit"]:
             return 0, json.dumps({"resources": {k: {"limit": 5000, "remaining": v, "reset": 9999} for k, v in self.remaining.items()}})
         k = sum(1 for c in self.calls if c != ["gh", "api", "rate_limit"])
         if k in self.limit_at:
             return 1, self.limit_at.pop(k)
-        if argv[:3] == ["gh", "api", "graphql"]:
-            return 0, json.dumps({"data": {"repository": {"i1": {"__typename": "Issue"}}}})
+        if "graphql" in argv[2:4]:
+            return self.graphql(argv[2] == "-i")
         path = argv[3]
         if any(d in path for d in self.down):
             return 1, self.inc(502, [], "", "gh: Bad Gateway (HTTP 502)\n")
@@ -886,10 +1022,13 @@ def cases(m) -> dict[str, bool]:
     spent = Stub.inc(403, [("X-Ratelimit-Remaining", "0"), ("X-Ratelimit-Reset", "4600")], '{"message": "API rate limit exceeded"}', "gh: (HTTP 403)\n")
 
     def mirror(root, stub, only=("S3",), floor=None, said=None):
-        mm = m.Mirror(root, run=stub.run, run_bytes=stub.run_bytes, git=stub.git, http=stub.http, new_bare=stub.new_bare, sleep=stub.sleeps.append,
+        mm = m.Mirror(root, run=stub.run, run_bytes=stub.run_bytes, git=stub.git, http=stub.http, new_bare=stub.new_bare, sleep=stub.sleep,
                       now=lambda: stub.clock, repo="o/r", site=site, say=(said if said is not None else []).append,
                       **({} if floor is None else {"floor": floor}))
-        return mm, mm.scan(list(only), "https://example.invalid/o/r", {})
+        try:
+            return mm, mm.scan(list(only), "https://example.invalid/o/r", {})
+        except AssertionError as e_:  # the gate refused a call: a FAIL of every case that scans, never a traceback
+            return mm, f"REFUSED {e_}"
 
     def issue_pages(stub):
         return [p for p in stub.fresh if "/issues?" in p]
@@ -903,9 +1042,9 @@ def cases(m) -> dict[str, bool]:
             rc == 0 and ma.cur["state"] == "complete" and whole == list(range(1, 251)) and len(issue_pages(a)) == 3 \
             and len(set(issue_pages(a))) == 3
         r["budget: rate_limit is read before the first call, and the gap is kept between calls"] = \
-            a.calls[0] == ["gh", "api", "rate_limit"] and len(a.sleeps) >= len(a.fresh) - 1 and set(a.sleeps) == {m.gh_read.MIN_GAP_S}
+            a.calls[0] == ["gh", "api", "rate_limit"] and a.events[1][0] == "call" and len(a.sleeps) >= len(a.fresh) - 1 and set(a.sleeps) == {m.gh_read.MIN_GAP_S}
         r["reads only: every gh call is a read or a query, and none names a search endpoint"] = \
-            all(m.gh_read.is_read(c) or m.gh_read.is_query(c) for c in a.calls if c[:1] == ["gh"]) \
+            all(m.gh_read.is_read(c) or m.gh_read.is_query(c[:2] + c[3:] if c[2:3] == ["-i"] else c) for c in a.calls if c[:1] == ["gh"]) \
             and not any("search" in " ".join(c) for c in a.calls)
         for label, answer in (("a secondary limit naming a long Retry-After", sec), ("a spent core bucket", spent)):
             b, said = Stub(), []
@@ -1165,18 +1304,132 @@ def cases(m) -> dict[str, bool]:
             and mg.man["sources"]["S5"]["unserved"] == m.UNSERVED["S5"] and ma.man["sources"]["S3"]["unserved"] == m.UNSERVED["S3"] \
             and stat.S_IMODE(os.stat(Path(td) / "a" / "corpus" / "MANIFEST.json").st_mode) == 0o600 \
             and stat.S_IMODE(os.stat(Path(td) / "a" / "corpus" / "pages" / "issues" / "1.json").st_mode) == 0o600
+        import math
+        n_batches = math.ceil(250 / m.GRAPHQL_BATCH)
+        paced = {}
+        for cost in (92, 46):
+            p_ = Stub()
+            p_.gql_cost = cost
+            mp, rc = mirror(Path(td) / f"pace{cost}", p_)
+            paced[cost] = (rc, mp.cur["state"], p_.gql_gaps(), mp)
+        want = {c_: c_ * 3600 / 5000 for c_ in paced}
+        r["graphql pace: after a query of cost c each GraphQL call waits c*3600/limit, proportional to the cost"] = \
+            all(rc == 0 and st == "complete" and len(gaps) == n_batches and gaps[0] == m.gh_read.MIN_GAP_S
+                and all(g_ is not None and abs(g_ - want[c_]) < 1e-6 for g_ in gaps[1:]) for c_, (rc, st, gaps, _) in paced.items())
+        stored = [json.loads(f_.read_text()) for f_ in (Path(td) / "pace92" / "corpus" / "graphql" / "items").glob("*.json")]
+        r["graphql pace: the rateLimit read for pacing is not stored with the items"] = \
+            len(stored) == n_batches and all("rateLimit" not in x and "repository" in x for x in stored)
+        r["graphql pace null: a query of cost 1 waits only the gap"] = \
+            set(a.gql_gaps()[1:]) == {m.gh_read.MIN_GAP_S}
+        fl, said = Stub(), []
+        fl.gql_cost, fl.gql_remaining = 92, 3300
+        reset0 = fl.gql_reset
+        mfl, rc = mirror(Path(td) / "gfloor", fl, said=said)
+        r["graphql floor: a query the last cost would take under the floor sleeps until resetAt (under an hour), and the scan completes"] = \
+            rc == 0 and mfl.cur["state"] == "complete" and fl.gql_min >= 0.6 * 5000 and reset0 in fl.gql_clocks \
+            and len([g_ for g_ in fl.gql_gaps() if g_ and g_ > 600]) == 1 and max(fl.sleeps) < 3600 \
+            and set(mfl.cur["items"]["item batches"].values()) == {"ok"} and not any("paused" in x for x in said)
+        ph, said = Stub(), []
+        ph.gql_cost, ph.gql_remaining, ph.gql_reset = 92, 3300, int(ph.clock) + 4000
+        mph, rc = mirror(Path(td) / "ghour", ph, said=said)
+        state1, done1 = mph.cur["state"], dict(mph.cur["items"].get("item batches", {}))
+        ph.clock = float(ph.gql_reset)  # the reset has come: the next run finds the bucket refilled
+        mph2, rc2 = mirror(Path(td) / "ghour", ph)
+        r["graphql floor: a reset an hour or more away pauses at the cursor instead of sleeping, and the run after it completes"] = \
+            rc == 0 and state1 == "paused" and any("paused" in x for x in said) and max(ph.sleeps) < 3600 \
+            and len(done1) == 3 and ph.gql_min >= 0.6 * 5000 - 92 \
+            and rc2 == 0 and mph2.cur["state"] == "complete" and set(mph2.cur["items"]["item batches"].values()) == {"ok"}
+        sec60 = Stub.inc(403, [("Retry-After", "60")], '{"message": "You have exceeded a secondary rate limit."}',
+                         "gh: You have exceeded a secondary rate limit. (HTTP 403)\n")
+        sec600 = sec60.replace("Retry-After: 60", "Retry-After: 600")
+        primary = Stub.inc(200, [("X-Ratelimit-Remaining", "0"), ("Retry-After", "60")], '{"errors": [{"type": "RATE_LIMITED", "message": "API rate limit exceeded for user ID 1."}]}',
+                           "gh: API rate limit exceeded for user ID 1.\n")
+        sec = {}
+        for label, fails in (("once", [sec60]), ("twice", [sec60, sec60]), ("long", [sec600]), ("primary", [primary])):
+            s_, said = Stub(), []
+            s_.gql_fail = list(fails)
+            ms_, rc = mirror(Path(td) / ("gsec" + label), s_, said=said)
+            sec[label] = (rc, ms_.cur["state"], len(s_.gql_clocks), s_.sleeps, ms_.cur["items"].get("item batches", {}), any("paused" in x for x in said))
+        rc, st, n_q, sl, items, paused = sec["once"]
+        r["graphql secondary: a secondary limit naming a 60 s Retry-After is waited out and the query retried once, and the scan completes"] = \
+            rc == 0 and st == "complete" and n_q == n_batches + 1 and sl.count(60.0) == 1 and len(items) == n_batches \
+            and set(items.values()) == {"ok"} and not paused
+        rc, st, n_q, sl, items, paused = sec["twice"]
+        r["graphql secondary: a second secondary answer after the one retry pauses at the cursor"] = \
+            rc == 0 and st == "paused" and paused and n_q == 2 and sl.count(60.0) == 1 and items == {}
+        r["graphql secondary: a Retry-After past the cap, or a spent primary bucket, pauses at once without sleeping"] = \
+            all(sec[k_][:3] == (0, "paused", 1) and sec[k_][5] and not [x for x in sec[k_][3] if x > 45] and sec[k_][4] == {} for k_ in ("long", "primary"))
+        fc = getattr(m, "formula_cost", None)
+        example = "query{viewer{login repositories(first:100){edges{node{id issues(first:50){edges{node{id labels(first:60){edges{node{id name}}}}}}}}}}}"
+        item_doc = lambda n_: m.ITEM_QUERY % "\n".join(m.ITEM_FIELDS % (k_, k_) for k_ in range(1, n_ + 1))  # noqa: E731
+        r["cost: GitHub's documented example costs 51 by the formula, and one item query of GRAPHQL_BATCH items stays under QUERY_COST_CAP"] = \
+            fc is not None and fc(example) == 51 and fc(item_doc(m.GRAPHQL_BATCH)) <= getattr(m, "QUERY_COST_CAP", 0) < fc(item_doc(m.GRAPHQL_BATCH + 3)) \
+            and (fc(item_doc(m.GRAPHQL_BATCH)), m.QUERY_COST_CAP) == (92, 100)
+        r["cost: the formula counts each connection once per parent node, rounds the hundreds and is at least 1"] = \
+            fc is not None and (fc("query{a(first:148){b(first:1){x}}}"), fc("query{a(first:100){b(first:100){c(first:100){x}}}}"),
+                                fc("query{viewer{login}}")) == (1, 101, 1)
+        z = Stub()
+        real_batch = m.GRAPHQL_BATCH
+        m.GRAPHQL_BATCH = 7
+        try:
+            mirror(Path(td) / "part", z)
+        finally:
+            m.GRAPHQL_BATCH = real_batch
+        mz, rc = mirror(Path(td) / "part", z)
+        uz = mz.man["sources"]["S3"]["units"]["item batches"]
+        r["partition: a batch key of another GRAPHQL_BATCH kept in the cursor is no unit of this pass: universe and examined count the current batches"] = \
+            rc == 0 and (uz["universe"], uz["examined"]) == (n_batches, n_batches) and len(mz.cur["items"]["item batches"]) == n_batches
+        w_ = Stub()
+        mw_ = m.Mirror(Path(td) / "unit", run=w_.run, run_bytes=w_.run_bytes, git=w_.git, http=w_.http, new_bare=w_.new_bare, sleep=w_.sleep,
+                       now=lambda: 1000.0, repo="o/r")
+        good = {"cost": 92, "remaining": 5000, "limit": 5000, "resetAt": "1970-01-01T01:00:00Z"}
+
+        def observed(rate):
+            mw_.gql = {}
+            try:
+                mw_.observe(rate)
+                return mw_.gql
+            except Exception as e_:  # noqa: BLE001 -- the defect: an answer's shape raises
+                return "RAISED " + type(e_).__name__
+        r["graphql observe: a rateLimit missing, malformed, with no positive limit or a reset that is no UTC stamp keeps no pacing state and never raises"] = \
+            all(observed(b_) == {} for b_ in (None, {}, {**good, "cost": "x"}, {**good, "limit": 0}, {**good, "limit": -5},
+                                              {**good, "resetAt": "not a time"}, {**good, "resetAt": "1970-01-01T01:00:00"})) \
+            and observed(good) == {"cost": 92, "remaining": 5000, "limit": 5000, "reset": 3600.0, "next": 1000.0 + 92 * 3600 / 5000} \
+            and observed({**good, "limit": 1})["limit"] == 1
+
+        def waited(remaining, reset, nxt):
+            mw_.gql = {"cost": 92, "remaining": remaining, "limit": 5000, "reset": reset, "next": nxt}
+            try:
+                return mw_.graphql_wait()
+            except m.Paused:
+                return "paused"
+        mw_.gql = {}
+        r["graphql wait: none before any answer; the pace at exactly the floor; the reset up to 3599 s and a pause at 3600; nothing once both are past"] = \
+            mw_.graphql_wait() == 0.0 and waited(3092, 9999.0, 1066.0) == 66.0 and waited(3091, 4599.0, 0.0) == 3599.0 \
+            and waited(3091, 4600.0, 0.0) == "paused" and waited(5000, 0.0, 900.0) == 0.0 and waited(3091, 990.0, 900.0) == 0.0
+        sw_ = lambda after, msg="You have exceeded a secondary rate limit.": mw_.secondary_wait(  # noqa: E731
+            Stub.inc(403, [("Retry-After", after)], json.dumps({"message": msg}), "gh: (HTTP 403)\n"))
+        r["graphql secondary: a Retry-After of 300 s is waited, 301 s is not, and a primary or unreadable one never"] = \
+            (sw_("300"), sw_("301"), sw_("60", "API rate limit exceeded"), sw_("soon")) == (300.0, None, None, None)
         j = Stub()
         mj = m.Mirror(Path(td) / "gate", run=j.run, run_bytes=j.run_bytes, git=j.git, http=j.http, new_bare=j.new_bare, sleep=j.sleeps.append, repo="o/r")
         blocked = []
         for argv in (["gh", "api", "-i", "search/issues?q=x"], ["gh", "api", "repos/o/r/issues", "-f", "title=x"],
-                     ["gh", "api", "graphql", "-f", "query=mutation{x}"], ["gh", "issue", "create"]):
+                     ["gh", "api", "graphql", "-f", "query=mutation{x}"], ["gh", "api", "-i", "graphql", "-f", "query=mutation{x}"],
+                     ["gh", "issue", "create"]):
             try:
                 mj._gate(argv, "core")
                 blocked.append(False)
             except AssertionError:
                 blocked.append(True)
         r["gate: a search path, a field write, a mutation or any other gh command stops the mirror before the call"] = \
-            blocked == [True] * 4 and j.calls == []
+            blocked == [True] * 5 and j.calls == []
+        try:
+            mj._gate(["gh", "api", "-i", "graphql", "-f", "query=query{x}"], "graphql")
+            admitted = True
+        except AssertionError:
+            admitted = False
+        r["gate null: a query read with its headers (-i) is admitted"] = admitted
     r["unmapped: only refs/ names outside heads, tags and pull count, each namespace once"] = \
         m.unmapped("a\tHEAD\nb\trefs/heads/x\nc\trefs/notes/a\nd\trefs/notes/b\ne\trefs/pull/1/merge\n") == ["refs/notes/"]
     r["links: relative and absolute same-site links are kept, another host and a fragment are cut"] = \
@@ -1192,8 +1445,28 @@ MUTANTS = {
     "pause on a limit": ('        if wait is not None:\n            raise Paused(f"rate limit: the answer names a {wait:.0f} s wait")\n', "", "pauses the scan at its cursor"),
     "floor": ("            if low:\n                raise Paused(", "            if False:\n                raise Paused(", "under 60 % pauses"),
     "budget first": ("        self.since_budget = gh_read.BATCH  # the first call is preceded by a budget read", "        self.since_budget = 0", "rate_limit is read before the first call"),
-    "gap": ('        if sum(self.cur["calls"].values()):\n            self.sleep(gh_read.MIN_GAP_S)\n', "", "gap is kept between calls"),
-    "reads only": ('        if not (gh_read.is_read(argv) or gh_read.is_query(argv)) or', "        if", "a field write, a mutation"),
+    "gap": ('        gap = gh_read.MIN_GAP_S if sum(self.cur["calls"].values()) else 0.0', "        gap = 0.0", "gap is kept between calls"),
+    "graphql paced": ('        if bucket == "graphql":\n            gap = max(gap, self.graphql_wait())\n', "", "proportional to the cost"),
+    "pace by cost": ('"next": self.now() + cost * 3600 / limit}', '"next": self.now()}', "proportional to the cost"),
+    "token bucket waited": ('        return max(g["next"] - now, 0.0)\n\n    def observe', "        return 0.0\n\n    def observe", "proportional to the cost"),
+    "rateLimit read": ('            self.observe(data.pop("rateLimit", None))', '            data.pop("rateLimit", None)', "proportional to the cost"),
+    "rateLimit not stored": ('            self.observe(data.pop("rateLimit", None))', '            self.observe(data.get("rateLimit"))', "not stored with the items"),
+    "floor before a query": ('        if g["remaining"] - g["cost"] < self.floor * g["limit"]:', "        if False:", "sleeps until resetAt"),
+    "expected cost": ('        if g["remaining"] - g["cost"] <', '        if g["remaining"] <', "sleeps until resetAt"),
+    "sleep to reset": ("            if wait >= RESET_WAIT_CAP_S:", "            if True:", "sleeps until resetAt"),
+    "reset past an hour": ("            if wait >= RESET_WAIT_CAP_S:", "            if False:", "an hour or more away pauses"),
+    "secondary retried": ("        if wait is not None:\n            self.sleep(wait)\n", "        if False:\n            self.sleep(wait)\n", "waited out and the query retried once"),
+    "secondary once": ("        if failure is not None:\n            if gh_read.RATE_LIMIT in failure.lower():\n                raise Paused(\"rate limit: a GraphQL",
+                       "        while failure is not None and self.secondary_wait(failure) is not None:\n            self.sleep(self.secondary_wait(failure))\n            value, failure, _, _ = gh_read.retry(attempt, lambda f: gh_read.included_wait(f, self.now), self.sleep)\n        if failure is not None:\n            if gh_read.RATE_LIMIT in failure.lower():\n                raise Paused(\"rate limit: a GraphQL",
+                       "after the one retry pauses"),
+    "secondary cap": ("int(after) <= SECONDARY_WAIT_CAP_S", "True", "past the cap, or a spent primary"),
+    "secondary only": ("        if gh_read.SECONDARY in out.lower() and after.isdigit()", "        if after.isdigit()", "past the cap, or a spent primary"),
+    "query read with -i": ('        query = argv[:2] + argv[3:] if argv[2:3] == ["-i"] else argv', "        query = argv", "a query read with its headers"),
+    "partition": ("            del kept[key]  #", "            pass  #", "no unit of this pass"),
+    "cost cap": ("GRAPHQL_BATCH = 30\n", "GRAPHQL_BATCH = 50\n", "stays under QUERY_COST_CAP"),
+    "formula per parent": ('            requests += scale[-1] if n else 0', '            requests += 1 if n else 0', "documented example costs 51"),
+    "formula nesting": ("            scale.append(scale[-1] * (pending or 1))", "            scale.append(scale[-1])", "documented example costs 51"),
+    "reads only": ('        if not (gh_read.is_read(argv) or gh_read.is_query(query)) or', "        if", "a field write, a mutation"),
     "no search": (' or path.lstrip("/").split("?")[0].split("/")[0] == "search":', ":", "a search path"),
     "etag sent": ('st["etags"].get(str(n), ""))', '"")', "If-None-Match"),
     "namespace exit": ("        return 1 if bad else 0\n", "        return 0\n", "a fourth namespace"),
diff --git a/tools/audit/seat/instruments/corpus_mirror.py.md b/tools/audit/seat/instruments/corpus_mirror.py.md
index 34a6534f36..01cc163783 100644
--- a/tools/audit/seat/instruments/corpus_mirror.py.md
+++ b/tools/audit/seat/instruments/corpus_mirror.py.md
@@ -17,6 +17,15 @@
     `paused` and exits 0; the next run resumes there. Every page is cached
     with its ETag and re-read with `If-None-Match`. It issues no search and no
     write, or stops.
+  - **GraphQL is paced by cost.** Each query asks `rateLimit{cost remaining
+    limit resetAt}`; after one of cost c the next waits c*3600/limit s (at
+    most the hourly limit an hour). When the last cost would take what
+    remains under the floor it sleeps until `resetAt`, and pauses only when
+    that is `RESET_WAIT_CAP_S` or more away. `GRAPHQL_BATCH` items per query,
+    at most `QUERY_COST_CAP` points by `formula_cost` (GitHub's documented
+    formula). A secondary limit naming a `Retry-After` up to
+    `SECONDARY_WAIT_CAP_S` is waited out and the query asked once more; a
+    longer one, a second one, or a spent bucket pauses. REST is unchanged.
   - **`MANIFEST.json`** holds each source's denominator (enumerator,
     universe, examined, not_reached with a reason) and the scan's state. A
     ref namespace outside heads, tags and pull is a `not_reached` line and a
@@ -30,13 +39,15 @@
     error, or that this host failed on, is `not_reached` in its pass and
     is read again by the next; a kept answer that is not `ok` (gone,
     refused) is `not_reached` in every pass and read once.
-  - `cost` prints the scan's own calls per bucket; `gh_calls.py --top --since
-    <scan start>` prints the shim's.
+  - `cost` prints the scan's own calls per bucket and the GraphQL costs the
+    API answered (last, max); `gh_calls.py --top --since <scan start>`
+    prints the shim's.
   - Not yet run against GitHub: the self-test stubs `gh`, `git` and HTTPS. An
     endpoint that does not serve what the script expects becomes a
     `not_reached` line, never a dropped row.
   `--self-test`: pause and exact resume under a secondary limit and a spent
-  bucket, the floor, the namespace assertion, hostile and unreadable
-  archives, the re-read of a unit that answered an error or that this host
-  failed on, and one
-  mutant per predicate.
+  bucket, GraphQL pacing proportional to cost, the sleep to a reset under an
+  hour and the pause past it, the one secondary-limit retry, the cost cap,
+  the floor, the namespace assertion, hostile and unreadable archives, the
+  re-read of a unit that answered an error or that this host failed on, and
+  one mutant per predicate.

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
