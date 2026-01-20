# Browser4AGI - Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/galaxyeye/browser4agi.git
cd browser4agi

# The system uses Python standard library, no additional dependencies required for basic usage
python3 --version  # Ensure Python 3.8+
```

## Basic Usage

### 1. Simple Browsing Example

```python
from core.browser4agi import Browser4AGI

# Initialize the system
system = Browser4AGI(initial_version="v0")

# Execute a task
report = system.execute_task("Browse to example.com")

# Check execution status
print(f"Status: {report.status}")
print(f"Events: {len(report.events)}")

# Get system state
state = system.get_system_state()
print(f"Version: {state['version']}")
print(f"Rules: {state['rule_count']}")
```

### 2. Self-Evolution Loop

```python
from core.browser4agi import Browser4AGI

# Initialize with LLM support (optional)
system = Browser4AGI(initial_version="v0", use_llm=False)

# Define test tasks
test_tasks = [
    "Navigate to example.com",
    "Search for browser automation",
    "Extract data from page"
]

# Run one evolution cycle
result = system.self_evolve_step(test_tasks)

print(f"Failures: {result['failures']}")
print(f"Patches generated: {result['patches_generated']}")
print(f"Patches applied: {result.get('patches_applied', 0)}")
print(f"New version: {result.get('current_version', 'N/A')}")
```

### 3. Adding Custom Rules

```python
from rules.rule import PreconditionRule, OrderRule
from core.browser4agi import Browser4AGI

system = Browser4AGI()

# Add a precondition rule
rule1 = PreconditionRule(
    rule_id="check_logged_in",
    required_state={"logged_in": True},
    description="User must be logged in"
)
system.rule_set.add_rule(rule1)

# Add an order constraint rule
rule2 = OrderRule(
    rule_id="click_after_load",
    action_name="browser.click",
    must_follow=["browser.open"],
    description="Page must load before clicking"
)
system.rule_set.add_rule(rule2)
```

### 4. Working with Tools

```python
from agent.executor import Executor
from core.action import Action

executor = Executor()

# Use browser tool
action = Action("browser.open", {"url": "https://example.com"})
observation = executor.execute_action(action)
print(observation.payload)

# Use filesystem tool
action = Action("filesystem.write", {
    "path": "output.txt",
    "content": "Hello, World!"
})
observation = executor.execute_action(action)
```

### 5. Version Management

```python
from core.browser4agi import Browser4AGI

system = Browser4AGI(initial_version="v0")

# Evolve the system
for i in range(3):
    result = system.self_evolve_step(["Task 1", "Task 2"])
    print(f"Version: {result.get('current_version')}")

# Get current version
current_version = system.world_model.version
print(f"Current: {current_version}")

# Rollback to previous version
success = system.rollback_to_version("v1")
if success:
    print("Rollback successful!")
```

### 6. Monitoring and Export

```python
from core.browser4agi import Browser4AGI

system = Browser4AGI()

# Execute some tasks
for i in range(5):
    system.execute_task(f"Task {i+1}")

# Get system state
state = system.get_system_state()
print(f"Executions: {state['execution_count']}")
print(f"Rule health: {state['rule_health']}")
print(f"Budget status: {state['budget_status']}")

# Export model
system.export_model("/tmp/model.json")

# Check rule health
health = state['rule_health']
print(f"Active rules: {health['active']}")
print(f"Deprecated rules: {health['deprecated']}")
print(f"Average confidence: {health['avg_confidence']:.2f}")
```

### 7. Budget Control

```python
from core.browser4agi import Browser4AGI
from core.evolution_control import PatchBudget

# Create strict budget
budget = PatchBudget(
    max_patches_per_window=5,
    max_rule_count_increase=10,
    time_window_hours=24.0
)

system = Browser4AGI(patch_budget=budget)

# System will automatically enforce budget during evolution
result = system.self_evolve_step(["Task 1", "Task 2"])

# Check budget status
status = system.evolution_controller.get_budget_status()
print(f"Patches used: {status['patches_used']}/{status['patches_used'] + status['patches_available']}")
```

## Running Examples

```bash
cd /home/runner/work/browser4agi/browser4agi

