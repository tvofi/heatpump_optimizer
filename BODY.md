R10-CATALOG-PR, PREPARATION ONLY (coordinator ruling): carry 0 attempted on a real Home Assistant instance, carry 1 dry-run at the current base. No code change, no pull request, nothing pushed outside tvofi/heatpump_optimizer, no tag or release. This is a result body: no `handoff/r10-catalog-pr` exists.

## Head

Measured at origin/main 6e100ef6980216a81eaa0438bdc215d62b19271f (= the dispatched base), 2026-11-12T12:02Z. Latest tag v7.1.12 (contains #3014: `git merge-base --is-ancestor cabfaadc3a v7.1.12` rc 0). No v10.0.0 tag exists, so carry 1 ran at the base, not at the v10.0.0 tree.

## Carry 0: result (not discharged; owner step)

A real Home Assistant **2026.11.1** (PyPI, Python 3.14.6, home-assistant-frontend 20261028.5, `default_config:`) was installed and onboarded in the seat container. The Marketplace config entry loaded, and the panel opened at `/marketplace` once its risk dialog was accepted.

Adding this repository as a custom repository failed on the real core's websocket API (`marketplace/repositories/add`, repository `tvofi/heatpump_optimizer`, category `integration`):
- before the dialog was accepted: `warning_not_accepted`;
- after it was accepted: `{"code": "github_not_connected", "message": "Connect a GitHub account to the Marketplace first"}`.

Connecting GitHub is a device flow (`marketplace` config flow, reconfigure step), and only a person signed in to GitHub can complete it. No seat can do that, so the repository page cannot be rendered from a seat until either:
- (a) a GitHub-connected Marketplace adds it as a custom repository (owner), or
- (b) the catalog lists it, after which browsing needs no GitHub connection (config_flow `async_step_system` creates a token-less entry).

What the real instance did establish:
- **Ref rule in the shipped bundle.** `hass_frontend/frontend_latest/42233.4d01354acd3b510d.js` (sha1 400168d1495ba19f685e4fdb8e9a537d921eb768, frontend 20261028.5) resolves relative URLs against `https://raw.githubusercontent.com/<full_name>/<installed_version || available_version || default_branch>/`. A `.md` target resolves against `https://github.com/<full_name>/blob/<same ref>/`. That is the rule the replica transcribed, so an uninstalled page renders at the latest release tag.
- **Replica on the released README.** `dev/audit/harnesses/r10_readme_marketplace_pipeline.mjs --readme <git show v7.1.12:README.md>` exits rc 0: relative_images 7/7, relative_links 28/28, picture_sources 4/4. Null control: absolute_images 5/5 resolve at both ends. Control on the README before #3014 (`cabfaadc3a^1:README.md`): rc 1, relative_images 0/4, relative_links 0/28. This is still the replica, not the shipped sanitizer, which is the reason carry 0 exists.

## Carry 1: dry run (at base, not at v10.0.0)

`python3 tools/audit/check_scopes.py --repo . --ref 6e100ef6980216a81eaa0438bdc215d62b19271f` returned rc 0. Its coverage line: `ok coverage tracked=10204 in_universe=1551 excluded=8653 unclassified=0`. Classified paths: none needed, because unclassified=0 at this base. The real run is owed at the v10.0.0 tree.

Null control: `check_scopes.py --repo . --self-test` returned rc 0 with `SELF-TEST passed (every perturbed scope refused)`. Its coverage arms refused the following perturbations, each naming the path:
- dropping D10's universe, which names `custom_components/heatpump_optimizer/py.typed`;
- stripping the tests/ and blueprints/ globs;
- a dead exclusion;
- an unreasoned exclusion;
- an excluded covered path (`optimizer.py`).

So the checker can go red, and an unclassified path would have printed by name.

## Steps left after the v10.0.0 tag (ordered; each owned as stated)

1. **Verify the release preconditions (any seat).**
   - `gh release view v10.0.0 -R tvofi/heatpump_optimizer --json assets -q '.assets[].name'` must list `heatpump_optimizer.zip`.
   - Run `D=$(mktemp -d); gh release download v10.0.0 -R tvofi/heatpump_optimizer -p heatpump_optimizer.zip -D "$D"; unzip -l "$D/heatpump_optimizer.zip" | tail -1; unzip -l "$D/heatpump_optimizer.zip" | awk '$4=="manifest.json"'`. The total must be under 104857600 bytes, and `manifest.json` must sit at the root.
   - Check that R10-MARKETPLACE and R10-STAMP-ROUND-MAJOR are ancestors: `git merge-base --is-ancestor <their merge SHAs> v10.0.0`.
2. **HACS action and hassfest at the tag (any seat).** `gh run list -R tvofi/heatpump_optimizer --workflow validate.yml --json headSha,conclusion,url` and the same for `hassfest.yml`. Need a `success` whose headSha = `git rev-list -n1 v10.0.0`. If none exists, dispatch one at the tag (both are code-owned workflows; their triggers decide whether `workflow_dispatch` is available) and keep the two run URLs.
3. **Carry 1 for real (fixer seat, at a merge base that is the v10.0.0 tree).**
   - `git fetch --tags origin && python3 tools/audit/check_scopes.py --repo . --ref $(git rev-list -n1 v10.0.0)`, then print the rc and the coverage line.
   - For each `unclassified` path, add it to a dimension universe or to `_coverage_excluded` in `dev/audit/config/scopes.json` with a reason. Rerun until rc 0, and run `--self-test` as the null control.
   - A nonzero rc blocks step 5.
4. **Carry 0 (owner, or tvofi on their own HA 2026.11+).**
   - Settings > Marketplace, accept the dialog, connect GitHub, then add custom repository `tvofi/heatpump_optimizer` (Integration). Open its page, which renders at v10.0.0 per the ref rule above.
   - Capture it with the OS colour scheme set to light, then to dark.
   - Confirm every README figure renders, and that the dark `<source srcset="./…">` resolves to `https://raw.githubusercontent.com/tvofi/heatpump_optimizer/v10.0.0/<path>`. DevTools Elements on the `<source>`, or right-click > open image, shows it.
   - Control: an absolute-URL image renders in both schemes.
   - To reproduce it in a seat instead, follow the recipe below. A seat still needs a GitHub-connected entry (device flow) or the catalog listing.
5. **Catalog PR (owner only, personal `tvofi` account; never an org, never hpo-author).**
   - Fork `hacs/default` and add `"tvofi/heatpump_optimizer"` to the `integration` JSON list in sorted position. `python3 -c 'import json;l=json.load(open("integration"));print(l==sorted(l,key=str.lower))'` checks the order before and after.
   - Open the PR, filling its template with the v10.0.0 release URL and the two run URLs from step 2.
6. **Record (orchestrator/tvofi).**
   - Read the PR back.
   - Comment its URL on #2965 via `gh_comment.py`, and read that back.
   - Record the URL in R10-CATALOG-PR's resume / `dev/programme/delivery/<N>.md`.
   - Never delete or rename the repository while it is listed.

## Recipe: a real HA 2026.11 instance in a seat (scratch, reproducible)

```
uv venv -p 3.14 venv && VIRTUAL_ENV=$PWD/venv uv pip install homeassistant==2026.11.1 aiogithubapi==26.0.0 home-assistant-frontend==20261028.5
# behind the agent proxy: core's aiohttp sessions ignore HTTPS_PROXY, so the launcher defaults trust_env=True
#   (import aiohttp; wrap ClientSession.__init__ with k.setdefault("trust_env", True); then homeassistant.__main__.main())
#   and the proxy CA is appended to the venv's certifi bundle
printf 'default_config:\n' > config/configuration.yaml; python launch.py config   # start by PID, kill by PID
POST /api/onboarding/users -> /auth/token -> POST /api/onboarding/{core_config,analytics,integration}
Playwright: localStorage hassTokens, open /marketplace, tick "I understand the risks and agree", Continue
```

With a minimal config (frontend+config only, no `default_config`), the panel hangs on "Loading…". Use `default_config`.

## Mutation proof

None: no production or tooling line changed.

## Null control

Carry 1: `--self-test` (above). Carry 0 replica: the pre-#3014 README goes red (rc 1) and absolute images resolve at both ends. Carry 0 real instance: the refusal is a result, not a measurement, and owes none.

## Figures

Every figure above is printed beside the command that produced it, measured at 6e100ef69802 on 2026-11-12. `main` did not move during the run.

## Red checks

None turned red: no branch was pushed.

## Forward-carry

- To R10-CATALOG-PR's own post-tag pass (this group): steps 1-6 above.
- Carry 0 now needs a GitHub-connected Marketplace or the catalog listing, so it is an owner step until listing.
- Steps 5-6 are owner and orchestrator acts this group cannot pre-perform.

## Friction

- Core 2026.11.1 requires Python ≥ 3.14.2. The container's 3.13 failed to resolve it, so uv fetched 3.14.6.
- The frugal inline-search guard blocked plain wait loops and was cleared only by delegating.
- `pkill` is refused by a hook, so kill by PID.
- The custom-repository path needs GitHub; the risk dialog alone is not enough.
