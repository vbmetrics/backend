from typing import NamedTuple


class ParsedAction(NamedTuple):
    team_context: str
    skill_code: str
    evaluation_code: str
    start_zone: int | None
    end_zone: int | None
    start_subzone: str | None
    end_subzone: str | None
    modifiers: str | None
    player_jersey_number: int | None

class CodeParser(NamedTuple):
    def parse(self, raw: str) -> ParsedAction:
        # parse & validate; raise ValueError on invalid format
        return
