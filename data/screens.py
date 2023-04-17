from enum import Enum


class ScreenType(Enum):
    """Kinds of screen we render"""

    ALWAYS_NEWS = "news"
    ALWAYS_STANDINGS = "standings"
    LEAGUE_OFFDAY = "league_offday"  # complete offday, implies at least news, possibly also standings
    PREFERRED_TEAM_OFFDAY = (
        "preferred_team_offday"  # offday only for preferred team AND news/standings are enabled for team offdays
    )
    GAMEDAY = "gameday"  # games are being played today. May also show standings and news if games aren't live
