# `corpus_mirror.py`

- `corpus_mirror.py` — reads every published source of the repository once
  into `<private root>/corpus/` for an owner-only dimension's seats, which
  call nothing themselves: refs and history into a bare mirror, GitHub's text
  as stored pages and GraphQL batches, releases, the published site, alert
  lists, and each workflow run's logs, check runs and artifacts. Started by
  `owner_only.py launch`; by hand:

        python3 -I tools/audit/seat/corpus_mirror.py run --private-root <dir> --token-fd 3 [--own-identity] [--only S2,S3,S4,S5] 3< <token file>
        python3 -I tools/audit/seat/corpus_mirror.py cost --private-root <dir>

  - **The read budget is `gh_read.py`'s**, its constants `BATCH`, `MIN_GAP_S`,
    `FLOOR_SHARED` and `FLOOR_OWN`: one serial stream, a `rate_limit` read
    before every batch, and a batch only while core and graphql keep the
    floor. Below it, or on a rate-limit answer, it writes its cursor, prints
    `paused` and exits 0; the next run resumes there. Every page is cached
    with its ETag and re-read with `If-None-Match`. It issues no search and no
    write, or stops.
  - **`MANIFEST.json`** holds each source's denominator (enumerator,
    universe, examined, not_reached with a reason) and the scan's state. A
    ref namespace outside heads, tags and pull is a `not_reached` line and a
    non-zero exit. An archive that traverses, links, passes a size or
    ratio cap, names its own directory as a file, holds a path that is both
    a file and a directory, a name past the length cap, or a member that
    cannot be read, is refused whole, in `refused.json`. Whatever reading
    an archive's bytes raises is the archive's (`read_archive`); whatever
    this host's file system raises is this host's, is no answer, and is
    never a refusal (`Mirror.each`). A per-item read that answers an
    error, or that this host failed on, is `not_reached` in its pass and
    is read again by the next; a kept answer that is not `ok` (gone,
    refused) is `not_reached` in every pass and read once.
  - `cost` prints the scan's own calls per bucket; `gh_calls.py --top --since
    <scan start>` prints the shim's.
  - Not yet run against GitHub: the self-test stubs `gh`, `git` and HTTPS. An
    endpoint that does not serve what the script expects becomes a
    `not_reached` line, never a dropped row.
  `--self-test`: pause and exact resume under a secondary limit and a spent
  bucket, the floor, the namespace assertion, hostile and unreadable
  archives, the re-read of a unit that answered an error or that this host
  failed on, and one
  mutant per predicate.
