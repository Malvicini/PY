# Persistent Workspace Instructions

Before generating code, answering questions, or modifying files:

Always read and use these files as the primary project context:

- /docs/AGENTS.md
- /docs/PROJECT_CONTEXT.md
- /docs/CURRENT_TASK.md
- /docs/NEXT_STEPS.md
- /docs/KNOWN_ISSUES.md
- /docs/ARCHITECTURE.md

Core behavior rules:

- Keep all context files continuously updated based on the current project state and current chat session.
- Whenever important architectural, functional, or structural changes happen, automatically update the relevant documentation files.
- Treat the documentation files as persistent AI memory for the project.
- Preserve consistency between codebase and documentation.
- Never leave outdated information inside documentation files.
- For any new chat or continuation task, start by reading these docs before proposing changes or asking the user for context that is already captured here.

Documentation update responsibilities:

1. AGENTS.md
Update when:
- coding conventions change
- architectural standards change
- workflow/process changes
- new project-wide rules are introduced

2. PROJECT_CONTEXT.md
Update when:
- features/modules are added
- services change
- flows change
- architecture evolves
- implementation status changes

3. CURRENT_TASK.md
Update continuously to reflect:
- current objective
- active implementation
- files/modules involved
- unfinished work
- blockers
- latest important progress

4. NEXT_STEPS.md
Update continuously with:
- next priorities
- missing implementations
- technical debt
- refactor opportunities
- pending testing tasks

5. KNOWN_ISSUES.md
Update whenever:
- bugs are discovered
- unstable areas are identified
- temporary workarounds are introduced
- risky code paths are found

6. ARCHITECTURE.md
Update when:
- project structure changes
- services/modules are reorganized
- APIs/data flow changes
- database structure changes
- infrastructure changes

README maintenance:

- Periodically update README.md to reflect the current real project state.
- Keep README.md concise, clean, and suitable for developers onboarding the project.
- Ensure installation, setup steps, architecture summary, and feature list stay accurate.

Implementation rules:

- Reuse existing patterns before introducing new ones.
- Avoid unnecessary dependencies.
- Inspect surrounding code before generating implementations.
- Keep implementations production-ready.
- Maintain architectural consistency.
- Avoid placeholder implementations unless explicitly requested.

Documentation quality rules:

- Use concise but information-dense markdown.
- Prefer structured headings and bullet points.
- Avoid duplication across files.
- Infer information directly from the codebase when possible.
- Optimize all documentation for future AI chat continuity and developer onboarding.

Project-specific guidance:

- This repository is Windows-first and script-based; preserve path assumptions and local filesystem behavior.
- The web app entrypoint is app.py; it creates a Flask app and registers main_bp from routes.py.
- Core backend modules include config.py, helpers.py, cache_manager.py, pdf_finder.py, and data_loader.py.
- Use DRAWINGS_DIR or the default H:\96-GESTIONE_STUDI\DISEGNI for PDF lookup.
- Keep Excel loading and PDF lookup behavior unchanged unless the task explicitly requires a redesign.
- Prefer small, incremental changes and update /docs/AGENTS.md, /docs/CURRENT_TASK.md, /docs/NEXT_STEPS.md, and /docs/ARCHITECTURE.md when architecture or workflow changes.
- When there is no test suite, rely on code compilation and running app.py for validation.
- Prefer docs/AGENTS.md as the primary AI instruction file for this repository.
