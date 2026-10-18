REBUILD GUIDE

Run commands from the package root (the directory above build/).

1. Python 3.11+ is required; author verification used 3.12.14 on Windows.
2. python -m pip install -r build/requirements-build.txt
3. python build/run_examples.py
4. python build/build_handbook.py
5. python build/render_book.py
6. python build/audit_book.py

Step 3 repeats local tests and captures the eight demonstration outputs. Set
RUN_SOCKET_TESTS=1 only when your environment permits loopback client connections.
Step 4 preserves existing diagrams. Add --visuals to regenerate the programmatic
PNG, SVG and Mermaid files. The original backpressure-analogy.png raster is retained.
Step 5 writes the main PDF and offline HTML companions for root Markdown files.
Use --html-only for documentation updates that do not affect the textbook PDF.
Step 6 checks topic structure, images, SVG XML/bounds, graph references and links.

Font defaults are Windows Arial and Consolas. HANDBOOK_FONT_DIR can select an
alternative folder containing the filenames listed in render_book.py; adjust
FONT and BOLD in visuals.py and the font paths in audit_book.py on other systems.
Install fonts with suitable licenses; no system fonts are redistributed here.

Authoring data is in topics_*.txt, foundations.md, ai.md, cases_*.md and practice.txt.
Edit these sources before rebuilding, because generated Markdown changes alone
will be overwritten by build_handbook.py. The examples/ source files are canonical.
The PDF displays wrapped code where needed; run the original files in examples/.

Mermaid source validation here is structural, not an actual Mermaid engine run.
With a separately installed Mermaid CLI, a PowerShell rendering loop is:

New-Item -ItemType Directory -Force work-mermaid
Get-ChildItem -LiteralPath diagrams -Filter *.mmd | ForEach-Object {
  mmdc -i $_.FullName -o (Join-Path work-mermaid ($_.BaseName + '.svg'))
  if ($LASTEXITCODE -ne 0) { throw "Mermaid rendering failed: $($_.Name)" }
}

Run real PostgreSQL, Docker, Kubernetes, Helm, Terraform and Nginx checks only in
your intended disposable environment. See VERIFICATION_REPORT.md for boundaries.
The saved JSON reports describe the author run; rebuilds update applicable reports.
Regenerate FILE_INVENTORY.csv if you change files; its hashes describe this edition.

Optional PDF QA: python build/pdf_quality.py
Install Poppler and put pdftoppm on PATH, or set HANDBOOK_PDFTOPPM to its executable.
This rerenders selected pages and checks all page text/image bounds. Inspect its
PNG output visually; the script cannot perform the recorded human/assistant review.
