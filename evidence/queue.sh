H=bba5b4d4d7ac37f339850de36b1ca24573f8c821; B=9a54629e11622402cb001502b9087650c1adc6a4
jobs_list="$H head null_comment
$H head m4
$H head m6
$H head guard_off
$H head check_after_read
$H head frame_time_off
$H head transl_off
$H head transl_key_off
$H head measure
$H head frame_bypass
$H head deadline_none
$B r4base null_comment
$B r4base m4
$B r4base m6
$B r4base transl_off"
echo "$jobs_list" | xargs -P 2 -L 1 bash /tmp/mut/runmut.sh
echo QUEUE-DONE
