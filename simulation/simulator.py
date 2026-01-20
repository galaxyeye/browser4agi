class Simulator:
    def __init__(self, engine):
        self.engine = engine

    def run(self, actions, observations):
        for action, observation in zip(actions, observations):
            self.engine.step(action, observation)
