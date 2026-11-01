#!/bin/bash
# R10-FLY-RAISE-REVIEWABLE (P348): the real-ref control for `bus.sh dispatch`'s
# review-carry refusal. Runs <checkout>/tools/audit/seat/bus.sh dispatch at
# <head> with --reviewed-head <reviewed>, against the live verdict/<pr> ref on
# origin, from the current checkout (which must have both shas). Only the
# classifier and the packet renderer are stubbed (GREEN, a packet naming the
# head); state, ledger and the past-three log go to a temporary directory, so a
# minted nonce is never recorded anywhere a seat reads and nothing is posted.
# --past-three is passed so a PR past three rounds reaches the carry test.
#
#   bash dev/audit/harnesses/r10_fly_raise_reviewable_carry.sh <checkout> <pr> <reviewed> [<head>]
#
# Prints `carry: MINTS rc=0` or `carry: REFUSED rc=N <reason>`.
# Control: #3045, 9ef51b82 -> 9ef51b82 (latest verdict blocked): REFUSED (CARRY)
# at the base, MINTS at the head. Null: #2962, 9ce0179f -> 9ce0179f (latest
# verdict merge): REFUSED (CARRY) at both ends.
set -u
co=$1 pr=$2 rh=$3 h=${4:-$3}
T=$(mktemp -d) || exit 2
trap 'rm -rf "$T"' EXIT
printf 'echo "GREEN $2 pending: none red: none"\n' > "$T/classifier"
cat > "$T/packer" <<'P'
while [ $# -gt 0 ]; do case $1 in --head) h=$2; shift 2 ;; --out) o=$2; shift 2 ;; *) shift ;; esac; done
mkdir -p "$(dirname "$o")" && printf '# Review packet\nhead: %s\n' "$h" > "$o"
P
out=$(HPO_BUS_STATE=$T/state HPO_BUS_LEDGER=$T/ledger/cloud-relay.log HPO_BUS_CLASSIFY="bash $T/classifier" \
      HPO_BUS_PACKER="bash $T/packer" bash "$co/tools/audit/seat/bus.sh" dispatch "$pr" "$h" harness-probe \
      --reviewed-head "$rh" --past-three "harness probe, scratch state" 2>&1); rc=$?
printf '%s\n' "$out" | grep -E '^bus: (review-carry|REFUSE)' | sed 's/^/  /'
if [ $rc = 0 ]; then echo "carry: MINTS rc=0"
else echo "carry: REFUSED rc=$rc $(printf '%s\n' "$out" | grep -o 'review_carry: CARRY\|cannot read[^,]*' | head -n 1)"; fi
