#!/bin/bash
# r11_shared_files_p2_mutants.sh -- the mutants of R11-PRE-SHARED-FILES part 2 that no in-tree harness holds.
#
# One mutant at a time, in a detached scratch worktree of HEAD (the checkout is never written): the
# stored-figure-block rule in tools/pr/figure_block.py and tools/policy/policy_lint.mjs, the agreement
# pair that holds the two readers together, and the line-pin re-pin in tools/policy/brief_lint.mjs.
# A mutant is KILLED when its command exits non-zero AND prints a line matching its pattern (a failing
# check's own line), so a crash is not read as a kill. The claim-file driver's mutants are
# claim_merge_mutants.py's; the body writers' are the `# mut:` lines pr_args.sh --self-test drives.
#
#     bash dev/audit/harnesses/r11_shared_files_p2_mutants.sh
#
# Prints one line per mutant and RESULT lines; exits 1 on a survivor or a mutant that no longer applies.
# The brief_lint.mjs rows run the whole linter each, about 100 s a row.
set -u
ROOT=$(git rev-parse --show-toplevel) || exit 2
W=$(mktemp -d) || exit 2
trap 'cd "$ROOT"; git -C "$ROOT" worktree remove --force "$W/wt" >/dev/null 2>&1; rm -rf "$W"' EXIT
git -C "$ROOT" worktree add -q --detach "$W/wt" HEAD || exit 2
cd "$W/wt" || exit 2
K=0; S=0
mut() { # <name> <file> <text, once in the file> <replacement> <command> <pattern of a failing check line>
  local name=$1 file=$2 old=$3 new=$4 cmd=$5 pat=$6
  python3 - "$file" "$old" "$new" <<'P' || { echo "$name NOT APPLIED"; S=$((S + 1)); return; }
import sys
f,o,n=sys.argv[1:4]; s=open(f).read()
if s.count(o)!=1: sys.exit(1)
open(f,'w').write(s.replace(o,n))
P
  out=$(bash -c "$cmd" 2>&1); rc=$?
  git checkout -q -- "$file"
  hits=$(printf '%s\n' "$out" | grep -a -E "$pat" | head -3 | cut -c1-160 | tr '\n' '|')
  if [ $rc != 0 ] && [ -n "$hits" ]; then echo "$name KILLED rc=$rc: $hits"; K=$((K + 1)); else echo "$name SURVIVED rc=$rc $hits"; S=$((S + 1)); fi
}
FB=tools/pr/figure_block.py; FBT="python3 tools/pr/figure_block.py --self-test"
mut fb-open-marker-not-refused $FB '        if line.startswith(MARKER):' '        if False:' "$FBT" '^  FAIL'
mut fb-stray-close-not-refused $FB '            if not opened:' '            if False:' "$FBT" '^  FAIL'
mut fb-close-does-not-reset $FB '            opened = False' '            pass' "$FBT" '^  FAIL'
mut fb-strip-deletes-nothing $FB '        del lines[i:j + 1]' '        pass' "$FBT" '^  FAIL'
mut fb-strip-writes-always $FB '    if n:
        open(body_path, "w", encoding="utf-8").write(out)' '    open(body_path, "w", encoding="utf-8").write(out + "x")' "$FBT" '^  FAIL'
PL=tools/policy/policy_lint.mjs; PLT="node tools/policy/policy_lint.mjs"
mut pl-figure-return-empty $PL "      if (!opened) msgs.push(\`line \${i + 1}: a figure-block close marker with no block above it; delete the line\`)
      opened = false
    }
  })
  return msgs" "      opened = false
    }
  })
  return []" "$PLT" 'VACUOUS'
mut pl-close-arm-gone $PL "      if (!opened) msgs.push(" "      if (false) msgs.push(" "$PLT" 'VACUOUS'
AG="python3 -I tools/policy/agreement_py.py --out $W/ag.json && node tools/policy/agreement.mjs --only pairs --py-json $W/ag.json"
mut ag-js-reader-skips-malformed $PL "    if (line.startsWith('<!-- figure-block')) {" "    if (line.startsWith('<!-- figure-block: ')) {" "$AG" 'divergent=[1-9]|DIVERGENT'
mut ag-py-reader-skips-close $FB '            if not opened:' '            if False:' "$AG" 'divergent=[1-9]|DIVERGENT'
BL=tools/policy/brief_lint.mjs; BLT="node tools/policy/brief_lint.mjs"
mut bl-ambiguous-is-moved $BL '    if (at.length === 1) {' '    if (at.length >= 1) {' "$BLT" 'VACUOUS'
mut bl-moved-stays-error $BL "      return { ok: true, warn: true, movedTo: to," "      return { ok: false, movedTo: to," "$BLT" 'VACUOUS'
mut bl-range-loses-length $BL 'end: end ? Math.min(lines.length, at[0] + (end - start)) : undefined' 'end: end ? at[0] : undefined' "$BLT" 'VACUOUS'
mut bl-twice-not-refused $BL "    if (out.split(was).length !== 2) {" "    if (out.split(was).length < 2) {" "$BLT" 'VACUOUS'
mut bl-repin-collects-nothing $BL "    if (r.movedTo && repins) {
      const sep = m[0].slice(token.length" "    if (false) {
      const sep = m[0].slice(token.length" "$BLT" 'VACUOUS'
mut fb-close-does-not-reset $FB '            opened = False' '            pass' "$FBT" '^  FAIL'
mut ag-js-close-does-not-reset $PL "      opened = false
    }
  })" "    }
  })" "$AG" 'divergent=[1-9]|DIVERGENT'
echo "RESULT killed=$K"
echo "RESULT survived_or_stale=$S"
[ "$S" = 0 ]
