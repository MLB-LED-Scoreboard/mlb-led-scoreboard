import debug
import time
import feedparser
from dates import Dates


HEADLINE_UPDATE_RATE = 60 * 60 # 1 hour between feed updates
HEADLINE_SPACER_SIZE = 10 # Number of spaces between headlines
HEADLINE_MAX_FEEDS = 3 # Number of preferred team's feeds to fetch
HEADLINE_MAX_ENTRIES = 7 # Number of headlines per feed

RSS_BASE = "http://mlb.mlb.com/partnerxml/gen/news/rss"
RSS_FEEDS = {
  "MLB": "mlb", "Angels": "ana", "Astros": "hou", "Athletics": "oak", "Blue Jays": "tor", "Indians": "cle",
  "Mariners": "sea", "Orioles": "bal", "Rangers": "tex", "Rays": "tb", "Red Sox": "bos", "Royals": "kc",
  "Tigers": "det", "Twins": "min", "White Sox": "chw", "Yankees": "nyy", "Braves": "atl", "Brewers": "mil",
  "Cardinals": "stl", "Cubs": "chc", "Diamondbacks": "ari", "D-Backs": "ari", "Dodgers": "la", "Giants": "sf",
  "Marlins": "mia", "Mets": "nym", "Nationals": "was", "Padres": "sd", "Phillies": "phi", "Pirates": "pit",
  "Reds": "cin", "Rockies": "col"
}

class Headlines:

  def __init__(self, preferred_teams, include_mlb, include_preferred, include_countdowns):
    self.preferred_teams = preferred_teams
    self.include_mlb = include_mlb
    self.include_preferred = include_preferred
    self.include_countdowns = include_countdowns
    self.feed_urls = []
    self.feed_data = None
    self.starttime = time.time()
    self.important_dates = Dates()

    self.__compile_feed_list()
    self.update(True)

  def update(self, force=False):
    if force == True or self.__should_update():
      debug.log("Headlines should update!")
      self.starttime = time.time()
      feeds = []
      debug.log("{} feeds to update...".format(len(self.feed_urls)))
      if len(self.feed_urls) > 0:
        debug.log("Feed URLs found...")
        for idx, url in enumerate(self.feed_urls):
          if idx < HEADLINE_MAX_FEEDS: # Only parse MAX teams to prevent potential hangs
            debug.log("Fetching {}".format(url))
            f = feedparser.parse(url)
            debug.log("Fetched feed '{}' with {} entries.".format(f.feed.title, len(f.entries)))
            feeds.append(f)
        self.feed_data = feeds

  def ticker_string(self, max_entries=HEADLINE_MAX_ENTRIES):
    ticker = ""
    if self.include_countdowns:
      countdown_string = self.important_dates.next_important_date_string()
      if countdown_string != "":
        ticker += countdown_string + (" " * HEADLINE_SPACER_SIZE)


    if self.feed_data != None:
      for feed in self.feed_data:
        ticker += self.__strings_for_feed(feed, max_entries)
    # In case all of the ticker options are turned off and there's no data, return a single space
    return " " if ticker == "" else ticker

  def available(self):
    return self.feed_data != None

  def __strings_for_feed(self, feed, max_entries):
    spaces = " " * HEADLINE_SPACER_SIZE
    title = feed.feed.title
    headlines = ""

    for idx, entry in enumerate(feed.entries):
      if idx < max_entries:
        headlines += entry.title + spaces
    return title + spaces + headlines

  def __compile_feed_list(self):
    if self.include_mlb:
      self.feed_urls.append(self.__url_for_team("MLB"))

    if self.include_preferred:
      if len(self.preferred_teams) > 0:
        for team in self.preferred_teams:
          self.feed_urls.append(self.__url_for_team(team))

  def __url_for_team(self, team_name):
    return "{}/{}.xml".format(RSS_BASE, RSS_FEEDS[team_name])

  def __should_update(self):
    endtime = time.time()
    time_delta = endtime - self.starttime
    return time_delta >= HEADLINE_UPDATE_RATE

