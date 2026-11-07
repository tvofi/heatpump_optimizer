#!/usr/bin/env bash
# Reviewer-built (not the finder's, not the fixer's): verdict-changing plants on the real tree at <head>.
# plant.sh <head> <case> <out> ; the arm is the head's ci_predict.py, --base <head>, --only graders.
set -u
head=$1 case=$2 out=$3
root=$(git rev-parse --show-toplevel)
. "$root/tests/throwaway_git.sh"
wt=$(mktemp -d); trap 'rm -rf "$wt"' EXIT
throwaway_git_clone -q --shared --no-checkout "$root" "$wt/t" >/dev/null || exit 2
cd "$wt/t" || exit 2
throwaway_git_env
git checkout -q --detach "$head" && git update-ref refs/remotes/origin/main "$head" || exit 2
body=
case $case in
 null) : ;;
 briefs-roster-only)   echo '{"groups":[{"group":"ZZ-PLANT","after":["NO-SUCH-GROUP"]}]}' > .claude/workflows/wave-zz-groups.json ;;
 briefs)   echo '{"groups":[{"group":"ZZ-PLANT","after":["NO-SUCH-GROUP"]}]}' > .claude/workflows/wave-zz-groups.json
           sed -i 's/process.exit(totalErrors > 0 || acceptanceRc ? 1 : 0)/process.exit(0)/' tools/policy/brief_lint.mjs
           grep -q 'process.exit(0)$' tools/policy/brief_lint.mjs || { echo "site missing"; exit 2; } ;;
 briefs-cosmetic) printf '\n// plant\n' >> tools/policy/brief_lint.mjs ;;
 carry)    body=$wt/body.md; printf '## Findings\n\n- Residual: the planted defect nobody routes.\n' > "$body"
           python3 - <<'PY'
p='tools/audit/carry_audit.py'; s=open(p).read()
i=s.index('\nimport ') ; s=s[:i]+"\nimport sys as _s\nif 'check' in _s.argv: _s.exit(0)"+s[i:]; open(p,'w').write(s)
PY
           ;;
 carry-base-only) body=$wt/body.md; printf '## Findings\n\n- Residual: the planted defect nobody routes.\n' > "$body"; printf '\n# plant\n' >> tools/audit/carry_audit.py ;;
 brg)      python3 - <<'PY'
import json; p='tests/structure_budgets.json'; d=json.load(open(p)); k=next(k for k,v in d.items() if isinstance(v,int)); d[k]+=5; open(p,'w').write(json.dumps(d,indent=2)+"\n")
p='tools/policy/budget_raise_gate.py'; s=open(p).read(); i=s.index('\nimport '); s=s[:i]+"\nimport sys as _s\nif '--pr' in _s.argv: _s.exit(0)"+s[i:]; open(p,'w').write(s)
PY
           ;;
esac
[ "$case" = null ] || git add -A && git commit -qm "plant $case" || true
cp "$root/tools/pr/ci_predict.py" tools/pr/ci_predict.py 2>/dev/null
extra=(); [ -n "$body" ] && extra=(--body "$body")
{ echo "case=$case head=$head diff: $(git diff --name-only $head HEAD | tr '\n' ' ')"
  if [ -n "$body" ]; then echo "head-copy carry_audit: $(python3 -I tools/audit/carry_audit.py check --body "$body" --branch x 2>&1 | tail -1) rc=$?"; fi
  [ "${case%%-*}" = briefs ] && echo "head-copy brief_lint rc: $(node tools/policy/brief_lint.mjs >/dev/null 2>&1; echo $?)"
  PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base "$head" --only graders "${extra[@]}" 2>&1; echo "rc=$?"; } > "$out"
