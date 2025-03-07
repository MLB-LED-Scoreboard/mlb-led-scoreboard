import debug


class Team:
    def __init__(self, abbrev, runs, name, hits, errors, record, special_uniform):
        self.abbrev = abbrev
        self.runs = runs
        self.name = name
        self.hits = hits
        self.errors = errors
        self.record = record
        self.special_uniform = special_uniform


    def lookup_color(self, team_colors):
        """
        Given a team color object, this returns the colors for the team.

        The result is guaranteed to have the 'home', 'accent', and 'text' keys.
        Any missing data is filled in with the default colors.
        If the team has a special uniform, the colors for that uniform are substuted
        """
        default_colors = team_colors.color("default")
        try:
            colors = team_colors.color(self.abbrev.lower())
            if self.special_uniform is not None and self.special_uniform in colors:
                colors |= colors[self.special_uniform]
            return default_colors | colors

        except KeyError:
            debug.exception("No color found for team: {}".format(self.abbrev))
            return default_colors
