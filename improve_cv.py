"""
ATS CV Improver - Main orchestration script with CV improvement workflow
Analyzes CV, adds missing keywords, generates improved LaTeX CV and PDF.
"""

import sys
import argparse
from pathlib import Path

from src.ats_cv_maker.cv_extractor import CVExtractor
from src.ats_cv_maker.keyword_extractor import KeywordExtractor
from src.ats_cv_maker.keyword_rating_agent import KeywordRatingAgent
from src.ats_cv_maker.ats_scorer import ATSScorer
from src.ats_cv_maker.cv_section_parser import CVSectionParser
from src.ats_cv_maker.missing_keyword_identifier import MissingKeywordIdentifier
from src.ats_cv_maker.keyword_placement_agent import KeywordPlacementAgent
from src.ats_cv_maker.latex_cv_generator import LaTeXCVGenerator
from src.ats_cv_maker.pdf_generator import PDFGenerator


def analyze_cv(cv_path: str, jd_path: str, use_spacy: bool = True) -> dict:
    """
    Analyze CV and calculate initial ATS score.
    
    Returns:
        Dictionary with all analysis data
    """
    print("🚀 Starting ATS CV Analysis...")
    print("=" * 60)
    
    # Extract text from CV and JD
    print("\n📄 Extracting text from CV...")
    cv_extractor = CVExtractor()
    cv_text = cv_extractor.extract(cv_path)
    print(f"✓ Extracted {len(cv_text)} characters from CV")
    
    print("\n📋 Extracting text from job description...")
    jd_text = cv_extractor.extract_from_text(jd_path)
    print(f"✓ Extracted {len(jd_text)} characters from job description")
    
    # Extract keywords
    print("\n🔍 Extracting keywords...")
    keyword_extractor = KeywordExtractor(use_spacy=use_spacy)
    cv_keywords = keyword_extractor.extract_keywords(cv_text, max_keywords=50)
    jd_keywords = keyword_extractor.extract_keywords(jd_text, max_keywords=50)
    print(f"✓ Extracted {len(cv_keywords)} keywords from CV")
    print(f"✓ Extracted {len(jd_keywords)} keywords from job description")
    
    # Rate keywords
    print("\n🤖 Rating keywords as required/optional...")
    rating_agent = KeywordRatingAgent()
    rated_keywords = rating_agent.rate_keywords(jd_keywords, jd_text)
    print(f"✓ Identified {len(rated_keywords['required'])} required keywords")
    print(f"✓ Identified {len(rated_keywords['optional'])} optional keywords")
    
    # Calculate initial score
    print("\n📊 Calculating initial ATS score...")
    scorer = ATSScorer()
    initial_score = scorer.calculate_keyword_match_score(
        cv_keywords=cv_keywords,
        required_keywords=rated_keywords['required'],
        optional_keywords=rated_keywords['optional']
    )
    
    return {
        'cv_text': cv_text,
        'jd_text': jd_text,
        'cv_keywords': cv_keywords,
        'jd_keywords': jd_keywords,
        'rated_keywords': rated_keywords,
        'initial_score': initial_score,
        'keyword_extractor': keyword_extractor,
        'scorer': scorer
    }


def improve_cv(analysis_data: dict, max_keywords: int = 10) -> dict:
    """
    Improve CV by adding missing keywords.
    
    Returns:
        Dictionary with improvement data
    """
    print("\n" + "=" * 60)
    print("🔧 IMPROVING CV")
    print("=" * 60)
    
    # Step 1: Parse CV sections
    print("\n📑 Parsing CV into sections...")
    section_parser = CVSectionParser()
    sections = section_parser.parse_cv(analysis_data['cv_text'])
    saved_sections = section_parser.save_sections(sections, output_dir="cv_sections")
    print(f"✓ Parsed and saved {len(saved_sections)-1} sections")
    
    # Step 2: Identify missing keywords
    print("\n🔍 Identifying missing keywords...")
    identifier = MissingKeywordIdentifier()
    missing_data = identifier.identify_missing_keywords(
        cv_keywords=analysis_data['cv_keywords'],
        required_keywords=analysis_data['rated_keywords']['required'],
        optional_keywords=analysis_data['rated_keywords']['optional']
    )
    print(f"✓ Found {missing_data['missing_required_count']} missing required keywords")
    print(f"✓ Found {missing_data['missing_optional_count']} missing optional keywords")
    
    # Prioritize keywords to add
    keywords_to_add = identifier.prioritize_missing_keywords(
        missing_data['missing_required'],
        missing_data['missing_optional'],
        max_keywords=max_keywords
    )
    
    if not keywords_to_add:
        print("\n✅ All important keywords are already present!")
        return {
            'sections': sections,
            'improved_sections': sections,
            'keywords_added': [],
            'missing_data': missing_data
        }
    
    print(f"\n📝 Will add {len(keywords_to_add)} keywords:")
    for kw in keywords_to_add:
        print(f"  • {kw}")
    
    # Step 3: Add keywords to CV sections
    print("\n🤖 Using AI to intelligently place keywords...")
    placement_agent = KeywordPlacementAgent()
    improved_sections = placement_agent.improve_cv_with_keywords(
        sections=sections,
        keywords_to_add=keywords_to_add,
        job_description=analysis_data['jd_text']
    )
    
    saved_improved = placement_agent.save_improved_sections(
        improved_sections,
        output_dir="improved_cv_sections"
    )
    print(f"✓ Improved sections saved to: improved_cv_sections/")
    
    if improved_sections.placement_notes:
        print(f"\n📋 Placement notes:\n{improved_sections.placement_notes}")
    
    return {
        'sections': sections,
        'improved_sections': improved_sections,
        'keywords_added': keywords_to_add,
        'missing_data': missing_data,
        'saved_improved': saved_improved
    }


