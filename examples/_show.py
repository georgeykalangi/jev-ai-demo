"""Printing helpers that narrate each example step by step."""

import json
import textwrap

from jev_demo import is_live

BAR_WIDTH = 20
LABEL_WIDTH = 34


def header(number: int, title: str, idea: str) -> None:
    mode = "LIVE: calling api.typesafe.ai" if is_live() else "OFFLINE: replaying a recorded response from the TypeSafe docs"
    print(f"\n{'=' * 72}\nExample {number}: {title}\n{'=' * 72}")
    print(f"mode: {mode}")
    print(f"idea: {idea}")


def step(number: int, text: str) -> None:
    print(f"\n[{number}] {text}")


def show_state(state: str) -> None:
    for line in textwrap.wrap(state, 66):
        print(f"    | {line}")


def show_questions(questions: dict) -> None:
    for question_id, question in questions.items():
        print(f"    - {question_id} ({question['type']}): {question['instructions']}")
        criteria = question.get("criteria")
        if isinstance(criteria, dict):
            print(f"        options: {', '.join(criteria)}")
        elif isinstance(criteria, list):
            for level, text in enumerate(criteria):
                print(f"        level {level}: {text}")


def show_request_json(body: dict) -> None:
    print(textwrap.indent(json.dumps(body, indent=2), "    "))


def bar(probability: float) -> str:
    filled = round(probability * BAR_WIDTH)
    return "#" * filled + "." * (BAR_WIDTH - filled)


def show_answers(answers: dict) -> None:
    for question_id, answer in answers.items():
        kind = answer["type"]
        if kind == "noul":
            print(f"    {question_id}: noul = {answer['noul']:.2f}  (probability the statement is true)")
            print(f"        {'true':<{LABEL_WIDTH}} {bar(answer['noul'])} {answer['noul']:.2f}")
            continue

        value = answer["choice"] if kind == "choice" else f"{answer['score']:.2f} (expected level)"
        print(f"    {question_id}: {kind} = {value}   confidence {answer['confidence']:.2f}")
        legend = answer.get("legend", {})
        for option, probability in sorted(answer["probabilities"].items(), key=lambda kv: -kv[1]):
            label = f"{option}: {legend[option]}" if option in legend else option
            label = label if len(label) <= LABEL_WIDTH else label[: LABEL_WIDTH - 3] + "..."
            print(f"        {label:<{LABEL_WIDTH}} {bar(probability)} {probability:.2f}")


def show_reasons(reasons: list[str]) -> None:
    for reason in reasons:
        print(f"    - {reason}")
