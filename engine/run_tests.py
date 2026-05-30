"""
Simple test runner for the Orchestrator Engine.
Runs tests without external dependencies (no pytest required).
"""

import sys
import traceback
import tempfile
import asyncio
from pathlib import Path
from typing import Callable, List, Tuple

# Add engine to path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import Orchestrator, SimpleTaskExecutor
from phase_manager import PhaseManager, ExecutionConfig, TaskExecutor
from state_manager import StateManager, PhaseStatus, TaskStatus
from task_decomposer import TaskDecomposer, Subtask, TaskDependencyType


class TestRunner:
    """Simple test runner."""

    def __init__(self):
        self.tests: List[Tuple[str, Callable]] = []
        self.passed = 0
        self.failed = 0
        self.errors = []

    def test(self, name: str) -> Callable:
        """Decorator to register a test."""
        def wrapper(func):
            self.tests.append((name, func))
            return func
        return wrapper

    async def run_all(self) -> bool:
        """Run all tests. Returns True if all passed."""
        print(f"\n{'='*60}")
        print("Running Orchestrator Engine Tests")
        print(f"{'='*60}\n")

        for test_name, test_func in self.tests:
            try:
                print(f"Running: {test_name}...", end=" ")
                
                # Check if async
                if asyncio.iscoroutinefunction(test_func):
                    await test_func()
                else:
                    test_func()
                
                print("✓ PASSED")
                self.passed += 1
            except Exception as e:
                print(f"✗ FAILED")
                self.failed += 1
                self.errors.append((test_name, e))
                traceback.print_exc()

        # Summary
        print(f"\n{'='*60}")
        print("Test Summary")
        print(f"{'='*60}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Total:  {self.passed + self.failed}")

        if self.errors:
            print(f"\n{'='*60}")
            print("Failures")
            print(f"{'='*60}")
            for test_name, error in self.errors:
                print(f"\n{test_name}:")
                print(f"  {error}")

        return self.failed == 0


# Create test runner
runner = TestRunner()


# ============================================================================
# STATE MANAGER TESTS
# ============================================================================

@runner.test("StateManager: Initialization")
def test_state_manager_init():
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = StateManager(tmpdir)
        assert manager.workflow_id is None
        assert len(manager.phases) == 0


@runner.test("StateManager: Phase lifecycle")
def test_phase_lifecycle():
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = StateManager(tmpdir)
        manager.init_workflow("test-wf", [1, 2])
        
        manager.start_phase(1, "Test Phase")
        assert manager.get_phase_status(1) == PhaseStatus.IN_PROGRESS
        
        manager.complete_phase(1, {"result": "success"}, duration_seconds=10.0)
        phase = manager.get_phase_result(1)
        assert phase.status == PhaseStatus.COMPLETED
        assert phase.duration_seconds == 10.0


@runner.test("StateManager: Task lifecycle")
def test_task_lifecycle():
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = StateManager(tmpdir)
        manager.init_workflow("test-wf", [1])
        manager.start_phase(1, "Test")
        
        manager.start_task("task-1")
        assert manager.get_task_status("task-1") == TaskStatus.IN_PROGRESS
        
        manager.complete_task("task-1", {"data": "test"}, duration_seconds=5.0)
        task = manager.get_task_result("task-1")
        assert task.status == TaskStatus.COMPLETED
        assert task.output == {"data": "test"}


@runner.test("StateManager: Checkpoint persistence")
def test_checkpoint_persistence():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save state
        manager1 = StateManager(tmpdir)
        manager1.init_workflow("test-wf", [1])
        manager1.start_phase(1, "Phase 1")
        manager1.start_task("task-1")
        manager1.complete_task("task-1", {"data": "test"})
        
        # Load in new manager
        manager2 = StateManager(tmpdir)
        assert manager2.load_checkpoint("test-wf")
        assert manager2.workflow_id == "test-wf"
        assert manager2.get_task_status("task-1") == TaskStatus.COMPLETED


@runner.test("StateManager: Workflow summary")
def test_workflow_summary():
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = StateManager(tmpdir)
        manager.init_workflow("test-wf", [1])
        manager.start_phase(1, "Phase")
        manager.start_task("task-1")
        manager.complete_task("task-1")
        manager.start_task("task-2")
        manager.fail_task("task-2", "error")
        manager.complete_phase(1)
        
        summary = manager.get_workflow_summary()
        assert summary["summary"]["total_tasks"] == 2
        assert summary["summary"]["completed_tasks"] == 1
        assert summary["summary"]["failed_tasks"] == 1


# ============================================================================
# TASK DECOMPOSER TESTS
# ============================================================================

@runner.test("TaskDecomposer: Decomposition")
def test_decomposer():
    decomposer = TaskDecomposer()
    plan = decomposer.decompose("Build a REST API")
    
    assert len(plan.phases) == 7
    for phase in range(1, 8):
        assert phase in plan.phases
        assert len(plan.phases[phase]) > 0


@runner.test("TaskDecomposer: Phase tasks")
def test_decomposer_phases():
    decomposer = TaskDecomposer()
    plan = decomposer.decompose("Test")
    
    phase_1 = plan.get_phase_tasks(1)
    assert len(phase_1) >= 1
    
    for task in phase_1:
        assert task.task_id
        assert task.title
        assert task.phase == 1


