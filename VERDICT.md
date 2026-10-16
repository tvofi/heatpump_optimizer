Fix review: blocked 9d7beec3bedb9557c19e42096689e1b137838c68 harness: class-open tools/audit/seat/prune_refs.py writes origin refs through gh api git/refs, which --check cannot see

bus-nonce: b3a3d5fea5bdf883235a751610eaa38f

Round 1. Reviewed #2316 (R10-REF-PRIVACY, closes #2310) at head 9d7beec3bedb9557c19e42096689e1b137838c68, in a detached worktree at that SHA. Merge base 25afc1c77. The preamble diff of `dev/governance/roles/` against origin/main is empty. Evidence is in `evidence/`, scrubbed: the host's home path, account name and uid are replaced by placeholders. Every planted identity is synthetic (`exampleuser`, `someone`, uid 4242).

## What holds

- **The defect's own instance is fixed.** `slug()` cannot return a leaking component. `wt_sync.sh` takes its slug from `slug()` and guards both pushes. The old slug, restored as M1, is refused by the guard and red in the self-test.
- **The finder's measurement.** `git ls-remote origin`, judged by `refusal()` under the host identity: 2339 refs (peeled lines dropped), 0 refused. The local `refs/remotes/origin/*` holds 2194 refs, 0 refused (`local-tracking.txt`).
- **The self-test passes in every shape I ran,** 34 checks and 0 failed in each:
  - the macOS default;
  - `TMPDIR` under /tmp;
  - `env -i` with HOME, USER and LOGNAME set Linux-shaped.

  CI's `instrument-self-tests` (job 116747147594, run 38830250935) at this head printed `ref_privacy self-test: 34 checks, 0 failed` and `--check ... 15 file(s) with a push site, 8 guarded, 0 refused`.
- **The CI-red cause reproduces.** At 29091251a, `TMPDIR=/tmp` gives `33 checks, 1 failed` on the wt_sync arm, and the macOS default gives 33 checks, 0 failed (`cired-repro-29091251a.txt`). The body's `## Red checks` answers it. The other red at 1e522a71b, `pr-contract`, is the body check. The remaining non-green runs at 1e522a71b and 639797353 were `cancelled`, superseded by later pushes.
- **False positives on main.** `leaks()` over all 6134 commit messages on origin/main (`fp-main.txt`):
  - Under the host identity: 3 host-path, 2 home-directory, 2 account-name. Two of those messages are real historical leaks of the home path, so they are true positives.
  - Identity-free: 3 host-path. One is a false positive, a message naming the `/home/claude` temp root. That is 1 in 6134.

  The host-path class is not too broad on this record.
- **Mutation proof.** All 12 of the body's mutants are killed, as the body states. M10 to M12 are killed by `--check` only. I added 18 mutants: 14 killed and 4 survived (`mutants.txt`):
  - M13: `wt_sync.sh`'s orchestrator-scratch guard deleted. Its ref and message are constants, so the risk is low.
  - M14: `bus.sh`'s guard bypassed with `true ||`. The body discloses this.
  - M16: `push.sh`'s `--commits HEAD` dropped. No arm drives push.sh's commit half.
  - M29: the site rule's Python-call arm dropped. The `git ... push` arm already covers every in-tree hit, so this arm is dead code.

  M15 (the stamp guard neutered with `if False`) is killed only by my out-of-tree probe, `stamp.py --title '/Users/exampleuser/y' --dry-run`. No in-tree check kills it.
- **Declined `tmp_paths.py` rule (item 4): agreed on its argument.** The leak was a value computed on one line and pushed from another. A spelling rule could only pin the expression `${w#$HOME/}`. The push-time guard covers every input.
- **Other contract items:**
  - VERSION, the manifest, the notes heading and both claim files are untouched.
  - `git merge-tree --write-tree origin/main HEAD` exits 0.
  - The `tests/closures.json` entry is earned: entities.py loads `state_docs.py`, which now imports `ref_privacy.py`.
  - Forward-carry: none is claimed, and none is owed by the items below.
  - Code-owned paths in the diff: `.github/workflows/governance.yml`, `tests/closure.py`, `tools/release/stamp.py`. They need the owner's review separately.

## Why blocked

The body's lead claim is "a new pusher cannot skip the check". `--check` is the body's class rule. My enumeration of the same class (`enum-raw.txt`, `site-rule-attacks.txt`) finds an in-tree ref writer the rule cannot see:

