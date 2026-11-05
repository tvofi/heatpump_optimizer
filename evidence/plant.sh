#!/bin/bash
# Reviewer's own harness (not the fixer's): plants commits with Claude identities and judges them
# with ref_privacy.py guard from tree $1. Prints RESULT lines.
T=$1; RP=$T/tools/audit/seat/ref_privacy.py; S=$(mktemp -d)
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
X="GIT_AUTHOR_NAME=hpo-fixer GIT_AUTHOR_EMAIL=hpo-fixer@users.noreply.github.com GIT_COMMITTER_NAME=hpo-fixer GIT_COMMITTER_EMAIL=hpo-fixer@users.noreply.github.com"
git init -q --bare $S/o.git; git init -q -b main $S/r; cd $S/r; git remote add origin $S/o.git
env $X git commit -q --allow-empty -m base; git push -q origin main; git fetch -q origin
guard() { python3 -I "$RP" guard --ref fix/x --commits HEAD --over refs/remotes/origin/main -C $S/r >/dev/null 2>$S/err; echo $?; }
CL="Claude"; CE="noreply@anthropic.com"
for arm in author committer both trailer control; do
  git reset -q --hard origin/main
  case $arm in
    author) env $X GIT_AUTHOR_NAME=$CL GIT_AUTHOR_EMAIL=$CE git commit -q --allow-empty -m "$arm";;
    committer) env $X GIT_COMMITTER_NAME=$CL GIT_COMMITTER_EMAIL=$CE git commit -q --allow-empty -m "$arm";;
    both) env $X GIT_AUTHOR_NAME=$CL GIT_AUTHOR_EMAIL=$CE GIT_COMMITTER_NAME=$CL GIT_COMMITTER_EMAIL=$CE git commit -q --allow-empty -m "$arm";;
    trailer) env $X git commit -q --allow-empty -m "$arm" -m "Co-Authored-By: Claude <noreply@anthropic.com>";;
    control) env $X git commit -q --allow-empty -m "$arm";;
  esac
  rc=$(guard); echo "RESULT plant=$arm rc=$rc why=$(head -c 160 $S/err | tr '\n' ' ')"
  if [ $arm != control ]; then
    env $X git commit -q --amend --allow-empty --reset-author -m "$arm re-authored"
    echo "RESULT plant=$arm-reauthored rc=$(guard)"
  fi
done
# history held by main is not judged
git reset -q --hard origin/main
env $X GIT_AUTHOR_NAME=$CL GIT_AUTHOR_EMAIL=$CE GIT_COMMITTER_NAME=$CL GIT_COMMITTER_EMAIL=$CE git commit -q --allow-empty -m "claude on main"
git push -q origin HEAD:main; git fetch -q origin
env $X git commit -q --allow-empty -m "clean over"
echo "RESULT plant=main-held-claude+clean-top rc=$(guard) why=$(head -c 160 $S/err | tr '\n' ' ')"
rm -rf $S
