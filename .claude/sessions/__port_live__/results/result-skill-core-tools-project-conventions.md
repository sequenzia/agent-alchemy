# Conversion Result: skill-core-tools-project-conventions

## Metadata

| Field | Value |
|-------|-------|
| Component ID | skill-core-tools-project-conventions |
| Component Type | skill |
| Group | core-tools |
| Name | project-conventions |
| Source Path | claude/core-tools/skills/project-conventions/SKILL.md |
| Target Path | .opencode/skills/project-conventions/SKILL.md |
| Fidelity Score | 68% |
| Fidelity Band | yellow |
| Status | partial |

## Converted Content

~~~markdown
---
description: Guides discovery and application of project-specific conventions including code patterns, naming, structure, and team practices. Use when exploring a codebase or implementing features to match existing patterns.
user-invocable: false
---

# Project Conventions

This skill guides you in discovering and applying project-specific conventions. Every codebase has its own patterns and practices - your job is to find them and follow them.

---

## Convention Discovery Process

### Step 1: Project Configuration

Check these files for explicit conventions:

**Code Style:**
- `.eslintrc*`, `eslint.config.*` - JavaScript/TypeScript linting rules
- `.prettierrc*`, `prettier.config.*` - Formatting rules
- `pyproject.toml`, `setup.cfg`, `.flake8` - Python config
- `.editorconfig` - Editor settings
- `ruff.toml`, `.ruff.toml` - Ruff linter config

**Project Structure:**
- `tsconfig.json` - TypeScript paths and settings
- `package.json` - Scripts, dependencies
- `pyproject.toml` - Python project config

**Documentation:**
- `CONTRIBUTING.md` - Contribution guidelines
- `CLAUDE.md` - AI coding guidelines
- `README.md` - Project overview
- `docs/` - Extended documentation

### Step 2: Existing Code Patterns

Study the codebase to find implicit conventions:

**File Organization:**
```bash
# Find how components are organized
ls -la src/components/

# Find test file patterns
find . -name "*.test.*" -o -name "*_test.*" -o -name "test_*"

# Find how utilities are organized
ls -la src/utils/ src/lib/ src/helpers/
```

**Naming Patterns:**
```bash
# Find function naming patterns
grep -r "^export function" src/ | head -20
grep -r "^def " src/ | head -20

# Find class naming patterns
grep -r "^export class" src/ | head -20
grep -r "^class " src/*.py | head -20
```

**Import Patterns:**
```bash
# Find import style (absolute vs relative)
grep -r "^import" src/ | head -30
grep -r "^from \." src/*.py | head -20
```

### Step 3: Similar Features

Find features similar to what you're building:

1. **Search for similar functionality:**
   ```bash
   # If building a "user profile" feature
   grep -r "profile" src/
   find . -name "*profile*"
   ```

2. **Study the implementation:**
   - How is it structured?
   - What patterns does it use?
   - How does it handle errors?
   - How is it tested?

3. **Note the patterns:**
   - Component structure
   - State management approach
   - API call patterns
   - Validation approach

---

## Common Convention Areas

### Naming Conventions

**Discover by example:**
```bash
# Function names
grep -E "^(export )?(async )?function " src/**/*.ts

# Variable names
grep -E "^(const|let|var) " src/**/*.ts

# Component names
grep -E "^(export )?function [A-Z]" src/**/*.tsx
```

**Common patterns:**
- `camelCase` for functions/variables
- `PascalCase` for components/classes
- `UPPER_SNAKE` for constants
- `kebab-case` for file names (some projects)
- `snake_case` for file names (Python)

### File Structure

**Discover the pattern:**
```bash
# Component structure
ls -la src/components/Button/

# Module structure
ls -la src/features/auth/
```

**Common patterns:**

Flat structure:
```
components/
  Button.tsx
  Button.test.tsx
  Button.styles.ts
```

Folder per component:
```
components/
  Button/
    index.ts
    Button.tsx
    Button.test.tsx
    Button.module.css
```

Feature-based:
```
features/
  auth/
    components/
    hooks/
    api.ts
    types.ts
```

### Error Handling

**Discover the pattern:**
```bash
# Find try-catch patterns
grep -A5 "try {" src/**/*.ts

# Find error types
grep -r "extends Error" src/

# Find error handling in API
grep -r "catch" src/api/
```

**Apply what you find:**
- Use the same error types
- Follow the same handling pattern
- Match logging approach

### Testing Patterns

