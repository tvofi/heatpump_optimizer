import re, sys, subprocess, json, os

REQ = re.compile(r'^([A-Za-z0-9][A-Za-z0-9._-]*)==(\S+)\s*\\?\s*$')
HASH = re.compile(r'--hash=sha256:([0-9a-f]{64})')

def parse(text):
    blocks = {}
    cur = None
    for line in text.splitlines():
        m = REQ.match(line)
        if m and not line.startswith(' '):
            cur = m.group(1).lower().replace('_','-').replace('.','-')
            blocks[cur] = {'name_raw': m.group(1), 'version': m.group(2), 'hashes': set()}
            continue
        if cur is not None:
            h = HASH.search(line)
            if h:
                blocks[cur]['hashes'].add(h.group(1))
            elif line.strip() and not line.startswith(' '):
                cur = None
    return blocks

def read_at(ref, path):
    return subprocess.run(['git','show',f'{ref}:{path}'], capture_output=True, text=True, check=True).stdout

base, head, path = sys.argv[1], sys.argv[2], sys.argv[3]
b = parse(read_at(base, path))
h = parse(read_at(head, path))
print(f'== {path} ==')
print('packages base:', len(b), 'head:', len(h))
removed = sorted(set(b) - set(h))
added = sorted(set(h) - set(b))
print('removed packages:', removed)
print('added packages:', added)
for name in sorted(set(b) | set(h)):
    bb, hh = b.get(name), h.get(name)
    if bb is None:
        print(f'ADDED {name}=={hh["version"]} hashes={len(hh["hashes"])}')
    elif hh is None:
        print(f'DROPPED {name}=={bb["version"]} hashes={len(bb["hashes"])}')
    elif bb['version'] != hh['version']:
        print(f'MOVED {name}: {bb["version"]} -> {hh["version"]} hashes {len(bb["hashes"])} -> {len(hh["hashes"])} equal_sets={bb["hashes"]==hh["hashes"]}')
    elif bb['hashes'] != hh['hashes']:
        print(f'HASHES-CHANGED {name}=={hh["version"]}: {len(bb["hashes"])} -> {len(hh["hashes"])} (same version!) added={len(hh["hashes"]-bb["hashes"])} removed={len(bb["hashes"]-hh["hashes"])}')
