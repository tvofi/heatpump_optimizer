# Review packet #3682
head: d5ba8b8ce56ba02776b02a1143657a8c98aec4d9
base: ef6363d5f291e2eaa60620b5ea12d8d5fb902478

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arch-score / arch-score id=133530099094 success
arm id=133524287209 skipped
budget-raise-gate / budget-raise-gate id=133530099127 queued
cancel-superseded id=133526654069 queued
codeql id=133530102922 skipped
governance id=133530101821 skipped
hassfest id=133530101817 skipped
kernel-points id=133530102460 skipped
prelude id=133526654068 queued
refresh id=133526653585 queued
tests id=133530102432 skipped
validate id=133530102148 skipped

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
NOTE body item f2442280: dismissed:implemented on main at 0b276e8c0c, nothing left to build.
NOTE body item 53471b02: R11-INTAKE-R10-RESIDUE
NOTE body item 709d0ed0: dismissed:one file per distinct path (a handful), bounded by the paths the instruments read.
NOTE body item ee874351: R11-PRE-TOKEN-LEDGER
CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash tools/audit/seat/ancestry_calls.sh <prepr.sh>
             `tools/audit/seat/ancestry_calls.sh` is in the tree at this head
  ok         tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  ok         python3 tools/audit/seat/gh_calls.py --top --since <utc>
             `tools/audit/seat/gh_calls.py` is in the tree at this head
  ok         python3 tools/audit/seat/gh_read.py
             `tools/audit/seat/gh_read.py` is in the tree at this head
  ok         python3 tools/audit/seat/orchestrator_tick.py --self-test
             `tools/audit/seat/orchestrator_tick.py` is in the tree at this head
  ok         python3 tools/audit/seat/merge_train.py --self-test
             `tools/audit/seat/merge_train.py` is in the tree at this head
  ok         python3 tools/audit/seat/gh_calls.py --self-test
             `tools/audit/seat/gh_calls.py` is in the tree at this head
  ok         bash tools/audit/seat/seat_venv.sh --self-test
             `tools/audit/seat/seat_venv.sh` is in the tree at this head
  ok         bash tools/pr/prepr.sh --self-test
             `tools/pr/prepr.sh` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  unverified git merge-base --is-ancestor 0aead91cf4 origin/main && git merge-base --is-ancestor e899dde4ab origin/main
             `git merge-base` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git merge-base --is-ancestor 0aead91cf4 origin/main && git merge-base --is-ancestor e899dde4ab origin/main
             `git merge-base` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 11 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3682.md b/dev/programme/delivery/3682.md
new file mode 100644
index 0000000000..77918563da
--- /dev/null
+++ b/dev/programme/delivery/3682.md
@@ -0,0 +1 @@
+- [#3682](https://github.com/tvofi/heatpump_optimizer/pull/3682) — **open**, R10-GH-READ-RESIDUE-P3: conditional reads of rarely-changing objects, whole host call log, cheaper ancestry reads (R10-GH-READ-RESIDUE-P3)
diff --git a/tools/audit/seat/ancestry_calls.sh b/tools/audit/seat/ancestry_calls.sh
new file mode 100755
index 0000000000..e03f065e74
--- /dev/null
+++ b/tools/audit/seat/ancestry_calls.sh
@@ -0,0 +1,33 @@
+#!/bin/bash
+# usage: ancestry_calls.sh <prepr.sh file>
+# The calls one `ancestry_reds` read makes (tools/pr/prepr.sh) over a synthetic 520-commit all-green
+# branch and a 2-commit one, cold (the kept reads off): a stub gh counts each check-runs url and real jq
+# applies the filter. Run it at `git show origin/main:tools/pr/prepr.sh` and at the head to compare.
+set -u
+ROOT=$(cd "$(dirname "$0")/../../.." && pwd -P)
+. "$ROOT/tests/throwaway_git.sh" || exit 2
+SRC=$(realpath "${1:?usage: ancestry_calls.sh <prepr.sh>}"); W=$(mktemp -d); cd "$W"
+throwaway_git_env
+export GIT_AUTHOR_NAME=st GIT_AUTHOR_EMAIL=st@st GIT_COMMITTER_NAME=st GIT_COMMITTER_EMAIL=st@st GIT_AUTHOR_DATE='2005-04-07T22:13:13 +0000' GIT_COMMITTER_DATE='2005-04-07T22:13:13 +0000'
+throwaway_git_init . -q -b main && git remote add origin https://github.com/tvofi/heatpump_optimizer.git
+echo a > code; git add -A; git -c commit.gpgsign=false commit -qm base
+tree=$(git write-tree); parent=$(git rev-parse HEAD); first=$parent
+for i in $(seq 1 520); do parent=$(git commit-tree "$tree" -p "$parent" -m "c$i"); [ "$i" = 2 ] && two=$parent; done
+git update-ref refs/remotes/origin/long "$parent"; git update-ref refs/remotes/origin/two "$two"; git update-ref refs/remotes/origin/main main
+mkdir fix; for sha in $(git rev-list main..origin/long); do printf '{"total_count":1,"check_runs":[{"name":"fast (3.14)","status":"completed","conclusion":"success"}]}' >fix/$sha.json; done
+cat > gh <<'EOS'
+#!/bin/bash
+f=""; u=""; p=""
+for a in "$@"; do [ "$p" = "--jq" ] && f=$a; case "$a" in repos/*/commits/*/check-runs) u=$a ;; esac; p=$a; done
+echo "$u" >>"$CALLS"; s=${u#*/commits/}; s=${s%/check-runs}; exec jq -r "$f" "$FIX/$s.json"
+EOS
+chmod +x gh
+# the function text: from REDS_JQ= through the end of ancestry_reds, plus gh_credential
+awk '/^REDS_JQ=/{p=1} /^reds_line\(\)/{p=0} /^# Step 7c/{p=0} p' "$SRC" > fn.sh
+sed -i 's/^reds_line.*//' fn.sh
+. ./fn.sh
+export GITHUB_TOKEN=x PREPR_GH=$W/gh FIX=$W/fix PREPR_ANCESTRY_TTL_S=0 HPO_STATE_DIR=$W/state
+for br in long two; do : >"$W/calls"; export CALLS=$W/calls
+  out=$(ancestry_reds origin/$br); rc=$?
+  echo "$br rc=$rc commits=$(git rev-list main..origin/$br | wc -l) calls=$(wc -l <"$W/calls") out=[$out]"
+done
diff --git a/tools/audit/seat/gh_calls.py b/tools/audit/seat/gh_calls.py
index 9c84ebd98e..c20517bbf7 100644
--- a/tools/audit/seat/gh_calls.py
+++ b/tools/audit/seat/gh_calls.py
@@ -6,8 +6,11 @@
     gh_calls.py --self-test
 
 --top ranks callers (the parent command) and endpoints (subcommand + target)
-by call count, over $HPO_STATE_DIR/gh-calls.log and its rotated .1 (default
-state root $HOME/.local/state/hpo). `--since` keeps lines whose UTC stamp is
+by call count, over the host-wide log the shim writes, $HOME/.local/state/hpo/
+gh-calls.log (the token and its core bucket are host-wide), plus a distinct
+$HPO_STATE_DIR/gh-calls.log an older shim left, each with its rotated .1. With
+more than one source holding calls the report ends with a `sources:` table of
+each log's own count in the window; `--log PATH` reads that one file alone. `--since` keeps lines whose UTC stamp is
 not before it; a stamp is the shim's `YYYY-MM-DDTHH:MM:SSZ`, and a value that
 is not one is refused, never read as "everything". A line the shim did not
 write is counted and reported, not ranked. With no call logged in the window
@@ -50,6 +53,26 @@ def state_dir():
     return Path(os.environ.get("HPO_STATE_DIR") or Path.home() / ".local/state/hpo")
 
 
+def host_log() -> Path:
+    """The one host-wide log the installed shim writes (P669)."""
+    return Path.home() / ".local/state/hpo" / "gh-calls.log"
+
+
+def log_sources() -> "list[Path]":
+    """The logs --top reads: the host-wide one, then the caller's $HPO_STATE_DIR one
+    when it is a different file (a shim from before the host-wide log wrote there)."""
+    host, extra = host_log(), state_dir() / "gh-calls.log"
+    return [host] if extra.resolve() == host.resolve() else [host, extra]
+
+
+def source_table(logs, since, limit) -> str:
+    """The `sources:` table, or "" while at most one log holds a call in the window."""
+    rows = [(top(read_lines(p), since, limit)[3], p) for p in logs]
+    if sum(1 for n, _ in rows if n) < 2:
+        return ""
+    return "\n".join(["sources:"] + [f"  {n:6d}  {p}" for n, p in rows])
+
+
 def read_lines(log: Path):
     out = []
     for p in (Path(f"{log}.1"), log):
@@ -183,9 +206,10 @@ def self_test():
         gcs = w / "gh_comment.py"  # stands for the tree's tools/pr/gh_comment.py: the installer bakes its path in
         gcs.write_text("import subprocess, sys\nsys.exit(subprocess.run(['gh', *sys.argv[1:]]).returncode)\n")
 
-        def install(src_text):
+        def install(src_text, logdir=None):
             dst = w / "own" / "gh"
-            dst.write_text(src_text.replace("gcpy=@HPO_GH_COMMENT@\n", f"gcpy={gcs}\n"))
+            dst.write_text(src_text.replace("gcpy=@HPO_GH_COMMENT@\n", f"gcpy={gcs}\n")
+                           .replace("loghome=@HPO_GH_LOG_HOME@\n", f"loghome='{logdir or w / 'state'}'\n"))
             dst.chmod(0o700)
 
         # Hermetic PATH: the shim and the stub, plus a dir of symlinks to the few
@@ -213,10 +237,9 @@ def self_test():
         (w / "state").mkdir()
 
         def run(args, state=None, shim_text=None, stdin=b"IN\n", env_extra=None, path=None, via=None):
-            if shim_text is not None:
-                install(shim_text)
-            env = {"PATH": path or hermetic,
-                   "HPO_STATE_DIR": str(state or w / "state"), "HOME": str(w)}
+            # the installer fixes the log's directory in the shim: `state` is that directory
+            install(good if shim_text is None else shim_text, state or w / "state")
+            env = {"PATH": path or hermetic, "HPO_STATE_DIR": str(w / "ignored"), "HOME": str(w)}
             env.update(env_extra or {})
             cmd = [str(w / "own" / "gh"), *args] if via is None else ["sh", "-c", via]
             r = subprocess.run(cmd, input=stdin, capture_output=True, env=env, timeout=60)
@@ -230,6 +253,8 @@ def self_test():
         m = LINE.fullmatch(text.strip())
         check("one log line naming parent and path", bool(m) and m.group(4) == "api" and m.group(5) == "repos/o/r/pulls"
               and text.count("\n") == 1 and int(m.group(2)) == os.getpid() and "python" in m.group(3))
+        check("the call is logged at the install-fixed host log and never at the caller's HPO_STATE_DIR",
+              log.exists() and not (w / "ignored").exists())
         check("a -f body=secret argument never reaches the log", "secret" not in text and "body" not in text)
 
         run(["api", "-X", "POST", "repos/o/r/issues?per_page=9", "--input", "tokfile"])
@@ -798,6 +823,34 @@ def self_test():
                            capture_output=True, text=True, env={"PATH": f"{w / 'real'}:{tools}", "HOME": str(w)}, timeout=60)
         check("the CLI exits 3 with the line on an empty window",
               r.returncode == 3 and r.stdout.startswith("gh_calls: UNATTRIBUTED: no call logged since "))
