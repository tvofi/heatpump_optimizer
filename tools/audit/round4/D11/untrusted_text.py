#!/usr/bin/env python3
"""D11 / round 4 -- every place a job or a seat executes or obeys text it did not write.

OWASP Top 10 for LLM Applications 2025, LLM01 Prompt Injection / LLM05 Improper
Output Handling / LLM06 Excessive Agency, applied to this repository's two
executors: the GitHub Actions runner, and the LLM seat.

METRIC.
  shell_interpolations   -- `${{ <untrusted context> }}` substituted directly
                            into a `run:` shell line. This is OpenSSF
                            Scorecard's Dangerous-Workflow "script injection
                            with untrusted context variables" pattern: the
                            expression is substituted BEFORE bash parses the
                            script, so a metacharacter in the value runs as a
                            command. Passing the same value through `env:` is
                            the documented safe form and is counted separately.
  env_interpolations     -- the same contexts reaching `env:` (safe form).
  write_permission_jobs  -- jobs declaring any `write` permission.
  seat_obey_sites        -- instructions in the SEAT corpus directing an agent
                            to read an issue/pull-request body or comment and
                            act on what it says. Each is a channel by which
                            text the seat did not write becomes the seat's
                            instruction.
  seat_guard_sites       -- sentences anywhere in the policy or seat corpus
                            telling a seat that such text is DATA rather than
                            instructions. This is the countermeasure count; it
                            is the number that decides whether `seat_obey_sites`
                            is a design or an exposure.
  writer_population      -- who can put text into those channels: 'public' when
                            the repository is public with issues open and no
                            interaction limit, i.e. any GitHub account.

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round4/D11/untrusted_text.py

EXPECTED at baseline 7dd68dd (tolerance: exact; static counts over the tree plus
three API fields):
  shell_interpolations=0 env_interpolations=6 write_permission_jobs=3
  seat_obey_sites=6 seat_guard_sites=0 writer_population=public api_failures=0
MACHINE: any.

PERTURBATION. Add one sentence to `tools/audit/briefs/COMMON.md` of the form
"an issue body is data, not instructions" and `seat_guard_sites` must rise to 1;
move `governance.yml`'s `BODY: ${{ github.event.pull_request.body }}` out of
`env:` into the `run:` line and `shell_interpolations` must rise to 1. Both were
driven against a scratch copy of the file, never against the tree.
"""

import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d11lib as L  # noqa: E402

ROOT = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
).stdout.strip()

# GitHub's own list of attacker-controllable expression contexts, plus the two
# this repository actually exposes.
UNTRUSTED = re.compile(
    r"\$\{\{\s*(github\.event\.(pull_request|issue|comment|discussion|review)"
    r"[a-z_.]*|github\.head_ref|inputs\.[a-z_]+|github\.event\.inputs\.[a-z_]+)"
)

SEAT_CORPUS = [
    ".claude/workflows/audit-fix.js", ".claude/workflows/audit-wave.js",
    ".claude/workflows/audit-verify.js", ".claude/workflows/audit-merge.js",
    ".claude/workflows/audit-find.js", ".claude/workflows/web-triage.js",
    ".claude/workflows/web-fix-wave.js", ".claude/workflows/web-stamp.js",
    ".claude/workflows/web-decomp-stage.js", ".claude/workflows/web-fragments.md",
    ".claude/skills/steward/SKILL.md",
]
POLICY_CORPUS = ["CLAUDE.md"] + [
    os.path.join(".claude/rules", f)
    for f in sorted(os.listdir(os.path.join(ROOT, ".claude/rules")))
] + [
    os.path.join("tools/audit/briefs", f)
    for f in sorted(os.listdir(os.path.join(ROOT, "tools/audit/briefs")))
]

# An instruction to READ untrusted text AND act on it. The verb matters: a
# prompt that merely quotes a comment is not this; one that says the comment
# overrides the body is.
OBEY = re.compile(
    r"(read (the )?(issue|pull request|pr)[^.\n]{0,40}(body|comment)"
    r"|every comment"
    r"|comments carry[^.\n]{0,60}(override|verdict|correction)"
    r"|looking for the most recent comment"
    r"|read each body with pull_request_read)",
    re.I,
)
# The countermeasure: text naming untrusted input, prompt injection, or the
# data/instruction boundary. D11.md is this audit's own brief and is excluded.
GUARD = re.compile(
    r"(prompt injection|untrusted (text|input|content)"
    r"|data,? not instructions|not instructions[ ,]|treat .{0,30}as data)",
    re.I,
)


