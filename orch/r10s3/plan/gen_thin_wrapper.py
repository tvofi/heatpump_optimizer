#!/usr/bin/env python3
"""Round-10 plan page: a thin wrapper over the tree's own instruments.

    python3 gen.py [--out round-10-plan.html]

It computes nothing about the roster. `plan_table.py` renders swimlanes, the
gantt (critical path tagged `crit`), per-group detail and the ETA;
`resume_doc.py` renders the resume state. This file (1) fetches the roster
ref, (2) hands `plan_table.py` a --live overlay that says which open PR is on
which group (the branch-to-group answer is roster_lib.group_for_branch's),
and (3) converts the two markdown documents to one self-contained HTML page.
"""
import argparse, html, json, os, re, subprocess, sys

TOOLS_CHECKOUT = os.environ.get("HPO_TOOLS", "/Users/timmalmstrom/hpo-seats/r10s3/orch-wt")
REPO_SLUG = "tvofi/heatpump_optimizer"
SEAT = os.path.join(TOOLS_CHECKOUT, "tools/audit/seat")
sys.path.insert(0, SEAT)
import roster_lib  # noqa: E402  (the one roster reader)

HERE = os.path.dirname(os.path.abspath(__file__))


def run(*cmd):
    r = subprocess.run(cmd, cwd=TOOLS_CHECKOUT, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"{' '.join(cmd[:3])} failed rc={r.returncode}: {r.stderr[-600:]}")
    return r.stdout


def esc(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- markdown
def inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s.replace("&lt;br&gt;", "<br>")


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def md_to_html(md):
    out, lines, i = [], md.splitlines(), 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```mermaid"):
            j = i + 1
            while not lines[j].startswith("```"):
                j += 1
            src = "\n".join(lines[i + 1:j])
            out.append(f'<div class="scroll"><pre class="mermaid">{esc(src)}</pre></div>'
                       f'<details><summary>gantt source</summary><pre>{esc(src)}</pre></details>')
            i = j + 1
        elif ln.startswith("|"):
            j = i
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            head, body = cells(lines[i]), [cells(x) for x in lines[i + 2:j]]
            stage_i = head.index("stage") if "stage" in head else None
            t = ["<div class=\"scroll\"><table><thead><tr>" +
                 "".join(f"<th>{esc(h)}</th>" for h in head) + "</tr></thead><tbody>"]
            for r in body:
                cls = f' class="st-{esc(r[stage_i])}"' if stage_i is not None and len(r) > stage_i else ""
                t.append(f"<tr{cls}>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            out.append("".join(t) + "</tbody></table></div>")
            i = j
        elif ln.startswith("#"):
            n = len(ln) - len(ln.lstrip("#"))
            out.append(f"<h{n + 1}>{inline(ln[n:].strip())}</h{n + 1}>")
            i += 1
        elif ln.startswith("- "):
            j = i
            while j < len(lines) and lines[j].startswith("- "):
                j += 1
            out.append("<ul>" + "".join(f"<li>{inline(x[2:])}</li>" for x in lines[i:j]) + "</ul>")
            i = j
        elif ln.strip():
            out.append(f"<p>{inline(ln)}</p>")
            i += 1
        else:
            i += 1
    return "\n".join(out)


CSS = """
:root{--bg:#f3f5f6;--panel:#fff;--fg:#17232b;--muted:#5d6b74;--line:#d8dee2;--accent:#d9561f;--done:#2f8f5b}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#10171c;--panel:#162028;--fg:#e4ebef;--muted:#93a3ad;--line:#2a3842;--accent:#f07a42;--done:#5cc48a;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#10171c;--panel:#162028;--fg:#e4ebef;--muted:#93a3ad;--line:#2a3842;--accent:#f07a42;--done:#5cc48a;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font:15px/1.45 "Source Sans 3","Segoe UI",system-ui,sans-serif;padding:20px max(16px,env(safe-area-inset-right,0px)) 40px max(16px,env(safe-area-inset-left,0px));margin:0}
main{max-width:1240px;margin:0 auto;display:flex;flex-direction:column;gap:22px}
h1{font:700 2.1rem/1 "Barlow Condensed","Arial Narrow",sans-serif;margin:0}
h2,h3{font:600 1.25rem/1.1 "Barlow Condensed","Arial Narrow",sans-serif;letter-spacing:.04em;text-transform:uppercase;margin:0 0 10px}
.sub,.note{color:var(--muted)}
section{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:16px;min-width:0}
.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:.86rem}
th{text-align:left;color:var(--muted);border-bottom:2px solid var(--line);padding:6px 8px;white-space:nowrap;font-size:.78rem;text-transform:uppercase;letter-spacing:.05em}
td{border-bottom:1px solid var(--line);padding:6px 8px;vertical-align:top}
tr.st-done td{color:var(--muted)}
tr.st-in-progress td:first-child{border-left:3px solid var(--accent)}
pre{overflow-x:auto;font:12px/1.4 ui-monospace,Menlo,monospace}
pre.mermaid{background:transparent}
code{font:.85em ui-monospace,Menlo,monospace}
summary{cursor:pointer;color:var(--muted);font-size:.85rem}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "round-10-plan.html"))
    a = ap.parse_args()

    run("git", "fetch", "-q", "origin")
    ref = roster_lib.reader_ref(TOOLS_CHECKOUT, None)
    roster = roster_lib.show_roster(TOOLS_CHECKOUT, ref, None)

    prs = json.loads(run("gh", "pr", "list", "--repo", REPO_SLUG, "--state", "open",
                         "--limit", "200", "--json", "number,headRefName,title"))
    live, orphans = {}, []
    for p in prs:
        g = roster_lib.group_for_branch(roster, p["headRefName"])
        if g:
            live[g] = (live[g] + "; " if g in live else "") + f"PR #{p['number']} open"
        else:
            orphans.append(p)

    overlay = os.path.join(HERE, "live-overlay.json")
    json.dump(live, open(overlay, "w"))
    pt = run("python3", os.path.join(SEAT, "plan_table.py"), "--roster-ref", ref, "--live", overlay)
    rd = run("python3", os.path.join(SEAT, "resume_doc.py"), "--roster-ref", ref, "--out", "/dev/stdout")
    rd = "\n".join(l for l in rd.splitlines() if not l.startswith("wrote "))

    orph = ("<ul>" + "".join(f"<li>#{p['number']} <code>{esc(p['headRefName'])}</code> {esc(p['title'])}</li>"
                             for p in orphans) + "</ul>") if orphans else "<p>none</p>"
    plan_html = md_to_html(pt)
    resume_html = md_to_html(rd)
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Round 10 Plan</title>
<style>{CSS}</style></head><body><main>
<header><h1>Round 10 Plan</h1>
<p class="sub">Rendered by tools/audit/seat/plan_table.py and resume_doc.py; this page adds only the open-PR overlay. Tracking issue #201.</p></header>
<section>{plan_html}
<h3>Open PRs matching no roster group</h3>{orph}</section>
<section><h2>Resume state</h2>{resume_html}</section>
</main>
<script type="module">
import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.esm.min.mjs";
const dark = matchMedia("(prefers-color-scheme: dark)").matches;
mermaid.initialize({{startOnLoad:true, theme: dark ? "dark" : "default", securityLevel:"strict", gantt:{{useWidth:1100}}}});
</script></body></html>
"""
    open(a.out, "w", encoding="utf-8").write(page)
    print(f"wrote {a.out} ({len(page)} bytes); open PRs {len(prs)}, on a group {len(live)}, orphan {len(orphans)}")


if __name__ == "__main__":
    main()
