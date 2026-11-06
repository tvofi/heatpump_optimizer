# Review packet #3253
head: 21be201ce8cc097c87d95e81e42d036786a539dc
base: b36679ceaa65a08a67a84f0d934c93aa15f7c7f3

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=127927383107 success
arch-score / arch-score id=127927308656 success
arm id=127927107522 skipped
budget-raise-gate / budget-raise-gate id=127927308665 success
cancel-superseded id=127927059161 success
codeql id=127927310713 skipped
codeql / Analyze (actions) id=127927294816 success
codeql / Analyze (javascript-typescript) id=127927294826 success
codeql / Analyze (python) id=127927294896 success
gate id=127928051522 failure
governance id=127927311284 skipped
governance / delivery-status id=127927295142 success
governance / delivery-status-publish id=127927298153 skipped
governance / env-matrix id=127927295182 in_progress
governance / instrument-self-tests id=127927294958 in_progress
governance / policy-docs id=127927294981 success
governance / record id=127927297716 skipped
governance / wave-script id=127927295121 success
hassfest id=127927310927 skipped
hassfest / hassfest id=127927294806 success
kernel-points id=127927310498 skipped
pr-contract id=127928053549 skipped
prelude id=127927059625 success
refresh id=127927059759 success
tests id=127927311066 skipped
tests / arch-instrument id=127927544041 success
tests / briefs id=127927294893 success
tests / browser id=127927544124 in_progress
tests / closure-scope id=127927294945 success
tests / closures id=127927543951 in_progress
tests / coverage id=127927543965 in_progress
tests / fast (3.14) id=127927544151 in_progress
tests / mutation id=127927295022 success
tests / mutation-autofix id=127927771793 skipped
tests / mutation-pins id=127927771241 skipped
tests / nightly-ha id=127927546881 skipped
tests / nightly-status id=127927295052 success
tests / replay id=127927546061 skipped
tests / typing id=127927543969 success
validate id=127927310402 skipped
validate / validate-hacs id=127927294720 success

## Refusals
red-unanswered: concluded red check `gate` is not named in ## Red checks
required-red: required context `gate` concluded failure at 21be201ce8cc097c87d95e81e42d036786a539dc

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/audit/seat/roster_edit.py --self-test
             `tools/audit/seat/roster_edit.py` is in the tree at this head
  ok         python3 tools/audit/seat/roster_queue.py --self-test
             `tools/audit/seat/roster_queue.py` is in the tree at this head
  ok         python3 tools/audit/seat/roster_lib.py --self-test
             `tools/audit/seat/roster_lib.py` is in the tree at this head
  ok         python3 tools/audit/seat/r10_roster_ops_mutants.py --self-test
             `tools/audit/seat/r10_roster_ops_mutants.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         bash tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  ok         python3 tests/closure.py select
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head

FIGURES: 8 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3253.md b/dev/programme/delivery/3253.md
new file mode 100644
index 000000000..c07763c6b
--- /dev/null
+++ b/dev/programme/delivery/3253.md
@@ -0,0 +1 @@
+- [#3253](https://github.com/tvofi/heatpump_optimizer/pull/3253) — **open**, R10-ROSTER-WRITE-SWEEP: the roster write path's residue in roster_edit.py and roster_queue.py (R10-ROSTER-WRITE-SWEEP)
diff --git a/tools/audit/seat/r10_roster_ops_mutants.py b/tools/audit/seat/r10_roster_ops_mutants.py
index bb277a710..c9d74537f 100644
--- a/tools/audit/seat/r10_roster_ops_mutants.py
+++ b/tools/audit/seat/r10_roster_ops_mutants.py
@@ -57,6 +57,23 @@ Plants, one per refusal of the two ops and per round-trip property:
          though its group would orphan an open issue (H1), and the
          set-resume --field stage door left unheld (H2).
 
+    W1-W15 the write-sweep arms (R10-ROSTER-WRITE-SWEEP): the lettered
+           proposal label unmatched (W1), append-group's `@` strip dropped
+           (W2), the overlap test skipping the not-started stage (W3), the
+           --reason escape always open (W4), the index exemption dropped (W5),
+           append-carry's closing refusal (W6), the open-PR WARN (W7) and the
+           absorbed_into naming (W8) lost, set-resume's pr field (W9), a stale
+           note kept (W10), the privacy gate not called (W11), absorbed --into
+           naming no live group (W12, W13) or needing none (W14), and a phase
+           branch unresolved in roster_lib.group_for_branch (W15).
+
+    Q1-Q7  roster_queue.py's own self-test: the plain shlex.split line grammar
+           (a trailing comment reaches the editor, Q1), the run-start snapshot
+           written over a line appended since (Q2), a flag folded into the
+           value (Q3), a held line released with its batch file absent (Q4),
+           marking the wrong line (Q5), `all` run without --mark (Q6) and no
+           lint-clone self-heal in `loop` (Q7).
+
     python3 tools/audit/seat/r10_roster_ops_mutants.py [plant ...]
     python3 tools/audit/seat/r10_roster_ops_mutants.py --null
     python3 tools/audit/seat/r10_roster_ops_mutants.py --self-test
@@ -77,6 +94,7 @@ from pathlib import Path
 ROOT = Path(__file__).resolve().parents[3]
 TARGET = "tools/audit/seat/roster_edit.py"
 DROP = '    del g["carry"][_carry_index(g, index, match, "drop-carry")]\n'
+RQ = "tools/audit/seat/roster_queue.py"
 LIB, SYNC, AUDIT = ("tools/audit/seat/roster_lib.py",
                     "tools/audit/seat/roster_sync.py", "tools/audit/carry_audit.py")
 _MARK_LINE = next((ln for ln in (ROOT / LIB).read_text().splitlines()
@@ -134,8 +152,8 @@ PLANTS = {
            "    if True:  # S5\n        return None\n"),
     "S6": ("    if size is None or size in sizes:\n        return None\n",
            "    if True:  # S6\n        return None\n"),
-    "S7": ("        op_append_group(roster, value, rel, sizes)\n",
-           "        op_append_group(roster, value)  # S7\n"),
+    "S7": ("        op_append_group(roster, value, rel, sizes, reason)\n",
+           "        op_append_group(roster, value, reason=reason)  # S7\n"),
     "K1": ('    if roster_lib.carry_mark(g["carry"][i]):\n', "    if False:  # K1\n"),
     "K2": ("    if kind not in roster_lib.CARRY_MARKS:\n", "    if False:  # K2\n"),
     "K3": ('    if kind == "implemented" and not SHA_RE.match(arg):\n',
@@ -145,15 +163,15 @@ PLANTS = {
     "K6": ('    if kind == "dismissed" and not arg:\n', "    if False:  # K6\n"),
     "K7": ('["stage"] = _closing(g, stage, legacy, "set-stage")\n',
            '["stage"] = stage  # K7\n'),
-    "K8": ("                    legacy = roster_lib.read_legacy(a.worktree, rel)\n",
-           "                    legacy = {}  # K8\n"),
+    "K8": ("                legacy = roster_lib.read_legacy(a.worktree, rel)\n",
+           "                legacy = {}  # K8\n"),
     "K9": ('        value = _closing(g, value, legacy, "set-resume")\n',
            "        pass  # K9\n"),
     "K10": ("        if stage in roster_lib.CARRY_CLOSED:\n",
             "        if False:  # K10\n"),
     "K11": ('    if "]" in arg:\n', "    if False:  # K11\n"),
     "K12": ('raise Refuse(f"the carry cut-over is unreadable, so no "\n'
-            '                                 f"stage is written: {e}")',
+            '                             f"stage is written: {e}")',
             "legacy = {}  # K12"),
     "L1": (LIB, "            if carry_mark(c) is None and c not in held]\n",
            "            if c not in held]  # L1\n"),
@@ -193,8 +211,8 @@ PLANTS = {
            '        elif isinstance(x, dict) and isinstance(x.get("number"), int):  # R5\n'),
     "H1": ("    if held:\n        g[\"resume\"][\"stage\"] = HOLD_STAGE\n",
            "    if False:  # H1\n        g[\"resume\"][\"stage\"] = HOLD_STAGE\n"),
-    "H2": ('            if a.op == "set-stage" or (a.op == "set-resume" and a.field == "stage"):\n',
-           '            if a.op == "set-stage":  # H2\n'),
+    "H2": ('        if a.op == "set-stage" or (a.op == "set-resume" and a.field == "stage"):\n',
+           '        if a.op == "set-stage":  # H2\n'),
 }
 
 
@@ -240,6 +258,35 @@ PLANTS.update({
     "R11": ('                    and _git_ok(checkout, "merge-base", "--is-ancestor",\n'
             '                                sha, cand):\n',
             '                    and True:  # R11\n'),
+    "W1": ('LABEL = r"P(?:\\d+|-[A-Q])\\b"', 'LABEL = r"P\\d+\\b"'),
+    "W2": ('    if json_file.startswith("@"):\n        json_file = json_file[1:]\n', ""),
+    "W3": ('        if (g.get("resume") or {}).get("stage") != "not-started":\n            continue\n', ""),
+    "W4": ('    if clash and not (reason or "").strip():\n', "    if clash and reason is None:\n"),
+    "W5": ('if not _is_index(f)}', "}"),
+    "W6": ("    if stage in roster_lib.CARRY_CLOSED:\n        into = resume.get",
+           "    if False:\n        into = resume.get"),
+    "W7": ('    if resume.get("pr"):\n        print(f"WARN', '    if False:\n        print(f"WARN'),
+    "W8": ('if stage == "absorbed" and into else', "if False else"),
+    "W9": ('"note", "pr")', '"note")'),
+    "W10": ("            and OWED_NOTE_RE.search(note):\n", "            and not OWED_NOTE_RE.search(note):\n"),
+    "W11": ('        why = privacy_refusal(added_texts(before, roster) + added_resume(before, roster))\n'
+            '        if why:\n            raise Refuse(f"privacy gate: {why}; nothing written")\n', ""),
+    "W12": ('    if hstage in roster_lib.CARRY_CLOSED:\n', "    if False:\n"),
+    "W13": ('    if into == group:\n        raise Refuse(f"set-stage: {group} cannot be absorbed',
+            '    if False:\n        raise Refuse(f"set-stage: {group} cannot be absorbed'),
+    "W14": ('    if not into:\n        raise Refuse(f"set-stage: {group} absorbed needs',
+            '    if False:\n        raise Refuse(f"set-stage: {group} absorbed needs'),
+    "W15": (LIB, "    if phase != tail:  # handoff", "    if False:  # handoff"),
+    "Q1": (RQ, "    t = _split(ln)\n", "    t = shlex.split(ln)\n"),
+    "Q2": (RQ, '            mark_line(a.queue, ln, "done" if ok else "refused")\n',
+           '            Path(a.queue).write_text("\\n".join((("#done " if ok else "#refused ") + x) if x == ln else x for x in qlines))\n'),
+    "Q3": (RQ, 'return t[0], t[1], (rest[0] if rest else ""), rest[1:]',
+           'return t[0], t[1], " ".join(rest), []'),
+    "Q4": (RQ, "        if files and all(_git(", "        if True or all(_git("),
+    "Q5": (RQ, "        if x == old:\n", "        if x.strip() == old.strip() or True:\n"),
+    "Q6": (RQ, "    if allq and not mark:\n", "    if False:\n"),
+    "Q7": (RQ, "    if Path(a.lint_clone).is_dir():\n        return False\n",
+           "    if True:\n        return False\n"),
 })
 
 
diff --git a/tools/audit/seat/roster_edit.py b/tools/audit/seat/roster_edit.py
index babb86301..86bd9fdfb 100644
--- a/tools/audit/seat/roster_edit.py
+++ b/tools/audit/seat/roster_edit.py
@@ -4,10 +4,11 @@
     python3 tools/audit/seat/roster_edit.py set-stage   <group> <stage> [--at-sha SHA]
     python3 tools/audit/seat/roster_edit.py wire-issue  <group> <issue#> [--field fixes|issues]
     python3 tools/audit/seat/roster_edit.py unwire-issue <group> <issue#> [--field fixes|issues]
-    python3 tools/audit/seat/roster_edit.py append-group <json-file>
+    python3 tools/audit/seat/roster_edit.py append-group <GROUP> <json-file | @json-file> [--reason TEXT]
     python3 tools/audit/seat/roster_edit.py edit-brief  <group> <text | @file>
     python3 tools/audit/seat/roster_edit.py append-carry <group> <text | @file>
-    python3 tools/audit/seat/roster_edit.py set-resume  <group> --field <stage|commit|branch|last_step|next_step|note> <text | @file>
+    python3 tools/audit/seat/roster_edit.py set-resume  <group> --field <stage|commit|branch|last_step|next_step|note|pr> <text | @file>
+    python3 tools/audit/seat/roster_edit.py set-stage   <group> absorbed --into <host-group>
     python3 tools/audit/seat/roster_edit.py set-after   <group> <G1,G2,... | ->
     python3 tools/audit/seat/roster_edit.py drop-carry  <group> <index | --match TEXT>
     python3 tools/audit/seat/roster_edit.py mark-carry  <group> <index | --match TEXT>
@@ -85,9 +86,19 @@ Ops (all group ids must exist, except append-group which must not):
   unwire-issue removes an integer from `issues` (default) or, with
                `--field fixes`, from `fixes`; refuses when it is not there;
   append-group inserts a validated new group (group/lane/after/brief needed,
-               `after` naming known groups, resume defaulted);
+               `after` naming known groups, resume defaulted). The argument
+               is `<GROUP> <json-file>`; a leading `@` on the file is
+               stripped, as append-carry and edit-brief read `@file` too.
+               A new group whose `files` share a file, other than an index
+               file (INDEX_FILES), with a `not-started` group is refused,
+               naming each group and file, unless `--reason TEXT` is given;
+               the reason is recorded in the new group's resume.note;
   edit-brief   replaces the brief (an @file argument reads the file);
-  append-carry appends to the group's carry list, refusing an exact repeat;
+  append-carry appends to the group's carry list, refusing an exact repeat
+               and a destination that is closing (a DONE_STAGES stage, or
+               `absorbed`, naming `absorbed_into` where it has one); a
+               destination with `resume.pr` set takes the carry and prints
+               `WARN carry to <G>: PR #<n> is open on it`. No gh call;
   set-resume   sets one resume field -- the free-text state a session
                restarts from. stage and branch are non-null: an empty value
                is refused. commit demands a sha. An empty value for commit,
