from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
import time


class ExecutionStatus(Enum):
    """Status of execution"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    TIMEOUT = "timeout"


@dataclass
class BuildTrace:
    """Records how a DAG node was constructed from rules"""
    node_id: str
    applied_rule_id: Optional[str]
    reason: str
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "applied_rule_id": self.applied_rule_id,
            "reason": self.reason,
            "timestamp": self.timestamp
        }


@dataclass
class ExecutionEvent:
    """Single event in execution trace"""
    event_type: str
    action: Optional[Any] = None
    observation: Optional[Any] = None
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "action": str(self.action) if self.action else None,
            "observation": str(self.observation) if self.observation else None,
            "error": self.error,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


@dataclass
class ExecutionReport:
    """Complete report of DAG execution"""
    task_id: str
    status: ExecutionStatus
    events: List[ExecutionEvent] = field(default_factory=list)
    build_traces: List[BuildTrace] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    error_message: Optional[str] = None
    world_model_version: Optional[str] = None
    
    def add_event(self, event: ExecutionEvent):
        """Add an event to the report"""
        self.events.append(event)
    
    def add_build_trace(self, trace: BuildTrace):
        """Add a build trace entry"""
        self.build_traces.append(trace)
    
    def complete(self, status: ExecutionStatus, error: Optional[str] = None):
        """Mark execution as complete"""
        self.status = status
        self.end_time = time.time()
        self.error_message = error
    
    def get_failed_rules(self) -> List[str]:
        """Extract rule IDs that were involved in failures"""
        failed_rules = []
        for event in self.events:
            if event.error and event.metadata.get('rule_id'):
                failed_rules.append(event.metadata['rule_id'])
        return list(set(failed_rules))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "events": [e.to_dict() for e in self.events],
            "build_traces": [t.to_dict() for t in self.build_traces],
            "start_time": self.start_time,
            "end_time": self.end_time,
            "error_message": self.error_message,
            "world_model_version": self.world_model_version
        }


class Trace:
    """Legacy trace class for backward compatibility"""
    
    def __init__(self):
        self.events = []

    def log(self, event):
        """Log an event"""
        self.events.append(event)
    
    def to_execution_report(self, task_id: str, status: ExecutionStatus) -> ExecutionReport:
        """Convert to ExecutionReport format"""
        report = ExecutionReport(task_id=task_id, status=status)
        for event in self.events:
            if isinstance(event, dict):
                report.add_event(ExecutionEvent(
                    event_type=event.get('type', 'unknown'),
                    metadata=event
                ))
            else:
                report.add_event(ExecutionEvent(
                    event_type='legacy',
                    metadata={'event': str(event)}
                ))
        return report
