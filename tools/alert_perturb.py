#!/usr/bin/env python3
"""Round-5 seat: perturbations of revision 4's alert_list.py (4.3 step 5) beyond its
self-test. Imports it unchanged and drives reds() over its own fixture builders.

  python3 -I tools/alert_perturb.py <rev4>/measure/rev
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
import alert_list as A  # noqa: E402

P = f"code-scanning alert 7 ({A.PLANT})"
EMPTY, THREE, M, R = A.EMPTY, A.THREE, A.M, A.R


def run(label, get, want_ok, want, note, **kw):
    ok, got = A.reds(get, R, kw.get("M", M), kw.get("legs", A.LEGS), A.BASE, kw.get("base_repeats", False))
    hit = ok == want_ok and (not ok or got == want)
    print(f"{'as-stated' if hit else 'DIFFERS  '} {label}: {'listed ' + str(got) if ok else got}\n      {note}")
    return hit


def main():
    res = []
    # H: a same-commit newer upload with an empty python SARIF (R-10's named residual)
    res.append(run("H  same-M newer hand upload, empty SARIF, same category",
                   A.world([A.an(15, "python", M)] + THREE, {15: A.sarif(), 13: A.sarif((7, A.PLANT)), **EMPTY},
                           [A.alert(7, A.PLANT, "fixed", M)]), True, [],
                   "the plant is MISSED (false green direction): the residual DESIGN-P2 R-10 names; needs security-events: write"))
    # page boundary: exactly 100 dismissed on page 1, the needed one on page 2
    res.append(run("PB exactly 100 rows on page 1, the dismissal on page 2",
                   A.world(THREE, {13: A.sarif((7, A.PLANT), (250, "py/x")), **EMPTY},
                           [A.alert(1000 + i, "py/y", "dismissed", M) for i in range(100)] + [A.alert(250, "py/x", "dismissed", M)]),
                   True, [P], "pagination reads page 2 when page 1 is full"))
    # D-X: alert dismissed, but the ref listing does not return it (state read per ref unknown)
    res.append(run("DX dismissed alert absent from the ref's dismissed listing",
                   A.world(THREE, {13: A.sarif((7, A.PLANT)), **EMPTY}, []), True, [P],
                   "over-lists (false red, fail-safe): the body must answer a dismissed alert"))
    # one alert number reported by two legs
    res.append(run("2L one alert number in two legs' SARIF",
                   A.world(THREE, {13: A.sarif((7, A.PLANT)), 12: A.sarif((7, A.PLANT)), 11: A.sarif()},
                           [A.alert(7, A.PLANT, "open", M)]), True, [P], "listed once"))
    # analyses listing oldest-first (order assumption broken), two same-M analyses differ
    res.append(run("OR analyses listed oldest-first; older same-M analysis lacks the plant",
                   A.world(list(reversed([A.an(15, "python", M)] + THREE)), {15: A.sarif((7, A.PLANT)), 13: A.sarif(), **EMPTY},
                           [A.alert(7, A.PLANT, "open", M)]), True, [],
                   "step 4's next() takes the first row; relies on the listing's documented created-desc default"))
    print(f"\nALERT-PERTURB {sum(res)}/{len(res)} as stated in this tool's expectations")


if __name__ == "__main__":
    main()
