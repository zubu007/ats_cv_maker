"""
Skill Matcher and Scorer
Matches skills between CV and job description, calculates skill match score.
"""

from typing import List, Dict, Set, Tuple
from difflib import SequenceMatcher
import re


class SkillMatcher:
    """Matches skills between CV and job description with fuzzy matching."""
    
    def __init__(self, similarity_threshold: float = 0.8):
        """
        Initialize the skill matcher.
        
        Args:
            similarity_threshold: Minimum similarity score for fuzzy matching (0-1)
        """
        self.similarity_threshold = similarity_threshold
    
    @staticmethod
    def normalize_skill_for_matching(skill: str) -> str:
        """
        Normalize skill name for comparison (lowercase, remove special chars).
        
        Args:
            skill: Original skill name
            
        Returns:
            Normalized skill name
        """
        # Convert to lowercase
        normalized = skill.lower()
        # Remove common punctuation and extra spaces
        normalized = re.sub(r'[.,\-/]+', ' ', normalized)
        # Remove extra spaces
        normalized = ' '.join(normalized.split())
        return normalized
    
    def fuzzy_match_skill(self, cv_skill: str, jd_skills: List[str]) -> Tuple[str, float]:
        """
        Find the best fuzzy match for a CV skill in job description skills.
        
        Args:
            cv_skill: Skill from CV
            jd_skills: List of skills from job description
            
        Returns:
            Tuple of (matched_skill, similarity_score) or (None, 0.0) if no match
        """
        cv_normalized = self.normalize_skill_for_matching(cv_skill)
        best_match = None
        best_score = 0.0
        
        for jd_skill in jd_skills:
            jd_normalized = self.normalize_skill_for_matching(jd_skill)
            
            # Calculate similarity
            similarity = SequenceMatcher(None, cv_normalized, jd_normalized).ratio()
            
            if similarity > best_score:
                best_score = similarity
                best_match = jd_skill
        
        if best_score >= self.similarity_threshold:
            return best_match, best_score
        
        return None, 0.0
    
    def match_skills(
        self,
        cv_skills: List[str],
        jd_skills: List[str],
        verbose: bool = False
    ) -> Dict[str, any]:
        """
        Match CV skills with job description skills.
        
        Args:
            cv_skills: List of skills extracted from CV
            jd_skills: List of skills extracted from job description
            verbose: Whether to print matching details
            
        Returns:
            Dictionary with matching results
        """
        matched_skills = []
        unmatched_cv_skills = []
        match_details = []
        
        for cv_skill in cv_skills:
            jd_skill, similarity = self.fuzzy_match_skill(cv_skill, jd_skills)
            
            if jd_skill:
                matched_skills.append({
                    'cv_skill': cv_skill,
                    'jd_skill': jd_skill,
                    'similarity': similarity
                })
                if verbose:
                    print(f"✓ Matched: '{cv_skill}' → '{jd_skill}' (similarity: {similarity:.2%})")
                match_details.append({
                    'type': 'matched',
                    'cv_skill': cv_skill,
                    'jd_skill': jd_skill,
                    'similarity': similarity
                })
            else:
                unmatched_cv_skills.append(cv_skill)
                if verbose:
                    print(f"✗ Not matched: '{cv_skill}'")
                match_details.append({
                    'type': 'unmatched',
                    'cv_skill': cv_skill
                })
        
        return {
            'matched_skills': matched_skills,
            'unmatched_cv_skills': unmatched_cv_skills,
            'match_details': match_details,
            'total_matched': len(matched_skills),
            'total_cv_skills': len(cv_skills),
            'total_jd_skills': len(jd_skills)
        }
    
    @staticmethod
    def calculate_skill_score(
        matched_skills_count: int,
        jd_skills_count: int
    ) -> float:
        """
        Calculate skill match score.
        
        Formula: (matched_skills / jd_skills_count) * 100
        
        Args:
            matched_skills_count: Number of matched skills
            jd_skills_count: Total skills found in job description
            
        Returns:
            Skill match score (0-100)
        """
        if jd_skills_count == 0:
            return 0.0
        
        score = (matched_skills_count / jd_skills_count) * 100
        return min(score, 100.0)  # Cap at 100
    
    @staticmethod
    def generate_matching_report(match_results: Dict) -> str:
        """
        Generate a detailed matching report.
        
        Args:
            match_results: Dictionary from match_skills()
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("🎯 Skill Matching Report")
        report.append("=" * 80)
        report.append("")
        
        report.append("📊 Summary:")
        report.append(f"  CV Skills: {match_results['total_cv_skills']}")
        report.append(f"  Job Description Skills: {match_results['total_jd_skills']}")
        report.append(f"  Matched Skills: {match_results['total_matched']}")
        report.append(f"  Unmatched Skills: {len(match_results['unmatched_cv_skills'])}")
        report.append(f"  Match Rate: {match_results['total_matched']}/{match_results['total_jd_skills']} " +
                     f"({(match_results['total_matched'] / max(match_results['total_jd_skills'], 1)) * 100:.1f}%)")
        report.append("")
        
        report.append("✓ Matched Skills:")
        for match in sorted(match_results['matched_skills'], 
                           key=lambda x: x['similarity'], reverse=True):
            report.append(f"  {match['cv_skill']} → {match['jd_skill']} " +
                         f"(similarity: {match['similarity']:.2%})")
        report.append("")
        
        if match_results['unmatched_cv_skills']:
            report.append("✗ Unmatched Skills (not found in job description):")
            for skill in match_results['unmatched_cv_skills']:
                report.append(f"  • {skill}")
            report.append("")
        
        report.append("=" * 80)
        return "\n".join(report)


if __name__ == '__main__':
    # Test the skill matcher
    cv_skills = [
        "Python",
        "JavaScript",
        "React",
        "Node.js",
        "PostgreSQL",
        "Docker",
        "Git"
    ]
    
    jd_skills = [
        "Python",
        "TypeScript",
        "React.js",
        "Node",
        "Postgres",
        "Docker",
        "GitHub",
        "AWS",
        "Kubernetes"
    ]
    
    matcher = SkillMatcher()
    print("🔍 Matching skills between CV and job description...\n")
    
    results = matcher.match_skills(cv_skills, jd_skills, verbose=True)
    print("\n" + matcher.generate_matching_report(results))
    
    skill_score = matcher.calculate_skill_score(
        results['total_matched'],
        results['total_jd_skills']
    )
    print(f"\n🏆 Skill Match Score: {skill_score:.1f}/100")
