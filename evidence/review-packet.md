# Review packet #3450
head: 8af19472a77eb2c51517f57bc2bf5597a0638927
base: cbd23f1c8bf6185c3a6c10f6e4aaf562417e75bf

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=130543122220 success
arch-score / arch-score id=130545704165 in_progress
arm id=130539650271 skipped
budget-raise-gate / budget-raise-gate id=130545704399 queued
cancel-superseded id=130543355307 queued
codeql id=130545703781 skipped
codeql / Analyze (actions) id=130542022733 success
codeql / Analyze (javascript-typescript) id=130542023119 success
codeql / Analyze (python) id=130542022846 success
gate id=130545630579 queued
governance id=130545703948 skipped
governance / delivery-status id=130542022920 success
governance / delivery-status-publish id=130542026307 skipped
governance / env-matrix id=130542022892 in_progress
governance / instrument-self-tests id=130542022785 in_progress
governance / policy-docs id=130542022845 success
governance / record id=130542025966 skipped
governance / wave-script id=130542022871 success
hassfest id=130545703393 skipped
hassfest / hassfest id=130542022442 success
kernel-points id=130545703552 skipped
pr-contract id=130545631995 skipped
prelude id=130543354758 success
refresh id=130543354517 success
tests id=130545703814 skipped
tests / briefs id=130542022732 queued
tests / closure-scope id=130542022956 queued
tests / mutation id=130542022677 in_progress
tests / nightly-status id=130542022657 failure
validate id=130545703685 skipped
validate / validate-hacs id=130542022641 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item aee61a46: R10-REVIEW-DISPATCH-RESIDUE: R10-REVIEW-DISPATCH-RESIDUE resolved on origin/handoff/audit-r10-roster
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 dev/audit/harnesses/r10_flow_dispatch_mutants.py
             `dev/audit/harnesses/r10_flow_dispatch_mutants.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
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

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_flow_dispatch_mutants.py b/dev/audit/harnesses/r10_flow_dispatch_mutants.py
index d0a103a24..f5628d102 100644
--- a/dev/audit/harnesses/r10_flow_dispatch_mutants.py
+++ b/dev/audit/harnesses/r10_flow_dispatch_mutants.py
@@ -12,7 +12,8 @@ cli-model-fixed, cli-overlay-dropped); round 5 added the flag table's arms
 R10-FLY-CACHE-PROMPTS re-aimed nonce-altered, topic-to-id, prompt-wrong and
 flag-unlisted at the publish_seat path and added the pointer, --publish, wait-cap
 and read-list arms (pointer-ref-dropped .. claude-md-reread). Each
-mutant is a one-occurrence replacement in tools/audit/seat/cloud_dispatch.py;
+mutant is a one-occurrence replacement in tools/audit/seat/cloud_dispatch.py
+(or the roster_lib.py a fourth element names);
 it is applied alone, `cloud_dispatch.py --self-test` run, and the file
 restored byte for byte. The drive refuses a dirty file and aborts on a
 pattern that is not found exactly once. Metric, one line per mutant:
@@ -49,6 +50,8 @@ def repo_root(start):
 
 ROOT = repo_root(__file__)
 REL = "tools/audit/seat/cloud_dispatch.py"
+#: The file a 4-tuple mutant names instead: roster_lib owns the brief's generated lines.
+ROSTER_REL = "tools/audit/seat/roster_lib.py"
 sys.path.insert(0, str(Path(__file__).resolve().parent))
 import mutant_guard  # noqa: E402 -- restores the mutated file on a kill (SIGTERM/SIGINT) and refuses a leftover mutant
 F = ROOT / REL
@@ -56,9 +59,10 @@ F = ROOT / REL
 MUTANTS = [
     ("M0", None, None),
     ("tree-skip", "    if tip and _git(repo_dir, \"rev-parse\"", "    if False and _git(repo_dir, \"rev-parse\""),
-    ("brief-drop", 'brief=group_brief(group))', 'brief="")'),
+    ("brief-drop", 'brief=group_brief(group, roster, fixer=role == "fixer") +', 'brief="" +'),
     ("parent-drop", '*(["-p", tip] if tip else [])', "*[]"),
     ("nonce-altered", "**args, nonce=nonce)\n    except Refusal:", "**args, nonce=nonce + \"0\")\n    except Refusal:"),
+    ("part-collision-off", "if other is not group and topic in (", "if False and topic in ("),
     ("topic-to-id", 'ref = dispatch_ref(role, topic, "")', 'ref = dispatch_ref(role, group_id, "")'),
     ("render-host-off", "    m = HOME.search(json.dumps(payload))", "    m = None"),
     ("privacy-off", "    if why:\n        raise Refusal(f\"the dispatch ref", "    if False:\n        raise Refusal(f\"the dispatch ref"),
@@ -77,10 +81,10 @@ MUTANTS = [
     ("fetch-skipped", '        _git(repo_dir, "fetch", "-q", "origin", f"refs/heads/{ref}")', "        pass"),
     ("cli-role-fixed", "print(dispatch_group(args.role,", 'print(dispatch_group("fixer",'),
     ("cli-pr-dropped", 'head=args.head or "", pr=args.pr,', 'head=args.head or "", pr="",'),
-    ("cli-nonce-dropped", "nonce=args.nonce, overlay=args.overlay))", 'nonce="", overlay=args.overlay))'),
+    ("cli-nonce-dropped", "nonce=args.nonce, overlay=args.overlay,", 'nonce="", overlay=args.overlay,'),
     ("cli-group-fixed", "print(dispatch_group(args.role, args.group,", 'print(dispatch_group(args.role, "R10-X",'),
-    ("cli-model-fixed", "args.group, args.model, roster_ref", 'args.group, "m-1", roster_ref'),
-    ("cli-overlay-dropped", "nonce=args.nonce, overlay=args.overlay))", "nonce=args.nonce, overlay=None))"),
+    ("cli-model-fixed", 'args.group, args.model or "", roster_ref', 'args.group, "m-1", roster_ref'),
+    ("cli-overlay-dropped", "nonce=args.nonce, overlay=args.overlay,", "nonce=args.nonce, overlay=None,"),
     ("group-refusal-off", "if why and getattr(args, dest)", "if False and getattr(args, dest)"),
     ("env-id-forwarded-as-none", '"env_id": "the environment id', '"env_id": None and "the environment id'),
     ("flag-unlisted", '    ap.add_argument("--out")\n', '    ap.add_argument("--out")\n    ap.add_argument("--extra")\n'),
@@ -97,6 +101,47 @@ MUTANTS = [
     ("claude-md-reread", "roles/fixer.md from main, and follow it exactly",
      "roles/fixer.md and CLAUDE.md from main, and follow them exactly"),
     ("cli-pr-truncated", 'head=args.head or "", pr=args.pr,', "head=args.head or \"\", pr=(args.pr or '')[:1],"),
+    # R10-REVIEW-DISPATCH-RESIDUE part 3 (topic r10-review-dispatch-residue-p3): Carry 13, the
+    # five-carry refusal and --part (triage P551); Carry 8, every reviewer stop path pushes a
+    # verdict (P437 C2); Carry 9, the frugal line; and the pins of Carries 2 and 3 already built.
+    ("part-count", "PART_CARRIES = 5\n", "PART_CARRIES = 6\n"),
+    ("part-refusal-off", '        if len(pending) <= PART_CARRIES:\n            return ""',
+     '        if True:\n            return ""'),
+    ("part-prefilter", 'len(group.get("carry") or []) > PART_CARRIES):', 'len(group.get("carry") or []) > 99):'),
+    ("part-fold-off", "    if len(parts) > 1 and len(parts[-1]) <= PART_FOLD:", "    if False:"),
+    ("part-fold-one", "len(parts[-1]) <= PART_FOLD:", "len(parts[-1]) < PART_FOLD:"),
+    ("part-pending-raw", "roster_lib.pending_carries(group, legacy)", 'list(range(len(group.get("carry") or [])))'),
+    ("part-topic-dropped", '            topic = f"{topic}-p{part}"\n', "            pass\n"),
+    ("part-coll-topic-off", "topic in (_topic_of(other), roster_lib.norm_group(", 'topic in ("", roster_lib.norm_group('),
+    ("part-coll-id-off", ', roster_lib.norm_group(str(other.get("group")))):', ', ""):'),
+    ("part-coll-self-off", "if other is not group and topic in (", "if topic in ("),
+    ("part-split-one", "    if len(parts) > 1 and len(parts[-1]) <= PART_FOLD:", "    if len(parts) >= 1 and len(parts[-1]) <= PART_FOLD:"),
+    ("part-runs-skip", "for j in range(1, len(idx) + 1):", "for j in range(2, len(idx) + 1):"),
+    ("part-cli-nogroup-open", '        if args.part:\n            raise Refusal("--part applies', '        if False:\n            raise Refusal("--part applies'),
+    ("part-line-dropped", '(f"\\n{pline}\\n" if pline else "")', '""'),
+    ("part-cli-dropped", "record_pr=args.record_pr, part=args.part))", "record_pr=args.record_pr, part=0))"),
+    ("part-role-open", 'if part and role != "fixer":', "if False:"),
+    ("part-range-off", "if not 1 <= part <= len(parts):", "if part < 1:"),
+    ("part-small-open", '    if len(pending) <= PART_CARRIES:\n        raise Refusal(f"--part',
+     '    if False:\n        raise Refusal(f"--part'),
+    ("wait-bound-dropped", '"about 30 minutes of polling, stop waiting: put', '"a while, stop waiting: put'),
+    ("ci-wait-dropped", 'blocked {head} ci-wait: <the last "', 'blocked {head} <the last "'),
+    ("required-red-dropped", "`prelude`. A review_packet `required-red` signal does not stop you while classify prints ",
+     "`prelude`. "),
+    ("seat-refused-dropped", "pushes `Fix review: blocked {head} seat-refused: ", "pushes `Fix review: blocked {head} "),
+    ("poll-end-dropped", 'never end your turn while "\n', 'end your turn while "\n'),
+    ("readback-dropped", "`git ls-remote origin refs/heads/probe/{ref_key}-{nonce.strip()[:8]}`", "`git ls-remote origin`"),
+    ("frugal-allowance-back", '\n               "frugal routing guard requires: when it refuses inline work',
+     '\n               "frugal routing guard requires; at most 5 inline search operations per prompt; when it refuses inline work'),
+    ("model-roster-ignored",
+     'for field, val in ((f"model.{key}", table.get(key)), (f"{key}Model", group.get(f"{key}Model"))):',
+     'for field, val in (("default", "opus"),):'),
+    ("record-pr-opus", 'return LIGHT_REVIEW_MODEL, "carry-only review" if carry_only else "record-PR review"',
+     'return (LIGHT_REVIEW_MODEL if carry_only else "opus"), "carry-only review" if carry_only else "record-PR review"'),
+    ("done-filter-dropped", 'if n != group_id and (g.get("resume") or {}).get("stage") not in CARRY_CLOSED',
+     "if n != group_id", ROSTER_REL),
+    ("enum-line-dropped", '    if enum:\n        out.append(f"Class-enumeration', '    if False:\n        out.append(f"Class-enumeration',
+     ROSTER_REL),
 ]
 SUMMARY = re.compile(r"cloud_dispatch self-test: (\d+) checks, (\d+) failed")
 
@@ -108,19 +153,21 @@ def run() -> tuple[int, list[str]]:
 
 
 def main(names: list[str]) -> int:
-    mutant_guard.arm([REL])
-    orig = F.read_text()
+    mutant_guard.arm([REL, ROSTER_REL])
+    origs = {rel: (ROOT / rel).read_text() for rel in (REL, ROSTER_REL)}
     survived = 0
     picked = [m for m in MUTANTS if not names or m[0] in names]
     try:
-        for name, old, new in picked:
+        for name, old, new, *where in picked:
+            target = ROOT / (where[0] if where else REL)
+            orig = origs[where[0] if where else REL]
             if old is not None:
                 if orig.count(old) != 1:
                     print(f"abort: {name}'s pattern occurs {orig.count(old)} times")
                     return 2
-                F.write_text(orig.replace(old, new))
+                target.write_text(orig.replace(old, new))
             failed, fails = run()
-            F.write_text(orig)
+            target.write_text(orig)
             if name == "M0":
                 verdict = "null-ok" if failed == 0 else "NULL-FAILED"
             else:
@@ -130,10 +177,10 @@ def main(names: list[str]) -> int:
             for ln in fails:
                 print(f"    {ln}")
     finally:
-        F.write_text(orig)
+        for rel, text in origs.items():
+            (ROOT / rel).write_text(text)
     print(f"RESULT mutants={sum(1 for m in picked if m[1] is not None)} survived={survived}")
     return 1 if survived else 0
 
-
 if __name__ == "__main__":
     sys.exit(main(sys.argv[1:]))
diff --git a/dev/programme/delivery/3450.md b/dev/programme/delivery/3450.md
new file mode 100644
index 000000000..d2d39ac2a
--- /dev/null
+++ b/dev/programme/delivery/3450.md
@@ -0,0 +1 @@
+- [#3450](https://github.com/tvofi/heatpump_optimizer/pull/3450) — **open**, R10-REVIEW-DISPATCH-RESIDUE (part 3): r10 review dispatch residue p3 (R10-REVIEW-DISPATCH-RESIDUE)
diff --git a/tools/audit/seat/cloud_dispatch.py b/tools/audit/seat/cloud_dispatch.py
index c62cfa173..b0b1a832f 100644
--- a/tools/audit/seat/cloud_dispatch.py
+++ b/tools/audit/seat/cloud_dispatch.py
@@ -134,11 +134,13 @@ SETUP_CHECK = "bash tools/audit/seat/cloud-setup.sh --check"
 WAIT_LINE = "Never wait in one tool call longer than 240 s; poll again instead."
 
 
-#: The owner's frugal-routing directive (tvofi 2026-11-06, triage s6-batch127 P398),
-#: stated to every role in one line, verbatim.
+#: The owner's frugal-routing directive (tvofi 2026-11-06, triage s6-batch127 P398), stated
+#: to every role in one line, verbatim; a guard refusal is answered by a cheaper sub-seat,
+#: never an inline allowance or a bypass (tvofi 2026-11-09, R10-FLY-CLOUD-FRUGAL-OFF dropped).
 FRUGAL_LINE = ("Discovery reads (search, list, read across files) go through Agent subagents, as the "
-               "frugal routing guard requires; at most 5 inline search operations per prompt; never "
-               "set FRUGAL_ALLOW_INLINE.")
+               "frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet "
+               "Agent subagent to do it rather than bypassing the guard; never set "
+               "FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.")
 
 #: Who owes a red an answer (owner rulings tvofi 2026-11-07, 2026-11-09: no merge is
 #: blocked on a non-required red), stated to the two seats that meet check runs, in one
@@ -264,10 +266,13 @@ def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, br
                    "or 4 (APPROVAL-OWED: the only red is the budget raise's approval, which follows your verdict; "
                    "judge the head as GREEN and quote the line); 3 is WAIT, so run it again. Never wait with `pgrep` or `pkill`, whose `-f` pattern matches "
                    "the waiter's own command line, nor on a context the ruleset does not require, such as "
-                   "`prelude`. If your review is otherwise complete and classify still prints WAIT after "
+                   "`prelude`. A review_packet `required-red` signal does not stop you while classify prints "
+                   "WAIT: classify decides. If your review is otherwise complete and classify still prints WAIT after "
                    "about 30 minutes of polling, stop waiting: put the line `pending-ci: <the context names it "
                    "printed>` straight after the `bus-nonce:` line and return the verdict as below; the relay "
