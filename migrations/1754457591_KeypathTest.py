from migrations._base import ConfigMigration


class KeypathTest(ConfigMigration):
    def up(self):
        self.add_key("path.to.the.key", 1, self.configs["base"])

    def down(self):
        self.remove_key("path", self.configs["base"])
