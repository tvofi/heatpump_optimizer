#!/bin/bash
# cases2.sh <shimdir>: the second-round reviewer's further spellings, offline against the stub
O=$(cd "$(dirname "$0")" && pwd); S=${1:-$O/shim}; R=$O/run.sh
p1=Rev; p2=oked; K="$p1$p2 mandate fixture-mandate-0000"
P=repos/o/r/issues/201/comments
echo "== further refusals (expect refuse)"
$R $S dashdash-path refuse -- api -f body=x -- $P
$R $S repositories-id refuse -- api repositories/123/issues/201/comments -f body=x
$R $S pct-lower refuse -- api repos/o/r/issues/%32%30%31/comments -f body=x
$R $S pct-path-comments refuse -- api repos/o/r/issues/201/%63omments -f body=x
$R $S api-fields-method-lower refuse -- api -X Post $P -F body=@f
$R $S api-dot-segment refuse -- api repos/o/r/./issues/201/./comments -f body=x
$R $S api-input-eq refuse -- api --input=f.json $P
$R $S api-host-flag refuse -- api --hostname github.com $P -f body=x
$R $S issue-comment-edit-last refuse -- issue comment 201 --edit-last -b x
$R $S issue-comment-body-file-eq refuse -- issue comment --body-file=f 201
$R $S issue-comment-Ff refuse -- issue comment -Ff 201
$R $S issue-comment-url-query refuse -- issue comment 'https://github.com/o/r/issues/201?x=1' -b x
$R $S issue-comment-plus refuse -- issue comment +201 -b x
$R $S issue-comment-repo-eq refuse -- issue comment --repo=o/r 201 -b x
$R $S issue-comment-pull-url refuse -- issue comment https://github.com/o/r/pull/201 -b x
$R $S issue-close-comment-201 refuse -- issue close 201 --comment "$K"
$R $S issue-close-c-201 refuse -- issue close 201 -c x
$R $S issue-reopen-comment-201 refuse -- issue reopen 201 --comment x
$R $S alias-word refuse -- c201 -b x
echo "== further null controls (expect pass)"
$R $S get-201-paginate pass -- api --paginate $P
$R $S issue-close-202-comment pass -- issue close 202 --comment x
$R $S post-2010 pass -- api repos/o/r/issues/2010/comments -f body=x
$R $S issue-comment-1201 pass -- issue comment 1201 -b x
