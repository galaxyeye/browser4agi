from typing import Optional, List
from core.action import ActionDAG, ActionNode, ActionStatus, Action
from core.trace import ExecutionReport, ExecutionStatus, ExecutionEvent, BuildTrace
from core.observation import Observation
from core.world_model import WorldModel
from rules.rule_set import RuleSet
from rules.rule import RuleViolation


class DagBuilder:
    """Builds Tool DAG from rules and task goal"""
    
    def __init__(self, rule_set: RuleSet):
        self.rule_set = rule_set
    
    def build(self, goal: str, world_model: WorldModel) -> tuple[ActionDAG, List[BuildTrace]]:
        """Build action DAG based on rules and goal"""
        dag = ActionDAG()
        build_traces = []
        
        # This is a simplified builder - in real implementation would use
        # more sophisticated planning based on rules
        # For now, return empty DAG as placeholder
        
        return dag, build_traces


class Engine:
    """Core execution engine for rule-driven Tool DAG"""
    
    def __init__(self, world_model: WorldModel, rule_set: RuleSet):
        self.world = world_model
        self.rules = rule_set
        self.dag_builder = DagBuilder(rule_set)

    def step(self, action: Action, observation: Observation):
        """Execute single action step (legacy interface)"""
        self.rules.validate(action, self.world)
        self.world.update(observation)
    
    def execute_dag(self, dag: ActionDAG, task_id: str) -> ExecutionReport:
        """Execute a complete action DAG"""
        report = ExecutionReport(
            task_id=task_id,
            status=ExecutionStatus.SUCCESS,
            world_model_version=self.world.version
        )
        
        executed_nodes = set()
        
        try:
            # Get topological order
            execution_order = dag.topological_sort()
            
            for node_id in execution_order:
                node = dag.nodes[node_id]
                
                # Check if dependencies are met
                if not node.can_execute(executed_nodes):
                    report.add_event(ExecutionEvent(
                        event_type="skip",
                        action=node.action,
                        error="Dependencies not met"
                    ))
                    node.status = ActionStatus.SKIPPED
                    continue
                
                # Update status
                node.status = ActionStatus.RUNNING
                
                # Validate with rules
                try:
                    self.rules.validate(node.action, self.world)
                    
                    # Execute action (placeholder - actual execution would call tools)
                    node.status = ActionStatus.SUCCESS
                    executed_nodes.add(node_id)
                    
                    report.add_event(ExecutionEvent(
                        event_type="success",
                        action=node.action
                    ))
                    
                    # Update world state
                    if 'executed_actions' not in self.world.state:
                        self.world.state['executed_actions'] = []
                    self.world.state['executed_actions'].append(node.action.name)
                    
                except RuleViolation as e:
                    node.status = ActionStatus.FAILED
                    node.error = str(e)
                    
                    report.add_event(ExecutionEvent(
                        event_type="failure",
                        action=node.action,
                        error=str(e)
                    ))
                    
                    # Stop execution on failure
                    report.complete(ExecutionStatus.FAILURE, str(e))
                    return report
            
            # All nodes executed successfully
            report.complete(ExecutionStatus.SUCCESS)
            
        except Exception as e:
            report.complete(ExecutionStatus.FAILURE, str(e))
        
        return report
    
    def plan_and_execute(self, goal: str, task_id: str) -> ExecutionReport:
        """Plan actions for goal and execute them"""
        # Build DAG from rules
        dag, build_traces = self.dag_builder.build(goal, self.world)
        
        # Execute DAG
        report = self.execute_dag(dag, task_id)
        
        # Attach build traces
        for trace in build_traces:
            report.add_build_trace(trace)
        
        return report
