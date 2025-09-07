import re
from dataclasses import dataclass
from typing import Optional

from app.services.errors import BadRequestError

# Contstants
TEAM_VALUES = {"H", "G"}  # Home, Away
SKILL_VALUES = {
    "S",
    "R",
    "P",
    "A",
    "B",
    "D",
}  # Serve, Receive, Pass, Attack, Block, Dig
EVAL_VALUES = {"+", "-", "#"}  # Positive, Negative, Perfect
SUBZONE_VALUES = set("ABCDEFGHI")


@dataclass(frozen=True)
class ParsedAction:
    team_context: str
    skill_code: str
    evaluation_code: str
    start_zone: Optional[int]
    start_subzone: Optional[str]
    end_zone: Optional[int]
    end_subzone: Optional[str]
    player_jersey_number: int
    modifiers: list[str]
    raw_action_code: str

    def to_action_create_dict(
        self, *, rally_id, player_id: Optional[str] = None
    ) -> dict:
        """
        Returns a dict suitable for ActionCreate model.
        """
        return {
            "sequence_in_rally": 0,  # fill at service layer
            "raw_action_code": self.raw_action_code,
            "team_context": self.team_context,
            "skill_code": self.skill_code,
            "evaluation_code": self.evaluation_code,
            "start_zone": self.start_zone,
            "start_subzone": self.start_subzone,
            "end_zone": self.end_zone,
            "end_subzone": self.end_subzone,
            "player_jersey_number": self.player_jersey_number,
            "modifiers": "".join(self.modifiers) if self.modifiers else None,
            "rally_id": rally_id,
            "player_id": player_id,
        }


@dataclass(frozen=True)
class ParsedRally:
    actions: list[ParsedAction]
    comment: Optional[str]


