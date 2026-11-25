#!/usr/bin/env bash
# Reviewer's mutants of the release step of .github/workflows/pages.yml at the head,
# each run through the reviewer's pages-section harness (h/pages_section.py) with a mutated copy.
set -u
W=$(cat $HOME/W); WT=$W/wt-f7aec2be; WF=$WT/.github/workflows/pages.yml
run() {  # name, python-replacement-expr
  local name=$1 old=$2 new=$3 m=$W/mut-$1.yml
  python3 - "$WF" "$m" "$old" "$new" <<'EOF'
import sys; s=open(sys.argv[1]).read(); old,new=sys.argv[3],sys.argv[4]
assert old in s, f"anchor not found: {old!r}"; open(sys.argv[2],'w').write(s.replace(old,new,1))
EOF
  out=$(cd $W && timeout 600 python3 h/pages_section.py wt-f7aec2be "$m" 2>/dev/null | grep -E "^(FAIL|RESULT)" | grep -iE "plan|release|RESULT")
  if echo "$out" | grep -q "^FAIL"; then echo "KILLED  $name"; else echo "SURVIVED $name"; fi
  echo "$out" | sed 's/^/    /'
}
run version-sort '--sort=-v:refname' '--sort=-refname'
run no-v-filter " origin 'refs/tags/v*'" " origin"
run local-tags "git ls-remote --tags --refs --sort=-v:refname origin 'refs/tags/v*' | head -n 1 | sed 's#.*refs/tags/##'" "git tag --list 'v*' --sort=-v:refname | head -n 1"
run no-fetch 'git fetch --quiet --no-tags --depth 1 origin "+refs/tags/$tag:refs/tags/$tag"' 'true'
run no-checkout 'git -c advice.detachedHead=false checkout --quiet "$tag"' 'true'
run oldest-tag 'head -n 1 | sed' 'tail -n 1 | sed'
