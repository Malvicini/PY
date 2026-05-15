---
mode: agent
---

Perform a full project handover and update the workspace documentation.

You MUST analyze the entire codebase and the current session context, then update the following files:

- /docs/PROJECT_CONTEXT.md
- /docs/CURRENT_TASK.md
- /docs/NEXT_STEPS.md
- /docs/KNOWN_ISSUES.md
- /docs/ARCHITECTURE.md

---

## 1. PROJECT_CONTEXT.md
Update to reflect:
- current project purpose
- actual implemented features (based on code, not assumptions)
- real architecture and structure
- tech stack in use
- key modules and responsibilities
- current project status

---

## 2. CURRENT_TASK.md
Update with:
- what is currently being worked on
- last meaningful changes in this session
- active goal / focus
- files modified or relevant
- blockers or unfinished work
- what should be continued immediately

---

## 3. NEXT_STEPS.md
Update with prioritized actions:
- next implementation steps
- missing features
- refactoring opportunities
- technical debt
- debugging or testing tasks
- improvements ordered by priority

---

## 4. KNOWN_ISSUES.md
Update with:
- newly discovered bugs
- unstable or risky areas
- temporary workarounds introduced
- edge cases discovered
- performance concerns
- components that should NOT be modified lightly

---

## 5. ARCHITECTURE.md
Update with:
- current system architecture
- module structure and responsibilities
- data flow (frontend → backend → storage)
- integrations (external systems like ADI)
- storage model (Excel/filesystem/etc.)
- architectural constraints and patterns

---

## GLOBAL RULES

- Always prefer accuracy over completeness
- Do NOT invent features that do not exist in the codebase
- Remove outdated or contradictory information
- Keep all files concise but information-dense
- Ensure consistency across all documentation files
- Use only facts inferred from the actual repository and current session
- Treat these files as the single source of truth for future AI sessions

---

## OUTPUT EXPECTATION

After completing updates:
- ensure all files are internally consistent
- ensure no duplication of information across files
- ensure CURRENT_TASK reflects only one active focus
- ensure NEXT_STEPS is actionable and prioritized