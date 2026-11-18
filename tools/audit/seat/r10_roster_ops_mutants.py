#!/usr/bin/env python3
"""R10-ROSTER-OPS: every plant roster_edit.py's self-test must refuse.

Metric, one line per plant: `RESULT mutant=<name> rc=<rc> fails=<n>`, then the
failing check names. Each plant is one exact one-occurrence replacement in
tools/audit/seat/roster_edit.py, or in the file a three-part plant names
(`parts`); the driver applies it, runs that file's `--self-test`, and
restores it byte for byte. It refuses to start when any target differs from
HEAD, so a restore cannot overwrite work.
Expected: every plant rc=1 with fails>=1 -- a FAIL line, not a crash (a
crash is rc=1 with fails=0 and prints its tail).

Plants, one per refusal of the two ops and per round-trip property:
  A1-A5  set-after: unknown after-group, self-edge, repeated edge, cycle, and
         the cycle checked on the graph before the edit.
  A6     set-after's unknown target group (a silent write to a detached dict).
  A7     set-after on a no-op moves the key, so its bytes change.
  C1-C5  drop-carry: an absent carry, no match (silently drops entry 0), an
         ambiguous match (silently drops the first), a negative index (drops
         the last), a non-integer index (silently drops entry 0).
  C6     the last drop deletes the `carry` key (the byte round-trip
         regression; the live roster's empty shape is `"carry": []`).
  C7     drop-carry by index drops the neighbour.
  C8     drop-carry's unknown group.
  P1-P3  the argparse refusals: index and --match together, neither, and
         --match on another op.
  D1     the dump's indent, the byte round-trip itself.
  T1-T5  the triage gate (decision 0015): the uncited proposal arm, a
         non-ACCEPT verdict passing, a missing batch read as an empty one, the gate's call
         in write_roster, and added_texts blind to appended carries.
  K1-K9  the carry ledger (#2733): mark-carry's refusals (K1 a carry already
         marked, K2 an unknown mark, K3 implemented without a sha, K4 the
         whole moved arm, K5 a move to itself, K6 dismissed with no reason),
         set-stage bypassing the shared closing rule (K7), the cut-over not
         read (K8), and set-resume --field stage bypassing it (K9); a move
         to a closed group (K10), a value holding `]` (K11), and an
         unreadable cut-over read as no legacy by set-stage (K12).
  L1-L8  roster_lib's predicate, under roster_lib.py --self-test: marks
         ignored (L1), legacy ignored (L2), every group's carries legacy at
         the cut-over (L3), absorbed not closed (L4), closing never
         downgrades (L5), a mark read anywhere in the text (L6), a carry
         routed to a carries-open or refuted group (L7) or a sink (L8).
  Y1-Y5  roster_sync: the merge bypassing the shared rule (Y1), an
         unreadable cut-over read as no legacy (Y2), the write path's
         re-derive without the legacy set (Y3), apply_plan writing the
         stage without it (Y4), and the dry run's (Y5) projection without it,
         which names a same-pass Carry:'s refusal. Y6, the write path's
         projection without it, is retired as equivalent: since
         R10-CARRY-SINK-BARRIER both stages it chooses between (done,
         carries-open) refuse the carry, and the write path drops the
         refusal text, so no output moves.
  R1-R5  carry_audit's roster arm: closed-only issues unreported (R1),
         unlisted issues unreported (R2), a record issue reported (R3), absorbed_into
         unnamed (R4), pull requests read as issues (R5).
  S1-S7  the vocabulary barrier (R10-ORCH-ROSTER-SCHEMA): each of the three
         stage-writing ops losing its classification check (S1 set-stage, S2
         set-resume --field stage, S3 append-group), append-group losing the
         size check (S4), the registry itself letting any word through (S5
         stage, S6 size), and apply_op dropping the threaded vocabulary, so a
         legal size is refused (S7 -- the barrier becoming a blanket one).
  H1-H2  the done hold (R10-RCA-ROSTER-SYNC-ORPHANS): a closed stage written
         though its group would orphan an open issue (H1), and the
         set-resume --field stage door left unheld (H2).

    W1-W15 the write-sweep arms (R10-ROSTER-WRITE-SWEEP): the lettered
           proposal label unmatched (W1), append-group's `@` strip dropped
           (W2), the overlap test skipping the not-started stage (W3), the
           --reason escape always open (W4), the index exemption dropped (W5),
           append-carry's closing refusal (W6), the open-PR WARN (W7) and the
           absorbed_into naming (W8) lost, set-resume's pr field (W9), a stale
           note kept (W10), the privacy gate not called (W11), absorbed --into
           naming no live group (W12, W13) or needing none (W14), and a phase
           branch unresolved in roster_lib.group_for_branch (W15).

    W18 append-carry's refusal of text already ending in a mark.
    U1-U6 orchestrator_tick's roster_invariants never reads an unreadable
           tool as clean: the guard dropped (U1), its rc arm (U2) or its
           summary arm (U3) alone, the OSError branch silent (U4) or not
           catching at all (U5), and a non-JSON issue list still passing
           --open-issues (U6).
    W16-W17 the lane marker on structural ops (carry 15): the guard dropped
           (W16) and set-stage wrongly made structural (W17); Q13 is the
           queue runner not setting it.

    Q1-Q12 roster_queue.py's own self-test: the plain shlex.split line grammar
           (a trailing comment reaches the editor, Q1), the run-start snapshot
           written over a line appended since (Q2), a flag folded into the
           value (Q3), a held line released with its batch file absent (Q4),
           marking the wrong line (Q5), `all` run without --mark (Q6) and no
           lint-clone self-heal in `loop` (Q7), the batch path resolving its
           editor from the edit checkout, not the one `run` executes (Q8),
           a file that is no roster_edit executed by the batch loader (Q9), and
           the read-only `diff` blind to removed groups (Q10), to a replaced
           carry of equal count (Q11), and `show --stage` unfiltered (Q12).

    python3 tools/audit/seat/r10_roster_ops_mutants.py [plant ...]
    python3 tools/audit/seat/r10_roster_ops_mutants.py --null
    python3 tools/audit/seat/r10_roster_ops_mutants.py --self-test

Null control: `--null` runs the self-test with no plant, which must print
rc=0 fails=0. `--self-test` does not run the plants -- one costs the target's
own minute -- and pins instead the preconditions the sweep rests on: every
anchor occurs exactly once in the target as it stands, every mutant parses,
and report()/select() keep their shapes.
"""
import contextlib
import io
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TARGET = "tools/audit/seat/roster_edit.py"
DROP = '    del g["carry"][_carry_index(g, index, match, "drop-carry")]\n'
RQ = "tools/audit/seat/roster_queue.py"
LIB, SYNC, AUDIT = ("tools/audit/seat/roster_lib.py",
                    "tools/audit/seat/roster_sync.py", "tools/audit/carry_audit.py")
