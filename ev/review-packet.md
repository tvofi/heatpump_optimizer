# Review packet #3248
head: a101717e588108b4520bb935f59a22fdab31f85f
base: b36679ceaa65a08a67a84f0d934c93aa15f7c7f3

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=127930314755 success
arch-score / arch-score id=127949585479 success
arm id=127929465972 skipped
budget-raise-gate / budget-raise-gate id=127949503694 success
cancel-superseded id=127949502613 success
codeql id=127949503645 skipped
codeql / Analyze (actions) id=127929670507 success
codeql / Analyze (javascript-typescript) id=127929670413 success
codeql / Analyze (python) id=127929670569 success
gate id=127949503809 success
governance id=127949562114 skipped
governance / delivery-status id=127929670556 success
governance / delivery-status-publish id=127929672409 skipped
governance / env-matrix id=127929670565 success
governance / instrument-self-tests id=127929670552 success
governance / policy-docs id=127929670665 success
governance / record id=127929672757 skipped
governance / wave-script id=127929670654 success
hassfest id=127949503820 skipped
hassfest / hassfest id=127929670276 success
kernel-points id=127949575807 skipped
pr-contract id=127949505628 skipped
pr-contract / pr-contract id=127945049366 success
prelude id=127949561481 success
refresh id=127949503510 success
tests id=127949570782 skipped
tests / arch-instrument id=127930092766 success
tests / briefs id=127929670443 success
tests / browser id=127930093154 success
tests / ci-ratchet id=127940816728 skipped
tests / claims-autofix id=127936717193 skipped
tests / closure-scope id=127929670448 success
tests / closures id=127930092910 success
tests / closures-autofix id=127940816785 skipped
tests / coverage id=127930092730 success
tests / coverage-ratchet id=127939975660 success
tests / fast (3.14) id=127930093190 success
tests / graders-head-copy id=127939975687 success
tests / lane-proofs id=127939975697 success
tests / mutation id=127929670615 success
tests / mutation-autofix id=127930529159 skipped
tests / mutation-pins id=127930528780 skipped
tests / nightly-ha id=127930094293 skipped
tests / nightly-status id=127929670520 success
tests / replay id=127930095128 skipped
tests / typing id=127930092877 success
validate id=127949504087 skipped
validate / validate-hacs id=127929670167 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/audit/seat/ledger.py --self-test
             `tools/audit/seat/ledger.py` is in the tree at this head
  ok         python3 tools/audit/seat/orchestrator_tick.py --self-test
             `tools/audit/seat/orchestrator_tick.py` is in the tree at this head
  ok         bash tools/audit/seat/bus.sh --self-test
             `tools/audit/seat/bus.sh` is in the tree at this head
  ok         python3 tools/audit/seat/r10_ledger_mutants.py --self-test
             `tools/audit/seat/r10_ledger_mutants.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         bash tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 6 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3248.md b/dev/programme/delivery/3248.md
new file mode 100644
index 000000000..89ce6a004
--- /dev/null
+++ b/dev/programme/delivery/3248.md
@@ -0,0 +1 @@
+- [#3248](https://github.com/tvofi/heatpump_optimizer/pull/3248) — **open**, R10-LEDGER-RESIDUE: the obligations ledger residue of R10-ORCH-LEDGER (R10-LEDGER-RESIDUE)
diff --git a/tools/audit/seat/bus.sh b/tools/audit/seat/bus.sh
index bb14786a4..3754fa66d 100755
--- a/tools/audit/seat/bus.sh
+++ b/tools/audit/seat/bus.sh
@@ -725,7 +725,7 @@ watch() {
 orphans() { # [--min-age-h N] [--no-body] [--no-ancestry] [--no-content] [--exclude-topic T]... -> one ORPHAN line each, rc 1 when any stranded
   local ns=refs/hpo-orphans LF=$'\n' min_age=2 no_body=0 no_ancestry=0 no_content=0 excl=$'\n'
   local t ref tip main fix_nl fix_heads bodies_nl landed_nl why hit arms
-  local reported=0 superseded=0 nb=0 named=0 anc=0 young=0
+  local reported=0 superseded=0 nb=0 named=0 anc=0 young=0 mrg=0 mt merged_nl
   local ct now age_s age_t word dn H bt
   while [ $# -gt 0 ]; do
     case $1 in
@@ -765,6 +765,17 @@ orphans() { # [--min-age-h N] [--no-body] [--no-ancestry] [--no-content] [--excl
   landed_nl=$LF"$(git for-each-ref --format='%(objectname)' "$ns/handoff/" \
     | python3 -I "$ROOT/tools/audit/seat/ledger.py" landed ${arms[@]+"${arms[@]}"} "$main" $fix_heads)"$LF \
     || die "orphans: ledger.py landed could not classify the handoff tips"
+  # MERGED, the level's last arm (R10-LEDGER-RESIDUE, #2721): a pull request of the topic merged at or
+  # after the tip's commit time delivered it, and main has since moved the files on, which no ref test
+  # sees. The listing is the relay's (`gh pr list --state merged`; $HPO_BUS_MERGED stubs it, printing
+  # `<head>\t<epoch>`). An unread listing says so on stderr and the run goes on without the arm: that
+  # can only add ORPHAN lines, never hide one.
+  merged_nl=$LF"$( { if [ -n "${HPO_BUS_MERGED:-}" ]; then $HPO_BUS_MERGED
+      else ${HPO_BUS_GH:-gh} pr list -R "$REPO" --state merged --limit 200 --json headRefName,mergedAt \
+        -q '.[] | [.headRefName, (.mergedAt | fromdateiso8601)] | @tsv'; fi; } 2>/dev/null \
+    | awk -F'\t' 'NF == 2 && $2 ~ /^[0-9]+$/ { t = $1; sub(/^fix\//, "", t); sub(/-pr$/, "", t)
+                  if ($2 > m[t]) m[t] = $2 } END { for (t in m) print t " " m[t] }')"$LF
+  case $merged_nl in *" "[0-9]*) ;; *) echo "orphans: merged pull requests unread; a merged handoff reads ORPHAN here" >&2 ;; esac
   now=$(date +%s)
   # A while-read over a heredoc, not a pipe: the counters survive the loop.
   while read -r ref tip; do
@@ -800,6 +811,11 @@ orphans() { # [--min-age-h N] [--no-body] [--no-ancestry] [--no-content] [--excl
       printf 'ORPHAN %s %s unknown-age uncovered=? repair=review\n' "$t" "$tip"
       reported=$((reported + 1)); continue
     fi
+    mt=${merged_nl#*"$LF$t "}
+    if [ "$mt" != "$merged_nl" ]; then
+      mt=${mt%%"$LF"*}
+      if [ "$mt" -ge "$ct" ]; then mrg=$((mrg + 1)); continue; fi
+    fi
     age_s=$((now - ct)); [ "$age_s" -lt 0 ] && age_s=0
     if [ "$((age_s / 3600))" -lt "$min_age" ]; then young=$((young + 1)); continue; fi
     age_t=$((age_s / 360))
@@ -833,8 +849,8 @@ orphans() { # [--min-age-h N] [--no-body] [--no-ancestry] [--no-content] [--excl
   done <<EOF
 $(git for-each-ref --format='%(refname) %(objectname)' "$ns/handoff/")
 EOF
-  printf 'orphans: %s stranded, %s superseded; skipped no-body=%s named=%s ancestor=%s young=%s; %s main %s\n' \
-    "$reported" "$superseded" "$nb" "$named" "$anc" "$young" "$REMOTE" "${main:0:7}"
+  printf 'orphans: %s stranded, %s superseded; skipped no-body=%s named=%s ancestor=%s young=%s merged-pr=%s; %s main %s\n' \
+    "$reported" "$superseded" "$nb" "$named" "$anc" "$young" "$mrg" "$REMOTE" "${main:0:7}"
   [ "$reported" = 0 ]
 }
 
@@ -1410,6 +1426,18 @@ B
   out=$(run orphans --min-age-h 0); rc=$?
   echo "$out" | grep -qx "ORPHAN orph1 $o1 .* repair=opener" && [ $rc = 1 ]
   expect "orphans reports an owed handoff with no pull request as repair=opener, exit 1" $?
+  # The level's merged-pull-request arm (#2721): a pull request of the topic merged at or after the tip's
+  # commit time delivered it; one merged before it (a re-handoff committed later) leaves it owed.
+  mrg_after=$(( $(date +%s) + 100 ))
+  out=$(HPO_BUS_MERGED="printf fix/orph1\\t$mrg_after\\n" run orphans --min-age-h 0); rc=$?
+  ! echo "$out" | grep -q "^ORPHAN orph1 " && [ $rc = 0 ] && echo "$out" | grep -q "merged-pr=1"
+  expect "a handoff whose pull request merged at or after its tip is merged-pr, not ORPHAN" $?
+  out=$(HPO_BUS_MERGED="printf fix/orph1\\t1\\n" run orphans --min-age-h 0); rc=$?
+  echo "$out" | grep -qx "ORPHAN orph1 $o1 .* repair=opener" && [ $rc = 1 ] && echo "$out" | grep -q "merged-pr=0"
+  expect "null control: a pull request merged before the tip leaves it ORPHAN" $?
+  out=$(HPO_BUS_MERGED="printf nothing" run orphans --min-age-h 0); rc=$?
+  echo "$out" | grep -qx "ORPHAN orph1 $o1 .* repair=opener" && [ $rc = 1 ] && echo "$out" | grep -q "merged pull requests unread"
+  expect "null control: an unread listing says so and the refs-only answer stands" $?
   # Null control 1: the same ref inside the age window is in flight, not an orphan.
   out=$(run orphans); rc=$?
   ! echo "$out" | grep -q "^ORPHAN orph1 " && [ $rc = 0 ] && echo "$out" | grep -q "young="
diff --git a/tools/audit/seat/ledger.py b/tools/audit/seat/ledger.py
index b5e3424db..89b882803 100644
--- a/tools/audit/seat/ledger.py
+++ b/tools/audit/seat/ledger.py
@@ -74,7 +74,11 @@ threshold, oldest first, naming the roster group and the repair; an OWNER FLAG
 at the second. The thresholds are policy (tvofi's); the switch is
 HPO_LEDGER_AGING = `<dispatch_h>,<owner_h>` or `off`, defaulting to the
 owner's ruling of 2026-10-21 (4 h, 12 h). A tip stamped ahead of the clock has
-no age (fixer.md step 16): it escalates nothing.
+no age (fixer.md step 16): it escalates nothing. Only an arrival after the
+newest fix/ or handoff/ pull-request opening ages (the tick passes it; the
+standing backlog would otherwise hold the alarm up for ever); an unread
+opening keys on age alone. `dispose` into a home other than the default says
+so on stderr: the tick reads the default.
 
 EXIT CODES (`board`, `level`, `disposed`). 0: nothing owed (not disposed).
 1: obligations exist (disposed), the finding, with `board`'s summary line.
@@ -287,7 +291,9 @@ def _import_log(log: str) -> "tuple[list, list[str]]":
             elif f[2] == "handoff-update":
                 continue  # derived now: the relay's level from cloud-handoff-failed
             elif f[2] == pr and len(f) > 3 and (f[3] == "-" or is_sha(f[3])):
-                kind, when, sha = "verdict-unposted", f[1], "-"
+                # the journal line's own sha, when it names one: the fold's head-move and read-back
+                # closers key on it (an imported row's text is not a verdict's first line)
+                kind, when, sha = "verdict-unposted", f[1], f[3] if is_sha(f[3]) else "-"
             else:
                 refused.append(f"'{line}' is no relay OWED shape")
                 continue
@@ -350,8 +356,11 @@ def fold(rows: list, live: "dict | None" = None, readback: "dict | None" = None)
                    else "superseded" if sha != "-" and live[subj] != sha else None)
         if how is None and kind in PR_KEYED and readback is not None and subj in readback:
             lines = readback[subj]
-            if (text in lines if kind == "verdict-unposted"
-                    else sha != "-" and any(verdict_head(l) == sha for l in lines)):
+            named = sha != "-" and any(verdict_head(l) == sha for l in lines)
+            # a native row's text is the verdict's first line; an imported one keeps the journal line,
+            # which no read-back equals, so it closes on the sha it names like the other kinds
+            if (text in lines or (named and verdict_head(text) is None) if kind == "verdict-unposted"
+                    else named):
                 how = "read-back"
         if how:
             closed[how] += 1
@@ -570,8 +579,14 @@ def parse_aging(value: "str | None"):
     return a, b
 
 
-def escalate(level_rows: list, now: datetime.datetime, aging, group_of) -> list[str]:
-    """DISPATCH lines, oldest first, then OWNER FLAG lines, one per topic."""
+def escalate(level_rows: list, now: datetime.datetime, aging, group_of,
+             last_open: "float | None" = None) -> list[str]:
+    """DISPATCH lines, oldest first, then OWNER FLAG lines, one per topic.
+    `last_open` is the epoch of the newest pull-request opening of a fix/ or
+    handoff/ branch: a tip committed at or before it is the standing backlog,
+    which an age-only threshold would flag for ever, and escalates nothing;
+    only an arrival after the last opening ages (as pulse.py's opener rule
+    does). None (the opening unread) keys on age alone: it over-owes."""
     if aging is None:
         return []
     by: dict[str, dict] = {}
@@ -587,6 +602,8 @@ def escalate(level_rows: list, now: datetime.datetime, aging, group_of) -> list[
         ref, sha, kv = refs.get("code") or refs["body"]
         if not kv.get("ct", "").isdigit():
             continue
+        if last_open is not None and int(kv["ct"]) <= last_open:
+            continue
         age = (now.timestamp() - int(kv["ct"])) / 3600  # ahead of the clock: < 0, below any threshold
         repair = ("no code ref" if "code" not in refs
                   else "opener" if "body" in refs or "body" in refs["code"][2] else "no body ref")
@@ -668,6 +685,9 @@ def main(argv: list) -> int:
     try:
         if cmd == "dispose" and len(args) in (2, 3):
             dispose(home, args[0], args[1], args[2] if len(args) == 3 else "disposed")
+            if home.resolve() != Path(default_log()).parent.resolve():
+                print(f"ledger: dispose wrote to {home}, not the default home; the tick reads "
+                      f"{Path(default_log()).parent}", file=sys.stderr)
             print(f"ledger: disposed {args[0]} {args[1]}")
             return 0
         if cmd == "disposed" and len(args) == 2:
@@ -759,6 +779,25 @@ def self_test() -> int:
               (h / DISP).read_text().count("\n") == 1 + 3 + 1 and dispositions(h)["refs/heads/probe/q"][0] == C)
         check("a ref matching no arm in the import was refused (wip-sync)",
               "refs/heads/wip-sync/x" not in dispositions(h))
+        import contextlib
+        import io
+        nh = D / "nondefault"
+        nh.mkdir()
+        with contextlib.redirect_stderr(io.StringIO()) as err, contextlib.redirect_stdout(io.StringIO()):
+            rc_n = main(["--log", str(nh / "cloud-relay.log"), "dispose", "refs/heads/probe/n", C])
+        check("dispose into a non-default home names it on stderr and still writes (carry 3)",
+              rc_n == 0 and str(nh) in err.getvalue() and "default home" in err.getvalue()
+              and dispositions(nh)["refs/heads/probe/n"][0] == C)
+        dflt = D / "dflt"
+        dflt.mkdir()
+        os.environ["HPO_STATE_DIR"] = str(dflt)
+        try:
+            with contextlib.redirect_stderr(io.StringIO()) as err, contextlib.redirect_stdout(io.StringIO()):
+                rc_d = main(["dispose", "refs/heads/probe/n", C])
+        finally:
+            del os.environ["HPO_STATE_DIR"]
+        check("null control: dispose into the default home prints nothing and writes",
+              rc_d == 0 and err.getvalue() == "" and dispositions(dflt)["refs/heads/probe/n"][0] == C)
         check("dispose refuses a ref of no arm", refuses(lambda: dispose(h, "refs/heads/main", A)) == "Refused")
         check("a missing store with no legacy file is first run: empty", dispositions(D / "none") == {})
         (D / "bad").mkdir()
@@ -820,6 +859,26 @@ def self_test() -> int:
         o2, _ = fold(rv, live=live, readback={"20": [f"Fix review: merge {A}"]})
         check("a relayed claim is no close: a read-back of another verdict leaves it open",
               "20" in {s for _, s, *_ in o2})
+        iv = [["open", "t", "verdict-unposted", "24", C, f"OWED t verdict-unposted 24 {C}"],
+              ["open", "t", "verdict-unposted", "25", "-", "OWED t verdict-unposted 25 -"]]
+        oi, ci = fold(iv, live={"24": C, "25": C}, readback={"24": [v], "25": [v]})
+        check("an imported verdict-unposted closes on a read-back naming its sha (carry 1)",
+              {s for _, s, *_ in oi} == {"25"} and ci["read-back"] == 1)
+        oi2, ci2 = fold(iv, live={"24": A, "25": C})
+        check("and on the PR head moving off it; a sha-less import stays owed (`close ... -` is its closer)",
+              {s for _, s, *_ in oi2} == {"25"} and ci2["superseded"] == 1)
+        oi3, _ = fold(iv, live={"24": C}, readback={"24": [f"Fix review: merge {A}"]})
+        check("null control: a read-back of another sha leaves the imported row open",
+              "24" in {s for _, s, *_ in oi3})
+        (D / "implog").mkdir()
+        ilog = str(D / "implog" / "cloud-relay.log")
+        Path(ilog).write_text(f"OWED 2026-10-18T19:00:00Z 30 {C} bus.sh confirm failed; run it by hand\n")
+        ir = events(D / "implog", ilog)
+        oq, cq = fold(ir, live={"30": C}, readback={"30": [f"Fix review: merge {C}"]})
+        check("a log OWED line imported through _import_log keeps its sha and a read-back naming it closes it (carry 1)",
+              ir[0][4] == C and not oq and cq["read-back"] == 1)
+        oq2, _ = fold(ir, live={"30": C}, readback={"30": [f"Fix review: merge {A}"]})
+        check("null control: the imported row stays open on a read-back of another sha", len(oq2) == 1)
         o3, c3 = fold(rv, live={"23": C})
         check("a PR no longer open closes its PR-keyed events (subject-absent)",
               {s for _, s, *_ in o3} == {"23"} and c3["subject-absent"] == 3)
@@ -845,6 +904,15 @@ def self_test() -> int:
               == ["R10-OLD"])
         check("null control: a young tip and a tip ahead of the clock escalate nothing",
               not any("/new " in x or "/fut " in x for x in es))
+        after_old = escalate(lv, now, parse_aging(None), dict().get, ts(20))
+        check("a tip committed before the last opening is backlog and escalates nothing; a later arrival still ages (carry 2)",
+              [x.split()[2] for x in after_old] == ["refs/heads/handoff/mid"]
+              and len(escalate(lv, now, parse_aging("0.5,40"), dict().get, ts(20))) == 2)
+        check("null control: the opening unread (None) keys on age alone, as before",
+              escalate(lv, now, parse_aging(None), dict().get, None)
+              == escalate(lv, now, parse_aging(None), dict().get))
+        check("a tip committed exactly at the last opening is backlog",
+              not escalate(lv[:1], now, parse_aging(None), dict().get, ts(30)))
         check("the switch off escalates nothing", escalate(lv, now, parse_aging("off"), dict().get) == [])
         check("a malformed switch is refused", refuses(lambda: parse_aging("4")) == "Refused"
               and refuses(lambda: parse_aging("12,4")) == "Refused")
diff --git a/tools/audit/seat/orchestrator_tick.py b/tools/audit/seat/orchestrator_tick.py
index c605a1601..2247e7a28 100644
--- a/tools/audit/seat/orchestrator_tick.py
+++ b/tools/audit/seat/orchestrator_tick.py
@@ -1008,6 +1008,21 @@ class Tick:
             self.unreadable(S, "bus dispatch record (REVIEW OWED)", str(e)[:100])
             return None
 
+    def last_opening(self, S: str) -> "float | None":
+        """Epoch of the newest pull request opened from a fix/ or handoff/ branch, any state
+        (the arrival key of `ledger.escalate`); None, reported, when the listing is unreadable."""
+        code, o = self.gh(["pr", "list", "--repo", self.repo, "--state", "all", "--limit", "30",
+                           "--json", "headRefName,createdAt"])
+        try:
+            if code:
+                raise ValueError(o.strip()[-100:])
+            ts = [datetime.datetime.fromisoformat(p["createdAt"].replace("Z", "+00:00")).timestamp()
+                  for p in json.loads(o) if p["headRefName"].startswith(("fix/", "handoff/"))]
+        except (ValueError, KeyError, TypeError) as e:
+            self.unreadable(S, "newest pull-request opening (handoff aging keys on age alone)", str(e)[:100])
+            return None
+        return max(ts) if ts else None
+
     def relay_owed(self, S: str) -> None:
         """`OWED: <line>` every pass for what the obligations ledger holds open
         (`ledger.py`, the one schema; R10-ORCH-LEDGER). The relay's DERIVED
@@ -1051,8 +1066,9 @@ class Tick:
                 read.append(self._roster(S, announce=False) if hasattr(self, "_roster") else (None, None))
             rl, rost = read[0]
             return rl.group_for_branch(rost, f"handoff/{t}") if rl else None
+        last_open = self.last_opening(S) if aging and any(" handoff-no-pr " in r for r in level) else None
         for text in lg.escalate(level, getattr(self, "now", None) or datetime.datetime.now(datetime.timezone.utc),
-                                aging, group_of):
+                                aging, group_of, last_open):
             self.line(S, text, flag=True)
         home = Path(self.relay_log).parent
         try:
@@ -4475,7 +4491,7 @@ def self_test() -> int:
         seq = iter(range(1000))
 
         def owed_lines(text=None, level=None, events=None, live=None, readback=None, aging=None,
-                       roster_groups=None):
+                       roster_groups=None, gh_extra=None):
             home = tmp / f"ledger{next(seq)}"
             home.mkdir()
             lg = home / "cloud-relay.log"
@@ -4493,7 +4509,7 @@ def self_test() -> int:
             if aging is not None:
                 os.environ["HPO_LEDGER_AGING"] = aging
             try:
-                t = tick(relay_log=str(lg), roster=str(rf) if rf else None)
+                t = tick(relay_log=str(lg), roster=str(rf) if rf else None, gh_extra=gh_extra)
                 t._live, t._readback = live, readback
                 t.relay_owed("PRS")
             finally:
@@ -4537,6 +4553,13 @@ def self_test() -> int:
                f"OWED 2026-10-12T17:00:00Z handoff-no-pr refs/heads/handoff/r10-new {'c' * 40} ct={ct2}\n")
         grp = [{"group": "R10-OLD", "resume": {"stage": "in-progress"}}]
         aged, _ = owed_lines(None, agl, roster_groups=grp)
+        ct10 = int((NOW - datetime.timedelta(hours=10)).timestamp())
+        opened = json.dumps([{"headRefName": "fix/other", "createdAt": datetime.datetime.fromtimestamp(
+            ct10, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}, {"headRefName": "dependabot/x", "createdAt": "2099-01-01T00:00:00Z"}])
+        agl4 = agl.replace(f"ct={ct2}", f"ct={ct2 - 3 * 3600}")  # r10-new: committed 5 h ago, after the opening
+        arrivals, _ = owed_lines(None, agl4, roster_groups=grp,
+                                 gh_extra=[(("pr", "list", "--state", "all"), 0, opened)])
+        no_listing, _ = owed_lines(None, agl4, roster_groups=grp, gh_extra=[(("pr", "list", "--state", "all"), 1, "boom")])
         aged_off, _ = owed_lines(None, agl, aging="off", roster_groups=grp)
         aged_bad, _ = owed_lines(None, agl, aging="4", roster_groups=grp)
         a, f = check("relay OWED", [
@@ -4564,6 +4587,12 @@ def self_test() -> int:
              any("UNREADABLE: obligations ledger" in x for x in flagged(unread_ev))),
             ("no store and no log yet is no OWED and no flag",
              not any(l["flag"] for l in none) and any("obligations ledger: none yet" in l["text"] for l in none)),
+            ("aging keys on arrivals after the newest fix/ or handoff/ opening: the 30 h backlog tip is silent, "
+             "the 5 h arrival escalates (carry 2)",
+             [x.split()[2] for x in flagged(arrivals) if x.startswith("DISPATCH")] == ["refs/heads/handoff/r10-new"]),
+            ("null control: an unreadable opening listing is UNREADABLE and keys on age alone, flagging the backlog",
+             any("UNREADABLE: newest pull-request opening" in x for x in flagged(no_listing))
+             and any("handoff/r10-old" in x for x in flagged(no_listing) if x.startswith("DISPATCH"))),
             ("a stranded handoff past 4 h is a DISPATCH line naming its group and opener, oldest first",
              [x.split(" (")[0] for x in flagged(aged) if x.startswith("DISPATCH")]
              == [f"DISPATCH: R10-OLD refs/heads/handoff/r10-old {'c' * 12} opener"]),
diff --git a/tools/audit/seat/r10_ledger_mutants.py b/tools/audit/seat/r10_ledger_mutants.py
index 84256aaf9..c56f1b351 100644
--- a/tools/audit/seat/r10_ledger_mutants.py
+++ b/tools/audit/seat/r10_ledger_mutants.py
@@ -34,7 +34,7 @@ PLANTS = {
     # the ledger: event closers, the level's closers, aging, refusals, stores
     "L1_readback_no_close": (LEDGER, '                how = "read-back"', "                how = None"),
     "L2_moved_head_kept": (LEDGER, 'else "superseded" if sha != "-" and live[subj] != sha else None)', "else None)"),
-    "L3_any_verdict_posts": (LEDGER, '(text in lines if kind == "verdict-unposted"',
+    "L3_any_verdict_posts": (LEDGER, '(text in lines or (named and verdict_head(text) is None) if kind == "verdict-unposted"',
                              '(bool(lines) if kind == "verdict-unposted"'),
     "L4_added_lines_unchecked": (LEDGER, "if not add <= have or rem & have:", "if rem & have:"),
     "L5_no_ancestry_close": (LEDGER, '''        if rc == 0 and out.strip() == "0":
@@ -58,6 +58,11 @@ PLANTS = {
                               "        elif False:\n            continue"),
     "L30_merged_strictly_before": (LEDGER, "and int(ct[code.get(t, sha)]) <= merged[t]:", "and int(ct[code.get(t, sha)]) < merged[t]:"),
     "L31_merged_last_listed": (LEDGER, "merged[f[0]] = max(merged.get(f[0], 0), int(when))", "merged[f[0]] = int(when)"),
+    "L32_dispose_home_silent": (LEDGER, "            if home.resolve() != Path(default_log()).parent.resolve():", "            if False:"),
+    "L33_imported_verdict_unclosable": (LEDGER, "(text in lines or (named and verdict_head(text) is None) if", "(text in lines if"),
+    "L35_import_sha_dropped": (LEDGER, 'kind, when, sha = "verdict-unposted", f[1], f[3] if is_sha(f[3]) else "-"', 'kind, when, sha = "verdict-unposted", f[1], "-"'),
+    "L34_backlog_escalates": (LEDGER, '        if last_open is not None and int(kv["ct"]) <= last_open:', '        if False:'),
+    "B4_orphans_merged_pr_ignored": (BUS, '      if [ "$mt" -ge "$ct" ]; then mrg=$((mrg + 1)); continue; fi', '      if false; then mrg=$((mrg + 1)); continue; fi'),
     "R6_merged_unread_clears": (RELAY, '"$state/cloud-merged.$$" \\\n    || { echo "cloud_relay: could not list merged PRs',
                                 '"$state/cloud-merged.$$" \\\n    || true || { echo "cloud_relay: could not list merged PRs'),
     "B1_orphans_merges_stranded": (BUS, "    case $why in ancestor|merges-only) anc=", "    case $why in ancestor) anc="),
@@ -90,8 +95,8 @@ PLANTS = {
     "T2_no_reads_fold": (TICK, 'lg.fold(rows, getattr(self, "_live", None), getattr(self, "_readback", None))', "lg.fold(rows)"),
     "T3_review_owed_silent": (TICK, '                                       getattr(rr, "RECORD_BRANCH", None)):\n                self.line(S, text, flag=True)',
                               '                                       getattr(rr, "RECORD_BRANCH", None)):\n                pass'),
-    "T4_no_escalation": (TICK, "                                aging, group_of):\n            self.line(S, text, flag=True)",
-                         "                                aging, group_of):\n            pass"),
+    "T4_no_escalation": (TICK, "                                aging, group_of, last_open):\n            self.line(S, text, flag=True)",
+                         "                                aging, group_of, last_open):\n            pass"),
     "T5_no_design_build": (TICK, "        self.design_builds(S, rl, roster)\n", ""),
     "T6_unreadable_silent": (TICK, '            self.unreadable(S, "obligations ledger", str(e)[:100])\n            return\n        if not rows',
                              "            return\n        if not rows"),

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
