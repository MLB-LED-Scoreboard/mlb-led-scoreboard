import requests
import re

class Standings:
    __URL = 'https://statsapi.mlb.com/api/v1/standings?season={year}&leagueId={league_ids}&date={month:0>2}/{day:0>2}/{year}&division=all'
    AL_LEAGUE_ID = '103'
    NL_LEAGUE_ID = '104'
    __LEAGUE_IDS = ','.join([AL_LEAGUE_ID, NL_LEAGUE_ID])

    @classmethod
    def fetch(cls, year, month, day):
        standings_data = requests.get(Standings.__URL.format(day=day, month=month, year=year, league_ids=Standings.__LEAGUE_IDS))

        if standings_data.status_code == 200:
            return Standings(standings_data.json())
        else:
            raise Exception('Could not fetch standings.')

    def __init__(self, data):
        self.__data = data
        self.divisions = self.__fetch_divisions()

    def __fetch_divisions(self):
        return [Division(division_data) for division_data in self.__data['records']]
        

class Division:
    def __init__(self, data):
        self.__data = data
        self.id = self.__data['division']['id']
        self.name = self.__name()
        self.teams = self.__teams()

    def __name(self):
        division_records = self.__data['teamRecords'][0]['records']['divisionRecords']
        full_name = [datum['division']['name'] for datum in division_records if datum['division']['id'] == self.id][0]
        
        # Use some regex to fix the division full name to what the config expects
        return re.sub(r'(ational|merican)\sLeague', 'L', full_name)

    def __teams(self):
        return [Team(team_data, self.id) for team_data in self.__data['teamRecords']]


class Team:
    __TEAM_NAMES = {
        'Arizona Diamondbacks': {'abbrev': 'ARI', 'short': 'Diamondbacks'},
        'Atlanta Braves': {'abbrev': 'ATL', 'short': 'Braves'},
        'Baltimore Orioles': {'abbrev': 'BAL', 'short': 'Orioles'},
        'Boston Red Sox': {'abbrev': 'BOS', 'short': 'Red Sox'},
        'Chicago Cubs': {'abbrev': 'CHC', 'short': 'Cubs'},
        'Chicago White Sox': {'abbrev': 'CHW', 'short': 'White Sox'},
        'Cincinnati Reds': {'abbrev': 'CIN', 'short': 'Reds'},
        'Cleveland Indians': {'abbrev': 'CLE', 'short': 'Indians'},
        'Colorado Rockies': {'abbrev': 'COL', 'short': 'Rockies'},
        'Detroit Tigers': {'abbrev': 'DET', 'short': 'Tigers'},
        'Florida Marlins': {'abbrev': 'FLA', 'short': 'Marlins'},
        'Houston Astros': {'abbrev': 'HOU', 'short': 'Astros'},
        'Kansas City Royals': {'abbrev': 'KAN', 'short': 'Royals'},
        'Los Angeles Angels': {'abbrev': 'LAA', 'short': 'Angels'},
        'Los Angeles Dodgers': {'abbrev': 'LAD', 'short': 'Dodgers'},
        'Miami Marlins': {'abbrev': 'MIA', 'short': 'Marlins'},
        'Milwaukee Brewers': {'abbrev': 'MIL', 'short': 'Brewers'},
        'Minnesota Twins': {'abbrev': 'MIN', 'short': 'Twins'},
        'New York Mets': {'abbrev': 'NYM', 'short': 'Mets'},
        'New York Yankees': {'abbrev': 'NYY', 'short': 'Yankees'},
        'Oakland Athletics': {'abbrev': 'OAK', 'short': 'Athletics'},
        'Philadelphia Phillies': {'abbrev': 'PHI', 'short': 'Phillies'},
        'Pittsburgh Pirates': {'abbrev': 'PIT', 'short': 'Pirates'},
        'San Diego Padres': {'abbrev': 'SD', 'short': 'Padres'},
        'San Francisco Giants': {'abbrev': 'SF', 'short': 'Giants'},
        'Seattle Mariners': {'abbrev': 'SEA', 'short': 'Mariners'},
        'St. Louis Cardinals': {'abbrev': 'STL', 'short': 'Cardinals'},
        'Tampa Bay Rays': {'abbrev': 'TB', 'short': 'Rays'},
        'Texas Rangers': {'abbrev': 'TEX', 'short': 'Rangers'},
        'Toronto Blue Jays': {'abbrev': 'TOR', 'short': 'Blue Jays'},
        'Washington Nationals': {'abbrev': 'WAS', 'short': 'Nationals'},
    }

    def __init__(self, data, division_id):
        self.__data = data
        self.name = self.__name()
        self.short_name = self.__TEAM_NAMES[self.name]["short"]
        self.team_abbrev = self.__TEAM_NAMES[self.name]["abbrev"]
        self.w = self.__parse_wins()
        self.l = self.__parse_losses()
        self.gb = self.__data['divisionGamesBack']

    def __name(self):
        return self.__data['team']['name']

    def __parse_wins(self):
        return self.__data['wins']

    def __parse_losses(self):
        return self.__data['losses']
