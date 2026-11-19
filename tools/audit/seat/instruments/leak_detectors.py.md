# `leak_detectors.py`

- `leak_detectors.py` — in `tools/audit/`, beside the seat instruments: candidate spans of data already
  published, by class (host path, token, address outside GitHub's noreply
  grammar, coordinates, private network address, person entity), for an
  owner-only seat to judge. The host-path grammar is `ref_privacy.py`'s,
  imported. A candidate is no finding, and a quiet detector proves nothing
  about a unit; what it does not detect is in its docstring.

        python3 -I tools/audit/leak_detectors.py scan --out <file under $HPO_PRIVATE_ROOT> <file>...
        python3 -I tools/audit/leak_detectors.py locate --file <f> --offset <n> --length <l> [--masked]

  `scan` refuses an `--out` outside the private root and prints neither a
  file, a class nor a value. `locate` is the location harness a leaked-data or
  opinion finding cites: it prints the span, and with `--masked` nothing.
  `--self-test`: a planted twin per class, the masked perturbation, the quiet
  list, and one mutant per predicate.
