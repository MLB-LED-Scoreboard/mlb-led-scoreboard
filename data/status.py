from data.scoreboard.inning import Inning

"""This will/should eventually download/read the actual json where
the status data comes from. https://statsapi.mlb.com/api/v1/gameStatus"""

CANCELLED = "Cancelled"  # Final
CANCELLED_COLD = "Cancelled: Cold"  # Final
CANCELLED_DARKNESS = "Cancelled: Darkness"  # Final
CANCELLED_EMERGENCY = "Cancelled: Emergency"  # Final
CANCELLED_FOG = "Cancelled: Fog"  # Final
CANCELLED_INCLEMENT_WEATHER = "Cancelled: Inclement Weather"  # Final
CANCELLED_LIGHTNING = "Cancelled: Lightning"  # Final
CANCELLED_POWER = "Cancelled: Power"  # Final
CANCELLED_RAIN = "Cancelled: Rain"  # Final
CANCELLED_SNOW = "Cancelled: Snow"  # Final
CANCELLED_TRAGEDY = "Cancelled: Tragedy"  # Final
CANCELLED_VENUE = "Cancelled: Venue"  # Final
CANCELLED_WET_GROUNDS = "Cancelled: Wet Grounds"  # Final
CANCELLED_WIND = "Cancelled: Wind"  # Final
COMPLETED_EARLY = "Completed Early"  # Final
COMPLETED_EARLY_COLD = "Completed Early: Cold"  # Final
COMPLETED_EARLY_DARKNESS = "Completed Early: Darkness"  # Final
COMPLETED_EARLY_EMERGENCY = "Completed Early: Emergency"  # Final
COMPLETED_EARLY_FOG = "Completed Early: Fog"  # Final
COMPLETED_EARLY_INCLEMENT_WEATHER = "Completed Early: Inclement Weather"  # Final
COMPLETED_EARLY_LIGHTNING = "Completed Early: Lightning"  # Final
COMPLETED_EARLY_MERCY_RULE = "Completed Early: Mercy Rule"  # Final
COMPLETED_EARLY_POWER = "Completed Early: Power"  # Final
COMPLETED_EARLY_RAIN = "Completed Early: Rain"  # Final
COMPLETED_EARLY_SNOW = "Completed Early: Snow"  # Final
COMPLETED_EARLY_TRAGEDY = "Completed Early: Tragedy"  # Final
COMPLETED_EARLY_VENUE = "Completed Early: Venue"  # Final
COMPLETED_EARLY_WET_GROUNDS = "Completed Early: Wet Grounds"  # Final
COMPLETED_EARLY_WIND = "Completed Early: Wind"  # Final
DELAYED = "Delayed"  # Live
DELAYED_ABOUT_TO_RESUME = "Delayed: About to Resume"  # Live
DELAYED_CEREMONY = "Delayed: Ceremony"  # Live
DELAYED_COLD = "Delayed: Cold"  # Live
DELAYED_DARKNESS = "Delayed: Darkness"  # Live
DELAYED_EMERGENCY = "Delayed: Emergency"  # Live
DELAYED_FOG = "Delayed: Fog"  # Live
DELAYED_INCLEMENT_WEATHER = "Delayed: Inclement Weather"  # Live
DELAYED_LIGHTNING = "Delayed: Lightning"  # Live
DELAYED_POWER = "Delayed: Power"  # Live
DELAYED_RAIN = "Delayed: Rain"  # Live
DELAYED_SNOW = "Delayed: Snow"  # Live
DELAYED_START = "Delayed Start"  # Preview
DELAYED_START_CEREMONY = "Delayed Start: Ceremony"  # Preview
DELAYED_START_COLD = "Delayed Start: Cold"  # Preview
DELAYED_START_DARKNESS = "Delayed Start: Darkness"  # Preview
DELAYED_START_EMERGENCY = "Delayed Start: Emergency"  # Preview
DELAYED_START_FOG = "Delayed Start: Fog"  # Preview
DELAYED_START_INCLEMENT_WEATHER = "Delayed Start: Inclement Weather"  # Preview
DELAYED_START_LIGHTNING = "Delayed Start: Lightning"  # Preview
DELAYED_START_POWER = "Delayed Start: Power"  # Preview
DELAYED_START_RAIN = "Delayed Start: Rain"  # Preview
DELAYED_START_SNOW = "Delayed Start: Snow"  # Preview
DELAYED_START_TRAGEDY = "Delayed Start: Tragedy"  # Preview
DELAYED_START_VENUE = "Delayed Start: Venue"  # Preview
DELAYED_START_WET_GROUNDS = "Delayed Start: Wet Grounds"  # Preview
DELAYED_START_WIND = "Delayed Start: Wind"  # Preview
DELAYED_TRAGEDY = "Delayed: Tragedy"  # Live
DELAYED_VENUE = "Delayed: Venue"  # Live
DELAYED_WET_GROUNDS = "Delayed: Wet Grounds"  # Live
DELAYED_WIND = "Delayed: Wind"  # Live
FINAL = "Final"  # Final
FINAL_TIED = "Final: Tied"  # Final
FINAL_TIE_DECISION_BY_TIEBREAKER = "Final: Tie, decision by tiebreaker"  # Final
FORFEIT = "Forfeit"  # Final
FORFEIT_DELAY_OF_GAME = "Forfeit: Delay of game"  # Final
FORFEIT_FAILURE_TO_APPEAR = "Forfeit: Failure to appear"  # Final
FORFEIT_FAILURE_TO_FIELD_LINEUP = "Forfeit: Failure to field lineup"  # Final
FORFEIT_FINAL = "Forfeit: Final"  # Final
FORFEIT_GAME_OVER = "Forfeit: Game Over"  # Final
FORFEIT_IGNORING_EJECTION = "Forfeit: Ignoring ejection"  # Final
FORFEIT_INELIGIBLE_PLAYER = "Forfeit: Ineligible player"  # Final
FORFEIT_REFUSES_TO_PLAY = "Forfeit: Refuses to play"  # Final
FORFEIT_UNPLAYABLE_FIELD = "Forfeit: Unplayable field"  # Final
FORFEIT_WILLFUL_RULE_VIOLATION = "Forfeit: Willful rule violation"  # Final
GAME_OVER = "Game Over"  # Final
GAME_OVER_TIED = "Game Over: Tied"  # Final
GAME_OVER_TIE_DECISION_BY_TIEBREAKER = "Game Over: Tie, decision by tiebreaker"  # Final
IN_PROGRESS = "In Progress"  # Live
INSTANT_REPLAY = "Instant Replay"  # Live
MANAGER_CHALLENGE = "Manager challenge"  # Live
MANAGER_CHALLENGE_CATCHDROP_IN_OUTFIELD = "Manager challenge: Catch/drop in outfield"  # Live
MANAGER_CHALLENGE_CLOSE_PLAY_AT_1ST = "Manager challenge: Close play at 1st"  # Live
MANAGER_CHALLENGE_FAIRFOUL_IN_OUTFIELD = "Manager challenge: Fair/foul in outfield"  # Live
MANAGER_CHALLENGE_FAN_INTERFERENCE = "Manager challenge: Fan interference"  # Live
MANAGER_CHALLENGE_FORCE_PLAY = "Manager challenge: Force play"  # Live
MANAGER_CHALLENGE_GROUNDS_RULE = "Manager challenge: Grounds rule"  # Live
MANAGER_CHALLENGE_HIT_BY_PITCH = "Manager challenge: Hit by pitch"  # Live
MANAGER_CHALLENGE_HOME_RUN = "Manager challenge: Home run"  # Live
MANAGER_CHALLENGE_HOMEPLATE_COLLISION = "Manager challenge: Home-plate collision"  # Live
MANAGER_CHALLENGE_MULTIPLE_ISSUES = "Manager challenge: Multiple issues"  # Live
MANAGER_CHALLENGE_PASSING_RUNNERS = "Manager challenge: Passing runners"  # Live
MANAGER_CHALLENGE_RECORD_KEEPING = "Manager challenge: Record keeping"  # Live
MANAGER_CHALLENGE_RULES_CHECK = "Manager challenge: Rules check"  # Live
MANAGER_CHALLENGE_SLIDE_INTERFERENCE = "Manager challenge: Slide interference"  # Live
MANAGER_CHALLENGE_STADIUM_BOUNDARY_CALL = "Manager challenge: Stadium boundary call"  # Live
MANAGER_CHALLENGE_TAG_PLAY = "Manager challenge: Tag play"  # Live
MANAGER_CHALLENGE_TAGUP_PLAY = "Manager challenge: Tag-up play"  # Live
MANAGER_CHALLENGE_TIMING_PLAY = "Manager challenge: Timing play"  # Live
MANAGER_CHALLENGE_TOUCHING_A_BASE = "Manager challenge: Touching a base"  # Live
MANAGER_CHALLENGE_TRAP_PLAY_IN_OUTFIELD = "Manager challenge: Trap play in outfield"  # Live
POSTPONED = "Postponed"  # Final
POSTPONED_COLD = "Postponed: Cold"  # Final
POSTPONED_DARKNESS = "Postponed: Darkness"  # Final
POSTPONED_EMERGENCY = "Postponed: Emergency"  # Final
POSTPONED_FOG = "Postponed: Fog"  # Final
POSTPONED_INCLEMENT_WEATHER = "Postponed: Inclement Weather"  # Final
POSTPONED_LIGHTNING = "Postponed: Lightning"  # Final
POSTPONED_POWER = "Postponed: Power"  # Final
POSTPONED_RAIN = "Postponed: Rain"  # Final
POSTPONED_SNOW = "Postponed: Snow"  # Final
POSTPONED_TRAGEDY = "Postponed: Tragedy"  # Final
POSTPONED_VENUE = "Postponed: Venue"  # Final
POSTPONED_WET_GROUNDS = "Postponed: Wet Grounds"  # Final
POSTPONED_WIND = "Postponed: Wind"  # Final
PREGAME = "Pre-Game"  # Preview
SCHEDULED = "Scheduled"  # Preview
SUSPENDED = "Suspended"  # Live
SUSPENDED_ABOUT_TO_RESUME = "Suspended: About to Resume"  # Live
SUSPENDED_APPEAL_UPHELD = "Suspended: Appeal Upheld"  # Live
SUSPENDED_COLD = "Suspended: Cold"  # Live
SUSPENDED_DARKNESS = "Suspended: Darkness"  # Live
SUSPENDED_EMERGENCY = "Suspended: Emergency"  # Live
SUSPENDED_FOG = "Suspended: Fog"  # Live
SUSPENDED_INCLEMENT_WEATHER = "Suspended: Inclement Weather"  # Live
SUSPENDED_LIGHTNING = "Suspended: Lightning"  # Live
SUSPENDED_POWER = "Suspended: Power"  # Live
SUSPENDED_RAIN = "Suspended: Rain"  # Live
SUSPENDED_SNOW = "Suspended: Snow"  # Live
SUSPENDED_TRAGEDY = "Suspended: Tragedy"  # Live
SUSPENDED_VENUE = "Suspended: Venue"  # Live
SUSPENDED_WET_GROUNDS = "Suspended: Wet Grounds"  # Live
SUSPENDED_WIND = "Suspended: Wind"  # Live
UMPIRE_REVIEW = "Umpire review"  # Live
UMPIRE_REVIEW_CATCHDROP_IN_OUTFIELD = "Umpire review: Catch/drop in outfield"  # Live
UMPIRE_REVIEW_CLOSE_PLAY_AT_1ST = "Umpire review: Close play at 1st"  # Live
UMPIRE_REVIEW_FAIRFOUL_IN_OUTFIELD = "Umpire review: Fair/foul in outfield"  # Live
UMPIRE_REVIEW_FAN_INTERFERENCE = "Umpire review: Fan interference"  # Live
UMPIRE_REVIEW_FORCE_PLAY = "Umpire review: Force play"  # Live
UMPIRE_REVIEW_GROUNDS_RULE = "Umpire review: Grounds rule"  # Live
UMPIRE_REVIEW_HIT_BY_PITCH = "Umpire review: Hit by pitch"  # Live
UMPIRE_REVIEW_HOME_RUN = "Umpire review: Home run"  # Live
UMPIRE_REVIEW_HOMEPLATE_COLLISION = "Umpire review: Home-plate collision"  # Live
UMPIRE_REVIEW_MULTIPLE_ISSUES = "Umpire review: Multiple issues"  # Live
UMPIRE_REVIEW_PASSING_RUNNERS = "Umpire review: Passing runners"  # Live
UMPIRE_REVIEW_RECORD_KEEPING = "Umpire review: Record keeping"  # Live
UMPIRE_REVIEW_RULES_CHECK = "Umpire review: Rules check"  # Live
UMPIRE_REVIEW_SLIDE_INTERFERENCE = "Umpire review: Slide interference"  # Live
UMPIRE_REVIEW_STADIUM_BOUNDARY_CALL = "Umpire review: Stadium boundary call"  # Live
UMPIRE_REVIEW_TAG_PLAY = "Umpire review: Tag play"  # Live
UMPIRE_REVIEW_TAGUP_PLAY = "Umpire review: Tag-up play"  # Live
UMPIRE_REVIEW_TIMING_PLAY = "Umpire review: Timing play"  # Live
UMPIRE_REVIEW_TOUCHING_A_BASE = "Umpire review: Touching a base"  # Live
UMPIRE_REVIEW_TRAP_PLAY_IN_OUTFIELD = "Umpire review: Trap play in outfield"  # Live
UNKNOWN = "Unknown"  # Other
WARMUP = "Warmup"  # Live
WRITING = "Writing"  # Other
REVIEW = "Review"  # Not in json

