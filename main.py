"""
ATS CV Maker - Main orchestration script
Extracts keywords from CV and job description, rates them, and calculates ATS score.
Includes skill matching score and experience relevance score.
"""

import sys
import argparse
from pathlib import Path

from src.ats_cv_maker.cv_extractor import CVExtractor
from src.ats_cv_maker.keyword_extractor import KeywordExtractor
from src.ats_cv_maker.keyword_rating_agent import KeywordRatingAgent
from src.ats_cv_maker.ats_scorer import ATSScorer
from src.ats_cv_maker.skill_extractor import SkillExtractor
from src.ats_cv_maker.skill_normalizer import SkillNormalizer
from src.ats_cv_maker.skill_matcher import SkillMatcher
from src.ats_cv_maker.cv_section_parser import CVSectionParser
from src.ats_cv_maker.experience_relevance_scorer import ExperienceRelevanceScorer


def extract_target_job_title(jd_text: str, jd_keywords: list) -> str:
    """
    Extract target job title from job description text.
    
    Args:
        jd_text: Full job description text
        jd_keywords: Keywords extracted from job description
        
    Returns:
        Target job title string
    """
    import re
    
    # Look for common patterns like "Job Title:", "Position:", "Role:"
    patterns = [
        r'(?:Job\s+Title|Position|Role|Title)\s*:\s*([^\n]+)',
        r'^([A-Z][^,\n]+(?:Engineer|Developer|Manager|Analyst|Designer|Architect|Lead|Director|Manager))[,\n]',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, jd_text, re.IGNORECASE | re.MULTILINE)
        if match:
            title = match.group(1).strip()
            if len(title) < 100:  # Sanity check
                return title
    
    # Fallback: use first meaningful keyword
    for kw in jd_keywords:
        if any(word in kw.lower() for word in ['engineer', 'developer', 'manager', 'analyst', 'designer', 'architect', 'lead']):
            return kw
    
    # Default fallback
    return jd_keywords[0] if jd_keywords else "Software Engineer"


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
    parser.add_argument(
        '--no-skills',
        action='store_true',
        help='Skip skill matching analysis'
    )
    parser.add_argument(
        '--no-normalize-skills',
        action='store_true',
        help='Skip skill normalization'
    )
    parser.add_argument(
        '--no-experience',
        action='store_true',
        help='Skip experience relevance analysis'
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
        
        # Step 6: Optional skill matching analysis
        skill_score_data = None
        if not args.no_skills:
            print("\n🎯 Analyzing skill matches...")
            try:
                # Extract and normalize skills
                skill_extractor = SkillExtractor()
                cv_skills_obj = skill_extractor.extract_skills_from_cv(cv_text)
                jd_skills_obj = skill_extractor.extract_skills_from_job_description(jd_text)
                
                cv_skills_list = cv_skills_obj.skills
                jd_skills_list = jd_skills_obj.skills
                
                print(f"✓ Extracted {len(cv_skills_list)} skills from CV")
                print(f"✓ Extracted {len(jd_skills_list)} skills from job description")
                
                # Normalize skills if requested
                if not args.no_normalize_skills:
                    print("  Normalizing skills...")
                    skill_normalizer = SkillNormalizer()
                    
                    normalized_cv = skill_normalizer.normalize_skills(cv_skills_list, context="cv")
                    normalized_jd = skill_normalizer.normalize_skills(jd_skills_list, context="job_description")
                    
                    cv_skills_list, _ = skill_normalizer.merge_skills(cv_skills_list, normalized_cv)
                    jd_skills_list, _ = skill_normalizer.merge_skills(jd_skills_list, normalized_jd)
                
                # Match skills
                skill_matcher = SkillMatcher(similarity_threshold=0.8)
                match_results = skill_matcher.match_skills(cv_skills_list, jd_skills_list, verbose=False)
                
                skill_score = skill_matcher.calculate_skill_score(
                    match_results['total_matched'],
                    match_results['total_jd_skills']
                )
                
                skill_score_data = {
                    'skill_match_score': skill_score,
                    'matched_skills': match_results['total_matched'],
                    'total_jd_skills': match_results['total_jd_skills'],
                    'match_percentage': (match_results['total_matched'] / max(match_results['total_jd_skills'], 1)) * 100
                }
                
                print(f"✓ Skill match score: {skill_score:.1f}/100")
                
            except Exception as e:
                print(f"⚠️  Skill analysis failed: {e}")
                print("  Continuing with keyword analysis only...")
        
        # Step 7: Optional experience relevance analysis
        experience_score_data = None
        if not args.no_experience:
            print("\n💼 Analyzing experience relevance...")
            try:
                # Parse CV sections to get work experience
                section_parser = CVSectionParser()
                sections = section_parser.parse_cv(cv_text)
                
                # Extract job titles from JD (first job title or primary role)
                jd_keywords_lower = [kw.lower() for kw in jd_keywords[:10]]  # Use top keywords as context
                target_job_title = extract_target_job_title(jd_text, jd_keywords)
                
                if sections.work_experience and target_job_title:
                    # Parse work experience
                    scorer_exp = ExperienceRelevanceScorer(use_embeddings=True)
                    cv_experiences = scorer_exp.parse_cv_work_experience(sections.work_experience)
                    
                    if cv_experiences:
                        experience_score_data = scorer_exp.score_experience(
                            cv_experiences=cv_experiences,
                            target_job_title=target_job_title,
                            target_seniority="Mid"
                        )
                        
                        print(f"✓ Experience relevance score: {experience_score_data['experience_relevance_score']:.1f}/100")
                        print(f"  {experience_score_data['details']}")
                else:
                    print("⚠️  Could not parse work experience from CV")
            except Exception as e:
                print(f"⚠️  Experience analysis failed: {e}")
                print("  Continuing without experience analysis...")
        
        # Step 8: Generate and display report
        print("\n" + "=" * 60)
        report = scorer.generate_report(score_data, skill_score_data, experience_score_data)
        print(report)
        
        # Step 9: Save report if output path provided
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n💾 Report saved to: {output_path}")
        
        # Return exit code based on score
        final_score = score_data['final_score']
        scores_to_average = [final_score]
        
        if skill_score_data:
            scores_to_average.append(skill_score_data['skill_match_score'])
        
        if experience_score_data:
            scores_to_average.append(experience_score_data['experience_relevance_score'])
        
        combined_score = sum(scores_to_average) / len(scores_to_average)
        print(f"\n📊 Combined ATS Score: {combined_score:.1f}/100")
        
        if final_score >= 70:
            print("\n✅ Great! Your CV has a strong match.")
            return 0
        elif final_score >= 50:
            print("\n⚠️  Your CV has a moderate match. Consider adding missing required keywords.")
            return 0
        else:
            print("\n❌ Your CV has a low match. Review and add missing required keywords.")
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
