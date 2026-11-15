#!/usr/bin/env python3
"""R10-FLOW-DISPATCH: each predicate of cloud_dispatch.py's group path dies alone.

Written by the R10-FLOW-DISPATCH fixer, round 2, after the round-1 review found
two survivors (head-ignored, privacy-off) that 42 green checks hid; round 3
added the four the round-2 review found (explicit-roster-ref-ignored,
cli-head-dropped, cli-roster-ref-dropped, fetch-skipped); round 4 added
the three the round-3 review found (cli-role-fixed, cli-pr-dropped,
cli-nonce-dropped) and the rest of the --group call's inputs (cli-group-fixed,
cli-model-fixed, cli-overlay-dropped); round 5 added the flag table's arms
(group-refusal-off, env-id-forwarded-as-none, flag-unlisted) and cli-pr-truncated;
R10-FLY-CACHE-PROMPTS re-aimed nonce-altered, topic-to-id, prompt-wrong and
flag-unlisted at the publish_seat path and added the pointer, --publish, wait-cap
and read-list arms (pointer-ref-dropped .. claude-md-reread). Each
mutant is a one-occurrence replacement in tools/audit/seat/cloud_dispatch.py
(or the roster_lib.py a fourth element names);
it is applied alone, `cloud_dispatch.py --self-test` run, and the file
restored byte for byte. The drive refuses a dirty file and aborts on a
pattern that is not found exactly once. Metric, one line per mutant:

  RESULT mutant=<name> failed=<n> verdict=killed|SURVIVED|CRASHED
  RESULT mutants=<n> survived=<n>

failed=-1 is a self-test that died before its summary line (CRASHED: it is
killed, but no check names what broke). Expected at the fixing head:
survived=0. Null control: M0, the file unmutated, must print failed=0.

    python3 dev/audit/harnesses/r10_flow_dispatch_mutants.py [NAME ...]
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
REL = "tools/audit/seat/cloud_dispatch.py"
#: The file a 4-tuple mutant names instead: roster_lib owns the brief's generated lines.
ROSTER_REL = "tools/audit/seat/roster_lib.py"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import mutant_guard  # noqa: E402 -- restores the mutated file on a kill (SIGTERM/SIGINT) and refuses a leftover mutant
F = ROOT / REL

MUTANTS = [
    ("M0", None, None),
    ("tree-skip", "    if tip and _git(repo_dir, \"rev-parse\"", "    if False and _git(repo_dir, \"rev-parse\""),
    ("brief-drop", 'brief=group_brief(group, roster, fixer=role == "fixer") +', 'brief="" +'),
    ("parent-drop", '*(["-p", tip] if tip else [])', "*[]"),
    ("nonce-altered", "**args, nonce=nonce)\n    except Refusal:", "**args, nonce=nonce + \"0\")\n    except Refusal:"),
    ("part-collision-off", "if other is not group and topic in (", "if False and topic in ("),
    ("topic-to-id", 'ref = dispatch_ref(role, topic, "")', 'ref = dispatch_ref(role, group_id, "")'),
    ("render-host-off", "    m = HOME.search(json.dumps(payload))", "    m = None"),
    ("privacy-off", "    if why:\n        raise Refusal(f\"the dispatch ref", "    if False:\n        raise Refusal(f\"the dispatch ref"),
    ("head-ignored", 'head or _git(repo_dir, "rev-parse", f"{HEAD_REF}', '_git(repo_dir, "rev-parse", f"{HEAD_REF}'),
    ("prompt-wrong", '"PAYLOAD.json": json.dumps(payload), "PROMPT.md": prompt}',
     '"PAYLOAD.json": json.dumps(payload), "PROMPT.md": ""}'),
    ("roster-repo-ignored", 'repo=roster.get("repo") or known["repo"]', 'repo=known["repo"]'),
    ("roster-ref-main", "roster_ref = roster_lib.reader_ref(repo_dir, roster_ref)",
     "roster_ref = roster_ref or roster_lib.MAIN_REF"),
    ("head-from-roster-ref", 'f"{HEAD_REF}^{{commit}}"', 'f"{roster_ref}^{{commit}}"'),
    ("reviewer-head-off", 'if role == "reviewer" and not head:', "if False:"),
    ("explicit-roster-ref-ignored", "roster_ref = roster_lib.reader_ref(repo_dir, roster_ref)",
     "roster_ref = roster_lib.reader_ref(repo_dir, None)"),
    ("cli-head-dropped", 'head=args.head or ""', 'head=""'),
    ("cli-roster-ref-dropped", "roster_ref=args.roster_ref,", "roster_ref=None,"),
    ("fetch-skipped", '        _git(repo_dir, "fetch", "-q", "origin", f"refs/heads/{ref}")', "        pass"),
    ("cli-role-fixed", "print(dispatch_group(args.role,", 'print(dispatch_group("fixer",'),
    ("cli-pr-dropped", 'head=args.head or "", pr=args.pr,', 'head=args.head or "", pr="",'),
    ("cli-nonce-dropped", "nonce=args.nonce, overlay=args.overlay,", 'nonce="", overlay=args.overlay,'),
    ("cli-group-fixed", "print(dispatch_group(args.role, args.group,", 'print(dispatch_group(args.role, "R10-X",'),
    ("cli-model-fixed", 'args.group, args.model or "", roster_ref', 'args.group, "m-1", roster_ref'),
    ("cli-overlay-dropped", "nonce=args.nonce, overlay=args.overlay,", "nonce=args.nonce, overlay=None,"),
    ("group-refusal-off", "if why and getattr(args, dest)", "if False and getattr(args, dest)"),
    ("env-id-forwarded-as-none", '"env_id": "the environment id', '"env_id": None and "the environment id'),
    ("flag-unlisted", '    ap.add_argument("--out")\n', '    ap.add_argument("--out")\n    ap.add_argument("--extra")\n'),
    # R10-FLY-CACHE-PROMPTS: the pointer event, --publish, the wait cap, the role read list.
    # R10-FLOW-DESIGN-STAGES part 2 re-aimed pointer-ref-dropped at the pinned stub: a
    # seat told to fetch the moving ref instead of the pinned commit must die.
    ("pointer-ref-dropped", "of {ref} (`git fetch origin {pin} && \"\n            f\"git show {pin}:PROMPT.md",
     "of {ref} (`git fetch origin {ref} && \"\n            f\"git show FETCH_HEAD:PROMPT.md"),
    ("pointer-off", "text = (_pointer(role, repo, pr, head, topic, nonce, publish_ref, pin) if publish_ref",
     "text = (_pointer(role, repo, pr, head, topic, nonce, publish_ref, pin) if False"),
    ("publish-ignored", "        if args.publish:", "        if False:"),
    ("publish-ref-rev-dropped", 'key = topic or (f"rev-{pr}"', 'key = topic or (f"{pr}"'),
    ("wait-line-dropped", 'Monitor and no timeout. " + WAIT_LINE)', 'Monitor and no timeout.")'),
    ("claude-md-reread", "roles/fixer.md from main, and follow it exactly",
     "roles/fixer.md and CLAUDE.md from main, and follow them exactly"),
    ("cli-pr-truncated", 'head=args.head or "", pr=args.pr,', "head=args.head or \"\", pr=(args.pr or '')[:1],"),
    # R10-REVIEW-DISPATCH-RESIDUE part 3 (topic r10-review-dispatch-residue-p3): Carry 13, the
    # five-carry refusal and --part (triage P551); Carry 8, every reviewer stop path pushes a
    # verdict (P437 C2); Carry 9, the frugal line; and the pins of Carries 2 and 3 already built.
    ("part-count", "PART_CARRIES = 5\n", "PART_CARRIES = 6\n"),
    ("part-refusal-off", '        if len(pending) <= PART_CARRIES:\n            return ""',
     '        if True:\n            return ""'),
    ("part-prefilter", 'len(group.get("carry") or []) > PART_CARRIES):', 'len(group.get("carry") or []) > 99):'),
    ("part-fold-off", "    if len(parts) > 1 and len(parts[-1]) <= PART_FOLD:", "    if False:"),
    ("part-fold-one", "len(parts[-1]) <= PART_FOLD:", "len(parts[-1]) < PART_FOLD:"),
    ("part-pending-raw", "roster_lib.pending_carries(group, legacy)", 'list(range(len(group.get("carry") or [])))'),
    ("part-topic-dropped", '            topic = f"{topic}-p{part}"\n', "            pass\n"),
    ("part-coll-topic-off", "topic in (_topic_of(other), roster_lib.norm_group(", 'topic in ("", roster_lib.norm_group('),
    ("part-coll-id-off", ', roster_lib.norm_group(str(other.get("group")))):', ', ""):'),
    ("part-coll-self-off", "if other is not group and topic in (", "if topic in ("),
    ("part-split-one", "    if len(parts) > 1 and len(parts[-1]) <= PART_FOLD:", "    if len(parts) >= 1 and len(parts[-1]) <= PART_FOLD:"),
    ("part-runs-skip", "for j in range(1, len(idx) + 1):", "for j in range(2, len(idx) + 1):"),
    ("part-cli-nogroup-open", '        if args.part:\n            raise Refusal("--part applies', '        if False:\n            raise Refusal("--part applies'),
    ("part-line-dropped", '(f"\\n{pline}\\n" if pline else "")', '""'),
    ("part-cli-dropped", "record_pr=args.record_pr, part=args.part))", "record_pr=args.record_pr, part=0))"),
    ("part-role-open", 'if part and role != "fixer":', "if False:"),
    ("part-range-off", "if not 1 <= part <= len(parts):", "if part < 1:"),
    ("part-small-open", '    if len(pending) <= PART_CARRIES:\n        raise Refusal(f"--part',
     '    if False:\n        raise Refusal(f"--part'),
    ("wait-bound-dropped", '"about 30 minutes of polling, stop waiting: put', '"a while, stop waiting: put'),
    ("ci-wait-dropped", 'blocked {head} ci-wait: <the last "', 'blocked {head} <the last "'),
    ("required-red-dropped", "`prelude`. A review_packet `required-red` signal does not stop you while classify prints ",
     "`prelude`. "),
    ("seat-refused-dropped", "pushes `Fix review: blocked {head} seat-refused: ", "pushes `Fix review: blocked {head} "),
    ("poll-end-dropped", 'never end your turn while "\n', 'end your turn while "\n'),
    ("readback-dropped", "`git ls-remote origin refs/heads/probe/{ref_key}-{nonce.strip()[:8]}`", "`git ls-remote origin`"),
    ("frugal-allowance-back", '\n               "frugal routing guard requires: when it refuses inline work',
     '\n               "frugal routing guard requires; at most 5 inline search operations per prompt; when it refuses inline work'),
    ("model-roster-ignored",
     'for field, val in ((f"model.{key}", table.get(key)), (f"{key}Model", group.get(f"{key}Model"))):',
     'for field, val in (("default", "opus"),):'),
    ("record-pr-opus", 'return LIGHT_REVIEW_MODEL, "carry-only review" if carry_only else "record-PR review"',
     'return (LIGHT_REVIEW_MODEL if carry_only else "opus"), "carry-only review" if carry_only else "record-PR review"'),
    ("done-filter-dropped", 'if n != group_id and (g.get("resume") or {}).get("stage") not in CARRY_CLOSED',
     "if n != group_id", ROSTER_REL),
    ("enum-line-dropped", '    if enum:\n        out.append(f"Class-enumeration', '    if False:\n        out.append(f"Class-enumeration',
     ROSTER_REL),
    ("fixer-guard-off", 'if role == "fixer" and (part or len', 'if (part or len'),
    ("readback-nonce", 'f"`git ls-remote origin refs/heads/probe/{ref_key}-{nonce.strip()[:8]}`, and push again',
     'f"`git ls-remote origin refs/heads/probe/{ref_key}-{nonce.strip()}`, and push again'),
    ("legacy-refusal-swallow", '        except roster_lib.RosterNotFound as e:\n            raise Refusal(str(e))\n        pline',
     '        except roster_lib.RosterNotFound as e:\n            pass\n        pline'),
]
SUMMARY = re.compile(r"cloud_dispatch self-test: (\d+) checks, (\d+) failed")


def run() -> tuple[int, list[str]]:
    r = subprocess.run([sys.executable, "-I", str(F), "--self-test"], capture_output=True, text=True, cwd=ROOT)
    m = SUMMARY.search(r.stdout)
    return (int(m.group(2)) if m else -1), [ln.strip() for ln in r.stdout.splitlines() if "FAIL" in ln]


def main(names: list[str]) -> int:
    mutant_guard.arm([REL, ROSTER_REL])
    origs = {rel: (ROOT / rel).read_text() for rel in (REL, ROSTER_REL)}
    survived = 0
    picked = [m for m in MUTANTS if not names or m[0] in names]
    try:
        for name, old, new, *where in picked:
            target = ROOT / (where[0] if where else REL)
            orig = origs[where[0] if where else REL]
            if old is not None:
                if orig.count(old) != 1:
                    print(f"abort: {name}'s pattern occurs {orig.count(old)} times")
                    return 2
                target.write_text(orig.replace(old, new))
            failed, fails = run()
            target.write_text(orig)
            if name == "M0":
                verdict = "null-ok" if failed == 0 else "NULL-FAILED"
            else:
                verdict = "killed" if failed > 0 else "CRASHED" if failed < 0 else "SURVIVED"
                survived += verdict == "SURVIVED"
            print(f"RESULT mutant={name} failed={failed} verdict={verdict}")
            for ln in fails:
                print(f"    {ln}")
    finally:
        for rel, text in origs.items():
            (ROOT / rel).write_text(text)
    print(f"RESULT mutants={sum(1 for m in picked if m[1] is not None)} survived={survived}")
    return 1 if survived else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
