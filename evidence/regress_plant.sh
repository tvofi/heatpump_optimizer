#!/bin/bash
# reviewer's own plant: the finder's harness (agreement_py.py --run) at both ends under
# one wrapped-argv writer whose program line holds the open bracket. Run from a head worktree.
set -u
AG=tools/policy/agreement.mjs; MT=tools/audit/seat/merge_train.py
cp $AG /tmp/ag.$$; cp $MT /tmp/mt.$$
run() { python3 -I tools/policy/agreement_py.py --run 2>&1 | grep -E 'merge call|REFUSED +merge-subject|RESULT' | sed -e 's/^ *//' -e 's/ seconds=[0-9.]*//' -e 's/.*commit(s) past [0-9a-f]*, //' | tr '\n' ' '; echo; }
printf '%s\n' 'if False:  # agreement_py imports this module' '    subprocess.run(["gh",' '                    "pr", "merge", str(n), "--squash",' '                    "--subject", s], check=True)' >> $MT
for ref in 683dd52cbb938ad00b38857117710791f5581f4b d0d35231c633ca447acf04770f9034281417b72d; do git show $ref:$AG > $AG; echo "$ref wrapped argv plant: $(run)"; done
cp $T/mt $MT
for ref in 683dd52cbb938ad00b38857117710791f5581f4b d0d35231c633ca447acf04770f9034281417b72d; do git show $ref:$AG > $AG; echo "$ref unperturbed: $(run)"; done
cp $T/ag $AG; rm -rf $T; git status --short -- $AG $MT
