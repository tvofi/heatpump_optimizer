Carry 38 (the Card 7 ruling) is already implemented on main; this is a body-only close by evidence, no code change.

Evidence at 8124343607cea8683983bf5e1005e4b27f55d502:
- renderer and registry: tools/pr/figure_block.py, tools/pr/figure_registry.json (scope-line, structure-ratchet, merge-base), commits 42e179c1, 5fb031fa
- render-and-compare step: .github/workflows/pr-contract.yml:383 (figure_block.py verify, read-only, base copy)
- checkPrBody offline half: tools/policy/policy_lint.mjs:7081-7113; template: .github/PULL_REQUEST_TEMPLATE.md:24
- figure_lint.mjs header narrowed: tools/policy/figure_lint.mjs:18-23
- closures: tests/closures.json:1951; body writer: tools/audit/seat/body_push.sh:159, tools/pr/prepr.sh:263,1826
- self-test pinned: governance.yml:571, field_coverage.mjs:379
- second item: LEGACY_CONTROL_CAP=14 and assertLegacyControl at tools/policy/brief_lint.mjs:965,1456,1660; cap accepted as the standing answer.

Carry 38: implemented at 8124343607cea8683983bf5e1005e4b27f55d502. Carry: dismissed: implemented at 8124343607cea8683983bf5e1005e4b27f55d502

## Head

8124343607cea8683983bf5e1005e4b27f55d502

## Mutation proof

n/a: no code change; the renderer's own mutants live in figure_block.py --self-test (governance.yml:571).

## Null control

n/a: body-only handoff; the unmodified tree is main at 8124343607cea8683983bf5e1005e4b27f55d502.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
