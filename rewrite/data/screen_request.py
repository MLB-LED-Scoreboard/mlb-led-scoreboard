from screens import Screen

class ScreenRequest:

    class InvalidRequest(Exception):
        pass

    def __init__(self, type, manager, *args):
        self.type = type
        self.manager = manager
        self.args = args

        if self.type not in Screen:
            raise ScreenRequest.InvalidRequest(f"Screen type {self.type} is not valid")
