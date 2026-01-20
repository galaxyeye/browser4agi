from typing import List, Dict, Any
from dataclasses import dataclass, field
from core.trace import ExecutionReport, ExecutionStatus
from core.world_model import WorldModel
from core.engine import Engine
from rules.rule_set import RuleSet


@dataclass
class WorldModelDiff:
    """Represents differences between two WorldModel versions"""
    version_a: str
    version_b: str
    rules_added: List[str] = field(default_factory=list)
    rules_removed: List[str] = field(default_factory=list)
    rules_modified: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version_a": self.version_a,
            "version_b": self.version_b,
            "rules_added": self.rules_added,
            "rules_removed": self.rules_removed,
            "rules_modified": self.rules_modified
        }


@dataclass
class SimulationMetrics:
    """Metrics from simulation run"""
    success_rate: float
    avg_execution_time: float
    failure_count: int
    success_count: int
    total_tasks: int
    rule_count: int
    avg_complexity: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success_rate": self.success_rate,
            "avg_execution_time": self.avg_execution_time,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "total_tasks": self.total_tasks,
            "rule_count": self.rule_count,
            "avg_complexity": self.avg_complexity
        }


@dataclass
class SimulationResult:
    """Result of A/B simulation"""
    baseline_metrics: SimulationMetrics
    patched_metrics: SimulationMetrics
    diff: WorldModelDiff
    baseline_reports: List[ExecutionReport] = field(default_factory=list)
    patched_reports: List[ExecutionReport] = field(default_factory=list)
    
    # Improvement thresholds (configurable)
    MAX_RULE_COUNT_DELTA: int = 5
    MAX_COMPLEXITY_DELTA: float = 2.0
    
    def get_success_delta(self) -> float:
        """Calculate change in success rate"""
        return self.patched_metrics.success_rate - self.baseline_metrics.success_rate
    
    def get_rule_count_delta(self) -> int:
        """Calculate change in rule count"""
        return self.patched_metrics.rule_count - self.baseline_metrics.rule_count
    
    def get_complexity_delta(self) -> float:
        """Calculate change in complexity"""
        return self.patched_metrics.avg_complexity - self.baseline_metrics.avg_complexity
    
    def is_improvement(self) -> bool:
        """Check if patch improves performance"""
        return (self.get_success_delta() > 0 and 
                self.get_rule_count_delta() <= self.MAX_RULE_COUNT_DELTA and
                self.get_complexity_delta() < self.MAX_COMPLEXITY_DELTA)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "baseline_metrics": self.baseline_metrics.to_dict(),
            "patched_metrics": self.patched_metrics.to_dict(),
            "diff": self.diff.to_dict(),
            "success_delta": self.get_success_delta(),
            "rule_count_delta": self.get_rule_count_delta(),
            "complexity_delta": self.get_complexity_delta(),
            "is_improvement": self.is_improvement()
        }


class Simulator:
    """A/B testing simulator for WorldModel changes"""
    
    def __init__(self, baseline_world: WorldModel, baseline_rules: RuleSet):
        self.baseline_world = baseline_world
        self.baseline_rules = baseline_rules
    
    def run_simulation(
        self, 
        patched_world: WorldModel,
        patched_rules: RuleSet,
        test_tasks: List[str]
    ) -> SimulationResult:
        """Run A/B simulation on test tasks"""
        
        # Run baseline
        baseline_reports = self._run_tests(
            self.baseline_world, 
            self.baseline_rules, 
            test_tasks
        )
        baseline_metrics = self._calculate_metrics(baseline_reports, self.baseline_rules)
        
        # Run patched version
        patched_reports = self._run_tests(
            patched_world,
            patched_rules,
            test_tasks
        )
        patched_metrics = self._calculate_metrics(patched_reports, patched_rules)
        
        # Calculate diff
        diff = self._calculate_diff(self.baseline_world, patched_world)
        
        return SimulationResult(
            baseline_metrics=baseline_metrics,
            patched_metrics=patched_metrics,
            diff=diff,
            baseline_reports=baseline_reports,
            patched_reports=patched_reports
        )
    
    def _run_tests(
        self, 
        world: WorldModel, 
        rules: RuleSet, 
        tasks: List[str]
    ) -> List[ExecutionReport]:
        """Run test tasks on a WorldModel"""
        engine = Engine(world, rules)
        reports = []
        
        for i, task in enumerate(tasks):
            report = engine.plan_and_execute(task, f"task_{i}")
            reports.append(report)
        
        return reports
    
    def _calculate_metrics(
        self, 
        reports: List[ExecutionReport],
        rules: RuleSet
    ) -> SimulationMetrics:
        """Calculate metrics from execution reports"""
        success_count = sum(1 for r in reports if r.status == ExecutionStatus.SUCCESS)
        failure_count = len(reports) - success_count
        success_rate = success_count / len(reports) if reports else 0.0
        
        # Calculate average execution time
        exec_times = [
            r.end_time - r.start_time 
            for r in reports 
            if r.end_time and r.start_time
        ]
        avg_time = sum(exec_times) / len(exec_times) if exec_times else 0.0
        
        # Calculate average complexity (based on rule conditions)
        total_complexity = sum(
            len(r.conditions) + len(r.order_constraints) 
            for r in rules.rules
        )
        avg_complexity = total_complexity / len(rules.rules) if rules.rules else 0.0
        
        return SimulationMetrics(
            success_rate=success_rate,
            avg_execution_time=avg_time,
            failure_count=failure_count,
            success_count=success_count,
            total_tasks=len(reports),
            rule_count=len(rules.rules),
            avg_complexity=avg_complexity
        )
    
    def _calculate_diff(
        self, 
        baseline: WorldModel, 
        patched: WorldModel
    ) -> WorldModelDiff:
        """Calculate difference between two WorldModels"""
        baseline_rule_ids = {r.id for r in baseline.rules}
        patched_rule_ids = {r.id for r in patched.rules}
        
        added = list(patched_rule_ids - baseline_rule_ids)
        removed = list(baseline_rule_ids - patched_rule_ids)
        
        # Check for modified rules (same ID but different content)
        modified = []
        for rule in patched.rules:
            if rule.id in baseline_rule_ids:
                baseline_rule = next(r for r in baseline.rules if r.id == rule.id)
                if rule.to_dict() != baseline_rule.to_dict():
                    modified.append(rule.id)
        
        return WorldModelDiff(
            version_a=baseline.version,
            version_b=patched.version,
            rules_added=added,
            rules_removed=removed,
            rules_modified=modified
        )
