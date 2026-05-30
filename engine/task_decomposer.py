"""
Task Decomposer: Break down requirements into subtasks with dependencies.
Analyzes problem statements and creates execution plans.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from enum import Enum
import hashlib


class TaskDependencyType(Enum):
    """Type of dependency between tasks."""
    SEQUENTIAL = "sequential"  # Must complete before next
    PARALLEL = "parallel"  # Can run in parallel
    CONDITIONAL = "conditional"  # Only if condition met


@dataclass
class Dependency:
    """Task dependency specification."""
    task_id: str
    dep_type: TaskDependencyType = TaskDependencyType.SEQUENTIAL
    condition: Optional[str] = None  # For conditional deps

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "dep_type": self.dep_type.value,
            "condition": self.condition,
        }


@dataclass
class Subtask:
    """Individual subtask within a phase."""
    task_id: str
    title: str
    description: str
    phase: int
    priority: int = 0  # Higher = higher priority
    estimated_duration_seconds: int = 300
    dependencies: List[Dependency] = field(default_factory=list)
    agent_type: str = "claude"  # Type of agent to handle this
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "phase": self.phase,
            "priority": self.priority,
            "estimated_duration_seconds": self.estimated_duration_seconds,
            "dependencies": [d.to_dict() for d in self.dependencies],
            "agent_type": self.agent_type,
            "parameters": self.parameters,
        }

    def get_ordered_dependencies(self) -> List[str]:
        """Get dependency task IDs in order (sequential first, then parallel)."""
        sequential = [d.task_id for d in self.dependencies if d.dep_type == TaskDependencyType.SEQUENTIAL]
        parallel = [d.task_id for d in self.dependencies if d.dep_type == TaskDependencyType.PARALLEL]
        return sequential + parallel

    def has_blocking_dependencies(self) -> bool:
        """Check if this task has any sequential dependencies."""
        return any(d.dep_type == TaskDependencyType.SEQUENTIAL for d in self.dependencies)


@dataclass
class DecomposedPlan:
    """Complete task decomposition plan for all phases."""
    problem_statement: str
    phases: Dict[int, List[Subtask]] = field(default_factory=dict)
    global_dependencies: Dict[str, List[Dependency]] = field(default_factory=dict)  # Task -> dependencies
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_all_tasks(self) -> List[Subtask]:
        """Get all tasks across all phases."""
        tasks = []
        for phase_tasks in self.phases.values():
            tasks.extend(phase_tasks)
        return tasks

    def get_phase_tasks(self, phase: int) -> List[Subtask]:
        """Get tasks for a specific phase."""
        return self.phases.get(phase, [])

    def get_task_by_id(self, task_id: str) -> Optional[Subtask]:
        """Find a task by ID."""
        for task in self.get_all_tasks():
            if task.task_id == task_id:
                return task
        return None

    def get_task_dependencies(self, task_id: str) -> List[Subtask]:
        """Get all tasks that a given task depends on."""
        task = self.get_task_by_id(task_id)
        if not task:
            return []
        
        dependencies = []
        for dep in task.dependencies:
            dep_task = self.get_task_by_id(dep.task_id)
            if dep_task:
                dependencies.append(dep_task)
        return dependencies

    def get_parallel_tasks(self, phase: int) -> List[List[Subtask]]:
        """
        Get tasks grouped by execution groups (tasks that can run in parallel).
        Returns list of lists, where each inner list contains tasks that can run together.
        """
        phase_tasks = self.get_phase_tasks(phase)
        if not phase_tasks:
            return []

        # Build dependency graph
        task_map = {t.task_id: t for t in phase_tasks}
        groups = []
        processed = set()

        for task in sorted(phase_tasks, key=lambda t: -t.priority):
            if task.task_id in processed:
                continue

            # Find all tasks that can run with this one
            group = [task]
            processed.add(task.task_id)

            for other in phase_tasks:
                if other.task_id in processed:
                    continue

                # Check if there's a dependency between them
                if not self._has_dependency_between(task, other, task_map):
                    group.append(other)
                    processed.add(other.task_id)

            groups.append(group)

        return groups

    def _has_dependency_between(self, task1: Subtask, task2: Subtask, task_map: Dict[str, Subtask]) -> bool:
        """Check if there's any dependency between two tasks."""
        # Task1 depends on Task2
        if any(d.task_id == task2.task_id for d in task1.dependencies):
            return True
        # Task2 depends on Task1
        if any(d.task_id == task1.task_id for d in task2.dependencies):
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "problem_statement": self.problem_statement,
            "phases": {
                str(k): [t.to_dict() for t in v]
                for k, v in self.phases.items()
            },
            "global_dependencies": {
                k: [d.to_dict() for d in v]
                for k, v in self.global_dependencies.items()
            },
            "metadata": self.metadata,
        }


