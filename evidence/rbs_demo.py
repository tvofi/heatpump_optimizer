import re, yaml as _yaml, sys
from pathlib import Path
def _bp_value(expr: str, ctx: dict) -> str:
    expr = expr.strip().removeprefix("${{").removesuffix("}}")
    for k, v in sorted(ctx.items(), key=lambda kv: -len(kv[0])):
        expr = expr.replace(k, repr(v))
    expr = expr.replace("&&", " and ").replace("||", " or ")
    return eval(expr, {"__builtins__": {}, "format": lambda f, *a: f.format(*a)})  # noqa: S307


_RBS_SRC = "MERGEPARENT"
_RBS_CTX = {"github.event.pull_request.base.sha": "BASESHA", "github.event.merge_group.base_sha": "",
            "github.sha": "MERGESHA", "inputs.base": "main", "inputs.restore_source": _RBS_SRC,
            "steps.source.outputs.sha": _RBS_SRC, "needs.prelude.outputs.restore_source": _RBS_SRC,
            "needs.gate.outputs.restore_source": _RBS_SRC}
_RBS_RESTORE = re.compile(r'git checkout "\$PINNED"|"\$PINNED:')


def _rbs_defects(texts: dict) -> "list[str]":
    out, restoring = [], set()
    for fname, text in sorted(texts.items()):
        for jid, job in ((_yaml.safe_load(text) or {}).get("jobs") or {}).items():
            for step in job.get("steps") or []:
                pinned = (step.get("env") or {}).get("PINNED")
                if not pinned or not _RBS_RESTORE.search(str(step.get("run") or "")):
                    continue
                restoring.add(fname)
                try:
                    got = _bp_value(pinned, _RBS_CTX)
                except Exception as exc:  # an expression this rule cannot read is refused, not skipped
                    got = f"unreadable ({exc.__class__.__name__})"
                if got != _RBS_SRC:
                    out.append(f"{fname}:{jid} restores from {got} on a pull_request: {pinned}")
    ci = _yaml.safe_load(texts["ci.yml"]) or {}
    for jid, job in (ci.get("jobs") or {}).items():
        callee = str(job.get("uses") or "").rpartition("/")[2]
        if callee in restoring and (job.get("with") or {}).get("restore_source") != (
                "${{ needs.prelude.outputs.restore_source }}"):
            out.append(f"ci.yml:{jid} calls {callee}, which restores, without passing restore_source")
    steps = ((ci.get("jobs") or {}).get("prelude") or {}).get("steps") or []
    ids = [s.get("id") for s in steps]
    first = next((i for i, s in enumerate(steps) if (s.get("env") or {}).get("PINNED")), len(steps))
    run = str(steps[ids.index("source")].get("run") or "") if "source" in ids else ""
    if "source" not in ids or ids.index("source") > first:
        out.append("ci.yml:prelude resolves no restore source before its own restore")
    for need in ('git merge-base --is-ancestor "$EVENT_BASE" "$source"', '"$GITHUB_SHA"', '-eq 2 ]'):
        if need not in run:
            out.append(f"ci.yml:prelude's resolver lacks {need!r}")
    return out


d = Path(sys.argv[1])
texts = {q.name: q.read_text() for q in sorted(d.glob("*.yml"))}
got = _rbs_defects(texts)
print(f"RESULT rbs_defects={len(got)}")
for g in got[:40]: print("  ", g)