_MARK_LINE = next((ln for ln in (ROOT / LIB).read_text().splitlines()
                   if ln.startswith("_CARRY_MARK = ")), "_CARRY_MARK missing")
TICK = "tools/audit/seat/orchestrator_tick.py"
RI_UNREAD = '            self.unreadable(S, "roster invariants"'
DETACHED = ('g = next((x for x in roster.get("groups", []) '
            'if x.get("group") == group), {})')

PLANTS = {
    "A1": ('    if bad:\n        raise Refuse(f"set-after: {group} after names',
           '    if False:\n        raise Refuse(f"set-after: {group} after names'),
    "A2": ("    if group in after:\n", "    if False:\n"),
    "A3": ("    if dup:\n", "    if False:\n"),
    "A4": ("    if cycle:\n", "    if False:\n"),
    "A5": ("    edges[group] = after\n", ""),
    "A6": ('    g = _need(roster, group)\n    after = [] if spec',
           f'    {DETACHED}\n    after = [] if spec'),
    "A7": ('    g["after"] = after\n',
           '    g.pop("after", None)\n    g["after"] = after\n'),
    "C1": ('    if not carry:\n        raise Refuse(f"{op}: {group} carries nothing")',
           '    if False:\n        raise Refuse(f"{op}: {group} carries nothing")'),
    "C2": ("if match in c]\n", "if match in c] or [0]\n"),
    "C3": ("        if len(hits) > 1:\n", "        if False:\n"),
    "C4": ("    if not 0 <= i < len(carry):\n",
           "    if not i < len(carry):\n"),
    "C5": ("        i = int(index)\n",
           '        i = int(index) if index.lstrip("-").isdigit() else 0\n'),
    "C6": (DROP, DROP + '    if not g["carry"]:\n        del g["carry"]\n'),
    "C7": (DROP, DROP.replace(')]', ') - 1]')),
    "C8": ('    g = _need(roster, group)\n    del g["carry"]',
           f'    {DETACHED}\n    g.setdefault("carry", [])\n    del g["carry"]'),
    "P1": ('p.error("drop-carry takes an index or --match, not both")', "pass"),
    "P2": ('p.error(f"{a.op} needs an index or --match")', "pass"),
    "P3": ('p.error("--match is a drop-carry flag")', "pass"),
    "D1": ("return json.dumps(roster, indent=1)",
           "return json.dumps(roster, indent=2)"),
    "T1": ("        if PROPOSAL_RE.search(text) and not cites:\n",
           "        if False:\n"),
    "T2": ('            if verdict != "ACCEPT":\n',
           "            if verdict is None:\n"),
    "T3": ("        return r.stdout if r.returncode == 0 else None\n",
           '        return r.stdout if r.returncode == 0 else ""\n'),
    "T4": ("        if why:\n            raise Refuse(f\"triage gate: {why}; nothing written\")\n", ""),
    "T5": ("        out += [c for c in carry if c not in held]\n", ""),
    "S1": ('    why = _stage_why(stage, rel, group)\n    if why:\n        raise Refuse(why)\n',
           '    why = None  # S1\n    if why:\n        raise Refuse(why)\n'),
    "S2": ('        why = _stage_why(value, rel, group)\n        if why:\n            raise Refuse(why)\n',
           '        why = None  # S2\n        if why:\n            raise Refuse(why)\n'),
    "S3": ('    if stage is not None:\n        why = _stage_why(stage, rel, gid)\n',
           '    if False:  # S3\n        why = _stage_why(stage, rel, gid)\n'),
    "S4": ('    why = _size_why(new.get("size"), sizes, rel, gid)\n    if why:\n'
           '        raise Refuse(f"append-group: {why}")\n',
           '    why = None  # S4\n    if why:\n'
           '        raise Refuse(f"append-group: {why}")\n'),
    "S5": ("    if stage in roster_lib.STAGES:\n        return None\n",
           "    if True:  # S5\n        return None\n"),
    "S6": ("    if size is None or size in sizes:\n        return None\n",
           "    if True:  # S6\n        return None\n"),
    "S7": ("        op_append_group(roster, value, rel, sizes, reason)\n",
           "        op_append_group(roster, value, reason=reason)  # S7\n"),
    "K1": ('    if roster_lib.carry_mark(g["carry"][i]):\n', "    if False:  # K1\n"),
    "K2": ("    if kind not in roster_lib.CARRY_MARKS:\n", "    if False:  # K2\n"),
    "K3": ('    if kind == "implemented" and not SHA_RE.match(arg):\n',
           "    if False:  # K3\n"),
    "K4": ('    if kind == "moved":\n', "    if False:  # K4\n"),
    "K5": ("        if arg == group:\n", "        if False:  # K5\n"),
    "K6": ('    if kind == "dismissed" and not arg:\n', "    if False:  # K6\n"),
    "K7": ('["stage"] = _closing(g, stage, legacy, "set-stage")\n',
           '["stage"] = stage  # K7\n'),
    "K8": ("                legacy = roster_lib.read_legacy(a.worktree, rel)\n",
           "                legacy = {}  # K8\n"),
    "K9": ('        value = _closing(g, value, legacy, "set-resume")\n',
           "        pass  # K9\n"),
    "K10": ("        if not roster_lib.carry_receivable(dest):\n",
            "        if False:  # K10\n"),
    "K11": ('    if "]" in arg:\n', "    if False:  # K11\n"),
    "K12": ('raise Refuse(f"the carry cut-over is unreadable, so no "\n'
            '                             f"stage is written: {e}")',
            "legacy = {}  # K12"),
    "L1": (LIB, "            if carry_mark(c) is None and c not in held]\n",
           "            if c not in held]  # L1\n"),
    "L2": (LIB, "            if carry_mark(c) is None and c not in held]\n",
           "            if carry_mark(c) is None]  # L2\n"),
    "L3": (LIB, '            if (g.get("resume") or {}).get("stage") in CARRY_CLOSED}\n',
           "            }  # L3\n"),
    "L4": (LIB, 'CARRY_CLOSED = CLOSED_STAGES\n',
           "CARRY_CLOSED = DONE_STAGES  # L4\n"),
    "L5": (LIB, '    return ("carries-open" if pending else "done"), pending\n',
           '    return "done", pending  # L5\n'),
    # L6 reads the mark's grammar from roster_lib's own line: a second
    # spelling of it here would be the grammar written twice (agreement.mjs).
    "L6": (LIB, _MARK_LINE, _MARK_LINE.replace('\\Z")', '")') + "  # L6"),
    "L7": (LIB, 'CARRY_DEST_CLOSED = CARRY_CLOSED + ("carries-open", "refuted")\n',
           "CARRY_DEST_CLOSED = CARRY_CLOSED  # L7\n"),
    "L8": (LIB, '    return res.get("stage") not in CARRY_DEST_CLOSED and not sink\n',
           '    return res.get("stage") not in CARRY_DEST_CLOSED  # L8\n'),
    "Y1": (SYNC, '        closed, _ = roster_lib.closing_stage(g, "done", legacy or {})\n',
           '        closed = "done"  # Y1\n'),
    "Y2": (SYNC, '            raise Refuse(f"the carry cut-over is unreadable: {e}")\n',
           "            legacy = {}  # Y2\n"),
    "Y3": (SYNC, "            changes, _, transitions = derive(roster, prs, legacy)\n",
           "            changes, _, transitions = derive(roster, prs)  # Y3\n"),
    "Y4": (SYNC, "        roster_edit.op_set_stage(roster, c.group, c.stage, c.merge_commit,\n"
                 "                                 legacy=legacy)\n",
           "        roster_edit.op_set_stage(roster, c.group, c.stage, c.merge_commit)"
           "  # Y4\n"),
    "Y5": (SYNC, "        apply_plan(projected, changes, [], legacy)\n        appends, refusals",
           "        apply_plan(projected, changes, [])  # Y5\n        appends, refusals"),
    "R1": (AUDIT, "        elif not any(live for _, live in by):\n",
           "        elif False:  # R1\n"),
    "R2": (AUDIT, "        if not by:\n", "        if False:  # R2\n"),
    "R3": (AUDIT, "    for n in sorted(open_issues - log_issues()):\n",
           "    for n in sorted(open_issues):  # R3\n"),
    "R4": (AUDIT, '        where = f"absorbed into {into}" if stage == "absorbed" and into else stage\n',
           "        where = stage  # R4\n"),
    "R5": (AUDIT, '        elif isinstance(x, dict) and "pull_request" not in x and isinstance(x.get("number"), int):\n',
           '        elif isinstance(x, dict) and isinstance(x.get("number"), int):  # R5\n'),
    "H1": ("    if held:\n        g[\"resume\"][\"stage\"] = HOLD_STAGE\n",
           "    if False:  # H1\n        g[\"resume\"][\"stage\"] = HOLD_STAGE\n"),
    "H2": ('        if closed or a.op == "set-stage" or (a.op == "set-resume" and a.field == "stage"):\n',
           '        if closed or a.op == "set-stage":  # H2\n'),
}