class TaskDecomposer:
    """Analyzes requirements and decomposes into structured subtasks."""

    def decompose(
        self,
        problem_statement: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> DecomposedPlan:
        """
        Decompose a problem into subtasks across all phases.
        
        This is a base implementation. In production, this would use LLM reasoning.
        For now, it returns a placeholder structure that can be extended.
        """
        context = context or {}
        
        plan = DecomposedPlan(
            problem_statement=problem_statement,
            metadata={
                "created_by": "task_decomposer",
                "context_keys": list(context.keys()),
            },
        )

        # Phase 1: Analysis & Decomposition
        phase_1_tasks = self._create_phase_1_tasks(problem_statement, context)
        plan.phases[1] = phase_1_tasks

        # Phase 2: Context Loading
        phase_2_tasks = self._create_phase_2_tasks(context)
        plan.phases[2] = phase_2_tasks

        # Phase 3: Code Generation
        phase_3_tasks = self._create_phase_3_tasks()
        plan.phases[3] = phase_3_tasks

        # Phase 4: Visual Verification
        phase_4_tasks = self._create_phase_4_tasks()
        plan.phases[4] = phase_4_tasks

        # Phase 5: Testing
        phase_5_tasks = self._create_phase_5_tasks()
        plan.phases[5] = phase_5_tasks

        # Phase 6: Re-verification
        phase_6_tasks = self._create_phase_6_tasks()
        plan.phases[6] = phase_6_tasks

        # Phase 7: Completion
        phase_7_tasks = self._create_phase_7_tasks()
        plan.phases[7] = phase_7_tasks

        return plan

    def _create_phase_1_tasks(self, problem_statement: str, context: Dict[str, Any]) -> List[Subtask]:
        """Phase 1: Analyze problem and create subtask plan."""
        return [
            Subtask(
                task_id="1.1-analyze-requirements",
                title="Analyze Requirements",
                description="Parse problem statement and identify key requirements",
                phase=1,
                priority=10,
                estimated_duration_seconds=120,
                agent_type="claude",
                parameters={
                    "problem_statement": problem_statement,
                    "max_subtasks": 10,
                },
            ),
            Subtask(
                task_id="1.2-create-decomposition",
                title="Create Task Decomposition",
                description="Break down requirements into concrete subtasks with dependencies",
                phase=1,
                priority=9,
                estimated_duration_seconds=180,
                dependencies=[
                    Dependency("1.1-analyze-requirements", TaskDependencyType.SEQUENTIAL)
                ],
                agent_type="claude",
            ),
            Subtask(
                task_id="1.3-validate-plan",
                title="Validate Execution Plan",
                description="Ensure plan is feasible and dependencies are correct",
                phase=1,
                priority=8,
                estimated_duration_seconds=90,
                dependencies=[
                    Dependency("1.2-create-decomposition", TaskDependencyType.SEQUENTIAL)
                ],
                agent_type="claude",
            ),
        ]

    def _create_phase_2_tasks(self, context: Dict[str, Any]) -> List[Subtask]:
        """Phase 2: Load context and gather resources."""
        tasks = [
            Subtask(
                task_id="2.1-load-skills",
                title="Load Available Skills",
                description="Scan .harness/generated/ and load skill definitions",
                phase=2,
                priority=10,
                estimated_duration_seconds=60,
                agent_type="system",
                parameters={
                    "skills_dir": ".harness/generated/",
                },
            ),
        ]

        # Add Figma design loading if provided
        if context.get("figma_url"):
            tasks.append(
                Subtask(
                    task_id="2.2-load-figma-design",
                    title="Load Figma Design",
                    description="Fetch and parse Figma design for UI reference",
                    phase=2,
                    priority=9,
                    estimated_duration_seconds=120,
                    dependencies=[
                        Dependency("2.1-load-skills", TaskDependencyType.PARALLEL)
                    ],
                    agent_type="system",
                    parameters={
                        "figma_url": context.get("figma_url"),
                    },
                )
            )

        tasks.append(
            Subtask(
                task_id="2.3-prepare-context",
                title="Prepare Execution Context",
                description="Assemble all context for code generation phase",
                phase=2,
                priority=8,
                estimated_duration_seconds=90,
                dependencies=[
                    Dependency("2.1-load-skills", TaskDependencyType.SEQUENTIAL),
                ] + (
                    [Dependency("2.2-load-figma-design", TaskDependencyType.SEQUENTIAL)]
                    if context.get("figma_url")
                    else []
                ),
                agent_type="system",
            )
        )

        return tasks

    def _create_phase_3_tasks(self) -> List[Subtask]:
        """Phase 3: Code generation with sub-agents."""
        return [
            Subtask(
                task_id="3.1-spawn-sub-agents",
                title="Spawn Sub-Agent Processes",
                description="Launch Claude Code or Codex sub-agents for each major task",
                phase=3,
                priority=10,
                estimated_duration_seconds=60,
                agent_type="orchestrator",
            ),
            Subtask(
                task_id="3.2-coordinate-generation",
                title="Coordinate Code Generation",
                description="Monitor sub-agent progress and handle inter-task dependencies",
                phase=3,
                priority=9,
                estimated_duration_seconds=600,
                dependencies=[
                    Dependency("3.1-spawn-sub-agents", TaskDependencyType.SEQUENTIAL)
                ],
                agent_type="orchestrator",
            ),
            Subtask(
                task_id="3.3-aggregate-artifacts",
                title="Aggregate Generated Artifacts",
                description="Collect output from all sub-agents",
                phase=3,
                priority=8,
                estimated_duration_seconds=120,
                dependencies=[
                    Dependency("3.2-coordinate-generation", TaskDependencyType.SEQUENTIAL)
                ],
                agent_type="system",
            ),
        ]

    def _create_phase_4_tasks(self) -> List[Subtask]:
        """Phase 4: Visual verification and UI testing."""
        return [
            Subtask(
                task_id="4.1-render-ui",
                title="Render UI Components",
                description="Build and render generated UI components",
                phase=4,
                priority=10,
                estimated_duration_seconds=120,
                agent_type="system",
            ),
            Subtask(
                task_id="4.2-compare-design",
                title="Compare Against Design",
                description="Visual comparison with Figma design if available",
                phase=4,
                priority=9,
                estimated_duration_seconds=180,
                dependencies=[
                    Dependency("4.1-render-ui", TaskDependencyType.PARALLEL)
                ],
                agent_type="claude",
            ),
            Subtask(
                task_id="4.3-generate-test-report",
                title="Generate Visual Test Report",
                description="Create report of visual verification results",
                phase=4,
                priority=8,
                estimated_duration_seconds=90,
                dependencies=[
                    Dependency("4.2-compare-design", TaskDependencyType.SEQUENTIAL)
                ],
                agent_type="system",
            ),
        ]

    def _create_phase_5_tasks(self) -> List[Subtask]:
        """Phase 5: Testing."""
        return [
            Subtask(
                task_id="5.1-write-tests",
                title="Write Unit Tests",
                description="Generate comprehensive unit tests for all modules",
                phase=5,
                priority=10,
                estimated_duration_seconds=300,
                agent_type="claude",
            ),
            Subtask(
                task_id="5.2-run-tests",
                title="Execute Test Suite",
                description="Run all tests and collect coverage metrics",
                phase=5,
                priority=9,
                estimated_duration_seconds=180,
                dependencies=[
                    Dependency("5.1-write-tests", TaskDependencyType.SEQUENTIAL)
                ],
                agent_type="system",
            ),
            Subtask(
                task_id="5.3-validate-coverage",
                title="Validate Test Coverage",
                description="Ensure adequate code coverage (>80%)",
                phase=5,
                priority=8,
                estimated_duration_seconds=120,
                dependencies=[
                    Dependency("5.2-run-tests", TaskDependencyType.SEQUENTIAL)
                ],
                agent_type="system",
            ),
        ]

    def _create_phase_6_tasks(self) -> List[Subtask]:
        """Phase 6: Re-verification (linting, types, design)."""
        return [
            Subtask(
                task_id="6.1-lint-code",
                title="Lint Code",
                description="Run linting checks (flake8, pylint, etc.)",
                phase=6,
                priority=10,
                estimated_duration_seconds=120,
                agent_type="system",
            ),
            Subtask(
                task_id="6.2-type-check",
                title="Type Check",
                description="Run static type checking (mypy, pyright)",
                phase=6,
                priority=9,
                estimated_duration_seconds=120,
                dependencies=[
                    Dependency("6.1-lint-code", TaskDependencyType.PARALLEL)
                ],
                agent_type="system",
            ),
            Subtask(
                task_id="6.3-design-review",
                title="Design Review",
                description="Review code architecture and design patterns",
                phase=6,
                priority=8,
                estimated_duration_seconds=150,
                dependencies=[
                    Dependency("6.1-lint-code", TaskDependencyType.PARALLEL),
                    Dependency("6.2-type-check", TaskDependencyType.PARALLEL),
                ],
                agent_type="claude",
            ),
        ]

    def _create_phase_7_tasks(self) -> List[Subtask]:
        """Phase 7: Completion and shipping."""
        return [
            Subtask(
                task_id="7.1-finalize-code",
                title="Finalize Code",
                description="Apply final polish, documentation, and cleanup",
                phase=7,
                priority=10,
                estimated_duration_seconds=120,
                agent_type="claude",
            ),
            Subtask(
                task_id="7.2-create-summary",
                title="Create Completion Summary",
                description="Generate summary of all work completed",
                phase=7,
                priority=9,
                estimated_duration_seconds=90,
                dependencies=[
                    Dependency("7.1-finalize-code", TaskDependencyType.SEQUENTIAL)
                ],
                agent_type="system",
            ),
            Subtask(
                task_id="7.3-ship-artifacts",
                title="Ship Artifacts",
                description="Package and deliver all artifacts",
                phase=7,
                priority=8,
                estimated_duration_seconds=60,
                dependencies=[
                    Dependency("7.2-create-summary", TaskDependencyType.SEQUENTIAL)
                ],
                agent_type="system",
            ),
        ]
