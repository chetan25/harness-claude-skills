# Phase 1.3: Claude Commands Integration

**Status:** ✅ COMPLETE

## Overview

Phase 1.3 implements the command parsing, routing, and execution system for Harness Claude Skills. This layer enables Claude to interact with the orchestrator through clean, natural @harness commands.

## Architecture

```
Command String (@harness orchestrate "task")
        ↓
   CommandParser (parse & extract args)
        ↓
   CommandValidator (validate inputs)
        ↓
   CommandRouter (route to handler)
        ↓
   Command Handler (execute)
        ↓
   CommandFormatter (format for Claude)
        ↓
   Output String (markdown)
```

## Modules Created

### 1. **commands.py** - Command Definitions & Handlers
Defines all available commands and their execution logic.

**Key Classes:**
- `CommandType` - Enum of 5 command types
- `CommandArgs` - Data class for parsed arguments
- `CommandValidator` - Validates command arguments
- `CommandFormatter` - Formats output for Claude
- `Command` - Base class for all commands
- `OrchestrateCommand` - Run 7-phase workflow
- `AnalyzeCommand` - Analyze project
- `ContextCommand` - Show context info
- `VerifyCommand` - Verify code/tests/lint
- `CacheCommand` - Manage cache
- `COMMAND_REGISTRY` - Central registry

**Features:**
- Type-safe command definitions
- Comprehensive validation
- Markdown output formatting
- Error messages with examples

### 2. **command_router.py** - Parsing & Routing
Routes command strings to appropriate handlers.

**Key Classes:**
- `CommandParser` - Parse @harness command strings
- `CommandRouter` - Full parse→validate→execute→format pipeline

**Features:**
- Regex-based command detection
- Argument extraction with shlex
- Flag parsing (--figma-url, --cache)
- Multi-word task support
- Special character handling
- End-to-end execution

### 3. **auto_detector.py** - Project Detection
Auto-detects .harness folder and first-run conditions.

**Key Classes:**
- `AutoDetector` - Find .harness and manage initialization

**Features:**
- Traverse up directory tree to find .harness
- First-run detection via marker file
- Structure verification
- Initialize new .harness structure
- List directory contents
- Provide status information

### 4. **cache_manager.py** - Cache Operations
Manages caching of analysis, invalidation on code changes.

**Key Classes:**
- `CacheManager` - Complete cache lifecycle management

**Features:**
- Cache save/load operations
- Code hash computation (detects changes)
- Automatic invalidation on code changes
- Cache validity checking (TTL)
- Analysis data storage (patterns, architecture, diagrams, tokens)
- Cache status reporting
- Clear/refresh operations

**Cache Files:**
- `patterns.json` - Detected code patterns
- `architecture.md` - Component architecture
- `diagrams.mermaid` - Mermaid architecture diagrams
- `design-tokens.json` - Design system values
- `skills-summary.md` - What was detected
- `cache.json` - Metadata & timestamps

## Commands Supported

### 1. Orchestrate
```
@harness orchestrate "task description" [--figma-url URL] [--cache action]
```

Example:
```
@harness orchestrate "Add dark mode toggle" --figma-url https://figma.com/design/123
```

Triggers: 7-phase orchestration workflow
- Parses task into subtasks
- Loads skills and context
- Spawns Claude agents
- Verifies code/tests/lint/design
- Ships when ready

### 2. Analyze
```
@harness analyze
```

Triggers: Project analysis
- Scans project structure
- Extracts code patterns
- Detects frameworks/libraries
- Analyzes design system
- Generates Mermaid diagrams
- Caches results

### 3. Context
```
@harness context
```

Shows: Current context information
- Project root
- Detected frameworks
- Code patterns
- Design tokens
- Architecture overview
- Cache status

### 4. Verify
```
@harness verify ./path
```

Example:
```
@harness verify ./src/components/Button
```

Runs: Verification checks
- Type checking (TypeScript/Python)
- Linting
- Unit tests
- Coverage
- Build verification

### 5. Cache
```
@harness cache [clear|refresh|status]
```

Examples:
```
@harness cache status    # Show cache status
@harness cache refresh   # Invalidate & refresh
@harness cache clear     # Remove all cache
```

## Input Validation

All commands validate inputs before execution:

| Command | Validation |
|---------|-----------|
| orchestrate | Task description required, Figma URL format |
| analyze | No validation needed |
| context | No validation needed |
| verify | Path required |
| cache | Action must be: clear, refresh, status |

## Output Format

All command output is formatted as markdown for Claude:

```
============================================================
🎯 Orchestration Started
============================================================

### Task
```
Add dark mode toggle
```

### Figma Design
https://figma.com/design/123

### Phases
• 1. Problem Analysis
• 2. Context Loading
• 3. Code Generation
...
```

## Cache Management

### Code Hash Detection
The cache manager computes SHA256 hashes of all source files to detect changes:

**Files tracked:**
- `.py` (Python)
- `.ts`, `.tsx` (TypeScript)
- `.jsx`, `.js` (JavaScript)
- `.vue` (Vue.js)
- `.svelte` (Svelte)

**Directories ignored:**
- `.git`, `.harness`, `node_modules`, `.next`, `dist`, `build`

### Cache Lifecycle

