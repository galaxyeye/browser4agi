from typing import List, Optional
from rules.rule import Rule, RuleViolation


class RuleSet:
    """Collection of rules with validation and selection logic"""
    
    def __init__(self, rules: Optional[List[Rule]] = None):
        self.rules = rules or []
    
    def add_rule(self, rule: Rule):
        """Add a rule to the set"""
        self.rules.append(rule)
    
    def remove_rule(self, rule_id: str):
        """Remove a rule by ID"""
        self.rules = [r for r in self.rules if r.id != rule_id]
    
    def get_rule(self, rule_id: str) -> Optional[Rule]:
        """Get a rule by ID"""
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        return None
    
    def validate(self, action, world_model):
        """Validate action against all applicable rules"""
        for rule in self.rules:
            if rule.applies_to(action, world_model):
                try:
                    rule.check(action, world_model)
                    rule.record_success()
                except RuleViolation as e:
                    rule.record_failure()
                    raise e
    
    def get_applicable_rules(self, action, world_model) -> List[Rule]:
        """Get all rules that apply to current context"""
        return [r for r in self.rules if r.applies_to(action, world_model)]
    
    def get_active_rules(self) -> List[Rule]:
        """Get all active (non-deprecated) rules"""
        from rules.rule import RuleStatus
        return [r for r in self.rules if r.metadata.status == RuleStatus.ACTIVE]
