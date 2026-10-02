#!/bin/bash
# Reviewer's own controls (my instrument, not the finder's or the fixer's). Run from the head worktree.
set -u; WT=$(pwd); PY=~/hpo-seats/R9-F11.4-venv/bin/python3; export PYTHONPATH=tests/hastub:tests:custom_components
SCR=$(mktemp -d); cp docs/site/docs.css $SCR/css.bak
echo "== C1 third-party @import in docs/site/docs.css (every built page links it)"
{ printf '@import url("https://fonts.googleapis.com/css2?family=Outfit");\n'; cat $SCR/css.bak; } > docs/site/docs.css
$PY tests/doc_claims.py 2>&1 | tail -1; cp $SCR/css.bak docs/site/docs.css
echo "== C2 third-party @font-face src in docs/site/docs.css"
sed -i '' '1s#url(fonts/outfit-latin-600-normal.woff2)#url(https://fonts.gstatic.com/x.woff2)#' docs/site/docs.css
$PY tests/doc_claims.py 2>&1 | tail -1; cp $SCR/css.bak docs/site/docs.css
echo "== C3 two anchor-free documents with one page name, real build vs errors.push(two documents...) mutant"
D=$SCR/dup; mkdir -p $D/docs/site $D/docs/x; cd $D
printf '# T\n\n## Documentation\n\n| Document | What |\n|---|---|\n| [docs/a.md](docs/a.md) | a |\n| [docs/x/a.md](docs/x/a.md) | xa |\n| [docs/backlog.md](docs/backlog.md) | arch |\n' > README.md
printf '# A\n\nplain\n' > docs/a.md; printf '# XA\n\nother plain\n' > docs/x/a.md; echo '# B' > docs/backlog.md; : > docs/site/docs.css
git init -q; git add -A; git ls-files > tree.txt
echo "-- real:"; node $WT/tools/site/build_docs.mjs --root . --tree tree.txt --out o1 | tail -2
sed 's/errors.push(.two documents would be built to one page name.)/void 0/' $WT/tools/site/build_docs.mjs > $WT/tools/site/_rev_mut.mjs
echo "-- mutant:"; node $WT/tools/site/_rev_mut.mjs --root . --tree tree.txt --out o2 | tail -2; ls o2; rm $WT/tools/site/_rev_mut.mjs
cd $WT; git status --short
