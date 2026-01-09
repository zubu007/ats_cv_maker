"""
Pipeline integration module for the One-Page Optimizer Agent.
This should be called at the very end of your CV generation pipeline.
"""

from pathlib import Path
from .one_page_optimizer import optimize_cv_to_one_page
from .output_manager import OutputDirectoryManager


def finalize_cv_with_one_page_optimization(
    tex_file_path: str,
    pdf_output_path: str,
    verbose: bool = True,
    output_base_dir: str = "output",
    use_output_manager: bool = True
) -> dict:
    """
    Finalize CV by ensuring it fits on one page with organized output structure.
    
    This function should be called as the LAST step in your CV generation pipeline,
    after all content has been added to the LaTeX file.
    
    Args:
        tex_file_path: Path to the .tex CV file (or filename if using output manager)
        pdf_output_path: Path where the final PDF should be saved (or filename if using output manager)
        verbose: Print progress messages
        output_base_dir: Base directory for timestamped outputs (default: "output")
        use_output_manager: If True, uses timestamped output directory structure
        
    Returns:
        Dictionary with optimization results
    """
    
    if verbose:
        print("\n" + "="*70)
        print("FINAL STEP: One-Page CV Optimization")
        print("="*70)
    
    # Setup output manager if requested
    output_manager = None
    final_tex_path = tex_file_path
    final_pdf_path = pdf_output_path
    
    if use_output_manager:
        output_manager = OutputDirectoryManager(output_base_dir)
        output_manager.create_session_directory()
        
        # Resolve file paths
        tex_filename = Path(tex_file_path).name
        pdf_filename = Path(pdf_output_path).name
        
        final_tex_path = str(output_manager.get_tex_file_path(tex_filename))
        final_pdf_path = str(output_manager.get_pdf_file_path(pdf_filename))
        
        # Copy original tex file to output directory if it exists
        if Path(tex_file_path).exists():
            import shutil
            shutil.copy2(tex_file_path, final_tex_path)
            if verbose:
                print(f"📁 Output directory: {output_manager.get_session_directory()}")
    
    # Optimize the CV to fit on one page
    success, page_count, message = optimize_cv_to_one_page(
        tex_file_path=final_tex_path,
        pdf_file_path=final_pdf_path,
        verbose=verbose,
        output_manager=output_manager
    )
    
    result = {
        'success': success,
        'final_page_count': page_count,
        'message': message,
        'tex_file': final_tex_path,
        'pdf_file': final_pdf_path,
        'output_directory': str(output_manager.get_session_directory()) if output_manager else None
    }
    
    if verbose:
        if success:
            print(f"\n✓ CV Successfully Optimized")
            print(f"  Final page count: {page_count}")
            print(f"  PDF saved to: {final_pdf_path}")
        else:
            print(f"\n✗ Optimization encountered issues")
            print(f"  {message}")
        
        # Print session summary if using output manager
        if output_manager:
            output_manager.cleanup_auxiliary_files()
            output_manager.print_session_summary()
    
    return result


# Example integration into existing pipeline:
# 
# from .latex_cv_generator import LaTeXCVGenerator
# from .pdf_generator import PDFGenerator
# from .pipeline_finalizer import finalize_cv_with_one_page_optimization
#
# # ... your existing CV generation code ...
# latex_content = LaTeXCVGenerator.generate_latex(improved_sections)
# with open('improved_cv.tex', 'w') as f:
#     f.write(latex_content)
#
# # FINAL STEP: Optimize to one page
# result = finalize_cv_with_one_page_optimization(
#     tex_file_path='improved_cv.tex',
#     pdf_output_path='improved_cv.pdf',
#     verbose=True
# )
#
# if result['success']:
#     print(f"Your CV is ready! {result['message']}")
# else:
#     print(f"Warning: {result['message']}")
