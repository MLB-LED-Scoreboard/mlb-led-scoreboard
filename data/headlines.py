import debug
import time
import feedparser
from datetime import datetime
from data.dates import Dates

try:
  from HTMLParser import HTMLParser
except ImportError:
  from html.parser import HTMLParser


HEADLINE_UPDATE_RATE = 60 * 60 # 1 hour between feed updates
HEADLINE_SPACER_SIZE = 10 # Number of spaces between headlines
HEADLINE_MAX_FEEDS = 3 # Number of preferred team's feeds to fetch
HEADLINE_MAX_ENTRIES = 7 # Number of headlines per feed
FALLBACK_DATE_FORMAT = "%A, %B %-d"


MLB_BASE = "https://www.mlb.com"
MLB_PATH = "feeds/news/rss.xml"
MLB_FEEDS = {
  "MLB": "", "Angels": "angels", "Astros": "astros", "Athletics": "athletics", "Blue Jays": "bluejays", 
  "Indians": "indians", "Mariners": "mariners", "Orioles": "orioles", "Rangers": "rangers", "Rays": "rays", 
  "Red Sox": "redsox", "Royals": "royals", "Tigers": "tigers", "Twins": "twins", "White Sox": "whitesox", 
  "Yankees": "yankees", "Braves": "braves", "Brewers": "brewers", "Cardinals": "cardinals", "Cubs": "cubs", 
  "Diamondbacks": "dbacks", "D-Backs": "dbacks", "Dodgers": "dodgers", "Giants": "giants", "Marlins": "marlins", 
  "Mets": "mets", "Nationals": "nationals", "Padres": "padres", "Phillies": "phillies", "Pirates": "pirates",
  "Reds": "reds", "Rockies": "rockies"
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
    self.include_date = config.news_ticker_date
    self.date_format = config.news_ticker_date_format
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
    if self.include_date:
      date_string = datetime.now().strftime(self.date_format)
      ticker = self.__add_string_to_ticker(ticker, date_string)

    if self.include_countdowns:
      countdown_string = self.important_dates.next_important_date_string()

      # If we get None back from this method, we don't have an important date coming soon
      if countdown_string is not None:
        ticker = self.__add_string_to_ticker(ticker, countdown_string)

    if self.feed_data != None:
      ticker = self.__add_string_to_ticker(ticker, "")
      for feed in self.feed_data:
        ticker += self.__strings_for_feed(feed, max_entries)

    # In case all of the ticker options are turned off and there's no data, return the date
    return datetime.now().strftime(FALLBACK_DATE_FORMAT) if len(ticker) < 1 else ticker

  def __add_string_to_ticker(self, ticker, text_to_add):
    t = ticker
    if len(t) > 0:
      t += (" " * HEADLINE_SPACER_SIZE)
    return (t + text_to_add)

  def available(self):
    return self.feed_data != None

  def __strings_for_feed(self, feed, max_entries):
    spaces = " " * HEADLINE_SPACER_SIZE
    title = feed.feed.title
    headlines = ""

    for idx, entry in enumerate(feed.entries):
      if idx < max_entries:
        h = HTMLParser()
        text = h.unescape(entry.title)
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
    return "{}/{}/{}".format(MLB_BASE, MLB_FEEDS[team_name], MLB_PATH)

  def __traderumors_url_for_team(self, team_name):
    return "{}/{}/{}".format(TRADE_BASE, TRADE_FEEDS[team_name], TRADE_PATH)

  def __should_update(self):
    endtime = time.time()
    time_delta = endtime - self.starttime
    return time_delta >= HEADLINE_UPDATE_RATE

