#!/usr/bin/env bash
# The delta_S of each finding's patch set, as REPORT.md states it, plus the all-in set.
#   bash dev/audit/rounds/round10/D7/arch-s2/run_findings.sh [label ...]
# Run from the repository root. Logs under a mktemp -d root printed first.
set -u
BASE=554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef
P=dev/audit/rounds/round10/D7/arch-s2/patches
H=dev/audit/rounds/round10/D7/arch-s2/harness.py
OUT=$(mktemp -d "${TMPDIR:-/tmp}/arch-s2-findings.XXXXXX")
echo "logs: $OUT"
declare -a SETS=(
  "00_scrub:$P/00_scrub_resolves_mro.patch"
  "01_value:$P/00_scrub_resolves_mro.patch $P/01_payload_value_mixin.patch"
  "02_path:$P/00_scrub_resolves_mro.patch $P/02_payload_path_mixin.patch"
  "03_zone:$P/03_zone_setpoint_attributes.patch"
  "04_suggested:$P/04_suggested_optional.patch"
  "05_clock:$P/05_hour_clock.patch"
  "06_finite:$P/06_finite_float_owner.patch"
  "07_cyclic:$P/07_cyclic_range.patch"
  "08_page:$P/08_options_page_template.patch"
  "99_all:$P/99_combined.patch"
)
for entry in "${SETS[@]}"; do
  label=${entry%%:*}
  patches=${entry#*:}
  if [ $# -gt 0 ] && [[ " $* " != *" $label "* ]]; then continue; fi
  # shellcheck disable=SC2086
  PYTHONPATH=tests/hastub python3 "$H" --base "$BASE" $patches > "$OUT/$label.log" 2>&1
  echo "rc=$?" >> "$OUT/$label.log"
  echo "== $label"
  grep -E '^RESULT (delta_S|perturbed_delta_S|perturbed_vector_equals_baseline|admissible|[a-z_]+=[0-9]+->)|^rc=' "$OUT/$label.log"
done
