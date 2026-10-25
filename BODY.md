r10-fly-depgraph-stale (owner question 2026-10-21; `.github/` changes under mandate 6319294694). The open Dependabot alerts on the pip locks under `tests/` (the owner's count, quoted in the brief; this seat's token cannot list them) are held open by a stale dependency graph, not by the tree.

**Cause, from evidence.** The graph for `tests/requirements-*.txt` is not parsed from the files: it is the snapshot the dynamic `Dependency Graph` workflow (id 346019373, a Dependabot graph job, `job.correlator` `dependabot-pip-tests`) submits through the Dependency Submission API; its run log for 2622b31c prints the payload, one manifest per lock with each blob oid. That job ran for every manifest-touching first-parent merge to main from 7af2a261 (2026-09-24) through 2622b31c (2026-10-03), and for neither of the two after it, d4f937d6 (#2487, 2026-10-20) and e7c66485 (#2544, 2026-10-21). The three suspects the brief names are each excluded by the same comparison:
- pusher: the repository activity API records all seven pushes, triggering and silent alike, as `pr_merge` by `tvofi`; neither the `hpo-author` App nor the deploy key pushed any of them;
- the hash-locked `\` continuation format: present since #1548, whose merge 7af2a261 triggered a graph run;
- a settings change: Dependabot's own jobs kept running on this repository through the silent window (the `Dependabot Updates` workflow, 366316603, ran on 2026-10-20T23:09Z and 2026-10-21T01:14Z, from the stale graph), so Dependabot and the graph are enabled.

An unrelated repository reports the same cutoff on the scheduler's own tracker: dependabot/dependabot-core#16044, comment 6317004144 (2026-10-21), "the last 'Graph Update: pip in /backend' job ran on 2026-10-03", later lock pushes to its default branch running none. A maintainer there (2026-09-04) states that what dispatches these jobs is "a service internally within GitHub that monitors for manifest changes". The cause is therefore GitHub's graph-job scheduler, not this tree. One confound remains and is stated, not excluded: `tests/requirements-typing.txt` grew from 247322 to 254610 bytes at d4f937d6; GitHub documents a 10 MB manifest limit and no smaller one, and the size of the cross-repository report's lock is not known here. The fix below does not depend on which holds.

**Fix.** `.github/workflows/dependency-graph.yml` `submit`: every push to main changing a pip lock, `tools/pr/depgraph.py` or the workflow itself, and a dispatch, POSTs a snapshot `depgraph.py snapshot` builds from the locks at the pushed commit, with the manifest names the Dependabot job used. The dependency-submission docs rank a user submission above a Dependabot graph job for the same manifest, so the stale snapshot stops counting whether or not GitHub's scheduler recovers. Alternatives and why each lost: waiting on GitHub (the owner's alerts stay open for an unbounded time; #16044 has no fix date); the "Refresh Dependabot alerts" button (reprocesses manifests, but the Python graph is the submitted snapshot, and it is a manual, once-an-hour UI act no seat can run); a trivial edit to a lock to re-trigger (d4f937d6 and e7c66485 were exactly that and triggered nothing); GitHub's paid automatic dependency submission (not the scheduler at fault's replacement for pip locks that are already fully resolved, and it bills Actions minutes for what a 5-minute parse does).

**One-time re-ingest.** Attempted from this seat with the branch's own snapshot of main's locks (identical to b89fea13's): the cloud proxy refused the POST (`Write access to this GitHub API path is not permitted through this proxy`, HTTP 403), and it was not routed around. The merge of this pull request is itself a push touching the workflow's own path, so its `submit` run is the re-ingest; `gh workflow run dependency-graph.yml --ref main` repeats it.

**Verification owed after the merge** (brief item 3; this seat's token reads no Dependabot alerts: `Resource not accessible by integration`): once the merge's `submit` run is green, `python3 -I tools/pr/depgraph.py check --repo tvofi/heatpump_optimizer` with an alerts-capable `gh` must print `OK` with `alerts: 0 open` on the pip arm; any alert Dependabot leaves open is named `open, fixed in the tree`. No alert is dismissed by hand.

**Guard.** `depgraph.py check` compares one SBOM read (and, from a seat, one open-alerts read) with every pin the tree carries: pypi against the pip locks, npm against every `package-lock.json`, githubactions against every `uses:` under `.github/`. A difference is `STALE`, exit 1; an ecosystem the SBOM reports that the census does not enumerate refuses, exit 2; an open alert the tree pins at or above the first patched version is `STALE`. The workflow's daily `check` job runs the SBOM arm (GITHUB_TOKEN cannot read Dependabot alerts); `--self-test` is wired in governance's `instrument-self-tests`, and `selftest_wiring.py --check` reads it as wired.

## Head

edc3f8bf5038dc1fb56db9ce3ddab0c3c49d53d8, cut from origin/main b89fea13e99f23cc75f01bb1604030cabea4ca66 (origin/main's tip at 2026-10-25T14:07Z).

## Mutation proof

Each mutant applied to `tools/pr/depgraph.py` in a `git archive` copy of the head, then `python3 -I tools/pr/depgraph.py --self-test`; the unmutated copy prints `depgraph self-test: 22 checks, 0 failed`.
- `stale |= bool(missing or extra)` -> `stale |= False` (the SBOM diff predicate): `a stale version is STALE`, `a pin missing from the graph is STALE`, `a graph package the tree dropped is STALE` FAIL, 3 failed.
- `release(v) >= release(patched)` -> `>` (the alert arm's predicate): `alerts: patched == pinned counts as fixed` FAIL, 1 failed.
- the unenumerated-ecosystem `raise` -> `continue`: `an unenumerated ecosystem refuses` FAIL, 1 failed.
- `manifests["/" + rel]` -> `manifests[rel]` (the name the Dependabot job used, which the precedence override depends on): `snapshot: one manifest per lock, named as Dependabot named it` FAIL, and the next check dies on the missing key.

## Null control

The same instrument over the same SBOM read, against the tree at 2622b31c (the commit the stale snapshot was taken at, `depgraph.py` copied into a worktree of it): `pypi: 123 pinned, 123 in the graph, 0 missing, 0 stale`. The pip arm reads the graph as exactly the 2622b31c locks, so the head's `STALE` is the graph's age, not a parsing difference. At the head the npm and githubactions arms read 0 missing, 0 stale against the same SBOM: those graphs are static parses and are current.

## Figures

- Graph-job runs by commit (the cause's table): `gh api 'repos/tvofi/heatpump_optimizer/actions/runs?event=dynamic&per_page=40' --jq '.workflow_runs[] | select(.workflow_id==346019373) | [.created_at,.head_sha[0:8]] | @tsv'` lists 7 runs, the last at 2622b31c 2026-10-03T12:04:07Z; `git log --first-parent --format=%h origin/main -- 'tests/requirements*.txt'` lists the manifest-touching merges, of which the two after 2622b31c (d4f937d6, e7c66485) have no run. Null control: the same `runs?head_sha=` read for 43afd53e returns its `Graph Update: pip in /tests` row, for d4f937d6 none.
- Pusher of each: `gh api 'repos/tvofi/heatpump_optimizer/activity?ref=refs/heads/main&per_page=100'` (paginated by its `after` cursor), the seven `after` SHAs above: `pr_merge` by `tvofi`, each.
- Stale graph at the head: `gh api repos/tvofi/heatpump_optimizer/dependency-graph/sbom > sbom.json && python3 -I tools/pr/depgraph.py check --sbom sbom.json` (SBOM created 2026-10-25T12:55:09Z) prints `pypi: 122 pinned, 123 in the graph, 4 missing, 5 stale`: missing aiohttp@3.14.5, certifi@2026.10.19, pillow@13.0.0, uv@0.13.4; stale aiohttp@3.14.3, certifi@2026.7.22, pillow@12.3.0, uv@0.12.5, yarl@1.24.5; `githubactions: 18 pinned, 18 in the graph, 0 missing, 0 stale`; `npm: 119 pinned, 119 in the graph, 0 missing, 0 stale`; exit 1. The pin count is distinct (name, version) pairs over the five locks, so a package two locks pin once counts once.
- Re-ingest attempt: `python3 -I tools/pr/depgraph.py snapshot --sha b89fea13e99f23cc75f01bb1604030cabea4ca66 --ref refs/heads/main --job-id seat-r10-fly-depgraph-stale-1` then POST to `repos/tvofi/heatpump_optimizer/dependency-graph/snapshots`: HTTP 403 from the proxy.
- Lock size across the cutoff: `git cat-file -s 2622b31c8:tests/requirements-typing.txt` 247322, `git cat-file -s d4f937d6e:tests/requirements-typing.txt` 254610.
- `python3 -I tools/pr/depgraph.py --self-test`: `depgraph self-test: 22 checks, 0 failed`.
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: `0 unwired`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff b89fea13e99f23cc75f01bb1604030cabea4ca66`: `Architecture score: dS +0.0000 NULL`.
- Scope: `python3 tests/closure.py select --diff b89fea13e99f23cc75f01bb1604030cabea4ca66`: `MODE: SCOPED -- 2 script(s) run` (tests/entities.py, tests/harness_headers.py), run with `PYTHONPATH=tests/hastub`, with the `run_always` scripts: env_drift `--claims-only`, `closure.py selftest`, `layout.py` and `harness_headers.py` exit 0; `entities.py` prints `2 of 2440 ENTITY CHECKS FAILED`, both `hb:` (py-spy in this container), the same two it prints at origin/main here, and no `every tracked file is either measured or deliberately classified` failure. `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: no red predicted.

## Architecture score

`dS +0.0000 NULL`: the new code is a tools/ program, which the score does not read.

## Red checks

none. The `UNCLASSIFIED .github/workflows/dependency-graph.yml` red `ci_predict.py` predicted was repaired before the handoff: `tests/entities.py` and `tests/harness_headers.py` read every workflow, so the file joined both closures (`derive_closures.sh --single ... --record-only`, then `closure.py merge --partial --allow-failures`, because entities.py exits 1 here on `hb:positive_control`, which fails identically at origin/main in this container: py-spy names no spin).

## Forward-carry

none

## Friction

- proxy-write: cost: the cloud seat's proxy refuses POST `dependency-graph/snapshots` (HTTP 403) and its token reads no Dependabot alerts (`Resource not accessible by integration`), so the brief's "re-ingest now" and the alert half of its verification cannot run from a cloud fixer seat; the merge's own `submit` run and a seat with an alerts-capable token carry them. Carry: dismissed: the session proxy's write policy, not a repository rule
