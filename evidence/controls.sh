#!/bin/bash
# usage: controls.sh <shimdir> <outfile>   -- every gh is the shim in <shimdir>, real gh is the stub
SH=$1; OUT=$2; O=$(cd "$(dirname "$0")" && pwd); WT=$O/../wt
K=$(printf '%s%s%s' Re vo ked); FX=fixture-mandate-0000; B="$K mandate $FX"
printf '{"query":"mutation { addComment }"}' > $O/gq.json; printf '{"body":"x"}' > $O/in.json
PY=/opt/hpo/venv-ci/bin/python3
n=0; bad=0
run() { # run <expect refuse|pass> <label> <cmd...>
  local exp=$1 lab=$2; shift 2; n=$((n+1)); local L=$O/log.$n; : > $L
  env -i HOME=$O/home PATH=$SH:$O/stub:/usr/bin:/bin STUBLOG=$L HPO_STATE_DIR=$O/state "$@" >/dev/null 2>$O/err.$n; local rc=$?
  local got; if [ -s $L ]; then got=pass; else got=refuse; fi
  local res=ok; [ "$got" = "$exp" ] || { res=MISMATCH; bad=$((bad+1)); }
  printf '%-8s exp=%-6s got=%-6s rc=%s  %s | stub: %s\n' "$res" "$exp" "$got" "$rc" "$lab" "$(tr '\n' ';' < $L | sed "s/$K/<KILL>/g")" >> $OUT
}
R=refuse; P=pass
run $R "planted raw api POST kill pairing" gh api -X POST repos/o/r/issues/201/comments -f "body=$B"
run $R "implicit POST via -f" gh api repos/o/r/issues/201/comments -f "body=$B"
run $R "leading slash + trailing slash" gh api -X POST /repos/o/r/issues/201/comments/ -f body=x
run $R "--method POST" gh api --method POST repos/o/r/issues/201/comments -f body=x
run $R "-XPOST joined" gh api -XPOST repos/o/r/issues/201/comments -f body=x
run $R "--method=post lower" gh api --method=post repos/o/r/issues/201/comments --raw-field=body=x
run $R "full URL" gh api https://api.github.com/repos/o/r/issues/201/comments -f body=x
run $R "leading zero 0201" gh api repos/o/r/issues/0201/comments -f body=x
run $R "%-encoded 201" gh api repos/o/r/issues/%32%30%31/comments -f body=x
run $R "dot-dot from 202" gh api repos/o/r/issues/202/../201/comments -f body=x
run $R "double slash" gh api repos/o/r/issues/201//comments -f body=x
run $R "query + anchor" gh api "repos/o/r/issues/201/comments?a=1#b" -f body=x
run $R "ISSUES upper" gh api repos/o/r/ISSUES/201/comments -f body=x
run $R "COMMENTS upper" gh api repos/o/r/issues/201/COMMENTS -f body=x
run $R "mixed case" gh api repos/o/r/Issues/201/Comments -f body=x
run $R "%-encoded upper ISSUES" gh api repos/o/r/%49SSUES/201/comments -f body=x
run $R "PATCH comment by id" gh api -X PATCH repos/o/r/issues/comments/123 -f "body=$B"
run $R "graphql mutation" gh api graphql -f "query=mutation { addComment(input:{subjectId:\"x\",body:\"$B\"}) { clientMutationId } }"
run $R "graphql MUTATION upper" gh api graphql -f "query=MUTATION { addComment }"
run $R "graphql from file" gh api graphql -F query=@$O/gq.json
run $R "graphql via --input" gh api graphql --input $O/gq.json
run $R "--input body to 201" gh api repos/o/r/issues/201/comments --input $O/in.json
run $R "method-override header" gh api repos/o/r/issues/201/comments -H "X-HTTP-Method-Override: POST"
run $R "unknown api flag" gh api --foo repos/o/r/issues/201/comments
run $R "issue comment 201 kill pairing" gh issue comment 201 --body "$B"
run $R "issue comment --repo first" gh issue comment --repo o/r 201 -b x
run $R "issue comment --repo last" gh issue comment 201 -b x --repo o/r
run $R "issue comment -R= form" gh issue comment 201 --repo=o/r --body=x
run $R "issue comment URL" gh issue comment https://github.com/o/r/issues/201 -b x
run $R "issue comment #201" gh issue comment '#201' -b x
run $R "issue comment 0201" gh issue comment 0201 -b x
run $R "issue comment URL trailing slash" gh issue comment https://github.com/o/r/issues/201/ -b x
run $P "null: issue comment 202 -bx (attached value, not a cluster)" gh issue comment 202 -bx
run $R "issue comment real cluster -wb" gh issue comment -wb x 201
run $R "issue comment --" gh issue comment -- 201 -b x
run $R "issue comment two targets" gh issue comment 202 201 -b x
run $R "issue close 201 --comment" gh issue close 201 --comment x
run $R "issue close 201 -c" gh issue close 201 -c x
run $R "issue edit 201" gh issue edit 201 --body x
run $R "issue reopen 201 -c" gh issue reopen 201 -c x
run $R "issue unlisted verb" gh issue frobnicate 201
run $R "pr comment 201" gh pr comment 201 -b x
run $R "pr comment URL 201" gh pr comment https://github.com/o/r/pull/201 -b x
run $R "leading -R flag" gh -R o/r issue comment 201 -b x
run $R "unlisted subcommand" gh frobnicate 201
run $R "alias" gh alias set c 'issue comment 201'
run $R "extension" gh extension exec x
run $R "spoof: sh naming gh_comment.py" sh -c "$PY -c pass gh_comment.py; gh api repos/o/r/issues/201/comments -f body=x"
run $R "python -c not script" $PY -c "import subprocess;subprocess.run(['gh','api','repos/o/r/issues/201/comments','-f','body=x'])" $WT/tools/pr/gh_comment.py
# null controls (must reach the stub)
run $P "null: GET #201 comments" gh api repos/o/r/issues/201/comments
run $P "null: POST 202" gh api repos/o/r/issues/202/comments -f body=x
run $P "null: POST 2011" gh api repos/o/r/issues/2011/comments -f body=x
run $P "null: ISSUES/202/COMMENTS" gh api repos/o/r/ISSUES/202/COMMENTS -f body=x
run $P "null: issue comment 202" gh issue comment 202 -b x
run $P "null: issue view 201" gh issue view 201
run $P "null: pr view 5" gh pr view 5
run $P "null: workflow list" gh workflow list
run $P "null: non-issue write" gh api -X POST repos/o/r/labels -f name=x
run $P "null: api read with Accept" gh api -H 'Accept: application/json' repos/o/r/issues/201/comments
run $P "null: graphql query" gh api graphql -f 'query=query { viewer { login } }'
cd $O/home && run $P "control: normal comment via gh_comment.py" $PY $WT/tools/pr/gh_comment.py post --repo o/r --issue 201 --body-file $O/normal.md
run $P "residual (declared): exec -a argv0 spoof" bash -c "exec -a '$PY $WT/tools/pr/gh_comment.py' bash -c 'gh api repos/o/r/issues/201/comments -f body=x; true'"
echo "TOTAL $n rows, $bad mismatches" >> $OUT
