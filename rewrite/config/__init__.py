import logging

from config.layout import Layout
from config.colors import Colors

from utils import logger as ScoreboardLogger
from utils import deep_update, read_json


class Config:
    REFERENCE_FILENAME = "config.json.example"

    def __init__(self, config_filename, width, height):
        self.width = width
        self.height = height
        self.dimensions = (width, height)

        config = self.__fetch_config(config_filename)
        self.__parse_config(config)

        self.__set_log_level()

        self.layout = Layout(width, height)
        self.colors = Colors()

    def __fetch_config(self, name):
        """
        Loads a config (JSON-formatted) with a custom filename. Falls back to a default if not found.
        """
        filename = f"{name}.json"

        custom_config = read_json(filename)
        reference_config = read_json(Config.REFERENCE_FILENAME)

        if custom_config:
            # Retain only the values that are valid.
            config = deep_update(reference_config, custom_config)

            return config

        return reference_config

    def __parse_config(self, config):
        """
        Convert a JSON config file to callable attributes on the Config class.

        If the key is nested, the top level key serves as its attribute prefix, i.e.:

        {
            "type": {
                "key1": 1,
                "key2": { "one": 1, "two": 2 }
            }
        }

        config.type_key1
        #=> 1
        config.type_key2
        #=> { "one": 1, "two": 2 }

        If not nested, returns the result with no namespace, i.e.:

        { "type": "config" }

        config.type
        #=> "config"
        """
        for key in config:
            if isinstance(config[key], dict):
                for value in config[key]:
                    setattr(self, f"{key}_{value}", config[key][value])
            else:
                setattr(self, key, config[key])

    def __set_log_level(self):
        # As early as possible, set the log level for the custom logger.
        logger = logging.getLogger("mlbled")
        if self.debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.WARNING)
