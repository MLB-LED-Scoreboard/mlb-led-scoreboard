from migrations import ConfigMigration

import json


class HelloWorldTwo(ConfigMigration):
    def up(self):
        for _config_type, config_files in self.configs.items():
            for config_file in config_files:
                with open(config_file, 'r') as f:
                    content = json.load(f)

                content["helloworld2"] = "Hello world!"

                with open(config_file, 'w') as f:
                    json.dump(content, f, indent=2)

    def down(self):
        for _config_type, config_files in self.configs.items():
            for config_file in config_files:
                with open(config_file, 'r') as f:
                    content = json.load(f)

                if "helloworld2" in content:
                    del content["helloworld2"]

                with open(config_file, 'w') as f:
                    json.dump(content, f, indent=2)
