import sys, os, runpy, io, contextlib
root=sys.argv[1]; os.chdir(root); sys.path[:0]=[root+'/tests', root+'/tests/hastub', root]
src=open('tests/backtest.py').read()
cut=src.index('# Wood furnace sizing (item 28)')
cut=src.rindex('\n# ====', 0, cut)
g={'__name__':'bt','__file__':root+'/tests/backtest.py'}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src[:cut], 'backtest.py', 'exec'), g)
sg=g['_store_gain']; print(root[-8:], {k: round(v,4) for k,v in sg.items()}, 'margin', round(sg['winter_typical']-sg['flat'],4))