# --- R10-ROSTER-OPS-2 part 1: set-size and set-files. A SEPARATE block, merged
# into PLANTS here so it neither edits the table above nor the docstring.
#   Z1-Z4   set-size: the _size_why check skipped, the cite check skipped, the
#           size write dropped, and the no-op case writing a note (null control).
#   Z5-Z9   set-files: the path-in-tree refusal skipped, the files write
#           dropped, the hot_files write dropped, the hot-token refusal
#           skipped, the cite check skipped.
#   Z10     set-files' unknown group (a silent write to a detached dict).
#   Z11     the dispatch dropping the cite, so set-size never checks it.
#   Z12     set-files writing hot_files on a call that never named it.
#   R11     cite_why's merge-base --is-ancestor clause dropped, so a ref holds
#           any commit that exists (the fix review's survivor of #3143).
CITE_GUARD = ("    if cite is not None and cite_check:\n"
              "        why = cite_check(cite)\n        if why:\n"
              "            raise Refuse(f\"{op}: {why}\")\n")
PLANTS.update({
    "Z1": ('    why = _size_why(size, sizes, rel, group)\n    if why:\n'
           '        raise Refuse(f"set-size: {why}")\n',
           '    why = None  # Z1\n    if why:\n'
           '        raise Refuse(f"set-size: {why}")\n'),
    "Z2": (CITE_GUARD.replace("{op}", "set-size"),
           CITE_GUARD.replace("{op}", "set-size").replace(
               "if cite is not None and cite_check:", "if False:  # Z2")),
    "Z3": ('    g["size"] = size\n', ""),
    "Z4": ("    if old == size:\n        return\n", ""),
    "Z5": ("        if p not in old_files and in_tree and not in_tree(p, cite):\n",
           "        if False:  # Z5\n"),
    "Z6": ('        g["files"] = files\n', ""),
    "Z7": ('        g["hot_files"] = hot\n', ""),
    "Z8": ("        if bad:\n            raise Refuse(f\"set-files: hot_files token",
           "        if False:  # Z8\n            raise Refuse(f\"set-files: hot_files token"),
    "Z9": (CITE_GUARD.replace("{op}", "set-files"),
           CITE_GUARD.replace("{op}", "set-files").replace(
               "if cite is not None and cite_check:", "if False:  # Z9")),
    "Z10": ("    g = _need(roster, group)\n    if not add and set_files",
            f"    {DETACHED}\n    if not add and set_files"),
    "Z11": ("op_set_size(roster, a.group, value, sizes, rel, a.cite, cite_check)",
            "op_set_size(roster, a.group, value, sizes, rel, None, cite_check)"),
    "Z12": ("    if hot != old_hot:\n", "    if True:  # Z12\n"),
    "R11": ('                    and _git_ok(checkout, "merge-base", "--is-ancestor",\n'
            '                                sha, cand):\n',
            '                    and True:  # R11\n'),
    "W1": ('LABEL = r"P(?:\\d+|-[A-Q])\\b"', 'LABEL = r"P\\d+\\b"'),
    "W2": ('    if json_file.startswith("@"):\n        json_file = json_file[1:]\n', ""),
    "W3": ('        if (g.get("resume") or {}).get("stage") != "not-started":\n            continue\n', ""),
    "W4": ('    if clash and not (reason or "").strip():\n', "    if clash and reason is None:\n"),
    "W5": ('if not _is_index(f)}', "}"),
    "W6": ("    if not roster_lib.carry_receivable(g):\n        into = resume.get",
           "    if False:\n        into = resume.get"),
    "W7": ('    if resume.get("pr"):\n        print(f"WARN', '    if False:\n        print(f"WARN'),
    "W8": ('if stage == "absorbed" and into else', "if False else"),
    "W9": ('"note", "pr")', '"note")'),
    "W10": ("            and OWED_NOTE_RE.search(note):\n", "            and not OWED_NOTE_RE.search(note):\n"),
    "W11": ('        why = privacy_refusal(added_texts(before, roster) + added_resume(before, roster))\n'
            '        if why:\n            raise Refuse(f"privacy gate: {why}; nothing written")\n', ""),
    "W12": ('    if not roster_lib.carry_receivable(host):\n', "    if False:\n"),
    "W13": ('    if into == group:\n        raise Refuse(f"set-stage: {group} cannot be absorbed',
            '    if False:\n        raise Refuse(f"set-stage: {group} cannot be absorbed'),
    "W14": ('    if not into:\n        raise Refuse(f"set-stage: {group} absorbed needs',
            '    if False:\n        raise Refuse(f"set-stage: {group} absorbed needs'),
    "W15": (LIB, "    if phase != tail:  # handoff", "    if False:  # handoff"),
    "Q1": (RQ, "    t = _split(ln)\n", "    t = shlex.split(ln)\n"),
    "Q2": (RQ, '            mark_line(a.queue, ln, "done" if ok else "refused")\n',
           '            Path(a.queue).write_text("\\n".join((("#done " if ok else "#refused ") + x) if x == ln else x for x in qlines))\n'),
    "Q3": (RQ, 'return t[0], t[1], (rest[0] if rest else ""), rest[1:]',
           'return t[0], t[1], " ".join(rest), []'),
    "Q4": (RQ, "        if files and all(_git(", "        if True or all(_git("),
    "Q5": (RQ, "        if x == old:\n", "        if x.strip() == old.strip() or True:\n"),
    "Q6": (RQ, "    if allq and not mark:\n", "    if False:\n"),
    "Q7": (RQ, "    if Path(a.lint_clone).is_dir():\n        return False\n",
           "    if True:\n        return False\n"),
    "Q8": (RQ, "        re_ = load_editor(editor)\n",
           '        re_ = load_editor(str(Path(a.edit_checkout, "tools/audit/seat/roster_edit.py")))\n'),
    "Q10": (RQ, "    out = [f\"- {g}\" for g in ga if g not in gb] + ",
            "    out = [] + "),
    "Q11": (RQ, "                out += [f\"~ {g} carry -{_short(c, 90)}\" for c in ca if c not in cb]\n"
                "                out += [f\"~ {g} carry +{_short(c, 90)}\" for c in cb if c not in ca]\n",
            "                if len(ca) != len(cb):\n"
            "                    out.append(f\"~ {g} carry +{len(cb) - len(ca)}\")\n"),
    "Q12": (RQ, "        if stage and r.get(\"stage\") != stage:\n", "        if False:\n"),
    "W16": ("    if op in STRUCTURAL_OPS and os.environ.get(LANE_ENV) != LANE_VALUE:\n",
            "    if False:\n"),
    "W17": ('STRUCTURAL_OPS = ("wire-issue",', 'STRUCTURAL_OPS = ("set-stage", "wire-issue",'),
    "W18": ("    if mark:\n        raise Refuse(f\"append-carry: the text already ends",
            "    if False:\n        raise Refuse(f\"append-carry: the text already ends"),
    "Q13": (RQ, '    env["HPO_ROSTER_LANE"] = "queue-runner"', '    env["HPO_ROSTER_LANE"] = "x"'),
    "Q9": (RQ, '    if "def batch_edit" not in Path(path).read_text():\n',
           '    if False:\n'),
    "U1": (TICK, f"        if rc not in (0, 1) or not summary:\n{RI_UNREAD}",
           f"        if False:\n{RI_UNREAD}"),
    "U2": (TICK, f"        if rc not in (0, 1) or not summary:\n{RI_UNREAD}",
           f"        if not summary:\n{RI_UNREAD}"),
    "U3": (TICK, f"        if rc not in (0, 1) or not summary:\n{RI_UNREAD}",
           f"        if rc not in (0, 1):\n{RI_UNREAD}"),
    "U4": (TICK, f"        except OSError as e:\n{RI_UNREAD}, str(e)[:80])\n            return\n",
           "        except OSError as e:\n            return\n"),
    "U5": (TICK, f"        except OSError as e:\n{RI_UNREAD}, str(e)[:80])\n            return\n",
           "        except ZeroDivisionError:\n            return\n"),
    "U6": (TICK, "            except ValueError:\n                pass\n        try:\n            rc, out = self.carry_run(argv)\n",
           '            except ValueError:\n                argv += ["--open-issues", "x"]\n        try:\n            rc, out = self.carry_run(argv)\n'),
})