# Simple example
PYTHONPATH=/home/runner/work/browser4agi/browser4agi python3 examples/simple_browse.py

# Comprehensive example with all features
PYTHONPATH=/home/runner/work/browser4agi/browser4agi python3 examples/comprehensive_example.py
```

## Key Concepts

### WorldModel
- Versioned representation of system's world knowledge
- Contains rules and state
- Supports branching and rollback

### Rules
- Define constraints and ordering for actions
- Have lifecycle (ACTIVE → COOLDOWN → DEPRECATED)
- Confidence scores based on success/failure

### Reflection
- Analyzes execution failures
- Generates patch proposals
- Two versions: rule-based (v1) and LLM-assisted (v2)

### Simulation
- A/B testing of patches
- Compares baseline vs patched versions
- Metrics-driven evaluation

### Evolution Control
- Prevents rule explosion
- Uses Pareto frontier for optimization
- Enforces budget constraints

### PatchApplier
- Only component that can modify WorldModel
- Maintains version history
- Ensures auditability

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                       Browser4AGI System                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │ WorldModel   │────────▶│  RuleSet     │                 │
│  │  (versioned) │         │  (rules)     │                 │
│  └──────┬───────┘         └──────┬───────┘                 │
│         │                        │                          │
│         ▼                        ▼                          │
│  ┌─────────────────────────────────┐                       │
│  │         Engine                  │                       │
│  │  - DagBuilder                   │                       │
│  │  - DAG Execution                │                       │
│  └────────────┬────────────────────┘                       │
│               │                                             │
│               ▼                                             │
│  ┌─────────────────────────────────┐                       │
│  │    ExecutionReport              │                       │
│  │  - Status                       │                       │
│  │  - Events                       │                       │
│  │  - BuildTraces                  │                       │
│  └────────────┬────────────────────┘                       │
│               │                                             │
│      Success  │  Failure                                    │
│        ▼      ▼                                            │
│  ┌─────────────────────────────────┐                       │
│  │      Reflection                 │                       │
│  │  - V1 (rule-based)              │                       │
│  │  - V2 (LLM-assisted)            │                       │
│  └────────────┬────────────────────┘                       │
│               │                                             │
│               ▼                                             │
│  ┌─────────────────────────────────┐                       │
│  │    PatchProposals               │                       │
│  └────────────┬────────────────────┘                       │
│               │                                             │
│               ▼                                             │
│  ┌─────────────────────────────────┐                       │
│  │      Simulator                  │                       │
│  │  - A/B Testing                  │                       │
│  │  - Metrics                      │                       │
│  └────────────┬────────────────────┘                       │
│               │                                             │
│               ▼                                             │
│  ┌─────────────────────────────────┐                       │
│  │  Evolution Controller           │                       │
│  │  - Pareto Frontier              │                       │
│  │  - Budget Constraints           │                       │
│  └────────────┬────────────────────┘                       │
│               │                                             │
│               ▼                                             │
│  ┌─────────────────────────────────┐                       │
│  │    PatchApplier                 │                       │
│  │  - Apply Patches                │                       │
│  │  - Version Management           │                       │
│  └────────────┬────────────────────┘                       │
│               │                                             │
│               ▼                                             │
│  ┌──────────────────────────────────┐                      │
│  │  WorldModel++ (new version)      │                      │
│  └──────────────────────────────────┘                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Next Steps

1. **Integrate Real Browser**: Replace mock BrowserTool with Playwright/Selenium
2. **Add LLM**: Integrate OpenAI/Anthropic for ReflectionV2
3. **Persistence**: Add database backend for version history
4. **Visualization**: Create web UI for monitoring
5. **Advanced Planning**: Implement PDDL or learned planners

## Documentation

- See `README.md` for architecture overview
- See `IMPLEMENTATION.md` for detailed technical documentation
- See `examples/` for code examples

## Support

For issues and questions, please open an issue on the GitHub repository.
