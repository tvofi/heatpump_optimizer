_Requested by **tvofi**_

Part of #201.

## Head

`0e2ee62bca778503d16b718d69deb7cc8d4d9374` — one policy file pair: CLAUDE.md gains the Instruments section; policy_budgets.json raises its two measured caps.

## Mutation proof

n/a: policy index text. The instrument is the budget report itself: at base, CLAUDE.md measures 3459/3460 tokens and 211/211 lines (0 headroom — the section cannot land without raises); at head 3702/3702 and 229/229, policy_lint --budgets rc 0, aggregates in band.

## Null control

Reverting CLAUDE.md only (budgets kept): the budget report fails on 3459 > 3702 is impossible (smaller passes) — the true control is the reverse: the section removed with the caps kept leaves 3460 == 3702 violated downward (under-cap, always green) — so the caps are proven one-directional and the raise binds only the addition that needed it.

## Figures

- `node .claude/workflows/policy_lint.mjs --budgets` at head: rc 0; CLAUDE.md 3590/3590 tokens, 221/221 lines; always-loaded 3590 < 3849; corpus 56239 < 56539.
- The screen (git ls-files over tools/ + .claude/workflows + .claude/skills, cross-referenced against CLAUDE.md): 894 live instrument files, 0 referenced from CLAUDE.md before this edit.
- The section names: tools/audit/seat/ (13 instruments), the .claude/workflows gate-check family, tools/audit/archscore/, tools/audit/harnesses/ + tools/audit/round9/, the app_* identity tools.

## Red checks

None expected: no code, no workflows, no closures-reachable path; nightly-status answers main's scheduled state.

## Forward-carry

none

## Friction

ratchet-budgets.md: cost: the index sits at cap by construction (always-loaded), so every addition is a raise — the alternative the budgets themselves document (moving prose to a paths-scoped rule) does not apply to an index obligation, which must load unconditionally.

## Red checks

budgets refusals are the designed pre-raise state: at base the per-file caps (3460/211) and the role-policy aggregate (9414+500) refuse this section; the raises to measured (3590, 221, 9958) clear them by construction. nightly-status answers main's scheduled state.

## Approval

Labelled agent approval under mandate #201 comment 5951564627 (scope all, until 2026-10-09T12:00Z) posts after the merge verdict, per the policy-approval procedure.
