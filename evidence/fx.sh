# usage: source fx.sh <prepr.sh path> -> defines the slice's functions and lists from that file
P=$1
for fn in pinned_touched figures_check privacy_line claims_reg_line fill_red diff_paths; do
  eval "$(awk -v n="$fn() {" 'index($0, n) == 1 {on=1} on {print} on && /^}$/ {exit}' "$P")"
done
eval "$(awk "/^WAVE_INPUTS='/{on=1} on{print} on && /'\$/ && !/^WAVE_INPUTS='.*[^']\$/{exit}" "$P")"
eval "$(awk "/^CLAIMS_DOCS='/{on=1} on{print} on && /'\$/ && !/^CLAIMS_DOCS='[^']*\$/{exit}" "$P")"
eval "$(grep '^CLAIMS_GEN=' "$P")"
