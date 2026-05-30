"""
Main ProjectAnalyzer class for comprehensive code analysis.

Orchestrates framework detection, pattern extraction, and artifact generation.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

from pattern_extractor import PatternExtractor
from mermaid_generator import MermaidGenerator


@dataclass
class FrameworkInfo:
    """Detected framework information."""
    name: str
    version: Optional[str] = None
    language: str = "javascript"
    package_manager: Optional[str] = None
    confidence: float = 0.0


@dataclass
class ProjectMetadata:
    """Project metadata."""
    name: str
    path: str
    framework: FrameworkInfo
    language: str
    file_count: int
    total_lines: int


class ProjectAnalyzer:
    """Main analyzer orchestrating all analysis operations."""

    def __init__(self, verbose: bool = False):
        """
        Initialize project analyzer.
        
        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.pattern_extractor = PatternExtractor()
        self.mermaid_generator = MermaidGenerator()
        self.metadata: Optional[ProjectMetadata] = None
        self.patterns: Dict[str, Any] = {}
        self.diagrams: Dict[str, str] = {}

    def analyze(self, project_path: str) -> Dict[str, Any]:
        """
        Analyze a project and generate artifacts.
        
        Args:
            project_path: Path to project root
            
        Returns:
            Dictionary containing analysis results
        """
        project_path = Path(project_path)

        if not project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")

        self._log(f"Starting analysis of {project_path}")

        # Step 1: Detect framework
        framework = self._detect_framework(project_path)
        self._log(f"Detected framework: {framework.name}")

        # Step 2: Extract patterns
        self.patterns = self.pattern_extractor.extract_from_project(project_path)
        self._log(f"Extracted patterns: {len(self.patterns)} pattern types")

        # Step 3: Generate diagrams
        self.diagrams = self._generate_all_diagrams()
        self._log(f"Generated {len(self.diagrams)} diagrams")

        # Step 4: Create project metadata
        self.metadata = self._create_metadata(project_path, framework)

        # Step 5: Generate output artifacts
        results = {
            "metadata": asdict(self.metadata),
            "framework": asdict(framework),
            "patterns": self.patterns,
            "diagrams": self.diagrams,
        }

        return results

    def _detect_framework(self, project_path: Path) -> FrameworkInfo:
        """
        Detect project framework and language.
        
        Args:
            project_path: Root project path
            
        Returns:
            FrameworkInfo object
        """
        framework = FrameworkInfo(name="generic", language="javascript")

        # Check package.json for dependencies
        package_json = project_path / "package.json"
        if package_json.exists():
            try:
                content = json.loads(package_json.read_text())
                deps = {**content.get("dependencies", {}), **content.get("devDependencies", {})}

                # Check for frameworks
                if "react" in deps:
                    framework = FrameworkInfo(
                        name="React",
                        version=deps.get("react", ""),
                        language="javascript",
                        confidence=0.95
                    )
                    if "typescript" in deps or "typescript" in content.get("devDependencies", {}):
                        framework.language = "typescript"

                elif "vue" in deps:
                    framework = FrameworkInfo(
                        name="Vue",
                        version=deps.get("vue", ""),
                        language="javascript",
                        confidence=0.95
                    )

                elif "@angular/core" in deps:
                    framework = FrameworkInfo(
                        name="Angular",
                        version=deps.get("@angular/core", ""),
                        language="typescript",
                        confidence=0.95
                    )

                elif "next" in deps:
                    framework = FrameworkInfo(
                        name="Next.js",
                        version=deps.get("next", ""),
                        language="typescript" if "typescript" in deps else "javascript",
                        confidence=0.95
                    )

                elif "nuxt" in deps:
                    framework = FrameworkInfo(
                        name="Nuxt",
                        version=deps.get("nuxt", ""),
                        language="javascript",
                        confidence=0.95
                    )

                # Detect package manager
                if (project_path / "yarn.lock").exists():
                    framework.package_manager = "yarn"
                elif (project_path / "pnpm-lock.yaml").exists():
                    framework.package_manager = "pnpm"
                else:
                    framework.package_manager = "npm"

            except json.JSONDecodeError:
                pass

        # Check for Python
        if (project_path / "requirements.txt").exists() or any(project_path.glob("*.py")):
            framework = FrameworkInfo(
                name="Python",
                language="python",
                confidence=0.9
            )

            # Detect Python frameworks
            try:
                req_file = project_path / "requirements.txt"
                if req_file.exists():
                    content = req_file.read_text()
                    if "django" in content:
                        framework.name = "Django"
                    elif "flask" in content:
                        framework.name = "Flask"
                    elif "fastapi" in content:
                        framework.name = "FastAPI"
            except Exception:
                pass

        return framework

    def _generate_all_diagrams(self) -> Dict[str, str]:
        """Generate all diagram types."""
        diagrams = {}

        # Component tree
        components = self.patterns.get("components", [])
        context_data = {"contexts": self.patterns.get("contexts", [])}
        diagrams["component_tree"] = self.mermaid_generator.generate_component_tree(
            components, context_data
        )

        # Data flow
        api_calls = self.patterns.get("api_calls", [])
        diagrams["data_flow"] = self.mermaid_generator.generate_data_flow(
            api_calls, self.patterns.get("imports", {})
        )

        # Dependency graph
        diagrams["dependency_graph"] = self.mermaid_generator.generate_dependency_graph(
            self.patterns.get("imports", {})
        )

        # Test coverage
        tests = self.patterns.get("tests", [])
        diagrams["test_coverage"] = self.mermaid_generator.generate_test_coverage(tests)

        return diagrams

    def _create_metadata(self, project_path: Path, framework: FrameworkInfo) -> ProjectMetadata:
        """Create project metadata."""
        # Count files
        file_count = sum(1 for _ in project_path.rglob("*") if _.is_file())

        # Count lines
        total_lines = 0
        source_extensions = {'.js', '.jsx', '.ts', '.tsx', '.py', '.vue', '.json'}
        for file_path in project_path.rglob("*"):
            if file_path.suffix in source_extensions:
                try:
                    total_lines += len(file_path.read_text(errors='ignore').split('\n'))
                except Exception:
                    pass

        return ProjectMetadata(
            name=project_path.name,
            path=str(project_path),
            framework=framework,
            language=framework.language,
            file_count=file_count,
            total_lines=total_lines,
        )

    def generate_artifacts(self, output_dir: str = None) -> Dict[str, Path]:
        """
        Generate and save output artifacts.
        
        Args:
            output_dir: Output directory (defaults to .harness/generated/)
            
        Returns:
            Dictionary of artifact paths
        """
        if not self.patterns:
            raise ValueError("No analysis performed. Run analyze() first.")

        if output_dir is None:
            output_dir = ".harness/generated"

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        artifacts = {}

        # 1. Save patterns.json
        patterns_file = output_path / "patterns.json"
        patterns_file.write_text(json.dumps(self.patterns, indent=2))
        artifacts["patterns"] = patterns_file

        # 2. Save diagrams to folder
        diagrams_dir = output_path / "diagrams"
        diagrams_dir.mkdir(exist_ok=True)
        for name, diagram in self.diagrams.items():
            diagram_file = self.mermaid_generator.save_diagram(name, diagram, diagrams_dir)
            artifacts[f"diagram_{name}"] = diagram_file

        # 3. Create architecture.md with embedded diagrams
        arch_md = self.mermaid_generator.create_embedded_markdown(
            self.diagrams,
            title=f"{self.metadata.name} Architecture"
        )
        arch_file = output_path / "architecture.md"
        arch_file.write_text(arch_md)
        artifacts["architecture"] = arch_file

        # 4. Create design-tokens.json
        tokens = self._generate_design_tokens()
        tokens_file = output_path / "design-tokens.json"
        tokens_file.write_text(json.dumps(tokens, indent=2))
        artifacts["design_tokens"] = tokens_file

        # 5. Save metadata
        metadata_file = output_path / "metadata.json"
        metadata_file.write_text(json.dumps(asdict(self.metadata), indent=2, default=str))
        artifacts["metadata"] = metadata_file

        self._log(f"Generated {len(artifacts)} artifacts in {output_path}")

        return artifacts

    def _generate_design_tokens(self) -> Dict[str, Any]:
        """Generate design tokens from patterns."""
        return {
            "components": len(self.patterns.get("components", [])),
            "hooks": len(self.patterns.get("hooks", [])),
            "api_endpoints": len(self.patterns.get("api_calls", [])),
            "test_cases": len(self.patterns.get("tests", [])),
            "type_definitions": len(self.patterns.get("types", [])),
            "contexts": len(self.patterns.get("contexts", [])),
            "external_dependencies": len(self.patterns.get("imports", {})),
            "common_hooks": self.patterns.get("hooks", [])[:10],
            "frameworks_detected": list(self.patterns.get("imports", {}).keys())[:10],
        }

    def _log(self, message: str) -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(f"[ProjectAnalyzer] {message}")

    def get_analysis_summary(self) -> str:
        """
        Get a human-readable summary of the analysis.
        
        Returns:
            Summary string
        """
        if not self.metadata:
            return "No analysis performed"

        lines = [
            f"Project: {self.metadata.name}",
            f"Framework: {self.metadata.framework.name} ({self.metadata.framework.language})",
            f"Files: {self.metadata.file_count}",
            f"Lines of Code: {self.metadata.total_lines}",
            "",
            "Patterns Detected:",
            f"  - Components: {len(self.patterns.get('components', []))}",
            f"  - Hooks: {len(self.patterns.get('hooks', []))}",
            f"  - API Calls: {len(self.patterns.get('api_calls', []))}",
            f"  - Tests: {len(self.patterns.get('tests', []))}",
            f"  - Type Definitions: {len(self.patterns.get('types', []))}",
            f"  - Contexts: {len(self.patterns.get('contexts', []))}",
            f"  - Dependencies: {len(self.patterns.get('imports', {}))}",
            "",
            "Diagrams Generated:",
            f"  - {len(self.diagrams)} architecture diagrams",
        ]

        return "\n".join(lines)
