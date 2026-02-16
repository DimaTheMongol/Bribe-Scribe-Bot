from dataclasses import dataclass

@dataclass
class Fixture:
    fixture_id: int
    round: int
    home_team: str
    away_team: str
    status: str