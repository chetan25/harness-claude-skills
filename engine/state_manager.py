"""
State Manager: Track progress, intermediate results, and workflow state.
Supports resumable workflows with checkpointing.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from datetime import datetime
import json
import os
from pathlib import Path


class PhaseStatus(Enum):
    """Workflow phase execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskStatus(Enum):
    """Individual task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"  # Waiting for dependencies


@dataclass
class TaskResult:
    """Result of a single task execution."""
    task_id: str
    status: TaskStatus
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_seconds: float = 0.0
    retries: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "duration_seconds": self.duration_seconds,
            "retries": self.retries,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskResult":
        """Create from dictionary."""
        data["status"] = TaskStatus(data["status"])
        return cls(**data)


@dataclass
class PhaseResult:
    """Result of a complete phase execution."""
    phase_num: int
    phase_name: str
    status: PhaseStatus
    tasks: List[TaskResult] = field(default_factory=list)
    aggregated_output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_seconds: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "phase_num": self.phase_num,
            "phase_name": self.phase_name,
            "status": self.status.value,
            "tasks": [t.to_dict() for t in self.tasks],
            "aggregated_output": self.aggregated_output,
            "error": self.error,
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PhaseResult":
        """Create from dictionary."""
        data["status"] = PhaseStatus(data["status"])
        data["tasks"] = [TaskResult.from_dict(t) for t in data["tasks"]]
        return cls(**data)


class StateManager:
    """Manages workflow state with checkpointing and resumable execution."""

    def __init__(self, state_dir: Optional[str] = None):
        """
        Initialize state manager.
        
        Args:
            state_dir: Directory for persisting state. Defaults to /tmp/harness-claude-skills/.harness/state/
        """
        if state_dir is None:
            state_dir = "/tmp/harness-claude-skills/.harness/state"
        
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.workflow_id: Optional[str] = None
        self.phases: Dict[int, PhaseResult] = {}
        self.task_results: Dict[str, TaskResult] = {}
        self.phase_sequence: List[int] = []
        self.current_phase: Optional[int] = None
        self.metadata: Dict[str, Any] = {}

    def init_workflow(self, workflow_id: str, phase_sequence: List[int], metadata: Optional[Dict[str, Any]] = None):
        """Initialize a new workflow."""
        self.workflow_id = workflow_id
        self.phase_sequence = phase_sequence
        self.metadata = metadata or {}
        self.current_phase = None
        self.phases = {}
        self.task_results = {}

    def start_phase(self, phase_num: int, phase_name: str):
        """Mark a phase as in-progress."""
        self.current_phase = phase_num
        if phase_num not in self.phases:
            self.phases[phase_num] = PhaseResult(
                phase_num=phase_num,
                phase_name=phase_name,
                status=PhaseStatus.IN_PROGRESS,
            )
        else:
            self.phases[phase_num].status = PhaseStatus.IN_PROGRESS
        self._checkpoint()

    def start_task(self, task_id: str):
        """Mark a task as in-progress."""
        if task_id not in self.task_results:
            self.task_results[task_id] = TaskResult(
                task_id=task_id,
                status=TaskStatus.IN_PROGRESS,
            )
        else:
            self.task_results[task_id].status = TaskStatus.IN_PROGRESS
        self._checkpoint()

    def complete_task(
        self,
        task_id: str,
        output: Optional[Dict[str, Any]] = None,
        duration_seconds: float = 0.0,
        retries: int = 0,
    ):
        """Mark a task as completed."""
        if task_id not in self.task_results:
            self.task_results[task_id] = TaskResult(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                output=output,
                duration_seconds=duration_seconds,
                retries=retries,
            )
        else:
            result = self.task_results[task_id]
            result.status = TaskStatus.COMPLETED
            result.output = output
            result.duration_seconds = duration_seconds
            result.retries = retries
        
        # Add to current phase
        if self.current_phase is not None and self.current_phase in self.phases:
            self.phases[self.current_phase].tasks.append(self.task_results[task_id])
        
        self._checkpoint()

    def fail_task(self, task_id: str, error: str, retries: int = 0):
        """Mark a task as failed."""
        if task_id not in self.task_results:
            self.task_results[task_id] = TaskResult(
                task_id=task_id,
                status=TaskStatus.FAILED,
                error=error,
                retries=retries,
            )
        else:
            result = self.task_results[task_id]
            result.status = TaskStatus.FAILED
            result.error = error
            result.retries = retries
        
        # Add to current phase
        if self.current_phase is not None and self.current_phase in self.phases:
            self.phases[self.current_phase].tasks.append(self.task_results[task_id])
        
        self._checkpoint()

    def block_task(self, task_id: str, reason: str):
        """Mark a task as blocked (waiting for dependencies)."""
        if task_id not in self.task_results:
            self.task_results[task_id] = TaskResult(
                task_id=task_id,
                status=TaskStatus.BLOCKED,
                error=reason,
            )
        else:
            self.task_results[task_id].status = TaskStatus.BLOCKED
            self.task_results[task_id].error = reason
        self._checkpoint()

    def complete_phase(
        self,
        phase_num: int,
        aggregated_output: Optional[Dict[str, Any]] = None,
        duration_seconds: float = 0.0,
    ):
        """Mark a phase as completed."""
        if phase_num in self.phases:
            phase = self.phases[phase_num]
            phase.status = PhaseStatus.COMPLETED
            phase.aggregated_output = aggregated_output
            phase.duration_seconds = duration_seconds
        self.current_phase = None
        self._checkpoint()

    def fail_phase(self, phase_num: int, error: str):
        """Mark a phase as failed."""
        if phase_num in self.phases:
            self.phases[phase_num].status = PhaseStatus.FAILED
            self.phases[phase_num].error = error
        self.current_phase = None
        self._checkpoint()

    def skip_phase(self, phase_num: int, reason: str):
        """Mark a phase as skipped."""
        if phase_num not in self.phases:
            self.phases[phase_num] = PhaseResult(
                phase_num=phase_num,
                phase_name=f"Phase {phase_num}",
                status=PhaseStatus.SKIPPED,
                error=reason,
            )
        else:
            self.phases[phase_num].status = PhaseStatus.SKIPPED
            self.phases[phase_num].error = reason
        self.current_phase = None
        self._checkpoint()

    def get_phase_status(self, phase_num: int) -> Optional[PhaseStatus]:
        """Get the status of a phase."""
        if phase_num in self.phases:
            return self.phases[phase_num].status
        return None

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the status of a task."""
        if task_id in self.task_results:
            return self.task_results[task_id].status
        return None

    def get_phase_result(self, phase_num: int) -> Optional[PhaseResult]:
        """Get full result of a phase."""
        return self.phases.get(phase_num)

    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get full result of a task."""
        return self.task_results.get(task_id)

    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get summary of entire workflow."""
        return {
            "workflow_id": self.workflow_id,
            "metadata": self.metadata,
            "phases": {
                num: result.to_dict()
                for num, result in self.phases.items()
            },
            "summary": {
                "total_phases": len(self.phases),
                "completed_phases": sum(
                    1 for p in self.phases.values()
                    if p.status == PhaseStatus.COMPLETED
                ),
                "failed_phases": sum(
                    1 for p in self.phases.values()
                    if p.status == PhaseStatus.FAILED
                ),
                "total_tasks": len(self.task_results),
                "completed_tasks": sum(
                    1 for t in self.task_results.values()
                    if t.status == TaskStatus.COMPLETED
                ),
                "failed_tasks": sum(
                    1 for t in self.task_results.values()
                    if t.status == TaskStatus.FAILED
                ),
            },
        }

    def _checkpoint(self):
        """Save state to disk."""
        if self.workflow_id:
            checkpoint_file = self.state_dir / f"{self.workflow_id}.json"
            state_data = {
                "workflow_id": self.workflow_id,
                "phase_sequence": self.phase_sequence,
                "metadata": self.metadata,
                "current_phase": self.current_phase,
                "phases": {
                    str(k): v.to_dict()
                    for k, v in self.phases.items()
                },
                "task_results": {
                    k: v.to_dict()
                    for k, v in self.task_results.items()
                },
                "checkpoint_time": datetime.now().isoformat(),
            }
            with open(checkpoint_file, "w") as f:
                json.dump(state_data, f, indent=2)

    def load_checkpoint(self, workflow_id: str) -> bool:
        """Load workflow state from checkpoint. Returns True if loaded, False if not found."""
        checkpoint_file = self.state_dir / f"{workflow_id}.json"
        if not checkpoint_file.exists():
            return False
        
        try:
            with open(checkpoint_file, "r") as f:
                state_data = json.load(f)
            
            self.workflow_id = state_data["workflow_id"]
            self.phase_sequence = state_data["phase_sequence"]
            self.metadata = state_data["metadata"]
            self.current_phase = state_data["current_phase"]
            
            self.phases = {
                int(k): PhaseResult.from_dict(v)
                for k, v in state_data["phases"].items()
            }
            self.task_results = {
                k: TaskResult.from_dict(v)
                for k, v in state_data["task_results"].items()
            }
            return True
        except Exception as e:
            print(f"Error loading checkpoint: {e}")
            return False

    def clear_state(self):
        """Clear all state."""
        self.workflow_id = None
        self.phases = {}
        self.task_results = {}
        self.phase_sequence = []
        self.current_phase = None
        self.metadata = {}

    def export_summary(self, output_path: str):
        """Export workflow summary to JSON file."""
        summary = self.get_workflow_summary()
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(summary, f, indent=2)
