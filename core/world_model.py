from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
import copy


@dataclass
class WorldModelSnapshot:
    """Immutable snapshot of WorldModel at a specific version"""
    version: str
    parent_version: Optional[str]
    rules: List[Any]  # Will be Rule objects
    state: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "parent_version": self.parent_version,
            "rules": [r.to_dict() if hasattr(r, 'to_dict') else str(r) for r in self.rules],
            "state": dict(self.state),
            "metadata": dict(self.metadata)
        }


class WorldModel:
    """
    Explicit, versioned belief of the environment.
    Must be serializable and comparable.
    Supports version DAG for branching and rollback.
    """

    def __init__(self, version: str, parent_version: Optional[str] = None, rules: Optional[List[Any]] = None):
        self.version = version
        self.parent_version = parent_version
        self.rules = rules or []
        self.state = {}
        self.metadata = {}
        self._snapshots: Dict[str, WorldModelSnapshot] = {}

    def update(self, observation):
        """Update world state based on observation"""
        self.state[observation.kind] = observation.payload

    def add_rule(self, rule):
        """Add a rule to the world model"""
        self.rules.append(rule)

    def remove_rule(self, rule_id: str):
        """Remove a rule by ID"""
        self.rules = [r for r in self.rules if getattr(r, 'id', None) != rule_id]

    def snapshot(self) -> WorldModelSnapshot:
        """Create an immutable snapshot of current state"""
        snap = WorldModelSnapshot(
            version=self.version,
            parent_version=self.parent_version,
            rules=copy.deepcopy(self.rules),
            state=copy.deepcopy(self.state),
            metadata=copy.deepcopy(self.metadata)
        )
        self._snapshots[self.version] = snap
        return snap

    def get_snapshot(self, version: str) -> Optional[WorldModelSnapshot]:
        """Retrieve a specific version snapshot"""
        return self._snapshots.get(version)

    def fork(self, new_version: str) -> 'WorldModel':
        """Create a new WorldModel branching from current version"""
        new_model = WorldModel(
            version=new_version,
            parent_version=self.version,
            rules=copy.deepcopy(self.rules)
        )
        new_model.state = copy.deepcopy(self.state)
        new_model.metadata = copy.deepcopy(self.metadata)
        new_model._snapshots = self._snapshots.copy()
        return new_model

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "version": self.version,
            "parent_version": self.parent_version,
            "rules": [r.to_dict() if hasattr(r, 'to_dict') else str(r) for r in self.rules],
            "state": dict(self.state),
            "metadata": dict(self.metadata)
        }
