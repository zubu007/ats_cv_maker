# Output Directory Management

## Overview

The ATS CV Maker now includes a sophisticated output directory management system that automatically organizes all generated files (LaTeX, PDF, logs, etc.) in timestamped directories. This makes it easy to keep track of multiple CV generations and versions.

## Directory Structure

By default, outputs are organized in the following structure:

```
output/
├── 2026-01-05_10-30-15/
│   ├── improved_cv.tex
│   ├── improved_cv.pdf
│   ├── sections.json
│   └── optimization.log
├── 2026-01-05_11-45-22/
│   ├── improved_cv.tex
│   ├── improved_cv.pdf
│   └── sections.json
└── 2026-01-05_14-20-33/
    ├── improved_cv.tex
    ├── improved_cv.pdf
    └── sections.json
```

Each timestamp directory is created automatically with the format: `YYYY-MM-DD_HH-MM-SS`

## OutputDirectoryManager Class

### Quick Start

```python
from src.ats_cv_maker.output_manager import OutputDirectoryManager, create_output_manager

# Create a manager with automatic session directory
manager = create_output_manager(base_dir="output")

# Get paths for files
tex_path = manager.get_tex_file_path('improved_cv.tex')
pdf_path = manager.get_pdf_file_path('improved_cv.pdf')
log_path = manager.get_log_file_path('optimization.log')
```

### API Methods

#### `__init__(base_output_dir: str = "output")`
Initialize the output manager.

```python
manager = OutputDirectoryManager(base_output_dir="my_outputs")
```

#### `create_session_directory() -> Path`
Create a new timestamped session directory.

```python
session_dir = manager.create_session_directory()
# Returns: output/2026-01-05_14-30-15/
```

#### `get_session_directory() -> Path`
Get the current session directory (creates one if needed).

```python
session_dir = manager.get_session_directory()
```

#### `get_tex_file_path(filename: str) -> Path`
Get the full path for a TeX file.

```python
tex_path = manager.get_tex_file_path('improved_cv.tex')
# Returns: output/2026-01-05_14-30-15/improved_cv.tex
```

#### `get_pdf_file_path(filename: str) -> Path`
Get the full path for a PDF file.

```python
pdf_path = manager.get_pdf_file_path('improved_cv.pdf')
# Returns: output/2026-01-05_14-30-15/improved_cv.pdf
```

#### `get_log_file_path(filename: str) -> Path`
Get the full path for a log file.

```python
log_path = manager.get_log_file_path('optimization.log')
# Returns: output/2026-01-05_14-30-15/optimization.log
```

#### `cleanup_auxiliary_files(keep_extensions: list = None)`
Remove LaTeX auxiliary files (.aux, .out, .log, etc).

```python
# Keep only .tex and .pdf files
manager.cleanup_auxiliary_files()

# Keep custom file types
manager.cleanup_auxiliary_files(keep_extensions=['.tex', '.pdf', '.json'])
```

#### `list_session_files() -> dict`
Get all files in the session directory organized by type.

```python
files = manager.list_session_files()
# Returns:
# {
#     'tex': [Path('output/.../improved_cv.tex')],
#     'pdf': [Path('output/.../improved_cv.pdf')],
#     'json': [Path('output/.../sections.json')],
#     'log': [Path('output/.../optimization.log')],
#     'other': []
# }
```

#### `print_session_summary()`
Print a formatted summary of files in the session directory.

```python
manager.print_session_summary()
# Output:
# ======================================================================
# Session Directory: /path/to/output/2026-01-05_14-30-15
# ======================================================================
# 
# 📄 TeX Files (1)
#   - improved_cv.tex
#
# 📕 PDF Files (1)
#   - improved_cv.pdf (0.50 MB)
#
# 📋 JSON Files (1)
#   - sections.json
#
# ======================================================================
```

## Integration with Pipeline

### Pipeline Finalizer (Recommended)

The `finalize_cv_with_one_page_optimization()` function automatically handles output management:

```python
from src.ats_cv_maker.pipeline_finalizer import finalize_cv_with_one_page_optimization

result = finalize_cv_with_one_page_optimization(
    tex_file_path='improved_cv.tex',
    pdf_output_path='improved_cv.pdf',
    verbose=True,
    output_base_dir='output',
    use_output_manager=True  # Enable timestamped output
)

print(result['output_directory'])  # Path to the timestamped directory
print(result['pdf_file'])          # Full path to generated PDF
```

### Without Output Manager

Disable output management if you want to save files directly:

```python
result = finalize_cv_with_one_page_optimization(
    tex_file_path='improved_cv.tex',
    pdf_output_path='improved_cv.pdf',
    use_output_manager=False  # Save to specified paths directly
)
```

## Usage Examples

### Example 1: Generate CV with Timestamped Output

```python
from src.ats_cv_maker.latex_cv_generator import LaTeXCVGenerator
from src.ats_cv_maker.pipeline_finalizer import finalize_cv_with_one_page_optimization

# Generate CV
latex_content = LaTeXCVGenerator.generate_latex(improved_sections)
with open('improved_cv.tex', 'w') as f:
    f.write(latex_content)

# Finalize with automatic output management
result = finalize_cv_with_one_page_optimization(
    tex_file_path='improved_cv.tex',
    pdf_output_path='improved_cv.pdf',
    use_output_manager=True  # Creates output/YYYY-MM-DD_HH-MM-SS/
)

print(f"✓ CV saved to: {result['output_directory']}")
```

