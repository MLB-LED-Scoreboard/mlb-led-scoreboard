from migrations import ConfigMigration


class KeypathRenameTest(ConfigMigration):
    def up(self):
        self.rename_key("path.to.the.renamed_key", "renamed_key2", self.configs["base"])

    def down(self):
        self.rename_key("path.to.the.renamed_key2", "renamed_key", self.configs["base"])
