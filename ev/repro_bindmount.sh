mount --bind /home/user/scr/fakenull /dev/null || { echo MOUNTFAIL; exit 9; }
for side in base rv; do
  cd /home/user/$side
  python3 -c 'import sys,subprocess,tempfile;sys.path.insert(0,"tests");import throwaway_git as t;d=tempfile.mkdtemp();r=subprocess.run(["git","init","-q",d+"/r"],env=t.throwaway_git_env(),capture_output=True,text=True);print("'$side' py exit",r.returncode,r.stderr.strip()[:80])' 2>&1
  bash -c '. tests/throwaway_git.sh; d=$(mktemp -d); throwaway_git_env; git init -q $d/r 2>&1|head -1; echo "'$side' sh exit ${PIPESTATUS[0]}"' 2>&1 </dev/zero
done
