"""
Pattern extraction for various code frameworks and languages.

Detects:
- React hooks, components, context API usage
- TypeScript type conventions
- API call patterns
- Testing patterns (Jest/Vitest)
- Module dependencies
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass, asdict


@dataclass
class CodePattern:
    """Represents a detected code pattern."""
    name: str
    pattern_type: str  # e.g., "react_hook", "api_call", "test_suite"
    frequency: int
    files: List[str]
    details: Dict[str, Any]


class PatternExtractor:
    """Extracts code patterns from project files."""

    def __init__(self):
        """Initialize pattern extractor."""
        self.patterns: Dict[str, CodePattern] = {}
        self.file_patterns: Dict[str, List[str]] = {}
        self.dependencies: Dict[str, Set[str]] = {}

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a single file for patterns.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Dictionary of detected patterns in the file
        """
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            suffix = file_path.suffix.lower()

            patterns_found = {}

            if suffix in ['.jsx', '.tsx', '.js', '.ts']:
                patterns_found = self._extract_js_patterns(content, file_path)

            elif suffix == '.json':
                patterns_found = self._extract_json_patterns(content, file_path)

            return patterns_found

        except Exception as e:
            return {"error": str(e)}

    def _extract_js_patterns(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Extract patterns from JavaScript/TypeScript files."""
        patterns = {
            "hooks": self._find_react_hooks(content),
            "components": self._find_components(content, file_path),
            "imports": self._find_imports(content),
            "api_calls": self._find_api_calls(content),
            "tests": self._find_test_patterns(content),
            "types": self._find_type_definitions(content),
            "context": self._find_context_usage(content),
        }
        return {k: v for k, v in patterns.items() if v}

    def _extract_json_patterns(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Extract patterns from JSON files (package.json, config, etc)."""
        try:
            data = json.loads(content)
            patterns = {}

            if "package.json" in str(file_path):
                patterns["dependencies"] = list(data.get("dependencies", {}).keys())
                patterns["dev_dependencies"] = list(data.get("devDependencies", {}).keys())
                patterns["type"] = data.get("type", "commonjs")
                patterns["scripts"] = list(data.get("scripts", {}).keys())

            return patterns

        except json.JSONDecodeError:
            return {}

    def _find_react_hooks(self, content: str) -> List[str]:
        """Find React hooks used in code."""
        hooks = []
        hook_patterns = [
            r'use[A-Z]\w*\s*\(',  # Custom hooks
            r'useState\s*\(',
            r'useEffect\s*\(',
            r'useContext\s*\(',
            r'useReducer\s*\(',
            r'useCallback\s*\(',
            r'useMemo\s*\(',
            r'useRef\s*\(',
            r'useLayoutEffect\s*\(',
            r'useQuery\s*\(',
            r'useMutation\s*\(',
            r'useNavigate\s*\(',
            r'useParams\s*\(',
            r'useLocation\s*\(',
        ]

        for pattern in hook_patterns:
            matches = re.findall(pattern, content)
            if matches:
                hook_name = re.match(r'(\w+)', pattern).group(1)
                hooks.extend([m.replace('(', '').strip() for m in matches])

        return list(set(hooks))

    def _find_components(self, content: str, file_path: Path) -> List[Dict[str, str]]:
        """Find React/Vue components."""
        components = []

        # React functional components
        export_patterns = [
            r'export\s+(?:default\s+)?(?:const|function)\s+(\w+)\s*=\s*(?:\(|{)',
            r'export\s+(?:default\s+)?(?:function\s+)?(\w+)\s*\(',
            r'function\s+(\w+)\s*\(.*?\)\s*{.*?return',
        ]

        for pattern in export_patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                components.append({
                    "name": match.group(1),
                    "file": str(file_path),
                    "type": "functional_component"
                })

        return components

    def _find_imports(self, content: str) -> Dict[str, List[str]]:
        """Extract import statements and dependencies."""
        imports = {}

        # Pattern 1: import { x, y } from 'module'
        pattern1 = r"import\s+{([^}]+)}\s+from\s+['\"]([^'\"]+)['\"]"
        for match in re.finditer(pattern1, content):
            items = match.group(1)
            module = match.group(2)
            if module not in imports:
                imports[module] = []
            imports[module].extend([n.strip() for n in items.split(',')])

        # Pattern 2: import default as X from 'module' or import X from 'module'
        pattern2 = r"import\s+(?:default\s+as\s+)?(\w+)\s+from\s+['\"]([^'\"]+)['\"]"
        for match in re.finditer(pattern2, content):
            name = match.group(1)
            module = match.group(2)
            if module not in imports:
                imports[module] = []
            imports[module].append(name)

        # Pattern 3: import * as X from 'module'
        pattern3 = r"import\s+\*\s+as\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]"
        for match in re.finditer(pattern3, content):
            name = match.group(1)
            module = match.group(2)
            if module not in imports:
                imports[module] = []
            imports[module].append(name)

        return imports

    def _find_api_calls(self, content: str) -> List[Dict[str, str]]:
        """Detect API call patterns."""
        api_calls = []

        # fetch calls
        fetch_pattern = r'fetch\s*\(\s*["\']([^"\']+)["\']'
        for match in re.finditer(fetch_pattern, content):
            api_calls.append({
                "type": "fetch",
                "endpoint": match.group(1)
            })

        # axios/superagent calls
        axios_pattern = r'(?:axios|request|http)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
        for match in re.finditer(axios_pattern, content):
            api_calls.append({
                "type": "axios",
                "method": match.group(1),
                "endpoint": match.group(2)
            })

        # Query/mutation calls
        query_pattern = r'(?:useQuery|useMutation)\s*\(\s*\{[^}]*queryFn["\']?\s*:\s*(?:async\s+)?\([^)]*\)\s*=>\s*(?:fetch|axios|request)[.\w]*\('
        if re.search(query_pattern, content):
            api_calls.append({
                "type": "react_query",
                "usage": "found"
            })

        return api_calls

    def _find_test_patterns(self, content: str) -> List[Dict[str, str]]:
        """Detect test patterns (Jest/Vitest)."""
        tests = []

        # describe blocks
        describe_pattern = r'describe\s*\(\s*["\']([^"\']+)["\']'
        for match in re.finditer(describe_pattern, content):
            tests.append({
                "type": "describe",
                "name": match.group(1)
            })

        # test/it blocks
        test_pattern = r'(?:test|it)\s*\(\s*["\']([^"\']+)["\']'
        for match in re.finditer(test_pattern, content):
            tests.append({
                "type": "test",
                "name": match.group(1)
            })

        return tests

    def _find_type_definitions(self, content: str) -> List[str]:
        """Extract TypeScript type definitions."""
        types = []

        # interface definitions
        interface_pattern = r'(?:export\s+)?interface\s+(\w+)'
        types.extend(re.findall(interface_pattern, content))

        # type definitions
        type_pattern = r'(?:export\s+)?type\s+(\w+)\s*='
        types.extend(re.findall(type_pattern, content))

        return list(set(types))

    def _find_context_usage(self, content: str) -> List[str]:
        """Detect React Context API usage."""
        contexts = []

        # createContext
        create_pattern = r'(?:const|export\s+const)\s+(\w+Context)\s*=\s*(?:React\.)?createContext'
        contexts.extend(re.findall(create_pattern, content))

        # useContext
        use_pattern = r'useContext\s*\(\s*(\w+Context)\s*\)'
        contexts.extend(re.findall(use_pattern, content))

        return list(set(contexts))

    def extract_from_project(self, project_path: Path, extensions: List[str] = None) -> Dict[str, Any]:
        """
        Extract patterns from entire project.
        
        Args:
            project_path: Root path of the project
            extensions: File extensions to analyze (default: common web dev)
            
        Returns:
            Aggregated patterns across project
        """
        if extensions is None:
            extensions = ['.js', '.jsx', '.ts', '.tsx', '.json', '.vue', '.py']

        all_patterns = {
            "hooks": [],
            "components": [],
            "api_calls": [],
            "tests": [],
            "imports": {},
            "types": [],
            "contexts": [],
        }

        for ext in extensions:
            for file_path in project_path.rglob(f"*{ext}"):
                # Skip node_modules, .next, dist, etc.
                if any(part in file_path.parts for part in ['node_modules', '.next', 'dist', '.venv', '__pycache__']):
                    continue

                file_patterns = self.analyze_file(file_path)

                # Aggregate patterns
                if "hooks" in file_patterns:
                    all_patterns["hooks"].extend(file_patterns["hooks"])
                if "components" in file_patterns:
                    all_patterns["components"].extend(file_patterns["components"])
                if "api_calls" in file_patterns:
                    all_patterns["api_calls"].extend(file_patterns["api_calls"])
                if "tests" in file_patterns:
                    all_patterns["tests"].extend(file_patterns["tests"])
                if "imports" in file_patterns:
                    for module, names in file_patterns["imports"].items():
                        if module not in all_patterns["imports"]:
                            all_patterns["imports"][module] = []
                        all_patterns["imports"][module].extend(names)
                if "types" in file_patterns:
                    all_patterns["types"].extend(file_patterns["types"])
                if "context" in file_patterns:
                    all_patterns["contexts"].extend(file_patterns["context"])

        # Deduplicate and count
        all_patterns["hooks"] = list(set(all_patterns["hooks"]))
        all_patterns["components"] = self._deduplicate_components(all_patterns["components"])
        all_patterns["types"] = list(set(all_patterns["types"]))
        all_patterns["contexts"] = list(set(all_patterns["contexts"]))

        return all_patterns

    def _deduplicate_components(self, components: List[Dict]) -> List[Dict]:
        """Deduplicate components by name."""
        seen = {}
        for comp in components:
            name = comp.get("name")
            if name not in seen:
                seen[name] = comp
        return list(seen.values())
