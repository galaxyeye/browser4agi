from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
import time


class RuleViolation(Exception):
    """Exception raised when a rule check fails"""
    pass


class RuleStatus(Enum):
    """Rule lifecycle status"""
    ACTIVE = "active"
    COOLDOWN = "cooldown"
    DEPRECATED = "deprecated"


@dataclass
class RuleCondition:
    """Condition that must be met for rule to apply"""
    field: str
    operator: str  # 'eq', 'ne', 'gt', 'lt', 'contains', 'exists'
    value: Any
    
    def evaluate(self, world_model) -> bool:
        """Evaluate condition against world model state"""
        state_value = world_model.state.get(self.field)
        
        if self.operator == 'exists':
            return state_value is not None
        if self.operator == 'eq':
            return state_value == self.value
        if self.operator == 'ne':
            return state_value != self.value
        if self.operator == 'gt':
            return state_value > self.value
        if self.operator == 'lt':
            return state_value < self.value
        if self.operator == 'contains':
            return self.value in state_value if state_value else False
        
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field": self.field,
            "operator": self.operator,
            "value": self.value
        }


@dataclass
class RuleMetadata:
    """Metadata for rule lifecycle management"""
    created_at: float = field(default_factory=time.time)
    last_success: Optional[float] = None
    last_failure: Optional[float] = None
    success_count: int = 0
    failure_count: int = 0
    confidence: float = 1.0
    status: RuleStatus = RuleStatus.ACTIVE
    specialization_score: float = 0.0  # Higher = more specialized
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "created_at": self.created_at,
            "last_success": self.last_success,
            "last_failure": self.last_failure,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "confidence": self.confidence,
            "status": self.status.value,
            "specialization_score": self.specialization_score
        }


class Rule:
    """
    Base rule class with conditions, constraints, and lifecycle management
    """
    
    def __init__(
        self, 
        rule_id: str,
        description: str = "",
        conditions: Optional[List[RuleCondition]] = None,
        order_constraints: Optional[List[str]] = None
    ):
        self.id = rule_id
        self.description = description
        self.conditions = conditions or []
        self.order_constraints = order_constraints or []  # List of rule IDs that must execute before
        self.metadata = RuleMetadata()
    
    def check(self, action, world_model):
        """Check if rule is satisfied - to be implemented by subclasses"""
        raise NotImplementedError
    
    def applies_to(self, action, world_model) -> bool:
        """Check if rule applies to current context"""
        # Check if rule is active
        if self.metadata.status == RuleStatus.DEPRECATED:
            return False
        
        # Check conditions
        for condition in self.conditions:
            if not condition.evaluate(world_model):
                return False
        
        return True
    
    def record_success(self):
        """Record successful application"""
        self.metadata.success_count += 1
        self.metadata.last_success = time.time()
        # Increase confidence
        self.metadata.confidence = min(1.0, self.metadata.confidence + 0.1)
    
    def record_failure(self):
        """Record failed application"""
        self.metadata.failure_count += 1
        self.metadata.last_failure = time.time()
        # Decrease confidence
        self.metadata.confidence = max(0.0, self.metadata.confidence - 0.15)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize rule to dictionary"""
        return {
            "id": self.id,
            "description": self.description,
            "conditions": [c.to_dict() for c in self.conditions],
            "order_constraints": self.order_constraints,
            "metadata": self.metadata.to_dict()
        }


class PreconditionRule(Rule):
    """Rule that enforces preconditions before action"""
    
    def __init__(self, rule_id: str, required_state: Dict[str, Any], **kwargs):
        super().__init__(rule_id, **kwargs)
        self.required_state = required_state
    
    def check(self, action, world_model):
        """Verify all required state exists"""
        for key, expected_value in self.required_state.items():
            actual_value = world_model.state.get(key)
            if actual_value != expected_value:
                raise RuleViolation(
                    f"Precondition failed: expected {key}={expected_value}, got {actual_value}"
                )
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["required_state"] = self.required_state
        return data


class OrderRule(Rule):
    """Rule that enforces action ordering"""
    
    def __init__(self, rule_id: str, action_name: str, must_follow: List[str], **kwargs):
        super().__init__(rule_id, **kwargs)
        self.action_name = action_name
        self.must_follow = must_follow
    
    def check(self, action, world_model):
        """Verify prerequisite actions have been executed"""
        executed_actions = world_model.state.get('executed_actions', [])
        
        if action.name == self.action_name:
            for prereq in self.must_follow:
                if prereq not in executed_actions:
                    raise RuleViolation(
                        f"Order violation: {self.action_name} requires {prereq} to execute first"
                    )
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["action_name"] = self.action_name
        data["must_follow"] = self.must_follow
        return data