### Example 2: Manual Output Management

```python
from src.ats_cv_maker.output_manager import create_output_manager

# Create output directory
manager = create_output_manager('output')

# Generate your CV files
tex_path = manager.get_tex_file_path('improved_cv.tex')
pdf_path = manager.get_pdf_file_path('improved_cv.pdf')

# Generate CV content
latex_content = LaTeXCVGenerator.generate_latex(sections)
with open(tex_path, 'w') as f:
    f.write(latex_content)

# Compile PDF
PDFGenerator.compile_latex_to_pdf(str(tex_path), str(pdf_path.parent))

# Optimize to one page
from src.ats_cv_maker.one_page_optimizer import optimize_cv_to_one_page
success, pages, msg = optimize_cv_to_one_page(
    tex_file_path=str(tex_path),
    pdf_file_path=str(pdf_path),
    output_manager=manager
)

# Clean up auxiliary files
manager.cleanup_auxiliary_files()

# Print summary
manager.print_session_summary()
```

### Example 3: Multiple CVs in Single Session

```python
from src.ats_cv_maker.output_manager import OutputDirectoryManager

manager = OutputDirectoryManager('output')
manager.create_session_directory()

# Generate first CV
cv1_tex = manager.get_tex_file_path('cv_standard.tex')
cv1_pdf = manager.get_pdf_file_path('cv_standard.pdf')
# ... generate CV1 ...

# Generate second CV
cv2_tex = manager.get_tex_file_path('cv_tailored.tex')
cv2_pdf = manager.get_pdf_file_path('cv_tailored.pdf')
# ... generate CV2 ...

# Both saved in same session directory
manager.print_session_summary()
```

## Configuration

### Custom Base Directory

```python
manager = OutputDirectoryManager(base_output_dir="my_cv_outputs")
manager.create_session_directory()
# Creates: my_cv_outputs/2026-01-05_14-30-15/
```

### Custom File Names

```python
manager = OutputDirectoryManager()
manager.create_session_directory()

# Use custom filenames
tex_path = manager.get_tex_file_path('resume.tex')
pdf_path = manager.get_pdf_file_path('resume.pdf')
```

## Cleanup Options

### Keep Only Specific File Types

```python
# Keep only .tex and .pdf files
manager.cleanup_auxiliary_files(keep_extensions=['.tex', '.pdf'])
```

### Remove All Auxiliary Files

```python
# Default: removes .aux, .out, .log, .synctex.gz, .fdb_latexmk, .fls, .bbl, .blg, .lof, .lot, .toc
manager.cleanup_auxiliary_files()
```

## Integration with Existing Code

### Before (without output management)

```python
latex_content = LaTeXCVGenerator.generate_latex(sections)
with open('improved_cv.tex', 'w') as f:
    f.write(latex_content)

PDFGenerator.compile_latex_to_pdf('improved_cv.tex')
```

### After (with output management)

```python
from src.ats_cv_maker.output_manager import create_output_manager

manager = create_output_manager()

latex_content = LaTeXCVGenerator.generate_latex(sections)
tex_path = manager.get_tex_file_path('improved_cv.tex')
with open(tex_path, 'w') as f:
    f.write(latex_content)

PDFGenerator.compile_latex_to_pdf(str(tex_path))
manager.print_session_summary()
```

## Benefits

1. **Organization**: Each CV generation is in its own dated directory
2. **Version Control**: Easy to compare multiple versions
3. **Cleanup**: Automatic removal of auxiliary files
4. **Tracking**: Maintain a history of all generated CVs
5. **Integration**: Seamlessly integrates with the one-page optimizer
6. **Automation**: No manual directory management needed

## Migration Guide

### From Direct File Paths to Output Manager

**Old code:**
```python
tex_file = 'improved_cv.tex'
pdf_file = 'improved_cv.pdf'
```

**New code:**
```python
manager = create_output_manager()
tex_file = str(manager.get_tex_file_path('improved_cv.tex'))
pdf_file = str(manager.get_pdf_file_path('improved_cv.pdf'))
```

### Preserving Old Behavior

If you want to keep files in specific locations without timestamping:

```python
# Disable output manager in pipeline finalizer
result = finalize_cv_with_one_page_optimization(
    tex_file_path='improved_cv.tex',
    pdf_output_path='improved_cv.pdf',
    use_output_manager=False  # Keep old behavior
)
```

## Troubleshooting

### Permission Denied

Ensure the output directory has write permissions:

```bash
chmod -R 755 output/
```

### Cleanup Not Working

Check that files aren't locked by other processes:

```python
# Force cleanup with error handling
try:
    manager.cleanup_auxiliary_files()
except PermissionError:
    print("Some files are locked, skipping cleanup")
```

## Performance

- Session directory creation: < 1ms
- File path generation: < 1ms
- File listing: < 10ms
- Cleanup: < 100ms (depending on number of files)

No noticeable performance impact on CV generation pipeline.