GAME_STATE_INNING_BREAK = [Inning.TOP, Inning.BOTTOM]

GAME_STATE_LIVE = [
    IN_PROGRESS,
    WARMUP,
    INSTANT_REPLAY,
    GAME_OVER,
    GAME_OVER_TIE_DECISION_BY_TIEBREAKER,
    GAME_OVER_TIED,
    MANAGER_CHALLENGE,
    MANAGER_CHALLENGE_CATCHDROP_IN_OUTFIELD,
    MANAGER_CHALLENGE_CLOSE_PLAY_AT_1ST,
    MANAGER_CHALLENGE_FAIRFOUL_IN_OUTFIELD,
    MANAGER_CHALLENGE_FAN_INTERFERENCE,
    MANAGER_CHALLENGE_FORCE_PLAY,
    MANAGER_CHALLENGE_GROUNDS_RULE,
    MANAGER_CHALLENGE_HIT_BY_PITCH,
    MANAGER_CHALLENGE_HOME_RUN,
    MANAGER_CHALLENGE_HOMEPLATE_COLLISION,
    MANAGER_CHALLENGE_MULTIPLE_ISSUES,
    MANAGER_CHALLENGE_PASSING_RUNNERS,
    MANAGER_CHALLENGE_RECORD_KEEPING,
    MANAGER_CHALLENGE_RULES_CHECK,
    MANAGER_CHALLENGE_SLIDE_INTERFERENCE,
    MANAGER_CHALLENGE_STADIUM_BOUNDARY_CALL,
    MANAGER_CHALLENGE_TAG_PLAY,
    MANAGER_CHALLENGE_TAGUP_PLAY,
    MANAGER_CHALLENGE_TIMING_PLAY,
    MANAGER_CHALLENGE_TOUCHING_A_BASE,
    MANAGER_CHALLENGE_TRAP_PLAY_IN_OUTFIELD,
    UMPIRE_REVIEW,
    UMPIRE_REVIEW_CATCHDROP_IN_OUTFIELD,
    UMPIRE_REVIEW_CLOSE_PLAY_AT_1ST,
    UMPIRE_REVIEW_FAIRFOUL_IN_OUTFIELD,
    UMPIRE_REVIEW_FAN_INTERFERENCE,
    UMPIRE_REVIEW_FORCE_PLAY,
    UMPIRE_REVIEW_GROUNDS_RULE,
    UMPIRE_REVIEW_HIT_BY_PITCH,
    UMPIRE_REVIEW_HOME_RUN,
    UMPIRE_REVIEW_HOMEPLATE_COLLISION,
    UMPIRE_REVIEW_MULTIPLE_ISSUES,
    UMPIRE_REVIEW_PASSING_RUNNERS,
    UMPIRE_REVIEW_RECORD_KEEPING,
    UMPIRE_REVIEW_RULES_CHECK,
    UMPIRE_REVIEW_SLIDE_INTERFERENCE,
    UMPIRE_REVIEW_STADIUM_BOUNDARY_CALL,
    UMPIRE_REVIEW_TAG_PLAY,
    UMPIRE_REVIEW_TAGUP_PLAY,
    UMPIRE_REVIEW_TIMING_PLAY,
    UMPIRE_REVIEW_TOUCHING_A_BASE,
    UMPIRE_REVIEW_TRAP_PLAY_IN_OUTFIELD,
]

