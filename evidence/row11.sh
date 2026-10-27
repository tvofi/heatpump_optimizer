  # shellcheck disable=SC2086 # CLAIMS_INPUTS is one path per line
  git ls-tree -r --name-only HEAD -- $CLAIMS_INPUTS "$CLAIMS_GEN" > "$WF/arch" 2>/dev/null
  miss=""
  for p in $CLAIMS_INPUTS "$CLAIMS_GEN"; do
    grep -q -e "^$p\$" -e "^$p/" "$WF/arch" || miss="$miss $p"
  done
  st "$miss" "" "6g's copy pathspec names only paths HEAD holds (a rename refuses the copy, never grades short)"
