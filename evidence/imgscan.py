import sys, pathlib, subprocess, re
sys.path.insert(0, "tests"); sys.argv=["x"]
import importlib.util
spec = importlib.util.spec_from_file_location("dc", "tests/doc_claims.py"); dc = importlib.util.module_from_spec(spec); spec.loader.exec_module(dc)
root = pathlib.Path(".")
tracked = subprocess.run(["git","ls-files","*.md","*.html"],capture_output=True,text=True).stdout.split()
bad, n = dc.image_dim_findings(root, tracked)
print(f"RESULT all_tracked_pages={len(tracked)} sized_img_compared={n} mismatches={len(bad)}"); [print(" ",b) for b in bad]
pub = dc.published_pages(); bad2, n2 = dc.image_dim_findings(root, pub)
print(f"RESULT published_pages={len(pub)} sized_img_compared={n2} mismatches={len(bad2)}")
# every <img> with width or height on published pages, how many escaped comparison
tot=0
for p in tracked:
    t=pathlib.Path(p).read_text(errors="replace")
    for tag in dc._IMG_TAG.findall(t):
        if re.search(r'\b(width|height)\s*=', tag): tot+=1; 
        if re.search(r"\b(width|height)\s*=\s*'", tag) or re.search(r"\bsrc\s*=\s*'", tag): print("  single-quoted:",p,tag[:100])
print(f"RESULT sized_img_tags_any_quote_all_tracked={tot}")
