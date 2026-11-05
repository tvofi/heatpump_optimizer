#!/bin/bash
# mutants.sh <tree> <ev>: each shim mutant in a copy of the tree; gh_calls self-test tail + the offline case it should flip
T=$1; E=$2; M=$(mktemp -d)
mut() { local name=$1 old=$2 new=$3 case_=$4; shift 4
  rm -rf $M/t; cp -r $T $M/t; python3 - "$M/t/tools/audit/seat/shims/seat-gh" "$old" "$new" <<'PY'
import sys; p,o,n=sys.argv[1:]; s=open(p).read(); assert o in s, o; open(p,'w').write(s.replace(o,n,1))
PY
  st=$(cd $M/t && python3 tools/audit/seat/gh_calls.py --self-test 2>&1 | tail -1)
  mkdir -p $M/shim; while IFS= read -r l; do [ "$l" = 'gcpy=@HPO_GH_COMMENT@' ] && l="gcpy=$T/tools/pr/gh_comment.py"; printf '%s\n' "$l"; done < $M/t/tools/audit/seat/shims/seat-gh > $M/shim/gh; chmod 755 $M/shim/gh
  oc=$(bash $E/run.sh $M/shim mut-$name refuse -- "$@")
  echo "MUTANT $name :: self-test: $st :: offline: $oc"; }
mut refusal-off '[ -n "$ok" ] || {' 'true || {' planted api -X POST repos/o/r/issues/201/comments -f body=x
mut body-not-skipped '-b|--body|--body-file|' '-b|' body issue comment --body x 201
mut zeros-kept 'n=${n#"${n%%[!0]*}"}' ':' zero issue comment 0201 -b x
mut trailing-slash-kept 'while [ "${w%/}" != "$w" ]; do w=${w%/}; done' ':' tslash issue comment https://github.com/o/r/issues/201/ -b x
mut write-flag-dropped '-f|-F|--field|--raw-field|--input) skip=1; prev=$a; write=1 ;;' '-f|-F|--field|--raw-field|--input) skip=1; prev=$a ;;' wf api repos/o/r/issues/201/comments -f body=x
mut tracker-0 'tracker=201' 'tracker=0' trk issue comment 201 -b x
rm -rf $M
