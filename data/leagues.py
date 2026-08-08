from dataclasses import dataclass
from typing import Literal, Protocol, Any

import statsapi
import wpbl_statsapi_adaptor


class StatAPI(Protocol):
    def schedule(self, date, **kwargs: str) -> dict[str, Any]: ...

    def get(
        self,
        endpoint: Literal["game", "game_content", "schedule", "game_uniforms"],
        params: dict[str, str | int] = {},
        force: bool = False,
        *,
        request_kwargs: dict[str, Any] = {}
    ) -> dict[str, Any]: ...


@dataclass
class League:
    name: str
    statsapi: StatAPI
    schedule_params: dict[str, str]


LEAGUES = {
    "MLB": League(
        name="MLB",
        statsapi=statsapi,
        schedule_params=dict(sportId="1", leagueId="103,104"),
    ),
    "WBC": League(
        name="WBC",
        statsapi=statsapi,
        schedule_params=dict(sportId="51", leagueIds="159,160"),
    ),
    "WPBL": League(
        name="WPBL",
        statsapi=wpbl_statsapi_adaptor,  # type: ignore
        schedule_params=dict(sportId="bsb"),
    ),
}
