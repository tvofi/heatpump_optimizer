import re, pathlib, importlib.util, subprocess
spec = importlib.util.spec_from_file_location("dc", "tests/doc_claims.py"); dc = importlib.util.module_from_spec(spec); spec.loader.exec_module(dc)
opened=set()
for rel in dc.published_pages():
    page=pathlib.Path(rel)
    if not page.is_file(): continue
    for tag in dc._IMG_TAG.findall(page.read_text(errors="replace")):
        src=re.search(r'\bsrc="([^"#?]+)"',tag)
        if src and re.search(r'\bwidth="\d+"',tag) and re.search(r'\bheight="\d+"',tag):
            p=(page.parent/src.group(1)).resolve().relative_to(pathlib.Path.cwd().resolve()); opened.add(str(p))
src=open("tests/closure.py").read()
inert=set(re.findall(r'"(docs/img/[^"]+\.png)"', src))
import json
cl=json.load(open("tests/closures.json"))
def find(o):
    if isinstance(o,dict):
        for k,v in o.items():
            if "doc_claims" in k: return v
            r=find(v)
            if r is not None: return r
rec=set(x for x in json.dumps(find(cl)).split('"') if x.startswith("docs/img/") and x.endswith(".png"))
print("RESULT pngs_opened_by_arm=%d inert_except_pngs=%d closure_pngs_doc_claims=%d"%(len(opened),len(inert),len(rec)))
print("RESULT opened==inert_except:",opened==inert," opened==closure:",opened==rec)
print("RESULT tracked_docs_img_png=", len(subprocess.run(["git","ls-files","docs/img/*.png"],capture_output=True,text=True).stdout.split()))
