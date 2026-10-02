#!/bin/bash
# reviewer shim: the Actions-token view of a ruleset read (bypass_actors hidden)
if [ "$1" = api ] && [[ "$2" == *"/rulesets/"* ]]; then "/opt/homebrew/bin/gh" "$@" | jq -c 'del(.bypass_actors)'; exit ${PIPESTATUS[0]}; fi
exec "/opt/homebrew/bin/gh" "$@"
