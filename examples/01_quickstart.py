"""Example 1: one message, three question types, one request.

Jev does not write a reply. For each question it returns a typed answer
(an option, a level, or a probability) that code can use directly.
"""

from _show import header, show_answers, show_questions, show_reasons, show_request_json, show_state, step

from jev_demo import ask, build_request
from jev_demo.triage import SUPPORT_QUESTIONS, support_action

TICKET = (
    "Our API integration started returning 500 errors on every request about "
    "20 minutes ago, and we can't process any customer orders until this is fixed."
)

if __name__ == "__main__":
    header(1, "Quickstart", "send data + typed questions, get typed answers back, not prose")

    step(1, "The STATE: the data Jev looks at (a support message)")
    show_state(TICKET)

    step(2, "The QUESTIONS: one of each primitive")
    show_questions(SUPPORT_QUESTIONS)
    print("\n    choice = pick one option | score = which level on a scale | noul = is this true? (0-1)")

    step(3, "What actually goes over the wire: POST https://api.typesafe.ai/v1/systemone")
    show_request_json(build_request(TICKET, SUPPORT_QUESTIONS))

    step(4, "Jev's ANSWERS: each question answered independently, with probabilities")
    answers = ask(TICKET, SUPPORT_QUESTIONS, fixture="quickstart")
    show_answers(answers)

    step(5, "YOUR CODE decides (rules live in jev_demo/triage.py, not in a prompt)")
    decision = support_action(answers)
    show_reasons(decision.reasons)
    print(f"\n    ACTION: {decision.action}\n")
