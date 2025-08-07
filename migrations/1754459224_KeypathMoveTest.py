from migrations import ConfigMigration


class KeypathMoveTest(ConfigMigration):
    def up(self):
        self.move_key("path.to.the.key", "path.to.the.renamed_key", self.configs["base"])

    def down(self):
        self.move_key("path.to.the.renamed_key", "path.to.the.key", self.configs["base"])
