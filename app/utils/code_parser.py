import re
from dataclasses import dataclass
from typing import Literal

from app.services.errors import BadRequestError

TeamLetter = Literal["H", "G"]
TeamSide = Literal["home", "away"]
Skill = Literal["S", "R", "P", "A", "B", "D"]
EvalMark = Literal["+", "-", "#"]

# --- Dataclasses (API parsera) ------------------------------------------------


@dataclass(frozen=True)
class Zone:
    zone: str  # "1".."9"
    sub: str  # "A".."I"


@dataclass(frozen=True)
class ActionToken:
    raw: str
    team_letter: TeamLetter  # H/G
    team: TeamSide  # home/away (zmapowane)
    player_jersey: int  # 1..99
    skill: Skill  # S/R/P/A/B/D
    eval: EvalMark  # + / - / #
    start: Zone | None  # None dla S, opcjonalne dla innych
    end: Zone  # wymagane dla wszystkich poza błędnym S
    modifiers: list[str]  # ["XF", "E", ...]

    # pomocniczo
    index: int  # kolejność w rally (0..)


@dataclass(frozen=True)
class PostAnnotation:
    raw: str


@dataclass(frozen=True)
class ParsedRally:
    actions: list[ActionToken]
    terminal_index: int  # index akcji kończącej (pierwsze # lub -)
    terminal_eval: Literal["#", "-"]
    post_annotations: list[PostAnnotation]
    comment: str | None  # treść w % ... % lub None


# --- Błędy i kody błędów ------------------------------------------------------


def parse_error(
    message: str, code: str, details: dict | None = None
) -> BadRequestError:
    return BadRequestError(message, code=code, details=details)


# --- Tokenizacja --------------------------------------------------------------

# 1 akcja – dopuszczamy brak start zony (dla S zabronimy osobno)
TOKEN_RE = re.compile(
    r"""
    ^(?P<team>[HG])
     (?P<player>\d{1,2})
     (?P<skill>[SRPABD])
     (?P<eval>[+\-#])
     (?:
        (?P<startZone>[1-9])(?P<startSub>[A-I])
     )?
     (?P<endZone>[1-9])(?P<endSub>[A-I])
     (?P<mods>(?:XF|XT|XH|E|F)*)$
    """,
    re.VERBOSE,
)

COMMENT_RE = re.compile(r"%(.+?)%")

# post-annot po terminalu: dopuszczamy np. "B-6C", "B-" itp. (bez # i bez E)
POST_ANNOT_RE = re.compile(
    r"^(?:(?P<team>[HG])(?P<player>\d{1,2}))?B-(?:(?P<endZone>[1-9])(?P<endSub>[A-I]))?(?P<mods>(?:XF|XT|XH|F)*)$"
)

MOD_SPLIT_RE = re.compile(r"(XF|XT|XH|E|F)")


def map_team(letter: TeamLetter) -> TeamSide:
    return "home" if letter == "H" else "away"


# --- Parser główny ------------------------------------------------------------


