"""
Phase Manager: Orchestrates execution of the 7-phase workflow.
Handles phase transitions, task scheduling, and retry logic.
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from enum import Enum

from task_decomposer import DecomposedPlan, Subtask, TaskDependencyType
from state_manager import StateManager, PhaseStatus, TaskStatus


@dataclass
class ExecutionConfig:
    """Configuration for phase execution."""
    max_retries: int = 3
    retry_delay_seconds: float = 2.0
    parallel_task_limit: int = 5
    fail_fast: bool = False  # Stop on first failure
    skip_phases: List[int] = None  # Phases to skip

    def __post_init__(self):
        if self.skip_phases is None:
            self.skip_phases = []


class TaskExecutor:
    """Base class for executing tasks."""

    async def execute(self, task: Subtask) -> Dict[str, Any]:
        """
        Execute a task and return result.
        Should be overridden by subclasses for different task types.
        """
        raise NotImplementedError

    async def validate(self, task: Subtask) -> bool:
        """Validate that task can be executed."""
        return True


class PhaseManager:
    """Manages the 7-phase workflow execution."""

    PHASE_NAMES = {
        1: "Analyze Problem",
        2: "Load Context",
        3: "Code Generation",
        4: "Visual Verification",
        5: "Testing",
        6: "Re-verification",
        7: "Completion",
    }

    def __init__(
        self,
        state_manager: StateManager,
        task_executors: Optional[Dict[str, TaskExecutor]] = None,
    ):
        """
        Initialize phase manager.
        
        Args:
            state_manager: State tracking manager
            task_executors: Dict mapping agent types to executors
        """
        self.state_manager = state_manager
        self.task_executors = task_executors or {}
        self.plan: Optional[DecomposedPlan] = None
        self.config: ExecutionConfig = ExecutionConfig()
        self._task_outputs: Dict[str, Any] = {}  # Cache task results
        self._phase_start_times: Dict[int, float] = {}

    def set_config(self, config: ExecutionConfig):
        """Set execution configuration."""
        self.config = config

    def set_plan(self, plan: DecomposedPlan):
        """Set the decomposed task plan."""
        self.plan = plan

    def set_task_executor(self, agent_type: str, executor: TaskExecutor):
        """Register a task executor for a specific agent type."""
        self.task_executors[agent_type] = executor

    async def execute_workflow(self, workflow_id: str) -> bool:
        """
        Execute the complete workflow. Returns True if successful.
        """
        if not self.plan:
            raise ValueError("No plan set. Call set_plan() first.")

        # Initialize workflow tracking
        phases = list(range(1, 8))
        self.state_manager.init_workflow(workflow_id, phases)

        try:
            for phase_num in phases:
                if phase_num in self.config.skip_phases:
                    self.state_manager.skip_phase(phase_num, "Skipped by configuration")
                    continue

                phase_name = self.PHASE_NAMES.get(phase_num, f"Phase {phase_num}")
                success = await self._execute_phase(phase_num, phase_name)

                if not success:
                    if self.config.fail_fast:
                        return False
                    # Continue to next phase even if this one failed

            return True
        except Exception as e:
            print(f"Workflow execution failed: {e}")
            return False

    async def _execute_phase(self, phase_num: int, phase_name: str) -> bool:
        """Execute a single phase. Returns True if successful."""
        print(f"\n{'='*60}")
        print(f"Executing Phase {phase_num}: {phase_name}")
        print(f"{'='*60}\n")

        self.state_manager.start_phase(phase_num, phase_name)
        self._phase_start_times[phase_num] = time.time()

        try:
            tasks = self.plan.get_phase_tasks(phase_num)
            if not tasks:
                print(f"No tasks for phase {phase_num}")
                self.state_manager.complete_phase(phase_num)
                return True

            # Get execution groups (parallel-safe task groupings)
            task_groups = self.plan.get_parallel_tasks(phase_num)

            for group_idx, task_group in enumerate(task_groups):
                print(f"  Executing task group {group_idx + 1}/{len(task_groups)}")
                success = await self._execute_task_group(task_group, phase_num)
                if not success and self.config.fail_fast:
                    self.state_manager.fail_phase(phase_num, "Task group failed")
                    return False

            phase_duration = time.time() - self._phase_start_times[phase_num]
            self.state_manager.complete_phase(phase_num, duration_seconds=phase_duration)
            print(f"\nPhase {phase_num} completed successfully ({phase_duration:.1f}s)")
            return True

        except Exception as e:
            print(f"Phase {phase_num} failed with error: {e}")
            self.state_manager.fail_phase(phase_num, str(e))
            return False

    async def _execute_task_group(self, tasks: List[Subtask], phase_num: int) -> bool:
        """Execute a group of tasks in parallel."""
        # Check dependencies
        for task in tasks:
            blocked = await self._check_dependencies(task)
            if blocked:
                self.state_manager.block_task(task.task_id, blocked)
                tasks.remove(task)

        if not tasks:
            return True

        # Execute in parallel with limit
        pending = set(tasks)
        while pending:
            batch = list(pending)[: self.config.parallel_task_limit]
            pending -= set(batch)

            coros = [self._execute_task(task) for task in batch]
            results = await asyncio.gather(*coros, return_exceptions=True)

            for task, result in zip(batch, results):
                if isinstance(result, Exception):
                    print(f"    Task {task.task_id} failed: {result}")
                else:
                    print(f"    Task {task.task_id} completed: {result}")

        return True

    async def _execute_task(self, task: Subtask) -> Dict[str, Any]:
        """Execute a single task with retry logic."""
        print(f"    Executing task {task.task_id}: {task.title}")
        self.state_manager.start_task(task.task_id)

        retries = 0
        last_error = None

        while retries <= self.config.max_retries:
            try:
                # Get executor for this task type
                executor = self.task_executors.get(task.agent_type)
                if not executor:
                    raise ValueError(f"No executor for agent type: {task.agent_type}")

                # Validate task can run
                if not await executor.validate(task):
                    raise ValueError(f"Task validation failed: {task.task_id}")

                # Execute task
                task_start = time.time()
                result = await executor.execute(task)
                task_duration = time.time() - task_start

                self._task_outputs[task.task_id] = result
                self.state_manager.complete_task(
                    task.task_id,
                    output=result,
                    duration_seconds=task_duration,
                    retries=retries,
                )
                return result

            except Exception as e:
                last_error = str(e)
                retries += 1

                if retries <= self.config.max_retries:
                    print(f"      Retry {retries}/{self.config.max_retries} after {self.config.retry_delay_seconds}s")
                    await asyncio.sleep(self.config.retry_delay_seconds)

        # All retries exhausted
        self.state_manager.fail_task(task.task_id, last_error or "Unknown error", retries=retries)
        raise Exception(f"Task {task.task_id} failed after {retries} retries: {last_error}")

    async def _check_dependencies(self, task: Subtask) -> Optional[str]:
        """
        Check if all dependencies are met.
        Returns error string if dependencies not met, None if all OK.
        """
        for dep in task.dependencies:
            dep_task = self.plan.get_task_by_id(dep.task_id)
            if not dep_task:
                return f"Dependency {dep.task_id} not found"

            # Check if dependency is completed
            dep_status = self.state_manager.get_task_status(dep.task_id)
            if dep_status is None:
                return f"Dependency {dep.task_id} not started"
            if dep_status == TaskStatus.FAILED:
                if dep.dep_type == TaskDependencyType.SEQUENTIAL:
                    return f"Required dependency {dep.task_id} failed"
            elif dep_status != TaskStatus.COMPLETED:
                return f"Dependency {dep.task_id} not completed (status: {dep_status})"

            # Check conditional dependency
            if dep.condition:
                dep_output = self._task_outputs.get(dep.task_id, {})
                if not self._evaluate_condition(dep.condition, dep_output):
                    return f"Conditional dependency {dep.task_id} not met"

        return None

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a dependency condition. Simple key existence check for now."""
        if "." in condition:
            keys = condition.split(".")
            val = context
            for key in keys:
                val = val.get(key) if isinstance(val, dict) else None
                if val is None:
                    return False
            return True
        return condition in context

    def get_task_output(self, task_id: str) -> Optional[Any]:
        """Get cached output from a completed task."""
        return self._task_outputs.get(task_id)

    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status."""
        return self.state_manager.get_workflow_summary()
