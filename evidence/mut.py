import sys, re, types
sys.path[:0]=['tools/pr','tests','tests/hastub']
from pathlib import Path
src=Path('tools/pr/ci_predict.py').read_text()
M={
 'M10 named_loads not followed in mjs_closure': ('            stack += [f for _, line, f in named_loads(root, p) if (Path(p).name, f, line) not in exempt]\n','            pass\n'),
 'M11 Python imports not followed': ('            stack += py_imports(root, p)\n','            pass\n'),
 'M12 stale-exempt refusal dropped': ('    gaps += [f"GRADER_NAMED_EXEMPT: no grader source', '    gaps += [] and [f"GRADER_NAMED_EXEMPT: no grader source'),
 'M13 named gap enumeration dropped': ('                    gaps.append(f"{job}: {mark}\'s {src}:{n} names {f}, restored from the base and outside its key")','                    pass'),
 'M14 path.join arm dropped from NAMED': ('NAMED = re.compile(r"path', 'NAMED = re.compile(r"NEVERpath'),
}
for name,(a,b) in [(k,v) for k,v in M.items() if k.startswith('M14')]:
    assert src.count(a)==1, (name, src.count(a))
    m=types.ModuleType('ci_predict'); m.__file__=str(Path('tools/pr/ci_predict.py').resolve())
    sys.modules['ci_predict']=m
    exec(compile(src.replace(a,b),m.__file__,'exec'),m.__dict__)
    import io, contextlib
    buf=io.StringIO()
    with contextlib.redirect_stdout(buf): rc=m.grader_key_self_test(Path('.').resolve())
    fails=[l for l in buf.getvalue().splitlines() if 'FAIL' in l]
    print(f'{name}: {len(fails)} failed'); [print('   ',f.strip()) for f in fails]
