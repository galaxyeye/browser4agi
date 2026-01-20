from typing import List, Optional
from core.action import Action, ActionDAG, ActionNode, ActionStatus
from core.world_model import WorldModel
from rules.rule_set import RuleSet
import uuid


class Planner:
    """Plans action sequences to achieve goals"""
    
    def __init__(self, world_model: WorldModel, rule_set: RuleSet):
        self.world_model = world_model
        self.rule_set = rule_set
    
    def plan(self, goal: str) -> ActionDAG:
        """
        Generate action DAG for achieving goal.
        Uses rules to determine necessary actions and dependencies.
        """
        dag = ActionDAG()
        
        # Parse goal to determine required actions
        # This is a simplified planner - real implementation would use
        # more sophisticated planning algorithms
        
        if "browse" in goal.lower() or "navigate" in goal.lower():
            # Browser navigation task
            self._plan_browse_task(dag, goal)
        elif "search" in goal.lower():
            # Search task
            self._plan_search_task(dag, goal)
        elif "extract" in goal.lower() or "scrape" in goal.lower():
            # Data extraction task
            self._plan_extraction_task(dag, goal)
        else:
            # Generic task
            self._plan_generic_task(dag, goal)
        
        return dag
    
    def _plan_browse_task(self, dag: ActionDAG, goal: str):
        """Plan a browsing task"""
        # 1. Open URL
        open_node = ActionNode(
            action=Action("browser.open", {"url": "https://example.com"}),
            node_id=f"node_{uuid.uuid4().hex[:8]}"
        )
        dag.add_node(open_node)
        
        # 2. Wait for page load
        wait_node = ActionNode(
            action=Action("browser.wait_for", {"selector": "body"}),
            node_id=f"node_{uuid.uuid4().hex[:8]}",
            dependencies=[open_node.node_id]
        )
        dag.add_node(wait_node)
    
    def _plan_search_task(self, dag: ActionDAG, goal: str):
        """Plan a search task"""
        # 1. Open search page
        open_node = ActionNode(
            action=Action("browser.open", {"url": "https://example.com/search"}),
            node_id=f"node_{uuid.uuid4().hex[:8]}"
        )
        dag.add_node(open_node)
        
        # 2. Fill search box
        fill_node = ActionNode(
            action=Action("browser.fill", {"selector": "#search", "value": goal}),
            node_id=f"node_{uuid.uuid4().hex[:8]}",
            dependencies=[open_node.node_id]
        )
        dag.add_node(fill_node)
        
        # 3. Click search button
        click_node = ActionNode(
            action=Action("browser.click", {"selector": "#search-button"}),
            node_id=f"node_{uuid.uuid4().hex[:8]}",
            dependencies=[fill_node.node_id]
        )
        dag.add_node(click_node)
    
    def _plan_extraction_task(self, dag: ActionDAG, goal: str):
        """Plan a data extraction task"""
        # 1. Navigate to page
        open_node = ActionNode(
            action=Action("browser.open", {"url": "https://example.com/data"}),
            node_id=f"node_{uuid.uuid4().hex[:8]}"
        )
        dag.add_node(open_node)
        
        # 2. Extract data
        extract_node = ActionNode(
            action=Action("browser.extract", {"selector": ".data-container"}),
            node_id=f"node_{uuid.uuid4().hex[:8]}",
            dependencies=[open_node.node_id]
        )
        dag.add_node(extract_node)
        
        # 3. Save to file
        save_node = ActionNode(
            action=Action("filesystem.write", {"path": "data.txt", "content": "extracted"}),
            node_id=f"node_{uuid.uuid4().hex[:8]}",
            dependencies=[extract_node.node_id]
        )
        dag.add_node(save_node)
    
    def _plan_generic_task(self, dag: ActionDAG, goal: str):
        """Plan a generic task"""
        # Create a single action node
        node = ActionNode(
            action=Action("generic.execute", {"goal": goal}),
            node_id=f"node_{uuid.uuid4().hex[:8]}"
        )
        dag.add_node(node)
    
    def replan(self, failed_dag: ActionDAG, error: str) -> ActionDAG:
        """
        Replan after failure.
        Analyzes failure and creates alternative plan.
        """
        # Create new DAG with alternative approach
        new_dag = ActionDAG()
        
        # Copy successful nodes
        for node_id, node in failed_dag.nodes.items():
            if node.status == ActionStatus.SUCCESS:
                new_dag.add_node(node)
        
        # Add recovery actions
        recovery_node = ActionNode(
            action=Action("recovery.retry", {"error": error}),
            node_id=f"node_{uuid.uuid4().hex[:8]}"
        )
        new_dag.add_node(recovery_node)
        
        return new_dag
