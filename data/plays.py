SINGLE = "single"
DOUBLE = "double"
TRIPLE = "triple"
HOME_RUN = "home_run"

WALK = "walk"
INTENTIONAL_WALK = "intent_walk"
HIT_BY_PITCH = "hit_by_pitch"

STRIKEOUT = "strikeout"
STRIKEOUT_ALT = "strike_out"
STRIKEOUT_LOOKING = "strikeout_looking"

ERROR = "error"
FIELDERS_CHOICE = "fielders_choice"

HITS = [SINGLE, DOUBLE, TRIPLE]

WALKS = [WALK, INTENTIONAL_WALK, HIT_BY_PITCH]

OTHERS = [ERROR, FIELDERS_CHOICE]

STRIKEOUTS = [STRIKEOUT, STRIKEOUT_ALT, STRIKEOUT_LOOKING]

PLAY_RESULTS = {
    SINGLE: {"short": "1B", "long": "Single"},
    DOUBLE: {"short": "2B", "long": "Double"},
    TRIPLE: {"short": "3B", "long": "Triple"},
    WALK: {"short": "BB", "long": "Walk"},
    INTENTIONAL_WALK: {"short": "IBB", "long": "Int. Walk"},
    STRIKEOUT: {"short": "K", "long": "K"},
    STRIKEOUT_ALT: {"short": "K", "long": "K"},
    STRIKEOUT_LOOKING: {"short": "ꓘ", "long": "ꓘ"},
    HIT_BY_PITCH: {"short": "HBP", "long": "Hit Bttr"},
    ERROR: {"short": "E", "long": "Error"},
    FIELDERS_CHOICE: {"short": "FC", "long": "Fielder's Chc"},
}
