"""Example 2: ask atomic questions, combine them in code.

Instead of one vague question ("what priority is this bug?"), ask three
narrow Score questions and weight them in Python. To change how priority
works, you edit a weight, not a prompt.
"""

from _show import header, show_answers, show_questions, show_state, step

from jev_demo import ask
from jev_demo.triage import (
    BUG_PRIORITY_QUESTIONS,
    FRUSTRATION_WEIGHT,
    REPORT_QUALITY_WEIGHT,
    SEVERITY_WEIGHT,
    bug_priority,
    normalized_score,
    priority_label,
)

TICKET = (
    "Export to PDF fails with a spinner that never finishes. Some of our team say CSV "
    "export still works for them, others say it fails too. This is the third time I'm "
    "writing in and honestly I'm done. Steps: open any report, click Export, choose PDF. "
    "Chrome 128 on macOS."
)

WEIGHTS = {
    "severity": SEVERITY_WEIGHT,
    "frustration": FRUSTRATION_WEIGHT,
    "report_quality": REPORT_QUALITY_WEIGHT,
}

if __name__ == "__main__":
    header(2, "Atomic scoring", "three narrow questions + weights in code beat one vague question")

    step(1, "The STATE: a bug report")
    show_state(TICKET)

    step(2, "The QUESTIONS: three independent Score questions (each a scale of levels)")
    show_questions(BUG_PRIORITY_QUESTIONS)

    step(3, "Jev's ANSWERS: score = expected level, e.g. 1.24 means mostly level 1, some level 2")
    answers = ask(TICKET, BUG_PRIORITY_QUESTIONS, fixture="bug_priority")
    show_answers(answers)

    step(4, "YOUR CODE combines them: normalise each score to 0-1, then weight it")
    for question_id, weight in WEIGHTS.items():
        top_level = len(BUG_PRIORITY_QUESTIONS[question_id]["criteria"]) - 1
        part = normalized_score(answers, question_id, BUG_PRIORITY_QUESTIONS)
        raw = answers[question_id]["score"]
        print(f"    {question_id:<15} {raw:.2f} / {top_level} = {part:.2f}  x weight {weight}  = {part * weight:.3f}")

    priority = bug_priority(answers)
    print(f"    {'':<15} {'':>27}total = {priority:.3f}")
    print(f"\n    PRIORITY: {priority_label(priority)}  (P1 >= 0.7, P2 >= 0.4, else P3)")
    print("    Care more about frustrated customers? Raise FRUSTRATION_WEIGHT. No prompt changes.\n")
