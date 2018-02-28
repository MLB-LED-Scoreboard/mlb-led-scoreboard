import mlbgame
from datetime import datetime
import debug
import pytz
import tzlocal

class Pregame:
  def __init__(self, overview):
    self.home_team = overview.home_name_abbrev
    self.away_team = overview.away_name_abbrev
    self.start_time = self.__convert_time(overview.time + overview.ampm)

    try:
      self.away_starter = overview.away_probable_pitcher_last_name or 'TBD'
    except:
      self.away_starter = 'TBD'

    try:
      self.home_starter = overview.home_probable_pitcher_last_name or 'TBD'
    except:
      self.home_starter = 'TBD'
    debug.log(self)

  def __convert_time(self, time):
    eastern_tz = pytz.timezone('America/New_York')
    game_time_eastern = datetime.strptime(time, '%I:%M%p')
    now = datetime.now()
    game_time_eastern = game_time_eastern.replace(year=now.year, month=now.month, day=now.day, tzinfo=eastern_tz)
    return game_time_eastern.astimezone(tzlocal.get_localzone()).strftime('%I:%M%p').lstrip('0')

  def __str__(self):
    s =  "<%s %s> " % (self.__class__.__name__, hex(id(self)))
    s += "%s @ %s, (%s), %s vs %s" % (
      self.away_team, self.home_team, self.start_time,
      self.away_starter, self.home_starter)
    return s
