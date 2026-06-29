from dataclasses import dataclass


@dataclass
class League:
    name: str
    sportId: int
    leagueIds: list[int]


LEAGUES = {
    "MLB": League(name="MLB", sportId=1, leagueIds=[103, 104]),
    "WBC": League(name="WBC", sportId=51, leagueIds=[159, 160]),
}