@runner.test("TaskDecomposer: Task dependencies")
def test_decomposer_dependencies():
    decomposer = TaskDecomposer()
    plan = decomposer.decompose("Test")
    
    phase_1 = plan.get_phase_tasks(1)
    if len(phase_1) > 1:
        # Second task should have dependencies
        assert len(phase_1[1].dependencies) > 0 or not phase_1[1].has_blocking_dependencies()


@runner.test("TaskDecomposer: Parallel grouping")
def test_parallel_grouping():
    decomposer = TaskDecomposer()
    plan = decomposer.decompose("Test")
    
    groups = plan.get_parallel_tasks(1)
    assert len(groups) > 0
    assert all(isinstance(g, list) and len(g) > 0 for g in groups)


# ============================================================================
# PHASE MANAGER TESTS
# ============================================================================

@runner.test("PhaseManager: Initialization")
def test_phase_manager_init():
    with tempfile.TemporaryDirectory() as tmpdir:
        state_manager = StateManager(tmpdir)
        phase_manager = PhaseManager(state_manager)
        assert phase_manager is not None


@runner.test("PhaseManager: Configuration")
def test_phase_manager_config():
    with tempfile.TemporaryDirectory() as tmpdir:
        state_manager = StateManager(tmpdir)
        phase_manager = PhaseManager(state_manager)
        
        config = ExecutionConfig(max_retries=5, parallel_task_limit=3)
        phase_manager.set_config(config)
        assert phase_manager.config.max_retries == 5


@runner.test("PhaseManager: Executor registration")
def test_executor_registration():
    with tempfile.TemporaryDirectory() as tmpdir:
        state_manager = StateManager(tmpdir)
        phase_manager = PhaseManager(state_manager)
        
        executor = SimpleTaskExecutor("test")
        phase_manager.set_task_executor("test", executor)
        assert "test" in phase_manager.task_executors


@runner.test("PhaseManager: Simple executor")
async def test_simple_executor():
    executor = SimpleTaskExecutor("test")
    task = Subtask(
        task_id="test-1",
        title="Test",
        description="Test task",
        phase=1,
    )
    
    result = await executor.execute(task)
    assert result["status"] == "success"
    assert result["task_id"] == "test-1"


# ============================================================================
# ORCHESTRATOR TESTS
# ============================================================================

@runner.test("Orchestrator: Initialization")
def test_orchestrator_init():
    with tempfile.TemporaryDirectory() as tmpdir:
        orchestrator = Orchestrator(tmpdir)
        assert orchestrator.workspace_root.exists()


@runner.test("Orchestrator: Problem analysis")
def test_problem_analysis():
    with tempfile.TemporaryDirectory() as tmpdir:
        orchestrator = Orchestrator(tmpdir)
        plan = orchestrator.analyze_problem("Build API")
        
        assert plan is not None
        assert len(plan.phases) == 7
        assert len(plan.get_all_tasks()) > 0


@runner.test("Orchestrator: Phase tasks retrieval")
def test_phase_tasks():
    with tempfile.TemporaryDirectory() as tmpdir:
        orchestrator = Orchestrator(tmpdir)
        orchestrator.analyze_problem("Test")
        
        tasks = orchestrator.get_phase_tasks(1)
        assert len(tasks) > 0
        assert "task_id" in tasks[0]


@runner.test("Orchestrator: Skill injection context")
def test_skill_context():
    with tempfile.TemporaryDirectory() as tmpdir:
        orchestrator = Orchestrator(tmpdir)
        
        # Create dummy skills
        skills_dir = Path(tmpdir) / ".harness" / "generated"
        skills_dir.mkdir(parents=True, exist_ok=True)
        (skills_dir / "skill1.md").write_text("Content")
        
        context = orchestrator.skill_injection_context()
        assert "available_skills" in context
        assert "skill1" in context["available_skills"]


@runner.test("Orchestrator: Claude prompt building")
def test_claude_prompt():
    with tempfile.TemporaryDirectory() as tmpdir:
        orchestrator = Orchestrator(tmpdir)
        orchestrator.analyze_problem("Test")
        
        tasks = orchestrator.get_phase_tasks(1)
        prompt = orchestrator.build_claude_prompt(tasks[0])
        assert "Task:" in prompt
        assert "Description" in prompt


@runner.test("Orchestrator: Status tracking")
def test_status_tracking():
    with tempfile.TemporaryDirectory() as tmpdir:
        orchestrator = Orchestrator(tmpdir)
        orchestrator.state_manager.init_workflow("test", [1])
        orchestrator.state_manager.start_phase(1, "Test")
        
        status = orchestrator.get_status()
        assert status["workflow_id"] == "test"
        assert "summary" in status


@runner.test("Orchestrator: Results export")
def test_results_export():
    with tempfile.TemporaryDirectory() as tmpdir:
        orchestrator = Orchestrator(tmpdir)
        orchestrator.state_manager.init_workflow("test", [1])
        orchestrator.state_manager.start_phase(1, "Phase")
        orchestrator.state_manager.complete_phase(1)
        
        output_file = Path(tmpdir) / "results.json"
        orchestrator.export_results(str(output_file))
        assert output_file.exists()


# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Run all tests."""
    success = await runner.run_all()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
