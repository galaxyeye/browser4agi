from core.world_model import WorldModel
from core.engine import Engine
from rules.rule_set import RuleSet
from tools.browser import BrowserTool


world = WorldModel(version="v0")
engine = Engine(world, RuleSet([]))

browser = BrowserTool()
observation = browser.open("https://example.com")

print(observation)
