"""
Mermaid diagram generation for architecture visualization.

Generates:
- Component tree diagrams (React/Vue/Angular)
- Data flow architecture diagrams
- Module/service dependency graphs
- File structure trees
"""

from typing import Dict, List, Set, Any, Tuple
from pathlib import Path
import json


class MermaidGenerator:
    """Generate Mermaid diagrams for project architecture."""

    def __init__(self):
        """Initialize Mermaid generator."""
        self.diagrams: Dict[str, str] = {}

    def generate_component_tree(self, components: List[Dict], context_data: Dict = None) -> str:
        """
        Generate component tree diagram.
        
        Args:
            components: List of component data
            context_data: Additional context information
            
        Returns:
            Mermaid diagram as string
        """
        if not components:
            return "graph TD\n    A[No components found]"

        lines = ["graph TD"]

        # Create component nodes
        component_names = set()
        for comp in components:
            name = comp.get("name", "Unknown")
            component_names.add(name)
            comp_type = comp.get("type", "component")
            lines.append(f"    {name}[{name}<br/>({comp_type})]")

        # Add context nodes if available
        if context_data and "contexts" in context_data:
            for ctx in context_data["contexts"]:
                lines.append(f"    {ctx}{{Context: {ctx}}}")

        # Simple hierarchy: typically App at root
        if "App" in component_names and len(components) > 1:
            for comp in components:
                name = comp.get("name", "Unknown")
                if name != "App" and name in component_names:
                    lines.append(f"    App --> {name}")

        return "\n".join(lines)

    def generate_data_flow(self, api_calls: List[Dict], imports: Dict[str, List[str]] = None) -> str:
        """
        Generate data flow architecture diagram.
        
        Args:
            api_calls: List of API calls detected
            imports: Import/dependency information
            
        Returns:
            Mermaid diagram as string
        """
        lines = ["graph LR"]

        # API flow nodes
        lines.append("    Client[Client/UI]")
        lines.append("    State[State Management]")

        api_endpoints = set()
        for call in api_calls:
            endpoint = call.get("endpoint", "unknown")
            if endpoint:
                api_endpoints.add(endpoint)

        if api_endpoints:
            lines.append("    API[API Layer]")
            lines.append("    Client --> State")
            lines.append("    State --> API")

            # Simplified endpoints (first 5)
            for i, endpoint in enumerate(list(api_endpoints)[:5]):
                # Extract base path
                base = endpoint.split('/')[0] if endpoint else "endpoint"
                service_id = f"Service{i}"
                lines.append(f"    API --> {service_id}[{service_id}: {base}]")

        else:
            lines.append("    Client --> State")

        lines.append("    State --> Render[Render]")

        return "\n".join(lines)

    def generate_dependency_graph(self, imports: Dict[str, List[str]], max_items: int = 15) -> str:
        """
        Generate module/dependency graph.
        
        Args:
            imports: Dictionary of imports and their usage
            max_items: Maximum items to show in diagram
            
        Returns:
            Mermaid diagram as string
        """
        if not imports:
            return "graph TD\n    A[No dependencies detected]"

        lines = ["graph TD"]

        # Categorize dependencies
        internal_deps = {}
        external_deps = {}

        for module, names in imports.items():
            # Simplified module names
            if any(x in module for x in ['react', 'vue', 'angular', './']) or '/' in module:
                internal_deps[module] = names
            else:
                external_deps[module] = names

        # Show external dependencies (libraries)
        shown = 0
        for module in list(external_deps.keys())[:5]:
            node_name = module.replace('-', '_').replace('@', '').replace('/', '_')
            lines.append(f"    App --> {node_name}[{module}]")
            shown += 1

        # Show internal modules
        for module in list(internal_deps.keys())[:5]:
            short_name = module.split('/')[-1] if '/' in module else module
            node_name = short_name.replace('-', '_').replace('.', '_')
            lines.append(f"    App --> {node_name}[{short_name}]")
            shown += 1

        if not lines[1:]:  # Only header
            lines.append("    App[Application]")

        return "\n".join(lines)

    def generate_file_structure(self, directory: Path, max_depth: int = 3, max_items: int = 20) -> str:
        """
        Generate file structure tree diagram.
        
        Args:
            directory: Root directory to visualize
            max_depth: Maximum depth to traverse
            max_items: Maximum total items to show
            
        Returns:
            Mermaid diagram as string
        """
        lines = ["graph TD"]

        # Build tree
        root_name = directory.name or "project"
        lines.append(f"    Root[📁 {root_name}]")

        items_added = 0
        self._add_tree_nodes(directory, "Root", lines, 0, max_depth, max_items)

        return "\n".join(lines)

    def _add_tree_nodes(self, path: Path, parent_id: str, lines: List[str], depth: int, max_depth: int, max_items: int) -> int:
        """
        Recursively add tree nodes.
        
        Args:
            path: Current path
            parent_id: Parent node ID
            lines: Lines to append to
            depth: Current depth
            max_depth: Maximum depth
            max_items: Maximum items to add
            
        Returns:
            Number of items added
        """
        if depth > max_depth or len(lines) > max_items:
            return 0

        items = 0

        # Skip hidden and common exclusions
        skip_dirs = {'.git', 'node_modules', '.next', 'dist', '__pycache__', '.venv', '.pytest_cache'}

        try:
            entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name))

            for entry in entries:
                if entry.name.startswith('.') and entry.name not in {'.env', '.gitignore'}:
                    continue
                if entry.name in skip_dirs:
                    continue
                if len(lines) > max_items:
                    break

                node_id = f"{parent_id}_{entry.name.replace('.', '_').replace('-', '_')}"

                if entry.is_dir():
                    lines.append(f"    {node_id}[📁 {entry.name}/]")
                    lines.append(f"    {parent_id} --> {node_id}")
                    items += 1 + self._add_tree_nodes(entry, node_id, lines, depth + 1, max_depth, max_items)
                else:
                    # Show file with extension icon
                    suffix = entry.suffix or "file"
                    icon = self._get_file_icon(suffix)
                    lines.append(f"    {node_id}[{icon} {entry.name}]")
                    lines.append(f"    {parent_id} --> {node_id}")
                    items += 1

        except (PermissionError, OSError):
            pass

        return items

    def _get_file_icon(self, suffix: str) -> str:
        """Get emoji icon for file type."""
        icons = {
            '.js': '⚙️',
            '.jsx': '⚛️',
            '.ts': '📘',
            '.tsx': '⚛️',
            '.json': '📄',
            '.md': '📝',
            '.py': '🐍',
            '.yaml': '⚙️',
            '.yml': '⚙️',
            '.css': '🎨',
            '.scss': '🎨',
            '.html': '🌐',
        }
        return icons.get(suffix, '📄')

    def generate_test_coverage(self, tests: List[Dict]) -> str:
        """
        Generate test coverage diagram.
        
        Args:
            tests: List of test cases
            
        Returns:
            Mermaid diagram as string
        """
        if not tests:
            return "graph TD\n    A[No tests found]"

        lines = ["graph TD"]

        # Group tests by describe block
        test_groups = {}
        for test in tests:
            test_type = test.get("type", "test")
            name = test.get("name", "Unknown")

            if test_type == "describe":
                test_groups[name] = []
            elif "describe" in test:
                parent = test.get("describe")
                if parent not in test_groups:
                    test_groups[parent] = []
                test_groups[parent].append(name)

        # Build diagram
        lines.append("    TestSuite[Test Suite]")

        for i, (group_name, tests_list) in enumerate(list(test_groups.items())[:10]):
            group_id = f"Group{i}"
            lines.append(f"    {group_id}[{group_name}]")
            lines.append(f"    TestSuite --> {group_id}")

            for j, test_name in enumerate(tests_list[:3]):
                test_id = f"{group_id}_Test{j}"
                lines.append(f"    {test_id}[✓ {test_name}]")
                lines.append(f"    {group_id} --> {test_id}")

        return "\n".join(lines)

    def save_diagram(self, name: str, diagram: str, output_dir: Path) -> Path:
        """
        Save diagram to file.
        
        Args:
            name: Diagram name
            diagram: Mermaid diagram content
            output_dir: Output directory
            
        Returns:
            Path to saved file
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir / f"{name}.mmd"
        file_path.write_text(diagram)
        return file_path

    def create_embedded_markdown(self, diagrams: Dict[str, str], title: str = "Architecture") -> str:
        """
        Create markdown with embedded Mermaid diagrams.
        
        Args:
            diagrams: Dictionary of diagram name -> content
            title: Document title
            
        Returns:
            Markdown content with embedded diagrams
        """
        lines = [
            f"# {title} Analysis",
            "",
            "This document contains architecture diagrams generated from code analysis.",
            "",
        ]

        for diagram_name, diagram_content in diagrams.items():
            # Convert name to readable title
            title_case = diagram_name.replace('_', ' ').title()

            lines.append(f"## {title_case}")
            lines.append("")
            lines.append("```mermaid")
            lines.append(diagram_content)
            lines.append("```")
            lines.append("")

        return "\n".join(lines)
