import re
import re as _re
def _workflow_job(text: str, name: str) -> str:
    """One job's YAML block, so a wiring check cannot match a sibling job."""
    start = text.index(f"\n  {name}:\n") + 1
    nxt = re.compile(r"^  [A-Za-z][\w-]*:", re.M).search(
        text, text.index("\n", start) + 1)
    return text[start:nxt.start()] if nxt else text[start:]


def _gh_if(job: str) -> str:
    m = _re.search(r"^    if: (?:>-\n((?:      .*\n)+)|(.*)\n)", job, _re.M)
    return " ".join((m.group(1) or m.group(2)).split()) if m else "true"


def _gh_eval(expr: str, ctx: dict) -> bool:
    for k, v in ctx.items():
        expr = expr.replace(k, repr(v))
    expr = (expr.replace("always()", "True").replace("!cancelled()", "True").replace("&&", " and ")
            .replace("||", " or ").replace("!=", "<>"))
    expr = _re.sub(r"!(?!=)", " not ", expr).replace("<>", "!=")
    return bool(eval(expr, {"__builtins__": {}}))  # noqa: S307 -- literals only


