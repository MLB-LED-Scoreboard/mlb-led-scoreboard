from migrations import ConfigMigration

import json


class HelloWorld(ConfigMigration):
    def up(self):
        for _config_type, config_files in self.configs.items():
            for config_file in config_files:
                with open(config_file, 'r') as f:
                    content = json.load(f)

                content["new_key"] = "Hello world!"

                with open(config_file, 'w') as f:
                    json.dump(content, f, indent=2)

    def down(self):
        for _config_type, config_files in self.configs.items():
            for config_file in config_files:
                with open(config_file, 'r') as f:
                    content = json.load(f)

                if "new_key" in content:
                    del content["new_key"]

                with open(config_file, 'w') as f:
                    json.dump(content, f, indent=2)
