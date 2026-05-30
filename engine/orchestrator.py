"""
Main Orchestrator: Coordinates the complete workflow from problem analysis to completion.
Integrates all components: decomposer, phase manager, state manager, and executors.
"""

import json
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from task_decomposer import TaskDecomposer, DecomposedPlan
from phase_manager import PhaseManager, ExecutionConfig, TaskExecutor
from state_manager import StateManager


class SimpleTaskExecutor(TaskExecutor):
    """
    Simple task executor that logs and simulates execution.
    In production, this would delegate to Claude Code, run system commands, etc.
    """

    def __init__(self, task_type: str = "default"):
        self.task_type = task_type

    async def execute(self, task) -> Dict[str, Any]:
        """Execute a task (mock implementation)."""
        # Simulate work
        await asyncio.sleep(0.1)
        
        return {
            "status": "success",
            "task_id": task.task_id,
            "task_type": self.task_type,
            "output": f"Completed {task.title}",
            "timestamp": datetime.now().isoformat(),
        }

    async def validate(self, task) -> bool:
        """Validate task can execute."""
        return task is not None


class Orchestrator:
    """
    Main orchestrator that manages the complete 7-phase workflow.
    
    Workflow:
    1. Analyze problem → decompose into subtasks
    2. Load context → gather skills + Figma design
    3. Code generation → spawn sub-agents per task
    4. Visual verification → UI testing + design comparison
    5. Testing → write + run tests
    6. Re-verification → lint/types/design
    7. Completion → finalize + ship
    """

    def __init__(
        self,
        workspace_root: str = "/tmp/harness-claude-skills",
        state_dir: Optional[str] = None,
    ):
        """
        Initialize orchestrator.
        
        Args:
            workspace_root: Root directory for the project
            state_dir: Directory for persisting state (defaults to .harness/state/)
        """
        self.workspace_root = Path(workspace_root)
        self.workspace_root.mkdir(parents=True, exist_ok=True)

        if state_dir is None:
            state_dir = str(self.workspace_root / ".harness" / "state")

        self.state_manager = StateManager(state_dir)
        self.decomposer = TaskDecomposer()
        self.phase_manager = PhaseManager(self.state_manager)
        self.plan: Optional[DecomposedPlan] = None
        self.config = ExecutionConfig()

        # Register default executors
        self._register_default_executors()

    def _register_default_executors(self):
        """Register default task executors."""
        self.phase_manager.set_task_executor("claude", SimpleTaskExecutor("claude"))
        self.phase_manager.set_task_executor("system", SimpleTaskExecutor("system"))
        self.phase_manager.set_task_executor("orchestrator", SimpleTaskExecutor("orchestrator"))

    def set_config(self, config: ExecutionConfig):
        """Set execution configuration."""
        self.config = config
        self.phase_manager.set_config(config)

    def register_executor(self, agent_type: str, executor: TaskExecutor):
        """Register a custom task executor."""
        self.phase_manager.set_task_executor(agent_type, executor)

    def analyze_problem(
        self,
        problem_statement: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> DecomposedPlan:
        """
        Analyze the problem and decompose into subtasks.
        
        Args:
            problem_statement: Description of work to be done
            context: Additional context (e.g., figma_url, skills_dir)
        
        Returns:
            DecomposedPlan with all phases and tasks
        """
        print(f"\n{'='*60}")
        print("Step 1: Analyzing Problem")
        print(f"{'='*60}\n")
        print(f"Problem: {problem_statement}\n")

        context = context or {}
        self.plan = self.decomposer.decompose(problem_statement, context)

        # Log decomposition
        print(f"Decomposed into {len(self.plan.get_all_tasks())} tasks across 7 phases:\n")
        for phase_num in range(1, 8):
            tasks = self.plan.get_phase_tasks(phase_num)
            if tasks:
                print(f"  Phase {phase_num}: {len(tasks)} tasks")
                for task in tasks:
                    deps = " (seq)" if task.has_blocking_dependencies() else ""
                    print(f"    - {task.task_id}: {task.title}{deps}")

        return self.plan

    async def execute(self, workflow_id: str) -> bool:
        """
        Execute the complete workflow.
        
        Args:
            workflow_id: Unique identifier for this workflow
        
        Returns:
            True if workflow succeeded, False otherwise
        """
        if not self.plan:
            raise ValueError("No plan available. Call analyze_problem() first.")

        print(f"\n{'='*60}")
        print("Step 2: Executing Workflow")
        print(f"{'='*60}\n")

        self.phase_manager.set_plan(self.plan)
        success = await self.phase_manager.execute_workflow(workflow_id)

        return success

    def resume_workflow(self, workflow_id: str) -> bool:
        """
        Resume a previously started workflow from checkpoint.
        
        Args:
            workflow_id: ID of workflow to resume
        
        Returns:
            True if checkpoint loaded successfully
        """
        if self.state_manager.load_checkpoint(workflow_id):
            print(f"Loaded checkpoint for workflow {workflow_id}")
            return True
        return False

    def get_status(self) -> Dict[str, Any]:
        """Get current workflow status and statistics."""
        return self.state_manager.get_workflow_summary()

    def export_results(self, output_path: str):
        """Export workflow results to JSON file."""
        self.state_manager.export_summary(output_path)
        print(f"\nWorkflow summary exported to {output_path}")

    async def run(
        self,
        problem_statement: str,
        workflow_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        export_results: bool = True,
    ) -> Dict[str, Any]:
        """
        Run complete workflow from problem statement to results.
        
        Args:
            problem_statement: Description of work to be done
            workflow_id: Unique workflow ID (auto-generated if not provided)
            context: Additional context
            export_results: Whether to export results to disk
        
        Returns:
            Workflow results dictionary
        """
        if workflow_id is None:
            workflow_id = f"wf_{int(datetime.now().timestamp())}"

        # Try to resume from checkpoint
        if not self.resume_workflow(workflow_id):
            # New workflow: analyze problem
            self.analyze_problem(problem_statement, context)

        # Execute workflow
        success = await self.execute(workflow_id)

        # Get results
        results = self.get_status()
        results["success"] = success

        # Export if requested
        if export_results:
            output_dir = self.workspace_root / ".harness" / "results"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"{workflow_id}.json"
            self.export_results(str(output_file))

        print(f"\n{'='*60}")
        print("Workflow Complete")
        print(f"{'='*60}\n")
        print(f"Status: {'✓ SUCCESS' if success else '✗ FAILED'}")
        print(f"Workflow ID: {workflow_id}")
        print(f"Total phases: {results['summary']['total_phases']}")
        print(f"Completed phases: {results['summary']['completed_phases']}")
        print(f"Failed phases: {results['summary']['failed_phases']}")
        print(f"Total tasks: {results['summary']['total_tasks']}")
        print(f"Completed tasks: {results['summary']['completed_tasks']}")
        print(f"Failed tasks: {results['summary']['failed_tasks']}")

        return results

    def get_phase_tasks(self, phase_num: int) -> List[Dict[str, Any]]:
        """Get all tasks for a specific phase."""
        if not self.plan:
            return []

        tasks = self.plan.get_phase_tasks(phase_num)
        return [task.to_dict() for task in tasks]

    def get_task_dependencies(self, task_id: str) -> List[str]:
        """Get dependency IDs for a task."""
        if not self.plan:
            return []

        task = self.plan.get_task_by_id(task_id)
        if not task:
            return []

        return task.get_ordered_dependencies()

    def skill_injection_context(self) -> Dict[str, Any]:
        """
        Build context for injecting skills into prompts for Claude sub-agents.
        This prepares skill definitions for use in code generation phase.
        """
        skills_dir = self.workspace_root / ".harness" / "generated"
        skills = {}

        if skills_dir.exists():
            for skill_file in skills_dir.glob("*.md"):
                try:
                    with open(skill_file) as f:
                        skills[skill_file.stem] = f.read()
                except Exception as e:
                    print(f"Error loading skill {skill_file}: {e}")

        return {
            "available_skills": list(skills.keys()),
            "skills": skills,
            "skills_dir": str(skills_dir),
        }

    def build_claude_prompt(
        self,
        task: Dict[str, Any],
        include_skills: bool = True,
    ) -> str:
        """
        Build a prompt for Claude sub-agents with task details and injected skills.
        
        Args:
            task: Task dictionary (from decomposed plan)
            include_skills: Whether to inject available skills
        
        Returns:
            Formatted prompt string
        """
        prompt = f"""# Task: {task.get('title', 'Unknown')}

## Description
{task.get('description', 'No description')}

## Phase
Phase {task.get('phase', '?')}: {self.phase_manager.PHASE_NAMES.get(task.get('phase', 0), 'Unknown')}

## Parameters
{json.dumps(task.get('parameters', {}), indent=2)}
"""

        if include_skills:
            context = self.skill_injection_context()
            if context["available_skills"]:
                prompt += f"\n## Available Skills\n"
                for skill_name in context["available_skills"]:
                    prompt += f"- {skill_name}\n"

        return prompt


# Convenience functions for common workflows
async def run_workflow(
    problem_statement: str,
    workspace_root: str = "/tmp/harness-claude-skills",
    workflow_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Quick workflow execution without manual orchestrator setup.
    
    Args:
        problem_statement: Description of work
        workspace_root: Project root directory
        workflow_id: Optional workflow ID
    
    Returns:
        Workflow results
    """
    orchestrator = Orchestrator(workspace_root)
    return await orchestrator.run(problem_statement, workflow_id)


def create_orchestrator(
    workspace_root: str = "/tmp/harness-claude-skills",
) -> Orchestrator:
    """Create an orchestrator instance for manual workflow management."""
    return Orchestrator(workspace_root)