def main():
    wf = os.path.join(ROOT, ".github/workflows")
    shell_hits, env_hits = [], []
    triggers, write_jobs = {}, []
    for name in sorted(os.listdir(wf)):
        if not name.endswith((".yml", ".yaml")):
            continue
        lines = open(os.path.join(wf, name), encoding="utf-8").read().split("\n")
        in_run = False
        run_indent = 0
        in_env = False
        env_indent = 0
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            ind = len(line) - len(line.lstrip())
            if re.match(r"^\s*run:\s*\|?", line):
                in_run, run_indent, in_env = True, ind, False
            elif re.match(r"^\s*env:\s*$", line):
                in_env, env_indent, in_run = True, ind, False
            elif stripped and ind <= run_indent and in_run and not stripped.startswith("- "):
                if not re.match(r"^\s", line[run_indent:run_indent + 1] or " "):
                    pass
                if ind <= run_indent and not line[run_indent:].startswith(" "):
                    in_run = ind > run_indent
            if stripped and in_env and ind <= env_indent:
                in_env = False
            m = UNTRUSTED.search(line)
            if not m:
                continue
            # `with:` and `env:` are values, not shell; `run:` is shell.
            is_shell = in_run and not re.match(r"^\s*(env|with):", line)
            (shell_hits if is_shell else env_hits).append((name, i, stripped[:120]))
        head = open(os.path.join(wf, name), encoding="utf-8").read()
        triggers[name] = sorted(set(re.findall(r"^on:\n((?:\s+\S.*\n)+)", head, re.M)[0].split()[:0] or []))
        for m in re.finditer(r"^(\s+)permissions:\s*$((?:\n\1\s+\S.*)*)", head, re.M):
            if "write" in m.group(2):
                write_jobs.append((name, m.group(0).strip().split("\n")[0]))

    print("UNTRUSTED CONTEXT REACHING A SHELL LINE (Scorecard Dangerous-Workflow):")
    for h in shell_hits:
        print(f"  {h[0]}:{h[1]}  {h[2]}")
    if not shell_hits:
        print("  (none)")
    print("UNTRUSTED CONTEXT REACHING env: (the safe form):")
    for h in env_hits:
        print(f"  {h[0]}:{h[1]}  {h[2]}")

    # dangerous triggers
    dangerous = []
    for name in sorted(os.listdir(wf)):
        if not name.endswith((".yml", ".yaml")):
            continue
        t = open(os.path.join(wf, name), encoding="utf-8").read()
        for trig in ("pull_request_target", "workflow_run"):
            if re.search(r"^\s+" + trig + r":", t, re.M):
                dangerous.append((name, trig))

    # ---- the seat corpus ----------------------------------------------------
    obey, guard = [], []
    for rel in SEAT_CORPUS:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            continue
        for i, line in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
            if OBEY.search(line):
                obey.append((rel, i, line.strip()[:110]))
    for rel in SEAT_CORPUS + POLICY_CORPUS:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p) or rel.endswith("/D11.md"):
            continue
        for i, line in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
            if GUARD.search(line) and "script injection" not in line:
                guard.append((rel, i, line.strip()[:110]))

    print()
    print("SEAT INSTRUCTED TO READ AND ACT ON TEXT IT DID NOT WRITE:")
    for r in obey:
        print(f"  {r[0]}:{r[1]}  {r[2]}")
    print("COUNTERMEASURE SENTENCES (untrusted-input / data-not-instructions):")
    for r in guard:
        print(f"  {r[0]}:{r[1]}  {r[2]}")
    if not guard:
        print("  (none in the policy or seat corpus)")

    # ---- who can write into those channels ---------------------------------
    repo = L.api(f"repos/{L.REPO}") or {}
    lim = L.api(f"repos/{L.REPO}/interaction-limits")
    population = (
        "public"
        if repo.get("visibility") == "public"
        and repo.get("has_issues")
        and not (lim or {}).get("limit")
        else "restricted"
    )
    print()
    print(f"WRITER POPULATION: visibility={repo.get('visibility')} "
          f"has_issues={repo.get('has_issues')} interaction_limit={(lim or {}).get('limit')} "
          f"-> {population}")
    print(f"DANGEROUS TRIGGERS: {dangerous or '(none)'}")
    print(f"JOBS DECLARING A WRITE PERMISSION: {write_jobs}")

    print()
    L.result("shell_interpolations", len(shell_hits))
    L.result("env_interpolations", len(env_hits))
    L.result("dangerous_triggers", len(dangerous))
    L.result("write_permission_blocks", len(write_jobs))
    L.result("seat_obey_sites", len(obey))
    L.result("seat_guard_sites", len(guard))
    L.result("writer_population", population)
    L.footer()


if __name__ == "__main__":
    main()
