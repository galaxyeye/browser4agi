# browser4agi Implementation Documentation

## Overview

This implementation realizes the browser4agi architecture as described in the README. The system is a self-evolving browser agent that uses rule-driven execution, failure-driven learning, and controlled evolution.

## Architecture

### Core Components

#### 1. WorldModel (`core/world_model.py`)
- **WorldModelSnapshot**: Immutable snapshot of world state at a specific version
- **WorldModel**: Versioned belief state with DAG structure
- Features:
  - Version management with parent tracking
  - Fork/branch support for A/B testing
  - Serialization and snapshot creation
  - Rule storage and management

#### 2. Rules (`rules/`)
- **Rule**: Base class with conditions, order constraints, and lifecycle metadata
- **RuleCondition**: Conditions that must be met for rule application
- **RuleMetadata**: Success/failure tracking, confidence scoring, lifecycle status
- **PreconditionRule**: Enforces required state before actions
- **OrderRule**: Enforces action ordering
- **RuleSet**: Collection of rules with validation logic

#### 3. Actions and Execution (`core/action.py`, `core/engine.py`)
- **Action**: Immutable action definition with name and parameters
- **ActionNode**: Node in DAG with dependencies and status
- **ActionDAG**: Directed acyclic graph of actions
- **DagBuilder**: Constructs DAG from rules and goals
- **Engine**: Executes DAG with rule validation

#### 4. Tracing (`core/trace.py`)
- **ExecutionEvent**: Single event in execution trace
- **BuildTrace**: Records how DAG nodes were constructed from rules
- **ExecutionReport**: Complete execution report with status, events, and traces

#### 5. Reflection (`core/reflection.py`)
- **ReflectionV1**: Rule-based failure analysis
  - Blame assignment
  - Minimal patch generation (add condition, add constraint, narrow scope)
- **ReflectionV2**: LLM-assisted reflection
  - Structured patch proposals
  - Safety validation

#### 6. Simulation (`simulation/simulator.py`)
- **WorldModelDiff**: Difference between two WorldModel versions
- **SimulationMetrics**: Success rate, execution time, complexity metrics
- **SimulationResult**: A/B comparison results
- **Simulator**: Runs A/B tests on WorldModel versions

#### 7. Evolution Control (`core/evolution_control.py`)
- **PatchBudget**: Global constraints on patch acceptance
- **ParetoFrontier**: Multi-objective optimization
- **RuleExplosionController**: Controls rule growth
  - Evaluates proposals against Pareto frontier
  - Enforces budget constraints
  - Tracks patch history

#### 8. Patch Application (`core/patch_applier.py`)
- **PatchApplier**: ONLY component that can modify WorldModel
- Operations:
  - Apply patches with validation
  - Create new versions
  - Maintain version history
  - Rollback support
  - Audit trail

#### 9. Rule Lifecycle (`core/rule_stats_updater.py`)
- **RuleStatsUpdater**: Manages rule lifecycle
- Features:
  - Confidence decay over time
  - Status transitions (ACTIVE → COOLDOWN → DEPRECATED)
  - Automatic cleanup of deprecated rules
  - Health reporting

#### 10. Integration (`core/browser4agi.py`)
- **Browser4AGI**: Main orchestrator
- Implements complete self-evolution loop:
  1. Execute tasks with current model
  2. Reflect on failures
  3. Generate patch proposals
  4. Simulate patches
  5. Apply patches within budget
  6. Update rule statistics

### Agent Components

#### Planner (`agent/planner.py`)
- Generates ActionDAG for goals
- Implements different planning strategies:
  - Browse tasks
  - Search tasks
  - Extraction tasks
  - Generic tasks
- Supports replanning after failures

#### Executor (`agent/executor.py`)
- Executes actions using tools
- Manages tool registry
- Converts actions to observations
- Handles DAG execution with dependency resolution

### Tools

#### BrowserTool (`tools/browser.py`)
- Simulated browser operations:
  - Navigate to URLs
  - Click elements
  - Fill forms
  - Wait for elements
  - Extract content
  - Execute JavaScript
  - Manage cookies
  - Take screenshots