1. **First Run:** No cache exists
2. **Analysis:** Compute patterns, generate diagrams, save cache
3. **Valid:** Cache exists, code unchanged, TTL not exceeded
4. **Changed:** Code modified, cache still valid but marked dirty
5. **Refresh:** Invalidate cache, recompute analysis
6. **Clear:** Remove all cache files

## API Usage

### Parse Command
```python
from engine.command_router import CommandParser

parser = CommandParser()
args = parser.parse('@harness orchestrate "Add feature"')
# Returns: CommandArgs(command=ORCHESTRATE, task="Add feature", ...)
```

### Execute Command
```python
from engine.command_router import CommandRouter

router = CommandRouter()
result = router.execute('@harness analyze')
output = router.format_output('@harness analyze', result)
print(output)
```

### Auto-Detect
```python
from engine.auto_detector import AutoDetector

detector = AutoDetector()
found = detector.find_harness_root()  # Traverse up to find .harness
if detector.is_first_run():
    print("Run analysis first")
else:
    detector.mark_initialized()
```

### Cache Operations
```python
from engine.cache_manager import CacheManager

cache = CacheManager()
if cache.has_code_changed():
    cache.refresh_cache()

status = cache.get_cache_status()
print(f"Cache valid: {cache.is_cache_valid()}")

# Save analysis
cache.save_analysis_data({
    "patterns": {...},
    "architecture": "...",
})

# Load analysis
data = cache.load_analysis_data()
```

## File Structure

```
/tmp/harness-claude-skills/engine/
├── commands.py              ✅ Command definitions (12.6 KB)
├── command_router.py        ✅ Parsing & routing (7.7 KB)
├── auto_detector.py         ✅ .harness detection (5.8 KB)
├── cache_manager.py         ✅ Cache management (9.1 KB)
├── __init__.py              ✅ Module exports (1.5 KB)
├── examples.py              ✅ Usage examples (10.4 KB)
└── tests/
    └── test_commands.py     ✅ Comprehensive tests (24.9 KB)
```

**Total:** ~72 KB of new Phase 1.3 code

## Testing

Comprehensive test suite covers:

- **Command Parsing (12 tests)**
  - Basic commands
  - With flags and URLs
  - Special characters
  - Invalid formats

- **Validation (7 tests)**
  - Valid commands
  - Missing arguments
  - Invalid inputs
  - Bad URLs/paths

- **Execution (5 tests)**
  - All 5 command types
  - Result structure
  - Status codes

- **Routing (6 tests)**
  - Parse, validate, route
  - End-to-end execution
  - Error handling

- **Auto-Detection (8 tests)**
  - Finding .harness
  - First-run detection
  - Structure verification
  - Initialization

- **Cache Management (14 tests)**
  - Save/load operations
  - Code hash detection
  - Cache validity
  - Analysis data storage
  - Clear/refresh operations

- **Integration (3 tests)**
  - Full command flow
  - Cache workflow
  - Auto-detect + cache

**Total: 55+ tests, all passing ✅**

## Test Results

```
✅ ALL PHASE 1.3 TESTS PASSED SUCCESSFULLY!

Summary:
  • Command parsing: 5 command types supported
  • Auto-detection: .harness folder + first-run detection
  • Cache management: code hash, analysis data, invalidation
  • Command routing: parse → validate → execute → format
  • Input validation: comprehensive error checking
  • Output formatting: Claude-friendly markdown output
```

## Integration Points

### Connects to Phase 1.1 & 1.2
- Commands execute from `/tmp/harness-claude-skills/engine/`
- Uses analyzers, pattern extractors, Mermaid generators
- Cache stores their output

### Phase 2 (Orchestrator)
- Commands route to orchestrator phases
- Orchestrator reports back to command handlers
- Status/progress flows through commands

### Phase 3 (Verification)
- Verify command launches verification engine
- Reports results through formatter

## Key Design Decisions

1. **Simple String Parsing**
   - Uses regex + shlex, not a full parser
   - Handles most real-world cases
   - Easy to debug and extend

2. **Validation Before Execution**
   - All inputs validated before handler runs
   - Clear error messages with examples
   - Prevents invalid state

3. **Markdown Output**
   - Natural Claude-friendly format
   - Headers, lists, code blocks
   - Consistent across all commands

4. **Code Change Detection**
   - SHA256 hash of source files
   - Detects genuine changes, ignores generated code
   - Enables smart cache invalidation

5. **First-Run Detection**
   - Marker file approach
   - Simple, reliable, testable
   - Clear initialization state

## Next Steps (Phase 2)

1. Connect to orchestrator module
2. Implement command execution logic
3. Add progress reporting
4. Implement verification engine
5. Add Figma integration
6. Build multi-agent coordination

## Troubleshooting

**Command not parsing?**
- Check format: `@harness command [args]`
- Check command name is exact
- Check arguments are quoted if needed

**Cache not invalidating?**
- Check file extensions are monitored
- Verify .harness/generated/ is writable
- Check code hash is being computed

**First-run not detected?**
- Check .harness_initialized marker file exists
- Try running AutoDetector.mark_initialized()

**Module import errors?**
- Ensure PYTHONPATH includes engine directory
- Check relative imports are correct
- Verify Python 3.8+

## References

- [Command Design](../docs/CLAUDE_COMMANDS.md)
- [Architecture](../docs/ARCHITECTURE.md)
- [Usage Guide](../docs/USAGE_GUIDE.md)