def parts(name):
    """(target, old, new) of a plant: roster_edit.py unless the plant names
    its file. Every target is a Python tool whose `--self-test` prints FAIL
    lines, so one driver reads them all."""
    plant = PLANTS[name]
    return plant if len(plant) == 3 else (TARGET,) + plant


def fail_lines(stdout):
    """A target's FAIL lines, indented or not: orchestrator_tick prints
    `  FAIL <check>`, roster_edit `FAIL <check>`."""
    return [ln.strip() for ln in stdout.splitlines() if ln.lstrip().startswith("FAIL ")]


def target_self_test(target=TARGET):
    r = subprocess.run([sys.executable, "-I", target, "--self-test"], cwd=ROOT,
                       capture_output=True, text=True)
    fails = fail_lines(r.stdout)
    return r.returncode, fails, (r.stdout + r.stderr).strip().splitlines()[-3:]


def report(name, rc, fails, tail):
    print(f"RESULT mutant={name} rc={rc} fails={len(fails)}")
    for f in fails:
        print("   ", re.sub(r" \(got: .*\)$", "", f))
    if rc and not fails:
        print("    crash tail:", *tail, sep="\n      ")


def select(names):
    """The plants a run names, and any name the table does not hold."""
    chosen = names or list(PLANTS)
    return chosen, [n for n in chosen if n not in PLANTS]


