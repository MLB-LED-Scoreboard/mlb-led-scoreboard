from datetime import datetime, timedelta

import statsapi

import debug


class Dates:
    def __init__(self, year: int):
        try:
            data = statsapi.get("season", {"sportId": 1, "seasonId": year})
            self.__parse_important_dates(data["seasons"][0], year)
            now = datetime.now()
            if year == now.year and self.season_ends_date < now:
                data = statsapi.get("season", {"sportId": 1, "seasonId": year + 1})
                self.__parse_important_dates(data["seasons"][0], year + 1)
        except:
            debug.exception("Failed to refresh important dates")
            self.playoffs_start_date = datetime(3000, 10, 1)
            self.important_dates = [{"text": "None", "date": datetime(3000, 1, 1), "max_days": 1}]

    def next_important_date_string(self):
        today = datetime.today()
        date = self.next_important_date()
        days = (date["date"] - today).days
        if days < date["max_days"]:
            return "{} days until {}!".format(days, date["text"])

    def next_important_date(self):
        today = datetime.today()
        return min(
            self.important_dates,
            key=lambda date: date["date"] - today if (date["date"] - today).days > 0 else timedelta.max,
        )

    def __parse_important_dates(self, dates, year):
        self.important_dates = []
        self.__add_date(dates["regularSeasonStartDate"], "Opening Day {}".format(year))
        self.__add_date(dates["lastDate1stHalf"], "the {} All-Star Break".format(year), 30)
        self.__add_date(dates["allStarDate"], "the {} All-Star Game".format(year))
        self.__add_date(dates["regularSeasonEndDate"], "the final day of the regular season", 30)
        self.playoffs_start_date = datetime.strptime(dates["regularSeasonEndDate"], "%Y-%m-%d")
        self.__add_date(dates["postSeasonStartDate"], "the {} Post-Season begins".format(year))
        self.season_ends_date = datetime.strptime(dates["postSeasonEndDate"], "%Y-%m-%d")
        self.__add_date(dates["postSeasonEndDate"], "the {} Post-Season ends".format(year))

    def __add_date(self, date, text, max_days_to_count=999):
        if date != "":
            self.important_dates.append(
                {"text": text, "date": datetime.strptime(date, "%Y-%m-%d"), "max_days": max_days_to_count}
            )