+
+    # P669: one host-wide log, read whatever the reader's HPO_STATE_DIR
+    with tempfile.TemporaryDirectory() as h_:
+        h_ = Path(h_)
+        host = h_ / ".local/state/hpo"
+        host.mkdir(parents=True)
+        other = h_ / "session"
+        other.mkdir()
+        (host / "gh-calls.log").write_text("2026-11-11T06:30:00Z 1 merge_train.py api repos/o/r/rulesets\n" * 3)
+        (other / "gh-calls.log").write_text("2026-11-11T06:31:00Z 2 orchestrator_tick.py api repos/o/r/pulls\n")
+
+        def top_cli(state, *extra):
+            env = {"PATH": os.environ.get("PATH", ""), "HOME": str(h_)}
+            if state:
+                env["HPO_STATE_DIR"] = str(state)
+            return subprocess.run([sys.executable, "-I", __file__, "--top", *extra], capture_output=True, text=True,
+                                  env=env, timeout=60)
+        a_, b_ = top_cli(None), top_cli(other)
+        check("a call written with HPO_STATE_DIR unset is counted by --top with it set to another dir",
+              "gh calls: 4" in b_.stdout and "merge_train.py" in b_.stdout and "orchestrator_tick.py" in b_.stdout)
+        check("a call under another HPO_STATE_DIR is counted by --top with HPO_STATE_DIR unset: the host log alone reads 3",
+              "gh calls: 3" in a_.stdout)
+        check("the report labels each source's own count", "sources:" in b_.stdout
+              and f"       3  {host / 'gh-calls.log'}" in b_.stdout and f"       1  {other / 'gh-calls.log'}" in b_.stdout)
+        check("null control: one log with one call prints today's tables, no sources table",
+              "sources:" not in a_.stdout and "gh calls: 3" in a_.stdout
+              and a_.stdout.rstrip("\n") == render_top(read_lines(host / "gh-calls.log")))
+        check("--log reads that file alone", "gh calls: 1" in top_cli(None, "--log", str(other / "gh-calls.log")).stdout)
     print(f"gh_calls self-test: {pass_n + fail_n} checks, {fail_n} failed")
     return 1 if fail_n else 0
 
@@ -806,12 +859,12 @@ def main(argv):
     a = list(argv)
     if "--self-test" in a:
         return self_test()
-    log = state_dir() / "gh-calls.log"
+    logs = log_sources()
     since = None
     limit = 10
     try:
         if "--log" in a:
-            log = Path(a[a.index("--log") + 1])
+            logs = [Path(a[a.index("--log") + 1])]
         if "--since" in a:
             since = a[a.index("--since") + 1]
         if "--limit" in a:
@@ -828,7 +881,9 @@ def main(argv):
         return 0
     if "--top" in a:
         try:
-            rc, text = top_report(read_lines(log), since, limit, os.environ.get("PATH", ""))
+            rc, text = top_report([x for p in logs for x in read_lines(p)], since, limit, os.environ.get("PATH", ""))
+            table = source_table(logs, since, limit) if rc == 0 else ""
+            text += f"\n{table}" if table else ""
         except ValueError as e:
             print(f"gh_calls: {e}", file=sys.stderr)
             return 2
diff --git a/tools/audit/seat/gh_read.py b/tools/audit/seat/gh_read.py
index 3adc4df52c..291ab3deaf 100644
--- a/tools/audit/seat/gh_read.py
+++ b/tools/audit/seat/gh_read.py
@@ -32,12 +32,15 @@ its self-test drives both over its alternatives table and compares them.
 from __future__ import annotations
 
 import email.utils
+import hashlib
 import json
+import os
 import http.client
 import re
 import sys
 import time
 import urllib.error
+from pathlib import Path
 from typing import Callable
 
 READ_TRIES = 4
