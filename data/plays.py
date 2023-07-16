SINGLE   = "single"
DOUBLE   = "double"
TRIPLE   = "triple"
HOME_RUN = "home_run"

WALK             = "walk"
INTENTIONAL_WALK = "intent_walk"

STRIKEOUT         = "strikeout"
STRIKEOUT_LOOKING = "strikeout_looking"

HITS = [
  SINGLE,
  DOUBLE,
  TRIPLE
]

WALKS = [
  WALK,
  INTENTIONAL_WALK
]

STRIKEOUTS = [
  STRIKEOUT,
  STRIKEOUT_LOOKING
]

PLAY_RESULTS = {
    SINGLE: {
    "short": "1B", 
    "long": "Single"
  },
    DOUBLE: {
    "short": "2B", 
    "long": "Double"
  },
    TRIPLE: {
    "short": "3B", 
    "long": "Triple"
  }, 
    HOME_RUN: {
    "short": "HR",
    "long": "Home Run"
    },
    WALK: {
    "short": "BB",
    "long": "Walk"
    },
    INTENTIONAL_WALK: {
    "short": "IBB",
    "long": "Int. Walk"
    },
    STRIKEOUT: {
    "short": "K",
    "long": "K"
    },
    STRIKEOUT_LOOKING: {
    "short": "ꓘ",
    "long": "ꓘ"
    }
}