class CodeParser:
    """
    Parser for volleyball action codes.

    Grammar (compact):
        ACTION := TEAM PLAYER SKILL EVAL
                    START_ZONE START_SUBZONE END_ZONE END_SUBZONE MODIFIERS?
        TEAM   := 'H' | 'G'
        PLAYER := '0'..'99'
        SKILL  := 'S' | 'R' | 'P' | 'A' | 'B' | 'D'
        EVAL   := '+' | '-' | '#'
        START_ZONE := '1'..'9'
        START_SUBZONE := 'A'..'I'
        END_ZONE := '1'..'9'
        END_SUBZONE := 'A'..'I'
        MODIFIERS := (one or more contiguous tokens), e.g. 'F', 'XT', 'XF'
                     We parse trailing uppercase/digit chunks as a list:
                     ['F'], ['XF'], ['F','XT'], etc.

    Rally format:
        "< ACTION_1 > < ACTION_2 > ... < ACTION_N >% optional comment"
        - Angle brackets are required around each action.
        - Arbitrary whitespace inside <> is ignored.
        - Comment begins with '%' and runs to end of line/string (optional).
    """

    _ACTION_RE = re.compile(
        r"([HG])"  # Team
        r"(\d{2})"  # Player jersey number
        r"([SRPABD])"  # Skill
        r"([+#-])"  # Eval
        r"([1-9])"  # Start zone
        r"([A-I])"  # Start subzone
        r"([1-9])"  # End zone
        r"([A-I])"  # End subzone
        r"([A-Z0-9]*?)(?=(?:[HG]\d{2}[SRPABD][+#-])|$)",  # MODIFIERS + lookahead
        flags=re.ASCII,
    )

    _MOD_TOKEN_RE = re.compile(r"[A-Z][A-Z0-9]*", flags=re.ASCII)

    def parse_rally(self, text: str) -> ParsedRally:
        if not text or not text.strip():
            raise BadRequestError(
                "Empty rally string",
                code="EMPTY_RALLY",
                details={},
            )

        body, comment = self._split_comment(text)
        compact = re.sub(r"\s+", "", body)  # remove all whitespace
        if not compact:
            raise BadRequestError(
                "No actions found",
                code="NO_ACTIONS_IN_RALLY",
                details={},
            )

        matches = list(self._ACTION_RE.finditer(compact))
        if not matches:
            raise BadRequestError(
                "Failed to parse action sequence",
                code="ACTION_PARSE_ERROR",
                details={},
            )

        cursor = 0
        for m in matches:
            if m.start() != cursor:
                context = compact[
                    max(0, cursor - 5) : min(len(compact), m.start() + 10)
                ]
                raise BadRequestError(
                    "Unexpected characters between actions",
                    code="GAP_IN_RALLY",
                    details={"position": cursor, "context": context},
                )
            cursor = m.end()
        if cursor != len(compact):
            context = compact[cursor : min(len(compact), cursor + 10)]
            raise BadRequestError(
                "Trailing garbage after last action",
                code="TRAILING_GARBAGE",
                details={"position": cursor, "context": context},
            )

        actions: list[ParsedAction] = []
        for m in matches:
            team, player_str, skill, eval_, sz, ssub, ez, esub, mods_raw = m.groups()
            self._validate_team(team, compact, m.start())
            player = self._validate_player(player_str, compact, m.start())
            self._validate_skill(skill, compact, m.start())
            self._validate_eval(eval_, compact, m.start())
            start_zone = self._validate_zone(sz, "start_zone", compact, m.start())
            end_zone = self._validate_zone(ez, "end_zone", compact, m.start())
            start_subzone = self._validate_subzone(
                ssub, "start_subzone", compact, m.start()
            )
            end_subzone = self._validate_subzone(
                esub, "end_subzone", compact, m.start()
            )
            modifiers = self._parse_modifiers(mods_raw)

            raw_token = compact[m.start() : m.end()]
            actions.append(
                ParsedAction(
                    team_context=team,
                    player_jersey_number=player,
                    skill_code=skill,
                    evaluation_code=eval_,
                    start_zone=start_zone,
                    start_subzone=start_subzone,
                    end_zone=end_zone,
                    end_subzone=end_subzone,
                    modifiers=modifiers,
                    raw_action_code=raw_token,
                )
            )

        return ParsedRally(actions=actions, comment=comment)

    def parse_action(self, token: str) -> ParsedAction:
        compact = re.sub(r"\s+", "", token)
        m = self._ACTION_RE.fullmatch(compact)
        if not m:
            raise BadRequestError(
                "Invalid action code format",
                code="INVALID_ACTION",
                details={"token": token},
            )

        team, player_str, skill, eval_, sz, ssub, ez, esub, mods_raw = m.groups()

        self._validate_team(team, compact, 0)
        player = self._validate_player(player_str, compact, 0)
        self._validate_skill(skill, compact, 0)
        self._validate_eval(eval_, compact, 0)
        start_zone = self._validate_zone(sz, "start_zone", compact, 0)
        end_zone = self._validate_zone(ez, "end_zone", compact, 0)
        start_subzone = self._validate_subzone(ssub, "start_subzone", compact, 0)
        end_subzone = self._validate_subzone(esub, "end_subzone", compact, 0)
        modifiers = self._parse_modifiers(mods_raw)

        return ParsedAction(
            team_context=team,
            player_jersey_number=player,
            skill_code=skill,
            evaluation_code=eval_,
            start_zone=start_zone,
            start_subzone=start_subzone,
            end_zone=end_zone,
            end_subzone=end_subzone,
            modifiers=modifiers,
            raw_action_code=compact,
        )

    # HELPERS

    @staticmethod
    def _split_comment(text: str) -> tuple[str, Optional[str]]:
        if "%" not in text:
            return text, None
        head, _, tail = text.partition("%")
        return head, (tail.strip() or None)

    @staticmethod
    def _validate_team(team: str, src: str, pos: int) -> None:
        if team not in TEAM_VALUES:
            raise BadRequestError(
                "Invalid team code identifier, expected 'H' or 'G'",
                code="INVALID_TEAM",
                details={"value": team, "position": pos},
            )

    @staticmethod
    def _validate_player(player_str: str, src: str, pos: int) -> int:
        if not player_str.isdigit():
            raise BadRequestError(
                "Player number must be two digits (00-99)",
                code="INVALID_PLAYER_FORMAT",
                details={"value": player_str, "position": pos},
            )
        val = int(player_str)
        if not (0 <= val <= 99):
            raise BadRequestError(
                "Player number out of range (0-99)",
                code="PLAYER_OUT_OF_RANGE",
                details={"value": val, "position": pos},
            )
        return val

    @staticmethod
    def _validate_skill(skill: str, src: str, pos: int) -> None:
        if skill not in SKILL_VALUES:
            raise BadRequestError(
                "Invalid skill code",
                code="INVALID_SKILL",
                details={
                    "value": skill,
                    "position": pos,
                    "allowed": sorted(SKILL_VALUES),
                },
            )

    @staticmethod
    def _validate_eval(eval_: str, src: str, pos: int) -> None:
        if eval_ not in EVAL_VALUES:
            raise BadRequestError(
                "Invalid evaluation code",
                code="INVALID_EVAL",
                details={
                    "value": eval_,
                    "position": pos,
                    "allowed": sorted(EVAL_VALUES),
                },
            )

    @staticmethod
    def _validate_zone(zone_char: str, field: str, src: str, pos: int) -> int:
        if zone_char not in "123456789":
            raise BadRequestError(
                "Zone must be a digit between 1 and 9",
                code="INVALID_ZONE",
                details={"field": field, "value": zone_char, "position": pos},
            )
        return int(zone_char)

    @staticmethod
    def _validate_subzone(subzone_char: str, field: str, src: str, pos: int) -> str:
        if subzone_char not in SUBZONE_VALUES:
            raise BadRequestError(
                "Subzone must be a letter between A and I",
                code="INVALID_SUBZONE",
                details={"field": field, "value": subzone_char, "position": pos},
            )
        return subzone_char

    def _parse_modifiers(self, tail: str) -> list[str]:
        if not tail:
            return []
        if not re.fullmatch(r"[A-Z0-9]+", tail):
            raise BadRequestError(
                "Invalid modifiers format, expected A-Z and 0-9 characters only",
                code="INVALID_MODIFIERS",
                details={"value": tail},
            )
        return self._MOD_TOKEN_RE.findall(tail)
