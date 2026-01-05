# One-Page CV Optimizer Agent

## Overview

The **One-Page Optimizer Agent** is an intelligent agent that automatically optimizes your CV's LaTeX file to fit all content on a single page. It works iteratively, checking the PDF page count and progressively adjusting LaTeX parameters until the entire CV fits on one page.

## Features

- **Automated Page Checking**: Monitors PDF page count after each generation
- **Iterative Optimization**: Progressively adjusts LaTeX parameters in stages
- **Smart Parameter Adjustment**:
  - Stage 1: Reduces document scale (0.85 → 0.70)
  - Stage 2: Reduces column width (3.0cm → 2.0cm)
  - Stage 3: Reduces list spacing (2pt → 0pt)
  - Stage 4: Shortens professional summary
- **Detailed Logging**: Tracks all optimization steps and parameters
- **Loop Exit**: Automatically exits when CV fits on 1 page

## Installation

### Prerequisites

1. **LaTeX Installation** (required for PDF generation):
   ```bash
   # macOS
   brew install basictex
   
   # Ubuntu/Debian
   sudo apt-get install texlive texlive-latex-extra
   
   # Fedora
   sudo dnf install texlive texlive-latex
   ```

2. **Python PDF Library** (optional, for better page detection):
   ```bash
   pip install PyPDF2
   # or
   pip install pypdf
   ```

## Usage

### Quick Start - Standalone Usage

```python
from src.ats_cv_maker.one_page_optimizer import optimize_cv_to_one_page

success, page_count, message = optimize_cv_to_one_page(
    tex_file_path='improved_cv.tex',
    pdf_file_path='improved_cv.pdf',
    verbose=True
)

if success:
    print(f"CV optimized to {page_count} page(s)!")
```

### Integration into Pipeline

Add this to the **END** of your CV generation pipeline:

```python
from src.ats_cv_maker.pipeline_finalizer import finalize_cv_with_one_page_optimization
from src.ats_cv_maker.latex_cv_generator import LaTeXCVGenerator

# ... your existing CV generation code ...

# Generate LaTeX
latex_content = LaTeXCVGenerator.generate_latex(improved_sections)
with open('improved_cv.tex', 'w') as f:
    f.write(latex_content)

# FINAL STEP: Optimize to one page
result = finalize_cv_with_one_page_optimization(
    tex_file_path='improved_cv.tex',
    pdf_output_path='improved_cv.pdf',
    verbose=True
)

if result['success']:
    print(f"✓ {result['message']}")
else:
    print(f"⚠ {result['message']}")
```

### Advanced Usage - Custom Optimizer

```python
from src.ats_cv_maker.one_page_optimizer import OnePageOptimizer

# Create optimizer instance
optimizer = OnePageOptimizer(
    tex_file_path='improved_cv.tex',
    pdf_file_path='improved_cv.pdf',
    max_iterations=15,  # Increase if needed
    verbose=True
)

# Run optimization
success, page_count, message = optimizer.optimize()

# View detailed optimization history
optimizer.print_optimization_summary()

# Access raw history
for entry in optimizer.optimization_history:
    print(f"Iteration {entry['iteration']}: "
          f"{entry['pages']} pages, "
          f"scale={entry['scale']}, "
          f"col_width={entry['column_width']}cm")
```

## How It Works

### Optimization Flow

```
┌─────────────────────────────────────┐
│ Start with Generated LaTeX CV File  │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ Generate PDF from LaTeX             │
│ (using pdflatex)                    │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ Check PDF Page Count                │
└────────────┬────────────────────────┘
             │
      ┌──────┴──────┐
      │             │
   1 page?      >1 page?
      │             │
      │             ▼
      │    ┌─────────────────────────┐
      │    │ Apply Optimization:     │
      │    │ - Reduce Scale          │
      │    │ - Reduce Column Width   │
      │    │ - Reduce Spacing        │
      │    │ - Shorten Summary       │
      │    └────────┬────────────────┘
      │             │
      │             ▼
      │    ┌─────────────────────────┐
      │    │ Max iterations reached? │
      │    └────────┬────────────────┘
      │             │
      │        ┌────┴─────┐
      │        │           │
      │       No          Yes
      │        │           │
      │        └──┬────────┘
      │           │
      └───────────┬───────────┘
                  │
                  ▼
        ┌──────────────────────┐
        │ Return Result        │
        │ (success/pages/msg)  │
        └──────────────────────┘
```

### Optimization Stages

The agent applies optimizations in stages to preserve quality while fitting on one page:

| Stage | Parameter | Initial | Minimum | Step |
|-------|-----------|---------|---------|------|
| 1 | Scale (geometry) | 0.85 | 0.70 | -0.05 |
| 2 | Column Width (cm) | 3.0 | 2.0 | -0.2 |
| 3 | Spacing (topsep pt) | 2 | 0 | -1 |
| 4 | Summary Length | Full | Shortened | Progressive |

## Output & Results

### Console Output Example

