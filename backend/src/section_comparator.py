"""
Section Comparator Service
Compares CV sections with Job Description requirements
"""

from typing import List, Dict, Any
from difflib import SequenceMatcher


class SectionComparator:
    """Compares sections between CV and Job Description"""
    
    def __init__(self, similarity_threshold: float = 0.8):
        """
        Initialize the section comparator.
        
        Args:
            similarity_threshold: Minimum similarity for fuzzy matching (0-1)
        """
        self.similarity_threshold = similarity_threshold
    
    @staticmethod
    def normalize_item(item: str) -> str:
        """Normalize item for comparison"""
        return item.lower().strip()
    
    def fuzzy_match(self, item1: str, item2: str) -> float:
        """
        Calculate similarity between two items.
        
        Args:
            item1: First item
            item2: Second item
            
        Returns:
            Similarity score (0-1)
        """
        norm1 = self.normalize_item(item1)
        norm2 = self.normalize_item(item2)
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def find_matches(
        self,
        cv_items: List[str],
        jd_items: List[str]
    ) -> Dict[str, List[str]]:
        """
        Find matching items between CV and JD.
        
        Args:
            cv_items: Items from CV
            jd_items: Items from JD
            
        Returns:
            Dictionary with matched, missing, and extra items
        """
        matched = []
        missing = []
        extra = []
        
        # Track which JD items have been matched
        jd_matched = set()
        
        for cv_item in cv_items:
            best_match = None
            best_score = 0.0
            
            for jd_item in jd_items:
                if jd_item in jd_matched:
                    continue
                    
                similarity = self.fuzzy_match(cv_item, jd_item)
                if similarity > best_score:
                    best_score = similarity
                    best_match = jd_item
            
            if best_match and best_score >= self.similarity_threshold:
                matched.append(best_match)
                jd_matched.add(best_match)
            else:
                extra.append(cv_item)
        
        # Items in JD but not matched in CV
        missing = [item for item in jd_items if item not in jd_matched]
        
        return {
            'matched': matched,
            'missing': missing,
            'extra': extra
        }
    
    def compare_skills(
        self,
        cv_skills: List[str],
        jd_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Compare skills section.
        
        Args:
            cv_skills: Skills from CV
            jd_skills: Skills from JD
            
        Returns:
            Section comparison data
        """
        result = self.find_matches(cv_skills, jd_skills)
        
        match_percentage = 0.0
        if len(jd_skills) > 0:
            match_percentage = (len(result['matched']) / len(jd_skills)) * 100
        
        return {
            'section_name': 'skills',
            'cv_items': cv_skills,
            'jd_items': jd_skills,
            'matched_items': result['matched'],
            'missing_items': result['missing'],
            'extra_items': result['extra'],
            'match_percentage': match_percentage
        }
    
    def compare_education(
        self,
        cv_education: str,
        jd_education: str
    ) -> Dict[str, Any]:
        """
        Compare education section.
        
        Args:
            cv_education: Education text from CV
            jd_education: Education requirements from JD
            
        Returns:
            Section comparison data
        """
        # Simple keyword-based comparison for education
        cv_keywords = self._extract_education_keywords(cv_education)
        jd_keywords = self._extract_education_keywords(jd_education)
        
        result = self.find_matches(cv_keywords, jd_keywords)
        
        match_percentage = 0.0
        if len(jd_keywords) > 0:
            match_percentage = (len(result['matched']) / len(jd_keywords)) * 100
        
        return {
            'section_name': 'education',
            'cv_items': cv_keywords,
            'jd_items': jd_keywords,
            'matched_items': result['matched'],
            'missing_items': result['missing'],
            'extra_items': result['extra'],
            'match_percentage': match_percentage
        }
    
    def compare_keywords(
        self,
        cv_keywords: List[str],
        required_keywords: List[str],
        optional_keywords: List[str]
    ) -> Dict[str, Any]:
        """
        Compare keywords (required + optional).
        
        Args:
            cv_keywords: Keywords from CV
            required_keywords: Required keywords from JD
            optional_keywords: Optional keywords from JD
            
        Returns:
            Section comparison data
        """
        all_jd_keywords = required_keywords + optional_keywords
        result = self.find_matches(cv_keywords, all_jd_keywords)
        
        match_percentage = 0.0
        if len(all_jd_keywords) > 0:
            match_percentage = (len(result['matched']) / len(all_jd_keywords)) * 100
        
        return {
            'section_name': 'keywords',
            'cv_items': cv_keywords[:20],  # Limit to top 20
            'jd_items': all_jd_keywords[:20],
            'matched_items': result['matched'],
            'missing_items': result['missing'],
            'extra_items': result['extra'],
            'match_percentage': match_percentage
        }
    
    def compare_experience(
        self,
        cv_experience_count: int,
        jd_experience_requirement: str
    ) -> Dict[str, Any]:
        """
        Compare experience requirements.
        
        Args:
            cv_experience_count: Number of years/positions in CV
            jd_experience_requirement: Experience requirement text
            
        Returns:
            Section comparison data
        """
        # Extract years from JD requirement
        import re
        years_match = re.search(r'(\d+)\+?\s*years?', jd_experience_requirement, re.IGNORECASE)
        required_years = int(years_match.group(1)) if years_match else 0
        
        cv_items = [f"{cv_experience_count} years experience"]
        jd_items = [f"{required_years}+ years required"] if required_years > 0 else ["Experience required"]
        
        matched = cv_items if cv_experience_count >= required_years else []
        missing = [] if matched else jd_items
        
        match_percentage = 100.0 if matched else 0.0
        
        return {
            'section_name': 'experience',
            'cv_items': cv_items,
            'jd_items': jd_items,
            'matched_items': matched,
            'missing_items': missing,
            'extra_items': [],
            'match_percentage': match_percentage
        }
    
    @staticmethod
    def _extract_education_keywords(text: str) -> List[str]:
        """Extract education-related keywords from text"""
        keywords = []
        
        # Degree patterns
        degree_patterns = [
            r"bachelor'?s?",
            r"master'?s?",
            r"phd",
            r"doctorate",
            r"associate'?s?",
            r"diploma",
            r"b\.?s\.?",
            r"m\.?s\.?",
            r"m\.?b\.?a\.?",
            r"b\.?a\.?"
        ]
        
        # Field patterns
        field_patterns = [
            r"computer science",
            r"software engineering",
            r"information technology",
            r"engineering",
            r"mathematics",
            r"physics",
            r"business",
            r"data science"
        ]
        
        text_lower = text.lower()
        
        import re
        for pattern in degree_patterns + field_patterns:
            if re.search(pattern, text_lower):
                keywords.append(pattern.replace(r"\.?\??'?s?", "").replace("\\", ""))
        
        return list(set(keywords))