@@ -95,6 +106,11 @@ Ops (all group ids must exist, except append-group which must not):
   set-after    replaces the group's after-edges whole (`-` for none),
                refusing an unknown group, a self-edge, a repeated edge and
                a cycle in the resulting after-graph;
+THE PRIVACY GATE. Every text an op adds (the same added_texts the triage gate
+judges, plus a set-resume value) is run through ref_privacy.leaks, so a carry
+naming a host path is refused at the op with a scrub hint, not at the
+landing of the roster on main.
+
 THE TRIAGE GATE (decision 0015). Every process, tooling or instrument proposal
 passes dev/governance/roles/proposal-triage.md before it reaches the roster, so
 the write path refuses roster text a proposal sourced that cites no ACCEPT
@@ -139,6 +155,7 @@ from __future__ import annotations
 
 import argparse
 import contextlib
+import copy
 import io
 import json
 import os
@@ -165,8 +182,13 @@ BRIEF_LINT_OLD = ".claude/workflows/brief_lint.mjs"
 BRIEF_LINT_NEW = "tools/policy/brief_lint.mjs"
 
 
-PROPOSAL_RE = re.compile(r"\b(?:triage|proposal)\s+P\d+\b", re.I)
-RULING_CITE_RE = re.compile(r"\btriage:\s*(dev/programme/triage/[A-Za-z0-9_.-]+\.md)#(P\d+)\b")
+#: A proposal label is `P<digits>` or, from session s4, `P-<A..Q>` (carry 0,
+#: #2670): the citation grammar below names both, or a lettered label could be
+#: neither refused uncited nor cited.
+LABEL = r"P(?:\d+|-[A-Q])\b"
+PROPOSAL_RE = re.compile(rf"\b(?:triage|proposal)\s+{LABEL}", re.I)
+RULING_CITE_RE = re.compile(
+    rf"\btriage:\s*(dev/programme/triage/[A-Za-z0-9_.-]+\.md)#({LABEL})")
 VERDICT_LINE_RE = re.compile(r"^Verdict:\s*(ACCEPT|REJECT|DEFER)\b", re.M)
 
 
@@ -188,8 +210,12 @@ def run(cmd, cwd=None):
 
 
 # ----------------------------------------------------------------- ops
-def op_set_stage(roster, group, stage, at_sha, rel="", legacy=None):
+def op_set_stage(roster, group, stage, at_sha, rel="", legacy=None, into=None):
     g = _need(roster, group)
+    if into is not None and stage != "absorbed":
+        raise Refuse("set-stage: --into is for stage absorbed")
+    if stage == "absorbed":
+        _absorb_into(roster, group, into)
     if not isinstance(stage, str) or not stage.strip():
         raise Refuse("stage must be a non-empty string")
     why = _stage_why(stage, rel, group)
@@ -198,18 +224,41 @@ def op_set_stage(roster, group, stage, at_sha, rel="", legacy=None):
     if at_sha and not SHA_RE.match(at_sha):
         raise Refuse(f"--at-sha is not a sha: {at_sha!r}")
     g.setdefault("resume", {})["stage"] = _closing(g, stage, legacy, "set-stage")
+    if stage == "absorbed":
+        g["resume"]["absorbed_into"] = into
+    elif "absorbed_into" in g["resume"]:
+        del g["resume"]["absorbed_into"]  # no longer folded: no stale host
+    _drop_stale_note(g, g["resume"]["stage"])
     if at_sha:
         g["resume"]["commit"] = at_sha
 
 
+def _absorb_into(roster, group, into):
+    """`set-stage G absorbed --into H`: H must be a live group other than G
+    (carry 16), so carry_audit can name where G's carries went."""
+    if not into:
+        raise Refuse(f"set-stage: {group} absorbed needs --into <host group>")
+    host = next((x for x in roster.get("groups", []) if x.get("group") == into),
+                None)
+    if host is None:
+        raise Refuse(f"set-stage: --into {into!r} names no group")
+    if into == group:
+        raise Refuse(f"set-stage: {group} cannot be absorbed into itself")
+    hstage = (host.get("resume") or {}).get("stage")
+    if hstage in roster_lib.CARRY_CLOSED:
+        raise Refuse(f"set-stage: --into {into} is {hstage}, not a live group")
+
+
 #: The resume fields set-resume may write. stage and branch are the roster's
 #: structural non-null fields (gen.py defaults them); commit and the
 #: free-text fields are str-or-null across the live roster, so an empty
 #: value clears them to null.
 RESUME_FIELDS = ("stage", "commit", "branch", "last_step", "next_step",
-                 "note")
+                 "note", "pr")
 NON_NULL_RESUME_FIELDS = ("stage", "branch")
 TEXT_RESUME_FIELDS = ("last_step", "next_step", "note")
+#: A note naming owed work is stale once the group closes (carry 2, #2559).
+OWED_NOTE_RE = re.compile(r"\bOwed\b|has no pull request", re.I)
 
 
 def op_set_resume(roster, group, field, value, rel="", legacy=None):
@@ -230,12 +279,30 @@ def op_set_resume(roster, group, field, value, rel="", legacy=None):
             raise Refuse(why)
     if field == "commit" and not SHA_RE.match(value):
         raise Refuse(f"--field commit needs a sha: {value!r}")
+    if field == "pr":
+        if not value.isdigit() or int(value) < 1:
+            raise Refuse(f"--field pr needs a pull request number: {value!r}")
+        g.setdefault("resume", {})["pr"] = int(value)
+        return
     if field == "stage":
         value = _closing(g, value, legacy, "set-resume")
+        _drop_stale_note(g, value)
     resume = g.setdefault("resume", {})
     resume[field] = _text(value) if field in TEXT_RESUME_FIELDS else value
 
 
