class WorldModel:
    """
    Explicit, versioned belief of the environment.
    Must be serializable and comparable.
    """

    def __init__(self, version: str):
        self.version = version
        self.state = {}

    def update(self, observation):
        self.state[observation.kind] = observation.payload

    def snapshot(self):
        return {
            "version": self.version,
            "state": dict(self.state)
        }
