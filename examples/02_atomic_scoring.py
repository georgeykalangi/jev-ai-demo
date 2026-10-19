"""Ask atomic questions, combine them in code.

Instead of asking "what priority is this bug?", ask three narrow Score
questions and weight them in Python. Re-prioritising = editing a weight.
"""

from _show import banner, show_answers

from jev_demo import ask
from jev_demo.triage import (
    BUG_PRIORITY_QUESTIONS,
    FRUSTRATION_WEIGHT,
    REPORT_QUALITY_WEIGHT,
    SEVERITY_WEIGHT,
    bug_priority,
)

TICKET = (
    "Export to PDF fails with a spinner that never finishes. Some of our team say CSV "
    "export still works for them, others say it fails too. This is the third time I'm "
    "writing in and honestly I'm done. Steps: open any report, click Export, choose PDF. "
    "Chrome 128 on macOS."
)

if __name__ == "__main__":
    banner("2. Atomic scoring: three Score questions -> one priority")
    answers = ask(TICKET, BUG_PRIORITY_QUESTIONS, fixture="bug_priority")
    show_answers(answers)
    print(
        f"priority = {SEVERITY_WEIGHT}*severity + {FRUSTRATION_WEIGHT}*frustration "
        f"+ {REPORT_QUALITY_WEIGHT}*report_quality (each normalised to 0-1)"
    )
    print(f"priority = {bug_priority(answers):.2f}")
