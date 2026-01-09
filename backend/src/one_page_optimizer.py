"""
One Page CV Optimizer Agent
Iteratively adjusts LaTeX CV parameters to fit content on a single page.
Monitors PDF page count and modifies scale, spacing, and column width accordingly.
"""

import subprocess
import re
import logging
from pathlib import Path
from typing import Tuple, Optional
from .output_manager import OutputDirectoryManager

# Try to import PyPDF2, fallback if not available
try:
    from PyPDF2 import PdfReader
    PDF_READER_AVAILABLE = True
except ImportError:
    PDF_READER_AVAILABLE = False
    try:
        import pypdf
        PdfReader = pypdf.PdfReader
        PDF_READER_AVAILABLE = True
    except ImportError:
        pass

logger = logging.getLogger(__name__)


class OnePageOptimizer:
    """Optimizes CV LaTeX file to fit content on a single page."""
    
    def __init__(self, 
                 tex_file_path: str,
                 pdf_file_path: str,
                 max_iterations: int = 10,
                 verbose: bool = True,
                 output_manager: OutputDirectoryManager = None):
        """
        Initialize the optimizer.
        
        Args:
            tex_file_path: Path to the .tex CV file
            pdf_file_path: Path where the PDF will be generated
            max_iterations: Maximum optimization iterations
            verbose: Print progress messages
            output_manager: OutputDirectoryManager for organized output (optional)
        """
        self.tex_path = Path(tex_file_path)
        self.pdf_path = Path(pdf_file_path)
        self.max_iterations = max_iterations
        self.verbose = verbose
        self.output_manager = output_manager
        
        # Optimization parameters (will decrease iteratively)
        self.scale = 0.85
        self.column_width = 3.0
        self.topsep = 2
        self.parsep = 2
        self.partopsep = 2
        
        # Track optimization history
        self.optimization_history = []
        
        if not self.tex_path.exists():
            raise FileNotFoundError(f"TeX file not found: {tex_file_path}")
    
    def get_pdf_page_count(self) -> Optional[int]:
        """
        Get the number of pages in the generated PDF.
        
        Returns:
            Number of pages, or None if unable to determine
        """
        if not self.pdf_path.exists():
            return None
        
        try:
            if PDF_READER_AVAILABLE:
                with open(self.pdf_path, 'rb') as f:
                    pdf = PdfReader(f)
                    return len(pdf.pages)
            else:
                # Fallback: use pdfinfo command (macOS/Linux)
                try:
                    result = subprocess.run(
                        ['pdfinfo', str(self.pdf_path)],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if 'Pages' in line:
                                return int(line.split(':')[1].strip())
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
                
                return None
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            return None
    
    def generate_pdf(self) -> bool:
        """
        Generate PDF from the current TeX file using pdflatex.
        
        Returns:
            True if PDF was generated successfully
        """
        try:
            # Run pdflatex in the directory of the tex file
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 
                 str(self.tex_path.name)],
                cwd=str(self.tex_path.parent),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if self.verbose:
                logger.info(f"PDF generation exit code: {result.returncode}")
            
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            logger.error("PDF generation timed out")
            return False
        except FileNotFoundError:
            logger.error("pdflatex not found. Please ensure LaTeX is installed.")
            return False
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return False
    
    def _modify_scale(self, latex_content: str, new_scale: float) -> str:
        """Modify the scale parameter in the LaTeX file."""
        pattern = r'\\usepackage\[scale=[\d.]+\]{geometry}'
        replacement = f'\\usepackage[scale={new_scale}]{{geometry}}'
        return re.sub(pattern, replacement, latex_content)
    
    def _modify_column_width(self, latex_content: str, new_width: float) -> str:
        """Modify the hints column width."""
        pattern = r'\\setlength{\\hintscolumnwidth}{[\d.]+cm}'
        replacement = f'\\setlength{{\\hintscolumnwidth}}{{{new_width}cm}}'
        return re.sub(pattern, replacement, latex_content)
    
    def _modify_spacing(self, latex_content: str, 
                       topsep: int, parsep: int, partopsep: int) -> str:
        """Modify list spacing parameters."""
        pattern = r'\\setlist{noitemsep,topsep=\d+pt,parsep=\d+pt,partopsep=\d+pt}'
        replacement = (f'\\setlist{{noitemsep,topsep={topsep}pt,'
                      f'parsep={parsep}pt,partopsep={partopsep}pt}}')
        return re.sub(pattern, replacement, latex_content)
    
    def _reduce_summary_length(self, latex_content: str) -> str:
        """Shorten professional summary if present."""
        # Find and reduce professional summary
        pattern = r'(\\section{Professional Summary})\n([^\\]*)'
        match = re.search(pattern, latex_content)
        if match:
            summary = match.group(2).strip()
            if len(summary) > 200:
                # Truncate and add ellipsis
                summary = summary[:150] + '...'
                latex_content = latex_content.replace(match.group(0), 
                    f'{match.group(1)}\n{summary}')
        return latex_content
    
    def optimize(self) -> Tuple[bool, int, str]:
        """
        Iteratively optimize the CV to fit on one page.
        
        Returns:
            Tuple of (success, final_page_count, status_message)
        """
        if self.verbose:
            print("\n" + "="*60)
            print("Starting One-Page CV Optimization Agent")
            print("="*60)
        
        iteration = 0
        current_pages = None
        
        while iteration < self.max_iterations:
            iteration += 1
            
            if self.verbose:
                print(f"\n[Iteration {iteration}]")
            
            # Generate PDF
            if not self.generate_pdf():
                return False, None, "Failed to generate PDF from LaTeX"
            
            # Check page count
            current_pages = self.get_pdf_page_count()
            
            if current_pages is None:
                # If we can't read PDF, assume it worked and exit
                logger.warning("Could not determine PDF page count")
                return True, None, "PDF generated but page count unknown"
            
            if self.verbose:
                print(f"PDF Page Count: {current_pages}")
            
            # Record history
            self.optimization_history.append({
                'iteration': iteration,
                'pages': current_pages,
                'scale': self.scale,
                'column_width': self.column_width,
                'topsep': self.topsep
            })
            
            # Check if we've achieved the goal
            if current_pages <= 1:
                if self.verbose:
                    print("\n" + "="*60)
                    print(f"✓ SUCCESS! CV fits on 1 page after {iteration} iteration(s)")
                    print("="*60)
                return True, current_pages, f"CV optimized to 1 page in {iteration} iteration(s)"
            
            # If we still have multiple pages, apply optimizations
            if self.verbose:
                print(f"CV exceeds 1 page ({current_pages} pages). Applying optimizations...")
            
            # Read current TeX file
            with open(self.tex_path, 'r') as f:
                latex_content = f.read()
            
            # Apply progressive optimizations
            # Stage 1: Reduce scale
            if self.scale > 0.70:
                self.scale -= 0.05
                if self.verbose:
                    print(f"  → Reducing scale to {self.scale}")
                latex_content = self._modify_scale(latex_content, self.scale)
            
            # Stage 2: Reduce column width
            elif self.column_width > 2.0:
                self.column_width -= 0.2
                if self.verbose:
                    print(f"  → Reducing column width to {self.column_width}cm")
                latex_content = self._modify_column_width(latex_content, self.column_width)
            
            # Stage 3: Reduce spacing
            elif self.topsep > 0:
                self.topsep = max(0, self.topsep - 1)
                self.parsep = max(0, self.parsep - 1)
                self.partopsep = max(0, self.partopsep - 1)
                if self.verbose:
                    print(f"  → Reducing spacing (topsep={self.topsep}pt)")
                latex_content = self._modify_spacing(latex_content, 
                                                    self.topsep, 
                                                    self.parsep, 
                                                    self.partopsep)
            
            # Stage 4: Reduce summary length
            else:
                if self.verbose:
                    print(f"  → Shortening professional summary")
                latex_content = self._reduce_summary_length(latex_content)
            
            # Write modified TeX file
            with open(self.tex_path, 'w') as f:
                f.write(latex_content)
        
        # Max iterations reached
        if self.verbose:
            print("\n" + "="*60)
            print(f"✗ Maximum iterations ({self.max_iterations}) reached")
            print(f"Final page count: {current_pages}")
            print("="*60)
        
        return False, current_pages, f"Could not fit CV to 1 page after {self.max_iterations} iterations (final: {current_pages} pages)"
    
    def print_optimization_summary(self):
        """Print a summary of the optimization process."""
        if not self.optimization_history:
            print("No optimization history available")
            return
        
        print("\nOptimization Summary:")
        print("-" * 80)
        print(f"{'Iter':<5} {'Pages':<8} {'Scale':<10} {'Col Width':<12} {'Top Sep':<10}")
        print("-" * 80)
        
        for entry in self.optimization_history:
            print(f"{entry['iteration']:<5} {entry['pages']:<8} "
                  f"{entry['scale']:<10.2f} {entry['column_width']:<12.1f} "
                  f"{entry['topsep']:<10}")
        
        print("-" * 80)


def optimize_cv_to_one_page(tex_file_path: str, 
                            pdf_file_path: str,
                            verbose: bool = True,
                            output_manager: OutputDirectoryManager = None) -> Tuple[bool, Optional[int], str]:
    """
    Convenience function to optimize a CV to one page.
    
    Args:
        tex_file_path: Path to the .tex CV file
        pdf_file_path: Path where the PDF will be generated
        verbose: Print progress messages
        output_manager: OutputDirectoryManager for organized output (optional)
        
    Returns:
        Tuple of (success, final_page_count, status_message)
    """
    optimizer = OnePageOptimizer(tex_file_path, pdf_file_path, verbose=verbose, 
                                output_manager=output_manager)
    success, pages, message = optimizer.optimize()
    if verbose:
        optimizer.print_optimization_summary()
    return success, pages, message


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python one_page_optimizer.py <tex_file> [pdf_file]")
        sys.exit(1)
    
    tex_file = sys.argv[1]
    pdf_file = sys.argv[2] if len(sys.argv) > 2 else tex_file.replace('.tex', '.pdf')
    
    success, pages, message = optimize_cv_to_one_page(tex_file, pdf_file, verbose=True)
    print(f"\n{message}")
    sys.exit(0 if success else 1)
