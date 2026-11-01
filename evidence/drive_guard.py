import ast, sys, importlib.util, re
spec = importlib.util.spec_from_file_location("h", sys.argv[1]); h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
src = open(sys.argv[2]).read()
m = re.search(r'FIELD = (\(.*?\))\n\n', src, re.S)
field = ast.literal_eval(m.group(1))
h.first_text = lambda: field
sys.exit(h.main(sys.argv[3:]))
