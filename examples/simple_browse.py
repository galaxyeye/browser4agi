"""
Simple browsing example using browser4agi
"""
from core.world_model import WorldModel
from core.engine import Engine
from rules.rule_set import RuleSet
from rules.rule import PreconditionRule
from tools.browser import BrowserTool
from core.action import Action
from core.observation import Observation


def main():
    print("=== Simple Browse Example ===\n")
    
    # Initialize components
    world = WorldModel(version="v0")
    rules = RuleSet([])
    engine = Engine(world, rules)
    browser = BrowserTool()
    
    # Add a simple rule
    rule = PreconditionRule(
        rule_id="check_initialized",
        required_state={"initialized": True},
        description="System must be initialized"
    )
    rules.add_rule(rule)
    
    # Initialize world state
    world.state["initialized"] = True
    
    print("Opening URL...")
    result = browser.open("https://example.com")
    print(f"Result: {result}\n")
    
    # Create observation
    observation = Observation(
        kind="page_loaded",
        payload=result
    )
    
    # Create action
    action = Action(
        name="browser.open",
        params={"url": "https://example.com"}
    )
    
    # Execute step
    print("Executing action through engine...")
    engine.step(action, observation)
    
    # Check world state
    print(f"World state: {world.state}")
    print(f"World version: {world.version}\n")
    
    # Take snapshot
    snapshot = world.snapshot()
    print(f"Snapshot created: version={snapshot.version}")
    print(f"Snapshot state: {snapshot.state}\n")
    
    print("Example completed successfully!")


if __name__ == "__main__":
    main()

