from typing import Dict, Any, Optional
from core.action import Action, ActionDAG, ActionNode, ActionStatus
from core.observation import Observation
from tools.browser import BrowserTool
from tools.filesystem import FileSystemTool


class Executor:
    """Executes actions using appropriate tools"""
    
    def __init__(self):
        self.browser = BrowserTool()
        self.filesystem = FileSystemTool()
        self.tools = {
            "browser": self.browser,
            "filesystem": self.filesystem
        }
    
    def execute(self, actions: list) -> list:
        """Execute list of actions (legacy interface)"""
        results = []
        for action in actions:
            result = self.execute_action(action)
            results.append(result)
        return results
    
    def execute_action(self, action: Action) -> Observation:
        """Execute a single action and return observation"""
        # Parse action name to determine tool and method
        parts = action.name.split(".")
        
        if len(parts) >= 2:
            tool_name = parts[0]
            method_name = parts[1]
            
            tool = self.tools.get(tool_name)
            if tool and hasattr(tool, method_name):
                method = getattr(tool, method_name)
                result = method(**action.params)
                
                return Observation(
                    kind=f"{tool_name}_result",
                    payload=result
                )
        
        # Fallback for unknown actions
        return Observation(
            kind="error",
            payload={"error": f"Unknown action: {action.name}"}
        )
    
    def execute_dag(self, dag: ActionDAG) -> Dict[str, Observation]:
        """Execute entire action DAG"""
        observations = {}
        executed_nodes = set()
        
        # Get execution order
        execution_order = dag.topological_sort()
        
        for node_id in execution_order:
            node = dag.nodes[node_id]
            
            # Check dependencies
            if not node.can_execute(executed_nodes):
                node.status = ActionStatus.SKIPPED
                continue
            
            # Execute action
            node.status = ActionStatus.RUNNING
            
            try:
                observation = self.execute_action(node.action)
                node.status = ActionStatus.SUCCESS
                node.result = observation.payload
                observations[node_id] = observation
                executed_nodes.add(node_id)
                
            except Exception as e:
                node.status = ActionStatus.FAILED
                node.error = str(e)
                observations[node_id] = Observation(
                    kind="error",
                    payload={"error": str(e)}
                )
        
        return observations
    
    def get_tool(self, name: str) -> Optional[Any]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def register_tool(self, name: str, tool: Any):
        """Register a new tool"""
        self.tools[name] = tool
