from typing import Optional
from core.trace import ExecutionReport
from rules.patch import PatchProposal, RulePatch, PatchType
from llm.prompts import RULE_PATCH_PROMPT, REFLECTION_PROMPT
import uuid


class LLMAdvisor:
    """
    LLM is NOT in the execution loop.
    It only proposes plans or rule patches.
    LLM acts as an advisor, not a decision maker.
    """
    
    def __init__(self, model: Optional[str] = None):
        self.model = model or "mock"  # Mock LLM for now
    
    def propose_rule_patch(self, report: ExecutionReport) -> Optional[PatchProposal]:
        """
        Generate rule patch proposal based on execution report.
        LLM suggests patches but cannot directly modify WorldModel.
        """
        # Format prompt
        failed_rules = report.get_failed_rules()
        prompt = RULE_PATCH_PROMPT.format(
            task_id=report.task_id,
            status=report.status.value,
            error=report.error_message or "None",
            failed_rules=", ".join(failed_rules) if failed_rules else "None"
        )
        
        # In real implementation, this would call an actual LLM
        # For now, return a mock proposal
        if self.model == "mock":
            return self._mock_proposal(report)
        
        # Real LLM call would be here
        # response = self.call_llm(prompt)
        # return self.parse_response(response)
        
        return None
    
    def propose_plan(self, goal: str, world_state: dict) -> list:
        """
        Generate action plan for achieving goal.
        Returns list of action descriptions, not executable actions.
        """
        from llm.prompts import PLANNING_PROMPT
        
        prompt = PLANNING_PROMPT.format(
            goal=goal,
            world_state=str(world_state)
        )
        
        # Mock planning
        if self.model == "mock":
            return [
                {"action": "browser.open", "params": {"url": "https://example.com"}},
                {"action": "browser.extract", "params": {"selector": ".content"}}
            ]
        
        return []
    
    def analyze_failure(self, report: ExecutionReport) -> dict:
        """
        Analyze failure and provide insights.
        Returns structured analysis, not patches.
        """
        prompt = REFLECTION_PROMPT.format(
            task_id=report.task_id,
            status=report.status.value,
            error_message=report.error_message or "Unknown",
            events="\n".join(str(e) for e in report.events[:5]),
            build_traces="\n".join(str(t) for t in report.build_traces[:5])
        )
        
        # Mock analysis
        return {
            "root_cause": report.error_message or "Unknown error",
            "affected_rules": report.get_failed_rules(),
            "suggestion": "Add precondition or narrow scope",
            "confidence": 0.7
        }
    
    def _mock_proposal(self, report: ExecutionReport) -> PatchProposal:
        """Generate mock patch proposal for testing"""
        failed_rules = report.get_failed_rules()
        
        patches = []
        if failed_rules:
            # Suggest narrowing scope of failed rule
            for rule_id in failed_rules[:1]:  # Just first one
                patches.append(
                    RulePatch(
                        patch_type=PatchType.ADD_CONDITION,
                        rule_id=rule_id,
                        changes={
                            "condition": {
                                "field": "context_validated",
                                "operator": "eq",
                                "value": True
                            }
                        },
                        reason=f"Add validation check to rule {rule_id}"
                    )
                )
        else:
            # Suggest adding precondition
            patches.append(
                RulePatch(
                    patch_type=PatchType.ADD_RULE,
                    rule_id=f"precond_{uuid.uuid4().hex[:8]}",
                    changes={
                        "type": "precondition",
                        "required_state": {"initialized": True},
                        "description": "Ensure system is initialized"
                    },
                    reason="Add missing precondition"
                )
            )
        
        return PatchProposal(
            proposal_id=f"llm_proposal_{uuid.uuid4().hex[:8]}",
            patches=patches,
            description="LLM-suggested patch to fix execution failure",
            source="reflection_v2"
        )
    
    def validate_proposal(self, proposal: PatchProposal) -> bool:
        """
        Validate that a proposal follows system constraints.
        This is a safety check.
        """
        # Check for unsafe operations
        unsafe_keywords = ['exec', 'eval', 'code', '__']
        
        for patch in proposal.patches:
            # Check patch type is valid (already a PatchType enum)
            if not isinstance(patch.patch_type, PatchType):
                return False
            
            # Check for unsafe content in changes
            for key, value in patch.changes.items():
                if any(kw in str(key).lower() or kw in str(value).lower() 
                       for kw in unsafe_keywords):
                    return False
        
        return True
