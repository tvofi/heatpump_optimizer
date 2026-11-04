import sys; sys.argv=['x']; sys.path.insert(0,'tests'); sys.path.insert(0,'tests/hastub')
import arch_score as A
A.card_rule_spellings(); A.card_template_spellings()
print("failed:", A.R.failed if hasattr(A.R,'failed') else '?')
