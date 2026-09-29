# Round-9 fix programme — live status for ALT v3 re-base

Measured 2026-09-29 (evening, +0200) at **origin/main `4d33b25c`** (#1771). Rev 2 was based on `5a2a62ff` (#1750). Read-only collection; nothing in the repo was changed.

## Sources

- **Rev-2 roster**: `alt/handoff/round9/state/ALT-ROSTER.json` (66 groups), byte-identical to `handoff/audit-r9-alt:handoff/round9/state/ALT-ROSTER.json` @065bd69a **and** to main's `tools/audit/round9/prestudy/ALT-ROSTER.json` (landed by #1771).
- **Live roster**: main carries **no** `.claude/workflows/wave-r9-groups.json`. `docs/HANDOVER.md` §"Round 9 in flight" on main names `handoff/audit-r9-fixplan` as the roster's home; read at tip `c5af8f3a` (2026-09-29 22:38 +0200), 66 groups, the same ids and order as rev 2. Only `resume` and four briefs differ: F6.3, F6.4, F11.4 and F11.5 carry new text.
- **Resume log**: `handoff/audit-r9-plan:handoff/round9/RESUME.md` @4c613d8c (2026-09-29 23:25 +0200).
- **#201 newest comment**: [5899374096](https://github.com/tvofi/heatpump_optimizer/issues/201#issuecomment-5899374096) (2026-09-29T21:32:49Z, "Register complete"): #1769, #1770, #1771 and #1772 merged; *"In flight: F1.6 round 2 (#1767) — its merge opens F2.4 ∥ F9.3 ∥ EG-B10."* The previous comment, [5896576410](https://github.com/tvofi/heatpump_optimizer/issues/201#issuecomment-5896576410), is the state batch listing #1751, #1763, #1764, #1765, #1766 and #1768.
- **Merged-PR record**: the first-parent `Merge pull request #N` commits on origin/main, plus `docs/delivery/*.md` on main. Open PRs from GitHub show **one** open PR, #1767. Closed PRs since 5a2a62ff are all merged; the MCP list returns `merged:false` with `merged_at` set, so git is the authority for merges.
- **Issue state**: GitHub open-issue list (70 open). Every merged group's `fixes[]` issue is closed except #1655, which F4.2 deliberately leaves open (recorded).

## Counts by live status

| live status | groups |
|---|---|
| merged | 33 (28 at rev 2 + 5 since: F1.5, EG-R0, F7.2, EG-B9, F7.4) |
| in review | 1 (R9-F1.6, PR #1767, round 2 at 929e5aa0) |
| fixing | 0 |
| blocked | 0 (F10.5 carries a `blocked_on` for the ledger-writer App identity, but it is not started, and per its own text the fixer does not wait on it) |
| not started | 31 |
| rca-done (no PR by design) | 1 (R9-EG-B0) |
| **total** | **66** |

Rev-2 counts were done 28, in-review 1, fixing 1, not-started 35, rca-done 1. The open groups have gone from 37 to **32**: 31 not started plus 1 in review.

## Disagreements

1. **R9-F1.6: the live roster says `not-started` but the group is in review round 2.** On `handoff/audit-r9-fixplan` @c5af8f3a, F1.6 has `resume.stage=not-started` with empty commit, last_step and PR, and the roster was never touched after dispatch. The other sources all say otherwise:
   - RESUME.md records dispatch at 05:23Z and draft PR #1767 at 11c1388c (14Z). CI round 2 went green at 1f477e9f, review round 1 was **blocked**, and round 2 was pushed at `929e5aa0` (21Z).
   - GitHub shows #1767 open as a draft, head `929e5aa0`. Of its 34 check-runs none has failed and `mutation` is still in progress. No GitHub reviews are posted.
   - #201's newest comment says "F1.6 round 2 (#1767) in flight".
   - The #1767 branch absorbed main only up to `7952d8f9`, so main has moved under it (#1771, a record-only merge).
2. **Rev 2, and its copy now on main, is stale on six groups.** These are F1.5 (in-review→merged #1751), F7.2 (fixing→merged #1764), EG-R0 (not-started→merged #1763), EG-B9 (not-started→merged #1765), F7.4 (not-started→merged #1766) and F1.6 (not-started→in review #1767). #1771 landed `tools/audit/round9/prestudy/ALT-ROSTER.json` byte-identical to rev 2, so main now carries a roster file with those six stale stages. It is labelled as a pre-study, but a reader can take it for the roster.
3. **No regression like rev 2 found.** For all 33 merged groups, the live roster reads `done` and its `resume.commit` equals the first-parent merge SHA on main. Every non-F1.6 group the roster calls `not-started` has no branch on origin and no open PR.
4. **The #1771 record lags.** `docs/delivery/1771.md` on main says **"open"**, although #1771 merged as `4d33b25c`: the row was written before the merge. #201's generated ledger lists #1772, #1762 and #1761 as pending a row (not overdue; 12 is the limit).
5. **The plan-of-record disposition rows lag.** On main, `docs/plan-2026-09-open-issues.md` still reads "scheduled — R9-EG-B9" for #1752/#1753, "scheduled — R9-F7.4" for #1760, "R9-EG-R0 … then R9-EG-R1" for #1759 and "R9-EG-B0 (root-cause seat, now)" for #1736, although those groups are merged or done. The delivery rows for #1763–#1766 exist and outrank them.
6. **Main's copy of the standing template is behind.** `tools/audit/round9/fixplan/standing.md` (from #1771) lacks the rule "Enumerators run INSIDE the tree" that `handoff/audit-r9-fixplan` c5af8f3a added to `handoff/round9/fix/src/standing.md` (F1.6/S3 precedent).
7. **Unstamped merges.** The last tag on main is `v6.7.10` (3490cb16, before 5a2a62ff), so all 12 merges since, including sev:high EG-B9 #1765, are unstamped. ALT §4.4 said to stamp at the next point after EG-B9. #201 5896576410 says "Stamp v6.7.11 follows when #1769/#1770/#1767 land"; #1769 and #1770 have landed and #1767 has not.

## Per-group status (66)

| group | lane | rev-2 status | live status | PR | SHA (merge / head) | evidence | disagreement |
|---|---|---|---|---|---|---|---|
| R9-F1.1 | F1 | done | merged | [#1722](https://github.com/tvofi/heatpump_optimizer/pull/1722) | `2d71759e` | git: 2d71759e "Merge pull request #1722 from tvofi/fix/r9-f1-1-jbqcyd" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1722; fixes[] [1665, 1683] all closed on GitHub | — |
| R9-F1.2 | F1 | done | merged | [#1724](https://github.com/tvofi/heatpump_optimizer/pull/1724) | `12b0df68` | git: 12b0df68 "Merge pull request #1724 from tvofi/fix/r9-f1-2-f12hk" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1724; fixes[] empty | — |
| R9-F1.3 | F1 | done | merged | [#1731](https://github.com/tvofi/heatpump_optimizer/pull/1731) | `3bae92d9` | git: 3bae92d9 "Merge pull request #1731 from tvofi/fix/r9-f1-coordinator-3" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1731; fixes[] empty | — |
| R9-F1.4 | F1 | done | merged | [#1735](https://github.com/tvofi/heatpump_optimizer/pull/1735) | `686239d2` | git: 686239d2 "Merge pull request #1735 from tvofi/fix/r9-f1-coordinator-4" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1735; fixes[] [1662, 1681] all closed on GitHub | — |
| R9-F1.5 | F1 | in-review | merged | [#1751](https://github.com/tvofi/heatpump_optimizer/pull/1751) | `c2a0448d` | git: c2a0448d "Merge pull request #1751 from tvofi/fix/r9-f1-coordinator-5" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1751; merged after 5a2a62ff; listed in #201 state batch https://github.com/tvofi/heatpump_optimizer/issues/201#issuecomment-5896576410; live roster (handoff/audit-r9-fixplan c5af8f3a) resume.stage=done: MERGED as #1751 at c2a0448d; fixes[] #1670, #1676 and #1682 confirmed closed; fixes[] [1670, 1676, 1682] all closed on GitHub | rev-2 roster (and main copy tools/audit/round9/prestudy/ALT-ROSTER.json, landed by #1771) says in-review; merged as #1751 c2a0448d |
| R9-F1.6 | F1 | not-started | in-review (round 2) | [#1767](https://github.com/tvofi/heatpump_optimizer/pull/1767) | `929e5aa0` | https://github.com/tvofi/heatpump_optimizer/pull/1767 open, draft, author hpo-author[bot], head handoff/r9-f1-coordinator-6 @929e5aa0 (pushed 2026-09-29 23:18 +0200); branch absorbed main at 7952d8f9 (c9a403fa), not 4d33b25c; PR #1767 check-runs at 929e5aa0 (read 2026-09-29): 34 runs, 0 failure; mutation still in_progress; no GitHub reviews posted; RESUME.md (handoff/audit-r9-plan 4c613d8c) 2026-09-29T21Z: review round 1 BLOCKED (harness + one real seam _fabricated_forecast); round 2 pushed at 929e5aa0, awaiting re-review; #201 newest comment https://github.com/tvofi/heatpump_optimizer/issues/201#issuecomment-5899374096: "In flight: F1.6 round 2 (#1767) -- its merge opens F2.4 // F9.3 // EG-B10" | live roster on handoff/audit-r9-fixplan still says stage=not-started with empty commit/last_step, while PR #1767 has been open since 2026-09-29T14:45Z (dispatched 05:23Z per RESUME.md) and #201 newest comment says round 2 in flight; rev-2 roster (and its copy on main, tools/audit/round9/prestudy/ALT-ROSTER.json) says not-started |
| R9-F1.7 | F1 | not-started | not started (waits on F1.6, F2.4) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-f1-coordinator-7 absent on origin | — |
| R9-F1.8 | F1 | not-started | not started (waits on F1.7) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-f1-coordinator-8 absent on origin | — |
| R9-F1.9 | F1 | not-started | not started (waits on F1.8) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-f1-coordinator-9 absent on origin | — |
| R9-F1.10 | F1 | not-started | not started (waits on F1.9, F2.4) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-f1-coordinator-10 absent on origin | — |
| R9-F1.11 | F1 | not-started | not started (waits on F1.10, F6.4) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-f1-coordinator-11 absent on origin | — |
| R9-F2.1 | F2 | done | merged | [#1694](https://github.com/tvofi/heatpump_optimizer/pull/1694) | `058e89f1` | git: 058e89f1 "Merge pull request #1694 from tvofi/fix/r9-f2-solver-1" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1694; fixes[] [1666] all closed on GitHub | — |
| R9-F2.2 | F2 | done | merged | [#1713](https://github.com/tvofi/heatpump_optimizer/pull/1713) | `9c6b923f` | git: 9c6b923f "Merge pull request #1713 from tvofi/fix/r9-f2-2-k1w278-v3" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1713; fixes[] empty | — |
| R9-F2.3 | F2 | done | merged | [#1723](https://github.com/tvofi/heatpump_optimizer/pull/1723) | `2eef524d` | git: 2eef524d "Merge pull request #1723 from tvofi/fix/r9-f2-solver-3" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1723; fixes[] [1671] all closed on GitHub | — |
| R9-F2.5 | F2 | done | merged | [#1734](https://github.com/tvofi/heatpump_optimizer/pull/1734) | `31394964` | git: 31394964 "Merge pull request #1734 from tvofi/fix/r9-f2-solver-5" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1734; fixes[] empty | — |
| R9-F2.4 | F2 | not-started | not started (ready when F1.6 merges) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-f2-solver-4 absent on origin | — |
| R9-F3.1 | F3 | done | merged | [#1691](https://github.com/tvofi/heatpump_optimizer/pull/1691) | `917f16c2` | git: 917f16c2 "Merge pull request #1691 from tvofi/fix/r9-f3-stores-1" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1691; fixes[] empty | — |
| R9-F3.2 | F3 | done | merged | [#1707](https://github.com/tvofi/heatpump_optimizer/pull/1707) | `ba60afab` | git: ba60afab "Merge pull request #1707 from tvofi/fix/r9-f3-stores-2-bmwr8c" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1707; fixes[] empty | — |
| R9-F3.3 | F3 | done | merged | [#1717](https://github.com/tvofi/heatpump_optimizer/pull/1717) | `49fc8bbe` | git: 49fc8bbe "Merge pull request #1717 from tvofi/fix/r9-f3-stores-3" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1717; fixes[] [1680] all closed on GitHub | — |
| R9-F4.1 | F4 | done | merged | [#1704](https://github.com/tvofi/heatpump_optimizer/pull/1704) | `0c9c4000` | git: 0c9c4000 "Merge pull request #1704 from tvofi/fix/r9-f4-inputs-sysid-1c" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1704; fixes[] [1673, 1684] all closed on GitHub | — |
| R9-F4.2 | F4 | done | merged | [#1718](https://github.com/tvofi/heatpump_optimizer/pull/1718) | `fab17619` | git: fab17619 "Merge pull request #1718 from tvofi/fix/r9-f4-inputs-sysid-2" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1718; fixes[] still open on GitHub: [1655]; #1655 in fixes[] deliberately left open (free-heat half carried to F1 lane) -- recorded in roster last_step, not a disagreement | — |
| R9-F5.1 | F5 | done | merged | [#1698](https://github.com/tvofi/heatpump_optimizer/pull/1698) | `5abd5f9d` | git: 5abd5f9d "Merge pull request #1698 from tvofi/fix/r9-f5-config-text-1" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1698; fixes[] [1675, 1688] all closed on GitHub | — |
| R9-F5.2 | F5 | done | merged | [#1732](https://github.com/tvofi/heatpump_optimizer/pull/1732) | `8ff6827a` | git: 8ff6827a "Merge pull request #1732 from tvofi/handoff/r9-f5-config-text-2" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1732; fixes[] [1679, 1685] all closed on GitHub | — |
| R9-F6.1 | F6 | done | merged | [#1699](https://github.com/tvofi/heatpump_optimizer/pull/1699) | `7428d87a` | git: 7428d87a "Merge pull request #1699 from tvofi/fix/r9-f6-card-1-v2" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1699; fixes[] empty | — |
| R9-F6.2 | F6 | done | merged | [#1709](https://github.com/tvofi/heatpump_optimizer/pull/1709) | `92bce7c4` | git: 92bce7c4 "Merge pull request #1709 from tvofi/fix/r9-f6-card-2-v2" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1709; fixes[] [1677] all closed on GitHub | — |
| R9-F6.3 | F6 | not-started | not started (waits on F1.8) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-f6-card-3 absent on origin | — |
| R9-F6.4 | F6 | not-started | not started (waits on F6.3, F1.8) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-f6-card-4 absent on origin | — |
| R9-F7.1 | F7 | done | merged | [#1690](https://github.com/tvofi/heatpump_optimizer/pull/1690) | `cbb8a271` | git: cbb8a271 "Merge pull request #1690 from tvofi/fix/r9-f7-entities-1" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1690; fixes[] empty | — |
| R9-F7.2 | F7 | fixing | merged | [#1764](https://github.com/tvofi/heatpump_optimizer/pull/1764) | `4f8088e8` | git: 4f8088e8 "Merge pull request #1764 from tvofi/fix/r9-f7-entities-2" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1764; merged after 5a2a62ff; listed in #201 state batch https://github.com/tvofi/heatpump_optimizer/issues/201#issuecomment-5896576410; live roster (handoff/audit-r9-fixplan c5af8f3a) resume.stage=done: MERGED as #1764 at 4f8088e8; fixes[] #1669 confirmed closed -- closed manually, the body's Fixes keyword sat in a code span; the close comment corrects the SHA; fixes[] [1669] all closed on GitHub | rev-2 roster (and main copy tools/audit/round9/prestudy/ALT-ROSTER.json, landed by #1771) says fixing; merged as #1764 4f8088e8 |
| R9-F8.1 | F8 | done | merged | [#1696](https://github.com/tvofi/heatpump_optimizer/pull/1696) | `62933b18` | git: 62933b18 "Merge pull request #1696 from tvofi/fix/r9-f8-docs-1" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1696; fixes[] [1674] all closed on GitHub | — |
| R9-F8.2 | F8 | done | merged | [#1703](https://github.com/tvofi/heatpump_optimizer/pull/1703) | `a67f4d40` | git: a67f4d40 "Merge pull request #1703 from tvofi/fix/r9-f8-docs-2" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1703; fixes[] empty | — |
| R9-F8.3 | F8 | done | merged | [#1733](https://github.com/tvofi/heatpump_optimizer/pull/1733) | `cdbca706` | git: cdbca706 "Merge pull request #1733 from tvofi/fix/r9-f8-docs-3" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1733; fixes[] [1668] all closed on GitHub | — |
| R9-F9.1 | F9 | done | merged | [#1702](https://github.com/tvofi/heatpump_optimizer/pull/1702) | `48b696c1` | git: 48b696c1 "Merge pull request #1702 from tvofi/fix/r9-f9-1-qei682" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1702; fixes[] empty | — |
| R9-F9.2 | F9 | done | merged | [#1714](https://github.com/tvofi/heatpump_optimizer/pull/1714) | `624db889` | git: 624db889 "Merge pull request #1714 from tvofi/fix/r9-f9-test-pins-2" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1714; fixes[] [1678] all closed on GitHub | — |
| R9-F9.3 | F9 | not-started | not started (ready when F1.6 merges) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-f9-test-pins-3 absent on origin | — |
| R9-F10.1 | F10 | done | merged | [#1693](https://github.com/tvofi/heatpump_optimizer/pull/1693) | `1ef6a805` | git: 1ef6a805 "Merge pull request #1693 from tvofi/fix/r9-f10-gate-infra-1" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1693; fixes[] empty | — |
| R9-F10.1b | F10 | not-started | not started (waits on F1.7) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-f10-gate-infra-1b absent on origin | — |
| R9-F10.2 | F10 | not-started | not started (waits on F10.1b) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-f10-gate-infra-2 absent on origin | — |
| R9-F10.3 | F10 | not-started | not started (waits on F10.2) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-f10-gate-infra-3 absent on origin | — |
| R9-F10.4 | F10 | not-started | not started (waits on F10.3, F1.11) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-f10-gate-infra-4 absent on origin | — |
| R9-F10.5 | F10 | not-started | not started (waits on F10.4) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-f10-gate-infra-5 absent on origin | — |
| R9-F10.6 | F10 | not-started | not started (waits on F10.5) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-f10-gate-infra-6 absent on origin | — |
| R9-F11.1 | F11 | done | merged | [#1697](https://github.com/tvofi/heatpump_optimizer/pull/1697) | `b5501cca` | git: b5501cca "Merge pull request #1697 from tvofi/fix/r9-f11-governance-1" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1697; fixes[] empty | — |
| R9-F11.2 | F11 | done | merged | [#1701](https://github.com/tvofi/heatpump_optimizer/pull/1701) | `399ef171` | git: 399ef171 "Merge pull request #1701 from tvofi/fix/r9-f11-governance-2-e9ywjb" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1701; fixes[] empty | — |
| R9-F11.3 | F11 | done | merged | [#1715](https://github.com/tvofi/heatpump_optimizer/pull/1715) | `87d780c7` | git: 87d780c7 "Merge pull request #1715 from tvofi/fix/r9-f11-governance-3" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1715; fixes[] [1648] all closed on GitHub | — |
| R9-F11.6 | F11 | done | merged | [#1720](https://github.com/tvofi/heatpump_optimizer/pull/1720) | `2d012406` | git: 2d012406 "Merge pull request #1720 from tvofi/fix/r9-f11-governance-6-v2" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1720; fixes[] [1667] all closed on GitHub | — |
| R9-F11.4 | F11 | not-started | not started (waits on F10.4) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-f11-governance-4 absent on origin | — |
| R9-F11.5 | F11 | not-started | not started (waits on F11.4) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-f11-governance-5 absent on origin | — |
| R9-EG-B0 | EG | rca-done | rca-done (no PR; RCA-1736 posted on #1736 comment 5877263448) | — | — | roster last_step unchanged since rev 2; its obligations carried into R9-EG-B1 | — |
| R9-EG-B2 | EG | not-started | not started (waits on F1.11) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-eg-surface-identity absent on origin | — |
| R9-EG-B3 | EG | not-started | not started (waits on F10.4, EG-B2) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-eg-typed-payload absent on origin | — |
| R9-EG-B4 | EG | not-started | not started (waits on F10.1b, F10.4, EG-B3) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-eg-store-version absent on origin | — |
| R9-EG-B1 | EG | not-started | not started (waits on F10.4, F2.4, F10.6, F11.5, EG-B4, EG-B5, EG-B10) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-eg-solve-inputs absent on origin | — |
| R9-EG-B6 | EG | not-started | not started (waits on EG-B1) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-eg-collaborator-interfaces absent on origin | — |
| R9-EG-B8 | EG | not-started | not started (waits on F2.4) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-eg-dhw-block-replan absent on origin | — |
| R9-EG-B5a | EG | not-started | not started (waits on F2.4, F10.4) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-eg-dhw-closure-dedupe absent on origin | — |
| R9-EG-B5 | EG | not-started | not started (waits on EG-B5a, EG-B8, F1.10, F10.4) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-eg-dhw-planner absent on origin | — |
| R9-EG-B7 | EG | not-started | not started (waits on EG-B1, EG-B6) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-eg-coordinator-seams absent on origin | — |
| R9-EG-B9 | EG | not-started | merged | [#1765](https://github.com/tvofi/heatpump_optimizer/pull/1765) | `5395394d` | git: 5395394d "Merge pull request #1765 from tvofi/handoff/r9-eg-action-copy" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1765; merged after 5a2a62ff; listed in #201 state batch https://github.com/tvofi/heatpump_optimizer/issues/201#issuecomment-5896576410; live roster (handoff/audit-r9-fixplan c5af8f3a) resume.stage=done: MERGED as #1765 at 5395394d; fixes[] #1752 and #1753 confirmed closed; fixes[] [1752, 1753] all closed on GitHub | rev-2 roster (and main copy tools/audit/round9/prestudy/ALT-ROSTER.json, landed by #1771) says not-started; merged as #1765 5395394d |
| R9-EG-B10 | EG | not-started | not started (ready when F1.6 merges) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-eg-solve-lifecycle absent on origin | — |
| R9-EG-R0 | EG | not-started | merged | [#1763](https://github.com/tvofi/heatpump_optimizer/pull/1763) | `89d1ddf5` | git: 89d1ddf5 "Merge pull request #1763 from tvofi/fix/eg-r0-register-v2" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1763; merged after 5a2a62ff; listed in #201 state batch https://github.com/tvofi/heatpump_optimizer/issues/201#issuecomment-5896576410; live roster (handoff/audit-r9-fixplan c5af8f3a) resume.stage=done: MERGED as #1763 at 89d1ddf5; fixes[] empty (data PR), so it closes nothing outright -- #1759 stays open as Part-of; fixes[] empty | rev-2 roster (and main copy tools/audit/round9/prestudy/ALT-ROSTER.json, landed by #1771) says not-started; merged as #1763 89d1ddf5 |
| R9-EG-R1 | EG | not-started | not started (waits on F11.4) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-eg-register-fold absent on origin | — |
| R9-F10.1c | F10 | not-started | not started (waits on F10.1b) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-f10-gate-infra-1c absent on origin | — |
| R9-F10.7 | F10 | not-started | not started (waits on F10.6) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-f10-loop-heartbeat absent on origin | — |
| R9-F11.7 | F11 | not-started | not started (waits on F11.5) | — | — | live roster stage=not-started; no open PR; branch handoff/r9-f11-governance-7 absent on origin | — |
| R9-F7.4 | F7 | not-started | merged | [#1766](https://github.com/tvofi/heatpump_optimizer/pull/1766) | `3defa2d5` | git: 3defa2d5 "Merge pull request #1766 from tvofi/handoff/r9-f7-entities-4" is first-parent on origin/main 4d33b25c; https://github.com/tvofi/heatpump_optimizer/pull/1766; merged after 5a2a62ff; listed in #201 state batch https://github.com/tvofi/heatpump_optimizer/issues/201#issuecomment-5896576410; live roster (handoff/audit-r9-fixplan c5af8f3a) resume.stage=done: MERGED as #1766 at 3defa2d5; fixes[] #1760 confirmed closed -- the N-name-sort barrier (declared families + contiguity check) landed; fixes[] [1760] all closed on GitHub | rev-2 roster (and main copy tools/audit/round9/prestudy/ALT-ROSTER.json, landed by #1771) says not-started; merged as #1766 3defa2d5 |

## Merges on main since 5a2a62ff that belong to no roster group (7 of 12)

The 5 affiliated merges are #1751 F1.5, #1763 EG-R0, #1764 F7.2, #1765 EG-B9 and #1766 F7.4.

| PR | merge | what it changed |
|---|---|---|
| [#1761](https://github.com/tvofi/heatpump_optimizer/pull/1761) | `d9d5e9f1` | Record: `docs/plan-2026-09-open-issues.md` only (+25/−2). ALT rev-2 adoption dispositions for #1752–#1760 and the #1070 row corrected. |
| [#1762](https://github.com/tvofi/heatpump_optimizer/pull/1762) | `f74e981a` | Record: plan +1 line. Register decision 3: the P2/I5 split is deferred to round 10 as a detector-first pre-study (tvofi 2026-09-29). |
| [#1768](https://github.com/tvofi/heatpump_optimizer/pull/1768) | `ee13f67e` | ALT §4.4 **endgame** "friction dispositions", which has no roster group. Closes #1640, #1700, #1706 and #1712: #1700 and #1712 are fixed, #1640 and #1706 are refused as inherent.<br>**Policy files changed:** `tests/closure.py` classifies `handoff/` as INERT; `.claude/rules/gate-scoping.md` (and its `.mdc`); `tools/audit/briefs/fixer.md` step 2; `docs/decisions/0013`; the plan.<br>Also adds the harness `tools/audit/handoff/r9-frictions/handoff_inert_harness.py` and `docs/delivery/1768.md`. 8 files. |
| [#1770](https://github.com/tvofi/heatpump_optimizer/pull/1770) | `acf5264d` | Record batch: adds delivery rows 1763 and 1764; updates rows 1751, 1765, 1766 and 1768; adds a round-8 citation note in `docs/audit-2026-09.md`. |
| [#1769](https://github.com/tvofi/heatpump_optimizer/pull/1769) | `b2fadf6e` | ALT endgame "register PR", tranche 1. 841 files, +114 010. The round-9 evidence tree (707 files under `tools/audit/round9/`, byte-identical to 79aa98ec), the round-8 harness salvage (131 `.py` under `tools/audit/round8/evidence/`, INERT) and `tools/audit/handoff/v6612-root-cause.md`. Merged over the non-required CodeQL context. |
| [#1772](https://github.com/tvofi/heatpump_optimizer/pull/1772) | `7952d8f9` | Record: delivery rows for #1769 and #1770. |
| [#1771](https://github.com/tvofi/heatpump_optimizer/pull/1771) | `4d33b25c` | Register tranche 2. 16 files, +7 214:<br>• seat tooling `tools/audit/seat/` (merge_pr.sh, remerge_main.sh, handoff_push.sh, ci-watch.sh, codeql-triage-poll.sh)<br>• the roster generator `tools/audit/round9/fixplan/` (gen.py, data.py, build.sh, FIX-PLAN-head.md, standing.md)<br>• the pre-studies `tools/audit/round9/prestudy/` (ALT-ENDGAME-PLAN.md, **ALT-ROSTER.json = rev 2**, DRAFT-ENDGAME-PLAN.md, integration- and surfaces-prestudy.md)<br>• `docs/delivery/1771.md`, which still says "open". |

## Groups on the live roster that are not in ALT rev 2

**None.** Main has no live roster file. The live roster on `handoff/audit-r9-fixplan` @c5af8f3a has exactly rev 2's 66 ids in the same order, and every field except `resume` and four briefs is equal. The briefs that changed:
- **F6.3** gains a NOTE: F6.4 carries tvofi's double-"now" label fix, so its overlap grid must not prescribe the old layout.
- **F6.4** gains a CARRY for tvofi's UI fix: `plan.now_temp` becomes "{temp} °C" in en and sv, and the axis keeps "now".
- **F11.4** now cites `field_coverage.mjs` at 844d14b7 on `handoff/r9-rca-i3`, not yet on main.
- **F11.5** gains a CARRY from F7.4: undeclared entity grouping is a proposed declaration change, not a split.

## Next to dispatch

- **Ready right now: none.** No not-started group has all its `after` edges merged; every one waits on F1.6 at least transitively.
- **Gate: merge #1767 (F1.6).** It needs a round-2 re-review verdict at `929e5aa0`, the in-progress `mutation` check to go green, and most likely a main-merge to `4d33b25c`. A main-only move carries the verdict under the precedent.
- **Ready the moment F1.6 merges:** **R9-F2.4** (Fixes #1664; P4 refusal carry; fixture mover), **R9-F9.3** (Fixes #1647) and **R9-EG-B10** (Fixes #1754 and #1755). None has an owner gate. This matches #201's newest comment and ALT W2.
- **After F2.4:** R9-F1.7 (also needs F1.6) and R9-EG-B8. **After F1.7:** R9-F1.8 and R9-F10.1b.
- **Stamp:** v6.7.11 is owed. Per #201 it follows #1767's merge, and it would be ALT's stamp point (b) plus the EG-B9 sev:high release.

## Out-of-scope observation (not investigated)

GitHub has 70 open issues. Besides the round-9 class and EG issues and #201, there are 30 issues from #1167 to #1204, labelled `[D0-01]` … `[D13-04]` and last updated 2026-09-19. Neither `docs/plan-2026-09-open-issues.md` nor `docs/HANDOVER.md` on main references them, and #201's body "Measured" block still says "Open issues: #201 only". Whether they are dispositioned elsewhere is not determined.

## Re-base to `f88e6af8` (added 2026-09-29, after this table was measured)

**R9-F1.6 merged** as #1767 at `f88e6af8b609c674ae7fa87838b9f13cf50aaecb` (2026-09-29T22:46Z), from round-2 head `929e5aa0` plus main.
- **Counts:** 34 groups merged, 0 in review, 31 not started, and EG-B0 `rca-done`.
- **What #1767 touched:** six production files and `tests/structure_budgets.json`.
- **Effect on the pre-study:** the architecture-score vector, the red-team counters and every per-file figure the rev-3 briefs cite are identical at `f88e6af8` and `4d33b25c`. #1767's ΔS is 0 (NULL).
- **Next to dispatch:** F2.4, F9.3 and EG-B10. Stamp v6.7.11 is owed.
