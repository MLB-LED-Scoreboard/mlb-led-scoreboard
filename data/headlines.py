import debug
import time
import feedparser
from dates import Dates

try:
  from HTMLParser import HTMLParser
except ImportError:
  from html.parser import HTMLParser


HEADLINE_UPDATE_RATE = 60 * 60 # 1 hour between feed updates
HEADLINE_SPACER_SIZE = 10 # Number of spaces between headlines
HEADLINE_MAX_FEEDS = 3 # Number of preferred team's feeds to fetch
HEADLINE_MAX_ENTRIES = 7 # Number of headlines per feed

MLB_BASE = "http://mlb.mlb.com/partnerxml/gen/news/rss"
MLB_FEEDS = {
  "MLB": "mlb", "Angels": "ana", "Astros": "hou", "Athletics": "oak", "Blue Jays": "tor", "Indians": "cle",
  "Mariners": "sea", "Orioles": "bal", "Rangers": "tex", "Rays": "tb", "Red Sox": "bos", "Royals": "kc",
  "Tigers": "det", "Twins": "min", "White Sox": "chw", "Yankees": "nyy", "Braves": "atl", "Brewers": "mil",
  "Cardinals": "stl", "Cubs": "chc", "Diamondbacks": "ari", "D-Backs": "ari", "Dodgers": "la", "Giants": "sf",
  "Marlins": "mia", "Mets": "nym", "Nationals": "was", "Padres": "sd", "Phillies": "phi", "Pirates": "pit",
  "Reds": "cin", "Rockies": "col"
}

TRADE_BASE = "https://www.mlbtraderumors.com"
TRADE_PATH = "feed/atom"
TRADE_FEEDS = {
  "Angels": "los-angeles-angels-of-anaheim",
  "Astros": "houston-astros",
  "Athletics": "oakland-athletics",
  "Blue Jays": "toronto-blue-jays",
  "Indians": "cleveland-indians",
  "Mariners": "seattle-mariners",
  "Orioles": "baltimore-orioles",
  "Rangers": "texas-rangers",
  "Rays": "tampa-bay-devil-rays",
  "Red Sox": "boston-red-sox",
  "Royals": "kansas-city-royals",
  "Tigers": "detroit-tigers",
  "Twins": "minnesota-twins",
  "White Sox": "chicago-white-sox",
  "Yankees": "new-york-yankees",
  "Braves": "atlanta-braves",
  "Brewers": "milwaukee-brewers",
  "Cardinals": "st-louis-cardinals",
  "Cubs": "chicago-cubs",
  "Diamondbacks": "arizona-diamondbacks",
  "D-Backs": "arizona-diamondbacks",
  "Dodgers": "los-angeles-dodgers",
  "Giants": "san-francisco-giants",
  "Marlins": "florida-marlins",
  "Mets": "new-york-mets",
  "Nationals": "washington-nationals",
  "Padres": "san-diego-padres",
  "Phillies": "philadelphia-phillies",
  "Pirates": "pittsburgh-pirates",
  "Reds": "cincinnati-reds",
  "Rockies": "colorado-rockies"
}

class Headlines:

  def __init__(self, config):
    self.preferred_teams = config.preferred_teams
    self.include_mlb = config.news_ticker_mlb_news
    self.include_preferred = config.news_ticker_preferred_teams
    self.include_traderumors = config.news_ticker_traderumors
    self.include_countdowns = config.news_ticker_countdowns
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
      feedparser.USER_AGENT = "mlb-led-scoreboard/3.0 +https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard"
      if len(self.feed_urls) > 0:
        debug.log("Feed URLs found...")
        for idx, url in enumerate(self.feed_urls):
          if idx < HEADLINE_MAX_FEEDS: # Only parse MAX teams to prevent potential hangs
            debug.log("Fetching {}".format(url))
            f = feedparser.parse(url)
            try:
              title = f.feed.title.encode("ascii", "ignore")
              debug.log("Fetched feed '{}' with {} entries.".format(title, len(f.entries)))
              feeds.append(f)
            except AttributeError:
              debug.warning("There was a problem fetching {}".format(url))
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
    title = feed.feed.title.encode("ascii", "ignore")
    headlines = ""

    for idx, entry in enumerate(feed.entries):
      if idx < max_entries:
        h = HTMLParser()
        text = h.unescape(entry.title.encode("ascii", "ignore"))
        headlines += text + spaces
    return title + spaces + headlines

  def __compile_feed_list(self):
    if self.include_mlb:
      self.feed_urls.append(self.__mlb_url_for_team("MLB"))

    if self.include_preferred:
      if len(self.preferred_teams) > 0:
        for team in self.preferred_teams:
          self.feed_urls.append(self.__mlb_url_for_team(team))

    if self.include_traderumors:
      if len(self.preferred_teams) > 0:
        for team in self.preferred_teams:
          self.feed_urls.append(self.__traderumors_url_for_team(team))

  def __mlb_url_for_team(self, team_name):
    return "{}/{}.xml".format(MLB_BASE, MLB_FEEDS[team_name])

  def __traderumors_url_for_team(self, team_name):
    return "{}/{}/{}".format(TRADE_BASE, TRADE_FEEDS[team_name], TRADE_PATH)

  def __should_update(self):
    endtime = time.time()
    time_delta = endtime - self.starttime
    return time_delta >= HEADLINE_UPDATE_RATE

