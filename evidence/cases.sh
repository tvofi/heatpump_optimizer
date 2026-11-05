#!/bin/bash
O=$(cd "$(dirname "$0")" && pwd); S=${1:-$O/shim}; R=$O/run.sh
p1=Rev; p2=oked; K="$p1$p2 mandate fixture-mandate-0000"   # kill word built at runtime from fragments
P=repos/o/r/issues/201/comments
echo "== refusals (shim dir $S)"
$R $S planted-kill refuse -- api -X POST $P -f "body=$K"
$R $S field-only refuse -- api $P -f body=x
$R $S flags-first refuse -- api -f body=x $P
$R $S leading-slash refuse -- api -X POST /$P -f body=x
$R $S full-url refuse -- api https://api.github.com/$P -f body=x
$R $S placeholder refuse -- api 'repos/{owner}/{repo}/issues/201/comments' -f body=x
$R $S querystring refuse -- api "$P?per_page=1" -f body=x
$R $S method-sep refuse -- api --method POST $P
$R $S method-eq refuse -- api --method=POST $P
$R $S XPOST refuse -- api -XPOST $P
$R $S X-lower refuse -- api -X post $P
$R $S input refuse -- api $P --input f.json
$R $S field-eq refuse -- api $P --field=body=x
$R $S raw-field refuse -- api $P --raw-field body=x
$R $S F-attached refuse -- api $P -Fbody=x
$R $S issue-201 refuse -- issue comment 201 -b "$K"
$R $S issue-repo-after refuse -- issue comment 201 --repo o/r -b x
$R $S issue-repo-before refuse -- issue comment --repo o/r 201 -b x
$R $S issue-R-before refuse -- issue comment -R o/r -b x 201
$R $S issue-hash refuse -- issue comment '#201' -b x
$R $S issue-url refuse -- issue comment https://github.com/o/r/issues/201 -b x
$R $S issue-url-anchor refuse -- issue comment 'https://github.com/o/r/issues/201#issuecomment-1' -b x
echo "== bypass probes (expect refuse)"
$R $S api-trailing-slash refuse -- api $P/ -f body=x
$R $S issue-url-trailing-slash refuse -- issue comment https://github.com/o/r/issues/201/ -b x
$R $S issue-long-body-before refuse -- issue comment --body x 201
$R $S issue-body-eq-ok refuse -- issue comment --body=x 201
$R $S issue-body-file-before refuse -- issue comment --body-file f 201
$R $S api-leading-zero refuse -- api repos/o/r/issues/0201/comments -f body=x
$R $S issue-leading-zero refuse -- issue comment 0201 -b x
$R $S api-pct refuse -- api repos/o/r/issues/%32%30%31/comments -f body=x
$R $S graphql-declared-residual refuse -- api graphql -f 'query=mutation{addComment(input:{subjectId:"I_x",body:"x"}){clientMutationId}}'
$R $S pr-comment-201 refuse -- pr comment 201 -b x
echo "== null controls (expect pass)"
$R $S get-201 pass -- api $P
$R $S get-201-explicit pass -- api -X GET $P
$R $S post-202 pass -- api $P/../../202/comments -f body=x
$R $S post-202b pass -- api repos/o/r/issues/202/comments -f body=x
$R $S post-2011 pass -- api repos/o/r/issues/2011/comments -f body=x
$R $S issue-202 pass -- issue comment 202 -b x
$R $S issue-view-201 pass -- issue view 201
$R $S patch-residual pass -- api -X PATCH repos/o/r/issues/comments/123 -f body=x