1. **class-open: `tools/audit/seat/prune_refs.py`.**
   - **What it does:** it creates refs on origin with `gh api repos/{repo}/git/refs -f ref=refs/tags/archive/<branch name>`. That composes a published ref name from a value it does not fix itself, which is the body's own criterion for the guard.
   - **Why it is in this class:** it archives the `wip-sync` family. Origin holds 506 `archive/*` tags, 1 of them `archive/wip-sync*`. Had it run over the 70 leaking refs before the cleanup, it would have republished them as permanent tags.
   - **Why the registry misses it:** `_SITE` matches no `gh api ... git/refs` write. The file is neither guarded, nor in `PUSHERS`, nor dispositioned in the body.
   - **Owed:** the site rule learns `gh api` ref writes (POST, or PATCH to `git/refs`). prune_refs.py is then registered, `republishes` at minimum, or guarded. A planted `gh api` ref write in the self-test must be found by the rule.
2. **The same rule misses `git` spelled through a variable.** `_SITE`'s `\bgit\b` is case-sensitive, so `"$GIT" push ...` and `$GIT push ...` are not sites (`site-rule-attacks.txt`). The brief named this shape, and the docstring's "another wrapper name" does not clearly cover it. No in-tree instance exists today. **Owed:** match the variable form, or narrow the body's claim to what the rule checks.
3. **A URL-escaped path carrying the host's own account name passes the guard.** For example, `see %2FUsers%2Fexampleuser%2Fproj` under the identity `exampleuser` passes (`encodings.txt`). The escape's trailing `F` is alphanumeric, so the account-name word boundary fails, and the home directory never appears verbatim. **Owed:** judge `urllib.parse.unquote(text)` as well as the raw text, with a self-test arm.

What the guard does refuse among the encodings tried:
- `Users-x` and lowercase `users-<own name>` in a slug;
- the mixed-case own name, and `<name>_wt`;
- `claude-<uid>`, and `tmp-claude-<any uid>`;
- `~name`, `name@host`, `file:///Users/...` and `/private/var/folders`.

What still passes, and what I judge acceptable:
- **Another host's name in lowercase or upper-case path shapes** (`users-someone`, `/USERS/someone`, `/HOME/someone`) and a JSON-escaped `\/Users\/someone`. Under the host's own identity, the account-name class catches each of these.
- **A bare `claude-<other uid>` with no tmp prefix.** The defect's shape always carried the tmp prefix.

## Observations, not part of the block

These are for the orchestrator to route under `finding-propagation.md`. None of them is filed.

- **Author and committer fields are not judged.** The guard reads ref names and messages only. On origin/main, 9 commits carry `<x>@<hostname>.local` author and committer emails. 2 of them are from 2026-10-11 (476dac6e0, e3511b221) and name the machine's hostname (`authors.txt`). This is outside #2310's stated fields.
- **File content is not judged, and the docstring says so.** All 77 `wip-sync` refs carry the home path in their tree content, and so does origin/main itself, in 125 files. This is consistent with the cancelled history scrub. I am recording the figure only.
- **Two grammars for one concept.** `ref_privacy.py`'s `_HOST_PATH` and `tmp_paths.py`'s home-abs class both define what a host path is, with different public-account lists.
- **The body's `## Head` paragraph reads backwards.** It says 639797353 "merges the authored code head 9d7beec3b". In fact 9d7beec3b is the head: it merges origin/main into 6f1a0f0e9, whose parent is 639797353. The SHA the body names is correct.

## RESULT lines

```
RESULT head=9d7beec3bedb9557c19e42096689e1b137838c68 preamble_roles_diff=empty
RESULT selftest mac=34/0fail tmpdir=/tmp:34/0fail linux-shape:34/0fail ci_job=116747147594:34/0fail
RESULT check 15 files, 8 guarded, 0 refused (local and CI)
RESULT ls-remote origin refs=2339 refused_host_identity=0
RESULT fp main_messages=6134 identity_free_host_path=3 (2 true leaks, 1 false positive on /home/claude)
RESULT mutants body=12/12 killed; reviewer=18, killed=14, survived=4 (M13 M14 M16 M29); M15 killed only by an out-of-tree probe
RESULT cired_repro 29091251a TMPDIR=/tmp 33/1fail, macOS default 33/0fail
RESULT class-open prune_refs.py (gh api git/refs); site-rule miss "$GIT" push; guard miss %2F-escaped own account name
RESULT ci all check-runs at the head concluded: 0 failure; closures, fast (3.14), coverage, mutation, Analyze (python) success (evidence/check-runs-9d7beec3b.tsv)
RESULT version/manifest/notes/claims untouched; merge-tree rc=0
```
