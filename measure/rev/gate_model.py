"""The gate predicate of DESIGN-P2.md section 4.1, revision 1: the reference
implementation `tools/ci/gate.py` ports, line for line, and the function
`gate_replay2.py` replays (review item 10). Pure: every input is passed in.

Nothing here is taken on the prelude's word. Applicability comes from the event
(`github.event_name`, `github.event.action`, `github.event.changes.base`, the
dispatch inputs); the prelude must have SUCCEEDED and its `kind`/`pr` outputs must
EQUAL what the gate derives itself (review item 2). A past run's kind is read from
its `display_title`, which `run-name:` sets when the run is CREATED, so a run
cancelled before any job started still says what it was (review item 2).
"""
from __future__ import annotations

CODE = {
    "tests": ["fast (3.14)", "browser", "briefs", "typing", "mutation", "closures", "closure-scope"],
    "codeql": ["Analyze (actions)", "Analyze (javascript-typescript)", "Analyze (python)"],
    "governance": ["policy-docs", "wave-script", "env-matrix"],
    "hassfest": ["hassfest"],
    "validate": ["validate-hacs"],
}
BODY = {
    "arch-score": ["arch-score"],          # owner ruling D-2: required when the diff reaches custom_components/
    "budget-raise-gate": ["budget-raise-gate"],
    "pr-contract": ["pr-contract"],
}
REQUIRED = {**CODE, **BODY}
BODY_ON_EDIT = {"arch-score", "budget-raise-gate", "pr-contract"}
BODY_ON_REVIEW = {"budget-raise-gate"}       # owner variant: a review re-runs only budget-raise-gate and gate


def derive(ctx: dict) -> tuple[str, str, str]:
    """(kind, pr, base) from the event alone. kind: code | edit | review."""
    ev = ctx["event_name"]
    if ev == "pull_request_review":
        return "review", str(ctx["pr_number"]), ctx["base_ref"]
    if ev == "pull_request":
        k = "edit" if ctx["action"] == "edited" and not ctx.get("changes_base") else "code"
        return k, str(ctx["pr_number"]), ctx["base_ref"]
    if ev == "merge_group":
        return "code", str(ctx.get("queue_pr") or ""), ctx.get("base_ref") or ""
    if ev == "workflow_dispatch":
        return "code", ctx.get("input_pr") or "", ctx.get("input_base") or ""
    return "code", "", ""                    # push


def title(kind: str, pr: str, base: str) -> str:
    """What ci.yml's `run-name:` renders at creation."""
    return f"CI {kind} pr={pr or '-'} base={base or '-'}"


def parse_title(t: str) -> tuple[str, str, str] | None:
    p = t.split()
    if len(p) != 4 or p[0] != "CI" or not p[2].startswith("pr=") or not p[3].startswith("base="):
        return None
    pr, base = p[2][3:], p[3][5:]
    return p[1], ("" if pr == "-" else pr), ("" if base == "-" else base)


def workset(kind: str, pr: str) -> set[str]:
    if kind == "edit":
        return set(BODY_ON_EDIT)
    if kind == "review":
        return set(BODY_ON_REVIEW)
    return set(CODE) | (set(BODY) if pr else set())


def gate(ctx: dict, api: dict) -> tuple[bool, list[str]]:
    """ctx: this run's github context. api: what gate.py reads at its own run time:
      prelude        {"conclusion", "kind", "pr"}
      jobs           {"<unit> / <name>": (status, conclusion)} of THIS run, latest attempts
      runs_at_head   [{"id", "title", "status", "jobs"}] every OTHER ci.yml run at the head
      live_pr        {"head_sha", "base_ref", "state"} of the PR named, or None
      open_pr_heads  set of SHAs that head an open PR (only read on an unnamed dispatch)
      reaches_cc     the three-dot diff touches custom_components/ (git, in the gate job)

    A green result certifies the head's CURRENT state: every required unit's newest
    completed evaluation at this head and base is green, and no other run at the head
    is still being judged. That is what lets a re-run of an older run's gate (the
    refresh and sweep hooks, DESIGN-P2.md 4.3) converge on the newest verdict, so the
    design holds whether the ruleset reads the newest `gate` or every `gate` at the
    head (#2009's reading, tools/policy/budget_raise_gate.py:604).
    """
    bad: list[str] = []
    kind, pr, base = derive(ctx)
    ev = ctx["event_name"]
    pre = api["prelude"]
    if pre.get("conclusion") != "success":
        return False, [f"prelude: {pre.get('conclusion')}"]
    if (pre.get("kind"), pre.get("pr", "")) != (kind, pr):
        return False, [f"prelude says kind={pre.get('kind')} pr={pre.get('pr')!r}, the event says kind={kind} pr={pr!r}"]
    if ev == "workflow_dispatch":
        if pr:
            lp = api.get("live_pr")
            if not lp or lp["state"] != "open" or lp["head_sha"] != ctx["sha"]:
                return False, [f"dispatch pr={pr} does not name the open PR headed by this SHA"]
        elif ctx["sha"] in api.get("open_pr_heads", set()):
            return False, ["this SHA heads an open PR: dispatch with -f pr=N -f base=REF"]
    # The base every source must have judged: the PR's base NOW, read live. A run
    # whose event named another base (an earlier base, before a retarget; or a
    # dispatch naming the wrong one) is no source for this head, so its own units
    # do not count, and its gate, re-judged, reads the runs that did judge the
    # live base.
    judge_base = base
    if pr and ev != "merge_group":
        lp = api.get("live_pr")
        if not lp:
            return False, [f"PR {pr} could not be read"]
        judge_base = lp["base_ref"]
    others = [r for r in api["runs_at_head"] if r["id"] != ctx["run_id"]]
    busy = sorted(r["id"] for r in others if r["status"] not in ("completed", "action_required"))
    if busy:
        return False, [f"run(s) {busy} at this head are still being judged; their gate decides"]
    required = {u: list(n) for u, n in CODE.items()}
    if ev == "push":
        required["tests"] = [n for n in required["tests"] if n != "closure-scope"]
    if pr:
        for u, n in BODY.items():
            if u != "arch-score" or api.get("reaches_cc"):
                required[u] = list(n)
    me = {"id": ctx["run_id"], "title": title(kind, pr, base), "status": "completed", "jobs": api["jobs"]}
    for unit, names in required.items():
        src = None
        for r in sorted(others + [me], key=lambda r: r["id"], reverse=True):
            if r["status"] == "action_required":
                continue
            t = parse_title(r["title"])
            if t is None:
                bad.append(f"run {r['id']}: unreadable title {r['title']!r}")
                continue
            if t[1] != pr or t[2] != judge_base or unit not in workset(t[0], t[1]):
                continue
            js = [r["jobs"].get(f"{unit} / {n}") for n in names]
            if r is me or all(j is not None and j[0] == "completed" for j in js):
                src = r                     # this run's own unit always counts (its needs ran it)
                break
        if src is None:
            bad.append(f"{unit}: no run at this head judged base {judge_base!r}")
            continue
        where = "this run" if src is me else f"run {src['id']}"
        for n in names:
            st = src["jobs"].get(f"{unit} / {n}")
            if st is None:
                bad.append(f"{unit} / {n}: ABSENT ({where})")
            elif st[0] != "completed":
                bad.append(f"{unit} / {n}: PENDING ({where})")
            elif st[1] != "success":
                bad.append(f"{unit} / {n}: {st[1].upper() if st[1] == 'skipped' else st[1]} ({where})")
    return not bad, sorted(set(bad), key=bad.index)