def self_test():
    passed = failed = 0

    def ck(name, ok):
        nonlocal passed, failed
        passed, failed = passed + ok, failed + (not ok)
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")

    for name in PLANTS:
        target, old, new = parts(name)
        text = (ROOT / target).read_text()
        ck(f"{name}: anchor occurs once in {target}", text.count(old) == 1)
        ck(f"{name}: the plant changes the text", new != old)
        try:
            compile(text.replace(old, new), target, "exec")
            ok = True
        except SyntaxError:
            ok = False
        ck(f"{name}: the mutant parses", ok)

    def rendered(rc, fails, tail):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            report("X", rc, fails, tail)
        return out.getvalue().splitlines()

    ck("a killed plant prints its tally and drops the (got:) suffix",
       rendered(1, ["FAIL a (got: 2)"], [])
       == ["RESULT mutant=X rc=1 fails=1", "    FAIL a"])
    ck("a crash with no FAIL line prints its tail",
       rendered(1, [], ["Traceback", "boom"])
       == ["RESULT mutant=X rc=1 fails=0", "    crash tail:",
           "      Traceback", "      boom"])
    ck("a survivor prints fails=0 and no tail",
       rendered(0, [], ["x"]) == ["RESULT mutant=X rc=0 fails=0"])
    ck("an indented FAIL line is read; an ok line naming FAIL is not",
       fail_lines("  FAIL a\nFAIL b\n  ok   FAIL-free c\n") == ["FAIL a", "FAIL b"])
    ck("no names selects every plant", select([]) == (list(PLANTS), []))
    ck("a named plant is kept", select(["A1"]) == (["A1"], []))
    ck("an unknown plant is returned for refusal",
       select(["ZZ"]) == (["ZZ"], ["ZZ"]))

    print(f"r10_roster_ops_mutants self-test: {passed + failed} checks, "
          f"{failed} failed")
    return 1 if failed else 0


