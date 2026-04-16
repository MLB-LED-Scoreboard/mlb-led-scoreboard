from datetime import datetime, timedelta, date

import statsapi

from bullpen.logging import LOGGER


class Dates:
    def __init__(self, dates, today: date):
        self.today = today
        year = today.year
        try:
            data_d = statsapi.get("season", {"sportId": 1, "seasonId": year})
            end_date = self.__parse_important_dates(data_d["seasons"][0], year)
            now = datetime.now()
            if year == now.year and end_date < now:
                data_d = statsapi.get("season", {"sportId": 1, "seasonId": year + 1})
                self.__parse_important_dates(data_d["seasons"][0], year + 1)
        except:
            LOGGER.exception("Failed to refresh important dates")
            self.important_dates = [{"text": "None", "date": datetime(3000, 1, 1), "max_days": 1}]
        try:
            for date in dates:
                d = date["date"]
                if d.count("-") == 1:
                    d = f"{year}-{d}"
                self.__add_date(d, date["text"], date.get("max_days", 365))
        except:
            LOGGER.exception("Failed to parse important dates from config")

        LOGGER.debug("Important dates: %s", self.important_dates)

    def next_important_date_string(self):
        date = self.next_important_date()
        days = (date["date"] - self.today).days
        if days < date["max_days"]:
            plural = "s" if days > 1 else ""
            return f"{days} day{plural} until {date['text']}!"

    def next_important_date(self):
        return min(
            self.important_dates,
            key=lambda date: date["date"] - self.today if (date["date"] - self.today).days > 0 else timedelta.max,
        )

    def __parse_important_dates(self, dates, year):
        self.important_dates = []
        self.__add_date(dates["regularSeasonStartDate"], "Opening Day {}".format(year))
        self.__add_date(dates["lastDate1stHalf"], "the {} All-Star Break".format(year), 30)
        self.__add_date(dates["allStarDate"], "the {} All-Star Game".format(year))
        self.__add_date(dates["regularSeasonEndDate"], "the final day of the regular season", 30)
        self.__add_date(dates["postSeasonStartDate"], "the {} Post-Season begins".format(year))
        self.__add_date(dates["postSeasonEndDate"], "the {} Post-Season ends".format(year))
        return datetime.strptime(dates["postSeasonEndDate"], "%Y-%m-%d")

    def __add_date(self, date, text, max_days_to_count=999):
        if date and text:
            self.important_dates.append(
                {"text": text, "date": datetime.strptime(date, "%Y-%m-%d").date(), "max_days": max_days_to_count}
            )