```
============================================================
Starting One-Page CV Optimization Agent
============================================================

[Iteration 1]
PDF Page Count: 2
CV exceeds 1 page (2 pages). Applying optimizations...
  → Reducing scale to 0.8

PDF generation exit code: 0

[Iteration 2]
PDF Page Count: 1

============================================================
✓ SUCCESS! CV fits on 1 page after 2 iteration(s)
============================================================

Optimization Summary:
--------------------------------------------------------------------------------
Iter  Pages    Scale      Col Width    Top Sep   
--------------------------------------------------------------------------------
1     2        0.85       3.0          2         
2     1        0.80       3.0          2         
--------------------------------------------------------------------------------
```

### Return Values

The optimizer returns a tuple of `(success, page_count, message)`:

```python
success, pages, msg = optimize_cv_to_one_page(...)

# success: bool
#   True if CV was optimized to 1 page
#   False if maximum iterations reached or error occurred

# pages: int or None
#   The final page count of the PDF
#   None if page count couldn't be determined

# message: str
#   Detailed message about the result
```

## Configuration

### Maximum Iterations

By default, the optimizer tries up to 10 iterations. Increase if needed:

```python
optimizer = OnePageOptimizer(
    tex_file_path='improved_cv.tex',
    pdf_file_path='improved_cv.pdf',
    max_iterations=20  # Increase limit
)
success, pages, msg = optimizer.optimize()
```

### Verbose Mode

Enable/disable console output:

```python
# With detailed output
success, pages, msg = optimize_cv_to_one_page(
    tex_file_path='improved_cv.tex',
    pdf_file_path='improved_cv.pdf',
    verbose=True  # Default
)

# Silent mode
success, pages, msg = optimize_cv_to_one_page(
    tex_file_path='improved_cv.tex',
    pdf_file_path='improved_cv.pdf',
    verbose=False
)
```

## Troubleshooting

### Issue: "pdflatex not found"

**Solution**: Install LaTeX tools:
```bash
# macOS
brew install basictex

# Then add to PATH if needed
export PATH="/usr/local/texlive/2023/bin/x86_64-darwin:$PATH"
```

### Issue: "Could not determine PDF page count"

**Solution**: Install PyPDF2 for better PDF detection:
```bash
pip install PyPDF2
```

Alternatively, ensure `pdfinfo` is available (comes with most LaTeX distributions).

### Issue: CV still exceeds 1 page after optimization

**Workaround**: 
1. Manually shorten some content in the CV sections
2. Remove less important projects or experiences
3. Increase `max_iterations` to allow more aggressive optimization

## Technical Details

### PDF Page Detection Methods

The optimizer uses multiple methods to detect page count (in order of preference):

1. **PyPDF2/pypdf** (most reliable)
2. **pdfinfo command** (fallback for macOS/Linux)

### LaTeX Modifications

The optimizer uses regex patterns to modify:

- `\usepackage[scale=0.85]{geometry}` → adjusts document scale
- `\setlength{\hintscolumnwidth}{3cm}` → adjusts column width  
- `\setlist{...}` → adjusts spacing parameters
- Professional summary text → shortens if needed

## Performance

- **Time per iteration**: 3-5 seconds (PDF generation)
- **Typical iterations needed**: 1-3 for most CVs
- **Total time**: Usually completes within 15-20 seconds

## API Reference

### OnePageOptimizer Class

```python
class OnePageOptimizer:
    def __init__(tex_file_path, pdf_file_path, max_iterations=10, verbose=True)
    def get_pdf_page_count() -> Optional[int]
    def generate_pdf() -> bool
    def optimize() -> Tuple[bool, Optional[int], str]
    def print_optimization_summary()
```

### Functions

```python
# Convenience function
def optimize_cv_to_one_page(
    tex_file_path: str,
    pdf_file_path: str,
    verbose: bool = True
) -> Tuple[bool, Optional[int], str]

# Pipeline integration
def finalize_cv_with_one_page_optimization(
    tex_file_path: str,
    pdf_output_path: str,
    verbose: bool = True
) -> dict
```

## Examples

### Example 1: Simple One-Time Optimization

```python
from src.ats_cv_maker.one_page_optimizer import optimize_cv_to_one_page

success, pages, message = optimize_cv_to_one_page(
    tex_file_path='improved_cv.tex',
    pdf_file_path='improved_cv.pdf'
)

print(message)  # "CV optimized to 1 page in 2 iteration(s)"
```

### Example 2: Pipeline Integration

```python
from src.ats_cv_maker.keyword_placement_agent import ImprovedCVSections
from src.ats_cv_maker.latex_cv_generator import LaTeXCVGenerator
from src.ats_cv_maker.pipeline_finalizer import finalize_cv_with_one_page_optimization

# Generate your improved CV
improved_sections = ImprovedCVSections(...)
latex_content = LaTeXCVGenerator.generate_latex(improved_sections)

# Save LaTeX
with open('improved_cv.tex', 'w') as f:
    f.write(latex_content)

# Optimize to one page (FINAL STEP)
result = finalize_cv_with_one_page_optimization(
    tex_file_path='improved_cv.tex',
    pdf_output_path='improved_cv.pdf'
)

print(f"Status: {result['message']}")
```

## License

This module is part of the ATS CV Maker project.
