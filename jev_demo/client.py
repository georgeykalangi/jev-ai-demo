"""Minimal Jev client: one POST, standard library only.

Live mode:    TYPESAFE_API_KEY is set (in the environment or in .env), so
              requests go to the TypeSafe API.
Offline mode: no key found, so a recorded response from fixtures/ is replayed.
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
REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = REPO_ROOT / "fixtures"
ENV_FILE = REPO_ROOT / ".env"


class JevError(RuntimeError):
    """Raised when the Jev API returns an error or cannot be reached."""


def api_key() -> str | None:
    """TYPESAFE_API_KEY from the environment, falling back to the .env file."""
    if os.environ.get(API_KEY_ENV):
        return os.environ[API_KEY_ENV]
    if not ENV_FILE.exists():
        return None
    for line in ENV_FILE.read_text().splitlines():
        name, _, value = line.partition("=")
        if name.strip() == API_KEY_ENV and value.strip():
            return value.strip().strip("'\"")
    return None


def is_live() -> bool:
    return api_key() is not None


def build_request(state: str | dict, questions: dict, model: str = DEFAULT_MODEL) -> dict:
    """The full request body: the state, plus independent typed questions about it."""
    return {"model": model, "state": state, "questions": questions}


def ask(state: str | dict, questions: dict, fixture: str | None = None) -> dict:
    """Ask Jev every question about `state` at once and return the `answers` dict.

    `fixture` names the recorded response to replay when no API key is set.
    """
    body = build_request(state, questions)
    key = api_key()
    if key:
        response = _post(body, key)
    elif fixture:
        response = load_fixture(fixture)
    else:
        raise JevError(f"Set {API_KEY_ENV} to call Jev, or pass a fixture to replay.")

    _check_answers_match(questions, response["answers"])
    return response["answers"]


def load_fixture(name: str) -> dict:
    path = FIXTURES_DIR / f"{name}.json"
    return json.loads(path.read_text())["response"]


def _post(body: dict, key: str) -> dict:
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
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
