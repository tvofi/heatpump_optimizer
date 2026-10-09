stamp_paths() { # name-only diff over VERSION, unified diffs of manifest.json and RELEASE_NOTES.md
  # Step 5's predicate, a pure function of its inputs so --self-test can
  # drive it. Prints the stamp-shaped paths it finds, space-separated; empty
  # means the branch touched no version.
  #
  # KEYED ON THE FIELD, NOT THE FILE. CLAUDE.md rule 4 forbids touching
  # "VERSION, the manifest VERSION, or the RELEASE_NOTES.md heading"; the
  # first form of this step diffed manifest.json by NAME and so refused every
  # manifest edit, including the one that adds `quality_scale` -- a predicate
  # wider than the rule it enforced, found by the first branch that made a
  # legitimate non-version manifest edit. The manifest's other keys are
  # ordinary production state; only its `version` line is the stamp's.
  local out=""
  if [ -n "${1// /}" ]; then out="VERSION"; fi
  # `grep >/dev/null`, never `grep -q`: -q exits on the first match and can
  # SIGPIPE the writer, which `pipefail` reads as no match -- a version edit
  # passed as none on a large diff (R9-RCA-prepr-tmp; the note above
  # `pinned_unrun`). A reader that drains its input cannot do that.
  if printf '%s\n' "$2" | grep -E '^[-+][[:space:]]*"version"[[:space:]]*:' >/dev/null; then
    out="${out:+$out }custom_components/heatpump_optimizer/manifest.json(version)"
  fi
  # The notes: a `## ` line added or removed is a release heading, which only
  # the stamp writes. `### ` subsections do not match, because the pattern
  # needs the space straight after two hashes.
  if printf '%s\n' "${3:-}" | grep -E '^[-+]## ' >/dev/null; then
    out="${out:+$out }RELEASE_NOTES.md(heading)"
  fi
  printf '%s' "$out"
}
