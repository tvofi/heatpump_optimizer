# Reviewer's own re-run: base (6d86acc9) vs fixed (PR head) carry over the 75 hm_out pairs, main@t.
import subprocess,sys
EV=sys.argv[1]
def g(*a): return subprocess.run(['git',*a],capture_output=True,text=True).stdout.strip()
flips=0; bad=0; n=0
for l in open('dev/audit/rca/headmoved/hm_out.tsv'):
    if not l.startswith('#'): continue
    f=l.split('\t'); pr,t1,pair=f[0],f[1],f[2]
    h0,h1=[g('rev-parse',x) for x in pair.split('->')]
    m=g('rev-list','-1','--first-parent',f'--before={t1}','origin/main')
    def run(s):
        r=subprocess.run(['bash',s,'--carry',h0,h1,m],capture_output=True,text=True); return 'yes' if 'CARRY: yes' in r.stdout else 'no'
    b=run(f'{EV}/aa_base.sh'); x=run(f'{EV}/aa_fixed.sh'); n+=1
    if b!=x: flips+=1
    if b=='yes' and x=='no': bad+=1
    print(pr,t1[:16],'base='+b,'fixed='+x,'FLIP' if b!=x else '',sep='\t',flush=True)
print('RESULT pairs',n,'flips',flips,'yes_to_no',bad)
