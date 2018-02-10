import json
import ledcolors.scoreboard
from rgbmatrix import graphics

class ScoreboardRenderer:
  def __init__(self, canvas, scoreboard):
    self.canvas = canvas
    self.scoreboard = scoreboard
    self.colors = json.load(open('Assets/colors.json'))

    self.font = graphics.Font()
    self.font.LoadFont('Assets/tom-thumb.bdf')

  def render(self):
    self.__render_team_colors()
    self.__render_team_text()
    self.__render_pitches()
    self.__render_outs()
    self.__render_bases()
    self.__render_inning()

  def __render_team_colors(self):
    away_team_color_data = self.colors[self.scoreboard.game_data['away_team'].lower()]
    away_team_color = away_team_color_data['home']

    home_team_color_data = self.colors[self.scoreboard.game_data['home_team'].lower()]
    home_team_color = home_team_color_data['home']

    scores_height = 14
    for x in range(self.canvas.width):
      for y in range(scores_height):
        color = home_team_color if y >= scores_height / 2 else away_team_color
        self.canvas.SetPixel(x, y, color['r'], color['g'], color['b'])

  def __render_team_text(self):
    away_team = self.scoreboard.game_data['away_team']
    away_text_color = self.colors[away_team.lower()].get('text', {'r': 255, 'g': 255, 'b': 255})
    away_text_color_graphic = graphics.Color(away_text_color['r'], away_text_color['g'], away_text_color['b'])
    away_text = '{:3s}'.format(away_team.upper()) + ' ' + str(self.scoreboard.game_data['inning']['at_bat']['away_team_runs'])

    home_team = self.scoreboard.game_data['home_team']
    home_text_color = self.colors[home_team.lower()].get('text', {'r': 255, 'g': 255, 'b': 255})
    home_text_color_graphic = graphics.Color(home_text_color['r'], home_text_color['g'], home_text_color['b'])
    home_text = '{:3s}'.format(home_team.upper()) + ' ' + str(self.scoreboard.game_data['inning']['at_bat']['home_team_runs'])

    graphics.DrawText(self.canvas, self.font, 1, 6, away_text_color_graphic, away_text)
    graphics.DrawText(self.canvas, self.font, 1, 13, home_text_color_graphic, home_text)

  def __render_pitches(self):
    at_bat = self.scoreboard.game_data['inning']['at_bat']
    pitches_color = graphics.Color(*ledcolors.scoreboard.text)
    graphics.DrawText(self.canvas, self.font, 1, 23, pitches_color, str(at_bat['balls']) + '-' + str(at_bat['strikes']))

  def __render_outs(self):
    outs = self.scoreboard.game_data['inning']['at_bat']['outs']
    out_px = []
    out_px.append({'x': 2, 'y': 27})
    out_px.append({'x': 6, 'y': 27})
    out_px.append({'x': 10, 'y': 27})
    for out in range(len(out_px)):
      self.__render_out_circle(out_px[out])
      # Fill in the circle if that out has occurred
      if (outs >= out):
        self.canvas.SetPixel(out_px[out]['x'], out_px[out]['y'], *ledcolors.scoreboard.text)

  def __render_bases(self):
    bases = self.scoreboard.game_data['inning']['at_bat']['bases']
    base_px = []
    base_px.append({'x': 26, 'y': 27} )
    base_px.append({'x': 21, 'y': 22} )
    base_px.append({'x': 16, 'y': 27} )

    for base in range(len(bases)):
      self.__render_base_outline(base_px[base])

      # Fill in the base if there's currently a baserunner
      if bases[base]:
        self.__render_baserunner(base_px[base])

  def __render_inning(self):
    inning = self.scoreboard.game_data['inning']
    self.__render_inning_half(inning)
    number = inning['number']
    number_color = graphics.Color(*ledcolors.scoreboard.text)
    pos_x = 28
    if number > 9:
      pos_x = 24
    graphics.DrawText(self.canvas, self.font, pos_x, 20, number_color, str(number))

  def __render_out_circle(self, out):
    offset = 1
    for x in range(-offset, offset + 1):
      for y in range(-offset, offset + 1):
        # The dead center is filled in only if that many outs has occurred, and happens elsewhere
        if x == 0 and y == 0:
          continue
        self.canvas.SetPixel(out['x'] + x, out['y'] + y, *ledcolors.scoreboard.text)

  def __render_base_outline(self, base):
    # Hollow diamonds are a popular homework problem but IDGAF
    self.canvas.SetPixel(base['x'] - 3, base['y'], *ledcolors.scoreboard.text)
    self.canvas.SetPixel(base['x'] - 2, base['y'] - 1, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(base['x'] - 2, base['y'] + 1, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(base['x'] - 1, base['y'] - 2, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(base['x'] - 1, base['y'] + 2, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(base['x'], base['y'] - 3, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(base['x'], base['y'] + 3, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(base['x'] + 1, base['y'] - 2, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(base['x'] + 1, base['y'] + 2, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(base['x'] + 2, base['y'] - 1, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(base['x'] + 2, base['y'] + 1, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(base['x'] + 3, base['y'], *ledcolors.scoreboard.text)

  def __render_baserunner(self, base):
    offset = 2
    for x in range(-offset, offset + 1):
      for y in range(-offset, offset + 1):
        if abs(x) == offset and abs(y) == offset:
          continue
        self.canvas.SetPixel(base['x'] + x, base['y'] + y, *ledcolors.scoreboard.text)

  def __render_inning_half(self, inning):
    tri_px = {'x': 24, 'y': 15}
    if inning['number'] > 9:
      tri_px['x'] = 20
    offset = 2
    for x in range(-offset, offset + 1):
      self.canvas.SetPixel(tri_px['x'] + x, tri_px['y'], *ledcolors.scoreboard.text)

    offset = 1 if inning['bottom'] else -1
    self.canvas.SetPixel(tri_px['x'] - 1, tri_px['y'] + offset, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(tri_px['x'], tri_px['y'] + offset, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(tri_px['x'] + 1, tri_px['y'] + offset, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(tri_px['x'], tri_px['y'] + offset + offset, *ledcolors.scoreboard.text)
