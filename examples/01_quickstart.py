"""One state, three question types, one request.

Jev does not write text back. It returns a typed answer per question.
"""

from _show import banner, show_answers, show_request

from jev_demo import ask, build_request, choice, noul, score

TICKET = (
    "Our API integration started returning 500 errors on every request about "
    "20 minutes ago, and we can't process any customer orders until this is fixed."
)

QUESTIONS = {
    "department": choice(
        "Which team should handle this",
        {
            "billing": "Payment or subscription issues",
            "technical": "Bugs or integration problems",
            "sales": "Pricing or account questions",
        },
    ),
    "frustration": score(
        "How frustrated the customer appears",
        ["Calm, just stating facts", "Frustrated but civil", "Very angry, strong language"],
    ),
    "is_urgent": noul("The message conveys urgency or time-sensitivity"),
}

if __name__ == "__main__":
    banner("1. Quickstart: choice + score + noul")
    show_request(build_request(TICKET, QUESTIONS))
    answers = ask(TICKET, QUESTIONS, fixture="quickstart")
    show_answers(answers)
    # Typed answers go straight into code. No parsing of free text.
    if answers["is_urgent"]["noul"] > 0.9 and answers["department"]["choice"] == "technical":
        print("action: page the on-call engineer")
