class Trace:
    def __init__(self):
        self.events = []

    def log(self, event):
        self.events.append(event)
