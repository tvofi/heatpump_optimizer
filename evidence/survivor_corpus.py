import re,pathlib
def mk(split=r"\n[ \t]*\n", lstrip=True, strip=True, pfilter=True):
    def f(text):
        t=text.strip() if strip else text
        paras=[p for p in re.split(split,t) if (p.strip() if pfilter else p)]
        title=bool(paras) and paras[0].startswith("# ") and "\n" not in paras[0]
        block=[ln for p in paras[:2 if title else 1] for ln in p.splitlines() if not (ln.lstrip() if lstrip else ln).startswith("|")]
        return {x.strip(".-") for x in re.findall(r"[\w.-]+","\n".join(block))}
    return f
base=mk(); V={"split-strict":mk(split=r"\n\n"),"table-nolstrip":mk(lstrip=False),"no-strip-text":mk(strip=False),"no-pstrip-filter":mk(pfilter=False)}
P=sorted(pathlib.Path("dev/audit/rca").glob("*.md"))
for k,f in V.items():
    d=[p.stem for p in P if f(p.read_text())!=base(p.read_text())]
    print(k,"records differing:",len(d),d[:5])