@@ -240,6 +243,116 @@ def read_pages(read, path: str, key: str = "", per_page: int = PER_PAGE, max_pag
     return 1, None, f"{path}: more than {max_pages} pages of {per_page}: refused, not truncated"
 
 
+# ----------------------------------------------------- conditional (ETag) reads
+# (no module-level re.compile here: ALTERNATIVES() reads those as the bash twin's table)
+#: A conditional read the server answers 304 costs no core-bucket call (P596 measured
+#: five of them moving `used` by 0, five plain reads by 6). The stored ETag and body sit
+#: under the state directory, one file per path, shared by every process of the host.
+
+
+def etag_dir() -> Path:
+    return Path(os.environ.get("HPO_STATE_DIR") or Path.home() / ".local/state/hpo") / "gh-etag"
+
+
+def parse_include(out: str) -> "tuple[int | None, dict, str]":
+    """`gh api -i`'s output -> (status, lower-cased headers, body); status None when the
+    output holds no response status line (a transport failure, or an error gh printed itself)."""
+    head, _, body = out.replace("\r\n", "\n").partition("\n\n")
+    lines = head.splitlines()
+    m = re.match(r"HTTP/\S+ (?P<code>[0-9]{3})\b", lines[0]) if lines else None
+    if m is None:
+        m2 = [GH_STATUS.search(x) for x in out.splitlines()]
+        code = next((int(x.group("code")) for x in reversed(m2) if x), None)
+        return code, {}, ""
+    headers = {k.strip().lower(): v.strip() for k, _, v in (x.partition(":") for x in lines[1:])}
+    return int(m.group("code")), headers, body
+
+
+def _etag_file(path: str, cache: Path) -> Path:
+    return cache / (hashlib.sha256(path.encode()).hexdigest()[:32] + ".json")
+
+
+def conditional_get(run, path: str, cache: "Path | None" = None) -> "tuple[int, str]":
+    """The body of the single-page GET at <path> -> (code, body); code != 0 is UNREADABLE and
+    the body then holds gh's output. `run(argv)` -> (code, output) is the caller's runner.
+
+    With an ETag stored for <path> the read sends If-None-Match: a 304 serves the stored
+    body, a 200 replaces both. With none stored (or a stored file that does not parse) it
+    is the plain read. Any other status, or a transport failure, is UNREADABLE as a plain
+    read's: a stale body is never served on a failure. A page past one page is no caller's:
+    it reads one page and no Link header is followed."""
+    cache = cache or etag_dir()
+    f = _etag_file(path, cache)
+    stored = None
+    try:
+        got = json.loads(f.read_text())
+        if isinstance(got.get("etag"), str) and isinstance(got.get("body"), str) and got["etag"]:
+            stored = got
+    except (OSError, ValueError, AttributeError):
+        pass
+    argv = ["gh", "api", "-i"] + (["-H", f"If-None-Match: {stored['etag']}"] if stored else []) + [path]
+    code, out = run(argv)
+    status, headers, body = parse_include(out)
+    if status == 304 and stored:
+        return 0, stored["body"]
+    if code or status != 200:
+        return code or 1, out
+    etag = headers.get("etag", "")
+    if etag:
+        try:
+            cache.mkdir(parents=True, exist_ok=True)
+            tmp = f.with_name(f"{f.name}.{os.getpid()}.tmp")
+            tmp.write_text(json.dumps({"etag": etag, "body": body}))
+            os.replace(tmp, f)
+        except OSError:
+            pass  # an unwritable state dir is the plain read, never a failure
+    return 0, body
+
+
+def ruleset_checks(run, repo: str, name: str, cache: "Path | None" = None) -> "tuple[bool, dict]":
+    """(read ok, the `required_status_checks` rule's parameters) of the ruleset called <name>,
+    both reads conditional (`conditional_get`). A ruleset list holding the name other than
+    once, or a body that is not the shape GitHub sends, is not read."""
+    code, out = conditional_get(run, f"repos/{repo}/rulesets", cache)
+    try:
+        ids = [r["id"] for r in json.loads(out) if r.get("name") == name] if not code else []
+        if len(ids) != 1 or not isinstance(ids[0], int):
+            return False, {}
+        code, out = conditional_get(run, f"repos/{repo}/rulesets/{ids[0]}", cache)
+        if code:
+            return False, {}
+        rules = [r for r in json.loads(out)["rules"] if r.get("type") == "required_status_checks"]
+    except (ValueError, TypeError, KeyError, AttributeError):
+        return False, {}
+    return True, (rules[0].get("parameters") or {}) if rules else {}
+
+
+def required_contexts(params: dict) -> "set[str]":
+    """The context names a `required_status_checks` rule's parameters require."""
+    return {c["context"].strip() for c in params.get("required_status_checks") or []
+            if isinstance(c, dict) and isinstance(c.get("context"), str) and c["context"].strip()}
+
+
+def fake_ruleset(argv, rid: str, contexts: str, strict: "str | None" = None, name: str = "main-protect-checks"):
+    """The self-tests' GitHub for the two ruleset paths: <contexts> (newline-separated, "" the
+    ruleset unreadable, a 404) answered as `gh api -i`, with an ETag a matching If-None-Match
+    turns into a 304 -- gh's own rc 1. The one fake both instruments' self-tests share."""
+    if not contexts:
+        return 1, "gh: Not Found (HTTP 404)"
+    path = next(a for a in argv if a.startswith("repos/"))
+    if path.endswith("/rulesets"):
+        body = json.dumps([{"id": int(rid), "name": name}])
+    else:
+        params = {"required_status_checks": [{"context": c} for c in contexts.splitlines() if c.strip()]}
+        if strict in ("true", "false"):  # anything else: the key absent, an unreadable policy
+            params["strict_required_status_checks_policy"] = strict == "true"
+        body = json.dumps({"rules": [{"type": "required_status_checks", "parameters": params}]})
+    etag = '"' + hashlib.sha256(body.encode()).hexdigest()[:16] + '"'
+    if f"If-None-Match: {etag}" in argv:
+        return 1, f"HTTP/2.0 304 Not Modified\nEtag: {etag}\n\ngh: HTTP 304"
+    return 0, f"HTTP/2.0 200 OK\nEtag: {etag}\nContent-Type: application/json\n\n{body}"
+
+
 def one_line(failure) -> str:
     return " ".join(str(failure).split())
 
@@ -632,6 +745,64 @@ def self_test() -> int:
     check("an unparseable page is a failure (rc 1), never an empty list",
           code == 1 and items is None and why.startswith("page 1 of repos/o/r/x is not JSON"))
 
+
+    # ---- conditional reads (P596, P625): one helper, the ETag and body under the state dir
+    import tempfile
+    with tempfile.TemporaryDirectory() as cd:
+        cache = Path(cd)
+        seen: list = []
+        world = {"body": '{"v": 1}', "etag": '"e1"', "rc": 0}
+
+        def gh_(argv):
+            seen.append(list(argv))
+            inm = next((a for a in argv if a.startswith("If-None-Match: ")), None)
+            if world["rc"]:
+                return 1, "gh: Bad Gateway (HTTP 502)"
+            if inm == f"If-None-Match: {world['etag']}":
+                return 1, f"HTTP/2.0 304 Not Modified\nEtag: {world['etag']}\n\ngh: HTTP 304"
+            return 0, f"HTTP/2.0 200 OK\r\nEtag: {world['etag']}\r\nX-A: b\r\n\r\n{world['body']}"
+
+        P = "repos/o/r/rulesets"
+        check("null control: with no stored ETag the plain read is made (no If-None-Match)",
+              conditional_get(gh_, P, cache) == (0, '{"v": 1}') and not any("If-None-Match" in a for a in seen[0]))
+        code, body = conditional_get(gh_, P, cache)
+        check("a 304 serves the stored body, from one request that carried the stored ETag",
+              (code, body) == (0, '{"v": 1}') and len(seen) == 2 and "If-None-Match: \"e1\"" in seen[1])
+        world.update(body='{"v": 2}', etag='"e2"')
+        check("a 200 replaces the stored body and ETag", conditional_get(gh_, P, cache) == (0, '{"v": 2}')
+              and json.loads(_etag_file(P, cache).read_text()) == {"etag": '"e2"', "body": '{"v": 2}'})
+        check("and the next read is the 304 of the new ETag", conditional_get(gh_, P, cache) == (0, '{"v": 2}')
+              and "If-None-Match: \"e2\"" in seen[-1])
+        world["rc"] = 1
+        code, out = conditional_get(gh_, P, cache)
+        check("any other failure is UNREADABLE, the stored body never served", code != 0 and "502" in out)
+        world["rc"] = 0
+        _etag_file(P, cache).write_text("{not json")
+        n0 = len(seen)
+        check("a corrupt stored file is the plain read", conditional_get(gh_, P, cache)[0] == 0
+              and not any("If-None-Match" in a for a in seen[n0]))
+        check("one stored file per path", conditional_get(gh_, P + "/7", cache)[0] == 0
+              and len(list(cache.glob("*.json"))) == 2)
+        check("a 304 with nothing stored is UNREADABLE, never an empty body",
+              conditional_get(lambda argv: (1, "HTTP/2.0 304 Not Modified\n\ngh: HTTP 304"), "repos/o/r/x", cache)[0] != 0)
+        # the ruleset reads: two reads each cold, none warm; the shared fake is the server
+        calls = []
+
+        def srv(argv):
+            calls.append(argv)
+            return fake_ruleset(argv, "7", "tests\nclosures\n", "true")
+        with tempfile.TemporaryDirectory() as cd2:
+            ok, params = ruleset_checks(srv, "o/r", "main-protect-checks", Path(cd2))
+            ok2, params2 = ruleset_checks(srv, "o/r", "main-protect-checks", Path(cd2))
+            check("ruleset_checks reads the required set and the strict flag",
+                  ok and [c["context"] for c in params["required_status_checks"]] == ["tests", "closures"]
+                  and params["strict_required_status_checks_policy"] is True and (ok2, params2) == (ok, params))
+            check("a warm ruleset read serves both reads as 304s: 4 calls, the second pair conditional",
+                  len(calls) == 4 and all("If-None-Match" in " ".join(c) for c in calls[2:])
+                  and not any("If-None-Match" in " ".join(c) for c in calls[:2]))
+            check("a ruleset by another name is not read",
+                  ruleset_checks(srv, "o/r", "other", Path(cd2)) == (False, {}))
+            check("an unreadable ruleset is not read", ruleset_checks(lambda a: (1, "HTTP 404"), "o/r", "x", Path(cd2)) == (False, {}))
     print(f"gh_read self-test: {passed + failed} checks, {failed} failed")
     return 1 if failed else 0
 
diff --git a/tools/audit/seat/instruments/gh_calls.py.md b/tools/audit/seat/instruments/gh_calls.py.md
index 32518a114a..92a6f9cc3f 100644
--- a/tools/audit/seat/instruments/gh_calls.py.md
+++ b/tools/audit/seat/instruments/gh_calls.py.md
@@ -2,7 +2,7 @@
 
 - `gh_calls.py` — the reader of the `shims/seat-gh` log. `--top [--since <utc>]
   [--limit N] [--log PATH]` ranks parent commands and `gh` endpoints by count
-  over the log and its `.1`; a malformed `--since` is refused (rc 2). `--coverage
+  over the host-wide log the shim writes (`$HOME/.local/state/hpo/gh-calls.log`) and a distinct `$HPO_STATE_DIR/gh-calls.log` an older shim left, each with its `.1`, ending in a `sources:` table of each log's count when more than one holds calls; a malformed `--since` is refused (rc 2). `--coverage
   [PID ...]` reads `/proc/<pid>/environ` (Linux) of each pid, or of every known
   daemon process, and says whether the first `gh` on its `PATH` is the shim.
   `--self-test` drives the shim against a stub gh: the byte, stderr and status
diff --git a/tools/audit/seat/instruments/gh_read.py.md b/tools/audit/seat/instruments/gh_read.py.md
index 4071c9f414..2b8c53d03c 100644
--- a/tools/audit/seat/instruments/gh_read.py.md
+++ b/tools/audit/seat/instruments/gh_read.py.md
@@ -16,4 +16,10 @@
   failure (401, a permission 403, 404, 422, an unclassified one) after its one
   call, a spent budget with its last error and the attempt count; a write is
   never retried. Its `self_test()` runs inside `record_row.py`'s. A workflow
-  step reads through `gh_read_run.py`.
+  step reads through `gh_read_run.py`. `conditional_get` is the one ETag-conditional
+  read of a single-page GET (`gh api -i`, `If-None-Match` from the ETag stored under
+  `$HPO_STATE_DIR/gh-etag/`, shared by every process): a 304 serves the stored body, a 200
+  replaces it, any other failure is UNREADABLE as a plain read's; `ruleset_checks` reads
+  the required-status-checks rule through it for `merge_train.py` and `orchestrator_tick.py`,
+  and the tick's comment and check-run reads go through it too. When: a seat instrument's
+  repeated read of an object that changes rarely.
diff --git a/tools/audit/seat/instruments/prepr.sh.md b/tools/audit/seat/instruments/prepr.sh.md
index a3a553f1b7..71116da98a 100644
--- a/tools/audit/seat/instruments/prepr.sh.md
+++ b/tools/audit/seat/instruments/prepr.sh.md
@@ -4,4 +4,4 @@
   freshness, claim files byte-identical, the MODE line, carry destinations,
   body headings, and the scoped-closure selection. When: always, before
   handing a branch off. Refusal: each blocked reason names the artifact —
-  a branch that fails prepr locally would have burned a review round instead.
+  a branch that fails prepr locally would have burned a review round instead. The ancestry-reds read makes one call per commit of the branch, carrying the red names, the run total and any pending run; a read with no run pending is kept an hour under `$HPO_STATE_DIR/prepr-ancestry/` (`PREPR_ANCESTRY_TTL_S`), so a repeat run reads only what changed.
diff --git a/tools/audit/seat/instruments/shims_seat-gh.md b/tools/audit/seat/instruments/shims_seat-gh.md
index 691b6a3bb0..70dbcc5587 100644
--- a/tools/audit/seat/instruments/shims_seat-gh.md
+++ b/tools/audit/seat/instruments/shims_seat-gh.md
@@ -2,7 +2,7 @@
 
 - `shims/seat-gh` — installed as `gh` by `seat_venv.sh --install-shims <dir>`.
   Appends `<utc> <parent pid> <parent, 80 chars> <subcommand> <target>`
-  to `$HPO_STATE_DIR/gh-calls.log` (target: the api path with its query cut, or
+  to ONE host-wide log, `gh-calls.log` in the directory `--install-shims` fixes (the installing user's `$HOME/.local/state/hpo`), whatever `HPO_STATE_DIR` the caller holds (target: the api path with its query cut, or
   the `pr`/`run` verb), never a flag's value or a body. The parent is the caller's argv[0] basename and, for a shell or interpreter, at most one more word: its script or `-m <module>` as given, or the flag name alone of a `-c`, `-e`, `-s`, `--eval`, `--print` or `--command` option, attached code cut off. Known no-value letters are passed over; a known value-taking one (python `-W`/`-X`, shell `-o`/`-O`) ends the field unlogged, as does any other option, so a script after such an option is not named. The field is cleaned and cut to 80 characters. Residual, by design: argv[0] and a script path are logged, so a value placed in a path is logged too (`sh ./T=v/s` logs `sh ./T?v/s`). A token outside
   `[A-Za-z0-9_./:-]` is logged `?`. Then execs the first real `gh` on `PATH`
   (a regular executable without the line-2 marker `# hpo-gh-shim`): stdin,
diff --git a/tools/audit/seat/merge_train.py b/tools/audit/seat/merge_train.py
index 033fe4f591..1b3d9ee510 100644
--- a/tools/audit/seat/merge_train.py
+++ b/tools/audit/seat/merge_train.py
@@ -4040,26 +4040,24 @@ class Train:
     def tree(self, rev: str) -> str:
         return self.git("rev-parse", f"{rev}^{{tree}}")
 
-    def _checks_rule(self, field: str) -> "tuple[bool, str]":
-        """RULESET's required_status_checks rule's <field> (a jq path under
-        .parameters), read live: (read ok, the jq output)."""
-        code, rid = self.run(["gh", "api", f"repos/{self.repo}/rulesets", "--jq",
-                              f'.[] | select(.name == "{RULESET}") | .id'])
-        code2, o = self.run(["gh", "api", f"repos/{self.repo}/rulesets/{rid.strip()}", "--jq",
-                             '.rules[] | select(.type == "required_status_checks") | .parameters' + field])
-        return not (code or code2 or not rid.strip().isdigit()), o
+    def _checks_rule(self) -> "tuple[bool, dict]":
+        """RULESET's required_status_checks rule's parameters, read live through
+        `gh_read.ruleset_checks`: both reads conditional, their ETag and body shared
+        with every other process of the host (a 304 costs no core-bucket call)."""
+        return gh_read.ruleset_checks(self.run, self.repo, RULESET)
 
     def strict_update(self) -> "bool | None":
         """Whether RULESET requires a branch up to date before its merge
         (`strict_required_status_checks_policy`), read live; None unreadable."""
-        ok, o = self._checks_rule(".strict_required_status_checks_policy")
-        return {"true": True, "false": False}.get(o.strip()) if ok else None
+        ok, params = self._checks_rule()
+        got = params.get("strict_required_status_checks_policy")
+        return got if ok and isinstance(got, bool) else None
 
     def required(self, pr_head: bool = False) -> list[str]:
         """The ruleset's required contexts, read live; less PR_ONLY unless
         <pr_head> (a pull request's head carries those; main and a proof never)."""
-        ok, o = self._checks_rule(".required_status_checks[].context")
-        names = sorted({n.strip() for n in o.splitlines() if n.strip()} - set(() if pr_head else PR_ONLY))
+        ok, params = self._checks_rule()
+        names = sorted(gh_read.required_contexts(params) - set(() if pr_head else PR_ONLY))
         if not ok or not names:
             raise Stop("proof", f"could not read {RULESET}'s required contexts; no proof is judged against a guessed list")
         return names
@@ -5217,10 +5215,8 @@ def _self_test() -> int:
             if argv[:2] == ["gh", "api"] and any(f"/issues/{n}/comments" in a for n in _mandate_gate().RECORD_ISSUES):
                 # every record issue is read; the fixture's thread is #201's
                 return 0, _jl(world.get("thread", []) if "/issues/201/" in a else [])
-            if argv[:2] == ["gh", "api"] and a.endswith("rulesets --jq " + argv[-1]):
-                return (0, "7") if world.get("required", "fast\n") else (1, "HTTP 404")
-            if "rulesets/7" in a:
-                return 0, world.get("required", "fast\n")
+            if "/rulesets" in a:
+                return gh_read.fake_ruleset(argv, "7", world.get("required", "fast\n"))
             if "app_approve.sh" in a:
                 return world.get("approve", (0, "APPROVED"))
             if argv[:3] == ["gh", "api", "user"]:  # the acting account
@@ -6926,6 +6922,7 @@ def _self_test() -> int:
     _state_self_test(check, go, merged, throwaway_git_init)
     _infra_self_test(check)
     _batch_self_test(check)
+    _ruleset_etag_self_test(check)
     _failed_marker_self_test(check)
     _add_self_test(check)
     _queue_self_test(check)
@@ -6935,6 +6932,39 @@ def _self_test() -> int:
     return 1 if failed else 0
 
 
+def _ruleset_etag_self_test(check) -> None:
+    """R10-GH-READ-RESIDUE-P3 item 1: the train's two ruleset reads are conditional and shared
+    through the state dir (P625: 235 reads an hour from 120 processes, each reading once)."""
+    calls: list = []
+
+    def srv(argv, cwd=ROOT, stdin=None):
+        calls.append(list(argv))
+        return gh_read.fake_ruleset(argv, "7", "fast\npr-contract\n", "true")
+
+    def train(d):
+        return Train("o/r", Path(d), None, "", (), 1, run=srv, sleep=lambda s: None, log=lambda s: None)
+    with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as st:
+        saved = os.environ.get("HPO_STATE_DIR")
+        os.environ["HPO_STATE_DIR"] = st
+        try:
+            first = train(d).required(pr_head=True)
+            cold = len(calls)
+            second = Train("o/r", Path(d), None, "", (), 1, run=srv, sleep=lambda s: None, log=lambda s: None)
+            warm_names, warm_strict = second.required(pr_head=True), second.strict_update()
+            warm = calls[cold:]
+        finally:
+            if saved is None:
+                os.environ.pop("HPO_STATE_DIR", None)
+            else:
+                os.environ["HPO_STATE_DIR"] = saved
+    check("a cold required() makes two plain ruleset reads (null control: no stored ETag, no If-None-Match)",
+          first == ["fast", "pr-contract"] and cold == 2 and not any("If-None-Match" in " ".join(c) for c in calls[:2]))
+    check("a second train process (a fresh object, the shared state dir) reads both rulesets conditionally "
+          "and gets the same set and the strict flag from the stored bodies",
+          warm_names == first and warm_strict is True and len(warm) == 4
+          and all("If-None-Match" in " ".join(c) for c in warm))
+
+
 def _introduced_self_test(check) -> None:
     """R10-INTRODUCED-REDS-BARRIER: a SELFTESTS step red at the head and not at
     the base is INTRODUCED, `classify --pr` reads it RED, and every unreadable
@@ -6969,10 +6999,8 @@ def _introduced_self_test(check) -> None:
             calls.append(a)
             if argv[:2] == ["git", "merge-base"]:
                 return (0, mb + "\n") if mb else (128, "fatal: Not a valid commit name")
-            if a.endswith("rulesets --jq " + argv[-1]):
-                return 0, "7"
-            if "rulesets/7" in a:
-                return 0, "fast\n"
+            if "/rulesets" in a:
+                return gh_read.fake_ruleset(argv, "7", "fast")
             for sha, runs in ((H, head_runs), (B, base_runs)):
                 if f"commits/{sha}/{SELFTESTS_RUNS}" in a:  # the filtered read: one JSON array
                     return (1, "HTTP 502") if runs is None else (0, json.dumps(
@@ -8533,10 +8561,8 @@ def _defer_wait_self_test(check, go, merged, cr, gt, gate_req, rollup_green: str
 
         def run(argv, cwd=ROOT, stdin=None):
             a = " ".join(argv)
-            if a.endswith("rulesets --jq " + argv[-1]) and argv[2] == "repos/o/r/rulesets":
-                return 0, "7\n"
-            if "repos/o/r/rulesets/7" in argv:
-                return 0, GATE + "\n"
+            if "repos/o/r/rulesets" in argv or "repos/o/r/rulesets/7" in argv:
+                return gh_read.fake_ruleset(argv, "7", GATE)
             if "actions/workflows/ci.yml/runs" in a:
                 return ci_out or (0, "\n".join(json.dumps(r) for r in frame.get("ci_runs", [])))
             if "check-runs" in a:
@@ -9019,9 +9045,9 @@ def _state_self_test(check, go, merged, throwaway_git_init) -> None:
             a = " ".join(argv)
             if "check-runs" in a:
                 return 0, "\n".join(json.dumps(c) for c in runs)
-            if a.endswith("rulesets --jq " + argv[-1]):
-                return (0, "7") if ruleset else (1, "HTTP 404")
-            return (0, ruleset) if "rulesets/7" in a else (1, "unexpected")
+            if "/rulesets" in a:
+                return gh_read.fake_ruleset(argv, "7", ruleset)
+            return 1, "unexpected"
         saved, buf = Train._run, io.StringIO()
         Train._run = staticmethod(fake_run)
         try:
@@ -9034,9 +9060,9 @@ def _state_self_test(check, go, merged, throwaway_git_init) -> None:
     def owed_cli(ruleset) -> "tuple[int, str]":  # `owed-reds` through main, the ruleset faked as `cli` fakes it
         def fake_run(argv, cwd=ROOT, stdin=None):
             a = " ".join(argv)
-            if a.endswith("rulesets --jq " + argv[-1]):
-                return (0, "7") if ruleset else (1, "HTTP 404")
-            return (0, ruleset) if "rulesets/7" in a else (1, "unexpected")
+            if "/rulesets" in a:
+                return gh_read.fake_ruleset(argv, "7", ruleset)
+            return 1, "unexpected"
         saved, buf = Train._run, io.StringIO()
         Train._run = staticmethod(fake_run)
         try:
@@ -9091,10 +9117,8 @@ def _state_self_test(check, go, merged, throwaway_git_init) -> None:
                 return 0, ""
             if "check-runs" in a:
                 return 0, "\n".join(json.dumps(c) for c in runs)
-            if a.endswith("rulesets --jq " + argv[-1]):
-                return 0, "7"
-            if "rulesets/7" in a:
-                return 0, "gate\n"
+            if "/rulesets" in a:
+                return gh_read.fake_ruleset(argv, "7", "gate")
             if argv[:2] == ["git", "merge-base"]:
                 return 0, BASE + "\n"
             if argv[:4] == ["git", "diff", "--no-renames", "--name-only"]:
@@ -9615,18 +9639,14 @@ def _batch_self_test(check) -> None:
                 return 0, '2026-10-07T00:00:00Z >>> FAILED: "$PYTHON" tests/ratchet.py'
             if "/actions/jobs/" in a:
                 return 0, "no script here"
-            if argv[:2] == ["gh", "api"] and a.endswith("rulesets --jq " + argv[-1]):
-                return (0, "7") if w["required"] else (1, "HTTP 404")
+            if "/rulesets" in a:
+                return gh_read.fake_ruleset(argv, "7", w["required"], w.get("strict", "true"))
             if argv[:3] == ["gh", "api", "graphql"] and "statusCheckRollup" in a:  # A5's rollup: GitHub agrees
                 n = int(next(x for x in argv if x.startswith("pr="))[3:])
                 return 0, json.dumps({"data": {"repository": {"pullRequest": {"commits": {"nodes": [{"commit": {
                     "oid": w["heads"][n], "statusCheckRollup": {"contexts": {"pageInfo": {"hasNextPage": False},
                         "nodes": [{"__typename": "CheckRun", "name": GATE, "status": "COMPLETED",
                                    "conclusion": "SUCCESS", "isRequired": True}]}}}}]}}}}})
-            if "rulesets/7" in a and "strict_required_status_checks_policy" in a:
-                return 0, w.get("strict", "true")  # today's world: an up-to-date branch is required
-            if "rulesets/7" in a:
-                return 0, w["required"]
             if argv[:3] == ["gh", "workflow", "run"]:
                 w["dispatched"].append((argv[3], argv[argv.index("--ref") + 1]))
                 return 0, ""
@@ -11041,6 +11061,7 @@ def _spool_edit_self_test(check, stub, H: str) -> None:
         st_g = spool3()
         (st_g / QUEUE_OPEN).write_text(f"{os.getpid()}\n")
         spooled0 = lines_of(st_g)
+        prev_state = os.environ.get("HPO_STATE_DIR")
         os.environ.update(HPO_STATE_DIR=str(gd), HPO_SEAT_GEN="roster=1")
         try:
             gsaid: list[str] = []
@@ -11053,7 +11074,11 @@ def _spool_edit_self_test(check, stub, H: str) -> None:
             check("seat_gen null: an add under the current generation spools as before",
                   rc == 0 and len(lines_of(st_g)) == len(spooled0) + 1)
         finally:
-            del os.environ["HPO_SEAT_GEN"], os.environ["HPO_STATE_DIR"]
+            del os.environ["HPO_SEAT_GEN"]
+            if prev_state is None:
+                del os.environ["HPO_STATE_DIR"]
+            else:
+                os.environ["HPO_STATE_DIR"] = prev_state
         said: list[str] = []
         live = Train("o/r", st, None, "", (), 1, run=stub({"pr": 15}), log=said.append)
         rc = train_add(live, {"pr": 15, "verdict": H, "verdict_comment": "42"}, ["train.sh"], front=True)
@@ -11494,7 +11519,9 @@ def main(argv: list[str]) -> int:
     if hasattr(sys.stdout, "reconfigure"):
         sys.stdout.reconfigure(line_buffering=True)
     if argv[:1] == ["--self-test"]:
-        return _self_test()
+        with tempfile.TemporaryDirectory() as st:  # the fakes' ETag files never reach the host's state dir
+            os.environ["HPO_STATE_DIR"] = st
+            return _self_test()
     if argv[:1] == ["job-log"]:  # `job-log <job id> <owner/repo>`: job_log for a shell caller
         if len(argv) != 3:
             print("usage: merge_train.py job-log <job id> <owner/repo>", file=sys.stderr)
diff --git a/tools/audit/seat/orchestrator_tick.py b/tools/audit/seat/orchestrator_tick.py
index f52fe8d93b..785dd53d3b 100644
--- a/tools/audit/seat/orchestrator_tick.py
+++ b/tools/audit/seat/orchestrator_tick.py
@@ -110,6 +110,7 @@ from __future__ import annotations
 import argparse
 import datetime
 import fnmatch
+import hashlib
 import importlib.util
 import json
 import os
@@ -121,6 +122,8 @@ from pathlib import Path
 
 SELF = "tools/audit/seat/orchestrator_tick.py"
 SEAT = Path(__file__).resolve().parent
+sys.path.insert(0, str(SEAT))
+import gh_read  # noqa: E402  the conditional (ETag) read every instrument shares
 ROOT = Path(__file__).resolve().parents[3]
 RULESET = "main-protect-checks"
 STUCK_FACTOR = 2  # a lane pending past this many critical-path medians is stuck (ETA and WAITING share it)
@@ -318,6 +321,11 @@ class Tick:
         r = subprocess.run(["gh", *argv], capture_output=True, text=True)
         return r.returncode, r.stdout + r.stderr
 
+    def conditional(self, path: str) -> tuple[int, str]:
+        """The body of the single-page GET at <path>, ETag-conditional and shared with every
+        process through the state dir (`gh_read.conditional_get`; a 304 costs no core call)."""
+        return gh_read.conditional_get(lambda argv: self.gh(argv[1:]), path)
+
     def git(self, argv: list[str]) -> tuple[int, str]:
         if self._git is not None:
             return self._git(argv)
@@ -385,8 +393,15 @@ class Tick:
     def check_runs(self, sha: str) -> "list[dict] | None":
         """Every check run at <sha>, one object per line across pages; the
         caller judges them through the train's classifier (`mt`)."""
-        code, raw = self.gh(["api", "--paginate", "--jq", ".check_runs[]",
-                             f"repos/{self.repo}/commits/{sha}/check-runs?per_page=100"])
+        path = f"repos/{self.repo}/commits/{sha}/check-runs?per_page=100"
+        code, raw = self.conditional(path)
+        try:  # one conditional page; a head with more runs than it holds is read in full
+            page = json.loads(raw) if code == 0 else None
+            if isinstance(page, dict) and page.get("total_count", 0) <= len(page.get("check_runs") or []):
+                return list(page.get("check_runs") or [])
+        except (ValueError, TypeError):
+            pass
+        code, raw = self.gh(["api", "--paginate", "--jq", ".check_runs[]", path])
         if code:
             return None
         try:
@@ -724,10 +739,13 @@ class Tick:
         lg, dispatched = _module("ledger_tick", "tools/audit/seat/ledger.py"), self._dispatched(S)
         for pr in sorted(prs, key=lambda p: p["number"]):
             n, head = pr["number"], pr.get("headRefOid") or ""
-            code, o = self.gh(["api", "--paginate", "--slurp",
-                               f"repos/{self.repo}/issues/{n}/comments?per_page=100"])
-            try:
-                cs = [c for page in json.loads(o) for c in page] if code == 0 else None
+            path = f"repos/{self.repo}/issues/{n}/comments?per_page=100"
+            code, o = self.conditional(path)
+            try:  # the conditional first page; a full page may have a next one: read them all
+                cs = json.loads(o) if code == 0 else None
+                if not isinstance(cs, list) or len(cs) >= gh_read.PER_PAGE:
+                    code, o = self.gh(["api", "--paginate", "--slurp", path])
+                    cs = [c for page in json.loads(o) for c in page] if code == 0 else None
             except (ValueError, TypeError):
                 cs = None
             if cs is None:
@@ -2033,23 +2051,16 @@ class Tick:
         read per tick: MAIN and PRS share it."""
         if getattr(self, "_req", None) is not None:
             return self._req
-        code, rid = self.gh(["api", f"repos/{self.repo}/rulesets", "--jq",
-                             f'.[] | select(.name == "{RULESET}") | .id'])
-        if code == 0 and rid.strip().isdigit():
-            code2, o = self.gh(["api", f"repos/{self.repo}/rulesets/{rid.strip()}",
-                                "--jq", '.rules[] | select(.type == '
-                                '"required_status_checks") | .parameters.'
-                                'required_status_checks[].context'])
-            if code2 == 0:
-                names = sorted({x.strip() for x in o.splitlines() if x.strip()}
-                               - set(PR_ONLY))
-                if names:
-                    self.line(S, f"required contexts ({RULESET}): "
-                                 f"{len(names)} read live")
-                    self._req = names
-                    # A pull request's head also carries PR_ONLY (K15 (d)).
-                    self._req_pr = sorted({x.strip() for x in o.splitlines() if x.strip()})
-                    return names
+        ok, params = gh_read.ruleset_checks(lambda argv: self.gh(argv[1:]), self.repo, RULESET)
+        every = sorted(gh_read.required_contexts(params))
+        names = sorted(set(every) - set(PR_ONLY))
+        if ok and names:
+            self.line(S, f"required contexts ({RULESET}): "
+                         f"{len(names)} read live")
+            self._req = names
+            # A pull request's head also carries PR_ONLY (K15 (d)).
+            self._req_pr = every
+            return names
         self.unreadable(S, "required contexts",
                         f"ruleset {RULESET} could not be read; "
                         "required-absence arms skipped, never guessed")
@@ -2882,18 +2893,49 @@ class Stub:
         self.h.append((match, rc, out))
         return self
 
+    def on_ruleset_list(self, rid="42"):
+        """The ruleset list read, which names RULESET's id (the id read lives at rulesets/<id>)."""
+        return self.on(lambda argv: any(a.endswith("/rulesets") for a in argv), out=rid)
+
     def __call__(self, argv):
         self.calls.append(list(argv))
         hay = " ".join(argv)
         for m, rc, out in self.h:
             if callable(m):
                 if m(argv):
-                    return rc, out
+                    return self.wire(argv, rc, out)
             elif all(x in hay for x in
                      (m if isinstance(m, (tuple, list)) else (m,))):
-                return rc, out
+                return self.wire(argv, rc, out)
         return 1, f"NO STUB for {' '.join(argv[:5])}"
 
+    @staticmethod
+    def wire(argv, rc, out):
+        """A conditional read (`gh api -i`) gets the wire form of what a handler holds: the
+        handlers state the body in the shape of the older jq/slurp read of the same path.
+        An ETag of the body's hash lets a matching If-None-Match answer 304, as gh does (rc 1)."""
+        if rc or "-i" not in argv:
+            return rc, out
+        path = next((a for a in argv if a.startswith("repos/")), "")
+        if path.endswith("/rulesets"):
+            body = [{"id": int(out), "name": RULESET}]
+        elif "/rulesets/" in path:
+            body = {"rules": [{"type": "required_status_checks", "parameters": {
+                "required_status_checks": [{"context": c} for c in out.splitlines() if c.strip()]}}]}
+        elif "/check-runs?" in path:
+            runs = [json.loads(x) for x in out.splitlines() if x.strip()]
+            body = {"total_count": len(runs), "check_runs": runs}
+        elif "/comments?" in path:
+            pages = json.loads(out)
+            body = pages[0] if pages and isinstance(pages[0], list) else pages
+        else:
+            return rc, out
+        text = json.dumps(body)
+        etag = '"' + hashlib.sha256(text.encode()).hexdigest()[:16] + '"'
+        if f"If-None-Match: {etag}" in argv:
+            return 1, f"HTTP/2.0 304 Not Modified\nEtag: {etag}\n\ngh: HTTP 304"
+        return 0, f"HTTP/2.0 200 OK\nEtag: {etag}\n\n{text}"
+
 
 NOW = datetime.datetime(2026, 10, 12, 18, 0, 0, tzinfo=datetime.timezone.utc)
 
@@ -2981,7 +3023,7 @@ def self_test() -> int:
         gh.on(("pr", "list"), out=json.dumps(prs))
         gh.on("commits/main", out=H1)
         if required_names is not None:
-            gh.on(".[] | select(.name", out="42")
+            gh.on_ruleset_list()
             gh.on("rulesets/42", out="\n".join(required_names))
         else:
             gh.on("rulesets", rc=1, out="no ruleset")
@@ -3566,7 +3608,7 @@ def self_test() -> int:
         # ---- MAIN ----
         gh = Stub()
         gh.on("commits/main", out=H1)
-        gh.on(".[] | select(.name", out="42")
+        gh.on_ruleset_list()
         gh.on("rulesets/42", out="tests\nclosures\n")
         gh.on(f"commits/{H1}/check-runs",
               out=json.dumps(run_obj("tests", conclusion="failure")) + "\n"
@@ -3602,7 +3644,7 @@ def self_test() -> int:
                 on_push.append(job)
         gh = Stub()
         gh.on("commits/main", out=H1)
-        gh.on(".[] | select(.name", out="42")
+        gh.on_ruleset_list()
         gh.on("rulesets/42", out="tests\nclosures\n")
         gh.on(f"commits/{H1}/check-runs",
               out="\n".join(json.dumps(run_obj(n)) for n in ("tests", "closures"))
@@ -3629,7 +3671,7 @@ def self_test() -> int:
         def umbrella(names_red):
             gh = Stub()
             gh.on("commits/main", out=H1)
-            gh.on(".[] | select(.name", out="42")
+            gh.on_ruleset_list()
             gh.on("rulesets/42", out="gate\n")
             gh.on(f"commits/{H1}/check-runs", out="\n".join(
                 json.dumps(run_obj(n, conclusion="failure" if n in names_red else "success"))
@@ -3667,7 +3709,7 @@ def self_test() -> int:
                 ("annotations unreadable (fails closed)", None, True)):
             gh = Stub()
             gh.on("commits/main", out=H1)
-            gh.on(".[] | select(.name", out="42")
+            gh.on_ruleset_list()
             gh.on("rulesets/42", out="tests\n")
             gh.on(f"commits/{H1}/check-runs",
                   out=json.dumps(run_obj("tests")) + "\n" + json.dumps(
@@ -3695,7 +3737,7 @@ def self_test() -> int:
         # verdict: still REQUIRED not green, and its annotations never read.
         gh = Stub()
         gh.on("commits/main", out=H1)
-        gh.on(".[] | select(.name", out="42")
+        gh.on_ruleset_list()
         gh.on("rulesets/42", out="tests\n")
         gh.on(f"commits/{H1}/check-runs", out=json.dumps(
             run_obj("tests", conclusion="cancelled", cid=119215715286)))
@@ -4763,7 +4805,7 @@ def self_test() -> int:
         # ---- main-red dispatch briefs: required lane, bot lane ----
         gh = Stub()
         gh.on("commits/main", out=H1)
-        gh.on(".[] | select(.name", out="42")
+        gh.on_ruleset_list()
         gh.on("rulesets/42", out="tests\nclosures\n")
         gh.on(f"commits/{H1}/check-runs",
               out=json.dumps(run_obj("tests", conclusion="failure", cid=424242))
@@ -5749,6 +5791,68 @@ def self_test() -> int:
         ])
         total, failed = total + a, failed + f
 
+    # R10-GH-READ-RESIDUE-P3 item 1 (P596, P625): the tick's comment, check-run and ruleset
+    # reads are conditional and their ETag and body shared through the state dir.
+    with tempfile.TemporaryDirectory() as st_dir:
+        saved_state = os.environ.get("HPO_STATE_DIR")
+        os.environ["HPO_STATE_DIR"] = st_dir
+        try:
+            h70 = f"{70:040x}"
+            runs70 = [run_obj("tests"), run_obj("closures")]
+            vcom = {"id": 9, "user": {"login": "x", "id": 1, "type": "User"}, "created_at": iso(NOW), "body": "hi"}
+
+            def pass_(comments, runs=None):
+                board = [pr_obj(70, h70)]
+                t = tick(prs=board, runs_at={H1: runs or runs70},
+                         gh_extra=[(("issues/70/comments?per_page=100",), 0, json.dumps(comments))])
+                t._git.on(("ls-remote",), out="")
+                t._git.on(("log", "-1", "--format=%ct"), out="0")
+                t.verdict_levels("PRS", board)
+                got = t.check_runs(H1)
+                req = t.required("PRS")
+                return t, got, req
+
+            def inm(t, frag):
+                return [any("If-None-Match" in a for a in c) for c in t._gh.calls
+                        if "-i" in c and any(frag in a for a in c)]
+            t1, runs1, req1 = pass_([[vcom]])
+            t2, runs2, req2 = pass_([[vcom]])
+            a, f = check("conditional reads (the tick's three single-page reads)", [
+                ("cold: comments, check-runs and both ruleset reads are plain (null control: no stored ETag)",
+                 inm(t1, "/comments?") == [False] and inm(t1, "/check-runs?") == [False]
+                 and inm(t1, "/rulesets") == [False, False]),
+                ("warm, another Tick object on the same state dir: all four are conditional and answered 304",
+                 inm(t2, "/comments?") == [True] and inm(t2, "/check-runs?") == [True]
+                 and inm(t2, "/rulesets") == [True, True]),
+                ("a 304 serves the stored bodies: the same runs and the same required set",
+                 runs2 == runs1 and len(runs1) == 2 and req2 == req1 == ["closures", "tests"]),
+            ])
+            total, failed = total + a, failed + f
+            t3, runs3, _ = pass_([[vcom]], runs=[run_obj("tests", conclusion="failure")])
+            a, f = check("a changed body is a 200 that replaces the stored one", [
+                ("the new check-run page is read, not the stored one",
+                 [r["conclusion"] for r in runs3] == ["failure"]),
+            ])
+            total, failed = total + a, failed + f
+            full = [[dict(vcom, id=i) for i in range(gh_read.PER_PAGE)]]
+            t4 = tick(prs=[pr_obj(71, f"{71:040x}")],
+                      gh_extra=[(lambda argv: "--slurp" in argv and "issues/71/comments" in " ".join(argv), 0,
+                                 json.dumps(full + [[dict(vcom, id=999)]])),
+                                (("issues/71/comments?per_page=100",), 0, json.dumps(full))])
+            t4._git.on(("ls-remote",), out="")
+            t4._git.on(("log", "-1", "--format=%ct"), out="0")
+            t4.verdict_levels("PRS", [pr_obj(71, f"{71:040x}")])
+            a, f = check("a full first page is read through to the end", [
+                ("the paginated slurp read follows the 100-comment conditional page",
+                 any("--slurp" in c and "issues/71/comments?per_page=100" in " ".join(c) for c in t4._gh.calls)),
+            ])
+            total, failed = total + a, failed + f
+        finally:
+            if saved_state is None:
+                os.environ.pop("HPO_STATE_DIR", None)
+            else:
+                os.environ["HPO_STATE_DIR"] = saved_state
+
     print(f"orchestrator_tick self-test: {total} checks, {failed} failed")
     return 1 if failed else 0
 
@@ -5788,7 +5892,9 @@ def main() -> int:
     ap.add_argument("--self-test", action="store_true")
     a = ap.parse_args()
     if a.self_test:
-        return self_test()
+        with tempfile.TemporaryDirectory() as st:  # the fakes' ETag files never reach the host's state dir
+            os.environ["HPO_STATE_DIR"] = st
+            return self_test()
     if not a.workers_file and a.queue:
         sib = Path(a.queue[0]).parent / "workers.json"
         if sib.exists():
diff --git a/tools/audit/seat/proof_watch.py b/tools/audit/seat/proof_watch.py
index f587e4bb8f..c65dce5056 100644
--- a/tools/audit/seat/proof_watch.py
+++ b/tools/audit/seat/proof_watch.py
@@ -460,6 +460,7 @@ def self_test() -> int:
     APPR = {"login": "hpo-approver[bot]", "type": "Bot", "id": 330097732}
 
     W = Path(tempfile.mkdtemp(prefix="proof-watch-selftest."))
+    os.environ["HPO_STATE_DIR"] = str(W / "state")  # the fake ruleset's ETag files stay in the self-test's dir
     fails, n = 0, 0
 
     def st(got, want, why):
@@ -528,10 +529,9 @@ def self_test() -> int:
                 return self.merge_rc, self.merge_out
             if "headRefOid" in argv:
                 return 0, self.pr_head + "\n"
-            if any(a == f"repos/{REPO}/rulesets" for a in argv):
-                return 0, "23698884\n"
-            if any(a.startswith(f"repos/{REPO}/rulesets/") for a in argv):
-                return 0, self.required + "\n"
+            if any(a.startswith(f"repos/{REPO}/rulesets") for a in argv):
+                import gh_read  # merge_train's own reader parses this wire form (ETag-conditional)
+                return gh_read.fake_ruleset(argv, "23698884", self.required)
             if any("actions/workflows/ci.yml/runs" in a for a in argv):
                 return 0, "".join(json.dumps(r) + "\n" for r in self.ci_runs)
             if any(a.startswith("repos/") and "/check-runs" in a for a in argv):
diff --git a/tools/audit/seat/seat_venv.sh b/tools/audit/seat/seat_venv.sh
index 7bee280cc8..4ba2321c0b 100755
--- a/tools/audit/seat/seat_venv.sh
+++ b/tools/audit/seat/seat_venv.sh
@@ -33,7 +33,7 @@
 # that interpreter exists and the variable is unset -- never overriding a
 # value the seat set. --install-shims copies them, as `python` and `python3`,
 # into the bin directory you name, which goes first on the seats' PATH, with
-# seat-gh as `gh` (it logs the call to $HPO_STATE_DIR/gh-calls.log, then execs the
+# seat-gh as `gh` (it logs the call to the host-wide $HOME/.local/state/hpo/gh-calls.log, then execs the
 # real gh; gh_calls.py reads the log):
 #
 #   tools/audit/seat/seat_venv.sh && tools/audit/seat/seat_venv.sh --install-shims <seat bin dir>
@@ -281,6 +281,11 @@ STUB
   grep -qxF "gcpy=$(printf '%q' "$ROOT/tools/pr/gh_comment.py")" "$W/inst/gh" \
     && ! grep -qF '@HPO_GH_COMMENT@' "$W/inst/gh"
   expect "--install-shims bakes the tree's gh_comment.py path into the installed gh shim" $?
+  grep -qxF 'loghome=@HPO_GH_LOG_HOME@' "$ROOT/tools/audit/seat/shims/seat-gh"
+  expect "the source gh shim carries the log-home placeholder (null control)" $?
+  grep -qxF "loghome=$(printf '%q' "$HOME/.local/state/hpo")" "$W/inst/gh" \
+    && ! grep -qF '@HPO_GH_LOG_HOME@' "$W/inst/gh" && ! grep -qF "$W" <(grep -x 'loghome=.*' "$W/inst/gh")
+  expect "--install-shims fixes the host-wide log home, not the caller's HPO_STATE_DIR" $?
 
   rm -rf "$W"
   printf 'seat_venv self-test: %s checks, %s failed\n' "$((pass + fail))" "$fail"
@@ -303,6 +308,8 @@ case ${1:-} in
     [ -f "$gcpy" ] || die "no $gcpy for the gh shim's comment guard"
     while IFS= read -r l; do
       [ "$l" = 'gcpy=@HPO_GH_COMMENT@' ] && l="gcpy=$(printf '%q' "$gcpy")"
+      # the one host-wide call log (P669): the installing user's default home, never the caller's HPO_STATE_DIR
+      [ "$l" = 'loghome=@HPO_GH_LOG_HOME@' ] && l="loghome=$(printf '%q' "$HOME/.local/state/hpo")"
       printf '%s\n' "$l"
     done < "$ROOT/tools/audit/seat/shims/seat-gh" > "$dest/gh" && chmod 755 "$dest/gh"
     printf 'seat_venv: shims installed in %s; they run %s/bin/python3\n' "$dest" "$VENV"
diff --git a/tools/audit/seat/shims/seat-gh b/tools/audit/seat/shims/seat-gh
index c691f3e161..b48916aab3 100755
--- a/tools/audit/seat/shims/seat-gh
+++ b/tools/audit/seat/shims/seat-gh
@@ -2,7 +2,10 @@
 # hpo-gh-shim
 # The seat's gh (P284). Installed as `gh` beside the python shims by
 # `seat_venv.sh --install-shims <dir>`. It appends ONE line per call to
-# $HPO_STATE_DIR/gh-calls.log (default $HOME/.local/state/hpo):
+# ONE host-wide log, gh-calls.log in the directory fixed at install (`loghome=` below;
+# the installing user's $HOME/.local/state/hpo), whatever HPO_STATE_DIR the caller
+# holds: the token and its core bucket are host-wide, so the log is (P669). Run from
+# the tree, uninstalled, it uses $HOME/.local/state/hpo:
 #
 #   <utc> <parent pid> <parent argv[0] [script], first 80 chars> <gh subcommand> <target>
 #
@@ -28,6 +31,10 @@
 # A log it cannot write is skipped: no output, no status of its own.
 # The log is capped: past HPO_GH_LOG_MAX bytes (default 1048576) it is moved
 # to gh-calls.log.1, replacing the older one.
+# The log's directory, fixed at install: seat_venv.sh --install-shims bakes the next line's
+# placeholder; no caller's environment (HPO_STATE_DIR) picks the log.
+loghome=@HPO_GH_LOG_HOME@
+case $loghome in @*) loghome=$HOME/.local/state/hpo ;; esac
 is_shim() { local l1= l2=; { IFS= read -r l1; IFS= read -r l2; } < "$1" 2>/dev/null; [ "$l2" = '# hpo-gh-shim' ]; }
 usable() { [ -f "$1" ] && [ -x "$1" ] && ! is_shim "$1"; }
 real=
@@ -61,7 +68,7 @@ esac
 # callers) is its own, so the real gh below runs under the caller's.
 (
   umask 077
-  state=${HPO_STATE_DIR:-$HOME/.local/state/hpo}
+  state=$loghome
   log=$state/gh-calls.log
   max=${HPO_GH_LOG_MAX:-1048576}
   # The parent field names the caller and nothing it was given: argv[0]'s basename and,
diff --git a/tools/pr/prepr.sh b/tools/pr/prepr.sh
index 1626906bea..200d9d273f 100755
--- a/tools/pr/prepr.sh
+++ b/tools/pr/prepr.sh
@@ -1376,11 +1376,18 @@ PY
 # job that re-executes this script exports a credential to it, so there the
 # arm prints its skip line and stays local-only-deterministic, the position
 # PREPR_SKIP_CLOSURES holds for the closures step.
-REDS_JQ='.check_runs[]
-         | select(.status == "completed" and .conclusion == "failure")
-         | select(.name != "pr-contract / pr-contract" and .name != "gate")
-         | .name'
-
+# One read per sha carries all three facts the arm needs, as lines: `T <total_count>` (per
+# page), `P` per run not yet completed, `R <name>` per red. The total used to be a second
+# read of every commit on an all-green branch (PC-1113-13 / ANCESTRY-REDS-PER-COMMIT-READS).
+REDS_JQ='(.total_count | "T \(.)"),
+         (.check_runs[] | select(.status != "completed") | "P"),
+         (.check_runs[]
+          | select(.status == "completed" and .conclusion == "failure")
+          | select(.name != "pr-contract / pr-contract" and .name != "gate")
+          | "R \(.name)")'
+# A sha's read is kept under the state dir for PREPR_ANCESTRY_TTL_S (default 3600 s) when no run at it
+# was still going: a commit's runs are final then, and `update_pr` and each prepr run re-read
+# the same ancestry. A read with a run pending is never kept (a red may still land).
 gh_credential() { # gh binary -> the token on stdout, rc 1 when none
   case "${GITHUB_TOKEN:-}" in ?*) printf '%s' "$GITHUB_TOKEN"; return 0 ;; esac
   case "${GH_TOKEN:-}" in ?*) printf '%s' "$GH_TOKEN"; return 0 ;; esac
@@ -1401,7 +1408,7 @@ alert_reds() { # the branch's own remote head ref -> rc 0: alert lines (maybe no
 ancestry_reds() { # the branch's own remote head ref
   # -> rc 0: the red names, one per line, sorted unique
   #    rc 3: the skip reason (one line)
-  local ghc tok url repo base shas sha out names any
+  local ghc tok url repo base shas sha out names any n
   ghc=${PREPR_GH:-gh}   # --self-test replaces the gh binary word, argv identical
   command -v "$ghc" >/dev/null 2>&1 || { echo "gh is absent, so no branch check run could be read"; return 3; }
   tok=$(gh_credential "$ghc") || { echo "no token: GITHUB_TOKEN and GH_TOKEN are unset and \`$ghc auth token\` refuses, so no branch check run could be read"; return 3; }
@@ -1416,24 +1423,32 @@ ancestry_reds() { # the branch's own remote head ref
   base=$(git merge-base origin/main HEAD 2>/dev/null) || { echo "no merge base with origin/main, so no ancestry could be enumerated"; return 3; }
   shas=$(git rev-list "$base..$1" 2>/dev/null) || { echo "$1 could not be read, so no ancestry was enumerated"; return 3; }
   [ -n "$shas" ] || { echo "no commit of this branch is on $1 yet -- the first push has no ancestry to read"; return 3; }
-  names=""; any=""
+  local cdir f runs ttl=${PREPR_ANCESTRY_TTL_S:-3600}
+  cdir=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/prepr-ancestry
+  names=""; any=""; runs=0
   for sha in $shas; do
-    out=$("$ghc" api --paginate "repos/$repo/commits/$sha/check-runs" --jq "$REDS_JQ" 2>/dev/null) || {
-      echo "the check runs at $sha could not be read, so the ancestry reds are UNCHECKED this run, not confirmed empty"; return 3; }
-    [ -n "$out" ] && { names="$names$out"$'\n'; any=1; }
-  done
-  if [ -z "$any" ]; then
-    # Nothing failed anywhere: say whether that was MEASURED or merely
-    # unpopulated -- a branch whose commits never ran CI owes no answer and
-    # confirms nothing, and `total_count` is on the first page of the same
-    # endpoint this loop already read. Only the all-green branch pays for
-    # this second pass.
-    for sha in $shas; do
-      out=$("$ghc" api "repos/$repo/commits/$sha/check-runs" --jq '.total_count' 2>/dev/null) || {
+    f=$cdir/${repo//\//_}-$sha
+    if [ -f "$f" ] && [ -n "$(find "$f" -mmin "-$((ttl / 60))" 2>/dev/null)" ]; then
+      out=$(cat "$f")
+    else
+      out=$("$ghc" api --paginate "repos/$repo/commits/$sha/check-runs" --jq "$REDS_JQ" 2>/dev/null) || {
         echo "the check runs at $sha could not be read, so the ancestry reds are UNCHECKED this run, not confirmed empty"; return 3; }
-      [ "${out:-0}" -gt 0 ] 2>/dev/null && { any=1; break; }
-    done
-    [ -n "$any" ] || { echo "no pushed commit carries any check run, so there is no red to answer and none confirmed absent"; return 3; }
+      # a read that did not answer in the lines' shape is UNCHECKED, never confirmed empty
+      case "$out" in "T "*) ;; *)
+        echo "the check runs at $sha could not be read, so the ancestry reds are UNCHECKED this run, not confirmed empty"; return 3 ;; esac
+      if ! grep -qx P <<<"$out" && mkdir -p "$cdir" 2>/dev/null; then
+        printf '%s\n' "$out" >"$f.$$" 2>/dev/null && mv -f "$f.$$" "$f" 2>/dev/null || rm -f "$f.$$"
+      fi
+    fi
+    n=$(printf '%s\n' "$out" | sed -n 's/^T //p' | sort -n | tail -1)
+    [ "${n:-0}" -gt 0 ] 2>/dev/null && runs=1
+    n=$(printf '%s\n' "$out" | sed -n 's/^R //p')
+    [ -n "$n" ] && { names="$names$n"$'\n'; any=1; }
+  done
+  # Nothing failed anywhere: say whether that was MEASURED or merely unpopulated -- a branch
+  # whose commits never ran CI owes no answer and confirms nothing; the totals came with the reads.
+  if [ -z "$any" ] && [ "$runs" -eq 0 ]; then
+    echo "no pushed commit carries any check run, so there is no red to answer and none confirmed absent"; return 3
   fi
   printf '%s' "$names" | sort -u
 }
@@ -2110,6 +2125,7 @@ if [ "${1:-}" = "--self-test" ]; then
   RAFIX=$(cd tools/policy/fixtures/red-ancestry && pwd -P)
   RA=$(mktemp -d)
   export PREPR_NO_ALERTS=1   # the rows below never reach code scanning; the alert rows opt in
+  export PREPR_ANCESTRY_TTL_S=0 HPO_STATE_DIR; HPO_STATE_DIR=$(mktemp -d)   # no kept read crosses a fixture; the cache rows below opt in
   (
     set -e; throwaway_git_env; cd "$RA"; throwaway_git_init . -q -b main
     git config user.name st; git config user.email st@st
@@ -2138,6 +2154,7 @@ for a in "$@"; do
   prev=$a
 done
 [ -n "$filter" ] && [ -n "$url" ] || exit 5
+[ -z "${CALLS:-}" ] || echo "$url" >>"$CALLS"
 sha=${url#*/commits/}; sha=${sha%/check-runs}
 [ -f "$REDFIX/$sha.json" ] || exit 1
 exec jq -r "$filter" "$REDFIX/$sha.json"
@@ -2198,6 +2215,54 @@ EOS
     reds_line "$DABS/red-answered.md" "$ZERO" '' "$DABS/paths-nonpolicy.txt" origin/fix)
   st $? 3 "an absent gh skips the arm (never refuses)"
   case "$out" in *gh\ is\ absent*) st 1 1 "and the skip line says why";; *) st 0 1 "and the skip line says why";; esac
+  # PC-1113-13 / ANCESTRY-REDS-PER-COMMIT-READS: the calls one ancestry read makes grow with the
+  # branch's commits, so they are counted (the stub appends each url to $CALLS) over a 520-commit
+  # branch whose every commit is green, then with a red on an ancestor, then warm.
+  LONG=$(mktemp -d); LFIX=$(mktemp -d); LCALLS="$LONG.calls"
+  (
+    set -e; throwaway_git_env; cd "$LONG"; throwaway_git_init . -q -b main
+    git config user.name st; git config user.email st@st
+    git remote add origin https://github.com/tvofi/heatpump_optimizer.git
+    export GIT_AUTHOR_NAME=st GIT_AUTHOR_EMAIL=st@st GIT_COMMITTER_NAME=st GIT_COMMITTER_EMAIL=st@st
+    export GIT_AUTHOR_DATE='2005-04-07T22:13:13 +0000' GIT_COMMITTER_DATE='2005-04-07T22:13:13 +0000'
+    echo a > code; git add -A; git -c commit.gpgsign=false commit -qm base
+    tree=$(git write-tree); parent=$(git rev-parse HEAD)
+    for i in $(seq 1 520); do parent=$(git commit-tree "$tree" -p "$parent" -m "c$i"); done
+    git update-ref refs/remotes/origin/long "$parent"; git update-ref refs/remotes/origin/main main
+  ) >/dev/null 2>&1
+  long_shas=$(GIT_DIR="$LONG/.git" git rev-list main..origin/long)
+  for sha in $long_shas; do
+    printf '{"total_count":1,"check_runs":[{"name":"fast (3.14)","status":"completed","conclusion":"success"}]}' >"$LFIX/$sha.json"
+  done
+  lreds() { # ttl, extra env... -> "<rc>:<names joined>:<calls>"
+    local ttl=$1 out r; shift; : >"$LCALLS"
+    out=$(GIT_DIR="$LONG/.git" REDFIX="$LFIX" CALLS="$LCALLS" GITHUB_TOKEN=selftest PREPR_GH="$RA/gh" \
+      PREPR_ANCESTRY_TTL_S="$ttl" HPO_STATE_DIR="$LSTATE" ancestry_reds origin/long); r=$?
+    echo "$r:$(echo $out):$(wc -l <"$LCALLS" | tr -d ' ')"
+  }
+  LSTATE=$(mktemp -d)
+  got=$(lreds 0)
+  st "$got" "0::520" "an all-green 520-commit branch reads each commit once: 520 calls, the total_count read with it (the merge base made 520 and then one more for the total)"
+  got=$(lreds 3600); got2=$(lreds 3600)
+  st "$got2" "0::0" "a second run in the hour reads nothing: every commit's runs were final and are kept"
+  oldest=$(printf '%s\n' $long_shas | sed -n 100p)
+  printf '{"total_count":2,"check_runs":[{"name":"fast (3.14)","status":"completed","conclusion":"success"},{"name":"closures","status":"completed","conclusion":"failure"}]}' >"$LFIX/$oldest.json"
+  rm -rf "$LSTATE"; LSTATE=$(mktemp -d)
+  got=$(lreds 3600); got2=$(lreds 3600)
+  st "$got" "0:closures:520" "a red on an ancestor commit is named on the cold read"
+  st "$got2" "0:closures:0" "and on the warm read, from the kept lines (no answered red lost)"
+  pending=$(printf '%s\n' $long_shas | sed -n 7p)
+  printf '{"total_count":1,"check_runs":[{"name":"fast (3.14)","status":"in_progress","conclusion":null}]}' >"$LFIX/$pending.json"
+  rm -rf "$LSTATE"; LSTATE=$(mktemp -d)
+  lreds 3600 >/dev/null; got2=$(lreds 3600)
+  st "$got2" "0:closures:1" "a commit with a run still pending is read again each time (never kept), the other 519 are kept"
+  got=$(lreds 0)
+  st "$got" "0:closures:520" "null control: with the keeping off (TTL 0) every commit is read, so the zero above is the cache's"
+  : >"$LCALLS"
+  GIT_DIR="$RA/.git" REDFIX="$RAFIX/green" CALLS="$LCALLS" GITHUB_TOKEN=selftest PREPR_GH="$RA/gh" \
+    PREPR_ANCESTRY_TTL_S=0 HPO_STATE_DIR="$(mktemp -d)" ancestry_reds origin/fix >/dev/null
+  st "$(wc -l <"$LCALLS" | tr -d ' ')" 2 "null control: a 2-commit all-green branch makes 2 calls (the merge base made 3), never more than before"
+  rm -rf "$LONG" "$LFIX" "$LONG.calls" "$LSTATE"
   # The alert listing (R4-1): `alert_reds` runs tools/pr/local_alerts.py, replaced here
   # by a script printing one alert line (the plant) or none (the null). An alert is a
   # red the body must name; a listing that could not be read says so and never refuses.

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
