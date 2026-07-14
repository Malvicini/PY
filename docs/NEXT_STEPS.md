# Next Steps

## Quick handoff summary
- Keep the docs in this folder as the main continuation context.
- Preserve the current family-based drawings layout.
- Validate the app and PDF lookup when code changes touch storage or routing.

## Immediate priorities
1. Keep the documents in this folder as the primary context for any new chat.
2. Preserve the current family-based drawings layout and do not reintroduce root-level study folders.
3. Validate the web app and the PDF lookup flow after any change touching data_loader.py, pdf_finder.py, or routes.py.
4. Prefer small incremental edits and update the docs whenever behavior changes.

## Short-term work
- Continue to verify that new study folders are created under DRAWINGS_DIR/<family>/<study_code>.
- Continue to verify that the PDF resolver finds files in the same structure and falls back only for legacy entries.
- Keep the documentation synchronized with the actual code path and filesystem convention.

## Follow-up work if a new feature is introduced
- Update the relevant docs before implementing the feature.
- Add or refine validation steps for the affected route or module.
- Keep the change scope small and avoid speculative architecture shifts.

## Technical debt to keep in mind
- Browser automation remains fragile and dependent on UI changes.
- Hardcoded Windows paths remain a risk for portability.
- The Excel-driven data model still depends on a specific sheet and column structure.

## Validation checklist
- Run the app locally and confirm the main routes still respond.
- Verify the PDF lookup path for at least one known family-based study code.
- Review the docs after any change that affects storage, routing, or workflow assumptions.
- If the task changes storage behavior, confirm the result against the workbook and the reference script.