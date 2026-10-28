# Sources only gh_transient from the head's app_approve.sh and classifies the probe lines.
src=$(sed -n '/^gh_transient() {/,/^}/p' "$1")
eval "$src"
for l in 'error connecting to api.github.com' \
         'gh: API rate limit exceeded for installation ID 1. (HTTP 403)' \
         'gh: You have exceeded a Secondary Rate Limit (HTTP 403)' \
         'gh: Bad Gateway (HTTP 520)'; do
  if gh_transient "$l"; then echo "transient | $l"; else echo "refuse    | $l"; fi
done
