"""Run the fixed carry() (its function body spliced into each main@t script is not needed: the fixed
script is run as is) against every re-verification, beside the carry of main@t, and print the flips."""
import subprocess,sys
def g(*a): return subprocess.run(['git','-C','wt',*a],capture_output=True,text=True).stdout.strip()
cls={}
for l in open('hm5_out.tsv'):
    if l.startswith('#'): f=l.split('\t'); cls[(f[0],f[1])]=(f[2],f[4])
for l in open('hm3_out.tsv'):
    if not l.startswith('#'): continue
    pr,t1,pair,kind=l.split('\t')[:4]
    h0,h1=[g('rev-parse',x) for x in pair.split('->')]
    m=g('rev-list','-1','--first-parent',f'--before={t1}','origin/main')
    def run(s):
        r=subprocess.run(['bash',s,'--carry',h0,h1,m],cwd='wt',capture_output=True,text=True); return 'yes' if 'CARRY: yes' in r.stdout else 'no'
    fx=run('../aa_fixed.sh'); base=run('../aa_base.sh')
    b,why=cls[(pr,t1[:16])]
    print(pr,t1[:16],kind,b,why,'main='+base,'fixed='+fx,'FLIP' if fx!=base else '',sep='\t')
