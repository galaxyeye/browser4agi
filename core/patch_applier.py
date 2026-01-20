"""
PatchApplier - The only component allowed to modify WorldModel
"""
from typing import Optional, List, Tuple
import uuid
from core.world_model import WorldModel, WorldModelSnapshot
from rules.rule_set import RuleSet
from rules.patch import PatchProposal, RulePatch, PatchType
from rules.rule import Rule, RuleCondition, PreconditionRule, OrderRule
import copy


class PatchApplier:
    """
    The only component with write access to WorldModel.
    All modifications must go through this gateway.
    """
    
    def __init__(self):
        self.version_history: List[WorldModelSnapshot] = []
        self.patch_lineage: List[Tuple[str, str]] = []  # (version, patch_id)
    
    def apply_patch(
        self,
        world_model: WorldModel,
        rule_set: RuleSet,
        proposal: PatchProposal
    ) -> tuple[WorldModel, RuleSet]:
        """
        Apply a validated patch proposal to create new version.
        Returns new WorldModel and RuleSet (originals unchanged).
        """
        # Create snapshot of current version
        snapshot = world_model.snapshot()
        self.version_history.append(snapshot)
        
        # Create new version
        new_version = self._generate_version_id(world_model.version)
        new_world = world_model.fork(new_version)
        new_rules = RuleSet(copy.deepcopy(rule_set.rules))
        
        # Apply each patch
        for patch in proposal.patches:
            self._apply_single_patch(new_world, new_rules, patch)
        
        # Sync rules between world model and rule set
        new_world.rules = new_rules.rules
        
        # Record in lineage
        self.patch_lineage.append((new_version, proposal.proposal_id))
        
        return new_world, new_rules
    
    def _apply_single_patch(
        self,
        world_model: WorldModel,
        rule_set: RuleSet,
        patch: RulePatch
    ):
        """Apply a single patch operation"""
        if patch.patch_type == PatchType.ADD_RULE:
            self._add_rule(world_model, rule_set, patch)
        
        elif patch.patch_type == PatchType.REMOVE_RULE:
            self._remove_rule(world_model, rule_set, patch)
        
        elif patch.patch_type == PatchType.MODIFY_RULE:
            self._modify_rule(world_model, rule_set, patch)
        
        elif patch.patch_type == PatchType.ADD_CONDITION:
            self._add_condition(rule_set, patch)
        
        elif patch.patch_type == PatchType.ADD_ORDER_CONSTRAINT:
            self._add_order_constraint(rule_set, patch)
        
        elif patch.patch_type == PatchType.NARROW_SCOPE:
            self._narrow_scope(rule_set, patch)
    
    def _add_rule(self, world_model: WorldModel, rule_set: RuleSet, patch: RulePatch):
        """Add a new rule"""
        rule_type = patch.changes.get('type', 'generic')
        
        if rule_type == 'precondition':
            rule = PreconditionRule(
                rule_id=patch.rule_id,
                required_state=patch.changes.get('required_state', {}),
                description=patch.changes.get('description', '')
            )
        elif rule_type == 'order':
            rule = OrderRule(
                rule_id=patch.rule_id,
                action_name=patch.changes.get('action_name', ''),
                must_follow=patch.changes.get('must_follow', []),
                description=patch.changes.get('description', '')
            )
        else:
            rule = Rule(
                rule_id=patch.rule_id,
                description=patch.changes.get('description', '')
            )
        
        rule_set.add_rule(rule)
        world_model.add_rule(rule)
    
    def _remove_rule(self, world_model: WorldModel, rule_set: RuleSet, patch: RulePatch):
        """Remove a rule"""
        rule_set.remove_rule(patch.rule_id)
        world_model.remove_rule(patch.rule_id)
    
    def _modify_rule(self, world_model: WorldModel, rule_set: RuleSet, patch: RulePatch):
        """Modify an existing rule"""
        rule = rule_set.get_rule(patch.rule_id)
        if not rule:
            return
        
        # Update description if provided
        if 'description' in patch.changes:
            rule.description = patch.changes['description']
        
        # Update conditions if provided
        if 'conditions' in patch.changes:
            new_conditions = []
            for cond_dict in patch.changes['conditions']:
                new_conditions.append(RuleCondition(**cond_dict))
            rule.conditions = new_conditions
    
    def _add_condition(self, rule_set: RuleSet, patch: RulePatch):
        """Add a condition to existing rule"""
        rule = rule_set.get_rule(patch.rule_id)
        if not rule:
            return
        
        condition_data = patch.changes.get('condition', {})
        if condition_data:
            condition = RuleCondition(
                field=condition_data.get('field', 'unknown'),
                operator=condition_data.get('operator', 'exists'),
                value=condition_data.get('value')
            )
            rule.conditions.append(condition)
    
    def _add_order_constraint(self, rule_set: RuleSet, patch: RulePatch):
        """Add order constraint to existing rule"""
        rule = rule_set.get_rule(patch.rule_id)
        if not rule:
            return
        
        must_follow = patch.changes.get('must_follow', [])
        for constraint in must_follow:
            if constraint not in rule.order_constraints:
                rule.order_constraints.append(constraint)
    
    def _narrow_scope(self, rule_set: RuleSet, patch: RulePatch):
        """Narrow the scope of a rule by adding conditions"""
        rule = rule_set.get_rule(patch.rule_id)
        if not rule:
            return
        
        # Add a generic narrowing condition
        condition = RuleCondition(
            field='scope',
            operator='eq',
            value=patch.changes.get('scope_value', 'narrow')
        )
        rule.conditions.append(condition)
    
    def _generate_version_id(self, parent_version: str) -> str:
        """Generate a new version ID"""
        # Parse version like "v0" -> "v1"
        if parent_version.startswith('v'):
            try:
                num = int(parent_version[1:])
                return f"v{num + 1}"
            except ValueError:
                pass
        
        # Fallback to UUID
        return f"v{uuid.uuid4().hex[:8]}"
    
    def rollback(
        self,
        world_model: WorldModel,
        target_version: str
    ) -> Optional[WorldModel]:
        """Rollback to a previous version"""
        # Find snapshot
        snapshot = world_model.get_snapshot(target_version)
        if not snapshot:
            # Search in history
            snapshot = next(
                (s for s in self.version_history if s.version == target_version),
                None
            )
        
        if not snapshot:
            return None
        
        # Create new WorldModel from snapshot
        restored = WorldModel(
            version=snapshot.version,
            parent_version=snapshot.parent_version,
            rules=copy.deepcopy(snapshot.rules)
        )
        restored.state = copy.deepcopy(snapshot.state)
        restored.metadata = copy.deepcopy(snapshot.metadata)
        
        return restored
    
    def get_lineage(self, version: str) -> List[str]:
        """Get the lineage of patches for a version"""
        lineage = []
        for v, patch_id in self.patch_lineage:
            if v == version or version.startswith(v):
                lineage.append(patch_id)
        return lineage
