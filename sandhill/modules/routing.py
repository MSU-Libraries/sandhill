from dataclasses import dataclass

@dataclass(order=True)
class Route:
    """
    It's a route, all bundled up into a class.
    """
    rule: str
    methods: list = None

    def __post_init__(self):
        if not self.methods:
            self.methods = ["GET"]
        self.methods = [method.upper() for method in self.methods]
