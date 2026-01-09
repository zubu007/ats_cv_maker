"""
Output Directory Manager
Manages timestamped output directories for organizing CV generation outputs.
"""

from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OutputDirectoryManager:
    """Manages timestamped output directories for CV files."""
    
    def __init__(self, base_output_dir: str = "output"):
        """
        Initialize the output directory manager.
        
        Args:
            base_output_dir: Base directory for all outputs (default: "output")
        """
        self.base_dir = Path(base_output_dir)
        self.current_session_dir = None
    
    def create_session_directory(self) -> Path:
        """
        Create a timestamped session directory.
        
        Returns:
            Path to the created session directory
        """
        # Create timestamp directory: YYYY-MM-DD_HH-MM-SS
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        session_dir = self.base_dir / timestamp
        
        # Create directory
        session_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_session_dir = session_dir
        logger.info(f"Created output session directory: {session_dir}")
        
        return session_dir
    
    def get_session_directory(self) -> Path:
        """
        Get the current session directory, creating one if needed.
        
        Returns:
            Path to the current session directory
        """
        if self.current_session_dir is None:
            self.create_session_directory()
        
        return self.current_session_dir
    
    def get_tex_file_path(self, filename: str = "cv.tex") -> Path:
        """
        Get the full path for a TeX file in the current session directory.
        
        Args:
            filename: Name of the TeX file (default: "cv.tex")
            
        Returns:
            Full path to the TeX file
        """
        session_dir = self.get_session_directory()
        return session_dir / filename
    
    def get_pdf_file_path(self, filename: str = "cv.pdf") -> Path:
        """
        Get the full path for a PDF file in the current session directory.
        
        Args:
            filename: Name of the PDF file (default: "cv.pdf")
            
        Returns:
            Full path to the PDF file
        """
        session_dir = self.get_session_directory()
        return session_dir / filename
    
    def get_log_file_path(self, filename: str = "optimization.log") -> Path:
        """
        Get the full path for a log file in the current session directory.
        
        Args:
            filename: Name of the log file (default: "optimization.log")
            
        Returns:
            Full path to the log file
        """
        session_dir = self.get_session_directory()
        return session_dir / filename
    
    def cleanup_auxiliary_files(self, keep_extensions: list = None) -> None:
        """
        Clean up auxiliary LaTeX files (.aux, .out, .log, etc).
        
        Args:
            keep_extensions: List of extensions to keep (default: keeps .tex and .pdf)
        """
        if keep_extensions is None:
            keep_extensions = ['.tex', '.pdf', '.json']
        
        if self.current_session_dir is None:
            return
        
        aux_extensions = ['.aux', '.out', '.log', '.synctex.gz', '.fdb_latexmk', 
                         '.fls', '.bbl', '.blg', '.lof', '.lot', '.toc']
        
        for ext in aux_extensions:
            for file in self.current_session_dir.glob(f'*{ext}'):
                try:
                    file.unlink()
                    logger.debug(f"Removed auxiliary file: {file}")
                except Exception as e:
                    logger.warning(f"Could not remove {file}: {e}")
    
    def list_session_files(self) -> dict:
        """
        List all files in the current session directory organized by type.
        
        Returns:
            Dictionary with file types as keys and lists of files as values
        """
        if self.current_session_dir is None:
            return {}
        
        files = {
            'tex': [],
            'pdf': [],
            'json': [],
            'log': [],
            'other': []
        }
        
        for file in self.current_session_dir.iterdir():
            if file.is_file():
                if file.suffix == '.tex':
                    files['tex'].append(file)
                elif file.suffix == '.pdf':
                    files['pdf'].append(file)
                elif file.suffix == '.json':
                    files['json'].append(file)
                elif file.suffix == '.log':
                    files['log'].append(file)
                else:
                    files['other'].append(file)
        
        return files
    
    def print_session_summary(self) -> None:
        """Print a summary of files in the current session directory."""
        files = self.list_session_files()
        
        print("\n" + "=" * 70)
        print(f"Session Directory: {self.current_session_dir}")
        print("=" * 70)
        
        total_files = sum(len(v) for v in files.values())
        
        if total_files == 0:
            print("No files in session directory")
        else:
            if files['tex']:
                print(f"\n📄 TeX Files ({len(files['tex'])})")
                for f in files['tex']:
                    print(f"  - {f.name}")
            
            if files['pdf']:
                print(f"\n📕 PDF Files ({len(files['pdf'])})")
                for f in files['pdf']:
                    size_mb = f.stat().st_size / (1024 * 1024)
                    print(f"  - {f.name} ({size_mb:.2f} MB)")
            
            if files['json']:
                print(f"\n📋 JSON Files ({len(files['json'])})")
                for f in files['json']:
                    print(f"  - {f.name}")
            
            if files['log']:
                print(f"\n📝 Log Files ({len(files['log'])})")
                for f in files['log']:
                    print(f"  - {f.name}")
            
            if files['other']:
                print(f"\n📦 Other Files ({len(files['other'])})")
                for f in files['other']:
                    print(f"  - {f.name}")
        
        print("=" * 70 + "\n")


def create_output_manager(base_dir: str = "output") -> OutputDirectoryManager:
    """
    Convenience function to create an output manager with a session directory.
    
    Args:
        base_dir: Base output directory
        
    Returns:
        Initialized OutputDirectoryManager with session directory created
    """
    manager = OutputDirectoryManager(base_dir)
    manager.create_session_directory()
    return manager


if __name__ == "__main__":
    # Demo usage
    manager = create_output_manager()
    
    print(f"Session directory: {manager.get_session_directory()}")
    print(f"TeX file path: {manager.get_tex_file_path('improved_cv.tex')}")
    print(f"PDF file path: {manager.get_pdf_file_path('improved_cv.pdf')}")
    print(f"Log file path: {manager.get_log_file_path()}")
    
    manager.print_session_summary()
