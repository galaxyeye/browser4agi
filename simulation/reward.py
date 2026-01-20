class RewardModel:
    def score(self, trace):
        return len(trace.events)
