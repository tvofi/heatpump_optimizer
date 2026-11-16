"""Reviewer's own mutants of the round-1 guards (not the tables' spellings): each is planted in a copy and the
instrument's self-test is run without its mutant table; a survivor is a predicate no case pins."""
import shutil, subprocess, sys, tempfile
from pathlib import Path
M = {
 "tools/audit/seat/owner_only.py": [
  ("work tree: or read as and", "    elif rc != 128 or NOT_A_REPOSITORY not in err:\n", "    elif rc != 128 and NOT_A_REPOSITORY not in err:\n"),
  ("reach: a denied stat read as absent", "        except PermissionError:\n            return DENIED\n", "        except PermissionError:\n            return ABSENT\n"),
  ("reach: any OSError read as denied", "        except OSError:\n            return UNKNOWN\n", "        except OSError:\n            return DENIED\n"),
  ("owner path: the names loop dropped", "    if any(view.reach(os.path.join(path, name)) == OPEN for name in names):\n", "    if False:\n"),
  ("credential fill: a failure with no stderr passes", "    elif rc != 0 and not NO_CREDENTIAL.search(err):\n", "    elif rc != 0 and err and not NO_CREDENTIAL.search(err):\n"),
  ("home dir: unlistable only when open", "        if names is None and view.reach(d) != ABSENT:\n", "        if names is None and view.reach(d) == OPEN:\n"),
  ("model exemption widened to any KEY name", "(name not in (model_env, \"SSH_AUTH_SOCK\") and credential_named(name))", "(name not in (model_env, \"SSH_AUTH_SOCK\") and not name.endswith(\"_KEY\") and credential_named(name))"),
  ("gh: timeout read as no login", "        elif rc is None:\n", "        elif rc is None and False:\n"),
  ("run: OSError only", "        except (OSError, subprocess.TimeoutExpired):\n", "        except OSError:\n"),
 ],
 "tools/audit/seat/corpus_mirror.py": [
  ("directory itself: a directory entry too", "        if target == base and not info.is_dir():\n", "        if target == base:\n"),
  ("every member counted a file", "        (parents if info.is_dir() else files).add(target)\n", "        files.add(target)\n"),
  ("every member counted a directory", "        (parents if info.is_dir() else files).add(target)\n", "        parents.add(target)\n"),
  ("write failure: ValueError uncaught", "        except (OSError, ValueError, zipfile.BadZipFile) as e:\n", "        except (OSError, zipfile.BadZipFile) as e:\n"),
  ("write failure: BadZipFile uncaught", "        except (OSError, ValueError, zipfile.BadZipFile) as e:\n", "        except (OSError, ValueError) as e:\n"),
  ("new pass: only error states dropped", "if not answered(state)]:", "if state.startswith(\"error\")]:"),
  ("size is no answer", 'ANSWERED = ("ok", "gone", "size", ', 'ANSWERED = ("ok", "gone", '),
 ],
}
surv = 0
for rel, muts in M.items():
    src = Path(rel).read_text()
    for name, old, new in muts:
        if src.count(old) != 1 and not (src.count(old) >= 1 and "ANSWERED" in old):
            print(f"SKIP {rel}: {name}: anchor found {src.count(old)} times"); continue
        td = Path(tempfile.mkdtemp()); dst = td / "tools" / "audit" / "seat"
        shutil.copytree(Path("tools/audit/seat"), dst)
        (td / rel).write_text(src.replace(old, new, 1))
        p = subprocess.run([sys.executable, "-I", str(td / rel), "--self-test", "--no-mutants"], capture_output=True, text=True, timeout=600)
        tail = [l for l in (p.stdout + p.stderr).splitlines() if "FAIL" in l or "Error" in l][-1:] or [""]
        k = p.returncode != 0
        surv += not k
        print(f"{'killed  ' if k else 'SURVIVED'} {rel.split('/')[-1]}: {name}" + (f"  [{tail[0][:150]}]" if k else ""))
        shutil.rmtree(td, ignore_errors=True)
print(f"RESULT reviewer mutants survived={surv}")
