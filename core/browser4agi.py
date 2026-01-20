"""
Main Browser4AGI system integration
Orchestrates the complete self-evolution loop
"""
from typing import List, Optional
from core.world_model import WorldModel
from core.engine import Engine
from core.trace import ExecutionReport, ExecutionStatus
from core.reflection import ReflectionV1, ReflectionV2
from core.patch_applier import PatchApplier
from core.evolution_control import RuleExplosionController, PatchBudget
from core.rule_stats_updater import RuleStatsUpdater
from rules.rule_set import RuleSet
from rules.patch import PatchProposal
from simulation.simulator import Simulator
from llm.advisor import LLMAdvisor
from agent.planner import Planner
from agent.executor import Executor


class Browser4AGI:
    """
    Main system orchestrator implementing the self-evolution loop:
    
    WorldModel -> DagBuilder -> Execution -> Report -> Reflection -> 
    Patches -> Simulation -> Evolution Control -> PatchApplier -> WorldModel++
    """
    
    def __init__(
        self,
        initial_version: str = "v0",
        use_llm: bool = False,
        patch_budget: Optional[PatchBudget] = None
    ):
        # Core components
        self.world_model = WorldModel(initial_version)
        self.rule_set = RuleSet([])
        self.engine = Engine(self.world_model, self.rule_set)
        
        # Agent components
        self.planner = Planner(self.world_model, self.rule_set)
        self.executor = Executor()
        
        # Evolution components
        self.patch_applier = PatchApplier()
        self.evolution_controller = RuleExplosionController(
            patch_budget or PatchBudget()
        )
        self.rule_updater = RuleStatsUpdater()
        
        # Reflection
        self.llm_advisor = LLMAdvisor()
        self.reflection_v1 = ReflectionV1(self.rule_set)
        self.reflection_v2 = ReflectionV2(self.rule_set, self.llm_advisor)
        self.use_llm = use_llm
        
        # History
        self.execution_history: List[ExecutionReport] = []
        self.applied_patches: List[PatchProposal] = []
    
    def execute_task(self, goal: str, task_id: Optional[str] = None) -> ExecutionReport:
        """
        Execute a single task with the current WorldModel.
        Returns execution report.
        """
        if task_id is None:
            task_id = f"task_{len(self.execution_history)}"
        
        # Plan and execute
        report = self.engine.plan_and_execute(goal, task_id)
        
        # Store in history
        self.execution_history.append(report)
        
        return report
    
    def self_evolve_step(self, test_tasks: List[str]) -> dict:
        """
        Execute one step of the self-evolution loop:
        1. Run tasks with current model
        2. Reflect on failures
        3. Generate patch proposals
        4. Simulate patches
        5. Apply best patches within budget
        
        Returns summary of evolution step.
        """
        # 1. Execute test tasks
        reports = []
        for task in test_tasks:
            report = self.execute_task(task)
            reports.append(report)
        
        # 2. Identify failures
        failed_reports = [r for r in reports if r.status == ExecutionStatus.FAILURE]
        
        if not failed_reports:
            return {
                "status": "success",
                "failures": 0,
                "patches_generated": 0,
                "patches_applied": 0
            }
        
        # 3. Generate patch proposals
        proposals = []
        for report in failed_reports:
            if self.use_llm:
                proposal = self.reflection_v2.analyze_failure(report)
            else:
                proposal = self.reflection_v1.analyze_failure(report)
            
            if proposal:
                proposals.append(proposal)
        
        if not proposals:
            return {
                "status": "no_patches",
                "failures": len(failed_reports),
                "patches_generated": 0,
                "patches_applied": 0
            }
        
        # 4. Simulate patches
        simulation_results = []
        for proposal in proposals:
            # Create patched version
            patched_world, patched_rules = self.patch_applier.apply_patch(
                self.world_model,
                self.rule_set,
                proposal
            )
            
            # Run simulation
            simulator = Simulator(self.world_model, self.rule_set)
            sim_result = simulator.run_simulation(
                patched_world,
                patched_rules,
                test_tasks
            )
            
            simulation_results.append((proposal, sim_result))
        
        # 5. Evaluate with evolution controller
        acceptable_proposals = self.evolution_controller.evaluate_proposals(
            simulation_results
        )
        
        # 6. Apply best patches
        patches_applied = 0
        for proposal in acceptable_proposals:
            self.world_model, self.rule_set = self.patch_applier.apply_patch(
                self.world_model,
                self.rule_set,
                proposal
            )
            self.evolution_controller.record_patch(proposal)
            self.applied_patches.append(proposal)
            patches_applied += 1
            
            # Update engine with new components
            self.engine = Engine(self.world_model, self.rule_set)
            self.planner = Planner(self.world_model, self.rule_set)
        
        # 7. Update rule statistics
        self.rule_updater.update_all_rules(self.rule_set)
        
        return {
            "status": "evolved",
            "failures": len(failed_reports),
            "patches_generated": len(proposals),
            "patches_simulated": len(simulation_results),
            "patches_applied": patches_applied,
            "current_version": self.world_model.version,
            "rule_count": len(self.rule_set.rules)
        }
    
    def get_system_state(self) -> dict:
        """Get complete system state for monitoring"""
        budget_status = self.evolution_controller.get_budget_status()
        health_report = self.rule_updater.get_rule_health_report(self.rule_set)
        
        return {
            "version": self.world_model.version,
            "parent_version": self.world_model.parent_version,
            "rule_count": len(self.rule_set.rules),
            "execution_count": len(self.execution_history),
            "patches_applied": len(self.applied_patches),
            "budget_status": budget_status,
            "rule_health": health_report,
            "world_state": self.world_model.state
        }
    
    def rollback_to_version(self, version: str) -> bool:
        """Rollback to a previous version"""
        restored = self.patch_applier.rollback(self.world_model, version)
        if restored:
            self.world_model = restored
            self.rule_set = RuleSet(restored.rules)
            self.engine = Engine(self.world_model, self.rule_set)
            self.planner = Planner(self.world_model, self.rule_set)
            return True
        return False
    
    def export_model(self, path: str):
        """Export current WorldModel to file"""
        import json
        data = {
            "world_model": self.world_model.to_dict(),
            "execution_history": [r.to_dict() for r in self.execution_history[-10:]],
            "system_state": self.get_system_state()
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def cleanup_deprecated_rules(self) -> int:
        """Remove deprecated rules and return count"""
        removed = self.rule_updater.cleanup_deprecated_rules(self.rule_set)
        self.world_model.rules = self.rule_set.rules
        return removed
