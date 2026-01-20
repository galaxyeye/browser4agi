from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum
import time


class PatchType(Enum):
    """Type of rule patch"""
    ADD_RULE = "add_rule"
    MODIFY_RULE = "modify_rule"
    REMOVE_RULE = "remove_rule"
    ADD_CONDITION = "add_condition"
    ADD_ORDER_CONSTRAINT = "add_order_constraint"
    NARROW_SCOPE = "narrow_scope"


@dataclass
class RulePatch:
    """Represents a change to a rule"""
    patch_type: PatchType
    rule_id: str
    changes: Dict[str, Any]
    reason: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "patch_type": self.patch_type.value,
            "rule_id": self.rule_id,
            "changes": self.changes,
            "reason": self.reason
        }


@dataclass
class PatchMetrics:
    """Metrics for evaluating patch effectiveness"""
    success_delta: float = 0.0  # Change in success rate
    rule_count_delta: int = 0  # Change in number of rules
    complexity_delta: float = 0.0  # Change in overall complexity
    specialization_score: float = 0.0  # How specialized the patch is
    
    def dominates(self, other: 'PatchMetrics') -> bool:
        """Check if this patch dominates another (Pareto)"""
        better_in_one = False
        worse_in_any = False
        
        # We want to maximize success_delta, minimize rule_count_delta and specialization
        if self.success_delta > other.success_delta:
            better_in_one = True
        elif self.success_delta < other.success_delta:
            worse_in_any = True
        
        if self.rule_count_delta < other.rule_count_delta:
            better_in_one = True
        elif self.rule_count_delta > other.rule_count_delta:
            worse_in_any = True
        
        if self.specialization_score < other.specialization_score:
            better_in_one = True
        elif self.specialization_score > other.specialization_score:
            worse_in_any = True
        
        return better_in_one and not worse_in_any
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success_delta": self.success_delta,
            "rule_count_delta": self.rule_count_delta,
            "complexity_delta": self.complexity_delta,
            "specialization_score": self.specialization_score
        }


@dataclass
class PatchProposal:
    """A proposed set of patches with metadata"""
    proposal_id: str
    patches: List[RulePatch]
    description: str
    source: str  # "reflection_v1", "reflection_v2", etc.
    metrics: Optional[PatchMetrics] = None
    created_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "patches": [p.to_dict() for p in self.patches],
            "description": self.description,
            "source": self.source,
            "metrics": self.metrics.to_dict() if self.metrics else None,
            "created_at": self.created_at
        }


class RulePatchProposal:
    """Legacy class for backward compatibility"""
    
    def __init__(self, description: str, diff):
        self.description = description
        self.diff = diff
    
    def to_proposal(self, proposal_id: str) -> PatchProposal:
        """Convert to new PatchProposal format"""
        return PatchProposal(
            proposal_id=proposal_id,
            patches=[],
            description=self.description,
            source="legacy"
        )
