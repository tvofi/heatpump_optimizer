#!/bin/bash
# reviewer's own mutant runner (review-2373); each mutant applied in $S/mut, run, restored by git checkout
export PATH=$HOME/.local/state/hpo/bin:$PATH
S=/Users/timmalmstrom/hpo-seats/r10s3/review-2373
cd $S/mut
IDS=a3_card_clone_copies_control,a3_card_clone_copies_fix,a3_card_clone_copies_null,a3_card_dead_definitions_control,a3_card_dead_definitions_fix,a3_card_dead_definitions_null,a3_literal_clone_copies_control,a3_literal_clone_copies_fix,a3_literal_clone_copies_null,rt_42_literal_respelled,rt_43_literal_local_hop,rt_44_card_rename_locals
run() { echo "== $1 head=$(git rev-parse HEAD)"; git diff --stat; PYTHONPATH=tests/hastub python3 tools/audit/archscore/calibrate.py --only $IDS --jobs 3 > $S/evidence/full_$1.txt 2>&1; echo "exit=$?"; grep -E "a3_(card|literal)|rt_4[234]|CALIBRATION|RED TEAM|Traceback|Error" $S/evidence/full_$1.txt; git checkout -- .; git status --porcelain; }
run M0 > $S/evidence/mut_M0.txt 2>&1
python3 - <<'P'
p='tools/audit/archscore/metrics/card.py'; s=open(p).read()
s=s.replace("    return sorted({d for d in definitions(toks) if d not in HOOKS and seen[d] <= 1})","    return []",1); open(p,'w').write(s)
P
run M1 > $S/evidence/mut_M1.txt 2>&1
python3 - <<'P'
p='tools/audit/archscore/metrics/literal_clones.py'; s=open(p).read()
s=s.replace("        def is_spec(e: ast.AST, locals_: dict[str, ast.AST]) -> bool:\n","        def is_spec(e: ast.AST, locals_: dict[str, ast.AST]) -> bool:\n            return False\n",1); open(p,'w').write(s)
P
run M4 > $S/evidence/mut_M4.txt 2>&1
python3 - <<'P'
p='tools/audit/archscore/metrics/card.py'; s=open(p).read()
s=s.replace("        if len(owners) > 1:","        if len(owners) > 999:",1); open(p,'w').write(s)
P
run M3 > $S/evidence/mut_M3.txt 2>&1
# M7: doc_claims _tokens empty
python3 - <<'P'
p='tests/doc_claims.py'; s=open(p).read()
s=s.replace("    return set(_IDENT.findall(text))","    return set()",1); open(p,'w').write(s)
P
echo "== M7"; git diff --stat; PYTHONPATH=tests/hastub python3 tests/doc_claims.py > $S/evidence/mut_M7_doc_claims.txt 2>&1; echo "exit=$?" >> $S/evidence/mut_M7_doc_claims.txt; git checkout -- .; git status --porcelain
PYTHONPATH=tests/hastub python3 tests/doc_claims.py > $S/evidence/doc_claims_head.txt 2>&1; echo "exit=$?" >> $S/evidence/doc_claims_head.txt
echo ALLDONE
