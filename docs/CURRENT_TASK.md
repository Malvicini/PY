# Current Task

## Current Objective
Stabilizzare la gestione delle cartelle dei disegni in modo che rispetti la struttura reale del workbook Excel e non introduca convenzioni inventate.

## Quick snapshot
- Status: the current folder convention is stabilized and documented.
- Priority: preserve it and avoid introducing alternative layouts.
- Success criteria: workbook-driven family folders are used and PDF lookup still resolves correctly.

## Scope
- Allineare la creazione delle cartelle ai codici famiglia presenti nel file Excel Gestione_Studi_DB_20251010.xlsx.
- Assicurare che il resolver dei PDF trovi i PDF nella struttura DRAWINGS_DIR/<family>/<study_code>/<study_code>.pdf.
- Documentare in modo definitivo la struttura da seguire e i vincoli da non violare.

## Files / Modules Involved
- data_loader.py: folder creation for newly created studies
- pdf_finder.py: PDF lookup and retroactive folder creation
- create_drawings_structure_fixed.py: reference script for mass recreation of the folder tree from Excel
- docs/AGENTS.md, docs/PROJECT_CONTEXT.md, docs/ARCHITECTURE.md: documentation alignment

## Completed Work
- Verified the real workbook structure and aligned the folder logic to the Excel family codes.
- Rebuilt the drawings tree from the workbook using the existing bulk script.
- Removed the earlier test folders created outside the intended structure.
- Implemented the approved PDF preview flow through /api/fetch_pdf_local using the direct iframe integration.
- Updated the documentation to describe the approved layout and the guardrails for future edits.

## Constraints
- Do not invent new folder prefixes.
- Do not create study folders directly under the root of DRAWINGS_DIR.
- Do not add new placeholder files or experimental layouts.
- Use the Excel family code as the source of truth.
- Keep the PDF preview implementation exactly as the current approved flow: Flask route /api/fetch_pdf_local serves the PDF and the frontend renders it in an iframe. Do not reintroduce fetch-to-blob preview logic, timeout-based fallback UI, or alternative browser-side PDF loading mechanisms.

## Definition of done
- The drawings folder layout matches the workbook-based family structure.
- PDF lookup resolves a known study code correctly.
- The docs reflect the current behavior and the current task state.

## Context for future chats
- This file is the entry point for continuation work.
- New sessions should start from this file and the other docs/ files before proposing changes.

## Next Step
- Keep this behavior stable and avoid introducing alternate layouts unless explicitly requested.
