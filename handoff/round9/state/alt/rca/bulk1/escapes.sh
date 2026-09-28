#!/bin/sh
# releases carrying each instance, lower bound: tags that contain the round's
# audit baseline and do not contain the fix (HEAD for an open instance).
cd /home/user/heatpump_optimizer
while read cls inst base fix; do
  n=$(git tag --contains "$base" --no-contains "$fix" | wc -l)
  first=$(git tag --contains "$base" --sort=creatordate | head -1)
  fixed=$(git tag --contains "$fix" --sort=creatordate | head -1)
  echo "$cls $inst base=$base first_tag_with_base=$first fix=$fix first_tag_with_fix=${fixed:-none} releases_carrying>=$n"
done <<'L'
P7 #243 c398fc8 90c71c47
P7 #777 ae36eff1 c7e2f817
P7 #1299 1cc89e0 8454c07d
P7 #1665 1936d5ca e90c649b
P10 #199 4bf3d7d 8542e51c
P10 #290 c398fc8 8542e51c
P10 #783 ae36eff1 546b4924
P10 #1399 e336cc2c 3489d4f7
P10 #1658 1936d5ca origin/main
P8 #168 4bf3d7d 2c135037
P8 #940 7dd68dd a97681b5
P8 #961 7dd68dd c27cb8d9
P8 #1456 f9d6f782 57a6e19f
P8 #1513 cdf82daa 56cb0027
P8 #1657 1936d5ca origin/main
P4 #185 4bf3d7d 38dc0610
P4 #826 ae36eff1 5cddbc9c
P4 #1447 f9d6f782 20cb1c46
P4 #1664 1936d5ca origin/main
L
