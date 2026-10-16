Fix review: merge 9b35a00a9b25be2d49e2e061c001ef7a3a575131

bus-nonce: 6cfadb7466654e7feba410391832965e

Round 3. Reviewed #2316 at head 9b35a00a9b25be2d49e2e061c001ef7a3a575131, in a fresh detached worktree at that SHA.
- The head is the update_pr of 2a2dda051 (round 3, one commit on 98ca694d1), then f72c046ad, then the merge of origin/main.
- The preamble diff of `dev/governance/roles/` is empty.
- Round 3's own diff touches only `ref_privacy.py` and `push.sh`.
- Evidence is in `evidence/`, scrubbed; every planted identity is synthetic.

## Round 2's two blocks: both closed

1. **release.yml is registered.**
   - The site rule now matches `gh release create`, and `gh api .../releases` with a field or a write method.
   - `.github/workflows/release.yml` is registered `shape-checked`. I verified the reason at line 98: `[[ "$TAG" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]` refuses anything else before the tag is made.
   - A release read is not a site; there is a null plant for it.
   - `--check` reads 17 files, 9 guarded, 0 refused.
   - The Contents API is now listed under "WHAT IT DOES NOT CATCH".
   - Mutants N11 (the `gh release create` arm dropped), N12 (the releases-API arm dropped) and N14 (the grep prefilter loses release) are each killed.
2. **M16 is killed.**
   - `push_branch` now runs for real in push.sh's self-test, in a throwaway repository: a leaking commit message exits 5 with nothing pushed, and the clean re-commit pushes.
   - With `--commits HEAD` removed, push.sh's self-test reads `78 passed, 3 failed` (`M16-alone.txt`; the baseline is 81 passed, 0 failed).
   - M11 (the guard deleted) and N13 (the guard bypassed with `true ||`) are killed by the same arm.

N6 is pinned too: the self-test asserts that `of_host()` reads a hostname.

## Mutants: 44 in all, 43 killed

I re-ran my own driver at this head (`scripts/mutate_driver.py`, `mutants.txt`): round 1's 30 (M11 and M16 restated on the moved lines), round 2's N1 to N10, and N11 to N14 new. Every baseline check is green (`baseline-checks.txt`):
- ref_privacy: self-test 47, 0 failed; `--check` 17 files, 9 guarded, 0 refused;
- state_docs: all passed;
- roster_edit: 47, 0 failed;
- app_push: 127, 0 failed;
- push.sh: 81, 0 failed;
- bus: 63, 0 failed;
- prune_refs: 24, pass;
- stamp: pass;
- tmp_paths: 50, 0 failed, and `--check` 0 refused.

The one survivor is M13, the orchestrator-scratch guard in `wt_sync.sh`. I accepted it in round 2: its ref and message are constants.

## Re-checked at this head

- **The self-test** reads 47 checks, 0 failed, under each of three shapes: the macOS default, `TMPDIR` under /tmp, and `env -i` with a Linux-shaped HOME and USER.
- **Site-rule attacks** (`attacks-sites-emails.txt`). Every gh shape from round 2's block is now found. What remains unmatched:
  - `"$GIT_CMD" push`, a multi-line `gh api`, and the Contents API: all disclosed in the docstring.
  - `gh api graphql -F query=@file` and `git send-pack`: neither is disclosed, and no tracked file uses either. Recorded, not blocking.
  - DELETE and read calls: not ref writes, correctly unmatched.
- **Encodings** (`encodings.txt`): unchanged from round 2. The `%2F`-escaped own name is refused.
- **main's record** (`fp-main.txt`), over 6280 commits:
  - host-path: 3 (the same 2 true leaks and 1 false positive on `/home/claude`);
  - decoding changes 0 verdicts;
  - 9 commits carry a refused identity, the known `.local` ones;
  - 0 noreply authors are refused.
- **The live remote after the orchestrator's restart of `wt_sync`** (`live-remote.txt`):
  - `git ls-remote origin` returns 2334 refs, 0 refused under the host identity.
  - Every `wip-sync` ref is `ext-<leaf>-<hash>`, because the synced worktrees sit outside the main checkout.
  - I fetched the 43 `wip-sync` tips: the guard refuses none by name, message, or author or committer email.
- **Contract items:**
  - Untouched: VERSION, the manifest, the notes heading and both claim files.
  - `git merge-tree --write-tree origin/main HEAD` exits 0.
  - No failure check-run on 2a2dda051 or f72c046ad.
  - Every check-run at this head concluded with no failure (`check-runs-9b35a00a9.tsv`).
  - Forward-carry: none.
- **Code-owned paths, needing the owner's approving review before merge:** `.github/workflows/governance.yml`, `tests/closure.py`, `tools/release/stamp.py`.

## Recorded, not blocking

- **Undisclosed exotic misses:** `git send-pack` and `gh api graphql -F query=@file` are not matched and not disclosed. The fix is one docstring line, at the next touch.
- **Outside #2310's fields:** file contents (77 refs and 125 files on main) and the 9 historical `.local` identities. These are already noted in round 1.

## RESULT lines

```
RESULT head=9b35a00a9b25be2d49e2e061c001ef7a3a575131 round=3 preamble_roles_diff=empty
RESULT selftest mac=47/0fail tmpdir=/tmp:47/0fail linux-shape:47/0fail
RESULT check 17 files, 9 guarded, 0 refused
RESULT mutants total=44 killed=43 survived=1 (M13 accepted: constant ref and message)
RESULT M16 alone: push.sh self-test 78 passed, 3 failed (baseline 81/0)
RESULT fp main_messages=6280 decoding_changes=0 commits_with_refused_identity=9 noreply_refused=0
RESULT live origin refs=2334 refused=0; wip-sync tips=43 refused(name/message/identity)=0
RESULT version/manifest/notes/claims untouched; merge-tree rc=0
```