def main(argv):
    if argv == ["--self-test"]:
        return self_test()
    targets = sorted({parts(n)[0] for n in PLANTS})
    if subprocess.run(["git", "diff", "--quiet", "HEAD", "--", *targets],
                      cwd=ROOT).returncode != 0:
        print(f"refusing: one of {targets} differs from HEAD", file=sys.stderr)
        return 2
    if argv == ["--null"]:
        for target in targets:
            report(f"null {target}", *target_self_test(target))
        return 0
    names, unknown = select(argv)
    if unknown:
        print(f"unknown plant(s): {unknown}", file=sys.stderr)
        return 2
    originals = {t: (ROOT / t).read_bytes() for t in targets}
    survivors = []
    try:
        for name in names:
            target, old, new = parts(name)
            path, original = ROOT / target, originals[target]
            text = original.decode("utf-8")
            if text.count(old) != 1:
                print(f"plant {name}: anchor occurs {text.count(old)} times",
                      file=sys.stderr)
                return 2
            path.write_bytes(text.replace(old, new).encode("utf-8"))
            rc, fails, tail = target_self_test(target)
            path.write_bytes(original)
            report(name, rc, fails, tail)
            if not fails:
                survivors.append(name)
    finally:
        for target, original in originals.items():
            (ROOT / target).write_bytes(original)
    print(f"plants: {len(names)}, without a FAIL line: {survivors or 'none'}")
    return 1 if survivors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
