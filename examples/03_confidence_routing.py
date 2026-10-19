"""Use confidence and probabilities, not just the top answer.

This ticket mixes a late delivery, a wrong size, and a double charge.
Jev picks "returns" but only with 0.42 confidence, and gives billing 0.35.
The code routes to returns, CCs billing, and asks the customer to clarify
because the requested resolution is unclear (confidence 0.20).
"""

from _show import banner, show_answers

from jev_demo import ask
from jev_demo.triage import ROUTING_QUESTIONS, route_ticket

TICKET = (
    "Shoes arrived two weeks late and in the wrong size. Also I see two charges of "
    "$120 on my card. What are you going to do about this?"
)

if __name__ == "__main__":
    banner("3. Confidence-aware routing")
    answers = ask(TICKET, ROUTING_QUESTIONS, fixture="ambiguous_ticket")
    show_answers(answers)
    print("department probabilities:", answers["department"]["probabilities"])
    print("decision:", route_ticket(answers))
