import re

from app.models.special_event import SpecialEventType
from app.services.errors import BadRequestError


class SpecialEventParser:
    """
    Mini parser for special event raw codes.
    Expected compact tokens, examples:

      - "TO-H"             => timeout (home)
      - "TO-A"             => timeout (away)
      - "SUB-A:12>7"       => substitution (away: player 12 out, 7 in)
      - "CARD-H:Y"         => card (home: yellow)
      - "CARD-A:R"         => card (away: red)
      - "CH-H"             => challenge by home
      - "OTHER:NOTE"       => other event with free text note
    """

    # Regex patterns for known event types
    _TIMEOUT_RE = re.compile(r"^TO-(H|A)$")
    _SUB_RE = re.compile(r"^SUB-(H|A):(\d{1,2})>(\d{1,2})$")
    _CARD_RE = re.compile(r"^CARD-(H|A):([YyRr])$")
    _CHALLENGE_RE = re.compile(r"^CH-(H|A)$")
    _OTHER_RE = re.compile(r"^OTHER:(.+)$")

    def parse(self, raw_code: str) -> tuple[SpecialEventType, dict]:
        if not raw_code or not raw_code.strip():
            raise BadRequestError(
                "Empty special event code",
                code="EMPTY_SPECIAL_EVENT_CODE",
                details={},
            )
        code = raw_code.strip()

        # Timeout
        m = self._TIMEOUT_RE.match(code)
        if m:
            team = m.group(1)
            return SpecialEventType.timeout, {"team": team}

        # Substitution
        m = self._SUB_RE.match(code)
        if m:
            team, out_num, in_num = m.groups()
            return SpecialEventType.substitution, {
                "team": team,
                "player_out": int(out_num),
                "player_in": int(in_num),
            }

        # Card
        m = self._CARD_RE.match(code)
        if m:
            team, color = m.groups()
            color = "yellow" if color.upper() == "Y" else "red"
            return SpecialEventType.card, {"team": team, "color": color}

        # Challenge
        m = self._CHALLENGE_RE.match(code)
        if m:
            team = m.group(1)
            return SpecialEventType.challenge, {"team": team}

        # Other
        m = self._OTHER_RE.match(code)
        if m:
            return SpecialEventType.other, {"note": m.group(1).strip()}

        raise BadRequestError(
            "Unknown special event code format",
            code="INVALID_SPECIAL_EVENT_CODE",
            details={"raw": raw_code},
        )
