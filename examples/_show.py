"""Shared printing helpers for the examples."""

import json

from jev_demo import is_live


def banner(title: str) -> None:
    mode = "LIVE (calling api.typesafe.ai)" if is_live() else "OFFLINE (replaying recorded docs response)"
    print(f"\n=== {title} ===\nmode: {mode}\n")


def show_request(body: dict) -> None:
    print("--> request body sent to POST /v1/systemone")
    print(json.dumps(body, indent=2), "\n")


def show_answers(answers: dict) -> None:
    print("<-- answers")
    for question_id, answer in answers.items():
        value = answer.get("choice", answer.get("score", answer.get("noul")))
        confidence = answer.get("confidence")
        conf_text = f"  (confidence {confidence:.2f})" if confidence is not None else ""
        print(f"  {question_id:<22} {answer['type']:<7} -> {value}{conf_text}")
    print()
