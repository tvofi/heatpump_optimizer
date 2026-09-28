import csv, io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import build as B
rows = list(csv.DictReader(open('../register_rows.tsv'), delimiter='\t'))
cls17 = {(r['round'], r['finding_id']): r['class_id'] for r in rows}
def esc(s): return s.replace('|', '\\|')
print('### R1-7 flags\n\n| round | id | v1 class | would move to | conf | reason |\n|---|---|---|---|---|---|')
for (rnd, fid), (tgt, conf, why) in sorted(B.FLAGS17.items(), key=lambda x: (x[1][0], x[0])):
    print(f'| {rnd} | {fid} | {cls17[(rnd, fid)]} | {tgt} | {conf} | {esc(why)} |')
print('\n### R8\n\n| id | issue | class | conf | reason |\n|---|---|---|---|---|')
iss = {r['finding_id']: r['issue'] for r in rows if r['round'] == 'R8'}
for fid, (c, conf, why) in sorted(B.R8.items(), key=lambda x: (x[1][0], x[0])):
    print(f'| {fid} | {iss.get(fid) or "not filed"} | {c} | {conf} | {esc(why)} |')
print('\n### R9 re-maps\n\n| judge class (alias) | roster id | v2 id | conf | members |\n|---|---|---|---|---|')
mem = {}
for r in rows:
    if r['round'] == 'R9' and r['r9_alias']:
        mem.setdefault(r['r9_alias'], []).append(r['finding_id'])
for jc, (al, c, conf) in sorted(B.R9MAP.items(), key=lambda x: (x[1][1], x[1][0])):
    print(f'| {esc(jc)} | {al} | {c} | {conf} | {", ".join(mem.get(al, []))} |')
print('\n### R9 judged rows kept in the judge\'s class but flagged\n\n| id | judge class | would move to | conf | reason |\n|---|---|---|---|---|')
c9 = {r['finding_id']: r['class_id'] for r in rows if r['round'] == 'R9'}
for fid, (tgt, conf, why) in sorted(B.FLAGS9.items()):
    print(f'| {fid} | {c9[fid]} | {tgt} | {conf} | {esc(why)} |')
