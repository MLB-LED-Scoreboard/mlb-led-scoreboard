from migrations import ConfigMigration, Transaction

import json


class TestTransaction(ConfigMigration):
    def up(self):
        with Transaction() as transaction:
            for file in self.configs["base"]:
                with open(file, 'r') as f:
                    content = json.load(f)

                content["test_transaction"] = True

                transaction.write(file, content)

    def down(self):
        with Transaction() as transaction:
            for file in self.configs["base"]:
                with open(file, 'r') as f:
                    content = json.load(f)

                if "test_transaction" in content:
                    del content["test_transaction"]

                transaction.write(file, content)