+def _drop_stale_note(g, stage):
+    """Closing a group clears a resume.note that names owed work, and says so;
+    any other note (a set-size record, say) stays (carry 2)."""
+    resume = g.get("resume") or {}
+    note = resume.get("note")
+    if stage in roster_lib.DONE_STAGES and isinstance(note, str) \
+            and OWED_NOTE_RE.search(note):
+        resume["note"] = None
+        print(f"{g.get('group')}: cleared the stale resume.note naming owed work: "
+              f"{note[:80]!r}")
+
+
 def _closing(g, stage, legacy, op):
     """The stage `op` writes for `stage`: roster_lib.closing_stage, the one
     rule roster_sync's merge applies too. A downgrade is printed with the
@@ -286,7 +353,33 @@ def op_unwire_issue(roster, group, issue, field="issues"):
     g[field] = [i for i in held if i != n]
 
 
-def op_append_group(roster, json_file, rel="", sizes=()):
+#: Files an overlap does not count (carry 5): the instrument index and the
+#: per-instrument notes every instrument group touches.
+INDEX_FILES = ("tools/audit/seat/INSTRUMENTS.md",)
+INDEX_DIRS = ("tools/audit/seat/instruments/",)
+
+
+def _is_index(path):
+    return path in INDEX_FILES or path.startswith(INDEX_DIRS)
+
+
+def overlap_why(roster, new):
+    """The not-started groups sharing a non-index file with `new`, as
+    `{group: [files]}` -- the existing-groups-first rule at admission."""
+    mine = {f for f in new.get("files") or [] if not _is_index(f)}
+    out = {}
+    for g in roster.get("groups", []):
+        if (g.get("resume") or {}).get("stage") != "not-started":
+            continue
+        both = sorted(mine & set(g.get("files") or []))
+        if both:
+            out[g.get("group")] = both
+    return out
+
+
+def op_append_group(roster, json_file, rel="", sizes=(), reason=None):
+    if json_file.startswith("@"):
+        json_file = json_file[1:]
     try:
         new = json.loads(Path(json_file).read_text(encoding="utf-8"))
     except (OSError, ValueError) as e:
@@ -314,10 +407,21 @@ def op_append_group(roster, json_file, rel="", sizes=()):
     bad = [a for a in after if a not in known]
     if bad:
         raise Refuse(f"append-group: {gid} after names no group: {bad}")
+    clash = overlap_why(roster, new)
+    if clash and not (reason or "").strip():
+        raise Refuse(f"append-group: {gid} shares files with not-started "
+                     "group(s); fold the scope into them, or pass "
+                     "--reason \"<text>\": "
+                     + "; ".join(f"{k}: {', '.join(v)}"
+                                 for k, v in clash.items()))
     new.setdefault("issues", [])
     new.setdefault("fixes", [])
     new.setdefault("resume", {"stage": "not-started",
                               "branch": new.get("resume", {}).get("branch")})
+    if clash:
+        note = f"overlap admitted ({', '.join(clash)}): {reason.strip()}"
+        new["resume"]["note"] = (f"{new['resume']['note']}; {note}"
+                                 if new["resume"].get("note") else note)
     roster.setdefault("groups", []).append(new)
 
 
@@ -327,6 +431,16 @@ def op_edit_brief(roster, group, text):
 
 def op_append_carry(roster, group, text):
     g = _need(roster, group)
+    resume = g.get("resume") or {}
+    stage = resume.get("stage")
+    if stage in roster_lib.CARRY_CLOSED:
+        into = resume.get("absorbed_into")
+        raise Refuse(f"append-carry: {group} is {stage}"
+                     + (f", absorbed into {into}: carry to {into}"
+                        if stage == "absorbed" and into else
+                        "; carry to an open group"))
+    if resume.get("pr"):
+        print(f"WARN carry to {group}: PR #{resume['pr']} is open on it")
     entry = _text(text)
     carry = g.setdefault("carry", [])
     if entry in carry:
@@ -453,7 +567,7 @@ def op_mark_carry(roster, group, index, match, kind, arg):
 
 
 def apply_op(roster, op, group, value, field, at_sha, match=None, rel="",
-             sizes=(), legacy=None, rest=()):
+             sizes=(), legacy=None, rest=(), into=None, reason=None):
     """One op on a loaded roster -- re-run on each attempt of a push race,
     so the edit is applied to the tip it is pushed onto. `rel` is the roster's
     path and `sizes` the duration model's vocabulary, for a refusal to name
