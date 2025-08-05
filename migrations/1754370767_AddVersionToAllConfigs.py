from migrations._base import ConfigMigration

import json


class AddVersionToAllConfigs(ConfigMigration):
    TARGET_VERSION = "1754370767"

    def up(self):
        for _config_type, config_files in self.configs.items():
            for config_file in config_files:
                with open(config_file, 'r') as f:
                    content = json.load(f)

                content["version"] = self.TARGET_VERSION

                with open(config_file, 'w') as f:
                    json.dump(content, f, indent=2)

    def down(self):
        for _config_type, config_files in self.configs.items():
            for config_file in config_files:
                with open(config_file, 'r') as f:
                    content = json.load(f)

                if "version" in content:
                    del content["version"]

                with open(config_file, 'w') as f:
                    json.dump(content, f, indent=2)
