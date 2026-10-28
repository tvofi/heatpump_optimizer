# probe: classify edge lines with original vs mutant gh_transient, sourced from a file
f=$1; shift
eval "$(sed -n '/^gh_transient() {/,/^}/p' "$f")"
for l in "$@"; do x=$(printf '%b' "$l"); if gh_transient "$x"; then r=transient; else r=refuse; fi; printf '%s\t%s\n' "$r" "$l"; done
