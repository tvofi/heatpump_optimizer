import re,glob,collections
from pathlib import Path
docs=["README.md"]+sorted(glob.glob("docs/*.md"))
seen=collections.defaultdict(list)
for d in docs:
    for blk in re.split(r"\n\s*\n",Path(d).read_text()):
        if blk.lstrip().startswith(("```","|","#")) : continue
        n=" ".join(blk.split())
        if len(n.split())>=12: seen[n].append(d)
print("dup paragraphs (ignoring fences/tables/headings):",sum(1 for v in seen.values() if len(v)>1))
# fences
fen=collections.defaultdict(list)
for d in docs:
    for m in re.finditer(r"```mermaid\n(.*?)```",Path(d).read_text(),re.S): fen[m.group(1).strip()].append(d)
print("identical mermaid in >1 doc:",[(len(v),v) for v in fen.values() if len(v)>1])
# orphan
for t in docs[1:]:
    b=Path(t).name
    inb=[d for d in docs if d!=t and re.search(r"\]\((?:\./|docs/|\.\./docs/)?"+re.escape(b),Path(d).read_text())]
    print(b,len(inb))
