"""
Tests for the Skill Builder Engine.

Tests pattern extraction, diagram generation, and project analysis.
"""

import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
engine_path = str(Path(__file__).parent.parent)
if engine_path not in sys.path:
    sys.path.insert(0, engine_path)

# Import directly from parent package
from analyzer import ProjectAnalyzer, FrameworkInfo
from pattern_extractor import PatternExtractor
from mermaid_generator import MermaidGenerator


class TestPatternExtractor(unittest.TestCase):
    """Tests for PatternExtractor."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = PatternExtractor()

    def test_find_react_hooks(self):
        """Test React hook detection."""
        code = """
        const [count, setCount] = useState(0);
        useEffect(() => {
            console.log('mounted');
        }, []);
        const ctx = useContext(AppContext);
        """

        hooks = self.extractor._find_react_hooks(code)

        self.assertIn("useState", hooks)
        self.assertIn("useEffect", hooks)
        self.assertIn("useContext", hooks)

    def test_find_components(self):
        """Test component detection."""
        code = """
        export const Button = (props) => {
            return <button>{props.children}</button>;
        };
        
        export function Header() {
            return <header>Header</header>;
        }
        """

        components = self.extractor._find_components(code, Path("Button.jsx"))

        self.assertTrue(any(c["name"] == "Button" for c in components))
        self.assertTrue(any(c["name"] == "Header" for c in components))

    def test_find_imports_with_destructuring(self):
        """Test import detection with destructuring."""
        code = """
        import { useState, useEffect } from 'react';
        import { Button, Card } from './components';
        import * as api from './api';
        """

        imports = self.extractor._find_imports(code)

        self.assertIn("react", imports)
        self.assertIn("./components", imports)
        self.assertIn("./api", imports)
        self.assertIn("useState", imports["react"])

    def test_find_api_calls(self):
        """Test API call detection."""
        code = """
        fetch('/api/users').then(r => r.json());
        axios.get('/api/data');
        const query = useQuery({
            queryFn: async () => fetch('/api/posts')
        });
        """

        api_calls = self.extractor._find_api_calls(code)

        self.assertTrue(len(api_calls) > 0)
        self.assertTrue(any(call.get("type") == "fetch" for call in api_calls))

    def test_find_test_patterns(self):
        """Test test pattern detection."""
        code = """
        describe('Button Component', () => {
            it('renders correctly', () => {
                expect(true).toBe(true);
            });
            
            test('handles click', () => {
                // test code
            });
        });
        """

        tests = self.extractor._find_test_patterns(code)

        self.assertTrue(len(tests) > 0)
        self.assertTrue(any(t.get("type") == "describe" for t in tests))
        self.assertTrue(any(t.get("type") == "test" for t in tests))

    def test_find_type_definitions(self):
        """Test TypeScript type detection."""
        code = """
        interface User {
            id: number;
            name: string;
        }
        
        type Status = 'active' | 'inactive';
        """

        types = self.extractor._find_type_definitions(code)

        self.assertIn("User", types)
        self.assertIn("Status", types)

    def test_find_context_usage(self):
        """Test Context API detection."""
        code = """
        const AppContext = createContext(null);
        const ThemeContext = React.createContext({});
        const user = useContext(AppContext);
        """

        contexts = self.extractor._find_context_usage(code)

        self.assertIn("AppContext", contexts)
        self.assertIn("ThemeContext", contexts)

    def test_analyze_file_js(self):
        """Test single file analysis."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "component.jsx"
            file_path.write_text("""
            export const MyComponent = () => {
                const [state, setState] = useState(0);
                return <div>{state}</div>;
            };
            """)

            patterns = self.extractor.analyze_file(file_path)

            self.assertIn("hooks", patterns)
            self.assertIn("components", patterns)

    def test_extract_json_patterns(self):
        """Test JSON pattern extraction."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_file = Path(tmpdir) / "package.json"
            pkg_file.write_text(json.dumps({
                "dependencies": {"react": "^18.0.0"},
                "devDependencies": {"jest": "^27.0.0"}
            }))

            patterns = self.extractor._extract_json_patterns(
                pkg_file.read_text(),
                pkg_file
            )

            self.assertIn("dependencies", patterns)
            self.assertIn("react", patterns["dependencies"])


class TestMermaidGenerator(unittest.TestCase):
    """Tests for MermaidGenerator."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = MermaidGenerator()

    def test_generate_component_tree(self):
        """Test component tree generation."""
        components = [
            {"name": "App", "type": "component"},
            {"name": "Header", "type": "component"},
            {"name": "Footer", "type": "component"},
        ]

        diagram = self.generator.generate_component_tree(components)

        self.assertIn("graph TD", diagram)
        self.assertIn("App", diagram)
        self.assertIn("Header", diagram)

    def test_generate_component_tree_empty(self):
        """Test component tree with empty input."""
        diagram = self.generator.generate_component_tree([])

        self.assertIn("graph TD", diagram)
        self.assertIn("No components found", diagram)

    def test_generate_data_flow(self):
        """Test data flow diagram generation."""
        api_calls = [
            {"endpoint": "/api/users", "type": "fetch"},
            {"endpoint": "/api/posts", "type": "axios", "method": "get"},
        ]

        diagram = self.generator.generate_data_flow(api_calls)

        self.assertIn("graph LR", diagram)
        self.assertIn("Client", diagram)
        self.assertIn("API", diagram)

    def test_generate_dependency_graph(self):
        """Test dependency graph generation."""
        imports = {
            "react": ["useState", "useEffect"],
            "axios": ["default"],
            "./api": ["fetchUsers"],
        }

        diagram = self.generator.generate_dependency_graph(imports)

        self.assertIn("graph TD", diagram)
        self.assertIn("react", diagram)

    def test_generate_file_structure(self):
        """Test file structure diagram generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "src").mkdir()
            (tmppath / "src" / "components").mkdir()
            (tmppath / "src" / "components" / "Button.jsx").touch()
            (tmppath / "package.json").touch()

            diagram = self.generator.generate_file_structure(tmppath)

            self.assertIn("graph TD", diagram)
            self.assertIn("src", diagram)

    def test_generate_test_coverage(self):
        """Test test coverage diagram generation."""
        tests = [
            {"type": "describe", "name": "Button"},
            {"type": "test", "name": "renders correctly"},
        ]

        diagram = self.generator.generate_test_coverage(tests)

        self.assertIn("graph TD", diagram)
        self.assertIn("TestSuite", diagram)

    def test_save_diagram(self):
        """Test diagram file saving."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            diagram = "graph TD\n    A[Test]"

            path = self.generator.save_diagram("test", diagram, output_dir)

            self.assertTrue(path.exists())
            self.assertEqual(path.read_text(), diagram)

    def test_create_embedded_markdown(self):
        """Test embedded markdown creation."""
        diagrams = {
            "component_tree": "graph TD\n    A[App]",
            "data_flow": "graph LR\n    A[Client] --> B[API]",
        }

        markdown = self.generator.create_embedded_markdown(diagrams)

        self.assertIn("# Architecture Analysis", markdown)
        self.assertIn("```mermaid", markdown)
        self.assertIn("Component Tree", markdown)


