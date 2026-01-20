class RuleSet:
    def __init__(self, rules):
        self.rules = rules

    def validate(self, action, world_model):
        for rule in self.rules:
            rule.check(action, world_model)
