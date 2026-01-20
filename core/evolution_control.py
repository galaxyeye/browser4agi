"""
Rule Explosion Control v2
Manages patch budget and Pareto frontier optimization
"""
from typing import List, Optional
from dataclasses import dataclass
from rules.patch import PatchProposal, PatchMetrics
from simulation.simulator import SimulationResult
import time


@dataclass
class PatchBudget:
    """Global budget constraints for patch acceptance"""
    max_patches_per_window: int = 10
    max_rule_count_increase: int = 20
    time_window_hours: float = 24.0
    
    def to_dict(self):
        return {
            "max_patches_per_window": self.max_patches_per_window,
            "max_rule_count_increase": self.max_rule_count_increase,
            "time_window_hours": self.time_window_hours
        }


@dataclass
class PatchRecord:
    """Record of an applied patch"""
    proposal_id: str
    applied_at: float
    rule_count_delta: int
    success_delta: float
    
    def to_dict(self):
        return {
            "proposal_id": self.proposal_id,
            "applied_at": self.applied_at,
            "rule_count_delta": self.rule_count_delta,
            "success_delta": self.success_delta
        }


class ParetoFrontier:
    """Manages Pareto frontier for multi-objective optimization"""
    
    def __init__(self):
        self.frontier: List[tuple[PatchProposal, PatchMetrics]] = []
    
    def add_proposal(self, proposal: PatchProposal, metrics: PatchMetrics):
        """Add proposal if it's non-dominated"""
        # Check if proposal is dominated by existing frontier
        for _, existing_metrics in self.frontier:
            if existing_metrics.dominates(metrics):
                return  # Dominated, don't add
        
        # Remove proposals dominated by new one
        self.frontier = [
            (p, m) for p, m in self.frontier
            if not metrics.dominates(m)
        ]
        
        # Add new proposal
        self.frontier.append((proposal, metrics))
    
    def get_best_proposals(self, count: int = 5) -> List[PatchProposal]:
        """Get top proposals from frontier"""
        # Sort by success delta (primary objective)
        sorted_frontier = sorted(
            self.frontier,
            key=lambda x: x[1].success_delta,
            reverse=True
        )
        return [p for p, m in sorted_frontier[:count]]
    
    def clear(self):
        """Clear the frontier"""
        self.frontier = []


class RuleExplosionController:
    """Controls rule growth and patch acceptance"""
    
    def __init__(self, budget: PatchBudget):
        self.budget = budget
        self.patch_history: List[PatchRecord] = []
        self.pareto = ParetoFrontier()
    
    def evaluate_proposals(
        self,
        proposals: List[tuple[PatchProposal, SimulationResult]]
    ) -> List[PatchProposal]:
        """Evaluate proposals and return acceptable ones"""
        # Clear previous frontier
        self.pareto.clear()
        
        # Build Pareto frontier
        for proposal, sim_result in proposals:
            metrics = PatchMetrics(
                success_delta=sim_result.get_success_delta(),
                rule_count_delta=sim_result.get_rule_count_delta(),
                complexity_delta=sim_result.get_complexity_delta(),
                specialization_score=self._calculate_specialization(proposal)
            )
            
            # Update proposal metrics
            proposal.metrics = metrics
            
            # Add to frontier if improvement
            if sim_result.is_improvement():
                self.pareto.add_proposal(proposal, metrics)
        
        # Get best proposals from frontier
        candidates = self.pareto.get_best_proposals()
        
        # Filter by budget constraints
        acceptable = []
        for proposal in candidates:
            if self._within_budget(proposal):
                acceptable.append(proposal)
        
        return acceptable
    
    def _within_budget(self, proposal: PatchProposal) -> bool:
        """Check if proposal is within budget constraints"""
        current_time = time.time()
        window_start = current_time - (self.budget.time_window_hours * 3600)
        
        # Get recent patches
        recent_patches = [
            p for p in self.patch_history
            if p.applied_at >= window_start
        ]
        
        # Check patch count limit
        if len(recent_patches) >= self.budget.max_patches_per_window:
            return False
        
        # Check rule count increase limit
        total_rule_increase = sum(p.rule_count_delta for p in recent_patches)
        proposal_rule_delta = proposal.metrics.rule_count_delta if proposal.metrics else 0
        
        if total_rule_increase + proposal_rule_delta > self.budget.max_rule_count_increase:
            return False
        
        return True
    
    def record_patch(self, proposal: PatchProposal):
        """Record that a patch was applied"""
        metrics = proposal.metrics
        record = PatchRecord(
            proposal_id=proposal.proposal_id,
            applied_at=time.time(),
            rule_count_delta=metrics.rule_count_delta if metrics else 0,
            success_delta=metrics.success_delta if metrics else 0.0
        )
        self.patch_history.append(record)
    
    def _calculate_specialization(self, proposal: PatchProposal) -> float:
        """Calculate how specialized a proposal is (0=general, 1=highly specialized)"""
        # Count how many constraints/conditions are added
        specialization = 0.0
        
        for patch in proposal.patches:
            if 'condition' in patch.changes:
                specialization += 0.3
            if 'must_follow' in patch.changes:
                specialization += 0.2
            if patch.patch_type.value == 'narrow_scope':
                specialization += 0.5
        
        return min(1.0, specialization)
    
    def get_budget_status(self) -> dict:
        """Get current budget utilization"""
        current_time = time.time()
        window_start = current_time - (self.budget.time_window_hours * 3600)
        
        recent_patches = [
            p for p in self.patch_history
            if p.applied_at >= window_start
        ]
        
        total_rule_increase = sum(p.rule_count_delta for p in recent_patches)
        
        return {
            "patches_used": len(recent_patches),
            "patches_available": self.budget.max_patches_per_window - len(recent_patches),
            "rule_count_increase": total_rule_increase,
            "rule_count_available": self.budget.max_rule_count_increase - total_rule_increase,
            "recent_patches": [p.to_dict() for p in recent_patches]
        }
