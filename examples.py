"""
Example usage of the Browser4AGI intelligent agent system.
Demonstrates long-term survival, self-repair, and self-expansion capabilities.
"""

import time
import json
from agent import IntelligentAgent
from web_capabilities import register_web_capabilities


def example_basic_usage():
    """Basic example of agent initialization and execution."""
    print("\n=== Example 1: Basic Agent Usage ===\n")
    
    # Create an intelligent agent
    agent = IntelligentAgent(name="MyAgent", state_file="example_agent_state.json")
    
    # Check initial status
    status = agent.get_status()
    print(f"Initial Status:")
    print(json.dumps(status, indent=2))
    
    # Run agent for a short duration
    print("\nRunning agent for 5 seconds...")
    agent.run(duration=5)
    
    # Check final status
    final_status = agent.get_status()
    print(f"\nFinal Status:")
    print(json.dumps(final_status, indent=2))


def example_self_expansion():
    """Example of agent self-expansion with new capabilities."""
    print("\n=== Example 2: Self-Expansion ===\n")
    
    agent = IntelligentAgent(name="ExpandableAgent", state_file="expandable_agent_state.json")
    
    print(f"Initial capabilities: {agent.capabilities.list_capabilities()}")
    
    # Expand agent with web capabilities
    print("\nExpanding agent with web capabilities...")
    register_web_capabilities(agent)
    
    print(f"Expanded capabilities: {agent.capabilities.list_capabilities()}")
    
    # Use a capability
    web_nav = agent.get_capability("web_navigation")
    if web_nav:
        result = web_nav.navigate("https://example.com")
        print(f"\nNavigation result: {json.dumps(result, indent=2)}")
    
    # Use scraping capability
    scraper = agent.get_capability("web_scraper")
    if scraper:
        result = scraper.scrape("https://example.com", selector=".content")
        print(f"\nScraping result: {json.dumps(result, indent=2)}")
    
    # Show capability statistics
    print(f"\nCapability statistics:")
    print(json.dumps(agent.capabilities.get_capability_stats(), indent=2))


def example_self_repair():
    """Example of agent self-repair mechanisms."""
    print("\n=== Example 3: Self-Repair ===\n")
    
    agent = IntelligentAgent(name="RepairableAgent", state_file="repairable_agent_state.json")
    
    # Perform health check
    print("Performing health check...")
    health_status = agent.perform_health_check()
    print(f"Health status: {json.dumps(health_status, indent=2)}")
    
    # Trigger self-repair
    print("\nAttempting self-repair...")
    repair_results = agent.perform_self_repair()
    print(f"Repair results: {json.dumps(repair_results, indent=2)}")
    
    # Custom health check example
    def custom_health_check():
        """Example custom health check."""
        return True  # Always healthy for this example
    
    agent.health_monitor.add_check("custom_check", custom_health_check)
    
    print("\nPerforming health check with custom check...")
    health_status = agent.perform_health_check()
    print(f"Health status: {json.dumps(health_status, indent=2)}")


def example_long_term_survival():
    """Example of agent long-term survival mechanisms."""
    print("\n=== Example 4: Long-Term Survival ===\n")
    
    # First run - create agent
    print("First run - Creating agent...")
    agent = IntelligentAgent(name="SurvivalAgent", state_file="survival_agent_state.json")
    print(f"Restart count: {agent.state.get('restart_count')}")
    
    # Add some data to state
    agent.state.set("custom_data", {"message": "This persists across restarts"})
    
    # Simulate shutdown
    agent.shutdown()
    
    # Second run - agent survives restart
    print("\nSecond run - Agent restarts and recovers state...")
    agent2 = IntelligentAgent(name="SurvivalAgent", state_file="survival_agent_state.json")
    print(f"Restart count: {agent2.state.get('restart_count')}")
    print(f"Recovered data: {agent2.state.get('custom_data')}")
    
    # Show state file exists
    import os
    if os.path.exists("survival_agent_state.json"):
        with open("survival_agent_state.json", 'r') as f:
            state_content = json.load(f)
        print(f"\nPersisted state content:")
        print(json.dumps(state_content, indent=2))


def example_web_automation():
    """Example of web automation capabilities."""
    print("\n=== Example 5: Web Automation ===\n")
    
    agent = IntelligentAgent(name="WebAgent", state_file="web_agent_state.json")
    
    # Register web capabilities
    register_web_capabilities(agent)
    
    # Get automation capability
    automation = agent.get_capability("web_automation")
    
    if automation:
        # Create an automation task
        task_steps = [
            {"action": "navigate", "url": "https://example.com"},
            {"action": "click", "selector": "#button"},
            {"action": "fill", "selector": "#input", "value": "test"}
        ]
        
        task = automation.create_task("Example Task", task_steps)
        print(f"Created task: {json.dumps(task, indent=2)}")
        
        # Execute the task
        result = automation.execute_task(task["id"])
        print(f"\nExecution result: {json.dumps(result, indent=2)}")
    
    # Get monitoring capability
    monitoring = agent.get_capability("web_monitoring")
    
    if monitoring:
        # Add a URL to monitor
        monitor = monitoring.add_monitor("https://example.com/api/status", check_interval=60)
        print(f"\nAdded monitor: {json.dumps(monitor, indent=2)}")
        
        # Check monitors
        check_results = monitoring.check_monitors()
        print(f"\nMonitor check results: {json.dumps(check_results, indent=2)}")


def example_api_interaction():
    """Example of API interaction capabilities."""
    print("\n=== Example 6: API Interaction ===\n")
    
    agent = IntelligentAgent(name="APIAgent", state_file="api_agent_state.json")
    
    # Register web capabilities
    register_web_capabilities(agent)
    
    # Get API interaction capability
    api = agent.get_capability("api_interaction")
    
    if api:
        # Make API calls
        result1 = api.call_api("https://api.example.com/users", method="GET")
        print(f"GET request result: {json.dumps(result1, indent=2)}")
        
        result2 = api.call_api("https://api.example.com/users", method="POST", 
                               data={"name": "John", "email": "john@example.com"})
        print(f"\nPOST request result: {json.dumps(result2, indent=2)}")
        
        # Get request history
        history = api.get_request_history()
        print(f"\nRequest history ({len(history)} requests):")
        for req in history:
            print(f"  - {req['method']} {req['endpoint']} at {req['timestamp']}")


def run_all_examples():
    """Run all examples."""
    examples = [
        example_basic_usage,
        example_self_expansion,
        example_self_repair,
        example_long_term_survival,
        example_web_automation,
        example_api_interaction
    ]
    
    for example in examples:
        try:
            example()
            time.sleep(1)  # Brief pause between examples
        except Exception as e:
            print(f"Error in example: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    import sys
    
    print("=" * 70)
    print("Browser4AGI - Intelligent Agent System Examples")
    print("=" * 70)
    
    if len(sys.argv) > 1:
        example_name = sys.argv[1]
        example_map = {
            "basic": example_basic_usage,
            "expansion": example_self_expansion,
            "repair": example_self_repair,
            "survival": example_long_term_survival,
            "automation": example_web_automation,
            "api": example_api_interaction,
            "all": run_all_examples
        }
        
        if example_name in example_map:
            example_map[example_name]()
        else:
            print(f"Unknown example: {example_name}")
            print(f"Available examples: {', '.join(example_map.keys())}")
    else:
        # Run all examples by default
        run_all_examples()
    
    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)
