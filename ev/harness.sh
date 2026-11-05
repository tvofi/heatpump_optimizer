#!/bin/bash
# usage: harness.sh <shim-source> <gh_comment.py path>   ; offline, stub gh only
SHIM=$1; GCPY=$2
T=$(mktemp -d); mkdir -p $T/shim $T/stub $T/home
LOG=$T/stub.log
printf '#!/bin/sh\nprintf "%%s\\n" "$*" >> %s\nexit 0\n' "$LOG" > $T/stub/gh; chmod 755 $T/stub/gh
while IFS= read -r l; do [ "$l" = 'gcpy=@HPO_GH_COMMENT@' ] && l="gcpy=$(printf '%q' "$GCPY")"; printf '%s\n' "$l"; done < "$SHIM" > $T/shim/gh; chmod 755 $T/shim/gh
E="env -i HOME=$T/home PATH=$T/shim:$T/stub:/usr/bin:/bin HPO_STATE_DIR=$T/state"
W="$(printf '%s%s' 'Re' 'voked')"; KILL="body=$W mandate fixture-mandate-0000"
GQ=$T/q.graphql; echo 'mutation{addComment(input:{subjectId:"x",body:"y"}){clientMutationId}}' > $GQ
pass=0; fail=0
c() { # expect(R|P) label args...
  local want=$1 label=$2; shift 2; : > $LOG
  $E bash -c 'exec gh "$@"' gh "$@" >/dev/null 2>$T/err; local rc=$?
  local got; if [ $rc = 0 ] && [ -s $LOG ]; then got=P; elif [ $rc = 1 ] && [ ! -s $LOG ]; then got=R; else got="?rc=$rc,log=$(wc -l <$LOG)"; fi
  if [ "$got" = "$want" ]; then pass=$((pass+1)); r=OK; else fail=$((fail+1)); r=MISMATCH; fi
  printf '%-8s want=%s got=%s %s\n' "$r" "$want" "$got" "$label"
}
# sanity: stub records
$T/stub/gh harmless probe; [ "$(cat $LOG)" = "harmless probe" ] && echo "STUB-RECORDS: ok" || echo "STUB-RECORDS: FAIL"; : > $LOG
echo "TOKENS-IN-ARM: [$($E env | grep -i token)]"
c R planted-kill-post api -X POST repos/o/r/issues/201/comments -f "$KILL"
c R implicit-post api repos/o/r/issues/201/comments -f "$KILL"
c R trailing-slash api repos/o/r/issues/201/comments/ -f body=x
c R leading-slash api /repos/o/r/issues/201/comments -f body=x
c R full-url api https://api.github.com/repos/o/r/issues/201/comments -f body=x
c R leading-zero api repos/o/r/issues/0201/comments -f body=x
c R pct-encoded api repos/o/r/issues/%32%30%31/comments -f body=x
c R double-slash api repos/o/r/issues/201//comments -f body=x
c R query api 'repos/o/r/issues/201/comments?a=1' -f body=x
c R anchor api 'repos/o/r/issues/201/comments#a' -f body=x
c R dotseg api repos/o/r/issues/202/../201/comments -f body=x
c R case-ISSUES api repos/o/r/ISSUES/201/comments -f body=x
c R case-COMMENTS api repos/o/r/issues/201/COMMENTS -f body=x
c R case-Issues-Comments api repos/o/r/Issues/201/Comments -f body=x
c R case-GRAPHQL api GRAPHQL -f 'query=mutation{x}'
c R method-eq api --method=POST repos/o/r/issues/201/comments --input /dev/null
c R XPOST api -XPOST repos/o/r/issues/201/comments -f body=x
c R Fkill api repos/o/r/issues/201/comments -F "$KILL"
c R raw-field api repos/o/r/issues/201/comments --raw-field "$KILL"
c R override-header api -H 'X-HTTP-Method-Override: POST' repos/o/r/issues/201/comments
c R patch-by-id api -X PATCH repos/o/r/issues/comments/123 -f body=x
c R graphql-mutation api graphql -f 'query=mutation{addComment(input:{subjectId:"x",body:"y"}){clientMutationId}}'
c R graphql-file api graphql -F query=@$GQ
c R graphql-input api graphql --input $GQ
c R issue-comment issue comment 201 -b x
c R issue-comment-repo-first issue comment --repo o/r 201 -b x
c R issue-comment-repo-last issue comment 201 -b x --repo o/r
c R issue-comment-R issue comment -R o/r 201 -b "$KILL"
c R issue-comment-url issue comment https://github.com/o/r/issues/201 -b x
c R issue-comment-url-slash issue comment https://github.com/o/r/issues/201/ -b x
c R issue-comment-zero issue comment 0201 -b x
c R issue-comment-hash issue comment '#201' -b x
c R issue-comment-cluster issue comment -Rb o/r 201
c R issue-comment-ddash issue comment -- 201 -b x
c R issue-close-comment issue close 201 --comment x
c R issue-reopen-c issue reopen 201 -c x
c R issue-edit issue edit 201 --body x
c R pr-comment pr comment 201 -b x
c R pr-comment-url pr comment https://github.com/o/r/pull/201 -b x
c R unlisted-sub foo bar 201
c R alias-word co 201
c R extension-word my-ext 201
c R leading-flag -R o/r issue comment 201 -b x
c R issue-unknown-verb issue frobnicate 201
c R api-unknown-flag api --bogus repos/o/r/issues/201/comments -f body=x
c R api-two-paths api repos/o/r/issues/202/comments repos/o/r/issues/201/comments -f body=x
# pass-through controls
c P get-201-comments api repos/o/r/issues/201/comments
c P post-202 api -X POST repos/o/r/issues/202/comments -f body=x
c P post-2011 api repos/o/r/issues/2011/comments -f body=x
c P issue-comment-202 issue comment 202 -b x
c P issue-comment-202-body201 issue comment 202 --body 201
c P issue-view-201 issue view 201
c P issue-list issue list -R o/r --state all
c P issue-close-202 issue close 202 --comment x
c P pr-view pr view 5
c P graphql-read api graphql -f 'query=query{viewer{login}}'
c P accept-get api -H 'Accept: application/vnd.github+json' repos/o/r/issues/201/comments
c P version --version
c P run-list run list
c P workflow-run workflow run x.yml
c P git-refs api -X POST repos/o/r/git/refs -f ref=x
echo "TOTAL: $pass ok, $fail mismatch"
# known poster through gh_comment.py
printf 'normal state comment\n' > $T/body.md; : > $LOG
$E bash -c "cd $T && python3 -I $GCPY post --repo o/r --issue 201 --body-file $T/body.md" >/dev/null 2>$T/err; echo "POSTER: rc=$? stub-lines=$(wc -l < $LOG)"; sed 's/^/  stub: /' $LOG | head -5
# declared residual: exec -a spoof
: > $LOG; $E bash -c "exec -a 'python3 $GCPY' bash -c 'gh api repos/o/r/issues/201/comments -f body=x'" >/dev/null 2>&1; echo "RESIDUAL exec-a: rc=$? stub-lines=$(wc -l < $LOG)"
rm -rf $T
