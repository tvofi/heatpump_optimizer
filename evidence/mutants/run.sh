cd $1 && PYTHONPATH=tests/hastub timeout 1800 python3 tests/partial.py > out.txt 2>&1; echo "rc=$?" >> out.txt
