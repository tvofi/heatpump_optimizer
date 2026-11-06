import sys
p = sys.argv[1]; m = sys.argv[2]
s = open(p).read()
OLD_BLOCK = '''        try:
            text: str | None = path.read_text()
        except FileNotFoundError:
            return i  # absent: the O_EXCL-style create (`Owner.create`) arbitrates
        except OSError:
            text = None
        try:
            owner = None if text is None else parse_owner(text)
        except ValueError:
            owner = None
        if owner is None:
            _steal(path, None)  # unparseable: no live holder to lose; a fresh owner is put back
            return i
'''
assert OLD_BLOCK in s
if m == "M1":  # merge base's form
    new = '''        owner = _read_at(path)
        if owner is None:
            if not path.is_file():
                return i
            path.unlink(missing_ok=True)
            return i
'''
elif m == "M2":  # is_file second read restored, reap through _steal
    new = '''        owner = _read_at(path)
        if owner is None:
            if not path.is_file():
                return i
            _steal(path, None)
            return i
'''
elif m == "M3":  # head's single read, old unlink for the broken branch
    new = OLD_BLOCK.replace("_steal(path, None)  #", "path.unlink(missing_ok=True)  #")
elif m == "M4":  # broken slot not reaped at all
    new = OLD_BLOCK.replace("            _steal(path, None)  # unparseable: no live holder to lose; a fresh owner is put back\n", "")
elif m == "M5":  # absent treated as broken
    new = OLD_BLOCK.replace("            return i  # absent", "            text = None  # absent")
s = s.replace(OLD_BLOCK, new); open(p, "w").write(s)
