import copy

import pytest

from jev_demo import JevError, ask, build_request, choice, noul, score
from jev_demo.client import API_KEY_ENV, load_fixture
from jev_demo.triage import BUG_PRIORITY_QUESTIONS, ROUTING_QUESTIONS, bug_priority, route_ticket


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.delenv(API_KEY_ENV, raising=False)


@pytest.fixture
def routing_answers():
    return copy.deepcopy(load_fixture("ambiguous_ticket")["answers"])


def test_question_builders_produce_api_shape():
    body = build_request(
        "state",
        {
            "c": choice("pick", {"a": "A", "b": None}),
            "s": score("rate", ["low", "high"]),
            "n": noul("is it true"),
        },
    )
    assert body["model"] == "jev-latest"
    assert body["questions"]["c"] == {"type": "choice", "instructions": "pick", "criteria": {"a": "A", "b": None}}
    assert body["questions"]["s"]["criteria"] == ["low", "high"]
    assert body["questions"]["n"] == {"type": "noul", "instructions": "is it true"}


def test_ask_without_key_or_fixture_fails_clearly():
    with pytest.raises(JevError, match=API_KEY_ENV):
        ask("state", {"n": noul("x")})


def test_ask_rejects_response_missing_an_answer():
    with pytest.raises(JevError, match="unasked_question"):
        ask("state", {"unasked_question": noul("x")}, fixture="quickstart")


def test_bug_priority_weights_normalised_scores():
    answers = ask("ticket", BUG_PRIORITY_QUESTIONS, fixture="bug_priority")
    # 0.6*(1.24/2) + 0.3*(1.28/2) + 0.1*(3/3)
    assert bug_priority(answers) == pytest.approx(0.664)


def test_low_confidence_department_goes_to_manual_triage(routing_answers):
    routing_answers["department"]["confidence"] = 0.1
    assert route_ticket(routing_answers).actions == ["send_to_manual_triage"]


def test_ambiguous_ticket_routes_to_returns_and_ccs_billing(routing_answers):
    decision = route_ticket(routing_answers)
    assert decision.team == "returns"
    assert decision.issue == "wrong_size"
    assert decision.cc_teams == ["billing"]
    assert decision.actions == ["ask_customer_what_they_want"]


def test_confident_refund_request_is_flagged(routing_answers):
    routing_answers["requested_resolution"]["confidence"] = 0.9
    assert "flag_for_refund_approval" in route_ticket(routing_answers).actions


def test_angry_tone_escalates_to_senior_agent(routing_answers):
    routing_answers["tone"]["choice"] = "angry"
    assert "flag_for_senior_agent" in route_ticket(routing_answers).actions


def test_routing_questions_match_fixture():
    assert set(ROUTING_QUESTIONS) == set(load_fixture("ambiguous_ticket")["answers"])
