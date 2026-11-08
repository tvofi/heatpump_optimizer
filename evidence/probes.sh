#!/bin/bash
# reviewer's own probe driver (disclosed): runs HOOK end to end over stdin
HOOK=$1; T=$(mktemp -d); mkdir -p $T/state $T/orch $T/other
for r in orch other; do git -C $T/$r init -q; git -C $T/$r -c user.name=a -c user.email=a@b commit -q --allow-empty -m i; done
echo $T/orch > $T/state/orch-checkout; O=$T/orch
p() { # want cwd command
  rc=$(python3 -c 'import json,sys;print(json.dumps({"tool_name":"Bash","cwd":sys.argv[1],"tool_input":{"command":sys.argv[2]}}))' "$2" "$3" | HPO_STATE_DIR=$T/state bash $HOOK >/dev/null 2>&1; echo $?)
  [ "$rc" = "$1" ] && s=ok || s=FAIL; printf '%s want=%s rc=%s  %s\n' $s $1 $rc "$3"
}
o=$T/other
echo "# prior verdict 6718280627 probes (cwd: other repo)"
p 2 $o "if true; then git -C $O pull; fi"
p 2 $o "if false; then :; else git -C $O pull; fi"
p 2 $o "if false; then :; elif git -C $O pull; then :; fi"
p 2 $o "for x in 1; do git -C $O pull; done"
p 2 $o "while git -C $O pull; do :; done"
p 2 $o "until git -C $O pull; do :; done"
p 2 $o "{ git -C $O pull; }"
p 2 $o "pushd $O && git pull"
p 2 $o "pushd $O >/dev/null; git reset --hard"
echo "# kill arm"
p 2 $o 'if true; then pkill x; fi'
p 2 $o '{ pkill x; }'
p 2 $o 'for i in 1; do pkill x; done'
p 2 $o 'while true; do killall y; done'
echo "# null controls"
p 0 $o "git -C $O status"
p 0 $O "echo then git pull"
p 0 $o "echo then pkill x"
p 0 $o "echo { pkill x }"
p 0 $o "for x in pkill killall; do echo \$x; done"
p 0 $o "git -C $O log --format='{ then do }'"
p 0 $o "if [ -f x ]; then echo pkill; fi"
p 0 $o "kill 1234"
p 2 $O "git pull"
echo "# new-construct probes beyond the block (class opening, informational)"
p 2 $o "f() { pkill x; }"
p 2 $o "function f { pkill x; }"
p 2 $o "coproc pkill x"
p 2 $o "case a in a) git -C $O pull;; esac"
p 2 $o "select x in 1; do git -C $O pull; done"
p 2 $o "[[ -d x ]] && git -C $O pull"
rm -rf $T
