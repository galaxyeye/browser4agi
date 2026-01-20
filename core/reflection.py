"""
DAG Reflection system for analyzing failures and generating patches
"""
from typing import List, Optional
from core.trace import ExecutionReport, ExecutionStatus
from rules.patch import PatchProposal, RulePatch, PatchType
from rules.rule_set import RuleSet
import uuid


class ReflectionV1:
    """
    Rule-based reflection that analyzes execution reports
    and generates minimal patches
    """
    
    def __init__(self, rule_set: RuleSet):
        self.rule_set = rule_set
    
    def analyze_failure(self, report: ExecutionReport) -> Optional[PatchProposal]:
        """Analyze execution report and generate patch proposal"""
        if report.status == ExecutionStatus.SUCCESS:
            return None
        
        # Extract failed rules
        failed_rule_ids = report.get_failed_rules()
        
        if not failed_rule_ids:
            # Failure but no rule blamed - suggest adding precondition
            return self._generate_precondition_patch(report)
        
        # Analyze why rule failed
        return self._generate_fix_patch(report, failed_rule_ids)
    
    def _generate_precondition_patch(self, report: ExecutionReport) -> PatchProposal:
        """Generate patch to add missing precondition"""
        patches = [
            RulePatch(
                patch_type=PatchType.ADD_RULE,
                rule_id=f"precond_{uuid.uuid4().hex[:8]}",
                changes={
                    "type": "precondition",
                    "description": f"Add precondition for {report.task_id}"
                },
                reason="Missing precondition caused failure"
            )
        ]
        
        return PatchProposal(
            proposal_id=f"proposal_{uuid.uuid4().hex[:8]}",
            patches=patches,
            description="Add missing precondition rule",
            source="reflection_v1"
        )
    
    def _generate_fix_patch(
        self, 
        report: ExecutionReport, 
        failed_rule_ids: List[str]
    ) -> PatchProposal:
        """Generate patch to fix failed rule"""
        patches = []
        
        for rule_id in failed_rule_ids:
            rule = self.rule_set.get_rule(rule_id)
            if not rule:
                continue
            
            # Strategy 1: Narrow scope by adding conditions
            if len(rule.conditions) < 3:  # Don't make it too specialized
                patches.append(
                    RulePatch(
                        patch_type=PatchType.ADD_CONDITION,
                        rule_id=rule_id,
                        changes={
                            "condition": {
                                "field": "context",
                                "operator": "exists"
                            }
                        },
                        reason=f"Narrow scope of rule {rule_id}"
                    )
                )
            
            # Strategy 2: Add order constraint
            if len(rule.order_constraints) < 2:
                patches.append(
                    RulePatch(
                        patch_type=PatchType.ADD_ORDER_CONSTRAINT,
                        rule_id=rule_id,
                        changes={
                            "must_follow": ["initialization"]
                        },
                        reason=f"Add ordering constraint to {rule_id}"
                    )
                )
        
        if not patches:
            # Last resort: remove failing rule
            for rule_id in failed_rule_ids:
                patches.append(
                    RulePatch(
                        patch_type=PatchType.REMOVE_RULE,
                        rule_id=rule_id,
                        changes={},
                        reason=f"Remove failing rule {rule_id}"
                    )
                )
        
        return PatchProposal(
            proposal_id=f"proposal_{uuid.uuid4().hex[:8]}",
            patches=patches,
            description=f"Fix failed rules: {', '.join(failed_rule_ids)}",
            source="reflection_v1"
        )


class ReflectionV2:
    """
    LLM-assisted reflection for more sophisticated patch generation
    """
    
    def __init__(self, rule_set: RuleSet, llm_advisor):
        self.rule_set = rule_set
        self.llm_advisor = llm_advisor
    
    def analyze_failure(self, report: ExecutionReport) -> Optional[PatchProposal]:
        """Use LLM to analyze failure and propose patches"""
        # LLM generates structured patch proposals
        # but does not modify WorldModel directly
        proposal = self.llm_advisor.propose_rule_patch(report)
        
        if proposal:
            # Validate that proposal follows constraints
            if self._validate_proposal(proposal):
                return proposal
        
        # Fallback to v1 if LLM proposal invalid
        v1 = ReflectionV1(self.rule_set)
        return v1.analyze_failure(report)
    
    def _validate_proposal(self, proposal: PatchProposal) -> bool:
        """Ensure LLM proposal follows system constraints"""
        # Check that patches only use whitelisted operations
        allowed_types = {pt for pt in PatchType}
        
        for patch in proposal.patches:
            if patch.patch_type not in allowed_types:
                return False
            
            # Ensure patches don't try to execute arbitrary code
            if 'code' in patch.changes or 'exec' in patch.changes:
                return False
        
        return True
