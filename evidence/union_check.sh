S=/private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-audit-r9-completion-b85771/a30f7fe1-0f0c-438d-95a1-396f9807d60e/scratchpad
AD=aadd1de4; MB=bcea74883bec1e3395377ff70d8640737c97fc3e
f(){ git show "${1}:tests/features.py"; }
f $AD | sort > $S/a_sorted
git diff $MB 421c77f9 -- tests/features.py | grep '^+[^+]' | sed 's/^+//' | sort > $S/main_add
git diff $MB 21a62c10 -- tests/features.py | grep '^+[^+]' | sed 's/^+//' | sort > $S/br_add
echo "main-added missing:" $(comm -23 $S/main_add $S/a_sorted | wc -l) of $(wc -l <$S/main_add)
echo "branch-added missing:" $(comm -23 $S/br_add $S/a_sorted | wc -l) of $(wc -l <$S/br_add)
(f 21a62c10; f 421c77f9) | sort -u > $S/par; echo "aadd lines in neither parent:" $(comm -13 $S/par $S/a_sorted | wc -l)
echo "removed-vs-main lines in MB/branch/main/aadd:"
P='a space-heating step writes the heating flow, not the 25 degC floor'
for p in $MB 21a62c10 421c77f9 $AD; do echo " $p" $(f $p | grep -cF "$P"); done
for r in $MB 21a62c10 421c77f9 $AD; do echo "$r checks=$(f $r | grep -cE 'def test_|R\.(check|section)\(') lines=$(f $r | wc -l)"; done
f $AD | python3 -c 'import sys,ast;ast.parse(sys.stdin.read());print("parse ok")'
f $AD | grep -cE '^(<<<<<<<|=======|>>>>>>>)'
