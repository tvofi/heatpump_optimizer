#!/bin/bash
# Reviewer-built harness for PR #2075 round 4. NOT the fixer's: this script
# builds its own fixture repository and its own attack set, and runs two
# independent copies of tools/pr/app_approve.sh (origin/main's and the head's)
# plus mutated copies of the head's, against every attack.
#
# usage: build_fixtures.sh <workdir>
# Emits <workdir>/heads.env with V=<verdict sha> and one var per attack head.
set -uo pipefail

W=${1:?usage: build_fixtures.sh <workdir>}
HEADWT=${HEADWT:?HEADWT must name the head worktree}
rm -rf "$W"; mkdir -p "$W"

. "$HEADWT/tests/throwaway_git.sh"
throwaway_git_env

g() { git -C "$W/clone" -c push.negotiate=false "$@"; }
throwaway_git_init "$W/remote.git" -q --bare
throwaway_git_init "$W/clone" -q -b main
g remote add origin "$W/remote.git"

BOT_NAME='github-actions[bot]'
BOT_EMAIL='41898282+github-actions[bot]@users.noreply.github.com'
as_bot() {
  GIT_AUTHOR_NAME="$BOT_NAME" GIT_AUTHOR_EMAIL="$BOT_EMAIL" \
  GIT_COMMITTER_NAME="$BOT_NAME" GIT_COMMITTER_EMAIL="$BOT_EMAIL" \
    g commit -q "$@"
}
row() { printf '{"anchor":"%s","killed_by":"t.py","old":"o","reason":"%s"}\n' "$1" "$2"; }

# ---- main ------------------------------------------------------------------
seq 1 40 > "$W/clone/a.txt"
echo b > "$W/clone/b.txt"
printf '{"cop_loc": 100}\n' > /dev/null
mkdir -p "$W/clone/tests"
echo 'led.json merge=ledgermerge' > "$W/clone/.gitattributes"
g add -A; g commit -qm m0
MAIN0=$(g rev-parse HEAD)

# ---- the branch, and the verdict head V ------------------------------------
# The branch's own reviewed diff: one line of a.txt AND one ledger row AND one
# line of tests/mutation_budgets.json (so the single-file bot_paths entry has
# reviewed content to attack too).
g checkout -qb fix "$MAIN0"
sed -i.bak 's/^5$/five/' "$W/clone/a.txt" && rm "$W/clone/a.txt.bak"
mkdir -p "$W/clone/tests/mutation_ledger/killed_by"
row tests/mutation_ledger/killed_by/row.json reviewed > "$W/clone/tests/mutation_ledger/killed_by/row.json"
mkdir -p "$W/clone/tests"; printf '{"m1": 1}\n' > "$W/clone/tests/mutation_budgets.json"
g add -A; g commit -qm "fix: own reviewed change"
V=$(g rev-parse HEAD)

g checkout -q main; g push -q origin main

# ---- attacks, each a first-parent descendant of V --------------------------
# A2: the bot REWRITES the reviewed row.
g checkout -q --detach "$V"
row tests/mutation_ledger/killed_by/row.json 'bot rewrite' > "$W/clone/tests/mutation_ledger/killed_by/row.json"
g add -A; as_bot -m "ci: pin killed mutants"; A2=$(g rev-parse HEAD)

# A3: the bot DELETES the reviewed row.
g checkout -q --detach "$V"
rm "$W/clone/tests/mutation_ledger/killed_by/row.json"
g add -A; as_bot -m "ci: pin killed mutants"; A3=$(g rev-parse HEAD)

# A9: the bot ADDS a file literally named `*` under the subtree AND rewrites the
# reviewed row beside it -- the glob-pathspec attack.
g checkout -q --detach "$V"
row 'tests/mutation_ledger/*' 'glob neighbour' > "$W/clone/tests/mutation_ledger/*"
row tests/mutation_ledger/killed_by/row.json 'glob rewrite' > "$W/clone/tests/mutation_ledger/killed_by/row.json"
g add -A; as_bot -m "ci: pin killed mutants"; A9=$(g rev-parse HEAD)

# OKADD (positive control): the bot only ADDS a fresh row. Must carry at both.
g checkout -q --detach "$V"
mkdir -p "$W/clone/tests/mutation_ledger/killed_by"
row tests/mutation_ledger/killed_by/fresh.json 'fresh' > "$W/clone/tests/mutation_ledger/killed_by/fresh.json"
g add -A; as_bot -m "ci: pin killed mutants"; OKADD=$(g rev-parse HEAD)

# OKGLOB (positive control): the bot only ADDS the file named `*`, nothing else.
g checkout -q --detach "$V"
row 'tests/mutation_ledger/*' 'only the glob file' > "$W/clone/tests/mutation_ledger/*"
g add -A; as_bot -m "ci: pin killed mutants"; OKGLOB=$(g rev-parse HEAD)

# DELREADD (reviewer's own attack): two bot commits -- one DELETES the reviewed
# row, the next RE-ADDS the same path with different content. Per commit neither
# is a rewrite; the pair is one, and the union of the two commits' exclusions is
# what the comparison actually sees.
g checkout -q --detach "$V"
rm "$W/clone/tests/mutation_ledger/killed_by/row.json"
g add -A; as_bot -m "ci: pin killed mutants"
row tests/mutation_ledger/killed_by/row.json 'delete then readd' > "$W/clone/tests/mutation_ledger/killed_by/row.json"
g add -A; as_bot -m "ci: pin killed mutants"; DELREADD=$(g rev-parse HEAD)

# BUDGET (reviewer's own attack): the bot rewrites tests/mutation_budgets.json,
# the single FILE bot_paths names, whose content the branch's own diff reviewed.
g checkout -q --detach "$V"
printf '{"m1": 999}\n' > "$W/clone/tests/mutation_budgets.json"
g add -A; as_bot -m "ci: pin killed mutants"; BUDGET=$(g rev-parse HEAD)

# OUTSIDE (control): the bot reaches past its subject's paths. Refuses at both.
g checkout -q --detach "$V"
echo b2 >> "$W/clone/b.txt"; g add -A; as_bot -m "ci: pin killed mutants"; OUTSIDE=$(g rev-parse HEAD)

# FORGE (control): the rewrite under a seat's authorship. Refuses at both.
g checkout -q --detach "$V"
row tests/mutation_ledger/killed_by/row.json 'seat rewrite' > "$W/clone/tests/mutation_ledger/killed_by/row.json"
g add -A; GIT_AUTHOR_EMAIL=seat@e GIT_COMMITTER_EMAIL=seat@e g commit -qm "ci: pin killed mutants"
FORGE=$(g rev-parse HEAD)

g checkout -q --detach "$V"

cat > "$W/heads.env" <<EOF
V=$V
A2=$A2
A3=$A3
A9=$A9
OKADD=$OKADD
OKGLOB=$OKGLOB
DELREADD=$DELREADD
BUDGET=$BUDGET
OUTSIDE=$OUTSIDE
FORGE=$FORGE
CLONE=$W/clone
EOF
cat "$W/heads.env"