def calculate_new_score(analysis_data: dict, improved_sections) -> dict:
    """Calculate new ATS score after improvements."""
    print("\n" + "=" * 60)
    print("📊 CALCULATING NEW SCORE")
    print("=" * 60)
    
    # Extract text from improved sections
    improved_text = "\n\n".join([
        improved_sections.personal_info,
        improved_sections.professional_summary,
        improved_sections.skills,
        improved_sections.work_experience,
        improved_sections.education,
        improved_sections.projects,
        improved_sections.certifications,
        improved_sections.additional
    ])
    
    # Extract keywords from improved CV
    print("\n🔍 Extracting keywords from improved CV...")
    improved_cv_keywords = analysis_data['keyword_extractor'].extract_keywords(
        improved_text, max_keywords=50
    )
    print(f"✓ Extracted {len(improved_cv_keywords)} keywords from improved CV")
    
    # Calculate new score
    print("\n📊 Calculating new ATS score...")
    new_score = analysis_data['scorer'].calculate_keyword_match_score(
        cv_keywords=improved_cv_keywords,
        required_keywords=analysis_data['rated_keywords']['required'],
        optional_keywords=analysis_data['rated_keywords']['optional']
    )
    
    return {
        'improved_text': improved_text,
        'improved_cv_keywords': improved_cv_keywords,
        'new_score': new_score
    }


def generate_pdf(improved_sections, output_name: str = "improved_cv") -> str:
    """Generate LaTeX and PDF from improved sections."""
    print("\n" + "=" * 60)
    print("📝 GENERATING LATEX AND PDF")
    print("=" * 60)
    
    # Generate LaTeX
    print("\n📝 Generating LaTeX code...")
    latex_generator = LaTeXCVGenerator()
    latex_code = latex_generator.generate_latex(improved_sections)
    
    tex_file = f"{output_name}.tex"
    latex_generator.save_latex(latex_code, tex_file)
    print(f"✓ LaTeX file saved: {tex_file}")
    
    # Generate PDF
    print(f"\n🔨 Compiling to PDF...")
    try:
        pdf_generator = PDFGenerator()
        pdf_path = pdf_generator.compile_latex_to_pdf(tex_file, cleanup=True)
        print(f"✅ PDF generated: {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f"⚠️  PDF generation failed: {e}")
        print(f"   LaTeX file is available at: {tex_file}")
        print(f"   You can compile manually with: pdflatex {tex_file}")
        return tex_file


def main():
    """Main function orchestrating the full CV improvement workflow."""
    parser = argparse.ArgumentParser(
        description='ATS CV Improver - Analyze, improve, and generate ATS-optimized CV'
    )
    parser.add_argument(
        'cv_path',
        type=str,
        help='Path to your CV file (.pdf or .txt)'
    )
    parser.add_argument(
        'job_description_path',
        type=str,
        help='Path to job description file (.txt)'
    )
    parser.add_argument(
        '--no-spacy',
        action='store_true',
        help='Disable spaCy noun phrase extraction'
    )
    parser.add_argument(
        '--max-keywords',
        type=int,
        default=10,
        help='Maximum number of keywords to add (default: 10)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='improved_cv',
        help='Output file name (without extension)'
    )
    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Only analyze without improving'
    )
    
    args = parser.parse_args()
    
    try:
        # Step 1: Analyze CV
        analysis_data = analyze_cv(args.cv_path, args.job_description_path, use_spacy=not args.no_spacy)
        
        # Show initial score
        print("\n" + "=" * 60)
        initial_report = analysis_data['scorer'].generate_report(analysis_data['initial_score'])
        print(initial_report)
        
        if args.analyze_only:
            print("\n✅ Analysis complete (--analyze-only mode)")
            return 0
        
        # Step 2: Improve CV
        improvement_data = improve_cv(analysis_data, max_keywords=args.max_keywords)
        
        if not improvement_data['keywords_added']:
            print("\n✅ CV is already well-optimized!")
            return 0
        
        # Step 3: Calculate new score
        new_score_data = calculate_new_score(analysis_data, improvement_data['improved_sections'])
        
        # Show improvement
        print("\n" + "=" * 60)
        print("📈 SCORE IMPROVEMENT")
        print("=" * 60)
        print(f"Initial Score: {analysis_data['initial_score']['final_score']:.2f}%")
        print(f"New Score:     {new_score_data['new_score']['final_score']:.2f}%")
        improvement = new_score_data['new_score']['final_score'] - analysis_data['initial_score']['final_score']
        print(f"Improvement:   {improvement:+.2f}%")
        
        # Show new score details
        print("\n" + "=" * 60)
        new_report = analysis_data['scorer'].generate_report(new_score_data['new_score'])
        print(new_report)
        
        # Step 4: Generate LaTeX and PDF
        pdf_path = generate_pdf(improvement_data['improved_sections'], output_name=args.output)
        
        # Final summary
        print("\n" + "=" * 60)
        print("✅ CV IMPROVEMENT COMPLETE!")
        print("=" * 60)
        print(f"Keywords added: {len(improvement_data['keywords_added'])}")
        print(f"Score improvement: {improvement:+.2f}%")
        print(f"Output: {pdf_path}")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
