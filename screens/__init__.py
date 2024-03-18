from screens.news import NewsScreen
from screens.standings import *

import Bullpen

class ScreenRotator:

    def __init__(self, matrix, data):
        self.matrix = matrix
        self.data = data
        self.canvas = matrix.CreateFrameCanvas()

        self.generate_rotations()
        self.manager = Bullpen.Manager(entrypoint=self.entrypoint)

    @property
    def entrypoint(self):
        return self.screens[0]
    
    def start(self):
        self.manager.perform()

    def generate_rotations(self):
        # ****************
        # * SCREEN SETUP *
        # ****************

        # NEWS
        news                 = NewsScreen(self.matrix, self.canvas, self.data)

        # NL DIVISION STANDINGS
        nl_central_standings = DivisionStandingsScreen(self.matrix, self.canvas, self.data, division="NL Central")
        nl_west_standings    = DivisionStandingsScreen(self.matrix, self.canvas, self.data, division="NL West")
        nl_east_standings    = DivisionStandingsScreen(self.matrix, self.canvas, self.data, division="NL East")

        # AL DIVISION STANDINGS
        al_central_standings = DivisionStandingsScreen(self.matrix, self.canvas, self.data, division="AL Central")
        al_west_standings    = DivisionStandingsScreen(self.matrix, self.canvas, self.data, division="AL West")
        al_east_standings    = DivisionStandingsScreen(self.matrix, self.canvas, self.data, division="AL East")

        self.screens = [
            news,
            nl_central_standings,
            nl_west_standings,
            nl_east_standings,
            nl_central_standings,
            nl_west_standings,
            nl_east_standings
        ]

        # ********************
        # * Transition SETUP *
        # ********************

        # NEWS
        news.add_transitions(
            Bullpen.Transition(to=nl_central_standings, on=Bullpen.Condition.Timer(10))
        )

        # NL DIVISION STANDINGS
        nl_central_standings.add_transitions(
            Bullpen.Transition(to=nl_east_standings, on=Bullpen.Condition.Timer(10))
        )
        nl_east_standings.add_transitions(
            Bullpen.Transition(to=nl_west_standings, on=Bullpen.Condition.Timer(10))
        )
        nl_west_standings.add_transitions(
            Bullpen.Transition(to=al_central_standings, on=Bullpen.Condition.Timer(10))
        )

        # AL DIVISION STANDINGS
        al_central_standings.add_transitions(
            Bullpen.Transition(to=al_east_standings, on=Bullpen.Condition.Timer(10))
        )
        al_east_standings.add_transitions(
            Bullpen.Transition(to=al_west_standings, on=Bullpen.Condition.Timer(10))
        )
        al_west_standings.add_transitions(
            Bullpen.Transition(to=news, on=Bullpen.Condition.Timer(10))
        )
