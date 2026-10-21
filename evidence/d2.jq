($a[0].groups|map({key:.group,value:.})|from_entries) as $A | (.groups|map({key:.group,value:.})|from_entries) as $B |
([$B|keys[]]-[$A|keys[]]) as $new |
{new: ($new|length),
 new_carries: ([$new[]|($B[.].carry//[])|length]|add),
 stage: [$B|to_entries[]|select($A[.key]!=null and $A[.key].resume.stage!=.value.resume.stage)|.key]|length,
 carry_groups: [$B|to_entries[]|select($A[.key]!=null and (($A[.key].carry//[])|length)!=((.value.carry//[])|length))|"\(.key) \($A[.key].carry|length)->\(.value.carry|length)"],
 carry_appended: ([$B|to_entries[]|select($A[.key]!=null)|((.value.carry//[])|length)-(($A[.key].carry//[])|length)]|add),
 text_edits: [$B|to_entries[]|select($A[.key]!=null) as $e | select(["brief","issues","fixes","findings"]|any(. as $k|$A[$e.key][$k]!=$e.value[$k]))|.key]|length}
