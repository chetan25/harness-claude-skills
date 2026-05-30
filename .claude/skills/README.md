# Claude Code Skills - Developer Guide

## What are Claude Code Skills?

Claude Code Skills are modular, reusable components that extend Claude's capabilities in the Claude Code environment. They enable structured task execution, code analysis, and project understanding.

## Core Skills in this Repository

### 1. Harness Analyzer
**Purpose**: Analyze codebases and extract patterns
- Scans code structure
- Identifies design patterns
- Extracts architecture insights
- Generates documentation

**Location**: `../skills/harness-codebase-analyzer/`

### 2. Harness Orchestrator
**Purpose**: Coordinate execution of multiple skills
- Manages skill dependencies
- Handles state between skills
- Implements execution workflows
- Provides error recovery

**Location**: `../skills/harness-code-orchestrator/`

### 3. Harness Context Loader
**Purpose**: Manage context and state
- Load and cache project context
- Maintain execution state
- Provide context to skills
- Handle context cleanup

**Location**: `../skills/harness-context-loader/`

### 4. Harness Verifier
**Purpose**: Validate results and outputs
- Verify code quality
- Validate architecture compliance
- Check for best practices
- Report verification results

**Location**: `../skills/harness-verifier/`

## Creating a New Skill

### Step 1: Create Skill Directory
```bash
mkdir harness-{domain-name}
cd harness-{domain-name}
```

### Step 2: Use Templates
Copy templates from `.claude/templates/`:
- `claude.md.template` → `skill.md` (skill definition)
- `mcp-config.yaml.template` → `mcp-config.yaml` (MCP configuration)
- `domain-skill.template` → `{domain_name}_skill.py` (implementation)

### Step 3: Implement Core Methods
```python
class YourSkill:
    def __init__(self):
        self.name = "your-skill"
        self.version = "1.0.0"
    
    def execute(self, **kwargs):
        # Your implementation
        return {"status": "success", "data": result}
```

### Step 4: Add Tests
Create `tests/test_{domain_name}_skill.py` with unit tests.

### Step 5: Document
Update `skill.md` with:
- Overview and purpose
- Usage examples
- Integration points
- Dependencies

## Skill Input/Output Format

### Standard Input
```json
{
  "params": {
    "param1": "value1",
    "param2": "value2"
  },
  "config": {
    "option1": true
  }
}
```

### Standard Output
```json
{
  "status": "success",
  "data": {
    "result": "..."
  },
  "metadata": {
    "skill": "skill-name",
    "version": "1.0.0",
    "execution_time_ms": 123
  }
}
```

### Error Output
```json
{
  "status": "error",
  "error": "Error message",
  "metadata": {
    "skill": "skill-name",
    "error_code": "ERROR_CODE"
  }
}
```

## Integration with Claude Code

### In Claude Code Environment
Use the Skills API to execute skills:
```javascript
const result = await skills.execute('harness-analyzer', {
  params: {
    repo_path: './my-project'
  }
});
```

### With Orchestrator
Chain skills together:
```javascript
const orchestrator = new Orchestrator();
orchestrator.addSkill('analyzer')
            .then('orchestrator')
            .then('verifier');
const results = await orchestrator.execute(input);
```

## Best Practices

1. **Single Responsibility**: Each skill should do one thing well
2. **Error Handling**: Return proper error status with messages
3. **Validation**: Validate all inputs before processing
4. **Performance**: Optimize for quick execution
5. **Documentation**: Keep skill.md and examples up to date
6. **Testing**: Aim for high test coverage
7. **Versioning**: Use semantic versioning
8. **Dependencies**: Keep external dependencies minimal

## Testing Skills

### Unit Testing
```bash
python -m pytest tests/
```

### Integration Testing
Test skill with orchestrator:
```python
from harness_orchestrator import Orchestrator
orchestrator = Orchestrator()
result = orchestrator.execute('your-skill', params)
```

## Examples

See `../../examples/` for:
- React application integration
- Node backend integration
- Skill usage patterns

## Troubleshooting

### Skill not executing
1. Check `mcp-config.yaml` is valid
2. Verify `execute()` method exists
3. Check error output for details

### Context not available
1. Ensure context-loader is initialized
2. Check context keys match expectations
3. Verify context cleanup on completion

### Results not validating
1. Check verifier configuration
2. Ensure output format matches schema
3. Review validation rules

## Resources

- **Templates**: See `.claude/templates/`
- **Examples**: See `../../examples/`
- **Architecture**: See `../../docs/ARCHITECTURE.md`
- **Usage Guide**: See `../../docs/USAGE_GUIDE.md`

## Contributing

When adding new skills:
1. Follow the naming conventions (kebab-case for folders)
2. Use the provided templates
3. Include comprehensive tests
4. Add documentation
5. Update this README with new skill details
