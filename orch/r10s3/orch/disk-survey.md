# Disk survey (read-only), 2026-10-18 ~19:10 CEST

Nothing was deleted, moved, killed or modified. / is 228 GiB with 3.3 GiB free. Liveness: an lsof snapshot (12680 lines) plus a python mtime walk with a 2 h cutoff (the shell's find is bfs and rejects '-2 hours', so the first pass was redone). PR state: `gh pr list --state all` by branch and head oid, then `gh api commits/<sha>/pulls` for the NOPR ones. A closed PR plus HEAD being an ancestor of origin/main counts as merged.

## Totals per class
| class | size | note |
|---|---|---|
| dead-worktree | 1.66 GB (14 trees) | all four tests pass (clean, HEAD in origin/main, PR closed, quiet over 2 h, no lsof) |
| temp-dead | about 5.0 GB (4.4 GB /private/tmp + 0.6 GB /var/folders T) | no process, no write in 2 h; contains registered worktrees, see section 2 |
| regenerable-cache | about 4.8 GB listed | owner tool per row |
| unknown | about 3.7 GB plain seat trees, plus 11 GB Claude VM, 13 GB iCloud, 2.3 GB game, 3.3 GB pr/ worktrees | owner decision, mostly LIVE-adjacent |
| LIVE | pr/ worktrees (3.3 GB), every seat worktree failing a test, /private/tmp/claude-501, hpo-gate.lock, cc-socks | do not touch |
| swap | 2.0 GB, /private/var/vm/sleepimage only | report only |

Home is 58 GB: Library 32 GB (Claude app 13 GB, iCloud Drive 13 GB, Caches 1 GB), hpo-seats 9.9 GB, .local 6.4 GB, heatpump_optimizer 2.8 GB, .claude 1.8 GB (projects 1.5 GB, report only), .cache 1.2 GB, .npm 1.0 GB, .cc-switch 0.9 GB.

## 1. dead-worktree (removal candidates)
| path | size | mtime | HEAD | PR | evidence |
|---|---|---|---|---|---|
| /Users/timmalmstrom/heatpump_optimizer/.claude/worktrees/audit-round-10-fixing-de8016 | 121 MB | 10-17 19:39 | 91c30656 | #2349:closed | status clean; HEAD ancestor of origin/main; no write in 2 h; lsof none |
| /Users/timmalmstrom/hpo-seats/r10s3/O12/wt2 | 121 MB | 10-18 16:03 | 9f3ae9fe | #2400:closed | status clean; HEAD ancestor of origin/main; no write in 2 h; lsof none |
| /Users/timmalmstrom/hpo-seats/r10s3/O17/wt-r10-codeql-lang-skip | 121 MB | 10-18 16:08 | 5359dd13 | #2405:closed | status clean; HEAD ancestor of origin/main; no write in 2 h; lsof none |
| /Users/timmalmstrom/hpo-seats/r10s3/deeplink-census/wt | 121 MB | 10-18 06:42 | 92e0513b | #2345:closed | status clean; HEAD ancestor of origin/main; no write in 2 h; lsof none |
| /Users/timmalmstrom/hpo-seats/r10s3/leaf-imports/wt | 121 MB | 10-18 05:26 | 75e2a037 | #2371:closed | status clean; HEAD ancestor of origin/main; no write in 2 h; lsof none |
| /Users/timmalmstrom/hpo-seats/r10s3/n-log-flood/wt | 121 MB | 10-18 09:49 | aef46436 | #2351:closed | status clean; HEAD ancestor of origin/main; no write in 2 h; lsof none |
| /Users/timmalmstrom/hpo-seats/r10s3/rca-inert-predict/wt | 121 MB | 10-18 07:49 | 1e44fb2d | #2376:closed | status clean; HEAD ancestor of origin/main; no write in 2 h; lsof none |
| /Users/timmalmstrom/hpo-seats/r10s3/ref-privacy/wt | 121 MB | 10-18 06:19 | e73c683a | #2366:closed | status clean; HEAD ancestor of origin/main; no write in 2 h; lsof none |
| /Users/timmalmstrom/hpo-seats/r10s3/roster-unwire/rwt | 120 MB | 10-18 14:16 | 07ba56db | #2384:closed | status clean; HEAD ancestor of origin/main; no write in 2 h; lsof none |
| /Users/timmalmstrom/hpo-seats/r10s3/roster-unwire/wt | 121 MB | 10-18 14:29 | 7f096fa7 | #2403:closed | status clean; HEAD ancestor of origin/main; no write in 2 h; lsof none |
| /Users/timmalmstrom/hpo-seats/r10s3/store/wt | 121 MB | 10-18 09:21 | ee964f0d | #2375:closed | status clean; HEAD ancestor of origin/main; no write in 2 h; lsof none |
| /Users/timmalmstrom/hpo-seats/r10s3/tools-o1/wt | 121 MB | 10-18 10:33 | 502943a6 | #2386:closed | status clean; HEAD ancestor of origin/main; no write in 2 h; lsof none |
| /private/tmp/r10-n-log-flood/wt-r3 | 121 MB | 10-17 20:27 | 7ef03783 | #2351:closed | status clean; HEAD ancestor of origin/main; no write in 2 h; lsof none |
| /private/tmp/r2345-r6/wt | 120 MB | 10-17 19:44 | 2393446e | #2345:closed | status clean; HEAD ancestor of origin/main; no write in 2 h; lsof none |

Subtotal 1697 MB. Caveat: `--head <branch>` found no PR for most seat branches, so the PR number came from the commit-to-PR lookup; the ancestor-of-main test is what proves the merge. audit-round-10-fixing-de8016 is a Claude session worktree outside the named areas; confirm no session owns it.

Exact removal commands (NOT run):
```
git -C /Users/timmalmstrom/heatpump_optimizer worktree remove /Users/timmalmstrom/heatpump_optimizer/.claude/worktrees/audit-round-10-fixing-de8016
git -C /Users/timmalmstrom/heatpump_optimizer worktree remove /Users/timmalmstrom/hpo-seats/r10s3/O12/wt2
git -C /Users/timmalmstrom/heatpump_optimizer worktree remove /Users/timmalmstrom/hpo-seats/r10s3/O17/wt-r10-codeql-lang-skip
git -C /Users/timmalmstrom/heatpump_optimizer worktree remove /Users/timmalmstrom/hpo-seats/r10s3/deeplink-census/wt
git -C /Users/timmalmstrom/heatpump_optimizer worktree remove /Users/timmalmstrom/hpo-seats/r10s3/leaf-imports/wt
git -C /Users/timmalmstrom/heatpump_optimizer worktree remove /Users/timmalmstrom/hpo-seats/r10s3/n-log-flood/wt
git -C /Users/timmalmstrom/heatpump_optimizer worktree remove /Users/timmalmstrom/hpo-seats/r10s3/rca-inert-predict/wt
git -C /Users/timmalmstrom/heatpump_optimizer worktree remove /Users/timmalmstrom/hpo-seats/r10s3/ref-privacy/wt
git -C /Users/timmalmstrom/heatpump_optimizer worktree remove /Users/timmalmstrom/hpo-seats/r10s3/roster-unwire/rwt
git -C /Users/timmalmstrom/heatpump_optimizer worktree remove /Users/timmalmstrom/hpo-seats/r10s3/roster-unwire/wt
git -C /Users/timmalmstrom/heatpump_optimizer worktree remove /Users/timmalmstrom/hpo-seats/r10s3/store/wt
git -C /Users/timmalmstrom/heatpump_optimizer worktree remove /Users/timmalmstrom/hpo-seats/r10s3/tools-o1/wt
git -C /Users/timmalmstrom/heatpump_optimizer worktree remove /private/tmp/r10-n-log-flood/wt-r3
git -C /Users/timmalmstrom/heatpump_optimizer worktree remove /private/tmp/r2345-r6/wt
```

### Worktrees failing a test (LIVE, not candidates)
- .local/state/hpo/pr (79 entries): every worktree has an OPEN PR (#2368 #2373 #2379 #2390 #2391 #2393 #2394 #2396 #2399 #2401 #2404 #2406 #2408 #2411 #2415 #2416) or no PR found; many written within 2 h. upd-fix-r10-pump-model-d2 is DIRTY(28) with an unmerged conflict (UU coordinator.py); upd-fix-r10-ci-autofix-inert-route HEAD is UNPUSHED; r10-readme-minimal-setup/wt is DIRTY(85).
- hpo-seats/r10s3: cloud-shape/wt HEAD UNPUSHED; fix-2368, fix-2391/wt, fix-sweep/wt, O11/wt, O17/wt-r10-roster-fastpath, O6b/wt, sav-baseline/wt, tick-watch, tick-wt, review-2396/wt2 written within 2 h; review-2400/wt, review-2411/base, sav-baseline/base+proto, ratio-anchor/base+wt, plan-artifact/wt, orch-wt DIRTY; archscore-p4/wt+wt5, ci-concurrency, sensor-payload/wt, vent-detector/wt, O17/wt-r10-roster-carry-policy have OPEN PRs; pump-model/wt-d2, rca-harness-friction/wt, roster-after/wt, i5-docs/wt have no PR found (PR test unproven).
- Never listed: ~/hpo-orch, ~/heatpump_optimizer, hpo-seats/r10s3/orch-wt.

## 2. temp-dead: /private/tmp
Total 4.7 GB. Excluded as LIVE: claude-501 (388 MB, 114 lsof hits, this session), hpo-gate.lock (written 19:07), cc-socks (written 18:44). Basis for dead: lsof none and mtime walk quiet over 2 h, not age. Caution: 16 registered worktrees live inside these dirs and 11 of them are DIRTY (one modified file each, e.g. tools/audit/seat/r10_deeplink_mutants.py, .github/workflows/tests.yml), with no merged PR proven. Remove those through `git worktree remove` (needs --force when dirty) only after the owning seat confirms. Plain extracted trees with no .git can be deleted outright.
| path | size | mtime | class | evidence |
|---|---|---|---|---|
| /private/tmp/havenv2 | 807 MB | 10-17 17:49 | temp-dead | lsof none; no write in 2 h |
| /private/tmp/r10-n-log-flood | 607 MB | 10-18 13:17 | temp-dead | lsof none; no write in 2 h |
| /private/tmp/rev-2345-r7 | 495 MB | 10-18 10:37 | temp-dead | lsof none; no write in 2 h |
| /private/tmp/r2345-r6 | 482 MB | 10-17 19:38 | temp-dead | lsof none; no write in 2 h |
| /private/tmp/r10-deeplink-census | 243 MB | 10-18 07:23 | temp-dead | lsof none; no write in 2 h |
| /private/tmp/mermaid-check | 167 MB | 10-17 16:06 | temp-dead | lsof none; no write in 2 h |
| /private/tmp/rca-coverage-base-reuse | 127 MB | 10-17 11:08 | temp-dead | lsof none; no write in 2 h |
| /private/tmp/r10-pump-model | 126 MB | 10-18 07:23 | temp-dead | lsof none; no write in 2 h |
| /private/tmp/r10-train-hold | 124 MB | 10-17 21:32 | temp-dead | lsof none; no write in 2 h |
| /private/tmp/r10-dev-onboard | 121 MB | 10-17 16:40 | temp-dead | lsof none; no write in 2 h |
| /private/tmp/r10-arch-doc | 120 MB | 10-17 16:43 | temp-dead | lsof none; no write in 2 h |
| /private/tmp/rev-2340 | 120 MB | 10-17 15:31 | temp-dead | lsof none; no write in 2 h |
| /private/tmp/r10-nlf-base2 | 120 MB | 10-17 16:59 | temp-dead | lsof none; no write in 2 h |
| /private/tmp/r10-nlf-base | 120 MB | 10-17 16:16 | temp-dead | lsof none; no write in 2 h |
| /private/tmp/r2345-fixer | 120 MB | 10-17 11:10 | temp-dead | lsof none; no write in 2 h |
| /private/tmp/r10sb-mb | 120 MB | 10-17 11:06 | temp-dead | lsof none; no write in 2 h |
| /private/tmp/r10sb-base | 120 MB | 10-17 10:58 | temp-dead | lsof none; no write in 2 h |
| /private/tmp/r10sb-b37 | 119 MB | 10-17 10:59 | temp-dead | lsof none; no write in 2 h |
| /private/tmp/havenv | 21 MB | 10-17 17:48 | temp-dead | lsof none; no write in 2 h |
| /private/tmp/base-2351 | 21 MB | 10-17 19:08 | temp-dead | lsof none; no write in 2 h |
| /private/tmp small remainder (about 35 entries plus loose logs and bodies) | about 0.1 GB | various | temp-dead | each under 20 MB |

## 3. /private/var/folders/47/470ps6zs6vs07m86bz9sczs00000gn (2.8 GB: T 2.6 GB, C 129 MB, 0 14 MB)
| path | size | mtime | class | evidence |
|---|---|---|---|---|
| T/mutation-table-fhj8uk1y (w0-w3, registered worktrees, DIRTY(1) each) | 480 MB | 10-17 00:27 | temp-dead | quiet, lsof none; same worktree caution |
| T/mutation-table-mbnz4lvi (w1, DIRTY(1)) | 120 MB | 10-17 16:16 | temp-dead | same |
| T/prepr-st.J1ZTa4IZ | 109 MB | 10-17 16:46 | temp-dead | prepr scratch; quiet, lsof none |
| T/pip-unpack-* (225 dirs) | 300 MB | 10-17 to 10-18 | temp-dead | pip build temp; quiet |
| T other (TelephonyUtilities 26 MB, remainder) and C, 0 | about 1.7 GB | | unknown | OS-owned per-user temp; cleared at reboot |

## 4. regenerable-cache
| path | size | mtime | owner tool | evidence |
|---|---|---|---|---|
| ~/.npm/_npx | 716 MB | 10-17 23:36 | npm/npx | exec cache, refetched on use |
| ~/.cache/uv | 563 MB | 10-17 23:36 | uv | wheel cache; `uv cache clean` |
| ~/.cache/puppeteer (chrome 362 MB, headless-shell 201 MB) | 563 MB | 10-17 23:36 | puppeteer | browser download cache. Not ~/.cache/pw-browsers (pinned, untouched) |
| ~/Library/Application Support/Claude/Cache/Cache_Data | 614 MB | 09-10 19:48 | Claude desktop | Chromium HTTP cache |
| ~/Library/Caches/ms-playwright (chromium-1148 279 MB, headless_shell 168 MB) | 449 MB | 10-10 09:52 | Playwright | memory: byte-duplicate of the pinned ~/.cache/pw-browsers 1148; confirm PLAYWRIGHT_BROWSERS_PATH first |
| ~/.claude-server-commander/puppeteer-cache | 362 MB | 10-14 17:55 | desktop-commander | browser cache, refetched |
| ~/Library/Caches/pip | 348 MB | 10-17 17:48 | pip | `pip cache purge` |
| ~/.npm/_cacache | 285 MB | 10-16 22:28 | npm | `npm cache clean --force` |
| ~/Library/Caches/Homebrew | 37 MB | 10-08 23:41 | brew | `brew cleanup` |
| ~/.cache/gh, ~/.cache/heatpump_optimizer | 74 MB |  | gh / repo tooling | small |

Absent: ~/.colima, Docker Desktop container dir, Xcode DerivedData, CoreSimulator (Library/Developer is 116 KB). ~/.docker 20 KB. Library/Logs 36 MB and /Library/Logs 32 MB are small.

## 5. unknown (owner decision)
| path | size | mtime | evidence |
|---|---|---|---|
| ~/Library/Application Support/Claude/vm_bundles/claudevm.bundle | 11 GB | 10-17 21:40 | Claude desktop VM image (rootfs); app-managed, probably recreated by the app, unverified. Largest single item |
| ~/Library/Mobile Documents/com~apple~CloudDocs (Jessica 12 GB, Downloads 880 MB) | 13 GB |  | iCloud user files; free by Finder 'Remove Download', never delete here |
| ~/Library/Application Support/unity.FunPlus.Misty Continent | 2.3 GB |  | game data; user decision |
| ~/hpo-seats/r10s3/pump-model (22 plain exp-* trees about 122 MB each; wt-d2 is a worktree) | 2.8 GB | 10-18 16:53 | no .git so worktree rules do not apply; seat PR #2368 is OPEN, ask the seat; exp-* quiet over 2 h |
| ~/hpo-seats/r10s3/sensor-payload-r2 (standalone clone, .git 1.8 GB) | 1.9 GB | 10-18 17:05 | clone on fix/r10-sensor-payload, PR #2379 OPEN; LIVE |
| ~/hpo-seats/r10s3/vent-detector (mut 607 MB, m6 364 MB, 4 plain trees) | 1.5 GB | 10-18 15:03 | PR #2391 OPEN; experiment outputs; ask seat |
| ~/hpo-seats/r10s3/fix-2368-x (main, head, m0, m1) | 500 MB | 10-18 18:43 | LIVE: written 17:42, open lsof handle (bash pid 85304) |
| ~/.local/state/hpo/venv-ha | 827 MB |  | HA test venv for seats; LIVE infra |
| ~/.local/lib/python3.9/site-packages | 824 MB | 08-17 19:03 | old user-site installs; owner unverified |
| ~/.local/share/uv/python | 406 MB | 10-18 17:23 | uv interpreters seat venvs rely on; LIVE |
| ~/.local/share/claude/versions | 719 MB |  | Claude Code binaries; older versions may be prunable, unverified |
| ~/.cc-switch/backups (9 db backups, about 88 MB each) | 732 MB | 10-18 12:10 | tool backups, oldest 10-06; user call |
| ~/.local/state/hpo/r3-before | 120 MB | 10-16 22:46 | registered DETACHED worktree, DIRTY (3 untracked files), no PR; not proven dead |
| ~/.claude/projects | 1.5 GB |  | report only |
| ~/Library/Application Support/{com.apple.wallpaper 458 MB, Bearly 297 MB, GitKrakenCLI 223 MB, Caches 153 MB, Arc 114 MB, Claude-3p 486 MB} | 1.7 GB |  | app data; unknown |

## 6. Swap (report only)
/private/var/vm holds only sleepimage, 2.0 GB (root-owned, 10-16 21:45). No swapfile was present at survey time. Both are OS-managed: swapfiles appear under memory pressure and are removed when it eases, and sleepimage is rewritten at hibernation. Load was high today, so swapfiles may reappear and take 1-4 GB more. Not deletable by us.

## Quick-win order (all need a go-ahead)
1. The 14 dead worktrees: 1.66 GB, no risk under the rules.
2. Regenerable caches: npx 716 MB, uv 563 MB, puppeteer 563+362 MB, pip 348 MB, npm 285 MB, about 2.8 GB.
3. /private/tmp and /var/folders temp, about 2-3 GB after owners confirm the dirty registered worktrees.
4. If still short: Claude VM bundle 11 GB or iCloud evict.
