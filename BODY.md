_Requested by **tvofi**_

Part of #201. Truths every `docs/delivery/<N>.md` that read **open** at origin/main 492d84011 for a PR that is no longer open on GitHub, per `delivery-status-tracking.md`. Each row now reads `**merged** <8-hex merge commit>, <existing text>`; only `docs/delivery/*.md` changes, one line per file.

Changed (68, all merged, 0 closed-unmerged): #1631 #1632 #1633 #1634 #1635 #1636 #1637 #1638 #1639 #1641 #1642 #1643 #1690 #1691 #1693 #1694 #1696 #1697 #1698 #1699 #1701 #1702 #1703 #1704 #1705 #1707 #1708 #1709 #1711 #1713 #1714 #1715 #1716 #1717 #1718 #1719 #1720 #1721 #1722 #1723 #1731 #1732 #1796 #1797 #1799 #1800 #1801 #1808 #1815 #1817 #1818 #1819 #1820 #1821 #1822 #1823 #1824 #1829 #1830 #1831 #1832 #1833 #1834 #1835 #1836 #1837 #1839 #1840 

## Head

f4405d794e646e1b31db38bc6cf9c571b11b8393

## Mutation proof

n/a: record-only change to `docs/delivery/*.md`; no production or check code changes.

## Null control

n/a: no cost, gain or timing claim. Before the change `git grep -l '\*\*open\*\*' origin/main -- docs/delivery` listed these 68 files; after it lists none.

## Figures

- merged 68, closed-unmerged 0, skipped-open 0, gh failures 0: `git grep -l '\*\*open\*\*' origin/main -- docs/delivery`, then `gh pr view N --json state,mergeCommit` per file.

## Red checks

none

## Forward-carry

none

## Friction

none
