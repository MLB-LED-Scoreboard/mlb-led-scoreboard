from inning import Inning

class Status:
  CANCELLED = 'Cancelled'
  COMPLETED_EARLY = 'Completed Early'
  COMPLETED_EARLY_RAIN = 'Completed Early: Rain'
  DELAYED = 'Delayed'
  DELAYED_START = 'Delayed Start'
  FINAL = 'Final'
  GAME_OVER = 'Game Over'
  IN_PROGRESS = 'In Progress'
  MANAGER_CHALLENGE = 'Manager Challenge'
  REVIEW = 'Review'
  PRE_GAME = 'Pre-Game'
  POSTPONED = 'Postponed'
  SCHEDULED = 'Scheduled'
  SUSPENDED = 'Suspended'
  TIED = 'Final: Tied'
  GAME_OVER_TIED = 'Game Over: Tied'
  WARMUP = 'Warmup'

  @staticmethod
  def is_static(status):
    """Returns whether the game being currently displayed has no text to scroll"""
    return status in [Status.IN_PROGRESS, Status.CANCELLED, Status.DELAYED, Status.DELAYED_START, Status.POSTPONED, Status.SUSPENDED, Status.MANAGER_CHALLENGE, Status.REVIEW]

  @staticmethod
  def is_pregame(status):
    """Returns whether the game is in a pregame state"""
    return status in [Status.PRE_GAME, Status.SCHEDULED, Status.WARMUP]

  @staticmethod
  def is_complete(status):
    """Returns whether the game has been completed"""
    return status in [Status.FINAL, Status.GAME_OVER, Status.COMPLETED_EARLY, Status.COMPLETED_EARLY_RAIN, Status.TIED]

  @staticmethod
  def is_live(status):
    """Returns whether the game is currently live"""
    return status in [Status.IN_PROGRESS, Status.WARMUP, Status.GAME_OVER, Status.MANAGER_CHALLENGE]

  @staticmethod
  def is_irregular(status):
    """Returns whether game is in an irregular state, such as delayed, postponed, cancelled,
    or in a challenge."""
    return status in [Status.POSTPONED, Status.SUSPENDED, Status.DELAYED, Status.DELAYED_START, Status.CANCELLED, Status.MANAGER_CHALLENGE, Status.REVIEW]

  @staticmethod
  def is_fresh(status):
    """Returns whether the game is in progress or is very recently complete. Game Over
    comes between In Progress and Final and allows a few minutes to see the final outcome before
    the rotation kicks in."""
    return status in [Status.IN_PROGRESS, Status.GAME_OVER, Status.GAME_OVER_TIED]

  @staticmethod
  def is_inning_break(inning_state):
    """Returns whether a game is in an inning break (mid/end). Pass in the inning state."""
    return inning_state not in [Inning.TOP, Inning.BOTTOM]
