"""Support-ticket triage built on Jev answers.

The pattern: Jev answers small, atomic questions with calibrated probabilities.
Plain Python turns those answers into a decision. Changing a business rule
means changing a constant here, not rewriting a prompt.
"""

from dataclasses import dataclass, field

from jev_demo.questions import choice, score

SEVERITY_WEIGHT = 0.6
FRUSTRATION_WEIGHT = 0.3
REPORT_QUALITY_WEIGHT = 0.1

MANUAL_TRIAGE_BELOW = 0.3  # department confidence too low to auto-route
ASK_CUSTOMER_BELOW = 0.5  # unclear what the customer actually wants
CC_TEAM_ABOVE = 0.25  # a runner-up team with this much probability gets a copy

BUG_PRIORITY_QUESTIONS = {
    "severity": score(
        "How severe is the reported issue?",
        [
            "Cosmetic; no impact to functionality",
            "Broken or degraded feature, but workaround exists",
            "Blocking issue; no workaround exists",
        ],
    ),
    "frustration": score(
        "How frustrated is the customer?",
        [
            "Calm, just stating facts",
            "Frustrated but civil",
            "Very angry, strong language or threatening to leave",
        ],
    ),
    "report_quality": score(
        "How much does the report give an engineer to work with?",
        [
            "No detail; just says something is broken",
            "Names the feature but no steps or environment",
            "Steps to reproduce or environment, but not both",
            "Steps to reproduce and environment",
        ],
    ),
}

ROUTING_QUESTIONS = {
    "department": choice(
        "Which team should handle this?",
        {
            "returns": "Exchanges, wrong or damaged items",
            "shipping": "Delivery status, delays, lost packages",
            "billing": "Charges, invoices, payment problems",
        },
    ),
    "return_reason": choice(
        "If the customer wants to return something, why?",
        {
            "wrong_size": "The item doesn't fit",
            "wrong_item": "A different product was delivered",
            "damaged": "The item arrived broken or faulty",
            "changed_mind": "The item is fine, the customer no longer wants it",
            "other": "A return reason that fits none of the above",
        },
    ),
    "shipping_issue": choice(
        "If this is a shipping problem, which kind is it?",
        {
            "not_delivered": "The package never arrived",
            "delayed": "The package is late but still on its way",
            "wrong_address": "The package went to the wrong place",
            "damaged_in_transit": "The package arrived damaged",
            "other": "A shipping problem that fits none of the above",
        },
    ),
    "requested_resolution": choice(
        "What does the customer want to happen?",
        {
            "exchange": "Swap the item for a different one",
            "refund": "Money back",
            "replacement": "The same item sent again",
            "information": "Just an answer, no action needed",
        },
    ),
    "tone": choice("What is the customer's tone?", {"calm": None, "frustrated": None, "angry": None}),
}


def normalized_score(answers: dict, question_id: str, questions: dict) -> float:
    """Map a score from 0..top_level onto 0..1."""
    top_level = len(questions[question_id]["criteria"]) - 1
    return answers[question_id]["score"] / top_level


def bug_priority(answers: dict) -> float:
    """Weighted 0-1 priority from three independent Score answers."""

    def part(question_id: str) -> float:
        return normalized_score(answers, question_id, BUG_PRIORITY_QUESTIONS)

    return (
        SEVERITY_WEIGHT * part("severity")
        + FRUSTRATION_WEIGHT * part("frustration")
        + REPORT_QUALITY_WEIGHT * part("report_quality")
    )


@dataclass
class RoutingDecision:
    team: str | None
    issue: str | None = None
    cc_teams: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)


def route_ticket(answers: dict) -> RoutingDecision:
    """Turn Choice answers + their confidence into a routing decision."""
    department = answers["department"]
    if department["confidence"] < MANUAL_TRIAGE_BELOW:
        return RoutingDecision(team=None, actions=["send_to_manual_triage"])

    team = department["choice"]
    issue_question = {"returns": "return_reason", "shipping": "shipping_issue"}.get(team)
    decision = RoutingDecision(
        team=team,
        issue=answers[issue_question]["choice"] if issue_question else None,
        cc_teams=[
            other
            for other, probability in department["probabilities"].items()
            if other != team and probability > CC_TEAM_ABOVE
        ],
    )

    resolution = answers["requested_resolution"]
    if resolution["confidence"] < ASK_CUSTOMER_BELOW:
        decision.actions.append("ask_customer_what_they_want")
    elif resolution["choice"] == "refund":
        decision.actions.append("flag_for_refund_approval")

    if answers["tone"]["choice"] == "angry":
        decision.actions.append("flag_for_senior_agent")
    return decision