@@ -461,13 +575,13 @@ def apply_op(roster, op, group, value, field, at_sha, match=None, rel="",
     roster's cut-over carries (roster_lib.read_legacy), which a stage write
     reads; `rest` is mark-carry's `<kind> <value...>`."""
     if op == "set-stage":
-        op_set_stage(roster, group, value, at_sha, rel, legacy)
+        op_set_stage(roster, group, value, at_sha, rel, legacy, into)
     elif op == "wire-issue":
         op_wire_issue(roster, group, value, field or "issues")
     elif op == "unwire-issue":
         op_unwire_issue(roster, group, value, field or "issues")
     elif op == "append-group":
-        op_append_group(roster, value, rel, sizes)
+        op_append_group(roster, value, rel, sizes, reason)
     elif op == "edit-brief":
         op_edit_brief(roster, group, value)
     elif op == "set-resume":
@@ -701,6 +815,32 @@ def added_texts(before, after):
     return [x for x in out if isinstance(x, str) and x]
 
 
+def added_resume(before, after):
+    """The resume free text `after` sets over `before`: set-resume's values and
+    an append-group's resume.note, the other texts an op writes."""
+    old = {g.get("group"): (g.get("resume") or {}) for g in before.get("groups", [])}
+    out = []
+    for g in after.get("groups", []):
+        o = old.get(g.get("group"), {})
+        for f in TEXT_RESUME_FIELDS:
+            v = (g.get("resume") or {}).get(f)
+            if isinstance(v, str) and v and v != o.get(f):
+                out.append(v)
+    return out
+
+
+def privacy_refusal(texts):
+    """Why the added `texts` may not land, or None: ref_privacy's leak classes,
+    the check prepr.sh runs when the roster lands on main (carry 7)."""
+    ident = ref_privacy.Identity.of_host()
+    for text in texts:
+        why = ref_privacy.leaks(text, ident)
+        if why:
+            return (f"{', '.join(why)} in {text[:80]!r}; scrub the path "
+                    "(name the file repo-relative, or cite its sha)")
+    return None
+
+
 def ruling_verdict(src, pid):
     """The `Verdict:` of the `## <pid>:` entry in a triage batch file: ACCEPT,
     REJECT or DEFER; None when no such entry; "unreadable" when it has no
@@ -932,6 +1072,9 @@ def write_roster(checkout, ref, branch, worktree, roster_path, msg, push,
                              ruling_reader(worktree, checkout))
         if why:
             raise Refuse(f"triage gate: {why}; nothing written")
+        why = privacy_refusal(added_texts(before, roster) + added_resume(before, roster))
+        if why:
+            raise Refuse(f"privacy gate: {why}; nothing written")
         path.write_text(dump(roster), encoding="utf-8")
         if not run(["git", "-C", str(worktree), "status", "--porcelain"]).strip():
             print(f"no change: {label} wrote the roster's own bytes "
@@ -977,16 +1120,7 @@ def write_roster(checkout, ref, branch, worktree, roster_path, msg, push,
                  "nothing of this edit reached origin")
 
 
-def main(argv=None) -> int:
-    if argv is None:
-        argv = sys.argv[1:]
-    if "--self-test" in argv:
-        # Every git call in the self-test, the runner's and the ops' under
-        # test, runs in a throwaway repository: all of them take the env.
-        sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
-        from throwaway_git import throwaway_git_environ
-        with throwaway_git_environ():
-            return _self_test()
+def build_parser():
     p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
     p.add_argument("op", choices=("set-stage", "wire-issue", "unwire-issue", "append-group",
                                   "edit-brief", "append-carry", "set-resume",
@@ -1001,6 +1135,9 @@ def main(argv=None) -> int:
     p.add_argument("--field", choices=RESUME_FIELDS + WIRE_FIELDS,
                    help="set-resume: which resume field to write; "
                         "unwire-issue: issues (default) or fixes")
+    p.add_argument("--into", help="set-stage absorbed: the live host group")
+    p.add_argument("--reason", help="append-group: why the new group shares "
+                   "files with a not-started group; recorded in resume.note")
     p.add_argument("--value", dest="value_opt",
                    help="the value, for when a positional value does not fit")
     p.add_argument("--match",
@@ -1029,6 +1166,13 @@ def main(argv=None) -> int:
     p.add_argument("--issue-state",
                    help="JSON object issue -> open|closed: the states the done "
                         "hold reads instead of gh (no network)")
+    return p
+
+
+def parse_op(argv):
+    """The parsed `argv` of one op: (args, value, rest). The one
+    grammar `main` and a batch (roster_queue.py run --batch) share."""
+    p = build_parser()
     a = p.parse_intermixed_args(argv)
     rest = list(a.rest)
     if a.op == "mark-carry" and a.match is not None and a.value is not None:
@@ -1050,6 +1194,10 @@ def main(argv=None) -> int:
         p.error(f"{a.op} needs an index or --match")
     if a.op == "set-files" and value is not None:
         p.error("set-files takes --add, --set-files or --set-hot, no value")
+    if a.into is not None and a.op != "set-stage":
+        p.error("--into is a set-stage flag")
+    if a.reason is not None and a.op != "append-group":
+        p.error("--reason is an append-group flag")
     if a.op not in ("set-size", "set-files") and a.cite:
         p.error("--cite is a set-size / set-files flag")
     if a.op != "set-files" and (a.add or a.set_files is not None
@@ -1068,6 +1216,82 @@ def main(argv=None) -> int:
         p.error(f"{a.op} --field is one of {', '.join(WIRE_FIELDS)}")
     if a.op not in ("set-resume", "wire-issue", "unwire-issue") and a.field:
         p.error("--field is a set-resume / wire-issue / unwire-issue flag")
+    return a, value, rest
+
+
+def make_edit(a, value, rest):
+    """The `edit(roster, rel)` callback of one parsed op, for write_roster."""
+    def edit(roster, rel) -> bool:
+        sizes = ()
+        if a.op == "append-group":
+            # The size vocabulary comes from the tree the roster lands in,
+            # not from this tool's: an XS appended while durations.json
+            # lacked it is the second half of this class.
+            try:
+                sizes = roster_lib.sizes(
+                    roster_lib.read_durations(a.worktree))
+            except roster_lib.SchemaError as e:
+                raise Refuse(str(e))
+        if a.op in ("set-size", "set-files"):
+            apply_files_op(roster, a, value, rel, a.checkout, a.worktree)
+            return True
+        legacy = None
+        if a.op in ("set-stage", "set-resume"):
+            try:
+                legacy = roster_lib.read_legacy(a.worktree, rel)
+            except roster_lib.RosterNotFound as e:
+                raise Refuse(f"the carry cut-over is unreadable, so no "
+                             f"stage is written: {e}")
+        apply_op(roster, a.op, a.group, value, a.field, a.at_sha, a.match,
+                 rel, sizes, legacy, rest, a.into, a.reason)
+        if a.op == "set-stage" or (a.op == "set-resume" and a.field == "stage"):
+            try:
+                held = hold_done(roster, a.group, a.worktree, carry_audit.issue_reader(
+                    roster.get("repo") or carry_audit.REPO, a.issue_state))
+            except (ValueError, SystemExit) as e:  # carry_audit's refusals
+                raise Refuse(f"the done hold cannot read issue state: {e}")
+            if held:
+                print(f"roster_edit: HELD {a.group} at {HOLD_STAGE}, not {value}: "
+                      f"it owns open {', '.join(f'#{n}' for n in held)} with no other "
+                      "live owner; wire each to its next owner or close it, then "
+                      "set the stage again", file=sys.stderr)
+        return True
+    return edit
+
+
+def batch_edit(edits):
+    """One `edit(roster, rel)` for write_roster that applies several parsed
+    ops (make_edit callbacks) in order, so a batch costs one lint and one
+    push (roster_queue.py run --batch). An op that refuses is rolled back and
+    skipped, its reason in `results[i]` (None: applied); the batch writes when
+    any applied. Re-run on a push race, `results` is rewritten each time."""
+    results = [None] * len(edits)
+
+    def edit(roster, rel) -> bool:
+        for i, one in enumerate(edits):
+            snap = copy.deepcopy(roster)
+            try:
+                one(roster, rel)
+                results[i] = None
+            except Refuse as e:
+                roster.clear()
+                roster.update(snap)
+                results[i] = str(e)
+        return any(r is None for r in results)
+    return edit, results
+
+
+def main(argv=None) -> int:
+    if argv is None:
+        argv = sys.argv[1:]
+    if "--self-test" in argv:
+        # Every git call in the self-test, the runner's and the ops' under
+        # test, runs in a throwaway repository: all of them take the env.
+        sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
+        from throwaway_git import throwaway_git_environ
+        with throwaway_git_environ():
+            return _self_test()
+    a, value, rest = parse_op(argv)
     try:
         fetch_origin(a.checkout)
         ref, branch = roster_target(a.checkout, a.roster_ref, a.branch,
@@ -1076,41 +1300,7 @@ def main(argv=None) -> int:
         why = ref_privacy.refusal(branch, (("the message", msg),))
         if why:
             raise Refuse(f"{why} would publish this host (#2310); nothing written")
-        def edit(roster, rel) -> bool:
-            sizes = ()
-            if a.op == "append-group":
-                # The size vocabulary comes from the tree the roster lands in,
-                # not from this tool's: an XS appended while durations.json
-                # lacked it is the second half of this class.
-                try:
-                    sizes = roster_lib.sizes(
-                        roster_lib.read_durations(a.worktree))
-                except roster_lib.SchemaError as e:
-                    raise Refuse(str(e))
-            if a.op in ("set-size", "set-files"):
-                apply_files_op(roster, a, value, rel, a.checkout, a.worktree)
-                return True
-            legacy = None
-            if a.op in ("set-stage", "set-resume"):
-                try:
-                    legacy = roster_lib.read_legacy(a.worktree, rel)
-                except roster_lib.RosterNotFound as e:
-                    raise Refuse(f"the carry cut-over is unreadable, so no "
-                                 f"stage is written: {e}")
-            apply_op(roster, a.op, a.group, value, a.field, a.at_sha, a.match,
-                     rel, sizes, legacy, rest)
-            if a.op == "set-stage" or (a.op == "set-resume" and a.field == "stage"):
-                try:
-                    held = hold_done(roster, a.group, a.worktree, carry_audit.issue_reader(
-                        roster.get("repo") or carry_audit.REPO, a.issue_state))
-                except (ValueError, SystemExit) as e:  # carry_audit's refusals
-                    raise Refuse(f"the done hold cannot read issue state: {e}")
-                if held:
-                    print(f"roster_edit: HELD {a.group} at {HOLD_STAGE}, not {value}: "
-                          f"it owns open {', '.join(f'#{n}' for n in held)} with no other "
-                          "live owner; wire each to its next owner or close it, then "
-                          "set the stage again", file=sys.stderr)
-            return True
+        edit = make_edit(a, value, rest)
         return write_roster(a.checkout, ref, branch, a.worktree, a.roster_path,
                             msg, a.push, a.lint_cwd, f"{a.op} {a.group}", edit)
     except Refuse as e:
@@ -1251,7 +1441,7 @@ def _self_test() -> int:
 
     def edit(op, group, value, push=True, branch="edit-1", lint_cwd=None,
              at_sha=None, field=None, value_opt=None, match=None, wt="wt",
-             rest=(), issues="closed"):
+             rest=(), issues="closed", into=None, reason=None):
         args = [op, group, "--issue-state", str(ISSUES[issues])]
         if value is not None:
             args += [value]
@@ -1264,6 +1454,10 @@ def _self_test() -> int:
             args += ["--value", value_opt]
         if at_sha:
             args += ["--at-sha", at_sha]
+        if into:
+            args += ["--into", into]
+        if reason is not None:
+            args += ["--reason", reason]
         try:
             return main(args
                         + ["--checkout", str(drv), "--roster-ref", "main",
@@ -1448,6 +1642,8 @@ def _self_test() -> int:
     check("edit-brief rc",
           edit("edit-brief", "R9-B", "rewritten brief") == 0
           and branch_roster()["groups"][1]["brief"] == "rewritten brief")
+    # append-carry refuses a closing destination (carry 3): reopen R9-A first.
+    edit("set-stage", "R9-A", "in-progress")
     check("append-carry rc",
           edit("append-carry", "R9-A", "carry text one") == 0
           and branch_roster()["groups"][0]["carry"] == ["carry text one"])
@@ -1465,7 +1661,9 @@ def _self_test() -> int:
         "Verdict: ACCEPT -> R9-B (carry)\nSource: sweep\n\n"
         "## P2: a second watcher\nVerdict: REJECT\nBinding: standing CPU\n\n"
         "## P3: no verdict line\nSource: sweep\n\n"
-        "## P4: a later watcher\nVerdict: DEFER\nSource: sweep\n", encoding="utf-8")
+        "## P4: a later watcher\nVerdict: DEFER\nSource: sweep\n\n"
+        "## P-C: a lettered proposal\nVerdict: ACCEPT -> R9-B (carry)\n\n"
+        "## P-D: a lettered reject\nVerdict: REJECT\n", encoding="utf-8")
     run(["git", "-C", str(seed), "add", "-A"])
     run(["git", "-C", str(seed), "commit", "-q", "-m", "fixture triage ruling"])
     run(["git", "-C", str(seed), "push", "-q", str(origin), "main:refs/heads/main"])
@@ -1488,6 +1686,23 @@ def _self_test() -> int:
     check("triage gate: a citation to a missing batch is refused, proposal named or not",
           refuses("not on the roster branch", "append-carry", "R9-B",
                   "plain text. triage: dev/programme/triage/nope.md#P1"))
+    # Carry 0 (#2670): session s4 labelled later proposals with letters
+    # (`P-A`..`P-Q`); the numbered-only grammar never fired on them.
+    lettered = "Triage P-C (s4): fold a lettered proposal."
+    check("triage gate: a lettered label citing no ruling is refused",
+          refuses("cites no triage ruling", "append-carry", "R9-B", lettered)
+          and lettered not in branch_roster()["groups"][1]["carry"])
+    check("triage gate: a lettered label citing its ACCEPT ruling lands",
+          edit("append-carry", "R9-B", lettered + f" triage: {ruling}#P-C") == 0
+          and lettered + f" triage: {ruling}#P-C" in branch_roster()["groups"][1]["carry"])
+    check("triage gate: a lettered label citing a REJECT ruling is refused",
+          refuses("REJECT", "append-carry", "R9-B",
+                  f"proposal P-D: a thing. triage: {ruling}#P-D"))
+    check("triage gate: a lettered label citing no such entry is refused",
+          refuses("no such entry", "append-carry", "R9-B",
+                  f"proposal P-E: a thing. triage: {ruling}#P-E"))
+    check("triage gate null control: a hyphenated word that is no label lands",
+          edit("append-carry", "R9-B", "the P-value of a triage Pareto plot") == 0)
     check("triage gate: a new group's brief is judged",
           refuses("cites no triage ruling", "edit-brief", "R9-A", "brief from proposal P4"))
     check("triage gate: text naming no proposal passes untouched",
@@ -1501,6 +1716,8 @@ def _self_test() -> int:
     check("triage gate fixture restored",
           edit("drop-carry", "R9-B", None, match="orphan discharge") == 0
           and edit("drop-carry", "R9-B", None, match="no proposal") == 0
+          and edit("drop-carry", "R9-B", None, match="lettered proposal") == 0
+          and edit("drop-carry", "R9-B", None, match="P-value") == 0
           and branch_roster()["groups"][1]["carry"] == [])
 
     # set-resume: the resume free-text fields a session restarts from, through
@@ -1867,10 +2084,12 @@ def _self_test() -> int:
     # `]` that would end carry_mark's grammar early (review X7, X8). R9-A is
     # put in each closed stage in turn; each refusal leaves the branch where it
     # was, and the null controls -- an open destination, a plain value -- land.
+    edit("set-stage", "R9-B", "in-progress", branch="mark-1")
     edit("append-carry", "R9-B", "carry four", branch="mark-1")
     edit("append-carry", "R9-B", "carry five", branch="mark-1")
     for closed in roster_lib.CARRY_CLOSED:
-        edit("set-stage", "R9-A", closed, branch="mark-1")
+        edit("set-stage", "R9-A", closed, branch="mark-1",
+             into="R9-B" if closed == "absorbed" else None)
         t1 = tip("mark-1")
         rc, out = mark("3", "moved", "R9-A")
         check(f"mark-carry refuses moved to a {closed} group",
@@ -1892,32 +2111,39 @@ def _self_test() -> int:
           (rc, out[-300:]))
     # The cut-over: a carry on a closed group at the cut-over commit is legacy
     # and never pending; one appended after it is.
-    edit("set-stage", "R9-A", "done", branch="mark-1")
-    edit("append-carry", "R9-A", "legacy carry", branch="mark-1")
+    # A closed group that holds a carry can only be admitted whole (append-group
+    # with a done stage), since append-carry now refuses a closed destination.
+    legacyg = Path(tmp, "legacy-group.json")
+    legacyg.write_text(json.dumps({
+        "group": "R9-L", "lane": "L2", "after": [], "brief": "fixture L",
+        "carry": ["legacy carry"], "resume": {"stage": "done", "branch": "handoff/l"}}),
+        encoding="utf-8")
+    edit("append-group", "R9-L", str(legacyg), branch="mark-1")
     saved = dict(roster_lib.CARRY_CUTOVER)
     roster_lib.CARRY_CUTOVER[FIXTURE_ROSTER] = tip("mark-1")
     try:
-        rc, out = said(lambda: edit("set-stage", "R9-A", "done", branch="mark-1"))
+        rc, out = said(lambda: edit("set-stage", "R9-L", "done", branch="mark-1"))
         check("a legacy carry alone leaves set-stage done as done (null control)",
-              rc == 0 and at_mark("R9-A")["resume"]["stage"] == "done",
+              rc == 0 and at_mark("R9-L")["resume"]["stage"] == "done",
               (rc, out[-300:]))
-        edit("append-carry", "R9-A", "post-cut-over carry", branch="mark-1")
-        rc, out = said(lambda: edit("set-stage", "R9-A", "done", branch="mark-1"))
+        edit("set-stage", "R9-L", HOLD_STAGE, branch="mark-1")
+        edit("append-carry", "R9-L", "post-cut-over carry", branch="mark-1")
+        rc, out = said(lambda: edit("set-stage", "R9-L", "done", branch="mark-1"))
         check("a carry after the cut-over is pending beside a legacy one",
-              rc == 0 and at_mark("R9-A")["resume"]["stage"] == "carries-open"
+              rc == 0 and at_mark("R9-L")["resume"]["stage"] == "carries-open"
               and "(1 pending carries)" in out, (rc, out[-300:]))
-        rc, out = said(lambda: edit("set-resume", "R9-A", "done", field="stage",
+        rc, out = said(lambda: edit("set-resume", "R9-L", "done", field="stage",
                                     branch="mark-1"))
         check("set-resume --field stage done reads the same rule",
-              rc == 0 and at_mark("R9-A")["resume"]["stage"] == "carries-open"
-              and "set-resume R9-A: done -> carries-open" in out, (rc, out[-300:]))
+              rc == 0 and at_mark("R9-L")["resume"]["stage"] == "carries-open"
+              and "set-resume R9-L: done -> carries-open" in out, (rc, out[-300:]))
         # An unreadable cut-over refuses the stage write and writes nothing
         # (review X6): read as "no legacy", the legacy carry would be pending.
         # The readable null is the "legacy carry alone" check above.
         roster_lib.CARRY_CUTOVER[FIXTURE_ROSTER] = "f" * 40
         t1 = tip("mark-1")
         for op, kw in (("set-stage", {}), ("set-resume", {"field": "stage"})):
-            rc, out = said(lambda: edit(op, "R9-A", "done", branch="mark-1",
+            rc, out = said(lambda: edit(op, "R9-L", "done", branch="mark-1",
                                         **kw))
             check(f"{op} refuses an unreadable cut-over and writes nothing",
                   rc == 2 and "the carry cut-over is unreadable" in out
@@ -1926,6 +2152,189 @@ def _self_test() -> int:
         roster_lib.CARRY_CUTOVER.clear()
         roster_lib.CARRY_CUTOVER.update(saved)
 
+    # R10-ROSTER-WRITE-SWEEP: carries 2, 3, 4, 5, 6, 7 and 16, each with the
+    # null control that keeps the refusal from being a blanket one.
+    W = "wsw-1"
+
+    def wedit(*a, **k):
+        return edit(*a, branch=W, **k)
+
+    def at_w(g):
+        return next(x for x in branch_roster(W)["groups"] if x["group"] == g)
+
+    def said_w(*a, **k):
+        out, err = io.StringIO(), io.StringIO()
+        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
+            rc = sysrc(lambda: wedit(*a, **k))
+        return rc, out.getvalue() + err.getvalue()
+
+    def jgroup(name, **kw):
+        f = Path(tmp, f"{name}.json")
+        f.write_text(json.dumps({"group": name, "lane": "L2", "after": [],
+                                 "brief": f"fixture {name}", **kw}),
+                     encoding="utf-8")
+        return str(f)
+
+    # carry 6: append-group reads @file like append-carry and edit-brief.
+    f1 = jgroup("R9-W1", files=["tools/x.py", "tools/audit/seat/INSTRUMENTS.md"])
+    check("append-group @file lands (carry 6)",
+          wedit("append-group", "R9-W1", "@" + f1) == 0
+          and at_w("R9-W1")["lane"] == "L2")
+    check("append-group bare path still lands (null control)",
+          wedit("append-group", "R9-W2", jgroup("R9-W2")) == 0
+          and at_w("R9-W2")["lane"] == "L2")
+    check("append-group @missing is still refused",
+          refuses("unreadable JSON", "append-group", "R9-W0",
+                  "@" + str(Path(tmp, "no-such.json")), branch=W))
+    # carry 5: existing-groups-first at admission.
+    f3 = jgroup("R9-W3", files=["tools/x.py"])
+    rc, out = said_w("append-group", "R9-W3", f3)
+    check("append-group overlapping a not-started group refuses, naming both (carry 5)",
+          rc == 2 and "R9-W1" in out and "tools/x.py" in out
+          and "--reason" in out, (rc, out[-300:]))
+    check("append-group --reason admits the overlap and records it",
+          wedit("append-group", "R9-W3", f3, reason="needs the same seam") == 0
+          and "needs the same seam" in at_w("R9-W3")["resume"]["note"]
+          and "R9-W1" in at_w("R9-W3")["resume"]["note"])
+    check("an empty --reason does not admit the overlap",
+          wedit("append-group", "R9-W3b",
+                jgroup("R9-W3b", files=["tools/x.py"]), reason=" ") == 2)
+    check("overlap on the index file alone passes (null control)",
+          wedit("append-group", "R9-W4",
+                jgroup("R9-W4", files=["tools/audit/seat/INSTRUMENTS.md",
+                                       "tools/audit/seat/instruments/a.md"])) == 0)
+    wedit("append-group", "R9-W5", jgroup(
+        "R9-W5", files=["tools/y.py"], resume={"stage": "in-progress", "branch": "handoff/w5"}))
+    wedit("append-group", "R9-W6", jgroup(
+        "R9-W6", files=["tools/z.py"], resume={"stage": "done", "branch": "handoff/w6"}))
+    check("overlap with an in-progress group passes (null control)",
+          wedit("append-group", "R9-W7", jgroup("R9-W7", files=["tools/y.py"])) == 0)
+    check("overlap with a done group passes (null control)",
+          wedit("append-group", "R9-W8", jgroup("R9-W8", files=["tools/z.py"])) == 0)
+    # carry 3: a carry to a closing group is refused at write time.
+    wedit("append-group", "R9-WD", jgroup(
+        "R9-WD", resume={"stage": "done", "branch": "handoff/wd"}))
+    wedit("append-group", "R9-WA", jgroup(
+        "R9-WA", resume={"stage": "absorbed", "branch": "handoff/wa",
+                         "absorbed_into": "R9-A"}))
+    wedit("append-group", "R9-WN", jgroup(
+        "R9-WN", resume={"stage": "absorbed", "branch": "handoff/wn"}))
+    wedit("append-group", "R9-WP", jgroup(
+        "R9-WP", resume={"stage": "in-progress", "branch": "handoff/wp", "pr": 123}))
+    t_w = branch_roster(W)
+    rc, out = said_w("append-carry", "R9-WD", "late carry")
+    check("append-carry to a done group refuses and writes nothing (carry 3)",
+          rc == 2 and "R9-WD is done" in out
+          and branch_roster(W) == t_w, (rc, out[-300:]))
+    rc, out = said_w("append-carry", "R9-WA", "late carry")
+    check("append-carry to an absorbed group names absorbed_into",
+          rc == 2 and "absorbed into R9-A" in out, (rc, out[-300:]))
+    rc, out = said_w("append-carry", "R9-WN", "late carry")
+    check("append-carry to an absorbed group with no host still refuses",
+          rc == 2 and "R9-WN is absorbed" in out, (rc, out[-300:]))
+    rc, out = said_w("append-carry", "R9-WP", "pr carry")
+    check("append-carry to a group with resume.pr appends and WARNs",
+          rc == 0 and "WARN carry to R9-WP: PR #123 is open on it" in out
+          and at_w("R9-WP")["carry"] == ["pr carry"], (rc, out[-300:]))
+    rc, out = said_w("append-carry", "R9-A", "open carry")
+    check("append-carry to an open group with no PR appends without a WARN",
+          rc == 0 and "WARN" not in out
+          and at_w("R9-A")["carry"] == ["open carry"], (rc, out[-300:]))
+    # carry 4: resume.pr round-trips through set-resume.
+    check("set-resume --field pr round-trips an integer (carry 4)",
+          wedit("set-resume", "R9-A", "2836", field="pr") == 0
+          and at_w("R9-A")["resume"]["pr"] == 2836)
+    check("set-resume --field pr refuses a non-number",
+          refuses("pull request number", "set-resume", "R9-A", "#x",
+                  field="pr", branch=W))
+    # carry 2: closing a group clears a note naming owed work.
+    wedit("append-group", "R9-WO", jgroup(
+        "R9-WO", resume={"stage": "in-progress", "branch": "handoff/wo",
+                         "note": "has no pull request. Owed: recarry and open"}))
+    wedit("append-group", "R9-WK", jgroup(
+        "R9-WK", resume={"stage": "in-progress", "branch": "handoff/wk",
+                         "note": "size was M (cite)"}))
+    rc, out = said_w("set-stage", "R9-WO", "done")
+    check("set-stage done clears a note naming owed work and says so (carry 2)",
+          rc == 0 and at_w("R9-WO")["resume"]["note"] is None
+          and "cleared the stale resume.note" in out, (rc, out[-300:]))
+    check("set-stage done keeps a note that owes nothing (null control)",
+          wedit("set-stage", "R9-WK", "done") == 0
+          and at_w("R9-WK")["resume"]["note"] == "size was M (cite)")
+    check("set-stage to an open stage keeps an owed note (null control)",
+          wedit("set-stage", "R9-WO", "in-progress") == 0
+          and wedit("set-resume", "R9-WO", "Owed: x", field="note") == 0
+          and wedit("set-stage", "R9-WO", "review") == 0
+          and at_w("R9-WO")["resume"]["note"] == "Owed: x")
+    # carry 7: a host path in an added text is refused at the op.
+    hostpath = "evidence in /" + "Users/someone/sweep/run.log"  # built, not spelled
+    for op, args, kw in (
+            ("append-carry", ("R9-A", hostpath), {}),
+            ("edit-brief", ("R9-A", hostpath), {}),
+            ("set-resume", ("R9-A", hostpath), {"field": "note"}),
+            ("append-group", ("R9-WH", jgroup("R9-WH", brief=hostpath)), {})):
+        rc, out = said_w(op, *args, **kw)
+        check(f"{op} naming a host path is refused with the scrub hint (carry 7)",
+              rc == 2 and "privacy gate" in out and "scrub" in out, (rc, out[-300:]))
+    check("the same carry scrubbed passes (null control)",
+          wedit("append-carry", "R9-A", "evidence in the sweep's run.log") == 0)
+    # carry 16: set-stage absorbed --into.
+    wedit("append-group", "R9-WX", jgroup("R9-WX"))
+    check("set-stage absorbed without --into is refused (carry 16)",
+          refuses("needs --into", "set-stage", "R9-WX", "absorbed", branch=W))
+    check("set-stage absorbed --into an unknown group is refused",
+          refuses("names no group", "set-stage", "R9-WX", "absorbed",
+                  into="R9-NOPE", branch=W))
+    check("set-stage absorbed --into itself is refused",
+          refuses("into itself", "set-stage", "R9-WX", "absorbed",
+                  into="R9-WX", branch=W))
+    check("set-stage absorbed --into a done group is refused",
+          refuses("not a live group", "set-stage", "R9-WX", "absorbed",
+                  into="R9-WD", branch=W))
+    check("--into on another stage is refused",
+          refuses("--into is for stage absorbed", "set-stage", "R9-WX",
+                  "done", into="R9-A", branch=W))
+    check("set-stage absorbed --into a live group records absorbed_into",
+          wedit("set-stage", "R9-WX", "absorbed", into="R9-A") == 0
+          and at_w("R9-WX")["resume"]["stage"] == "absorbed"
+          and at_w("R9-WX")["resume"]["absorbed_into"] == "R9-A")
+    check("a later open stage drops the stale absorbed_into",
+          wedit("set-stage", "R9-WX", "in-progress") == 0
+          and "absorbed_into" not in at_w("R9-WX")["resume"])
+
+    # run --batch (carry 13): a batch of one is byte-identical to the single
+    # path; a refused op is skipped and rolled back; one push carries the rest.
+    def batch_bytes(branch, ops):
+        edits = []
+        for op in ops:
+            a, v, r = parse_op(op + ["--checkout", str(drv), "--worktree",
+                                      str(Path(tmp, "wtb")), "--issue-state",
+                                      str(ISSUES["closed"])])
+            edits.append(make_edit(a, v, r))
+        bedit, results = batch_edit(edits)
+        rc = write_roster(str(drv), "main", branch, str(Path(tmp, "wtb")), None,
+                          "batch", True, str(seed), "batch", bedit)
+        pushed = run(["git", "-C", str(origin), "branch", "--list", branch]).strip()
+        return rc, results, (json.dumps(branch_roster(branch), sort_keys=True)
+                             if pushed else None)
+
+    rc1, res1, one = batch_bytes("batch-1", [["wire-issue", "R9-A", "41"]])
+    check("batch of one lands and reports it applied", rc1 == 0 and res1 == [None])
+    check("run via the single-op path first (control)",
+          edit("wire-issue", "R9-A", "41", branch="single-1") == 0)
+    check("a batch of one is byte-identical to the single-op path",
+          one == json.dumps(branch_roster("single-1"), sort_keys=True))
+    rc2, res2, two = batch_bytes("batch-2", [["wire-issue", "R9-A", "41"],
+                                              ["set-stage", "R9-ZZ", "done"],
+                                              ["wire-issue", "R9-A", "42"]])
+    got = branch_roster("batch-2")["groups"][0]["issues"]
+    check("a batch skips a refused op and applies the others in one push",
+          rc2 == 0 and res2[0] is None and res2[1] and "R9-ZZ" in res2[1]
+          and res2[2] is None and got == [10, 41, 42], (res2, got))
+    check("a batch of only refused ops writes nothing",
+          batch_bytes("batch-3", [["set-stage", "R9-ZZ", "done"]])[0] == 0
+          and batch_bytes("batch-3", [["set-stage", "R9-ZZ", "done"]])[2] is None)
+
     # THE ROUND-TRIP REGRESSION. The roster's canonical bytes are indent=1,
     # ASCII-escaped, no trailing newline (the file at the fixplan ref). A dump
     # that does not reproduce them rewrites every line of the file on ANY edit
diff --git a/tools/audit/seat/roster_lib.py b/tools/audit/seat/roster_lib.py
index e520976b2..502d4af5b 100644
--- a/tools/audit/seat/roster_lib.py
+++ b/tools/audit/seat/roster_lib.py
@@ -537,7 +537,9 @@ def group_for_branch(roster: dict, branch: str) -> str | None:
     normalized the same way: `fix/r9-fr-4` answers for `R9-FR-4` without the
     roster having to name every branch spelling a seat used. Equality, never
     a prefix -- `fix/r9-fr-1` must not answer for `R9-FR-10`. None for a
-    branch no group claims: the caller rows it in the neutral phrasing.
+    branch no group claims: the caller rows it in the neutral phrasing. A
+    phase branch `<group>-pN` (handoff/r10-x-p2) answers for its group when
+    no group is itself named `<group>-pN`.
     """
     if not branch:
         return None
@@ -549,6 +551,11 @@ def group_for_branch(roster: dict, branch: str) -> str | None:
         gid = norm_group(str(g.get("group") or ""))
         if gid and gid == tail:
             return g.get("group")
+    phase = re.sub(r"-p\d+\Z", "", tail)
+    if phase != tail:  # handoff/<group>-pN: a phase branch of the group
+        for g in roster.get("groups", []):
+            if norm_group(str(g.get("group") or "")) == phase:
+                return g.get("group")
     return None
 
 
@@ -752,6 +759,19 @@ def _self_test() -> int:
         # The critical-path set: read at a ref and normalized; None for every
         # failure shape, so a caller fails to FIFO rather than crashing.
         check("a group id normalizes case and underscore", norm_group("R10_A") == "r10-a")
+        # Phase branches (handoff/<group>-pN) answer for their group (carry 5).
+        rg = {"groups": [{"group": "R10-PH", "resume": {"branch": "handoff/other"}},
+                         {"group": "R10-PH-P2", "resume": {"branch": "handoff/x"}}]}
+        check("group_for_branch: handoff/<group>-p2 resolves to the group",
+              group_for_branch(rg, "handoff/r10-ph-p2") == "R10-PH-P2"
+              and group_for_branch({"groups": rg["groups"][:1]},
+                                   "handoff/r10-ph-p2") == "R10-PH")
+        check("group_for_branch: a phase branch of no group is None (null control)",
+              group_for_branch(rg, "handoff/r10-zz-p2") is None
+              and group_for_branch(rg, "handoff/r10-ph-px") is None)
+        check("group_for_branch: -p2 never answers a longer id by prefix",
+              group_for_branch({"groups": [{"group": "R10-PH-1"}]},
+                               "handoff/r10-ph-p2") is None)
         check("no critical-path file at a ref is None",
               critical_path_groups(str(repo), "HEAD") is None)
         check("critical_path_read: a ref publishing no file is (set(), ''), a "
diff --git a/tools/audit/seat/roster_queue.py b/tools/audit/seat/roster_queue.py
index df5667aed..2abf98aab 100644
--- a/tools/audit/seat/roster_queue.py
+++ b/tools/audit/seat/roster_queue.py
@@ -4,6 +4,10 @@
     python3 -I tools/audit/seat/roster_queue.py run FIRST LAST --queue Q --report R \
         --edit-checkout DIR --worktree WT --lint-clone LC [--alive FILE] [--branch B]
     python3 -I tools/audit/seat/roster_queue.py readback SHA GROUP TEXTFILE
+    python3 -I tools/audit/seat/roster_queue.py run all --mark ... [--batch]
+    python3 -I tools/audit/seat/roster_queue.py loop [--every 300] ...
+    python3 -I tools/audit/seat/roster_queue.py release-held --queue Q --edit-checkout DIR
+    python3 -I tools/audit/seat/roster_queue.py unwired --edit-checkout DIR --open-issues FILE [--ref REF]
     python3 -I tools/audit/seat/roster_queue.py --self-test
 
 `run` applies queue lines FIRST..LAST (1-based; blank and `#` lines skipped, a
@@ -18,6 +22,21 @@ refusal is that main moved or the push lost a race with a clean lint
 `--edit-checkout` (the orchestrator's), which only supplies the tool and the
 roster. A refusal is reported, never forced.
 
+LINE GRAMMAR (one parser for `run`, `--batch` and `loop`): an unquoted word that
+begins with `#` ends the line (a `#` inside a word, or a quoted `'a # b'`,
+stays); the first token after the group is the value unless it is a flag, and
+`--flag value` pairs reach roster_edit as flags. `--mark` rewrites each applied
+line in place as `#done <line>` (pushed, read-back not FAILED) or `#refused
+<line>`, re-reading the queue at write time and replacing it atomically, so a
+line appended meanwhile survives; `all` (with --mark) is every unmarked op line;
+`#` lines (`#done`, `#refused`, `#held`, `#note`) are never applied. `--batch`
+parses every line with roster_edit.parse_op, applies them in ONE worktree and
+pushes once (a refused op is rolled back and skipped; any batch-level failure
+falls back to the single-op path). `loop` re-provisions a missing --lint-clone,
+then runs `all --mark` every --every seconds. `release-held` frees `#held
+append-carry` lines whose batch file is on origin/main; `unwired` lists open
+issues no roster group lists (carry_audit's ISSUE-UNLISTED).
+
 Every `append-carry <group> @file` is read back from the pushed commit: the
 roster JSON at that SHA must hold the file's text exactly as one carry entry.
 `readback` prints the figures; the report line says FAILED when none match.
@@ -29,6 +48,8 @@ touched after each report line. Blind spot, stated: only append-carry with an
 from __future__ import annotations
 
 import argparse
+import contextlib
+import io
 import json
 import os
 import re
@@ -74,10 +95,48 @@ def readback(sha, grp, fn, cwd=None, rel=ROSTER_REL):
             f"last120={last[:120]!r} len={len(last)}/{len(want)}"), bool(hit)
 
 
+def readback_text(sha, grp, text, cwd=None, rel=ROSTER_REL):
+    """True when the first 60 characters of an inline carry are inside a carry
+    entry of `grp` in the roster at `sha` (the LANDED test of the old loops)."""
+    s = _git("show", f"{sha}:{rel}", cwd=cwd)
+    if s.returncode:
+        raise RuntimeError(f"no {rel} at {sha}: {s.stderr.strip()[-120:]}")
+    g = next(_walk(json.loads(s.stdout), grp), None)
+    if g is None:
+        raise RuntimeError(f"group {grp} not in the roster at {sha}")
+    want = text.strip()[:60]
+    return any(want in x for x in g["carry"])
+
+
+def _split(ln):
+    """Shell words of `ln`, ending at an unquoted word that begins with `#`
+    (shell semantics: `@/p/b#1.txt` and `s6-batch8.md#P70` keep their `#`, a
+    quoted `'a # b'` is one word). Not shlex's comments=True, which cuts a `#`
+    in the middle of a word (P300). Words are split by the one lexer, then
+    each dequoted; a line it cannot dequote falls back to plain shlex.split."""
+    try:
+        lex = shlex.shlex(ln, posix=False)
+        lex.whitespace_split, lex.commenters = True, ""
+        out = []
+        for tok in lex:
+            if tok.startswith("#"):
+                break
+            out.append("".join(shlex.split(tok)))
+        return out
+    except ValueError:
+        return shlex.split(ln)
+
+
 def parse_line(ln):
+    """`(op, group, value, flags)` of one queue line, or None for a blank or
+    `#` line. THE ONE FLAG GRAMMAR, shared by `run`, `--batch` and `loop`: the
+    first token after the group is the value unless it is a flag, and every
+    `--flag value` after it reaches roster_edit as a flag, never folded into
+    the value (`set-stage G done --at-sha S` once wrote stage "done --at-sha
+    S", 2026-10-27)."""
     if not ln.strip() or ln.lstrip().startswith("#"):
         return None
-    t = shlex.split(ln)
+    t = _split(ln)
     if t and t[0][0].isdigit():
         t = t[1:]
     if len(t) < 2:
@@ -90,6 +149,31 @@ def parse_line(ln):
     return t[0], t[1], (rest[0] if rest else ""), rest[1:]
 
 
+def mark_line(queue, ln, tag):
+    """Rewrite the first unmarked line equal to `ln` as `#<tag> <ln>`. The
+    queue is re-read at write time, so a line another writer appended since
+    the run began is kept, and replaced through a temp file in the same
+    directory by os.replace, so a reader never sees a half-written queue."""
+    return replace_line(queue, ln, f"#{tag} {ln}")
+
+
+def replace_line(queue, old, new):
+    """Replace the first line equal to `old` by `new` (the queue re-read now)."""
+    q = Path(queue)
+    lines = q.read_text().split("\n")
+    for i, x in enumerate(lines):
+        if x == old:
+            lines[i] = new
+            break
+    else:
+        return False
+    fd, tmp = tempfile.mkstemp(dir=q.parent, prefix=q.name + ".")
+    with os.fdopen(fd, "w") as f:
+        f.write("\n".join(lines))
+    os.replace(tmp, q)
+    return True
+
+
 def run_queue(a, python=None):
     env = dict(os.environ)
     shims = Path(a.edit_checkout, "tools/audit/seat/shims")
@@ -117,17 +201,85 @@ def run_queue(a, python=None):
             rep(msg)
             return 2
     sh("git", "fetch", "-q", "origin")  # fetch only: the edit checkout is never moved
-    lines = Path(a.queue).read_text().split("\n")[a.first - 1:a.last]
+    mark = getattr(a, "mark", False)
+    allq = str(a.first) == "all"
+    if allq and not mark:
+        print("roster: `all` needs --mark (a cursor-less run must mark what it applied)",
+              file=sys.stderr)
+        return 2
+    qlines = Path(a.queue).read_text().split("\n")
+    lines = qlines if allq else qlines[int(a.first) - 1:int(a.last)]
+    if getattr(a, "batch", False):
+        return _run_batch(a, sh, rep, py, editor, lines, mark)
     for ln in lines:
         p = parse_line(ln)
         if not p:
             continue
         op, g, arg, extra = p
         try:
-            _run_op(a, sh, rep, py, editor, op, g, arg, extra)
+            ok = _run_op(a, sh, rep, py, editor, op, g, arg, extra)
         except Exception as e:  # noqa: BLE001 - every op attempted writes one line
             rep(f"roster: {op} {g} FAILED {type(e).__name__}: {e}"[:400].replace("\n", " "))
             return 1
+        if mark:
+            mark_line(a.queue, ln, "done" if ok else "refused")
+    return 0
+
+
+def _run_batch(a, sh, rep, py, editor, lines, mark):
+    """`run --batch`: every applicable line through roster_edit's own parser and
+    checks, ONE lint and ONE push (0.36 s a line against 1-3 min). A refused
+    op is rolled back and skipped. Any batch-level failure (a lint refusal, a
+    gate refusal of the joint text, a lost race) falls back to the single-op
+    path for every line, so a bad line never strands the others."""
+    sys.path.insert(0, str(Path(a.edit_checkout, "tools/audit/seat")))
+    import roster_edit as re_
+    items = []
+    for ln in lines:
+        p = parse_line(ln)
+        if p:
+            items.append((ln, p))
+    if not items:
+        return 0
+    common = ["--checkout", a.edit_checkout, "--worktree", a.worktree,
+              "--lint-cwd", a.lint_clone]
+    if a.branch:
+        common += ["--branch", a.branch]
+    try:
+        edits = []
+        for _, (op, g, arg, extra) in items:
+            with contextlib.redirect_stderr(io.StringIO()):  # argparse's usage noise
+                args, value, rest = re_.parse_op(
+                    [op, g] + ([arg] if arg else []) + extra + common)
+            edits.append(re_.make_edit(args, value, rest))
+        edit, results = re_.batch_edit(edits)
+        _git("fetch", "-q", "origin", cwd=a.lint_clone)
+        _git("checkout", "-q", "--detach", "origin/main", cwd=a.lint_clone)
+        re_.fetch_origin(a.edit_checkout)
+        ref, branch = re_.roster_target(a.edit_checkout, None, a.branch, None)
+        buf = io.StringIO()
+        with contextlib.redirect_stdout(buf):
+            rc = re_.write_roster(a.edit_checkout, ref, branch, a.worktree, None,
+                                  f"roster_edit batch of {len(items)} ({re_.SELF})",
+                                  True, a.lint_clone, "batch", edit)
+        m = re.search(r"pushed \S+ at ([0-9a-f]+)", buf.getvalue())
+        if rc != 0 or not (m or not any(r is None for r in results)):
+            raise RuntimeError(f"batch rc={rc}")
+    except SystemExit as e:  # argparse refused a line: that is a batch-level failure
+        rc, m, results = 1, None, None
+    except Exception as e:  # noqa: BLE001
+        rc, m, results = 1, None, None
+    if results is None:
+        rep("roster: batch fell back to the single-op path")
+        b = argparse.Namespace(**{**vars(a), "batch": False})
+        return run_queue(b, python=py)
+    for (ln, (op, g, arg, extra)), why in zip(items, results):
+        if why is None:
+            rep(f"roster: {op} {g} pushed {(m.group(1)[:9] if m else 'no-change')}")
+        else:
+            rep(f"roster: {op} {g} refused rc=2 {why[:300]}")
+        if mark:
+            mark_line(a.queue, ln, "done" if why is None else "refused")
     return 0
 
 
@@ -151,24 +303,88 @@ def _run_op(a, sh, rep, py, editor, op, g, arg, extra):
                     rb = " | readback: " + readback(m.group(1), g, arg[1:], cwd=a.worktree)[0]
                 except Exception as e:  # noqa: BLE001 - reported, not hidden
                     rb = f" | readback: FAILED {str(e)[-200:]}"
+            if op == "append-carry" and arg and not arg.startswith("@"):
+                try:
+                    hit = readback_text(m.group(1), g, arg, cwd=a.worktree)
+                    rb = " | readback: " + ("LANDED" if hit else "FAILED not-landed")
+                except Exception as e:  # noqa: BLE001
+                    rb = f" | readback: FAILED {str(e)[-200:]}"
             rep(f"roster: {op} {g} pushed {m.group(1)[:9]}{rb}")
-            return
+            return "FAILED" not in rb
         if attempt < 4 and (MOVED in out or ("failed to push" in out and "lint gate: TOTAL: 0" in out)):
             sh("git", "worktree", "remove", "--force", a.worktree)
             continue
         rep(f"roster: {op} {g} refused rc={r.returncode} " + " | ".join(out.strip().split("\n")[-3:])[:400])
-        return
+        return False
+
+
+HELD = "#held "
+BATCH_FILE_RE = re.compile(r"dev/programme/[A-Za-z0-9_./-]+\.md")
+
+
+def heal_clone(a):
+    """Provision a missing --lint-clone as a detached worktree of the edit
+    checkout at origin/main: the `loop` self-heal. `run` still refuses a missing
+    clone by name (#3020). The edit checkout's branches and files are untouched."""
+    if Path(a.lint_clone).is_dir():
+        return False
+    r = _git("worktree", "add", "-q", "--detach", a.lint_clone, "origin/main",
+             cwd=a.edit_checkout)
+    if r.returncode:
+        raise RuntimeError(f"lint clone self-heal failed: {r.stderr.strip()[-200:]}")
+    return True
+
+
+def loop_queue(a, once=False, sleep=None, python=None):
+    """`loop --every N`: heal the lint clone, apply every unmarked line with
+    marking, wait N seconds, repeat. The same runner and line grammar as `run`."""
+    import time
+    sleep = sleep or time.sleep
+    while True:
+        heal_clone(a)
+        run_queue(argparse.Namespace(**{**vars(a), "first": "all", "last": None,
+                                        "mark": True}), python=python)
+        if once:
+            return 0
+        sleep(a.every)
+
+
+def release_held(queue, checkout):
+    """`#held append-carry` lines whose batch file (a dev/programme/... .md path
+    in the line) exists on origin/main lose the `#held ` prefix and run next
+    pass. Returns (released, still_held) line lists."""
+    _git("fetch", "-q", "origin", "main", cwd=checkout)
+    released, held = [], []
+    for ln in Path(queue).read_text().split("\n"):
+        if not ln.startswith(HELD + "append-carry"):
+            continue
+        files = BATCH_FILE_RE.findall(ln)
+        if files and all(_git("cat-file", "-e", f"origin/main:{f}", cwd=checkout).returncode == 0
+                         for f in files):
+            if replace_line(queue, ln, ln[len(HELD):]):
+                released.append(ln)
+        else:
+            held.append(ln)
+    return released, held
+
+
+def unwired(roster, open_issues):
+    """Open issue numbers no roster group lists (carry_audit's ISSUE-UNLISTED)."""
+    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
+    import carry_audit
+    return [x for x in carry_audit.roster_report(roster, {}, set(open_issues))
+            if x.startswith("ISSUE-UNLISTED")]
 
 
 def _self_test():
     fails = []
     n = [0]
 
-    def ck(name, ok):
+    def ck(name, ok, got=""):
         n[0] += 1
         if not ok:
             fails.append(name)
-            print("  FAIL", name)
+            print("FAIL", name, f"(got: {got})" if got != "" else "")
 
     ck("parse: numbered", parse_line("7 set-stage G done") == ("set-stage", "G", "done", []))
     ck("parse: blank/comment", parse_line("") is None and parse_line("# x") is None)
@@ -267,6 +483,119 @@ def _self_test():
         ck("run: a missing --lint-clone is refused by name, rc 2, before any op",
            rc3 == 2 and "--lint-clone" in r3[-1] and "no-such-clone" in r3[-1]
            and len(r3) == 2 and not (t / "no-such-clone").exists())
+
+    # --- R10-ROSTER-WRITE-SWEEP: comment grammar, flags, marking, batch, loop
+    ck("parse: a trailing ` # comment` is dropped (carry 11)",
+       parse_line("set-stage G done # #2955 merged aced2589") == ("set-stage", "G", "done", []))
+    ck("parse: a # inside a word is kept (null)",
+       parse_line("append-carry G @/p/b#1.txt") == ("append-carry", "G", "@/p/b#1.txt", []))
+    ck("parse: an unquoted drop-carry --match keeps its #P (null)",
+       parse_line("drop-carry G --match s6-batch8.md#P70")
+       == ("drop-carry", "G", "", ["--match", "s6-batch8.md#P70"]))
+    ck("parse: a quoted 'a # b' stays one argument (null)",
+       parse_line("append-carry G 'a # b' # note") == ("append-carry", "G", "a # b", []))
+    ck("parse: set-stage keeps --at-sha a flag, not part of the value (carry 14)",
+       parse_line("set-stage G done --at-sha abc1234")
+       == ("set-stage", "G", "done", ["--at-sha", "abc1234"]))
+    with tempfile.TemporaryDirectory() as t2:
+        t = Path(t2)
+        sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
+        from throwaway_git import throwaway_git_init, throwaway_git_clone
+        repo = t / "repo"
+        env = throwaway_git_init(repo, "-q", "-b", "main")
+        (repo / "dev/programme/triage").mkdir(parents=True)
+        (repo / "dev/programme/triage/b.md").write_text("batch\n")
+        (repo / ROSTER_REL).parent.mkdir(parents=True, exist_ok=True)
+        (repo / ROSTER_REL).write_text(json.dumps({"groups": [{"group": "G", "carry": ["hello carry"], "issues": [5]}]}))
+        _git("add", "-A", cwd=repo, env=env)
+        _git("commit", "-qm", "r", cwd=repo, env=env)
+        sha = _git("rev-parse", "HEAD", cwd=repo, env=env).stdout.strip()
+        clone = t / "clone"
+        throwaway_git_clone(repo, clone, "-q")
+        stub = t / "stub2.py"
+        stub.write_text(
+            "import sys,pathlib\n"
+            f"q=pathlib.Path({str(t / 'q.txt')!r}); app=pathlib.Path({str(t / 'append')!r})\n"
+            "if app.exists():\n"
+            "    app.unlink(); q.write_text(q.read_text()+'\\n9 set-stage LATE done')\n"
+            "if 'BAD' in sys.argv: print('REFUSED: no group'); sys.exit(2)\n"
+            f"print('pushed handoff/x at {sha}')\n")
+        base = argparse.Namespace(first=1, last=4, queue=str(t / "q.txt"), report=str(t / "rep"),
+                                  edit_checkout=str(clone), worktree=str(clone),
+                                  lint_clone=str(clone), alive=None, branch=None,
+                                  editor=str(stub))
+        body = "1 set-stage G done # why\n2 set-stage BAD done\n# a note\n3 set-stage H done"
+
+        def fresh(text=body):
+            (t / "q.txt").write_text(text)
+            (t / "rep").write_text("")
+        fresh()
+        before = (t / "q.txt").read_bytes()
+        run_queue(base, python=sys.executable)
+        ck("run: without --mark the queue is byte-identical (null)",
+           (t / "q.txt").read_bytes() == before)
+        fresh()
+        (t / "append").write_text("")
+        run_queue(argparse.Namespace(**{**vars(base), "mark": True}), python=sys.executable)
+        got = (t / "q.txt").read_text().split("\n")
+        ck("run --mark: a pushed op is `#done`, a refused op `#refused`",
+           got[0] == "#done 1 set-stage G done # why" and got[1] == "#refused 2 set-stage BAD done"
+           and got[3] == "#done 3 set-stage H done", got)
+        ck("run --mark: a line appended after the run's first read survives",
+           got[-1] == "9 set-stage LATE done" and got[2] == "# a note", got)
+        fresh()
+        rc = run_queue(argparse.Namespace(**{**vars(base), "first": "all", "last": None}),
+                       python=sys.executable)
+        ck("run all without --mark is refused, nothing applied (rc 2)",
+           rc == 2 and (t / "q.txt").read_bytes() == body.encode())
+        fresh()
+        run_queue(argparse.Namespace(**{**vars(base), "first": "all", "last": None, "mark": True}),
+                  python=sys.executable)
+        ck("run all --mark applies every unmarked op line, no cursor",
+           (t / "q.txt").read_text().split("\n")[3].startswith("#done 3 set-stage H"))
+        run_queue(argparse.Namespace(**{**vars(base), "first": "all", "last": None, "mark": True}),
+                  python=sys.executable)
+        ck("a marked line is never applied again", (t / "rep").read_text().count("\n") == 3)
+        # inline append-carry readback (LANDED test, first 60 chars)
+        ck("readback_text: the carry's first 60 chars are found",
+           readback_text(sha, "G", "hello carry", cwd=clone))
+        ck("readback_text: an absent carry is not landed (null)",
+           not readback_text(sha, "G", "never written", cwd=clone))
+        # --batch: a line the batch cannot parse falls back to the single path
+        fresh("1 bogus-op G done\n")
+        run_queue(argparse.Namespace(**{**vars(base), "first": 1, "last": 1, "batch": True}),
+                  python=sys.executable)
+        rr = (t / "rep").read_text().split("\n")
+        ck("run --batch: a batch-level failure falls back to the single-op path",
+           rr[0] == "roster: batch fell back to the single-op path"
+           and rr[1] == f"roster: bogus-op G pushed {sha[:9]}", rr)
+        fresh("1 set-stage G done\n")
+        run_queue(argparse.Namespace(**{**vars(base), "first": 1, "last": 1, "batch": True}),
+                  python=sys.executable)
+        ck("run --batch: a batch whose every op is refused reports each refused, no fallback",
+           (t / "rep").read_text().startswith("roster: set-stage G refused rc=2"))
+        # release-held: a held carry waits for its batch file on origin/main
+        (t / "q.txt").write_text(
+            "#held append-carry G 'x dev/programme/triage/b.md#P1'\n"
+            "#held append-carry G 'y dev/programme/triage/absent.md#P2'\n")
+        rel, held = release_held(str(t / "q.txt"), str(clone))
+        q2 = (t / "q.txt").read_text().split("\n")
+        ck("release-held: a held line whose batch file exists is released",
+           len(rel) == 1 and q2[0].startswith("append-carry G"), q2)
+        ck("release-held: a held line whose batch file is absent stays held (null)",
+           len(held) == 1 and q2[1].startswith("#held "), q2)
+        # unwired sweep
+        ros = {"groups": [{"group": "G", "issues": [5], "resume": {"stage": "not-started"}}]}
+        ck("unwired: an open issue no group lists is reported",
+           unwired(ros, [5, 9]) == ["ISSUE-UNLISTED #9"])
+        ck("unwired: every open issue listed reports nothing (null)", unwired(ros, [5]) == [])
+        # loop: heals a missing lint clone, then applies and marks
+        fresh("1 set-stage G done\n")
+        lc = t / "healed"
+        run_a = argparse.Namespace(**{**vars(base), "lint_clone": str(lc), "every": 1})
+        loop_queue(run_a, once=True, python=sys.executable)
+        ck("loop: a missing lint clone is re-provisioned from origin, then the pass runs",
+           (lc / ".git").exists() and (t / "q.txt").read_text().startswith("#done 1 set-stage G done"))
     print(f"roster_queue self-test: {n[0]} checks, {len(fails)} failed")
     return 1 if fails else 0
 
@@ -279,20 +608,58 @@ def main(argv=None):
     p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
     sub = p.add_subparsers(dest="cmd", required=True)
     r = sub.add_parser("run")
-    r.add_argument("first", type=int)
-    r.add_argument("last", type=int)
-    for k in ("queue", "report", "edit-checkout", "worktree", "lint-clone"):
-        r.add_argument("--" + k, required=True)
-    r.add_argument("--alive")
-    r.add_argument("--branch")
-    r.add_argument("--editor")
+    r.add_argument("first", help="1-based first line, or `all` (needs --mark)")
+    r.add_argument("last", nargs="?", type=int)
+    r.add_argument("--mark", action="store_true",
+                   help="rewrite each applied line as `#done <line>` (pushed) "
+                        "or `#refused <line>`")
+    r.add_argument("--batch", action="store_true",
+                   help="all lines in one worktree: one lint, one push")
+    lp = sub.add_parser("loop")
+    for sp in (r, lp):
+        for k in ("queue", "report", "edit-checkout", "worktree", "lint-clone"):
+            sp.add_argument("--" + k, required=True)
+        sp.add_argument("--alive")
+        sp.add_argument("--branch")
+        sp.add_argument("--editor")
+    lp.add_argument("--every", type=int, default=300)
+    lp.add_argument("--batch", action="store_true")
+    rh = sub.add_parser("release-held")
+    rh.add_argument("--queue", required=True)
+    rh.add_argument("--edit-checkout", required=True)
+    uw = sub.add_parser("unwired")
+    uw.add_argument("--edit-checkout", required=True)
+    uw.add_argument("--ref", default="origin/main")
+    uw.add_argument("--open-issues", required=True,
+                    help="JSON list of open issue numbers (or gh issue objects)")
     b = sub.add_parser("readback")
     b.add_argument("sha")
     b.add_argument("group")
     b.add_argument("file")
     a = p.parse_args(argv)
     if a.cmd == "run":
+        if a.first != "all" and (a.last is None or not a.first.isdigit()):
+            p.error("run needs FIRST LAST, or `all` with --mark")
         return run_queue(a)
+    if a.cmd == "loop":
+        return loop_queue(a)
+    if a.cmd == "release-held":
+        released, held = release_held(a.queue, a.edit_checkout)
+        for ln in released:
+            print("RELEASED", ln[len(HELD):][:100])
+        for ln in held:
+            print("held    ", ln[len(HELD):][:100])
+        return 0
+    if a.cmd == "unwired":
+        s_ = _git("show", f"{a.ref}:{ROSTER_REL}", cwd=a.edit_checkout)
+        if s_.returncode:
+            print(f"no {ROSTER_REL} at {a.ref}", file=sys.stderr)
+            return 2
+        nums = [x if isinstance(x, int) else x.get("number")
+                for x in json.loads(Path(a.open_issues).read_text())]
+        out = unwired(json.loads(s_.stdout), [n for n in nums if isinstance(n, int)])
+        print("\n".join(out) or "no unwired open issue")
+        return 1 if out else 0
     line, ok = readback(a.sha, a.group, a.file)
     print(line)
     return 0 if ok else 1

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
