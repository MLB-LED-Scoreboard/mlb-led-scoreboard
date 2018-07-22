class Inning:

  TOP = 'Top'
  BOTTOM = 'Bottom'
  MIDDLE = 'Middle'
  END = 'End'
  ORDINAL = ['0', '1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th', '11th', '12th', '13th', '14th', '15th', '16th', '17th', '18th', '19th', '20th', '21st', '22nd', '23rd', '24th', '25th', '26th', '27th', '28th', '29th', '30th']

  @staticmethod
  def is_break(inning_state):
    return inning_state not in [Inning.TOP, Inning.BOTTOM]

  def __init__(self, overview):
    self.number = overview.inning
    self.state = overview.inning_state

  def ordinal(self):
    return Inning.ORDINAL[self.number]
