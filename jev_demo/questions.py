"""Builders for Jev's three question primitives.

Each builder returns the plain JSON dict the API expects, so you can see
exactly what goes over the wire.
"""

from collections.abc import Mapping, Sequence


def choice(instructions: str, criteria: Mapping[str, str | None]) -> dict:
    """Pick one option. `criteria` maps option id -> description (or None)."""
    return {"type": "choice", "instructions": instructions, "criteria": dict(criteria)}


def score(instructions: str, levels: Sequence[str]) -> dict:
    """Rate on an ordered scale. Level 0 is the lowest, len(levels)-1 the highest."""
    return {"type": "score", "instructions": instructions, "criteria": list(levels)}


def noul(instructions: str) -> dict:
    """Probability (0-1) that a statement about the state is true."""
    return {"type": "noul", "instructions": instructions}