#### FileSystemTool (`tools/filesystem.py`)
- File operations:
  - Read/write files
  - JSON serialization
  - Directory listing
  - File existence checks

### LLM Integration

#### LLMAdvisor (`llm/advisor.py`)
- Acts as advisor, not decision maker
- Proposes patches (never modifies WorldModel directly)
- Validates proposals for safety
- Mock implementation for testing

## Key Design Principles

### 1. Execution First
- Everything starts with executable Tool DAG
- Rules are concrete and verifiable
- No abstract planning without execution capability

### 2. Failure Driven Learning
- Only failures trigger evolution
- Successes reinforce existing rules
- Blame assignment identifies responsible rules

### 3. Simulation Before Mutation
- All changes validated through A/B simulation
- Baseline vs patched comparison
- Metrics-driven decision making

### 4. Global Constraint Over Local Optimal
- Patch budget prevents rule explosion
- Pareto frontier for multi-objective optimization
- System-wide consistency over local fixes

### 5. Explicit Version Control
- Every change creates new immutable version
- Complete audit trail
- Rollback capability
- Fork/branch support

## Evolution Loop

```
1. Execute tasks with current WorldModel
   ↓
2. Collect ExecutionReports
   ↓
3. Identify failures
   ↓
4. Reflection (v1 or v2)
   ↓
5. Generate PatchProposals
   ↓
6. For each proposal:
   - Apply to fork of WorldModel
   - Run A/B simulation
   - Calculate metrics
   ↓
7. RuleExplosionController
   - Build Pareto frontier
   - Filter by budget
   ↓
8. PatchApplier
   - Apply accepted patches
   - Create new version
   - Record lineage
   ↓
9. RuleStatsUpdater
   - Update confidence
   - Apply decay
   - Manage lifecycle
   ↓
10. Continue with new WorldModel
```

## Usage Examples

### Basic Usage
```python
from core.browser4agi import Browser4AGI

# Initialize system
system = Browser4AGI(initial_version="v0")

# Execute task
report = system.execute_task("Browse to example.com")

# Check status
print(f"Status: {report.status}")
print(f"State: {system.get_system_state()}")
```

### Self-Evolution
```python
# Define test tasks
test_tasks = [
    "Navigate to example.com",
    "Search for data",
    "Extract content"
]

# Run evolution step
result = system.self_evolve_step(test_tasks)

print(f"Patches applied: {result['patches_applied']}")
print(f"New version: {result['current_version']}")
```

### Version Management
```python
# Current version
current = system.world_model.version

# Rollback
system.rollback_to_version("v0")

# Export model
system.export_model("model.json")
```

## Extension Points

### Adding New Rules
```python
from rules.rule import Rule

class CustomRule(Rule):
    def check(self, action, world_model):
        # Custom validation logic
        pass
```

### Adding New Tools
```python
# Register custom tool
executor.register_tool("custom", CustomTool())

# Use in actions
action = Action("custom.method", {"param": "value"})
```

### Custom Reflection Logic
```python
from core.reflection import ReflectionV1

class CustomReflection(ReflectionV1):
    def _generate_fix_patch(self, report, failed_rules):
        # Custom patch generation
        pass
```

## Testing

Run examples:
```bash
cd /home/runner/work/browser4agi/browser4agi
PYTHONPATH=/home/runner/work/browser4agi/browser4agi python3 examples/simple_browse.py
PYTHONPATH=/home/runner/work/browser4agi/browser4agi python3 examples/comprehensive_example.py
```

## Future Enhancements

1. **Real Browser Integration**
   - Playwright/Selenium integration
   - Actual DOM manipulation
   - Real network requests

2. **LLM Integration**
   - OpenAI/Anthropic API
   - Structured output parsing
   - Multi-turn reasoning

3. **Persistence**
   - Database backend for WorldModel history
   - Rule repository
   - Execution history

4. **Visualization**
   - WorldModel version DAG
   - Rule confidence heatmap
   - Execution trace visualization
   - Pareto frontier plots

5. **Advanced Planning**
   - PDDL-based planning
   - Monte Carlo tree search
   - Learned heuristics

6. **Distributed Execution**
   - Parallel task execution
   - Distributed simulation
   - Sharded rule sets

## License

See repository LICENSE file.
