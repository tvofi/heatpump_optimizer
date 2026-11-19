#!/bin/bash
S=/private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-11-orchestrator-resume-928854/f2a0d03a-dc77-4fb9-b8fa-10babda9f42a/scratchpad; EV=$S/ev3816
cd $S/rev3816; git worktree add --detach -q $S/base3816 cb8edb65a5a9c0940dbe263acee49e02ba5f0b25 2>/dev/null
for end in base3816:cb8edb65a5a9c0940dbe263acee49e02ba5f0b25 rev3816:500eef956e218cd69967681ca147821a4e26b649; do d=${end%%:*}; sha=${end#*:}; cd $S/$d
 python3 -I tools/audit/check_scopes.py --repo . --ref $sha --population > $EV/pop-$d.txt 2>&1; echo "rc=$?" >> $EV/pop-$d.txt
 python3 -I -c "
import sys; sys.path.insert(0,'tools/audit/seat'); import plant_recall as p
c=p.population(open('$EV/pop-$d.txt').read())
cells=[f'{a}={l}' for a in ('tank_volume','house_size') for l in ('min','default','max')]
print('$d', '$sha', 'accepted', sum(x in c for x in cells), '/6', [x for x in cells if x not in c])
for x in ('layout=no_valve','layout=moon','tank_volume=typical'): print(' control', x, 'in' if x in c else 'refused')
" > $EV/carry0-$d.txt 2>&1
done
cd $S/rev3816; python3 -I tools/audit/check_scopes.py --self-test --repo . > $EV/selftest.txt 2>&1; echo "rc=$?" >> $EV/selftest.txt
python3 -I tools/audit/product_reads.py operation --ledger dev/audit/rounds/round11/product-reads/operation.tsv --jobs 3 > $EV/carry1.txt 2>&1; echo "rc=$?" >> $EV/carry1.txt
python3 tests/structure.py > $EV/structure.txt 2>&1; echo "rc=$?" >> $EV/structure.txt
git merge-tree --write-tree origin/main HEAD > $EV/mergetree.txt 2>&1; echo "rc=$?" >> $EV/mergetree.txt
git diff --name-only cb8edb65a5a9c0940dbe263acee49e02ba5f0b25...HEAD > $EV/files.txt
echo DONE > $EV/ends.done
