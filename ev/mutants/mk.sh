# usage: mk.sh <dir> ; builds archive copy at head with partial features
set -e
D=$1; rm -rf $D; mkdir -p $D
git -C /home/user/rev archive 785d43a97fe5ca765b97090a0e735c2d5690f11e | tar -x -C $D
head -n 14131 $D/tests/features.py > $D/tests/partial.py
printf '\nsys.exit(R.close("PARTIAL"))\n' >> $D/tests/partial.py
