from symposium.core.router import RouteRegistry
from symposium.windows.state import State
from symposium.windows.window import Window


class DialogRegistry:
    def __init__(self, router: RouteRegistry):
        self.windows = {}
        self.router = router

    def include(self, window: Window):
        self.windows[window.state] = window
        window.register(self.router)

    def find_window(self, state: State) -> Window:
        return self.windows[state]
