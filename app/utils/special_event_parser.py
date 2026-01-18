from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.services.errors import BadRequestError

SpecialNeutral = Literal["T", "C", "S"]  # timeout, card, substitution
SpecialPenal = Literal["F", "RC"]  # fault, red-card (modelujemy jako skrót)


@dataclass(frozen=True)
class SpecialEvent:
    raw: str
    kind: Literal["T", "C", "S", "F", "RC"]
    payload: str | None = None  # np. "yellow", "green", "player=H6>H10", itp.


def parse_special(token: str) -> SpecialEvent:
    """
    Do wywołania, gdy token zaczyna się od '!'
    (np. '!T', '!C=yellow', '!F-', '!S=H6>H10', '!RC').
    Zwraca obiekt neutralny (=) lub karny (-).
    """
    if not token.startswith("!"):
        raise BadRequestError("Not a special token.", code="NOT_SPECIAL")

    body = token[1:]  # bez '!'
    # dopuszczamy warianty: T, C=..., S=..., F-, RC (red card)
    if body == "T":
        return SpecialEvent(raw=token, kind="T")

    if body.startswith("C="):
        return SpecialEvent(raw=token, kind="C", payload=body[2:])

    if body.startswith("S="):
        return SpecialEvent(raw=token, kind="S", payload=body[2:])

    if body == "F-":
        return SpecialEvent(raw=token, kind="F")  # karny punkt dla rywala

    if body == "RC":
        return SpecialEvent(raw=token, kind="RC")  # karny punkt dla rywala

    raise BadRequestError(
        "Unknown special token.", code="UNKNOWN_SPECIAL", details={"token": token}
    )


class SpecialEventParser:
    @staticmethod
    def parse(token: str) -> SpecialEvent:
        return parse_special(token)
