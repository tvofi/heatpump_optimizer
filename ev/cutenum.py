# Reviewer's own enumerator: every removed diff line (base..head, -U0), split at
# sentence/clause punctuation; a fragment of >=3 words survives when its normalised
# words are a contiguous run inside ONE tracked file at head.
import re, subprocess, sys
base, head = sys.argv[1], sys.argv[2]
def git(*a): return subprocess.run(("git",)+a, capture_output=True, check=True, cwd="/home/user/heatpump_optimizer").stdout.decode("utf-8","replace")
def norm(s): return " ".join(re.findall(r"[a-z0-9]+", s.lower()))
files=[f for f in git("ls-tree","-r","--name-only","-z",head).split("\0") if f]
corpus={}
for f in files:
    try: corpus[f]=" "+norm(git("show",f"{head}:{f}"))+" "
    except Exception: pass
diff=git("diff","-U0","--no-color",base,head)
cur=None; n=tot=0
for line in diff.split("\n"):
    if line.startswith("--- "): cur=line[6:] if line.startswith("--- a/") else None; continue
    if line.startswith("-") and cur:
        for frag in re.split(r"(?<=[.!?;:])\s+|\s+[—–]\s+", line[1:]):
            w=norm(frag)
            if len(w.split())<3: continue
            tot+=1
            hits=[f for f,t in corpus.items() if f" {w} " in t]
            if not hits:
                n+=1; print(f"GONE {cur}: {frag.strip()[:200]}")
print(f"TOTAL {n} gone of {tot} removed fragments")
