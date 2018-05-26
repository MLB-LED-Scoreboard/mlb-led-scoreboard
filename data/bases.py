class Bases:
  def __init__(self, overview):
    b1 = None
    b2 = None
    b3 = None

    try:
      b1 = overview.runner_on_1b
    except AttributeError:
      pass

    try:
      b2 = overview.runner_on_2b
    except AttributeError:
      pass

    try:
      b3 = overview.runner_on_3b
    except AttributeError:
      pass
    self.runners = [b1, b2, b3]

  def __str__(self):
    rs = []
    for r in self.runners:
      rs.append("X" if r else " ")
    return "[{}][{}][{}]".format(rs[0],rs[1],rs[2])