**Discover the pattern:**
```bash
# Find test structure
head -50 src/**/*.test.ts

# Find test utilities
cat src/test/setup.ts
cat src/test/utils.ts
```

**Match the patterns:**
- Test file location (co-located vs separate)
- Naming convention (`*.test.ts` vs `*.spec.ts`)
- Setup and teardown approach
- Mocking strategy
- Assertion style

### API Patterns

**Discover the pattern:**
```bash
# Find API call patterns
grep -r "fetch\|axios\|api\." src/

# Find API response handling
grep -A10 "async function fetch" src/api/
```

**Match the patterns:**
- How are endpoints defined?
- How is authentication handled?
- What's the error format?
- How are responses typed?

---

## Convention Application Checklist

When implementing a feature, verify you're following conventions for:

### Code Style
- [ ] Variable naming matches existing code
- [ ] Function naming matches existing code
- [ ] File naming follows project pattern
- [ ] Import style matches (absolute vs relative)

### Structure
- [ ] File location follows project structure
- [ ] Component organization matches
- [ ] Export style matches (default vs named)

### Patterns
- [ ] Error handling follows project patterns
- [ ] Async patterns match existing code
- [ ] State management follows project approach
- [ ] API calls follow established patterns

### Testing
- [ ] Test file location is correct
- [ ] Test naming follows convention
- [ ] Test structure matches existing tests
- [ ] Mocking approach is consistent

### Documentation
- [ ] Comments follow existing style
- [ ] JSDoc/docstrings match project
- [ ] README updates if needed

---

## When Conventions Conflict

Sometimes you'll find inconsistent patterns:

1. **Prefer newer code** - Recent files often reflect current team preferences
2. **Prefer maintained code** - Active parts of the codebase reflect current practices
3. **Prefer documented conventions** - Explicit rules in configs override implicit patterns
4. **Ask if unclear** - When in doubt, ask the user which pattern to follow

---

## Red Flags

Watch for these signs that you might be breaking conventions:

- Your code looks very different from surrounding code
- You're using a library/pattern not used elsewhere
- Your file structure doesn't match siblings
- Your naming feels inconsistent with the codebase
- Linting errors (the project has explicit rules you're breaking)

When you notice these, stop and investigate the existing conventions more carefully.
~~~

## Fidelity Report

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | 2 | 1.0 | 2.0 |
| Workaround | 1 | 0.7 | 0.7 |
| TODO | 0 | 0.2 | 0.0 |
| Omitted | 1 | 0.0 | 0.0 |
| **Total** | **4** | | **2.7 / 4.0 = 67.5 → 68%** |

**Notes:** All body content transferred without loss. Fidelity reduction is entirely in frontmatter: one field relocated to filename (workaround) and one null-mapped field omitted (cosmetic auto-resolve). The skill's instructional content is fully preserved.

## Decisions

| Feature | Decision Type | Original | Converted | Rationale | Confidence | Resolution Mode |
|---------|-------------|----------|-----------|-----------|------------|----------------|
| name field | relocated | `name: project-conventions` | Derived from directory: `skills/project-conventions/SKILL.md` | OpenCode derives skill name from directory name; embedded:filename mapping from conversion knowledge. | high | auto |
| description field | direct | `description: Guides discovery and application...` | `description: Guides discovery and application...` | Direct 1:1 mapping; field name and semantics identical in OpenCode skill frontmatter. | high | N/A |
| user-invocable field | direct | `user-invocable: false` | `user-invocable: false` | Direct 1:1 mapping; controls appearance in OpenCode command dialog, same semantics. | high | N/A |
| disable-model-invocation field | omitted | `disable-model-invocation: false` | (omitted) | Maps to null — OpenCode has no concept of preventing model auto-invocation. Original value is `false` (not restricting), so omission has zero behavioral impact. Cosmetic auto-resolve applied. | high | auto |

## Gaps

| Feature | Reason | Severity | Workaround | User Acknowledged |
|---------|--------|----------|------------|-------------------|
| disable-model-invocation | No equivalent in OpenCode; skills are always discoverable via the `skill` tool regardless. | cosmetic | Original value was `false` (non-restrictive default), so omitting the field preserves identical behavior. No action required. | false |

## Unresolved Incompatibilities

| Group Key | Feature | Severity | Category | Reason | Suggested Workaround | Confidence | Affected Locations |
|-----------|---------|----------|----------|--------|---------------------|------------|-------------------|

No unresolved incompatibilities.
