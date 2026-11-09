# Review packet #3364
head: f29c16fac7d846ac098fb30eb466c6961c7f9038
base: 6457496aba7b1076b1ed60c374c5badafdf66fc1

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=128931446579 success
arch-score / arch-score id=128976562134 success
arm id=128927556536 skipped
budget-raise-gate / budget-raise-gate id=128976605564 success
cancel-superseded id=128976599960 success
codeql id=128976588218 skipped
codeql / Analyze (actions) id=128931369559 success
codeql / Analyze (javascript-typescript) id=128931369488 success
codeql / Analyze (python) id=128931369585 success
gate id=128976561187 success
governance id=128976589405 skipped
governance / delivery-status id=128931369503 failure
governance / delivery-status-publish id=128931371233 skipped
governance / env-matrix id=128931369521 success
governance / instrument-self-tests id=128931369536 success
governance / policy-docs id=128931369506 success
governance / record id=128931371292 skipped
governance / wave-script id=128931369524 success
hassfest id=128976561973 skipped
hassfest / hassfest id=128931369397 success
kernel-points id=128976602824 skipped
pr-contract id=128976562110 skipped
pr-contract / pr-contract id=128938325919 success
prelude id=128976561392 success
refresh id=128976562687 success
tests id=128976584631 skipped
tests / arch-instrument id=128932358467 success
tests / briefs id=128931369605 success
tests / browser id=128932358479 success
tests / ci-ratchet id=128938174797 skipped
tests / claims-autofix id=128936152378 skipped
tests / closure-scope id=128931369615 success
tests / closures id=128932358448 success
tests / closures-autofix id=128937476477 skipped
tests / coverage id=128932358471 success
tests / coverage-ratchet id=128938173741 success
tests / fast (3.14) id=128932358660 success
tests / graders-head-copy id=128938173662 success
tests / lane-proofs id=128938173673 success
tests / mutation id=128931369583 success
tests / mutation-autofix id=128931848282 skipped
tests / mutation-pins id=128931848158 skipped
tests / nightly-ha id=128932359209 skipped
tests / nightly-status id=128931369766 success
tests / replay id=128932360125 skipped
tests / typing id=128932358581 success
validate id=128976600875 skipped
validate / validate-hacs id=128931369471 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 4e500647: dismissed:the instrument is fixed here and the record recounts, so no later stage's work changes
NOTE body item 3ef5ae0f: dismissed:a sibling reader outside this group's files, named here so the owner of review_strength.py can pair it in agreement.mjs
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified - The base copy is dev/audit/harnesses/r10_triage_p393.py at main 661d26a5d (unchanged since 17e621f08), sha1 aad12c7b1a754c181fa49ae348840676ea9e04e4. The head copy has sha1 040151ecdc06d0f7cdf45cbb7e0311056b9353de.
             no segment of this names a program this check knows
  unverified - The runs were taken back to back, 2026-11-08T22:36:22Z to 22:36:42Z, over one fetch of every `verdict/*` and `review/*` ref. The bus moves (703, 704 and 705 refs across this session's runs), so a later run re-derives its own counts.
             no segment of this names a program this check knows
  unverified - The `stale` arm's events log is host-local and absent here, so it was given an empty file. That is why the brief's `1 stale, 21 later` cannot be re-taken here: STALE and LATER need a time, and SAME does not.
             no segment of this names a program this check knows
  unverified - base: `verdict refs=705 instances=64 stale=0 later=0 same=4 unknown=60`;
             no segment of this names a program this check knows
  unverified - head: `verdict refs=705 instances=64 stale=0 later=0 same=3 unknown=61`.
             no segment of this names a program this check knows
  unverified - `diff` of the two outputs differs only on PR 2465's line (`SAME ... merge=0f1f8919` -> `UNKNOWN ... merge=f8b99351`) and on the tally.
             no segment of this names a program this check knows
  unverified - base merge_train, empty state dir: `guard=absent admitted=64 refused-stale=0 refused-undecidable=0`.
             no segment of this names a program this check knows
  unverified - head, empty state dir (no registry): `guard=yes admitted=3 refused-stale=0 refused-undecidable=61`. The 3 admitted are exactly the head `stale` arm's 3 SAME: PR 2323, 2329 and 3045.
             no segment of this names a program this check knows
  unverified - head, with a registry of PR 3232's two dispatches only, at the triage's recorded times, with full nonces read from that PR's verdict commits b09e48026 and 8000a4f5d: `admitted=3 refused-stale=1 refused-undecidable=60`. The refusal line is `refused-stale pr=3232 head=bba5b4d4 merge=b09e4802 stale merge verdict: its nonce 2a9f4501 was dispatched at 2026-11-06T20:50:26Z, before the blocked verdict's cc3bfb99 at 2026-11-06T22:13:28Z`.
             no segment of this names a program this check knows
  unverified - null control, the same registry with the merge dispatch moved after the blocked one (23:50:26Z): `admitted=4 refused-stale=0 refused-undecidable=60`, PR 3232 admitted.
             no segment of this names a program this check knows
  unverified - base merge_train with the PR 3232 registry: `admitted=64`, so the base admits the stale verdict.
             no segment of this names a program this check knows
  ok         python3 tools/audit/seat/merge_train.py --self-test
             `tools/audit/seat/merge_train.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/proof_watch.py --self-test
             `tools/audit/seat/proof_watch.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/cloud_dispatch.py --self-test
             `tools/audit/seat/cloud_dispatch.py` is in the tree at this head
  ok         python3 -I dev/audit/harnesses/r10_triage_p393.py stale <empty events.tsv>
             `dev/audit/harnesses/r10_triage_p393.py` is in the tree at this head
  ok         python3 -I dev/audit/harnesses/r10_triage_p393.py guard <state dir>
             `dev/audit/harnesses/r10_triage_p393.py` is in the tree at this head
  ok         python3 -I dev/audit/harnesses/r10_triage_p393.py guard ~/.zcode/bus
             `dev/audit/harnesses/r10_triage_p393.py` is in the tree at this head
  unverified git grep -n -E 'parse_verdict\(|posted_verdict\(|VERDICT_MERGE' -- tools
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only
             `tests/env_drift.py` is in the tree at this head
  ok         tests/closure.py selftest
             `tests/closure.py` is in the tree at this head
  ok         tests/layout.py
             `tests/layout.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 -I tools/policy/agreement_py.py --out <f>
             `tools/policy/agreement_py.py` is in the tree at this head
  ok         node tools/policy/agreement.mjs --py-json <f>
             `tools/policy/agreement.mjs` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         bash tools/pr/prepr.sh <this body>
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 17 resolved, 12 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_triage_p393.py b/dev/audit/harnesses/r10_triage_p393.py
index 53e45c561..4a5fd88d1 100644
--- a/dev/audit/harnesses/r10_triage_p393.py
+++ b/dev/audit/harnesses/r10_triage_p393.py
@@ -19,6 +19,16 @@ only if it holds the log. STALE: the merge verdict's nonce was dispatched
 before the blocked verdict's. LATER: dispatched after. SAME: one nonce posted
 both. UNKNOWN: a dispatch time is missing (the log starts 2026-10-28).
 
+`guard` (R10-TRAIN-STALE-VERDICT-GUARD) walks the same instances and drives
+the production guard, `merge_train.Train.stale_verdict`, at each merge
+verdict's own commit, with bus.sh's registry read from STATE_DIR/dispatched
+(STATE_DIR is `$HPO_BUS_STATE`, else `~/.zcode/bus`: host-local, like the
+events log). It prints one line per instance and the tally
+`admitted= refused-stale= refused-undecidable=`; at a tree without the guard
+every instance is `admitted` (the newest merge verdict was all it read).
+
+    python3 -I dev/audit/harnesses/r10_triage_p393.py guard  STATE_DIR
+
 `bodies` (P396) reads a `gh pr list --state merged --json number,body,mergedAt`
 dump and counts bodies whose `## Forward-carry` section holds a `Carry:` line
 that the triage gate's PROPOSAL_RE matches with no RULING_CITE_RE citation.
@@ -51,7 +61,6 @@ sys.path.insert(0, str(ROOT / "tools" / "audit"))
 
 SUBJ = re.compile(r"^verdict: #(\d+) Fix review: (merge|blocked) ([0-9a-f]{40})")
 CONF = re.compile(r"^bus-confirmed: .*\(review/\d+ at ([0-9a-f]{40})\)", re.M)
-NONCE = re.compile(r"bus-nonce:\s*([0-9a-f]{8})")
 NS = "refs/p393scan"
 
 
@@ -72,47 +81,89 @@ def dispatch_times(events: str) -> dict[str, str]:
 
 
 def nonce_of(body: str) -> str | None:
+    """The first 8 hex of the verdict's own nonce, by bus.sh's anchored rule
+    (`proof_watch.verdict_nonce`, imported): an unanchored search read a nonce
+    quoted in a finding's prose (PR 2465) as the verdict's own."""
+    import proof_watch
     m = CONF.search(body)
     if not m:
         return None
-    n = NONCE.search(git("show", f"{m.group(1)}:VERDICT.md"))
-    return n.group(1) if n else None
+    n = proof_watch.verdict_nonce(git("show", f"{m.group(1)}:VERDICT.md"))
+    return n[:8] if n else None
 
 
-def stale(events: str) -> int:
+def instances():
+    """(verdict refs, then per instance: pr, head, merge commit, merge body,
+    blocked body): the first merge verdict after a blocked one at its head."""
     subprocess.run(["git", "-C", str(ROOT), "fetch", "-q", "origin",
                     f"+refs/heads/verdict/*:{NS}/verdict/*",
                     f"+refs/heads/review/*:{NS}/review/*"], check=True)
-    disp = dispatch_times(events)
-    counts = {"STALE": 0, "LATER": 0, "SAME": 0, "UNKNOWN": 0}
     refs = git("for-each-ref", "--format=%(refname)", f"{NS}/verdict").split()
+    yield refs
     for ref in refs:
-        blocked: dict[str, str | None] = {}
+        blocked: dict[str, str] = {}
         seen: set[str] = set()
         for ent in git("log", "--reverse", "--format=%H%x00%B%x01", ref).split("\x01"):
             if "\x00" not in ent:
                 continue
-            body = ent.strip("\n").split("\x00", 1)[1].strip()
+            sha, body = ent.strip("\n").split("\x00", 1)
+            body = body.strip()
             m = SUBJ.match(body)
             if not m:
                 continue
             pr, verdict, head = m.groups()
             if verdict == "blocked":
-                blocked[head] = nonce_of(body)
+                blocked[head] = body
                 continue
             if head not in blocked or head in seen:
                 continue
             seen.add(head)
-            mn, bn = nonce_of(body), blocked[head]
-            mt, bt = disp.get(mn or ""), disp.get(bn or "")
-            if mn and mn == bn:
-                tag = "SAME"
-            elif mt and bt:
-                tag = "STALE" if mt < bt else "LATER"
-            else:
-                tag = "UNKNOWN"
-            counts[tag] += 1
-            print(f"{tag} pr={pr} head={head[:8]} merge={mn}@{mt} blocked={bn}@{bt}")
+            yield pr, head, sha, body, blocked[head]
+
+
+def guard(state: str) -> int:
+    import os
+    import merge_train
+    os.environ["HPO_BUS_STATE"] = state
+
+    def run(argv, cwd=ROOT, stdin=None):  # instances() fetched every verdict ref already
+        if argv[:2] == ["git", "fetch"]:
+            return 0, ""
+        p = subprocess.run(argv, cwd=cwd, input=stdin, capture_output=True, text=True)
+        return p.returncode, p.stdout + p.stderr
+
+    t = merge_train.Train("o/r", Path(state), None, "", (), 1, run=run, log=lambda m: None)
+    probe = getattr(t, "stale_verdict", None)
+    gen = instances()
+    refs = next(gen)
+    counts = {"admitted": 0, "refused-stale": 0, "refused-undecidable": 0}
+    for pr, head, sha, _, _ in gen:
+        why = probe(int(pr), sha, head) if probe else None
+        tag = ("admitted" if not why else "refused-undecidable" if "undecidable" in why
+               else "refused-stale")
+        counts[tag] += 1
+        print(f"{tag} pr={pr} head={head[:8]} merge={sha[:8]} {why or ''}".rstrip())
+    print(f"verdict refs={len(refs)} instances={sum(counts.values())} guard={'yes' if probe else 'absent'} "
+          + " ".join(f"{k}={v}" for k, v in counts.items()))
+    return 0
+
+
+def stale(events: str) -> int:
+    disp = dispatch_times(events)
+    counts = {"STALE": 0, "LATER": 0, "SAME": 0, "UNKNOWN": 0}
+    gen = instances()
+    refs = next(gen)
+    for pr, head, _, body, bbody in gen:
+        mn, bn = nonce_of(body), nonce_of(bbody)
+        mt, bt = disp.get(mn or ""), disp.get(bn or "")
+        if mn and mn == bn:
+            tag = "SAME"
+        elif mt and bt:
+            tag = "STALE" if mt < bt else "LATER"
+        else:
+            tag = "UNKNOWN"
+        counts[tag] += 1
+        print(f"{tag} pr={pr} head={head[:8]} merge={mn}@{mt} blocked={bn}@{bt}")
     print(f"verdict refs={len(refs)} instances={sum(counts.values())} "
           + " ".join(f"{k.lower()}={v}" for k, v in counts.items()))
     return 0
@@ -140,6 +191,8 @@ def bodies(dump: str) -> int:
 if __name__ == "__main__":
     if len(sys.argv) == 3 and sys.argv[1] == "stale":
         sys.exit(stale(sys.argv[2]))
+    if len(sys.argv) == 3 and sys.argv[1] == "guard":
+        sys.exit(guard(sys.argv[2]))
     if len(sys.argv) == 3 and sys.argv[1] == "bodies":
         sys.exit(bodies(sys.argv[2]))
     sys.exit(__doc__)
diff --git a/dev/programme/delivery/3364.md b/dev/programme/delivery/3364.md
new file mode 100644
index 000000000..abeda0615
--- /dev/null
+++ b/dev/programme/delivery/3364.md
@@ -0,0 +1 @@
+- [#3364](https://github.com/tvofi/heatpump_optimizer/pull/3364) — **open**, R10-TRAIN-STALE-VERDICT-GUARD: train stale verdict guard (R10-TRAIN-STALE-VERDICT-GUARD)
diff --git a/tools/audit/seat/cloud_dispatch.py b/tools/audit/seat/cloud_dispatch.py
index 18268798f..a1037afdd 100644
--- a/tools/audit/seat/cloud_dispatch.py
+++ b/tools/audit/seat/cloud_dispatch.py
@@ -86,6 +86,7 @@ def _sibling(name: str):
 
 ref_privacy = _sibling("ref_privacy")
 roster_lib = _sibling("roster_lib")
+proof_watch = _sibling("proof_watch")  # the bus-nonce line's one Python reader
 HOME = re.compile(ref_privacy.HOME_DIR)
 LOWER_HEX = frozenset("0123456789abcdef")
 
@@ -555,10 +556,10 @@ def _bus_dispatch(repo_dir: str, pr: str, head: str, model: str, nonce: str, env
     r = subprocess.run(["bash", str(HERE / "bus.sh"), "dispatch", pr, head, "cloud", "--model", model,
                         *(["--nonce", nonce] if nonce else [])],
                        cwd=repo_dir, env={**os.environ, **environ}, capture_output=True, text=True)
-    m = re.search(r"^bus-nonce: ([0-9a-f]{32})$", r.stdout, re.M)
-    if r.returncode or not m:
+    n = proof_watch.verdict_nonce(r.stdout)
+    if r.returncode or not n:
         raise Refusal(f"bus.sh dispatch refused: {(r.stderr or r.stdout).strip()[-300:]}")
-    return m.group(1)
+    return n
 
 
 def _config(args: argparse.Namespace, environ=None) -> dict:
@@ -915,8 +916,7 @@ def _group_checks(check) -> None:
                                env={**os.environ, **env}, capture_output=True, text=True).stdout
         # Search, never strip a prefix: `dispatch` prints its `review-packet:` line
         # above the nonce, and `_bus_dispatch` reads it the same way.
-        _m = re.search(r"^bus-nonce: ([0-9a-f]{32})$", relay, re.M)
-        nonce81 = _m.group(1) if _m else ""
+        nonce81 = proof_watch.verdict_nonce(relay) or ""
         check("a relay dispatch at a second pull request mints its nonce", len(nonce81) == 32)
         out = io.StringIO()
         with contextlib.chdir(work), contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()), \
diff --git a/tools/audit/seat/instruments/merge_train.py.md b/tools/audit/seat/instruments/merge_train.py.md
index c7f4806bc..659f096db 100644
--- a/tools/audit/seat/instruments/merge_train.py.md
+++ b/tools/audit/seat/instruments/merge_train.py.md
@@ -42,6 +42,13 @@
   (tvofi 2026-11-01, batch by default).
   `add`'s admission (`Train.admit_add`) reads the same posted verdict
   first, as its `verdict` rule, and fills an absent comment id from it.
+  That read refuses a stale merge verdict (P393, `stale_merge`): a
+  `blocked` commit at the same head on `verdict/<pr>` whose bus-nonce
+  (its VERDICT.md) bus.sh's registry (`$HPO_BUS_STATE/dispatched`, else
+  `~/.zcode/bus/dispatched`) records as dispatched after the merge
+  verdict's; a missing record or utc refuses with its reason, and a
+  blocked verdict under the merge's own nonce is that reviewer's revision.
+  The registry is host-local, so run the train where bus.sh dispatches.
   bus.sh's post loads the train the moment it posts a merge verdict
   (`merge_train.py add --auto`, with `HPO_BUS_TRAIN_STATE` set);
   `sweep` is the slow backstop (`tick_loop.sh --sweep`, every 1800 s by
diff --git a/tools/audit/seat/merge_train.py b/tools/audit/seat/merge_train.py
index a156f1514..40613779c 100644
--- a/tools/audit/seat/merge_train.py
+++ b/tools/audit/seat/merge_train.py
@@ -1201,6 +1201,51 @@ def spool_edit_locked(t: "Train", pr: int, op: str) -> int:
     return 0
 
 
+def bus_registry() -> Path:
+    """bus.sh's worker registry, `$S/dispatched`, where `S=${HPO_BUS_STATE:-$HOME/.zcode/bus}`."""
+    return Path(os.environ.get("HPO_BUS_STATE") or Path.home() / ".zcode" / "bus") / "dispatched"
+
+
+def dispatch_order(registry: str, pr: int, head: str, nonce: str) -> "tuple[str, int] | None":
+    """(utc, line index) of <nonce>'s FIRST record for <pr> at <head> in bus.sh's
+    registry (`<pr> <head> <reviewer> <nonce> <utc> <model>`), its mint: a
+    `--nonce` re-record later is the same dispatch. None when no such record
+    exists or it predates the utc field. The registry is append-only, so the
+    index orders a same-second pair. A mint with no time is not dated by a
+    later re-record: the dispatch happened before that."""
+    for i, ln in enumerate(registry.splitlines()):
+        f = ln.split() + ["", ""]  # a short line reads as empty fields, never an IndexError
+        if f[:2] == [str(pr), head] and f[3] == nonce:
+            try:  # bus.sh writes `date -u +%FT%TZ`; anything else is no time
+                datetime.datetime.strptime(f[4], "%Y-%m-%dT%H:%M:%SZ")
+            except ValueError:
+                return None
+            return f[4], i
+    return None
+
+
+def stale_merge(pr: int, head: str, merge: "str | None", blocked: "list[str | None]", registry: str) -> "str | None":
+    """P393 (triage batch 127): the merge verdict at <head>, nonce <merge>, is
+    refused when a blocked verdict at the same head carries a different nonce
+    dispatched after it (a later reviewer's finding stands), and refused with
+    the reason when either dispatch time is missing. A blocked verdict posted
+    under the merge's own nonce is that reviewer's revision; None admits."""
+    for b in blocked:
+        if merge is not None and b == merge:
+            continue
+        mt = dispatch_order(registry, pr, head, merge) if merge else None
+        bt = dispatch_order(registry, pr, head, b) if b else None
+        if mt is None or bt is None:
+            return (f"stale merge verdict undecidable: a blocked verdict at {head[:12]} carries nonce "
+                    f"{(b or 'none')[:8]} and the merge verdict {(merge or 'none')[:8]}; "
+                    f"{'the merge' if mt is None else 'the blocked'} verdict's dispatch time is not in "
+                    f"bus.sh's registry ({bus_registry()})")
+        if mt < bt:
+            return (f"stale merge verdict: its nonce {merge[:8]} was dispatched at {mt[0]}, before the blocked "
+                    f"verdict's {b[:8]} at {bt[0]}, at the same head {head[:12]}: the later finding stands")
+    return None
+
+
 def already_held(pr: int, verdict: "str | None", seen: dict, spooled: "set[int]") -> "str | None":
     """THE admission rule `add` (`train_add`) and the drain (`Train.queue_take`)
     both apply (P129, P189, P291): None admits <pr> at <verdict>, else why it
@@ -2991,8 +3036,42 @@ class Train:
         got = proof_watch.parse_verdict(first)
         if got is None or got[0] != "merge":
             return f"the newest verdict is {got[0] if got else 'unparsed'}: {first[:120]}"
+        why = self.stale_verdict(n, tip, got[1])
+        if why:
+            return why
         return got[1], str(v.get("id"))
 
+    def stale_verdict(self, n: int, tip: str, head: str) -> "str | None":
+        """P393: None, or why the merge verdict at verdict/<n>'s <tip> is stale. Every
+        older `blocked <head>` commit on verdict/<n> is a finding at the same head;
+        `stale_merge` rules on their bus-nonces (VERDICT.md, which each verdict
+        commit carries as its review tree) against bus.sh's dispatch registry. An
+        unreadable history refuses: it is never read as no blocked verdict."""
+        import proof_watch
+        if self.run(["git", "fetch", "-q", "origin", f"verdict/{n}"])[0]:
+            return f"stale merge verdict undecidable: verdict/{n}'s history could not be read (fetch failed)"
+        code, o = self.run(["git", "log", "--format=%H%x00%s", tip])
+        if code:
+            return f"stale merge verdict undecidable: verdict/{n}'s history could not be read: {o.strip()[-120:]}"
+        blocked = []
+        for ln in o.splitlines():
+            c, _, subj = ln.partition("\x00")
+            m = re.match(rf"verdict: #{n} (.*)$", subj)
+            if c != tip and m and proof_watch.parse_verdict(m.group(1)) == ("blocked", head):
+                blocked.append(c)
+        if not blocked:
+            return None
+
+        def nonce(c: str) -> "str | None":
+            code, o = self.run(["git", "show", f"{c}:VERDICT.md"])
+            return None if code else proof_watch.verdict_nonce(o)
+
+        try:
+            registry = bus_registry().read_text()
+        except OSError:
+            registry = ""
+        return stale_merge(n, head, nonce(tip), [nonce(c) for c in blocked], registry)
+
     # ------------------------------------------------------------- the batch
     def git(self, *argv: str) -> str:
         code, o = self.run(["git", *argv])
@@ -5275,10 +5354,124 @@ def _self_test() -> int:
     _failed_marker_self_test(check)
     _add_self_test(check)
     _queue_self_test(check)
+    _stale_verdict_self_test(check)
     print(f"merge_train self-test: {passed + failed} checks, {failed} failed")
     return 1 if failed else 0
 
 
+def _stale_verdict_self_test(check) -> None:
+    """P393 (R10-TRAIN-STALE-VERDICT-GUARD): a merge verdict at <head> whose
+    dispatch is older than a blocked verdict's at the same head is refused by
+    `posted_verdict`, so by the queue builder and `admit_add` alike. The bus is a
+    stubbed verdict/7 history; bus.sh's registry is a real file under a
+    temporary HPO_BUS_STATE."""
+    sys.modules.setdefault("merge_train", sys.modules[__name__])
+    import proof_watch
+    login, vid = (lambda a: (sorted(a[0])[0], a[1]))(proof_watch.verdict_allowlist(ROOT / "tools/pr/app_approve.sh"))
+    H, OTHER, T, BC, MC = "1" * 40, "3" * 40, "7" * 40, "b" * 40, "a" * 40
+    NM, NB = "a" * 32, "b" * 32
+    tmp = tempfile.TemporaryDirectory()
+
+    calls: list = []
+
+    def world(registry=None, blocked_head=H, blocked_nonce=NB, merge_nonce=NM, log_code=0, fetch_code=0):
+        def run(argv, cwd=ROOT, stdin=None):
+            a = " ".join(argv)
+            calls.append(argv)
+            if argv[:2] == ["git", "fetch"]:
+                # a successful fetch may still print (a redirect warning): its exit code decides
+                return (fetch_code, "fatal: couldn't find remote ref" if fetch_code else "warning: redirecting to https://x/")
+            if argv[:2] == ["git", "ls-remote"]:
+                return 0, f"{T}\trefs/heads/verdict/7\n"
+            if argv[:2] == ["gh", "api"] and "/comments" in a:
+                return 0, json.dumps([[{"id": 42, "created_at": "2026-11-06T23:00:00Z",
+                                        "user": {"login": login, "id": vid},
+                                        "body": f"Fix review: merge {H}\n\nbus: verdict/7 at {T}, confirmed\n"}]])
+            if argv[:2] == ["git", "log"]:  # verdict/7, newest first: the merge tip over a blocked one
+                return (log_code, "fatal: bad object" if log_code else
+                        f"{T}\x00verdict: #7 Fix review: merge {H}\n"
+                        f"{BC}\x00verdict: #7 Fix review: blocked {blocked_head} tests: red\n"
+                        f"{MC}\x00verdict: #7 Fix review: merge {OTHER}\n")
+            if argv[:2] == ["git", "show"] and argv[2].endswith(":VERDICT.md"):
+                n = {T: merge_nonce, BC: blocked_nonce}.get(argv[2].split(":")[0])
+                # A finding quoting the OTHER verdict's nonce in prose (PR 2465's shape) is not this one's.
+                quote = f"- a note on round 2's `bus-nonce: {NB if n != NB else NM}` line\n"
+                return (0, f"Fix review: x\n\n{quote}\nbus-nonce: {n}\n") if n else (0, f"Fix review: x\n\n{quote}")
+            if argv[:3] == ["gh", "pr", "view"]:
+                return 0, json.dumps({"state": "OPEN", "baseRefName": "main", "headRefOid": H})
+            if argv[:2] == ["git", "diff"]:
+                return 0, f"a.py\n{ROW_DIR}/7.md"
+            if "--corpus-filter" in a:  # admit_add's policy read: no fixture file is policy
+                return 0, "\n".join(f for f in (stdin or "").split() if f == "CLAUDE.md")
+            return 0, ""
+        d = Path(tempfile.mkdtemp(dir=tmp.name))
+        if registry is not None:
+            (d / "dispatched").write_text("".join(ln + "\n" for ln in registry))
+        return run, d
+
+    def posted(**w):
+        run, d = world(**w)
+        was = os.environ.get("HPO_BUS_STATE")
+        os.environ["HPO_BUS_STATE"] = str(d)
+        try:
+            t = Train("o/r", Path("."), None, "", (), 1, run=run, log=lambda m: None)
+            return t.posted_verdict(7, T, ({login}, vid)), t.admit_add({"pr": 7, "verdict": H, "verdict_comment": "42"})
+        finally:
+            if was is None:
+                os.environ.pop("HPO_BUS_STATE", None)
+            else:
+                os.environ["HPO_BUS_STATE"] = was
+
+    rec = lambda n, at, h=H: f"7 {h} cmsg_R {n} {at} opus"  # noqa: E731  bus.sh dispatch's six fields
+    stale, stale_add = posted(registry=[rec(NM, "2026-11-06T20:50:26Z"), rec(NB, "2026-11-06T22:13:28Z")])
+    check("stale verdict: STALE -- a merge verdict dispatched before a blocked verdict at the same head is refused "
+          "(PR 3232's times), by posted_verdict and as admit_add's `verdict` rule",
+          isinstance(stale, str) and stale.startswith("stale merge verdict:") and "aaaaaaaa" in stale
+          and "bbbbbbbb" in stale and (stale_add or "").startswith("verdict: stale merge verdict:"))
+    later, later_add = posted(registry=[rec(NB, "2026-11-06T22:13:28Z"), rec(NM, "2026-11-06T23:40:00Z")])
+    check("stale verdict: LATER (null control) -- the merge verdict's dispatch after the blocked one's is admitted",
+          later == (H, "42") and later_add is None)
+    same, same_add = posted(registry=[], blocked_nonce=NM)
+    check("stale verdict: SAME (null control) -- one nonce posted both verdicts, admitted with no dispatch time read",
+          same == (H, "42") and same_add is None)
+    for name, w in (("the merge verdict's nonce has no registry record", {"registry": [rec(NB, "2026-11-06T22:13:28Z")]}),
+                    ("the blocked verdict's nonce has no registry record", {"registry": [rec(NM, "2026-11-06T20:50:26Z")]}),
+                    ("a pre-R10-ORCH-DISPATCH-REG record stops at the nonce",
+                     {"registry": [f"7 {H} cmsg_R {NM}", rec(NB, "2026-11-06T22:13:28Z")]}),
+                    ("a mint before the utc field is not dated by a later --nonce re-record",
+                     {"registry": [f"7 {H} cmsg_R {NM}", rec(NM, "2026-11-06T23:40:00Z"),
+                                   rec(NB, "2026-11-06T22:13:28Z")]}),
+                    ("a malformed time is no time", {"registry": [rec(NM, "2026-11-06T25:61:00Z"),
+                                                                 rec(NB, "2026-11-06T22:13:28Z")]}),
+                    ("no registry file on this machine", {"registry": None}),
+                    ("the blocked verdict carries no bus-nonce", {"registry": [rec(NM, "2026-11-06T23:40:00Z")],
+                                                                  "blocked_nonce": None}),
+                    ("a record at another head is not this nonce's dispatch",
+                     {"registry": [rec(NM, "2026-11-06T23:40:00Z", OTHER), rec(NB, "2026-11-06T22:13:28Z")]})):
+        got = posted(**w)[0]
+        check(f"stale verdict: a missing dispatch time is refused with its reason ({name})",
+              isinstance(got, str) and got.startswith("stale merge verdict undecidable:"))
+    tie = posted(registry=[rec(NM, "2026-11-06T22:13:28Z"), rec(NB, "2026-11-06T22:13:28Z")])[0]
+    tie_later = posted(registry=[rec(NB, "2026-11-06T22:13:28Z"), rec(NM, "2026-11-06T22:13:28Z")])[0]
+    check("stale verdict: a same-second tie is ordered by the registry's append order (refused, then admitted)",
+          isinstance(tie, str) and tie.startswith("stale merge verdict:") and tie_later == (H, "42"))
+    skew = posted(registry=[rec(NB, "2026-11-06T22:13:28Z"), rec(NM, "2026-11-06T20:50:26Z")])[0]
+    check("stale verdict: the dispatch time decides, not the registry's line order (a merge dispatch recorded "
+          "after the blocked one but timed before it is refused)",
+          isinstance(skew, str) and skew.startswith("stale merge verdict:"))
+    calls.clear()
+    other = posted(registry=None, blocked_head=OTHER)[0]
+    check("stale verdict: a blocked verdict at another head is not this head's finding (admitted, no nonce read)",
+          other == (H, "42") and any(c[:2] == ["git", "log"] for c in calls)  # the read ran: the null below is not vacuous
+          and not any(c[:2] == ["git", "show"] for c in calls))
+    unread = posted(registry=[], log_code=128)[0]
+    unfetched = posted(registry=[], fetch_code=128)[0]
+    check("stale verdict: an unreadable verdict/<pr> history (log or fetch) is refused, never read as no blocked verdict",
+          isinstance(unread, str) and "history could not be read" in unread
+          and isinstance(unfetched, str) and "could not be read (fetch failed)" in unfetched)
+    tmp.cleanup()
+
+
 def _failed_marker_self_test(check) -> None:
     """culprit() names a red proof's scripts from run.sh's lane report. The
     report's if/else is lifted from tests/run.sh and driven on a crash log and
diff --git a/tools/audit/seat/proof_watch.py b/tools/audit/seat/proof_watch.py
index 7e7694bf2..6baf73fa4 100644
--- a/tools/audit/seat/proof_watch.py
+++ b/tools/audit/seat/proof_watch.py
@@ -118,6 +118,20 @@ def parse_verdict(first: str) -> "tuple[str, str] | None":
     return None
 
 
+#: The nonce line bus.sh `dispatch` prints and a verdict carries, read as bus.sh's
+#: `verdict_nonce` reads it: the first WHOLE `bus-nonce: <32 hex>` line. Whole-line,
+#: so a finding quoting another round's nonce in prose is not this text's (PR 2465's
+#: merge verdict quotes round 2's). The one Python reader: cloud_dispatch.py and
+#: merge_train.py's stale-verdict guard call it, never a copy.
+NONCE_LINE = re.compile(r"^bus-nonce: ([0-9a-f]{32})$", re.M)
+
+
+def verdict_nonce(text: str) -> "str | None":
+    """The 32-hex nonce of the first whole `bus-nonce:` line in <text>, or None."""
+    m = NONCE_LINE.search(text)
+    return m.group(1) if m else None
+
+
 def _json_docs(raw: str) -> list:
     """What `gh api` prints: concatenated JSON documents, an array per page
     (plain --paginate) or one object per line (--jq '.check_runs[]')."""

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
