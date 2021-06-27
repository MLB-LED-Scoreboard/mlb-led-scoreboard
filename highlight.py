import json
import sys

TEAMS = {
    "Athletics",
    "Pirates",
    "Padres",
    "Mariners",
    "Giants",
    "Cardinals",
    "Rays",
    "Rangers",
    "Blue Jays",
    "Twins",
    "Phillies",
    "Braves",
    "White Sox",
    "Marlins",
    "Yankees",
    "Brewers",
    "Angels",
    "Diamondbacks",
    "Orioles",
    "Red Sox",
    "Cubs",
    "Reds",
    "Indians",
    "Rockies",
    "Tigers",
    "Astros",
    "Royals",
    "Dodgers",
    "Nationals",
    "Mets",
}

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Supply team name(s) or -l to list")
        sys.exit(1)
    else:
        if sys.argv[1] == "-l":
            for team in TEAMS:
                print(team)
        else:
            teams = sys.argv[1:]
            if any(t not in TEAMS for t in teams):
                print("Invalid team supplied!")
                sys.exit(1)
            with open("configs/config-default.json", "r") as default:
                config = json.load(default)
                config["preferred"]["teams"] = teams

                with open("config.json", "w") as f:
                    json.dump(config, f)
