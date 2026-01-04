"""
PDF Generator
Compiles LaTeX to PDF using pdflatex.
"""

import subprocess
import os
import shutil
from pathlib import Path


class PDFGenerator:
    """Generates PDF from LaTeX files."""
    
    @staticmethod
    def check_latex_installed() -> bool:
        """
        Check if pdflatex is installed on the system.
        
        Returns:
            True if pdflatex is available
        """
        return shutil.which('pdflatex') is not None
    
    @staticmethod
    def compile_latex_to_pdf(
        tex_file: str,
        output_dir: str = None,
        cleanup: bool = True
    ) -> str:
        """
        Compile LaTeX file to PDF.
        
        Args:
            tex_file: Path to .tex file
            output_dir: Output directory for PDF (default: same as tex file)
            cleanup: Whether to clean up auxiliary files
            
        Returns:
            Path to generated PDF file
            
        Raises:
            Exception if compilation fails
        """
        if not PDFGenerator.check_latex_installed():
            raise Exception(
                "pdflatex not found. Please install LaTeX:\n"
                "  macOS: brew install --cask mactex-no-gui\n"
                "  Ubuntu: sudo apt-get install texlive-latex-base texlive-latex-extra\n"
                "  Windows: Install MiKTeX from https://miktex.org/"
            )
        
        tex_path = Path(tex_file).resolve()
        if not tex_path.exists():
            raise FileNotFoundError(f"LaTeX file not found: {tex_file}")
        
        # Determine output directory
        if output_dir:
            out_dir = Path(output_dir).resolve()
            out_dir.mkdir(parents=True, exist_ok=True)
        else:
            out_dir = tex_path.parent
        
        # Change to output directory for compilation
        original_dir = os.getcwd()
        
        try:
            os.chdir(out_dir)
            
            # Copy tex file to output directory if needed
            if tex_path.parent != out_dir:
                shutil.copy(tex_path, out_dir / tex_path.name)
                tex_file_name = tex_path.name
            else:
                tex_file_name = tex_path.name
            
            print(f"🔨 Compiling LaTeX to PDF...")
            
            # Run pdflatex twice (for references and table of contents)
            for run in [1, 2]:
                print(f"   Run {run}/2...")
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', tex_file_name],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode != 0:
                    # Try to extract error message
                    error_msg = "LaTeX compilation failed."
                    if result.stdout:
                        # Look for error lines
                        for line in result.stdout.split('\n'):
                            if line.startswith('!'):
                                error_msg = line
                                break
                    raise Exception(f"{error_msg}\nFull output saved to latex_error.log")
            
            # Check if PDF was generated
            pdf_name = tex_file_name.replace('.tex', '.pdf')
            pdf_path = out_dir / pdf_name
            
            if not pdf_path.exists():
                raise Exception("PDF file was not generated")
            
            # Cleanup auxiliary files
            if cleanup:
                PDFGenerator._cleanup_latex_files(out_dir, tex_file_name.replace('.tex', ''))
            
            print(f"✅ PDF generated successfully: {pdf_path}")
            return str(pdf_path)
            
        except subprocess.TimeoutExpired:
            raise Exception("LaTeX compilation timed out after 60 seconds")
        except Exception as e:
            # Save error log
            log_file = out_dir / 'latex_error.log'
            if 'result' in locals() and result.stdout:
                with open(log_file, 'w') as f:
                    f.write(result.stdout)
            raise
        finally:
            os.chdir(original_dir)
    
    @staticmethod
    def _cleanup_latex_files(directory: Path, base_name: str):
        """
        Clean up auxiliary LaTeX files.
        
        Args:
            directory: Directory containing files
            base_name: Base name of the tex file (without extension)
        """
        extensions_to_remove = ['.aux', '.log', '.out', '.toc', '.lof', '.lot', '.fls', '.fdb_latexmk']
        
        for ext in extensions_to_remove:
            file_path = directory / f"{base_name}{ext}"
            if file_path.exists():
                try:
                    file_path.unlink()
                except:
                    pass  # Ignore cleanup errors
    
    @staticmethod
    def install_moderncv_package():
        """
        Attempt to install moderncv package (for LaTeX CV template).
        This is a helper function - actual installation depends on TeX distribution.
        """
        print("💡 If you get 'moderncv.cls not found' error:")
        print("")
        print("For MacTeX/TeX Live:")
        print("  sudo tlmgr install moderncv")
        print("")
        print("For MiKTeX (Windows):")
        print("  Open MiKTeX Console -> Packages -> Search 'moderncv' -> Install")
        print("")
        print("For Ubuntu/Debian:")
        print("  sudo apt-get install texlive-latex-extra")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        # Check if LaTeX is installed
        if PDFGenerator.check_latex_installed():
            print("✅ pdflatex is installed and available")
            print("\nUsage: python pdf_generator.py <tex_file> [output_dir]")
        else:
            print("❌ pdflatex is not installed")
            print("\nTo install LaTeX:")
            print("  macOS: brew install --cask mactex-no-gui")
            print("  Ubuntu: sudo apt-get install texlive-latex-base texlive-latex-extra")
            print("  Windows: Install MiKTeX from https://miktex.org/")
        sys.exit(1)
    
    tex_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        pdf_path = PDFGenerator.compile_latex_to_pdf(tex_file, output_dir)
        print(f"\n✅ Success! PDF created at: {pdf_path}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if "moderncv" in str(e).lower():
            print("\n")
            PDFGenerator.install_moderncv_package()
        sys.exit(1)
