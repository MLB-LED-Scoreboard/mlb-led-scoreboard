import mlbgame
from datetime import datetime
import debug
import pytz
import tzlocal

class Pregame:
  def __init__(self, overview, time_format):
    self.home_team = overview.home_name_abbrev
    self.away_team = overview.away_name_abbrev
    self.time_format = time_format

    try:
      self.start_time = self.__convert_time(overview.time + overview.ampm)
    except:
      self.start_time = "TBD"

    self.status = overview.status

    try:
      self.away_starter = ("{}. {} ({}-{} {} ERA)".format(
        overview.away_probable_pitcher_first_name[0],
        overview.away_probable_pitcher_last_name,
        overview.away_probable_pitcher_wins,
        overview.away_probable_pitcher_losses,
        self.__convert_era(overview.away_probable_pitcher_era))
      ) or 'TBD'
    except:
      self.away_starter = 'TBD'

    try:
      self.home_starter = ("{}. {} ({}-{} {} ERA)".format(
        overview.home_probable_pitcher_first_name[0],
        overview.home_probable_pitcher_last_name,
        overview.home_probable_pitcher_wins,
        overview.home_probable_pitcher_losses,
        self.__convert_era(overview.home_probable_pitcher_era))
      ) or 'TBD'
    except:
      self.home_starter = 'TBD'

  def __convert_era(self, era_string):
    if era_string == "-.--":
      return "-.--"
    return "{0:.2f}".format(era_string)

  def __convert_time(self, time):
    """Converts MLB's pregame times (Eastern) into the local time zone"""
    time_str = "{}:%M".format(self.time_format)
    if self.time_format == "%-I":
      time_str += "%p"

    game_time_eastern = datetime.strptime(time, '%I:%M%p')
    now = datetime.now()
    game_time_eastern = game_time_eastern.replace(year=now.year, month=now.month, day=now.day)
    eastern_tz = pytz.timezone('America/New_York')
    game_time_eastern = eastern_tz.localize(game_time_eastern)
    return game_time_eastern.astimezone(tzlocal.get_localzone()).strftime(time_str)

  def __str__(self):
    s = "<{} {}> {} @ {}; {}; {} vs {}".format(
      self.__class__.__name__, hex(id(self)),
      self.away_team, self.home_team, self.start_time,
      self.away_starter, self.home_starter)
    return s
