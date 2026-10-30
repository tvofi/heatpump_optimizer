Fix review: merge c2578bfa2cbdb6e367cc77cd58afbd52378f3d00

bus-nonce: 98910504ef873813771120ca3ca20f04

## Round

Round 1: no earlier verdict exists for this PR.

## Findings

- Surviving mutant m5 (`ev/mutant_m5.diff`): in "Publish the release once its asset is on it", `grep -Fqx "${ASSET}"` becomes `grep -Fqx "${ASSET}" || true`, so the step publishes even when the asset is missing. `tests/entities.py` stays green: 2487 of 2487 pass (`ev/entities_m5.txt`). The draft/publish pin checks only that `--json assets` and `--draft=false` appear in that order; it never runs the guard. The guarantee the body claims still holds without the guard. `gh release create TAG <asset> --draft` exits non-zero when the asset upload fails, so the job stops before the publish step. The guard is defence in depth, and only its pin is weak. Carry: dismissed: redundant with gh release create's own non-zero exit on a failed asset upload; the pin is shape-only, which does not move a guarantee
- Owner-only tasks owed after the merge, named in the body: the hacs/default catalog PR from tvofi's account once a release carries the asset, and a 2026.11 beta install test. No seat can run either. Carry: dismissed: owner-only (tvofi), recorded in the PR body's follow-ups; no seat can execute them

## Evidence

- Head reviewed: c2578bfa2cbdb6e367cc77cd58afbd52378f3d00 (`ev/HEAD.txt`). Re-read with `git ls-remote` just before writing this verdict: still the head. The body's head section names this SHA.
- Role file: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Review packet rendered at this head. Refusals: none. Gate digest: green.
- Merge with origin/main b646e8306: `git merge-tree --write-tree` exit 0, tree 99507b03f (`ev/merge_tree.txt`). No conflict, and no claim files were touched.
- `VERSION`, `RELEASE_NOTES.md` and the manifest `version` are untouched in the three-dot diff (merge base aced2589).
- Claims: the diff touches no golden or claim file. `tests/env_drift.py --claims-only` rc=0 (`ev/env_drift_claims.txt`).
- `tests/entities.py` at the head: ALL 2487 ENTITY CHECKS PASSED, rc=0, all four new checks ok (`ev/entities_head.txt`).
- RESULT mutation m1 (the body's mutant: hacs.json filename `heatpump-optimizer.zip`): rc=1. FAIL "hacs.json names the release asset release.yml uploads, with zip_release". Reproduces the body.
- RESULT mutation m2 (`--draft` removed from create): rc=1. FAIL "the release is a draft carrying the asset ...".
- RESULT mutation m3 (build archives the whole commit, not the subtree): rc=1. FAIL "the release ZIP holds the integration folder at its root ..." (the ZIP carries a custom_components/ prefix).
- RESULT mutation m4 (check step's filename comparison deleted): rc=1. FAIL on the same check ("the check step passes a hacs.json naming another file"), so the null control inside it works.
- RESULT mutation m5: survives; see Findings.
- Figures re-derived (`ev/figures.txt`):
  - Tracked bytes at e5ddba1fa: 119233983. dev/: 88090351. tar at e5ddba1fa: 125255680. All match the body.
  - The body's "head" tar 125265920, ZIP 1404633 and unpacked 4317032 match the authored code head e5cdf4316 exactly.
  - At the reviewed head c2578bf (after the main merges) the values are tar 125562880, ZIP 1406807 and unpacked 4322263.
  - The conclusion holds at every head: the tar is over 104857600 B, the asset is far under it, and `manifest.json` sits at the ZIP root.
- C111 count of 19: re-derived by running `dev/audit/rounds/round4/D6/claims.py` at the head in a clean worktree. The tree stays byte-identical, and the committed claims.md reads 19 (`ev/d6_claims_run.txt`).
- Finder's harness: none. This is an owner-requested feature (R10-MARKETPLACE), not an audit finding. The four committed checks in `tests/entities.py` serve as its harness, and I drove them with m1–m5. I built no instrument of my own.
- Class enumeration (step 6): I grepped README.md, docs/ and the integration for install wording that names HACS without the Marketplace. Every remaining hit is the HACS-before-2026.11 section, the HACS badge, a CSS class, or quality_scale's "HACS validate green", which is still true. I found no unhandled install seam.
- CI at this head, from the PR check-runs API (`ev/checks_head.txt`): all 42 runs are completed, each concluding success or skipped. Among them, `pr-contract` (started after every other run had concluded), gate, validate-hacs, hassfest, mutation and nightly-status are success. No check is red at this head.
- The body answers the `nightly-status` red from earlier heads, which was main's slow lane (cause: #2971), and names `harness_headers.py` as local CPU-bound container noise.
- Forward-carry: the body says none, and the diff changes no later stage's working method.
