"""Minimal Jev client: one POST, standard library only.

Live mode:    set TYPESAFE_API_KEY and requests go to the TypeSafe API.
Offline mode: no key set, so a recorded response from fixtures/ is replayed.
"""

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "https://api.typesafe.ai/v1/systemone"
DEFAULT_MODEL = "jev-latest"
API_KEY_ENV = "TYPESAFE_API_KEY"
REQUEST_TIMEOUT_SECONDS = 30
FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


class JevError(RuntimeError):
    """Raised when the Jev API returns an error or cannot be reached."""


def is_live() -> bool:
    return bool(os.environ.get(API_KEY_ENV))


def build_request(state: str | dict, questions: dict, model: str = DEFAULT_MODEL) -> dict:
    """The full request body: the state, plus independent typed questions about it."""
    return {"model": model, "state": state, "questions": questions}


def ask(state: str | dict, questions: dict, fixture: str | None = None) -> dict:
    """Ask Jev every question about `state` at once and return the `answers` dict.

    `fixture` names the recorded response to replay when no API key is set.
    """
    body = build_request(state, questions)
    if is_live():
        response = _post(body, os.environ[API_KEY_ENV])
    elif fixture:
        response = load_fixture(fixture)
    else:
        raise JevError(f"Set {API_KEY_ENV} to call Jev, or pass a fixture to replay.")

    _check_answers_match(questions, response["answers"])
    return response["answers"]


def load_fixture(name: str) -> dict:
    path = FIXTURES_DIR / f"{name}.json"
    return json.loads(path.read_text())["response"]


def _post(body: dict, api_key: str) -> dict:
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as err:
        raise JevError(f"Jev API returned {err.code}: {err.read().decode()[:300]}") from err
    except urllib.error.URLError as err:
        raise JevError(f"Could not reach Jev API: {err.reason}") from err


def _check_answers_match(questions: dict, answers: dict) -> None:
    missing = set(questions) - set(answers)
    if missing:
        raise JevError(f"Response is missing answers for: {sorted(missing)}")