-                   "posts it once CI is green at this head, refuses it over a red, and refuses it if the head moves.\n")
+                   "posts it once CI is green at this head, refuses it over a red, and refuses it if the head moves. "
+                   f"If the review is not complete then, push `Fix review: blocked {head} ci-wait: <the last "
+                   "classify line>` as below.\n")
         body = (
             "Role: read dev/governance/roles/fix-review.md and its rules from main, and follow them "
             f"exactly. Fetch the {'handoff' if at_handoff else 'PR'} head with `git fetch origin {head}`; " + where +
@@ -306,7 +311,13 @@ def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, br
             f"sh -c 'git add -A -f . && git write-tree') && C=$(GIT_DIR=$G git -c user.name={SEAT_NAME} "
             f"-c user.email={SEAT_EMAIL} commit-tree $T -m \"verdict {subj_key} {head}\") && "
             f"git -C $R push -q origin $C:refs/heads/probe/{ref_key}-{nonce.strip()[:8]}`. "
-            "That ref is the return signal. Do not post comments, approve or merge.")
+            "That ref is the return signal. Do not post comments, approve or merge.\n"
+            # CARRY 8 (P437 C2): 13 of 160 reviewer dispatches ended with no probe ref (11-07, 11-08).
+            "Every way your turn ends pushes a verdict to that ref: a setup or hook refusal that stops you "
+            f"pushes `Fix review: blocked {head} seat-refused: <the refusing line>`; never end your turn while "
+            "a background poll runs. After the push, read the ref back with "
+            f"`git ls-remote origin refs/heads/probe/{ref_key}-{nonce.strip()[:8]}`, and push again if it does "
+            "not print your commit.")
     elif role == "fixer":
         body = (
             "Role: read dev/governance/roles/fixer.md from main, and follow it exactly, "
@@ -501,6 +512,48 @@ def group_brief(group: dict, roster: dict | None = None, *, fixer: bool = False)
     return "\n\n".join(p for p in parts if p) + "\n"
 
 
+#: fixer.md's "at most five findings", applied to a group's pending carries (triage P551).
+PART_CARRIES = 5
+#: The remainder a split folds into its last part rather than dispatching alone (P551: "one or two").
+PART_FOLD = 2
+
+
+def part_split(pending: list[int]) -> str:
+    """The serial parts of `pending` (roster carry indices, in order): fives, a remainder of
+    PART_FOLD or fewer folded into the last; each part's indices as runs (`0-4`, `0-1+3`),
+    parts comma-separated."""
+    parts = [pending[i:i + PART_CARRIES] for i in range(0, len(pending), PART_CARRIES)]
+    if len(parts) > 1 and len(parts[-1]) <= PART_FOLD:
+        parts[-2:] = [parts[-2] + parts[-1]]
+    def runs(idx):
+        out, start = [], 0
+        for j in range(1, len(idx) + 1):
+            if j == len(idx) or idx[j] != idx[j - 1] + 1:
+                out.append(str(idx[start]) if start == j - 1 else f"{idx[start]}-{idx[j - 1]}")
+                start = j
+        return "+".join(out)
+    return ", ".join(runs(p) for p in parts)
+
+
+def part_line(group_id: str, pending: list[int], part: int) -> str:
+    """The generated brief line for `--part <part>`, or "" for a group of five or fewer pending
+    carries dispatched with none. Over five with no part refuses with the split: a silent part 1
+    would re-dispatch part 1's carries at its own handoff, since they stay pending until its merge."""
+    split = part_split(pending)
+    if not part:
+        if len(pending) <= PART_CARRIES:
+            return ""
+        raise Refusal(f"{group_id} holds {len(pending)} pending carries, over the fixer's five (fixer.md): "
+                      f"dispatch serial parts, each at the previous part's handoff, with --part <k>: {split}")
+    if len(pending) <= PART_CARRIES:
+        raise Refusal(f"--part {part}: {group_id} holds five or fewer pending carries ({len(pending)}), no split")
+    parts = split.split(", ")
+    if not 1 <= part <= len(parts):
+        raise Refusal(f"--part {part}: {group_id} splits into {len(parts)} parts: {split}")
+    return (f"Part {part} of {len(parts)}: build carries {parts[part - 1]}; the others are later parts "
+            "dispatched at this part's handoff; answer none of them")
+
+
 def dispatch_ref(role: str, topic: str, pr: str) -> str:
     """`dispatch/<role>-<topic>`, or `dispatch/<role>-rev-<PR>` for a seat with no topic."""
     key = topic or (f"rev-{pr}" if pr.isdigit() else "")
@@ -544,7 +597,8 @@ def design_approved(repo_dir: str, group_id: str) -> bool:
 def dispatch_group(role: str, group_id: str, model: str, *, repo_dir: str = ".",
                    roster_ref: str | None = None, head: str = "", pr: str = "", nonce: str = "",
                    overlay: str | None = None, environ=None, design_exempt: str = "",
-                   carry_only: bool = False, record_pr: bool = False, reviewed_head: str = "") -> str:
+                   carry_only: bool = False, record_pr: bool = False, reviewed_head: str = "",
+                   part: int = 0) -> str:
     """Render the seat for `group_id` from the roster, publish it, return its ref name.
 
     The roster at `roster_ref` of `repo_dir` (default: the round's roster
@@ -575,6 +629,20 @@ def dispatch_group(role: str, group_id: str, model: str, *, repo_dir: str = ".",
     environ = os.environ if environ is None else environ
     known = _config(argparse.Namespace(overlay=overlay, env_id=None, model=model, repo=None), environ)
     topic = group_id if role in DESIGN_ROLES else _topic_of(group)
+    pline = ""
+    if part and role != "fixer":
+        raise Refusal(f"--part is the fixer's: a {role} seat is not split")
+    if role == "fixer" and (part or len(group.get("carry") or []) > PART_CARRIES):
+        try:
+            legacy = roster_lib.read_legacy(repo_dir, roster_lib.roster_path(repo_dir, roster_ref, None))
+        except roster_lib.RosterNotFound as e:
+            raise Refusal(str(e))
+        pline = part_line(group_id, roster_lib.pending_carries(group, legacy), part)
+        if part > 1:
+            topic = f"{topic}-p{part}"
+            for other in roster.get("groups", []):  # a part's topic is a roster group's own: one seat ref, one wrong credit
+                if other is not group and topic in (_topic_of(other), roster_lib.norm_group(str(other.get("group")))):
+                    raise Refusal(f"--part {part}: {topic} is the topic of {other.get('group')}")
     design = ""
     if role == "fixer" and roster_lib.needs_design(group) and not design_exempt.strip():
         if not design_approved(repo_dir, group_id):
@@ -590,7 +658,8 @@ def dispatch_group(role: str, group_id: str, model: str, *, repo_dir: str = ".",
         if not design:
             raise Refusal(f"no design/{group_id} on origin to review")
     args = dict(design=design, env_id=known["env_id"], model=model, repo=roster.get("repo") or known["repo"],
-                pr=pr, topic=topic, brief=group_brief(group, roster, fixer=role == "fixer"),
+                pr=pr, topic=topic,
+                brief=group_brief(group, roster, fixer=role == "fixer") + (f"\n{pline}\n" if pline else ""),
                 reviewed_head=reviewed_head)
     head = head or _git(repo_dir, "rev-parse", f"{HEAD_REF}^{{commit}}").strip()
     if role == "reviewer":
@@ -690,7 +759,17 @@ def _group_checks(check) -> None:
         cons = {"group": "R10-CONS", "brief": "Consume.\n", "after": ["R10-PROD"], "resume": {"stage": "queued"}}
         share = {"group": "R10-SHARE", "brief": "Share.\n", "files": ["tools/a.py", "tools/b.py"], "resume": {"stage": "queued"}}
         donec = {"group": "R10-DONEC", "brief": "Done.\n", "after": ["R10-PROD"], "resume": {"stage": "done"}}
-        land([grp, bad, big, two, cbad, ruled, legacy, prod, cons, share, donec])
+        # CARRY 13 (P551): 21 pending carries and a marked one past them; five pending and a moved one.
+        many = {"group": "R10-SPLIT", "brief": "Many.\n", "resume": {"branch": "handoff/r10-split"},
+                "carry": [f"Carry text {i}." for i in range(21)] + ["Built. [implemented: abc1234]"]}
+        five = {"group": "R10-FIVE", "brief": "Five.\n", "carry": [f"Five {i}." for i in range(5)] + ["Gone. [moved: R10-X]"]}
+        # Part 2's topic is R10-CLASH-P2's id, part 3's R10-ALIAS's branch; R10-SELF-P2's part 2 is its own id.
+        clash = {"group": "R10-CLASH", "brief": "Clash.\n", "carry": [f"Clash {i}." for i in range(13)]}
+        clash2 = {"group": "R10-CLASH-P2", "brief": "Own.\n", "resume": {"branch": "handoff/other-topic"}}
+        alias = {"group": "R10-ALIAS", "brief": "Alias.\n", "resume": {"branch": "handoff/r10-clash-p3"}}
+        selfp = {"group": "R10-SELF-P2", "brief": "Self.\n", "resume": {"branch": "handoff/r10-self"},
+                 "carry": [f"Self {i}." for i in range(8)]}
+        land([grp, bad, big, two, cbad, ruled, legacy, prod, cons, share, donec, many, five, clash, clash2, alias, selfp])
         git(work, "remote", "add", "origin", str(origin))
         tip = git(work, "rev-parse", "origin/main").strip()
 
@@ -797,6 +876,69 @@ def _group_checks(check) -> None:
               and "R10-DONEC" not in ptext.split("Valid `Carry:` targets")[1])
         check("and the group's class-enumeration command",
               "disposition every seam it returns): git grep -n seam -- tools\n" in ptext)
+        # CARRY 13 (P551): over five pending carries refuses with the split; --part k renders one part.
+        saved_cut = dict(roster_lib.CARRY_CUTOVER)
+        roster_lib.CARRY_CUTOVER.clear()  # the fixture's roster has no cut-over commit to read legacy at
+
+        def why_any(*a, **kw) -> str:  # reason(), but any exception reads as a named failure, not a crash
+            try:
+                return reason(*a, **kw)
+            except Exception as e:  # noqa: BLE001 -- a mutant's IndexError must fail a check, not the run
+                return f"{e.__class__.__name__}: {e}"
+
+        def split_any(n: int) -> str:  # part_split of 0..n-1; an exception reads as a named failure, as why_any
+            try:
+                return part_split(list(range(n)))
+            except Exception as e:  # noqa: BLE001
+                return f"{e.__class__.__name__}: {e}"
+        try:
+            mwhy = reason("R10-SPLIT")
+            check("a fixer for a group with 21 pending carries (a marked 22nd not counted) refuses, printing the split",
+                  "21 pending carries" in mwhy and "--part <k>: 0-4, 5-9, 10-14, 15-20" in mwhy and "\n" not in mwhy
+                  and not git(work, "ls-remote", "origin", "refs/heads/dispatch/fixer-r10-split*").strip())
+            p2 = dispatch("R10-SPLIT", part=2)
+            p2text = fetched(p2, "PROMPT.md")
+            pline = ("Part 2 of 4: build carries 5-9; the others are later parts dispatched at this part's handoff; "
+                     "answer none of them")
+            check("--part 2 renders the topic <topic>-p2 and one generated line naming carries 5-9",
+                  p2 == "dispatch/fixer-r10-split-p2" and "topic r10-split-p2, at head" in p2text
+                  and sum(ln == pline for ln in p2text.splitlines()) == 1 and p2text.endswith(pline + "\n"))
+            cwhy = why_any("R10-CLASH", part=2)
+            awhy = why_any("R10-CLASH", part=3)
+            check("a part whose topic is another group's id (R10-CLASH-P2) or branch (R10-ALIAS) refuses naming it; "
+                  "part 1, a free part and a part that is its own group's id (R10-SELF-P2) publish",
+                  "R10-CLASH-P2" in cwhy and "\n" not in cwhy and "R10-ALIAS" in awhy and "\n" not in awhy
+                  and not git(work, "ls-remote", "origin", "refs/heads/dispatch/fixer-r10-clash-p*").strip()
+                  and not why_any("R10-CLASH", part=1) and p2 == "dispatch/fixer-r10-split-p2"
+                  and not why_any("R10-SELF-P2", part=2))
+            p1text = fetched(dispatch("R10-SPLIT", part=1), "PROMPT.md")
+            check("--part 1 keeps the group's own topic and names carries 0-4",
+                  "topic r10-split, at head" in p1text and "\nPart 1 of 4: build carries 0-4; the others" in p1text)
+            check("a part past the split, a part of a group of five or fewer, and a part for another role refuse",
+                  "splits into 4 parts" in why_any("R10-SPLIT", part=5) and "five or fewer" in why_any("R10-FIVE", part=1)
+                  and "fixer's" in why_any("R10-SPLIT", "probe", part=2))
+            fwhy = why_any("R10-FIVE")
+            ftext = "" if fwhy else fetched("dispatch/fixer-" + _topic_of(five), "PROMPT.md")
+            check("five pending carries (a moved sixth not counted) dispatch unrefused, the brief byte-identical (null control)",
+                  not fwhy and ftext.endswith("Brief (snapshotted when this payload was rendered):\n"
+                                 + group_brief(five, {"groups": [five]}, fixer=True)) and "\nPart " not in ftext)
+            check("the split folds a remainder of one or two into the last part, and only that",
+                  [split_any(n) for n in (1, 2, 5, 6, 7, 8, 21, 22, 23)]
+                  == ["0", "0-1", "0-4", "0-5", "0-6", "0-4, 5-7", "0-4, 5-9, 10-14, 15-20", "0-4, 5-9, 10-14, 15-21",
+                      "0-4, 5-9, 10-14, 15-19, 20-22"]
+                  and part_split([0, 1, 3, 4, 5, 6, 9]) == "0-1+3-6+9" and part_split([0, 2, 3]) == "0+2-3")
+            out = io.StringIO()
+            with contextlib.chdir(work), _env(env), contextlib.redirect_stdout(out), \
+                    contextlib.redirect_stderr(io.StringIO()):
+                crc = main(["--role", "fixer", "--group", "R10-SPLIT", "--part", "3", "--model", "m-1"])
+            err = io.StringIO()
+            with contextlib.chdir(work), _env(env), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
+                nrc = main(["--role", "fixer", "--part", "2", "--head", tip, "--model", "m-1"])
+            check("the CLI forwards --part to the group path, and refuses it without --group",
+                  crc == 0 and out.getvalue().strip() == "dispatch/fixer-r10-split-p3"
+                  and nrc == 2 and "--part applies only with --group" in err.getvalue())
+        finally:
+            roster_lib.CARRY_CUTOVER.update(saved_cut)
         check("a reviewer's brief carries neither generated line",
               "Valid `Carry:`" not in group_brief(prod, {"groups": [prod, cons]}, fixer=False))
         try:
@@ -1084,6 +1226,7 @@ def _flag_checks(check) -> None:
     import io
     dests = {a.dest for a in _parser()._actions if a.dest != "help"}
     switches = {a.dest for a in _parser()._actions if a.nargs == 0 and a.dest != "help"}
+    ints = {a.dest for a in _parser()._actions if a.type is int}  # `--part`: a number, forwarded as one
     check("every flag the parser accepts has a --group disposition in GROUP_FLAGS, and no other",
           dests == set(GROUP_FLAGS))
     calls: list = []
@@ -1092,7 +1235,7 @@ def _flag_checks(check) -> None:
     try:
         for dest in sorted(dests):
             base = {"role": "fixer", "group": "G-BASE", "model": "m-base"}
-            value = "probe" if dest == "role" else (True if dest in switches else f"value-of-{dest}")
+            value = "probe" if dest == "role" else (True if dest in switches else "7" if dest in ints else f"value-of-{dest}")
             argv = [x for k, v in {**base, dest: value}.items() for x in ("--" + k.replace("_", "-"), v)]
             if dest in switches:  # a switch takes no value
                 argv = argv[:-1]
@@ -1105,7 +1248,7 @@ def _flag_checks(check) -> None:
             else:
                 sent = [*calls[0][0], *calls[0][1].values()] if len(calls) == 1 else []
                 check(f"--group forwards --{dest.replace('_', '-')} to dispatch_group",
-                      rc == 0 and value in sent)
+                      rc == 0 and (int(value) if dest in ints else value) in sent)
     finally:
         globals()["dispatch_group"] = real
 
@@ -1170,7 +1313,12 @@ def self_test() -> int:
           all(WAIT_LINE in t and "240 s" in WAIT_LINE for t in prompts.values()))
     check("every role's prompt carries the frugal-routing line once, verbatim (P398)",
           all(sum(line == FRUGAL_LINE for line in t.splitlines()) == 1 for t in prompts.values())
-          and FRUGAL_LINE.startswith("Discovery reads (search, list, read across files) go through Agent subagents"))
+          and FRUGAL_LINE == ("Discovery reads (search, list, read across files) go through Agent subagents, as the "
+                              "frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet "
+                              "Agent subagent to do it rather than bypassing the guard; never set "
+                              "FRUGAL_ALLOW_INLINE and never edit .claude/settings.json."))
+    check("and no prompt grants an inline allowance the guard does not (tvofi 2026-11-09, Carry 9)",
+          not any("inline search operations" in t for t in prompts.values()))
     owed_roles = ("reviewer", "fixer")  # literal: a mutant of OWED_REDS_ROLES must not move the test too
     check("the reviewer and the fixer are told, in one line citing its rule, that only a red "
           "`merge_train.py owed-reds` prints is owed an answer or blocks (tvofi 2026-11-07, 2026-11-09)",
@@ -1193,6 +1341,22 @@ def self_test() -> int:
           and "exits 0 (GREEN), 1 (RED), 2 (unreadable: say so in the verdict)" in rv and "3 is WAIT" in rv)
     check("the reviewer is forbidden a pgrep or pkill waiter and a context the ruleset does not require",
           "Never wait with `pgrep` or `pkill`" in rv and "such as\n`prelude`" not in rv and "such as `prelude`" in rv)
+    # CARRY 8 (P437 C2): every reviewer stop path ends in a verdict pushed to its probe ref, read back.
+    hv = render("reviewer", head, **base, topic="t-1", nonce="abc123")["job_config"]["ccr"]["events"][0]["data"]["message"]["content"]
+    check("the reviewer's setup or hook refusal pushes `seat-refused`, and it reads its ref back, at the PR and at the handoff",
+          all(f"`Fix review: blocked {head} seat-refused: <the refusing line>`" in t
+              and "never end your turn while a background poll runs" in t for t in (rv, hv))
+          and "`git ls-remote origin refs/heads/probe/rev-7-abc123`" in rv
+          and "`git ls-remote origin refs/heads/probe/revt-t-1-abc123`" in hv)
+    check("a required-red packet does not stop the reviewer while classify reads WAIT: classify decides",
+          "A review_packet `required-red` signal does not stop you while classify prints WAIT: classify decides" in rv)
+    check("WAIT is bounded: past about 30 minutes an incomplete review pushes `ci-wait` with the classify line",
+          re.search(r"still prints WAIT after about 30 minutes of polling, stop waiting: .*?If the review is not "
+                    rf"complete then, push `Fix review: blocked {head} ci-wait: <the last classify line>`", rv, re.S)
+          is not None and "ci-wait" not in hv)
+    check("no other role is told any reviewer stop push (null control: the fixer prompt carries none)",
+          all("seat-refused" not in t and "ci-wait" not in t and "refs/heads/probe/" not in t
+              for r, t in prompts.items() if r != "reviewer"))
     check("no other role is told to wait on merge_train.py classify (null control)",
           all("merge_train.py classify" not in t and "pgrep" not in t for r, t in prompts.items() if r != "reviewer"))
     wip, fx = f"refs/heads/{WIP_NS}/t-1", prompts["fixer"]
@@ -1299,7 +1463,7 @@ def self_test() -> int:
 GROUP_FLAGS = {
     "role": None, "group": None, "model": None, "head": None, "roster_ref": None,
     "pr": None, "nonce": None, "overlay": None, "design_exempt": None, "reviewed_head": None,
-    "carry_only": None, "record_pr": None,
+    "carry_only": None, "record_pr": None, "part": None,
     "design": "dispatch_group reads the tip of design/<group> on origin",
     "topic": "the roster gives the topic (the group's branch)",
     "brief": "the roster gives the brief",
@@ -1331,6 +1495,8 @@ def _parser() -> argparse.ArgumentParser:
                     "and the field is printed")
     ap.add_argument("--carry-only", action="store_true", help="--group reviewer: a review_carry CARRY or delta re-review (sonnet)")
     ap.add_argument("--record-pr", action="store_true", help="--group reviewer: a record-PR review (sonnet)")
+    ap.add_argument("--part", type=int, default=0, help="--group fixer over five pending carries: the serial "
+                    "part k to dispatch (the refusal without it prints the split)")
     ap.add_argument("--repo")
     ap.add_argument("--overlay")
     ap.add_argument("--out")
@@ -1352,8 +1518,10 @@ def main(argv: list[str]) -> int:
             print(dispatch_group(args.role, args.group, args.model or "", roster_ref=args.roster_ref,
                                  head=args.head or "", pr=args.pr, design_exempt=args.design_exempt,
                                  nonce=args.nonce, overlay=args.overlay, reviewed_head=args.reviewed_head,
-                                 carry_only=args.carry_only, record_pr=args.record_pr))
+                                 carry_only=args.carry_only, record_pr=args.record_pr, part=args.part))
             return 0
+        if args.part:
+            raise Refusal("--part applies only with --group: the roster gives the carries it splits")
         if not args.head:
             raise Refusal("--head is required without --group")
         brief = ""
diff --git a/tools/audit/seat/instruments/cloud_dispatch.py.md b/tools/audit/seat/instruments/cloud_dispatch.py.md
index 8905bbe34..e4b73d020 100644
--- a/tools/audit/seat/instruments/cloud_dispatch.py.md
+++ b/tools/audit/seat/instruments/cloud_dispatch.py.md
@@ -93,3 +93,9 @@ is read from the roster (`model.<role>`, `<role>Model`) and the field is printed
 `--carry-only` and `--record-pr` run a reviewer on sonnet. A fixer's brief ends with the live
 consumer groups (the only valid `Carry:` targets) and the group's `enumeration` command,
 from `roster_lib.brief_lines`.
+A `fixer` for a group holding more than five pending carries (`roster_lib.pending_carries`)
+is refused, and the refusal prints the split: index-ordered fives, a remainder of one or two
+folded into the last part. `--part <k>` dispatches part k under topic `<topic>-p<k>` (k over 1)
+with one generated line naming its carries; dispatch each part at the previous part's handoff.
+Every reviewer stop path, a setup refusal and a bounded CI wait included, pushes a verdict to
+its probe ref and reads it back.

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