GAME_STATE_PREGAME = [SCHEDULED, PREGAME, WARMUP]

GAME_STATE_COMPLETE = [
    COMPLETED_EARLY,
    COMPLETED_EARLY_COLD,
    COMPLETED_EARLY_DARKNESS,
    COMPLETED_EARLY_EMERGENCY,
    COMPLETED_EARLY_FOG,
    COMPLETED_EARLY_INCLEMENT_WEATHER,
    COMPLETED_EARLY_LIGHTNING,
    COMPLETED_EARLY_MERCY_RULE,
    COMPLETED_EARLY_POWER,
    COMPLETED_EARLY_RAIN,
    COMPLETED_EARLY_SNOW,
    COMPLETED_EARLY_TRAGEDY,
    COMPLETED_EARLY_VENUE,
    COMPLETED_EARLY_WET_GROUNDS,
    COMPLETED_EARLY_WIND,
    FINAL,
    FINAL_TIE_DECISION_BY_TIEBREAKER,
    FINAL_TIED,
    GAME_OVER,
    GAME_OVER_TIE_DECISION_BY_TIEBREAKER,
    GAME_OVER_TIED,
]

GAME_STATE_FRESH = [IN_PROGRESS, GAME_OVER, GAME_OVER_TIED, GAME_OVER_TIE_DECISION_BY_TIEBREAKER]

