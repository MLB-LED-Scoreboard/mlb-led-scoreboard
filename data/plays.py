SINGLE = "single"
DOUBLE = "double"
TRIPLE = "triple"

STOLEN_BASE_2B = "stolen_base_2b"
STOLEN_BASE_3B = "stolen_base_3b"
STOLEN_BASE_HOME = "stolen_base_home"

WALK = "walk"
INTENTIONAL_WALK = "intent_walk"
HIT_BY_PITCH = "hit_by_pitch"

SINGLE_RBI = "single_rbi"
DOUBLE_RBI = "double_rbi"
TRIPLE_RBI = "triple_rbi"
WALK_RBI = "walk_rbi"
HIT_BY_PITCH_RBI = "hit_by_pitch_rbi"

FIELD_OUT_RBI = "field_out_rbi"
FIELD_OUT_FLY_RBI = "field_out_fly_rbi"
FIELD_OUT_LINE_RBI = "field_out_line_rbi"
FIELD_OUT_GROUND_RBI = "field_out_ground_rbi"
FIELD_OUT_POP_RBI = "field_out_pop_rbi"

HOME_RUN = "home_run"
HOME_RUN_2 = "home_run_2"
HOME_RUN_3 = "home_run_3"
HOME_RUN_4 = "home_run_4"

SACRIFICE_BUNT = "sac_bunt"
SACRIFICE_FLY = "sac_fly"
SACRIFICE_BUNT_RBI = "sac_bunt_rbi"
SACRIFICE_FLY_RBI = "sac_fly_rbi"

ERROR = "error"
FIELDERS_CHOICE = "fielders_choice"

STRIKEOUT = "strikeout"
STRIKEOUT_ALT = "strike_out"
STRIKEOUT_LOOKING = "strikeout_looking"

FIELD_OUT = "field_out"
FIELD_OUT_FLY = "field_out_fly"
FIELD_OUT_LINE = "field_out_line"
FIELD_OUT_GROUND = "field_out_ground"
FIELD_OUT_POP = "field_out_pop"

DOUBLE_PLAY = "double_play"
DOUBLE_PLAY_ALT = "grounded_into_double_play"

HITS = [SINGLE, DOUBLE, TRIPLE, HOME_RUN, HOME_RUN_2, HOME_RUN_3, HOME_RUN_4, SINGLE_RBI, DOUBLE_RBI, TRIPLE_RBI, WALK_RBI, SACRIFICE_FLY_RBI, SACRIFICE_BUNT_RBI, FIELD_OUT, FIELD_OUT_FLY, FIELD_OUT_LINE, FIELD_OUT_GROUND, FIELD_OUT_POP, SACRIFICE_BUNT, SACRIFICE_FLY, ERROR, FIELDERS_CHOICE, DOUBLE_PLAY, DOUBLE_PLAY_ALT]

WALKS = [WALK, INTENTIONAL_WALK, HIT_BY_PITCH, STOLEN_BASE_2B, STOLEN_BASE_3B, STOLEN_BASE_HOME, WALK_RBI]

OUTS = [FIELD_OUT, FIELD_OUT_FLY, FIELD_OUT_LINE, FIELD_OUT_GROUND, FIELD_OUT_POP, DOUBLE_PLAY, DOUBLE_PLAY_ALT]

STRIKEOUTS = [STRIKEOUT, STRIKEOUT_ALT, STRIKEOUT_LOOKING]

SCORING = [HOME_RUN, HOME_RUN_2, HOME_RUN_3, HOME_RUN_4, SINGLE_RBI, DOUBLE_RBI, TRIPLE_RBI, STOLEN_BASE_HOME, WALK_RBI, HIT_BY_PITCH_RBI, SACRIFICE_FLY_RBI, SACRIFICE_BUNT_RBI, FIELD_OUT_FLY_RBI, FIELD_OUT_LINE_RBI, FIELD_OUT_GROUND_RBI, FIELD_OUT_POP_RBI, FIELD_OUT_RBI]

OTHERS = [ERROR, FIELDERS_CHOICE]

PLAY_RESULTS = {
    SINGLE: {"short": "1B", "long": "Single"},
    DOUBLE: {"short": "2B", "long": "Double"},
    TRIPLE: {"short": "3B", "long": "Triple"},
    HOME_RUN: {"short": "HR", "long": "Home Run"},
    HOME_RUN_2: {"short": "HR", "long": "HomeRun!"},
    HOME_RUN_3: {"short": "HR", "long": "HomeRn!!"},
    HOME_RUN_4: {"short": "GS", "long": "GrndSlam"},
    WALK: {"short": "BB", "long": "Walk"},
    INTENTIONAL_WALK: {"short": "IBB", "long": "Int Walk"},
    STRIKEOUT: {"short": "K", "long": "StrKeout"},
    STRIKEOUT_ALT: {"short": "K", "long": "StrKeout"},
    STRIKEOUT_LOOKING: {"short": "ꓘ", "long": "Strꓘeout"},
    HIT_BY_PITCH: {"short": "HBP", "long": "Hit Bttr"},
    ERROR: {"short": "E", "long": "Error"},
    FIELDERS_CHOICE: {"short": "FC", "long": "Fld Chce"},
    FIELD_OUT_FLY: {"short": "FO", "long": "Flyout"},
    FIELD_OUT_LINE: {"short": "LO", "long": "Lineout"},
    FIELD_OUT_GROUND: {"short": "GO", "long": "Grndout"},
    FIELD_OUT_POP: {"short": "PO", "long": "Popout"},
    FIELD_OUT: {"short": "O", "long": "Out"},
    DOUBLE_PLAY: {"short": "DP", "long": "Dbl Play"},
    DOUBLE_PLAY_ALT: {"short": "DP", "long": "Dbl Play"},
    SACRIFICE_BUNT: {"short": "ScB", "long": "Sac Bunt"},
    SACRIFICE_BUNT_RBI: {"short": "ScB", "long": "RBI SBnt"},
    SACRIFICE_FLY: {"short": "ScF", "long": "Sac Fly"},
    SACRIFICE_FLY_RBI: {"short": "ScF", "long": "RBI SFly"},
    SINGLE_RBI: {"short": "1B", "long": "RBI Sngl"},
    DOUBLE_RBI: {"short": "2B", "long": "RBI Dble"},
    TRIPLE_RBI: {"short": "3B", "long": "RBI Trpl"},
    WALK_RBI: {"short": "BB", "long": "RBI Walk"},
    HIT_BY_PITCH_RBI: {"short": "HBP", "long": "RBI HBP"},
    STOLEN_BASE_2B: {"short": "SB", "long": "Stoln Bs"},
    STOLEN_BASE_3B: {"short": "SB", "long": "Stoln Bs"},
    STOLEN_BASE_HOME: {"short": "SB", "long": "Stl Home"},
    FIELD_OUT_FLY_RBI: {"short": "FO", "long": "RBI FlyO"},
    FIELD_OUT_LINE_RBI: {"short": "LO", "long": "RBI LneO"},
    FIELD_OUT_GROUND_RBI: {"short": "GO", "long": "RBI GrdO"},
    FIELD_OUT_POP_RBI: {"short": "PO", "long": "RBI PopO"},
    FIELD_OUT_RBI: {"short": "O", "long": "RBI Out"},
}
