"""
Skill Scoring Analysis Script
Standalone script for analyzing and scoring skills between CV and job description.
"""

import sys
import argparse
from pathlib import Path

from src.ats_cv_maker.cv_extractor import CVExtractor
from src.ats_cv_maker.skill_extractor import SkillExtractor
from src.ats_cv_maker.skill_normalizer import SkillNormalizer
from src.ats_cv_maker.skill_matcher import SkillMatcher


def main():
    """Main function for skill scoring analysis."""
    
    parser = argparse.ArgumentParser(
        description='Analyze skill match between CV and job description'
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
        '--output',
        type=str,
        help='Output file path for the report (optional)',
        default=None
    )
    parser.add_argument(
        '--no-normalize',
        action='store_true',
        help='Skip skill normalization'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print detailed step-by-step output'
    )
    
    args = parser.parse_args()
    
    try:
        print("🚀 Starting Skill Analysis...")
        print("=" * 80)
        
        # Extract text
        print("\n📄 Extracting text from files...")
        cv_extractor = CVExtractor()
        cv_text = cv_extractor.extract(args.cv_path)
        jd_text = cv_extractor.extract_from_text(args.job_description_path)
        print("✓ Files extracted successfully")
        
        # Extract skills
        print("\n🔍 STEP 1: Extracting skills from CV...")
        skill_extractor = SkillExtractor()
        cv_skills_obj = skill_extractor.extract_skills_from_cv(cv_text)
        cv_skills = cv_skills_obj.skills
        print(f"✓ Extracted {len(cv_skills)} skills from CV")
        
        if args.verbose:
            print("\n  Extracted CV Skills:")
            for skill in cv_skills:
                print(f"    • {skill}")
        
        print("\n🔍 STEP 2: Extracting skills from job description...")
        jd_skills_obj = skill_extractor.extract_skills_from_job_description(jd_text)
        jd_skills = jd_skills_obj.skills
        print(f"✓ Extracted {len(jd_skills)} skills from job description")
        
        if args.verbose:
            print("\n  Extracted Job Description Skills:")
            for skill in jd_skills:
                print(f"    • {skill}")
        
        # Normalize skills if requested
        if not args.no_normalize:
            print("\n📊 STEP 3: Normalizing CV skills...")
            skill_normalizer = SkillNormalizer()
            
            normalized_cv = skill_normalizer.normalize_skills(cv_skills, context="cv")
            cv_skills, cv_mappings = skill_normalizer.merge_skills(cv_skills, normalized_cv)
            print(f"✓ Normalized to {len(cv_skills)} unique skills")
            
            if args.verbose:
                print("\n  Normalized CV Skills:")
                for skill in cv_skills:
                    print(f"    • {skill}")
            
            print("\n📊 STEP 4: Normalizing job description skills...")
            normalized_jd = skill_normalizer.normalize_skills(jd_skills, context="job_description")
            jd_skills, jd_mappings = skill_normalizer.merge_skills(jd_skills, normalized_jd)
            print(f"✓ Normalized to {len(jd_skills)} unique skills")
            
            if args.verbose:
                print("\n  Normalized JD Skills:")
                for skill in jd_skills:
                    print(f"    • {skill}")
        
        # Match skills
        print("\n🎯 STEP 5: Matching skills...")
        skill_matcher = SkillMatcher(similarity_threshold=0.8)
        match_results = skill_matcher.match_skills(cv_skills, jd_skills, verbose=args.verbose)
        
        # Calculate score
        print("\n📈 STEP 6: Calculating skill match score...")
        skill_score = skill_matcher.calculate_skill_score(
            match_results['total_matched'],
            match_results['total_jd_skills']
        )
        
        # Generate report
        print("\n" + "=" * 80)
        print("📋 SKILL MATCH ANALYSIS REPORT")
        print("=" * 80)
        print(skill_matcher.generate_matching_report(match_results))
        
        print("\n" + "=" * 80)
        print("🏆 FINAL SKILL MATCH SCORE")
        print("=" * 80)
        print(f"\nSkill Match Score: {skill_score:.1f}/100")
        print(f"Matched Skills: {match_results['total_matched']}/{match_results['total_jd_skills']}")
        print(f"Match Percentage: {(match_results['total_matched'] / max(match_results['total_jd_skills'], 1)) * 100:.1f}%")
        print(f"\nCV Skills: {len(cv_skills_obj.skills)}")
        print(f"Job Description Skills: {len(jd_skills_obj.skills)}")
        
        if not args.no_normalize:
            print(f"\nAfter Normalization:")
            print(f"CV Skills: {len(cv_skills)}")
            print(f"Job Description Skills: {len(jd_skills)}")
        
        print("\n" + "=" * 80)
        
        # Interpretation
        if skill_score >= 80:
            print("\n✅ EXCELLENT: Your CV has exceptional skill match with the job.")
        elif skill_score >= 60:
            print("\n✅ GOOD: Your CV has good skill match with the job.")
        elif skill_score >= 40:
            print("\n⚠️  MODERATE: Your CV has moderate skill match. Consider learning some required skills.")
        else:
            print("\n❌ LOW: Your CV has low skill match. You may need significant skill development.")
        
        print("=" * 80)
        
        # Save report if requested
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            report_content = []
            report_content.append("=" * 80)
            report_content.append("SKILL MATCH ANALYSIS REPORT")
            report_content.append("=" * 80)
            report_content.append("")
            report_content.append(f"CV File: {args.cv_path}")
            report_content.append(f"Job Description File: {args.job_description_path}")
            report_content.append("")
            report_content.append(f"SKILL MATCH SCORE: {skill_score:.1f}/100")
            report_content.append(f"Matched Skills: {match_results['total_matched']}/{match_results['total_jd_skills']}")
            report_content.append(f"Match Percentage: {(match_results['total_matched'] / max(match_results['total_jd_skills'], 1)) * 100:.1f}%")
            report_content.append("")
            report_content.append(skill_matcher.generate_matching_report(match_results))
            report_content.append("")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(report_content))
            
            print(f"\n💾 Report saved to: {output_path}")
        
        # Exit code based on score
        if skill_score >= 70:
            return 0
        elif skill_score >= 50:
            return 0
        else:
            return 1
            
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
