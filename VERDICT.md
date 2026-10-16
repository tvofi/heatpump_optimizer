Fix review: blocked 98ca694d1bb08532e7a440fd2bfb718a7bdcd1d0 harness: class-open .github/workflows/release.yml creates a tag through gh release create, which the site rule cannot see; push.sh's --commits is unpinned

bus-nonce: df4f9d2315aa360580590ac8c50e343c

Round 2. Reviewed #2316 at head 98ca694d1bb08532e7a440fd2bfb718a7bdcd1d0, in a fresh detached worktree at that SHA.
- The head merges handoff 24bae2485 (round-2 commit 101a57725, then the merge of origin/main 7215e39df) and then origin/main ef08fb420.
- The preamble diff of `dev/governance/roles/` is empty.
- I judged the round-2 delta (101a57725) and the main merges' resolution. Three-dot from merge base ef08fb420: the PR's 16 files.

Evidence is in `evidence/`, scrubbed; every planted identity is synthetic. The round-1 driver file is renamed (`scripts/enum_sites.py`), so nothing there shadows the stdlib.

## Round 1's items: closed

1. **`prune_refs.py` is closed.**
   - `plan()` refuses an archive tag that would name the host, without echoing it.
   - It is registered `guarded`.
   - `--check` now sees `gh api` writes to `git/refs` and `git/tags` (`-f`, `-F`, `--input`, `--method=POST`/`-X PATCH`, `createRef`).
   - `--check` reads 16 files, 9 guarded, 0 refused.
   - My mutants N1 (guard neutered) and N2 (guard deleted, import kept) are killed by `prune_refs.py --self-test`. N9 (the grep prefilter loses `git/refs`) is killed by `--check`.
2. **`$GIT`, `${GIT}`, `${GIT:-git}` and `$git` are now sites.** `"$GIT_CMD"` is not, and the docstring discloses that.
3. **URL-decoded text is judged.** `%2FUsers%2F<name>` is now refused (`encodings.txt`). Decoding changes the verdict on 0 of the 6259 messages on origin/main. N3 (decoding dropped) is killed.
4. **The new `host-email` class holds on main's record** (`fp-main.txt`).
   - 9 commits on origin/main carry a refused identity. They are round 1's 9 `.local` commits.
   - 0 noreply authors are refused.
   - Probes (`attacks-sites-emails.txt`): `.local`, `.lan`, `.localdomain`, `.home.arpa`, `localhost`, and the host's own name, short, full and under another suffix, are all refused.
   - IP-literal domains pass. That is minor: git's default identity uses the hostname, not an address.
5. **One grammar for the home directory.** `tmp_paths.py` now uses `ref_privacy`'s `HOME_DIR` and `CLOUD_ROOTS`. Its `MACHINE` pattern is equivalent to the old one. N10 (home-abs taken off the shared grammar) is killed by `tmp_paths.py --self-test` (50 checks).
6. **Round 1's survivors are now killed:**
   - M10 and M14 (the bus.sh guard deleted, or bypassed with `true ||`), by the new `push-verdict` arm.
   - M12 and M15 (the stamp guard), by stamp's own self-test.
   - M29 (the Python-call arm), by its plant.

## Mutants: 40 in all, 37 killed

I re-ran my own driver at this head (`scripts/mutate_driver.py`, `mutants.txt`): the 30 from round 1 (M12 and M17 restated on the moved lines) and 10 new ones (N1 to N10). Every baseline check is green at this head (`baseline-checks.txt`). Three survive:
- **M13: the orchestrator-scratch guard in `wt_sync.sh`. Justification accepted.** Its ref and message are constants plus `date`, so no input reaches the guard to be refused.
- **M16: `push.sh` without `--commits HEAD`. Justification not accepted.** The cited pin is M25, which is `app_push.sh`'s arm. It tests the guard CLI behind app_push, not that push.sh passes `--commits`. And a push.sh push is still a push to this public repository: decision 0011 stops such a PR merging, not the branch being published. The line this PR added is pinned by nothing.
  **Owed:** a push.sh self-test arm that plants a leaking unpushed commit message and expects exit 5 with no push (app_push's stub shape). Alternatively, drop `--commits` from push.sh and state that the retired path judges the branch only.
- **N6: `of_host()` reads no hostname. Recorded, not blocking.** Nothing pins that the host's own name is read. On macOS the `.local` suffix arm covers git's default identity anyway. A self-test check that `Identity.of_host().hosts` is non-empty would pin it.

## Why still blocked: class-open

`.github/workflows/release.yml:144` runs `gh release create "${TAG}" --target "${GITHUB_SHA}"`. On dispatch, that creates the tag ref on origin through the Releases API.
- The site rule matches neither `gh release create` nor `gh api .../releases -f tag_name=` (`attacks-sites-emails.txt`, rows "MISSED").
- The file is in `--check`'s scope (`.github/workflows/`), and it is not in `PUSHERS` or in the body.
- **The in-tree risk is nil.** release.yml refuses any `TAG` outside `^v[0-9]+\.[0-9]+\.[0-9]+$` (line 98) before creating it, so its disposition is a fixed shape.
- **The mechanism is the defect.** The body claims "a new pusher cannot skip the check". A new instrument that names a release tag from a path skips it today. This is the same seam as round 1's `gh api git/refs`, through a second API.

**Owed:** the site rule sees `gh release create` (or `edit --tag`) and `gh api .../releases` with a field. release.yml is then registered with its shape check as the reason. A self-test plant must be found by the rule. The docstring's "WHAT IT DOES NOT CATCH" also gains the Contents API (`PUT .../contents/...`, which writes a commit with a message), unless the rule matches it. No in-tree file uses that API.

## Other checks

- **The self-test** reads 45 checks, 0 failed, under each of three shapes: the macOS default, `TMPDIR` under /tmp, and `env -i` with a Linux-shaped HOME and USER.
- **The pushers' own self-tests at this head:**
  - state_docs: all passed;
  - roster_edit: 47, 0 failed;
  - app_push: 127, 0 failed;
  - push.sh: 77, 0 failed;
  - bus: 63, 0 failed;
  - prune_refs: 24, pass;
  - stamp: pass;
  - tmp_paths: 50, 0 failed.

  `tmp_paths.py --check`: 0 refused.
- **Untouched:** VERSION, the manifest, the notes heading and both claim files. `git merge-tree --write-tree origin/main HEAD` exits 0.
- **Red checks on the round-2 commits:** 101a57725, 24bae2485 and 651ce8c4a have none. Every check-run at this head concluded with no failure (`check-runs-98ca694d1.tsv`).
- **Code-owned paths, for the owner's separate gate:** `.github/workflows/governance.yml`, `tests/closure.py`, `tools/release/stamp.py`.

## RESULT lines

```
RESULT head=98ca694d1bb08532e7a440fd2bfb718a7bdcd1d0 round=2 preamble_roles_diff=empty
RESULT selftest mac=45/0fail tmpdir=/tmp:45/0fail linux-shape:45/0fail
RESULT check 16 files, 9 guarded, 0 refused
RESULT mutants total=40 killed=37 survived=3 (M13 accepted, M16 not accepted, N6 recorded)
RESULT fp main_messages=6259 decoding_changes=0 commits_with_refused_identity=9 noreply_refused=0
RESULT encodings %2F-escaped own name now REFUSED; $GIT/${GIT}/$git now sites; gh api git/refs writes now sites
RESULT class-open .github/workflows/release.yml gh release create (tag writer; shape-checked vN.N.N, undispositioned, rule cannot see it)
RESULT version/manifest/notes/claims untouched; merge-tree rc=0
```
