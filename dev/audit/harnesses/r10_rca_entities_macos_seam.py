#!/usr/bin/env python3
"""The macOS sampler seam of tests/entities.py, its checks run verbatim, and four mutants.

    python3 dev/audit/harnesses/r10_rca_entities_macos_seam.py [tests/entities.py]

Root-cause record: dev/audit/rca/R10-RCA-ENTITIES-MACOS.md. The seam
(``_hb_stdlib_sampling``) and its three checks are cut from the file between
``def _hb_stdlib_sampling(`` and the ``_hb_samples, _hb_why = (`` call site and
exec'd against a stub ``R``; no real process is sampled, so the run takes
milliseconds on any host. It prints one ``<arm> FAILS <n>`` line per arm: the
head must print 0, every mutant at least 1.
"""
from __future__ import annotations

import sys

ARM = "    except PermissionError as exc:\n        if platform != \"darwin\":\n            raise\n"
MUTANTS = {
    # the denial escapes, as before the fix: the script ends at the sampler
    "M1-no-catch": (ARM + "        return None, f\"{platform}: {exc}\"\n", "    except ZeroDivisionError:\n        raise\n"),
    # a Linux denial becomes a skip: CI would go green by skipping
    "M2-skip-off-darwin": ("        if platform != \"darwin\":\n            raise\n", ""),
    # every error becomes a skip, not only the task-port denial
    "M3-catch-all": ("    except PermissionError as exc:", "    except Exception as exc:"),
    # a skip with no reason: the call site falls through to the no-unwinder arm and passes silently
    "M4-unnamed-skip": ('return None, f"{platform}: {exc}"', 'return None, ""'),
}


def run(text: str) -> int:
    lines = text.splitlines(keepends=True)
    start = next(i for i, ln in enumerate(lines) if ln.startswith("def _hb_stdlib_sampling("))
    end = next(i for i, ln in enumerate(lines) if i > start and ln.startswith("_hb_samples, _hb_why = ("))

    class R:
        fails = 0

        @classmethod
        def check(cls, name: str, cond: bool, detail: str = "") -> bool:
            cls.fails += not cond
            print(("    ok   " if cond else "    FAIL ") + name[:72] + ("" if cond else f"  [{detail}]"))
            return bool(cond)

    def never(spin: bool) -> str:
        raise AssertionError("the seam's checks must never take a real sample")

    exec("".join(lines[start:end]), {"R": R, "sys": sys, "_hb_stdlib_reads": never})  # noqa: S102
    return R.fails


def main() -> int:
    text = open(sys.argv[1] if len(sys.argv) > 1 else "tests/entities.py", encoding="utf-8").read()
    bad = 0
    print("head")
    head = run(text)
    print(f"head FAILS {head}")
    bad += head != 0
    for name, (old, new) in MUTANTS.items():
        if text.count(old) != 1:
            print(f"{name} NOT APPLIED (the seam moved; update this harness)")
            bad += 1
            continue
        print(name)
        n = run(text.replace(old, new, 1))
        print(f"{name} FAILS {n}")
        bad += n == 0
    print("SEAM HARNESS " + ("OK" if not bad else f"{bad} ARM(S) WRONG"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
