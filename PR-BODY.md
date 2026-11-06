R10-HOTFIX-STAMP-BASE (lane C, fix, size S). v7.1.2 was tagged by hand at b8e823699, a tree whose VERSION, manifest version and notes still read 7.1.1. `tools/release/stamp.py` bumped from VERSION alone, so its next patch was v7.1.2 again, which rule 3 refuses as an existing tag. Rules "flush", 4 and 5 (`window_log_args`, `rule4_problem`, `disposition_gate`) also took their window from the newest v* tag, and no stamp made that tag. v7.1.2 is kept. Nothing is deleted or retagged.

What changes:

- `stamp.py`: two pure functions. `bump_base(current, tags)` returns the higher of VERSION and the highest `TAG_RE` tag. `last_stamped_tag(tags, version_at)` returns the newest release tag whose own tree's VERSION equals its name; the VERSION lookup is passed in, so the self-test needs no git. `tag_version` reads `git show <tag>:VERSION` through the module's `sh` seam. `main()` still refuses bad flags before it fetches (decision 0016's pre-fetch refusal is unchanged). After Rule 1's `fetch --tags`, the Rule 3 block computes `base = bump_base(current, tags + remote)` and then `nxt = next_version(base, ...)`. `last_tag = last_stamped_tag(tags, tag_version)` is what feeds flush, rule 4 and rule 5. Rule 3's exists refusal and its above-every-tag refusal stay as the backstop.
- `release.yml`: a new step, `Refuse a tag whose tree does not carry its version`, runs after the on-main check and so before `Create the GitHub release`. It refuses unless VERSION is the tag, the manifest version is the tag and RELEASE_NOTES.md has an exact `## $TAG` line. It prints every problem it finds, then fails. The publish step's asset read-back now tries `attempts=5` times with a `sleep 10` between tries (no sleep after the last) and fails after the last. `RELEASE_READBACK_ATTEMPTS` in stamp.py names the same bound, and the self-test pins the two to agree.
- The self-test cuts each step's own `run: |` block out of release.yml with `release_step_script` and runs it under `bash -e -c`, the errexit shell `tests/entities.py` countermeasure B requires. It never runs a copy of the step's logic.

Alternatives considered, and why they lost: (a) reading the base from the tag list alone (VERSION ignored) loses the case where VERSION is ahead of every tag, which is a first stamp after a manual VERSION fix. (b) Anchoring the windows on the newest tag minus hand tags listed by name would be a spelling list that the next hand tag defeats; the tree-VERSION rule is structural. (c) Deleting or retagging v7.1.2 is excluded by the brief, and v7.1.2 has downloads.

## Head

a082cf8aff7970127474c94bdbfca18c31328f0d: 6eb6ea0fc377b014be9720c75beae068e529b5e7 (the fix) merged with origin/main twice, 0a7c84fa2 and then 8a39977cba2f9f0c798647e8fe1b793e4fcdf106, because main moved during the handoff. Main's delta since c679f4b69 touches neither stamp.py, release.yml, tests/entities.py nor tests/closures.json (`git diff --stat c679f4b69 8a39977cb -- tools/release/stamp.py .github/workflows/release.yml tests/entities.py tests/closures.json` prints nothing). On the merged heads the self-test, all ten mutants and both null controls were run again, with the same results.

## Mutation proof

Driver: `$S/mutants.py` (sha1 ce2d7e026112f0fd0b4bfbbcef4acd0ff186c84e; `$S` is the seat's scratch directory, not in the tree). It applies each mutant to the working tree, runs `python3 -I tools/release/stamp.py --self-test`, prints the FAIL lines and restores the file. The unmutated run and the restored run each print `exit 0, 0 FAIL`.

- M1 `bump_base` returns `current`: exit 1; FAIL bump base: a hand tag above VERSION is the base, so the next patch is 7.1.3
- M2 `bump_base` drops the `TAG_RE` filter: exit 1; crash `ValueError: invalid literal for int() with base 10: '15-rc1'` (the non-release-tag pin)
- M3 `last_stamped_tag` skips the VERSION comparison: exit 1; FAIL last stamp: a tag whose tree VERSION is not its name is skipped; FAIL last stamp: non-release and VERSION-less tags are skipped, none is None
- M4 `last_stamped_tag` drops the `TAG_RE` filter: exit 1; FAIL last stamp: non-release and VERSION-less tags are skipped, none is None
- M5 `main()` anchors on the newest tag (the base line restored): exit 1; FAIL last stamp: main() anchors rules flush, 4 and 5 on the last stamped tag
- M6 `main()` bumps from VERSION (`base = current`): exit 1; FAIL bump base: main() reads it after the tag fetch and bumps from it
- M7 tree step drops the VERSION test: exit 1; FAIL release tree: a tag over another VERSION refuses (v7.1.2 at 7.1.1)
- M8 tree step drops the manifest test: exit 1; FAIL release tree: a manifest that disagrees refuses
- M9 tree step drops the notes test: exit 1; FAIL release tree: notes without the tag's own section refuse
- M10 publish step reads once (`attempts=1`): exit 1; FAIL release publish: an asset read back on the third read is published; FAIL release publish: an asset never read back fails after 5 reads, unpublished

The failing-first run: this head's stamp.py with the merge base's release.yml (`git show origin/main:.github/workflows/release.yml > .github/workflows/release.yml`) exits 1 with `ValueError: list.index(x): x not in list`, because the step is not there. The pure pins name `bump_base` and `last_stamped_tag`, which the merge base's stamp.py does not define.

## Null control

- Self-test, unmutated: `python3 -I tools/release/stamp.py --self-test` prints `RESULT stamp_self_test=pass`, exit 0.
- Each pin has its own null arm in the self-test, and each arm passes. `bump_base("7.1.1", ["v7.1.1"]) == "7.1.1"` (and `[]` gives `"7.1.1"`). `bump_base("6.2.14", ["v6.2.14", "v6.2.15-rc1"]) == "6.2.14"`. `last_stamped_tag(["v7.1.0","v7.1.1"]) == "v7.1.1"`; here the old newest-tag rule gives the same answer. A stamped tree releases (exit 0). An asset on the first read is published after one read.
- The release step on real tag trees: the stamp-era tags v7.1.0 and v7.1.1 pass (exit 0). v7.1.2 refuses (exit 1) on all three tests (see Figures).

## Figures

- Release tree step on real tags: `python3 $S/tree_proof.py v7.1.0 v7.1.1 v7.1.2` (sha1 30da5b81a3a36e9eaebabe149d897605e1f381e9). It `git archive`s each tag into a temp directory and runs `stamp.release_step_script(stamp.RELEASE_TREE_STEP)` under `bash -e -c` with `TAG` set. First it asserts that the extracted text equals PyYAML's `run` value for the step: `extractor == yaml run text: True`. Results: v7.1.0 exit 0, v7.1.1 exit 0, v7.1.2 exit 1 with `VERSION reads 7.1.1`, `the manifest version reads 7.1.1` and `RELEASE_NOTES.md has no '## v7.1.2' section`.
- Bump base and window anchor over this checkout's real tags. Rule: every local tag matching `TAG_RE`, VERSION read at the merge base, `stamp.bump_base`, `stamp.last_stamped_tag(tags, stamp.tag_version)`. Base rule: VERSION 7.1.1 -> next 7.1.2 (an existing tag), last_tag v7.1.2. Head rule: bump_base 7.1.2 -> next 7.1.3, last_stamped_tag v7.1.1. Tags whose tree VERSION is not their name: v3.1.0, v3.1.1, v3.1.2, v3.2.0 and v7.1.2. The v3 tags come before the stamp, are older than v7.1.1 and are never reached, because the search walks newest first and stops at the first match.
- Scoped gate, `tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 3 script(s) run, 30 scoped out` (doc_claims.py, entities.py, harness_headers.py). Plus run_always: `tests/layout.py`, `tests/closure.py selftest`, `tests/env_drift.py --claims-only <merge base>`, and `tests/structure.py`. Exits at the first commit 3f65ea301a5253fe7e5001d7f7a4f873687a8802: doc_claims 0, entities 1 (countermeasure B refused a bare `bash -c` in the two new self-test drivers), harness_headers 0, structure 0, layout 0, closure selftest 0, env_drift --claims-only 0. The head 6eb6ea0fc377b014be9720c75beae068e529b5e7 changes only those two driver lines, to `bash -e -c`. At the head, entities ran again and exited 0 (`ALL 2632 ENTITY CHECKS PASSED`), and prepr's `merged structure` step printed `STRUCTURE RATCHET PASSED`, with no budget moved. `tools/pr/prepr.sh` on this body: rc=0 at 6eb6ea0fc377 against origin/main c679f4b69. Main then moved, so origin/main was merged. At cf238ebe8 (merged with 0a7c84fa2) the scoped gate printed `MODE: SCOPED -- 3 script(s) run, 30 scoped out`, and every script and run_always line exited 0: doc_claims `ALL 296 checks PASSED`, entities `ALL 2632 ENTITY CHECKS PASSED`, harness_headers `ALL 112 HARNESS HEADER CHECKS PASSED`, structure `STRUCTURE RATCHET PASSED`, layout ok, closure selftest `ALL 118 closure shrink pins PASSED`, env_drift claims hygiene ok. prepr gave rc=0 at cf238ebe8. Main moved again during that run, so it was merged again, at 8a39977cb, and prepr was run again at a082cf8aff79.
- Architecture score: `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` prints `Architecture score: dS +0.0000 NULL`.
- Class census. Rule: `grep -rnE 'describe --tags|"tag", "--list"|tag --list|--sort=-v:refname|ls-remote", "--tags|ls-remote --tags|git tag -l' tools tests .github .claude/workflows | grep -v tests/closures.json` enumerates every reader of a tag list. Dispositions of the seams it returns:
  - `tools/release/stamp.py` rule 3 tag read: closed in this diff (bump base and last-stamp anchor).
  - `.github/workflows/governance.yml` `record` job `SINCE=$(git describe --tags --abbrev=0 --match 'v*')` (and its `HEAD^` arm), and `.github/workflows/nightly.yml` `SINCE=...`: these take the newest v* tag, so until the next stamp they anchor on v7.1.2. Outside this group's file scope (the roster names two files). The read heals itself at the v7.1.3 stamp, which is a stamped tag and becomes the newest again. The merges between v7.1.1 and v7.1.2 that `record` passes over meanwhile are in this stamp's rule-5 window, which now runs from v7.1.1, so the stamp's disposition gate checks them before the anchor moves. The new release step means a future hand tag publishes no release. It does not stop the tag being pushed, because the tag ruleset is the owner's barrier.
  - `tools/audit/seat/closeout.py`, `tools/audit/seat/prune_refs.py`: read `refs/tags/archive/*` only, not release tags. Not this class.
  - `tests/entities.py`, `tests/delivery_status.py` matches are a string literal and a comment; they read no tag.

## Red checks

none (no pull request exists yet; the orchestrator opens it from these refs)

## Forward-carry

none

## Friction

none