class TestProjectAnalyzer(unittest.TestCase):
    """Tests for ProjectAnalyzer."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ProjectAnalyzer(verbose=False)

    def test_detect_framework_react(self):
        """Test React framework detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_file = Path(tmpdir) / "package.json"
            pkg_file.write_text(json.dumps({
                "dependencies": {"react": "^18.0.0"}
            }))

            framework = self.analyzer._detect_framework(Path(tmpdir))

            self.assertEqual(framework.name, "React")
            self.assertGreater(framework.confidence, 0.9)

    def test_detect_framework_vue(self):
        """Test Vue framework detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_file = Path(tmpdir) / "package.json"
            pkg_file.write_text(json.dumps({
                "dependencies": {"vue": "^3.0.0"}
            }))

            framework = self.analyzer._detect_framework(Path(tmpdir))

            self.assertEqual(framework.name, "Vue")

    def test_detect_framework_angular(self):
        """Test Angular framework detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_file = Path(tmpdir) / "package.json"
            pkg_file.write_text(json.dumps({
                "dependencies": {"@angular/core": "^15.0.0"}
            }))

            framework = self.analyzer._detect_framework(Path(tmpdir))

            self.assertEqual(framework.name, "Angular")

    def test_detect_framework_typescript(self):
        """Test TypeScript detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_file = Path(tmpdir) / "package.json"
            pkg_file.write_text(json.dumps({
                "dependencies": {"react": "^18.0.0"},
                "devDependencies": {"typescript": "^4.0.0"}
            }))

            framework = self.analyzer._detect_framework(Path(tmpdir))

            self.assertEqual(framework.language, "typescript")

    def test_detect_package_manager_npm(self):
        """Test npm package manager detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "package.json").write_text("{}")

            framework = self.analyzer._detect_framework(Path(tmpdir))

            self.assertEqual(framework.package_manager, "npm")

    def test_detect_package_manager_yarn(self):
        """Test yarn package manager detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "package.json").write_text("{}")
            (Path(tmpdir) / "yarn.lock").touch()

            framework = self.analyzer._detect_framework(Path(tmpdir))

            self.assertEqual(framework.package_manager, "yarn")

    def test_analyze_simple_project(self):
        """Test analyzing a simple project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create package.json
            (tmppath / "package.json").write_text(json.dumps({
                "name": "test-app",
                "dependencies": {"react": "^18.0.0"}
            }))

            # Create source file
            (tmppath / "src").mkdir()
            (tmppath / "src" / "App.jsx").write_text("""
            export const App = () => {
                const [count, setCount] = useState(0);
                return <div>{count}</div>;
            };
            """)

            results = self.analyzer.analyze(str(tmppath))

            self.assertIn("metadata", results)
            self.assertIn("framework", results)
            self.assertIn("patterns", results)
            self.assertIn("diagrams", results)
            self.assertEqual(results["framework"]["name"], "React")

    def test_generate_artifacts(self):
        """Test artifact generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create package.json
            (tmppath / "package.json").write_text(json.dumps({
                "name": "test-app",
                "dependencies": {"react": "^18.0.0"}
            }))

            # Create source file
            (tmppath / "src").mkdir()
            (tmppath / "src" / "App.jsx").write_text("""
            export const App = () => {
                return <div>Hello</div>;
            };
            """)

            self.analyzer.analyze(str(tmppath))

            artifacts = self.analyzer.generate_artifacts(f"{tmpdir}/.harness/generated")

            self.assertIn("patterns", artifacts)
            self.assertIn("architecture", artifacts)
            self.assertIn("design_tokens", artifacts)
            self.assertTrue(artifacts["patterns"].exists())

    def test_get_analysis_summary(self):
        """Test analysis summary generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            (tmppath / "package.json").write_text(json.dumps({
                "name": "test-app",
                "dependencies": {"react": "^18.0.0"}
            }))

            (tmppath / "src").mkdir()
            (tmppath / "src" / "App.jsx").write_text("export const App = () => <div>App</div>;")

            self.analyzer.analyze(str(tmppath))
            summary = self.analyzer.get_analysis_summary()

            # Check for key summary components (project name may vary in temp dir)
            self.assertIn("React", summary)
            self.assertIn("Patterns Detected:", summary)
            self.assertIn("Components:", summary)

    def test_analyze_nonexistent_project(self):
        """Test analysis of nonexistent project."""
        with self.assertRaises(ValueError):
            self.analyzer.analyze("/nonexistent/path")

    def test_generate_artifacts_without_analysis(self):
        """Test artifact generation without prior analysis."""
        with self.assertRaises(ValueError):
            self.analyzer.generate_artifacts()


if __name__ == "__main__":
    unittest.main()
