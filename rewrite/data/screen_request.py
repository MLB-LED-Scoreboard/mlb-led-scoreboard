from screens import Screen


class ScreenRequest:
    class InvalidRequest(Exception):
        pass

    def __init__(self, type, manager, **kwargs):
        # Required arguments
        self.type = type
        self.manager = manager

        # Screen-specific arguments
        self.kwargs = kwargs

        if self.type not in Screen:
            raise ScreenRequest.InvalidRequest(f"Screen type {self.type} is not valid")