GAME_STATE_IRREGULAR = [
    CANCELLED,
    CANCELLED_COLD,
    CANCELLED_DARKNESS,
    CANCELLED_EMERGENCY,
    CANCELLED_FOG,
    CANCELLED_INCLEMENT_WEATHER,
    CANCELLED_LIGHTNING,
    CANCELLED_POWER,
    CANCELLED_RAIN,
    CANCELLED_SNOW,
    CANCELLED_TRAGEDY,
    CANCELLED_VENUE,
    CANCELLED_WET_GROUNDS,
    CANCELLED_WIND,
    DELAYED,
    DELAYED_ABOUT_TO_RESUME,
    DELAYED_CEREMONY,
    DELAYED_COLD,
    DELAYED_DARKNESS,
    DELAYED_EMERGENCY,
    DELAYED_FOG,
    DELAYED_INCLEMENT_WEATHER,
    DELAYED_LIGHTNING,
    DELAYED_POWER,
    DELAYED_RAIN,
    DELAYED_SNOW,
    DELAYED_START,
    DELAYED_START_CEREMONY,
    DELAYED_START_COLD,
    DELAYED_START_DARKNESS,
    DELAYED_START_EMERGENCY,
    DELAYED_START_FOG,
    DELAYED_START_INCLEMENT_WEATHER,
    DELAYED_START_LIGHTNING,
    DELAYED_START_POWER,
    DELAYED_START_RAIN,
    DELAYED_START_SNOW,
    DELAYED_START_TRAGEDY,
    DELAYED_START_VENUE,
    DELAYED_START_WET_GROUNDS,
    DELAYED_START_WIND,
    DELAYED_TRAGEDY,
    DELAYED_VENUE,
    DELAYED_WET_GROUNDS,
    DELAYED_WIND,
    FORFEIT,
    FORFEIT_DELAY_OF_GAME,
    FORFEIT_FAILURE_TO_APPEAR,
    FORFEIT_FAILURE_TO_FIELD_LINEUP,
    FORFEIT_FINAL,
    FORFEIT_GAME_OVER,
    FORFEIT_IGNORING_EJECTION,
    FORFEIT_INELIGIBLE_PLAYER,
    FORFEIT_REFUSES_TO_PLAY,
    FORFEIT_UNPLAYABLE_FIELD,
    FORFEIT_WILLFUL_RULE_VIOLATION,
    MANAGER_CHALLENGE,
    MANAGER_CHALLENGE_CATCHDROP_IN_OUTFIELD,
    MANAGER_CHALLENGE_CLOSE_PLAY_AT_1ST,
    MANAGER_CHALLENGE_FAIRFOUL_IN_OUTFIELD,
    MANAGER_CHALLENGE_FAN_INTERFERENCE,
    MANAGER_CHALLENGE_FORCE_PLAY,
    MANAGER_CHALLENGE_GROUNDS_RULE,
    MANAGER_CHALLENGE_HIT_BY_PITCH,
    MANAGER_CHALLENGE_HOME_RUN,
    MANAGER_CHALLENGE_HOMEPLATE_COLLISION,
    MANAGER_CHALLENGE_MULTIPLE_ISSUES,
    MANAGER_CHALLENGE_PASSING_RUNNERS,
    MANAGER_CHALLENGE_RECORD_KEEPING,
    MANAGER_CHALLENGE_RULES_CHECK,
    MANAGER_CHALLENGE_SLIDE_INTERFERENCE,
    MANAGER_CHALLENGE_STADIUM_BOUNDARY_CALL,
    MANAGER_CHALLENGE_TAG_PLAY,
    MANAGER_CHALLENGE_TAGUP_PLAY,
    MANAGER_CHALLENGE_TIMING_PLAY,
    MANAGER_CHALLENGE_TOUCHING_A_BASE,
    MANAGER_CHALLENGE_TRAP_PLAY_IN_OUTFIELD,
    POSTPONED,
    POSTPONED_COLD,
    POSTPONED_DARKNESS,
    POSTPONED_EMERGENCY,
    POSTPONED_FOG,
    POSTPONED_INCLEMENT_WEATHER,
    POSTPONED_LIGHTNING,
    POSTPONED_POWER,
    POSTPONED_RAIN,
    POSTPONED_SNOW,
    POSTPONED_TRAGEDY,
    POSTPONED_VENUE,
    POSTPONED_WET_GROUNDS,
    POSTPONED_WIND,
    SUSPENDED,
    SUSPENDED_ABOUT_TO_RESUME,
    SUSPENDED_APPEAL_UPHELD,
    SUSPENDED_COLD,
    SUSPENDED_DARKNESS,
    SUSPENDED_EMERGENCY,
    SUSPENDED_FOG,
    SUSPENDED_INCLEMENT_WEATHER,
    SUSPENDED_LIGHTNING,
    SUSPENDED_POWER,
    SUSPENDED_RAIN,
    SUSPENDED_SNOW,
    SUSPENDED_TRAGEDY,
    SUSPENDED_VENUE,
    SUSPENDED_WET_GROUNDS,
    SUSPENDED_WIND,
    UMPIRE_REVIEW,
    UMPIRE_REVIEW_CATCHDROP_IN_OUTFIELD,
    UMPIRE_REVIEW_CLOSE_PLAY_AT_1ST,
    UMPIRE_REVIEW_FAIRFOUL_IN_OUTFIELD,
    UMPIRE_REVIEW_FAN_INTERFERENCE,
    UMPIRE_REVIEW_FORCE_PLAY,
    UMPIRE_REVIEW_GROUNDS_RULE,
    UMPIRE_REVIEW_HIT_BY_PITCH,
    UMPIRE_REVIEW_HOME_RUN,
    UMPIRE_REVIEW_HOMEPLATE_COLLISION,
    UMPIRE_REVIEW_MULTIPLE_ISSUES,
    UMPIRE_REVIEW_PASSING_RUNNERS,
    UMPIRE_REVIEW_RECORD_KEEPING,
    UMPIRE_REVIEW_RULES_CHECK,
    UMPIRE_REVIEW_SLIDE_INTERFERENCE,
    UMPIRE_REVIEW_STADIUM_BOUNDARY_CALL,
    UMPIRE_REVIEW_TAG_PLAY,
    UMPIRE_REVIEW_TAGUP_PLAY,
    UMPIRE_REVIEW_TIMING_PLAY,
    UMPIRE_REVIEW_TOUCHING_A_BASE,
    UMPIRE_REVIEW_TRAP_PLAY_IN_OUTFIELD,
    WRITING,
    UNKNOWN,
]


def is_pregame(status):
    """Returns whether the game is in a pregame state"""
    return status in GAME_STATE_PREGAME


def is_complete(status):
    """Returns whether the game has been completed"""
    return status in GAME_STATE_COMPLETE


def is_live(status):
    """Returns whether the game is currently live"""
    return status in GAME_STATE_LIVE


def is_irregular(status):
    """Returns whether game is in an irregular state, such as delayed, postponed, cancelled,
    or in a challenge."""
    return status in GAME_STATE_IRREGULAR


def is_fresh(status):
    """Returns whether the game is in progress or is very recently complete. Game Over
    comes between In Progress and Final and allows a few minutes to see the final outcome before
    the rotation kicks in."""
    return status in GAME_STATE_FRESH


def is_inning_break(inning_state):
    """Returns whether a game is in an inning break (mid/end). Pass in the inning state."""
    return inning_state not in GAME_STATE_INNING_BREAK
