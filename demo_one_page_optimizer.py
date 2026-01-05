#!/usr/bin/env python3
"""
Demo script: One-Page CV Optimizer Agent
Shows how to use the optimizer at the end of your CV generation pipeline.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ats_cv_maker.one_page_optimizer import optimize_cv_to_one_page
from src.ats_cv_maker.pipeline_finalizer import finalize_cv_with_one_page_optimization
from src.ats_cv_maker.output_manager import OutputDirectoryManager


def main():
    """Demo the one-page optimizer."""
    
    # Example usage with your CV files
    tex_file = "improved_cv.tex"
    pdf_file = "improved_cv.pdf"
    
    print("One-Page CV Optimizer Agent - Demo")
    print("=" * 70)
    
    # Check if files exist
    if not Path(tex_file).exists():
        print(f"Error: {tex_file} not found")
        print("\nUsage:")
        print("  1. Generate your CV LaTeX file first")
        print("  2. Run: python demo_one_page_optimizer.py")
        return
    
    # Method 1: Direct usage of optimizer
    print("\nMethod 1: Using OnePageOptimizer directly (no output manager)")
    print("-" * 70)
    success, pages, message = optimize_cv_to_one_page(
        tex_file_path=tex_file,
        pdf_file_path=pdf_file,
        verbose=True
    )
    
    # Method 2: Using the pipeline finalizer with output manager
    print("\n\nMethod 2: Using Pipeline Finalizer with Timestamped Output Directory")
    print("-" * 70)
    result = finalize_cv_with_one_page_optimization(
        tex_file_path=tex_file,
        pdf_output_path=pdf_file,
        verbose=True,
        output_base_dir="output",  # Files will be saved in output/YYYY-MM-DD_HH-MM-SS/
        use_output_manager=True
    )
    
    # Method 3: Manual output manager usage
    print("\n\nMethod 3: Using OutputDirectoryManager directly")
    print("-" * 70)
    manager = OutputDirectoryManager("output")
    session_dir = manager.create_session_directory()
    
    print(f"Session directory: {session_dir}")
    print(f"TeX path: {manager.get_tex_file_path('improved_cv.tex')}")
    print(f"PDF path: {manager.get_pdf_file_path('improved_cv.pdf')}")
    print(f"Log path: {manager.get_log_file_path()}")
    
    print("\n" + "=" * 70)
    print("Demo Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()

