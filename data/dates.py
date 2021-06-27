from datetime import datetime, timedelta

import mlbgame

import debug

MLB_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


class Dates:
    def __init__(self):
        try:
            self.__parse_important_dates(self.__fetch_important_dates())
        except:
            debug.error("Failed to refresh important dates")
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

    def __parse_important_dates(self, dates):
        self.important_dates = []
        self.__add_date(dates.first_date_seas, "Opening Day {}".format(dates.year))
        self.__add_date(dates.last_date_1sth, "the {} All-Star Break".format(dates.year), 30)
        self.__add_date(dates.all_star_date, "the {} All-Star Game".format(dates.year))
        self.__add_date(dates.last_date_seas, "the final day of the regular season", 30)
        self.__add_date(dates.playoffs_start_date, "the {} Post-Season begins".format(dates.year))
        self.__add_date(dates.playoffs_end_date, "the {} Post-Season ends".format(dates.year))

    def __add_date(self, date, text, max_days_to_count=999):
        if date != "":
            self.important_dates.append(
                {"text": text, "date": datetime.strptime(date, MLB_DATE_FORMAT), "max_days": max_days_to_count}
            )

    def __fetch_important_dates(self):
        today = datetime.today()
        dates = mlbgame.important_dates()

        if dates.playoffs_end_date != "":
            season_end_date = datetime.strptime(dates.playoffs_end_date, MLB_DATE_FORMAT)
            if (season_end_date - today).days < 0:
                dates = mlbgame.important_dates(today.year + 1)

        return dates
