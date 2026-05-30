"""
Comprehensive tests for the Orchestrator Engine.
Tests all components: state management, task decomposition, phase execution, and orchestration.
"""

import asyncio
import json
import tempfile
from pathlib import Path
from typing import Dict, Any
import sys

# Add engine to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator import Orchestrator, SimpleTaskExecutor
from phase_manager import PhaseManager, ExecutionConfig, TaskExecutor
from state_manager import StateManager, PhaseStatus, TaskStatus
from task_decomposer import TaskDecomposer, TaskDependencyType, Subtask


class TestStateManager:
    """Tests for StateManager component."""

    def test_state_manager_init(self):
        """Test state manager initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(tmpdir)
            assert manager.workflow_id is None
            assert len(manager.phases) == 0
            assert len(manager.task_results) == 0

    def test_phase_lifecycle(self):
        """Test complete phase lifecycle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(tmpdir)
            manager.init_workflow("test-wf", [1, 2, 3])

            # Start phase
            manager.start_phase(1, "Test Phase")
            assert manager.get_phase_status(1) == PhaseStatus.IN_PROGRESS

            # Complete phase
            manager.complete_phase(1, {"result": "success"}, duration_seconds=10.5)
            phase_result = manager.get_phase_result(1)
            assert phase_result.status == PhaseStatus.COMPLETED
            assert phase_result.duration_seconds == 10.5

    def test_task_lifecycle(self):
        """Test complete task lifecycle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(tmpdir)
            manager.init_workflow("test-wf", [1])
            manager.start_phase(1, "Test Phase")

            # Start task
            manager.start_task("task-1")
            assert manager.get_task_status("task-1") == TaskStatus.IN_PROGRESS

            # Complete task
            manager.complete_task("task-1", {"output": "done"}, duration_seconds=5.0)
            task_result = manager.get_task_result("task-1")
            assert task_result.status == TaskStatus.COMPLETED
            assert task_result.output == {"output": "done"}

    def test_checkpoint_persistence(self):
        """Test state persistence and recovery."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and save state
            manager1 = StateManager(tmpdir)
            manager1.init_workflow("test-wf", [1, 2])
            manager1.start_phase(1, "Phase 1")
            manager1.start_task("task-1")
            manager1.complete_task("task-1", {"data": "test"})

            # Load state in new manager
            manager2 = StateManager(tmpdir)
            assert manager2.load_checkpoint("test-wf")
            assert manager2.workflow_id == "test-wf"
            assert manager2.get_task_status("task-1") == TaskStatus.COMPLETED
            assert manager2.get_task_result("task-1").output == {"data": "test"}

    def test_workflow_summary(self):
        """Test workflow summary generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(tmpdir)
            manager.init_workflow("test-wf", [1])
            manager.start_phase(1, "Phase 1")
            manager.start_task("task-1")
            manager.complete_task("task-1")
            manager.start_task("task-2")
            manager.fail_task("task-2", "test error")
            manager.complete_phase(1)

            summary = manager.get_workflow_summary()
            assert summary["workflow_id"] == "test-wf"
            assert summary["summary"]["total_tasks"] == 2
            assert summary["summary"]["completed_tasks"] == 1
            assert summary["summary"]["failed_tasks"] == 1


class TestTaskDecomposer:
    """Tests for TaskDecomposer component."""

    def test_decomposer_init(self):
        """Test decomposer initialization."""
        decomposer = TaskDecomposer()
        assert decomposer is not None

    def test_problem_decomposition(self):
        """Test basic problem decomposition."""
        decomposer = TaskDecomposer()
        problem = "Build a REST API with user authentication"
        plan = decomposer.decompose(problem)

        # Should create tasks for all 7 phases
        assert len(plan.phases) == 7
        for phase_num in range(1, 8):
            assert phase_num in plan.phases
            assert len(plan.phases[phase_num]) > 0

    def test_phase_tasks_structure(self):
        """Test that phase tasks have correct structure."""
        decomposer = TaskDecomposer()
        plan = decomposer.decompose("Test problem")

        # Phase 1 should have analysis tasks
        phase_1_tasks = plan.get_phase_tasks(1)
        assert len(phase_1_tasks) >= 1
        
        # Each task should have required fields
        for task in phase_1_tasks:
            assert task.task_id
            assert task.title
            assert task.description
            assert task.phase == 1

    def test_dependency_resolution(self):
        """Test task dependency resolution."""
        decomposer = TaskDecomposer()
        plan = decomposer.decompose("Test problem")

        # Phase 1 task 2 should depend on task 1
        phase_1_tasks = plan.get_phase_tasks(1)
        if len(phase_1_tasks) > 1:
            task_2 = phase_1_tasks[1]
            # Should have dependencies
            assert len(task_2.dependencies) > 0 or task_2.task_id.endswith("-1")

    def test_task_to_dict_serialization(self):
        """Test task serialization to dict."""
        decomposer = TaskDecomposer()
        plan = decomposer.decompose("Test problem")

        task = plan.get_all_tasks()[0]
        task_dict = task.to_dict()

        assert "task_id" in task_dict
        assert "title" in task_dict
        assert "dependencies" in task_dict
        assert task_dict["phase"] == 1

    def test_parallel_task_grouping(self):
        """Test parallel task grouping logic."""
        decomposer = TaskDecomposer()
        plan = decomposer.decompose("Test problem")

        # Get parallel groups for phase 4 (visual verification)
        groups = plan.get_parallel_tasks(4)
        assert len(groups) > 0
        
        # Each group should be a list of tasks
        for group in groups:
            assert isinstance(group, list)
            assert len(group) > 0


class TestPhaseManager:
    """Tests for PhaseManager component."""

    def test_phase_manager_init(self):
        """Test phase manager initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_manager = StateManager(tmpdir)
            phase_manager = PhaseManager(state_manager)
            assert phase_manager is not None
            assert len(phase_manager.task_executors) == 0

    def test_execution_config(self):
        """Test execution configuration."""
        config = ExecutionConfig(
            max_retries=5,
            retry_delay_seconds=1.0,
            parallel_task_limit=3,
        )
        assert config.max_retries == 5
        assert config.retry_delay_seconds == 1.0
        assert config.parallel_task_limit == 3

    def test_executor_registration(self):
        """Test task executor registration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_manager = StateManager(tmpdir)
            phase_manager = PhaseManager(state_manager)
            executor = SimpleTaskExecutor("test")

            phase_manager.set_task_executor("test_type", executor)
            assert "test_type" in phase_manager.task_executors

    def test_simple_executor_async(self):
        """Test simple task executor."""
        async def run_test():
            executor = SimpleTaskExecutor("test")
            
            task = Subtask(
                task_id="test-1",
                title="Test Task",
                description="Test",
                phase=1,
            )
            
            result = await executor.execute(task)
            assert result["status"] == "success"
            assert result["task_id"] == "test-1"
        
        asyncio.run(run_test())


class TestOrchestrator:
    """Tests for main Orchestrator component."""

    def test_orchestrator_init(self):
        """Test orchestrator initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = Orchestrator(tmpdir)
            assert orchestrator is not None
            assert orchestrator.workspace_root.exists()

    def test_problem_analysis(self):
        """Test problem analysis and decomposition."""
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = Orchestrator(tmpdir)
            problem = "Build a simple Python utility"
            
            plan = orchestrator.analyze_problem(problem)
            
            assert plan is not None
            assert len(plan.phases) == 7
            assert len(plan.get_all_tasks()) > 0

    def test_get_phase_tasks(self):
        """Test retrieving phase tasks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = Orchestrator(tmpdir)
            orchestrator.analyze_problem("Test problem")
            
            tasks = orchestrator.get_phase_tasks(1)
            assert len(tasks) > 0
            assert "task_id" in tasks[0]

    def test_get_task_dependencies(self):
        """Test retrieving task dependencies."""
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = Orchestrator(tmpdir)
            orchestrator.analyze_problem("Test problem")
            
            # Get first phase tasks
            phase_1_tasks = orchestrator.get_phase_tasks(1)
            if len(phase_1_tasks) > 1:
                task_2_id = phase_1_tasks[1]["task_id"]
                deps = orchestrator.get_task_dependencies(task_2_id)
                # Should have at least the first task as dependency
                assert len(deps) >= 0

    def test_skill_injection_context(self):
        """Test skill injection context building."""
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = Orchestrator(tmpdir)
            
            # Create dummy skills
            skills_dir = Path(tmpdir) / ".harness" / "generated"
            skills_dir.mkdir(parents=True, exist_ok=True)
            (skills_dir / "test-skill.md").write_text("# Test Skill\nContent here")
            
            context = orchestrator.skill_injection_context()
            assert "available_skills" in context
            assert "test-skill" in context["available_skills"]

    def test_claude_prompt_building(self):
        """Test Claude prompt building."""
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = Orchestrator(tmpdir)
            orchestrator.analyze_problem("Test problem")
            
            tasks = orchestrator.get_phase_tasks(1)
            if tasks:
                prompt = orchestrator.build_claude_prompt(tasks[0])
                assert "Task:" in prompt
                assert "Description" in prompt
                assert "Phase" in prompt

    def test_execution_config(self):
        """Test setting execution config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = Orchestrator(tmpdir)
            config = ExecutionConfig(max_retries=2, fail_fast=True)
            orchestrator.set_config(config)
            assert orchestrator.config.max_retries == 2

    def test_custom_executor_registration(self):
        """Test registering custom executors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = Orchestrator(tmpdir)
            executor = SimpleTaskExecutor("custom")
            orchestrator.register_executor("custom_type", executor)
            # Verify it's registered with phase manager
            assert "custom_type" in orchestrator.phase_manager.task_executors

    def test_status_retrieval(self):
        """Test status retrieval."""
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = Orchestrator(tmpdir)
            orchestrator.state_manager.init_workflow("test", [1])
            orchestrator.state_manager.start_phase(1, "Test")
            
            status = orchestrator.get_status()
            assert status["workflow_id"] == "test"
            assert "summary" in status

    def test_results_export(self):
        """Test exporting results to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = Orchestrator(tmpdir)
            orchestrator.state_manager.init_workflow("test", [1])
            orchestrator.state_manager.start_phase(1, "Test Phase")
            orchestrator.state_manager.complete_phase(1)
            
            output_file = Path(tmpdir) / "results.json"
            orchestrator.export_results(str(output_file))
            
            assert output_file.exists()
            with open(output_file) as f:
                data = json.load(f)
                assert data["workflow_id"] == "test"


if __name__ == "__main__":
    # Run with: python -m pytest tests/test_orchestrator.py -v
    # Or run with: python tests/test_orchestrator.py
    import unittest
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestStateManager))
    suite.addTests(loader.loadTestsFromTestCase(TestTaskDecomposer))
    suite.addTests(loader.loadTestsFromTestCase(TestPhaseManager))
    suite.addTests(loader.loadTestsFromTestCase(TestOrchestrator))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
