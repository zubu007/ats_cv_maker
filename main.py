"""
ATS CV Maker - Main orchestration script
Extracts keywords from CV and job description, rates them, and calculates ATS score.
"""

import sys
import argparse
from pathlib import Path

from src.ats_cv_maker.cv_extractor import CVExtractor
from src.ats_cv_maker.keyword_extractor import KeywordExtractor
from src.ats_cv_maker.keyword_rating_agent import KeywordRatingAgent
from src.ats_cv_maker.ats_scorer import ATSScorer


def main():
    """Main function to orchestrate the ATS scoring process."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='ATS CV Maker - Calculate keyword match score for your CV'
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
        help='Disable spaCy noun phrase extraction (use TF-IDF only)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path for the report (optional)',
        default=None
    )
    
    args = parser.parse_args()
    
    try:
        print("🚀 Starting ATS CV Analysis...")
        print("=" * 60)
        
        # Step 1: Extract text from CV
        print("\n📄 Extracting text from CV...")
        cv_extractor = CVExtractor()
        cv_text = cv_extractor.extract(args.cv_path)
        print(f"✓ Extracted {len(cv_text)} characters from CV")
        
        # Step 2: Extract text from job description
        print("\n📋 Extracting text from job description...")
        jd_text = cv_extractor.extract_from_text(args.job_description_path)
        print(f"✓ Extracted {len(jd_text)} characters from job description")
        
        # Step 3: Extract keywords
        print("\n🔍 Extracting keywords using TF-IDF and NLP...")
        keyword_extractor = KeywordExtractor(use_spacy=not args.no_spacy)
        
        cv_keywords = keyword_extractor.extract_keywords(cv_text, max_keywords=50)
        jd_keywords = keyword_extractor.extract_keywords(jd_text, max_keywords=50)
        
        print(f"✓ Extracted {len(cv_keywords)} keywords from CV")
        print(f"✓ Extracted {len(jd_keywords)} keywords from job description")
        
        # Step 4: Rate keywords using AI agent
        print("\n🤖 Rating keywords as required/optional using AI agent...")
        rating_agent = KeywordRatingAgent()
        rated_keywords = rating_agent.rate_keywords(jd_keywords, jd_text)
        
        print(f"✓ Identified {len(rated_keywords['required'])} required keywords")
        print(f"✓ Identified {len(rated_keywords['optional'])} optional keywords")
        
        # Step 5: Calculate ATS score
        print("\n📊 Calculating ATS keyword match score...")
        scorer = ATSScorer()
        score_data = scorer.calculate_keyword_match_score(
            cv_keywords=cv_keywords,
            required_keywords=rated_keywords['required'],
            optional_keywords=rated_keywords['optional']
        )
        
        # Step 6: Generate and display report
        print("\n" + "=" * 60)
        report = scorer.generate_report(score_data)
        print(report)
        
        # Step 7: Save report if output path provided
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n💾 Report saved to: {output_path}")
        
        # Return exit code based on score
        if score_data['final_score'] >= 70:
            print("\n✅ Great! Your CV has a strong keyword match.")
            return 0
        elif score_data['final_score'] >= 50:
            print("\n⚠️  Your CV has a moderate keyword match. Consider adding missing required keywords.")
            return 0
        else:
            print("\n❌ Your CV has a low keyword match. Review and add missing required keywords.")
            return 1
            
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
