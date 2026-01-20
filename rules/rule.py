class RuleViolation(Exception):
    pass


class Rule:
    def check(self, action, world_model):
        raise NotImplementedError
