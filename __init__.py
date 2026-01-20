"""
browser4agi - A Self-Evolving Browser Agent Architecture

Main components:
- WorldModel: Versioned world representation
- Engine: Execution engine with DAG support
- Rules: Rule system with lifecycle management
- Reflection: Failure analysis and patch generation
- Simulation: A/B testing for patches
- Evolution Control: Budget and Pareto optimization
- PatchApplier: Safe WorldModel mutation
"""

__version__ = "0.1.0"

from core.browser4agi import Browser4AGI
from core.world_model import WorldModel, WorldModelSnapshot
from core.engine import Engine, DagBuilder
from core.action import Action, ActionDAG, ActionNode
from core.observation import Observation
from core.trace import ExecutionReport, ExecutionStatus, BuildTrace
from rules.rule import Rule, PreconditionRule, OrderRule, RuleStatus
from rules.rule_set import RuleSet
from rules.patch import PatchProposal, RulePatch, PatchType
from simulation.simulator import Simulator, SimulationResult
from agent.planner import Planner
from agent.executor import Executor

__all__ = [
    "Browser4AGI",
    "WorldModel",
    "WorldModelSnapshot",
    "Engine",
    "DagBuilder",
    "Action",
    "ActionDAG",
    "ActionNode",
    "Observation",
    "ExecutionReport",
    "ExecutionStatus",
    "BuildTrace",
    "Rule",
    "PreconditionRule",
    "OrderRule",
    "RuleStatus",
    "RuleSet",
    "PatchProposal",
    "RulePatch",
    "PatchType",
    "Simulator",
    "SimulationResult",
    "Planner",
    "Executor",
]
