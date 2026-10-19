"""Example 4 (live only): run Jev on your own message.

    .venv/bin/python examples/04_try_your_own.py "My card was charged twice!!"

Needs TYPESAFE_API_KEY (environment or .env). There is no recording to
replay here, because the input is whatever you type.
"""

import sys

from _show import header, show_answers, show_reasons, show_state, step

from jev_demo import JevError, ask, is_live
from jev_demo.client import API_KEY_ENV
from jev_demo.triage import SUPPORT_QUESTIONS, support_action

USAGE = 'usage: .venv/bin/python examples/04_try_your_own.py "your support message"'

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(USAGE)
    if not is_live():
        sys.exit(
            f"This example calls the real model. Put {API_KEY_ENV}=<your key> in .env\n"
            "(get one at https://console.typesafe.ai/keys), then run it again."
        )

    message = " ".join(sys.argv[1:])
    header(4, "Try your own message", "same questions as Example 1, your input, the real model")

    step(1, "The STATE: your message")
    show_state(message)

    step(2, "Jev's ANSWERS")
    try:
        answers = ask(message, SUPPORT_QUESTIONS)
    except JevError as err:
        sys.exit(f"    {err}")
    show_answers(answers)

    step(3, "YOUR CODE decides")
    decision = support_action(answers)
    show_reasons(decision.reasons)
    print(f"\n    ACTION: {decision.action}\n")
