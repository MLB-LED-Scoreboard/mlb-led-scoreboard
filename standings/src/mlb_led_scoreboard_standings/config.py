import bullpen


DEFAULT_PREFERRED_DIVISIONS = ["NL Central"]


class Config(bullpen.Config):
    def __init__(self, config) -> None:
        self.preferred_divisions = config.for_plugin("standings").get("divisions", DEFAULT_PREFERRED_DIVISIONS)
        self.parse_today = config.parse_today
        self.check_preferred_divisions()

    def check_preferred_divisions(self):
        if not isinstance(self.preferred_divisions, str) and not isinstance(self.preferred_divisions, list):
            bullpen.LOGGER.warning(
                "preferred_divisions should be an array of division names or a single division name string."
                "Using default preferred_divisions, {}".format(DEFAULT_PREFERRED_DIVISIONS)
            )
            self.preferred_divisions = DEFAULT_PREFERRED_DIVISIONS
        if isinstance(self.preferred_divisions, str):
            division = self.preferred_divisions
            self.preferred_divisions = [division]
