"""Example 3: use confidence and probabilities, not just the top answer.

This message mixes three problems: a late delivery, a wrong size, and a
double charge. A plain LLM would answer "returns" and hide the rest.
Jev's probabilities show billing is also involved, and its confidence
shows the customer never said what they actually want.
"""

from _show import header, show_answers, show_questions, show_reasons, show_state, step

from jev_demo import ask
from jev_demo.triage import ROUTING_QUESTIONS, route_ticket

TICKET = (
    "Shoes arrived two weeks late and in the wrong size. Also I see two charges of "
    "$120 on my card. What are you going to do about this?"
)

if __name__ == "__main__":
    header(3, "Confidence-aware routing", "when Jev is unsure, it says so, and your code can act on that")

    step(1, "The STATE: a messy message with three problems in it")
    show_state(TICKET)

    step(2, "The QUESTIONS: five Choice questions, all answered in one request")
    show_questions(ROUTING_QUESTIONS)

    step(3, "Jev's ANSWERS: look at the bars, not just the top pick")
    answers = ask(TICKET, ROUTING_QUESTIONS, fixture="ambiguous_ticket")
    show_answers(answers)

    step(4, "YOUR CODE decides, using confidence thresholds from jev_demo/triage.py")
    decision = route_ticket(answers)
    show_reasons(decision.reasons)
    print(f"\n    ROUTE TO: {decision.team}  (issue: {decision.issue})")
    print(f"    CC:       {', '.join(decision.cc_teams) or 'nobody'}")
    print(f"    ACTIONS:  {', '.join(decision.actions) or 'none'}\n")