def parse_rally(code: str) -> ParsedRally:
    """
    Parsuje pełny string rally (ciąg akcji + ewentualny komentarz w %...%).
    Zwraca ParsedRally, gotowe do dalszej walidacji domenowej (jersey→player,
    rotacje, set_state) w serwisie live/match-flow.

    Reguły:
    - terminal to PIERWSZE # albo -, licząc po akcjach;
    - po terminalu dopuszczamy post-annotacje (negatywne blokowe) – bez zmiany wyniku;
    - S: brak start zony; R/P/A/D/B: end zona wymagana; start opcjonalna.
    """
    raw = code.strip()
    comment_match = COMMENT_RE.search(raw)
    comment = comment_match.group(1).strip() if comment_match else None
    main = COMMENT_RE.sub("", raw).strip()

    # Tokeny oddzielamy białymi znakami
    tokens = [t for t in re.split(r"\s+", main) if t]

    actions: list[ActionToken] = []
    post_annotations: list[PostAnnotation] = []
    terminal_index: int | None = None
    terminal_eval: Literal["#", "-"] | None = None

    # Faza 1: parsuj akcje, do momentu aż trafisz na pierwszy terminal (# lub -)
    for idx, tok in enumerate(tokens):
        m = TOKEN_RE.match(tok)
        if not m:
            # jeśli nie wygląda jak akcja, to albo post-annot (po terminalu), albo błąd
            if terminal_index is not None:
                if POST_ANNOT_RE.match(tok):
                    post_annotations.append(PostAnnotation(raw=tok))
                    continue
                raise parse_error(
                    f"Invalid post-annotation token: '{tok}'",
                    code="INVALID_POST_ANNOTATION",
                    details={"token": tok},
                )
            else:
                # jeszcze nie było terminala, więc to musi być akcja → błąd
                raise parse_error(
                    f"Invalid action token: '{tok}'",
                    code="INVALID_TOKEN_SEQUENCE",
                    details={"token": tok},
                )

        # rozbij akcję
        gd = m.groupdict()
        team_letter: TeamLetter = gd["team"]  # type: ignore
        team = map_team(team_letter)
        player_jersey = int(gd["player"])
        skill: Skill = gd["skill"]  # type: ignore
        ev: EvalMark = gd["eval"]  # type: ignore

        start = None
        if gd["startZone"] and gd["startSub"]:
            start = Zone(gd["startZone"], gd["startSub"])

        end = Zone(gd["endZone"], gd["endSub"])

        mods_raw = gd["mods"] or ""
        mods = [m for m in MOD_SPLIT_RE.findall(mods_raw) if m]

        # Walidacje per skill:
        if skill == "S":
            # zagrywka: start zabroniony
            if start is not None:
                raise parse_error(
                    "Serve (S) cannot have a start zone.",
                    code="SERVE_START_FORBIDDEN",
                    details={"token": tok},
                )
        else:
            # dla R/P/A/D/B end musi być zawsze
            if end is None:
                # praktycznie nie trafi, bo regex wymaga end, ale defensywnie:
                raise parse_error(
                    "Action must have an end zone.",
                    code="END_ZONE_REQUIRED",
                    details={"token": tok},
                )

        action = ActionToken(
            raw=tok,
            team_letter=team_letter,
            team=team,
            player_jersey=player_jersey,
            skill=skill,
            eval=ev,
            start=start,
            end=end,
            modifiers=mods,
            index=len(actions),
        )
        actions.append(action)

        # wykryj terminal (# lub -)
        if terminal_index is None and ev in ("#", "-"):
            terminal_index = len(actions) - 1
            terminal_eval = ev  # type: ignore

            # od teraz kolejne tokeny mogą być tylko post-annotacjami
            # (petla nie przerywana – zbieramy post-annot dalej)
            continue

    if not actions:
        raise parse_error("Empty rally.", code="EMPTY_RALLY")

    if terminal_index is None or terminal_eval is None:
        raise parse_error(
            "Rally must contain at least one terminal (# or -).",
            code="NO_TERMINAL_FOUND",
        )

    # Faza 2: wszystko PO terminalu musi być post-annot (już zebrane w pętli)
    # Dodatkowa walidacja: w post-annot nie wolno mieć '#' ani 'E'
    for pa in post_annotations:
        pm = POST_ANNOT_RE.match(pa.raw)
        assert pm, "post annotation must match or byłby rzucony wyżej"
        mods_raw = pm.group("mods") or ""
        if "E" in mods_raw:
            raise parse_error(
                "Modifier 'E' is not allowed in post-annotations.",
                code="POST_ANNOT_E_FORBIDDEN",
                details={"token": pa.raw},
            )
        # brak '#' gwarantuje sam regex

    return ParsedRally(
        actions=actions,
        terminal_index=terminal_index,
        terminal_eval=terminal_eval,
        post_annotations=post_annotations,
        comment=comment,
    )


class CodeParser:
    """
    Lightweight wrapper class – docelowo trzyma EBNF/regexy,
    parse() zwraca strukturę pośrednią dla Rally/Action.
    """

    @staticmethod
    def parse(rally_code: str) -> ParsedRally:
        return parse_rally(rally_code)
