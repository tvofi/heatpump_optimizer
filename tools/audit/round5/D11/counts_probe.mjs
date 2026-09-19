// D11 round 5 -- drive the production ruleset reader `counts.mjs:liveRequiredContexts`
// against a stubbed `gh`, so the same production module can be asked twice with
// two different ruleset documents. Called by ruleset.py; not run on its own.
//
//   STUB_DIR=<dir with branch.json + ruleset.json> PATH=<dir with stub gh>:$PATH \
//     node counts_probe.mjs <repo-root>
//
// Prints one JSON object: the value `liveRequiredContexts()` returned, plus its
// reason string when it returned null.
import path from 'node:path'
import { pathToFileURL } from 'node:url'

const [root] = process.argv.slice(2)
const mod = await import(pathToFileURL(path.join(root, '.claude/workflows/counts.mjs')).href)
const value = mod.liveRequiredContexts()
console.log(JSON.stringify({ value, why: mod.liveRequiredContextsWhy() }))
