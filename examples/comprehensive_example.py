"""
Comprehensive example demonstrating the browser4agi system
"""
from core.browser4agi import Browser4AGI
from core.world_model import WorldModel
from core.action import Action
from rules.rule import PreconditionRule, OrderRule
from rules.rule_set import RuleSet


def example_basic_usage():
    """Basic usage example"""
    print("=== Browser4AGI Basic Usage Example ===\n")
    
    # Initialize system
    system = Browser4AGI(initial_version="v0", use_llm=False)
    
    # Add some initial rules
    rule1 = PreconditionRule(
        rule_id="require_url",
        required_state={"has_url": True},
        description="URL must be available before browsing"
    )
    system.rule_set.add_rule(rule1)
    
    rule2 = OrderRule(
        rule_id="click_after_load",
        action_name="browser.click",
        must_follow=["browser.open"],
        description="Must open page before clicking"
    )
    system.rule_set.add_rule(rule2)
    
    print(f"Initial state: {system.get_system_state()}\n")
    
    # Execute a task
    print("Executing task: Browse example.com")
    report = system.execute_task("Browse to example.com and extract title")
    print(f"Status: {report.status.value}")
    print(f"Events: {len(report.events)}\n")
    
    # Get system state
    state = system.get_system_state()
    print(f"System state after execution:")
    print(f"  Version: {state['version']}")
    print(f"  Rule count: {state['rule_count']}")
    print(f"  Executions: {state['execution_count']}\n")


def example_self_evolution():
    """Self-evolution loop example"""
    print("=== Browser4AGI Self-Evolution Example ===\n")
    
    # Initialize system
    system = Browser4AGI(initial_version="v0", use_llm=False)
    
    # Define test tasks
    test_tasks = [
        "Navigate to example.com",
        "Search for 'browser automation'",
        "Extract data from page"
    ]
    
    print(f"Running self-evolution with {len(test_tasks)} test tasks\n")
    
    # Run evolution step
    result = system.self_evolve_step(test_tasks)
    
    print("Evolution step result:")
    print(f"  Status: {result['status']}")
    print(f"  Failures: {result['failures']}")
    print(f"  Patches generated: {result['patches_generated']}")
    print(f"  Patches applied: {result.get('patches_applied', 0)}")
    print(f"  Current version: {result.get('current_version', 'N/A')}")
    print(f"  Rule count: {result.get('rule_count', 0)}\n")
    
    # Check rule health
    state = system.get_system_state()
    health = state['rule_health']
    print("Rule health report:")
    print(f"  Total rules: {health['total_rules']}")
    print(f"  Active: {health['active']}")
    print(f"  Cooldown: {health['cooldown']}")
    print(f"  Deprecated: {health['deprecated']}")
    print(f"  Avg confidence: {health['avg_confidence']:.2f}\n")


def example_version_management():
    """Version management and rollback example"""
    print("=== Browser4AGI Version Management Example ===\n")
    
    # Initialize system
    system = Browser4AGI(initial_version="v0")
    
    print(f"Starting version: {system.world_model.version}")
    
    # Create some versions through evolution
    test_tasks = ["Task 1", "Task 2"]
    
    for i in range(3):
        result = system.self_evolve_step(test_tasks)
        print(f"Evolution {i+1}: version={result.get('current_version', 'N/A')}, "
              f"rules={result.get('rule_count', 0)}")
    
    current_version = system.world_model.version
    print(f"\nCurrent version: {current_version}")
    
    # Rollback
    print("\nAttempting rollback to v0...")
    success = system.rollback_to_version("v0")
    if success:
        print(f"Rollback successful! Now at version: {system.world_model.version}")
    else:
        print("Rollback failed - version not found")
    
    print()


def example_budget_control():
    """Budget control and rule explosion prevention example"""
    print("=== Browser4AGI Budget Control Example ===\n")
    
    from core.evolution_control import PatchBudget
    
    # Create system with strict budget
    budget = PatchBudget(
        max_patches_per_window=3,
        max_rule_count_increase=5,
        time_window_hours=24.0
    )
    
    system = Browser4AGI(initial_version="v0", patch_budget=budget)
    
    print("Budget constraints:")
    print(f"  Max patches per window: {budget.max_patches_per_window}")
    print(f"  Max rule count increase: {budget.max_rule_count_increase}")
    print(f"  Time window: {budget.time_window_hours} hours\n")
    
    # Try to evolve multiple times
    test_tasks = ["Task A", "Task B", "Task C"]
    
    for i in range(5):
        result = system.self_evolve_step(test_tasks)
        budget_status = system.evolution_controller.get_budget_status()
        
        print(f"Evolution {i+1}:")
        print(f"  Patches applied: {result.get('patches_applied', 0)}")
        print(f"  Budget used: {budget_status['patches_used']}/{budget_status['patches_used'] + budget_status['patches_available']}")
        print(f"  Rule count: {result.get('rule_count', 0)}\n")


def example_export_import():
    """Export and monitoring example"""
    print("=== Browser4AGI Export Example ===\n")
    
    # Initialize and run some tasks
    system = Browser4AGI(initial_version="v0")
    
    # Execute some tasks
    for i in range(3):
        system.execute_task(f"Task {i+1}")
    
    # Export model
    export_path = "/tmp/browser4agi_model.json"
    system.export_model(export_path)
    print(f"Model exported to: {export_path}")
    
    # Show what was exported
    import json
    with open(export_path, 'r') as f:
        data = json.load(f)
    
    print(f"\nExported data contains:")
    print(f"  World model version: {data['world_model']['version']}")
    print(f"  Rules: {len(data['world_model']['rules'])}")
    print(f"  Recent executions: {len(data['execution_history'])}")
    print(f"  System state keys: {list(data['system_state'].keys())}\n")


def main():
    """Run all examples"""
    examples = [
        example_basic_usage,
        example_self_evolution,
        example_version_management,
        example_budget_control,
        example_export_import
    ]
    
    for example in examples:
        try:
            example()
            print("-" * 60 + "\n")
        except Exception as e:
            print(f"Error in {example.__name__}: {e}\n")


if __name__ == "__main__":
    main()
