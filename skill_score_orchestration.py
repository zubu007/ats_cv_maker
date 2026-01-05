"""
Skill Scoring Orchestration
Complete workflow for extracting, normalizing, and matching skills.
"""

import sys
from typing import Dict, Tuple
from src.ats_cv_maker.cv_extractor import CVExtractor
from src.ats_cv_maker.skill_extractor import SkillExtractor, SkillList
from src.ats_cv_maker.skill_normalizer import SkillNormalizer, NormalizedSkillList
from src.ats_cv_maker.skill_matcher import SkillMatcher


def extract_and_normalize_cv_skills(
    cv_text: str,
    verbose: bool = False
) -> Tuple[list, list]:
    """
    Extract and normalize skills from CV text.
    
    Args:
        cv_text: Full CV text
        verbose: Print detailed output
        
    Returns:
        Tuple of (original_skills, normalized_merged_skills)
    """
    # Extract skills
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 1: Extracting skills from CV...")
        print("=" * 80)
    
    extractor = SkillExtractor()
    cv_skills = extractor.extract_skills_from_cv(cv_text)
    
    if verbose:
        print(extractor.generate_skills_report(cv_skills, "📄 CV Skills Extracted"))
    
    # Normalize skills
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 2: Normalizing CV skills...")
        print("=" * 80)
    
    normalizer = SkillNormalizer()
    normalized_cv_skills = normalizer.normalize_skills(cv_skills.skills, context="cv")
    
    if verbose:
        print(normalizer.generate_normalization_report(normalized_cv_skills, len(cv_skills.skills)))
    
    # Merge original and normalized skills
    merged_cv_skills, cv_skill_mappings = normalizer.merge_skills(
        cv_skills.skills,
        normalized_cv_skills
    )
    
    if verbose:
        print(f"\n✅ Merged CV Skills ({len(merged_cv_skills)} total)")
    
    return cv_skills.skills, merged_cv_skills


def extract_and_normalize_jd_skills(
    jd_text: str,
    verbose: bool = False
) -> Tuple[list, list]:
    """
    Extract and normalize skills from job description text.
    
    Args:
        jd_text: Job description text
        verbose: Print detailed output
        
    Returns:
        Tuple of (original_skills, normalized_merged_skills)
    """
    # Extract skills
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 3: Extracting skills from job description...")
        print("=" * 80)
    
    extractor = SkillExtractor()
    jd_skills = extractor.extract_skills_from_job_description(jd_text)
    
    if verbose:
        print(extractor.generate_skills_report(jd_skills, "💼 Job Description Skills Extracted"))
    
    # Normalize skills
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 4: Normalizing job description skills...")
        print("=" * 80)
    
    normalizer = SkillNormalizer()
    normalized_jd_skills = normalizer.normalize_skills(jd_skills.skills, context="job_description")
    
    if verbose:
        print(normalizer.generate_normalization_report(normalized_jd_skills, len(jd_skills.skills)))
    
    # Merge original and normalized skills
    merged_jd_skills, jd_skill_mappings = normalizer.merge_skills(
        jd_skills.skills,
        normalized_jd_skills
    )
    
    if verbose:
        print(f"\n✅ Merged Job Description Skills ({len(merged_jd_skills)} total)")
    
    return jd_skills.skills, merged_jd_skills


def calculate_skill_match_score(
    cv_skills: list,
    jd_skills: list,
    verbose: bool = False
) -> Dict:
    """
    Match CV skills with job description skills and calculate score.
    
    Args:
        cv_skills: List of CV skills (preferably normalized)
        jd_skills: List of JD skills (preferably normalized)
        verbose: Print detailed output
        
    Returns:
        Dictionary with skill matching results and score
    """
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 5: Matching skills between CV and job description...")
        print("=" * 80)
    
    matcher = SkillMatcher(similarity_threshold=0.8)
    match_results = matcher.match_skills(cv_skills, jd_skills, verbose=verbose)
    
    if verbose:
        print(matcher.generate_matching_report(match_results))
    
    skill_score = matcher.calculate_skill_score(
        match_results['total_matched'],
        match_results['total_jd_skills']
    )
    
    if verbose:
        print(f"\n🏆 Skill Match Score: {skill_score:.1f}/100")
    
    return {
        'skill_match_score': skill_score,
        'match_results': match_results,
        'total_matched': match_results['total_matched'],
        'total_jd_skills': match_results['total_jd_skills'],
        'match_percentage': (match_results['total_matched'] / max(match_results['total_jd_skills'], 1)) * 100
    }


def analyze_skills(
    cv_file: str,
    jd_file: str,
    verbose: bool = True,
    normalize: bool = True
) -> Dict:
    """
    Complete skill analysis workflow.
    
    Args:
        cv_file: Path to CV file
        jd_file: Path to job description file
        verbose: Print detailed output
        normalize: Whether to normalize skills
        
    Returns:
        Dictionary with complete skill analysis results
    """
    # Extract CV and JD texts
    cv_extractor = CVExtractor()
    cv_text = cv_extractor.extract(cv_file)
    jd_text = cv_extractor.extract(jd_file)
    
    if normalize:
        # Extract and normalize skills
        _, cv_skills = extract_and_normalize_cv_skills(cv_text, verbose)
        _, jd_skills = extract_and_normalize_jd_skills(jd_text, verbose)
    else:
        # Just extract skills without normalization
        extractor = SkillExtractor()
        cv_skills_obj = extractor.extract_skills_from_cv(cv_text)
        jd_skills_obj = extractor.extract_skills_from_job_description(jd_text)
        cv_skills = cv_skills_obj.skills
        jd_skills = jd_skills_obj.skills
    
    # Match skills and calculate score
    results = calculate_skill_match_score(cv_skills, jd_skills, verbose)
    
    return {
        'cv_skills': cv_skills,
        'jd_skills': jd_skills,
        'skill_match_score': results['skill_match_score'],
        'total_matched': results['total_matched'],
        'total_jd_skills': results['total_jd_skills'],
        'match_percentage': results['match_percentage'],
        'match_results': results['match_results']
    }


def print_skill_score_summary(skill_analysis: Dict) -> None:
    """
    Print a summary of skill analysis.
    
    Args:
        skill_analysis: Dictionary from analyze_skills()
    """
    print("\n" + "=" * 80)
    print("📊 SKILL ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"\nCV Skills Analyzed: {len(skill_analysis['cv_skills'])}")
    print(f"Job Description Skills: {len(skill_analysis['jd_skills'])}")
    print(f"Matched Skills: {skill_analysis['total_matched']}")
    print(f"\n🏆 SKILL MATCH SCORE: {skill_analysis['skill_match_score']:.1f}/100")
    print(f"Match Percentage: {skill_analysis['match_percentage']:.1f}%")
    print("=" * 80)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python -m src.ats_cv_maker.skill_score_orchestration <cv_file> <jd_file> [--no-normalize] [--quiet]")
        print("\nExample:")
        print("  python -m src.ats_cv_maker.skill_score_orchestration examples/sample_cv.txt examples/sample_job_description.txt")
        sys.exit(1)
    
    cv_file = sys.argv[1]
    jd_file = sys.argv[2]
    
    normalize = '--no-normalize' not in sys.argv
    verbose = '--quiet' not in sys.argv
    
    print("\n🚀 Starting Skill Analysis...")
    
    results = analyze_skills(cv_file, jd_file, verbose=verbose, normalize=normalize)
    
    if not verbose:
        print_skill_score_summary(results)
