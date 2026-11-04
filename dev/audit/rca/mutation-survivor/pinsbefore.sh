# For each PR: every PR commit with a concluded `tests / mutation-pins*` run, its latest completion,
# so a measurement that existed before the blocked head was pushed can be read off.
R=repos/tvofi/heatpump_optimizer
for n in "$@"; do
  echo "=== #$n"
  for sha in $(gh api --paginate "$R/pulls/$n/commits?per_page=100" --jq '.[].sha'); do
    d=$(gh api "$R/commits/$sha" --jq '.commit.committer.date')
    p=$(gh api "$R/commits/$sha/check-runs?per_page=100" --jq '[.check_runs[]|select(.name|startswith("tests / mutation-pins"))|select(.completed_at)|.completed_at]|max // "-"')
    a=$(gh api "$R/commits/$sha/check-runs?per_page=100" --jq '[.check_runs[]|select(.name=="tests / mutation-autofix")|.conclusion]|join(",")')
    echo "${sha:0:9} pushed $d pins-concluded $p autofix $a"
  done
done
