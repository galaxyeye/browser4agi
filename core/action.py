from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum


class ActionStatus(Enum):
    """Status of action execution"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class Action:
    """Represents an action to be executed"""
    name: str
    params: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"{self.name}({', '.join(f'{k}={v}' for k, v in self.params.items())})"


@dataclass
class ActionNode:
    """A node in the action DAG with dependencies"""
    action: Action
    node_id: str
    dependencies: List[str] = field(default_factory=list)  # IDs of nodes this depends on
    status: ActionStatus = ActionStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    
    def can_execute(self, executed_nodes: set) -> bool:
        """Check if all dependencies are satisfied"""
        return all(dep_id in executed_nodes for dep_id in self.dependencies)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "action": str(self.action),
            "dependencies": self.dependencies,
            "status": self.status.value,
            "result": str(self.result) if self.result else None,
            "error": self.error
        }


class ActionDAG:
    """Directed Acyclic Graph of actions"""
    
    def __init__(self):
        self.nodes: Dict[str, ActionNode] = {}
        self.execution_order: List[str] = []
    
    def add_node(self, node: ActionNode):
        """Add a node to the DAG"""
        self.nodes[node.node_id] = node
    
    def add_dependency(self, node_id: str, depends_on: str):
        """Add a dependency between nodes"""
        if node_id in self.nodes:
            if depends_on not in self.nodes[node_id].dependencies:
                self.nodes[node_id].dependencies.append(depends_on)
    
    def get_executable_nodes(self, executed_nodes: set) -> List[ActionNode]:
        """Get all nodes ready to execute"""
        executable = []
        for node in self.nodes.values():
            if node.status == ActionStatus.PENDING and node.can_execute(executed_nodes):
                executable.append(node)
        return executable
    
    def topological_sort(self) -> List[str]:
        """Return topologically sorted node IDs"""
        # Simple topological sort using DFS
        visited = set()
        stack = []
        
        def visit(node_id: str):
            if node_id in visited:
                return
            visited.add(node_id)
            node = self.nodes[node_id]
            for dep_id in node.dependencies:
                if dep_id in self.nodes:
                    visit(dep_id)
            stack.append(node_id)
        
        for node_id in self.nodes:
            visit(node_id)
        
        return stack
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "execution_order": self.execution_order
        }
