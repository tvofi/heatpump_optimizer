// The PR contract for a Dependabot pull request (r10-codeql-dependabot,
// tvofi 2026-10-24: "dependabot PRs pass the gates without manual fixes").
//
// A Dependabot pull request has no seat behind it: nobody writes `## Head`,
// a mutation proof or `## Red checks`, so the engineered-fix contract
// (REQUIRED_H2 in policy_lint.mjs) refuses every one. This module replaces
// that contract with a dependency-bump contract, for one identity and one
// diff shape only, and keeps the full contract for everyone else:
//
//   1. the pull request's author is the Dependabot App (REST `dependabot[bot]`,
//      GraphQL `app/dependabot`) -- a login no user or other App can hold;
//   2. EVERY commit on the branch is Dependabot's own: author login
//      `dependabot[bot]`, committer `web-flow`, signature verified by GitHub.
//      A human commit pushed onto a Dependabot branch leaves the PR's author
//      unchanged, so the author alone would hand that commit the reduced
//      contract; the commit list closes it. An unreadable or empty list
//      refuses (fail-closed);
//   3. every changed path is a manifest that .github/dependabot.yml, read from
//      the BASE, configures (`dependabotManifests`); one other path and the PR
//      is refused, never given the full contract's chance to explain it;
//   4. no check is red: a red needs `## Red checks`, which no one will write,
//      so it keeps the pull request for a seat.
//
// The design choice: a Dependabot PR that fails any of 2-4 is REFUSED here,
// not sent back to the headings contract, because no one would ever answer
// that contract either. A seat that takes such a PR over re-opens it as the
// hpo-author App (decision 0011).

export const DEPENDABOT_AUTHORS = new Set(['dependabot[bot]', 'app/dependabot'])

// The files each ecosystem rewrites in its directory. pip is restricted to
// the requirements*.txt locks this tree installs from; github-actions to the
// workflow and composite-action files under .github/.
const ECOSYSTEM_FILES = {
  pip: (dir) => new RegExp(`^${dir}requirements[^/]*\\.txt$`),
  npm: (dir) => new RegExp(`^${dir}(?:package\\.json|package-lock\\.json)$`),
  'github-actions': () => /^\.github\/(?:workflows\/[^/]+\.ya?ml|actions\/[^/]+\/action\.ya?ml)$/,
}

const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

// The (ecosystem, directory) entries of a dependabot.yml, in file order. The
// file's own header fixes the shape this reads (`package-ecosystem:` then
// `directory:` per entry); the entities census compares this parse with a real
// YAML parse, so a shape this reader misses is a red there, not a silent drop.
export function dependabotEntries(text) {
  const out = []
  let eco = null
  for (const raw of String(text).split('\n')) {
    const line = raw.replace(/\s+#.*$/, '')
    let m = line.match(/^\s*-?\s*package-ecosystem:\s*["']?([A-Za-z0-9_-]+)["']?\s*$/)
    if (m) { eco = m[1]; continue }
    m = line.match(/^\s*directory:\s*["']?([^"'\s]+)["']?\s*$/)
    if (m && eco) { out.push({ ecosystem: eco, directory: m[1] }); eco = null }
  }
  return out
}

// One matcher per entry; an ecosystem this module does not know matches
// nothing, so configuring it in dependabot.yml without teaching this module
// leaves its PRs refused rather than waved through.
export function dependabotManifests(text) {
  return dependabotEntries(text).flatMap(({ ecosystem, directory }) => {
    const make = ECOSYSTEM_FILES[ecosystem]
    if (!make) return []
    const d = directory.replace(/^\/+|\/+$/g, '')
    return [make(d ? `${esc(d)}/` : '')]
  })
}

// `pulls/{n}/commits` reduced to `sha<TAB>author<TAB>committer<TAB>verified`.
export function parseCommits(tsv) {
  return String(tsv).split('\n').map((l) => l.trim()).filter(Boolean).map((l) => {
    const [sha = '', author = '', committer = '', verified = ''] = l.split('\t')
    return { sha, author, committer, verified: verified === 'true' }
  })
}

// [] when the pull request satisfies the dependency-bump contract; otherwise
// one message per unmet clause. `manifests` is dependabotManifests' output,
// `commits` parseCommits' (null: the list was never supplied).
export function dependencyBumpProblems({ paths = [], commits = null, red = [], manifests = [] }) {
  const out = []
  if (commits == null || !commits.length) {
    out.push('no commit list was read for this Dependabot pull request (`--commits-file`), so its commits cannot be shown to be Dependabot\'s own; refused rather than assumed')
  } else {
    const foreign = commits.filter((c) => !(c.author === 'dependabot[bot]' && c.committer === 'web-flow' && c.verified))
    if (foreign.length) {
      out.push(`commit(s) ${foreign.map((c) => c.sha.slice(0, 7)).join(', ')} on this Dependabot branch are not Dependabot's own (author dependabot[bot], committer web-flow, verified signature); a seat taking the PR over re-opens it as the hpo-author App`)
    }
  }
  if (!paths.length) out.push('the changed-path list is empty; a Dependabot pull request changes at least one manifest')
  const off = paths.filter((p) => !manifests.some((re) => re.test(p)))
  if (off.length) {
    out.push(`this Dependabot pull request changes ${off.length} path(s) no .github/dependabot.yml entry configures, including \`${off[0]}\`; the dependency-bump contract covers configured manifests only`)
  }
  if (red.length) {
    out.push(`check(s) are red at this Dependabot head (${red.join(', ')}); no one writes \`## Red checks\` for a bot, so a red keeps the pull request for a seat`)
  }
  return out
}
