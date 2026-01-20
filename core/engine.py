class Engine:
    def __init__(self, world_model, rule_set):
        self.world = world_model
        self.rules = rule_set

    def step(self, action, observation):
        self.rules.validate(action, self.world)
        self.world.update(observation)
