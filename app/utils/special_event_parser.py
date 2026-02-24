import re
from dataclasses import dataclass
from typing import Literal

from app.services.errors import BadRequestError

TeamCode = Literal["H", "G", "R"]  # Home, Guest, Referee
EventType = Literal["F", "T", "S", "C", "N"]  # Fault, Timeout, Sub, Card, iNjury
EvalMark = Literal["+", "-", "="]

# Wyciąganie komentarza między %%
COMMENT_RE = re.compile(r"%(.+?)%")

# Baza parsera zdarzeń specjalnych
# np. !H00S=09.23, !R00C-H14R, !G12N=
SPECIAL_RE = re.compile(
    r"""
    ^!
    (?P<team>[HGR])              # H, G lub R
    (?P<player>\d{1,2})          # 00 lub nr zawodnika (np. 14, 25)
    (?P<type>[FTSCN])            # Typ zdarzenia
    (?P<eval>[+\-=])             # Wpływ zdarzenia (+, -, =)
    (?P<payload>[a-zA-Z0-9.]+)?  # Opcjonalny cel/modyfikator (np. H14Y, 09.23, G25)
    $
    """,
    re.VERBOSE,
)


@dataclass(frozen=True)
class ParsedSpecialEvent:
    raw: str
    team: TeamCode
    player_jersey: int
    event_type: EventType
    evaluation: EvalMark
    target: str | None           # Cel (np. "09.23", "H14", "G25")
    modifier: str | None         # Modyfikator dla kartek (np. "Y", "R", "G")
    comment: str | None          # Treść między %%
    is_penal: bool               # True, jeśli eval to "-", co oznacza stratę/karny


def parse_special(raw_token: str) -> ParsedSpecialEvent:
    """
    Parsuje token zdarzenia specjalnego.
    Zwraca ustrukturyzowany obiekt ParsedSpecialEvent.
    """
    if not raw_token.startswith("!"):
        raise BadRequestError("Not a special token.", code="NOT_SPECIAL")

    # 1. Wyciągnij i oczyść komentarz (jeśli istnieje)
    comment_match = COMMENT_RE.search(raw_token)
    comment = comment_match.group(1).strip() if comment_match else None

    # 2. Usuń komentarz z tokena bazowego, żeby regex nie zwariował
    main_token = COMMENT_RE.sub("", raw_token).strip()

    # 3. Przepuść przez główny regex
    m = SPECIAL_RE.match(main_token)
    if not m:
        raise BadRequestError(
            f"Invalid special event format: '{main_token}'",
            code="INVALID_SPECIAL_FORMAT",
            details={"token": raw_token}
        )

    gd = m.groupdict()
    team: TeamCode = gd["team"]  # type: ignore
    player_jersey = int(gd["player"])
    event_type: EventType = gd["type"]  # type: ignore
    evaluation: EvalMark = gd["eval"]  # type: ignore
    payload = gd["payload"] or None

    target = None
    modifier = None

    # 4. Sprytne przetwarzanie payloadu w zależności od typu zdarzenia
    if payload:
        if event_type == "C":
            # W przypadku Kartek (Card), na końcu payloadu często jest kolor (Y/R/G)
            if payload[-1].upper() in ("Y", "R", "G"):
                modifier = payload[-1].upper()
                # Zostawiamy w target samego zawodnika, obcinając modyfikator
                target = payload[:-1] if len(payload) > 1 else None
            else:
                target = payload
        elif event_type == "S":
            # Zmiany (Sub) - przekazujemy wprost układ (np. "09.23")
            target = payload
        else:
            # Dla Fault/Injury payload to zazwyczaj zawodnik przeciwnika (np. "G25")
            target = payload

    # 5. Ustalenie wpływu punktowego
    # W Twoich przykładach ewaluacja "-" wprost skutkuje stratą punktu rywala.
    is_penal = (evaluation == "-")

    return ParsedSpecialEvent(
        raw=raw_token,
        team=team,
        player_jersey=player_jersey,
        event_type=event_type,
        evaluation=evaluation,
        target=target,
        modifier=modifier,
        comment=comment,
        is_penal=is_penal
    )


class SpecialEventParser:
    """
    Wrapper do wykorzystania w innych serwisach.
    """
    @staticmethod
    def parse(token: str) -> ParsedSpecialEvent:
        return parse_special(token)
