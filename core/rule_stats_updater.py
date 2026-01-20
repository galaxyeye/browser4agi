"""
RuleStatsUpdater - Manages rule lifecycle and confidence decay
"""
import time
from typing import List
from rules.rule import Rule, RuleStatus
from rules.rule_set import RuleSet


class RuleStatsUpdater:
    """
    Updates rule statistics and manages lifecycle transitions.
    Implements confidence decay and automatic deprecation.
    """
    
    def __init__(
        self,
        decay_rate: float = 0.01,  # Confidence decay per day
        cooldown_threshold: float = 0.5,  # Confidence threshold for cooldown
        deprecate_threshold: float = 0.2,  # Confidence threshold for deprecation
        inactive_days_threshold: int = 30  # Days before considering rule inactive
    ):
        self.decay_rate = decay_rate
        self.cooldown_threshold = cooldown_threshold
        self.deprecate_threshold = deprecate_threshold
        self.inactive_days_threshold = inactive_days_threshold
    
    def update_all_rules(self, rule_set: RuleSet):
        """Update statistics for all rules in the set"""
        current_time = time.time()
        
        for rule in rule_set.rules:
            self._update_rule(rule, current_time)
    
    def _update_rule(self, rule: Rule, current_time: float):
        """Update a single rule's statistics"""
        # Apply time-based confidence decay
        self._apply_decay(rule, current_time)
        
        # Update status based on confidence
        self._update_status(rule, current_time)
    
    def _apply_decay(self, rule: Rule, current_time: float):
        """Apply confidence decay based on time since last success"""
        if rule.metadata.last_success is None:
            # Never succeeded - faster decay
            days_since_creation = (current_time - rule.metadata.created_at) / 86400
            decay = self.decay_rate * 2 * days_since_creation
        else:
            # Decay based on time since last success
            days_since_success = (current_time - rule.metadata.last_success) / 86400
            decay = self.decay_rate * days_since_success
        
        # Apply decay
        rule.metadata.confidence = max(0.0, rule.metadata.confidence - decay)
    
    def _update_status(self, rule: Rule, current_time: float):
        """Update rule status based on confidence and activity"""
        confidence = rule.metadata.confidence
        
        # Check if rule has been inactive
        days_inactive = self._get_inactive_days(rule, current_time)
        
        if confidence < self.deprecate_threshold or days_inactive > self.inactive_days_threshold:
            rule.metadata.status = RuleStatus.DEPRECATED
        
        elif confidence < self.cooldown_threshold:
            rule.metadata.status = RuleStatus.COOLDOWN
        
        else:
            rule.metadata.status = RuleStatus.ACTIVE
    
    def _get_inactive_days(self, rule: Rule, current_time: float) -> float:
        """Get number of days since rule was last used"""
        last_activity = max(
            rule.metadata.last_success or 0,
            rule.metadata.last_failure or 0
        )
        
        if last_activity == 0:
            # Use creation time
            last_activity = rule.metadata.created_at
        
        days = (current_time - last_activity) / 86400
        return days
    
    def cleanup_deprecated_rules(self, rule_set: RuleSet) -> int:
        """Remove deprecated rules from the set"""
        initial_count = len(rule_set.rules)
        
        # Keep only non-deprecated rules
        rule_set.rules = [
            r for r in rule_set.rules
            if r.metadata.status != RuleStatus.DEPRECATED
        ]
        
        removed_count = initial_count - len(rule_set.rules)
        return removed_count
    
    def revive_rule(self, rule: Rule):
        """Manually revive a rule (e.g., after validation)"""
        rule.metadata.confidence = min(1.0, rule.metadata.confidence + 0.3)
        rule.metadata.status = RuleStatus.ACTIVE
        rule.metadata.last_success = time.time()
    
    def get_rule_health_report(self, rule_set: RuleSet) -> dict:
        """Generate health report for all rules"""
        active = 0
        cooldown = 0
        deprecated = 0
        
        avg_confidence = 0.0
        low_confidence_rules = []
        
        for rule in rule_set.rules:
            if rule.metadata.status == RuleStatus.ACTIVE:
                active += 1
            elif rule.metadata.status == RuleStatus.COOLDOWN:
                cooldown += 1
            elif rule.metadata.status == RuleStatus.DEPRECATED:
                deprecated += 1
            
            avg_confidence += rule.metadata.confidence
            
            if rule.metadata.confidence < self.cooldown_threshold:
                low_confidence_rules.append({
                    "id": rule.id,
                    "confidence": rule.metadata.confidence,
                    "status": rule.metadata.status.value
                })
        
        total = len(rule_set.rules)
        avg_confidence = avg_confidence / total if total > 0 else 0.0
        
        return {
            "total_rules": total,
            "active": active,
            "cooldown": cooldown,
            "deprecated": deprecated,
            "avg_confidence": avg_confidence,
            "low_confidence_rules": low_confidence_rules
        }
