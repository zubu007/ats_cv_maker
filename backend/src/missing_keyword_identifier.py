"""
Missing Keywords Identifier
Identifies important keywords that are missing from the CV.
"""

from typing import List, Dict, Set


class MissingKeywordIdentifier:
    """Identifies missing keywords from CV based on job requirements."""
    
    @staticmethod
    def identify_missing_keywords(
        cv_keywords: List[str],
        required_keywords: List[str],
        optional_keywords: List[str]
    ) -> Dict[str, List[str]]:
        """
        Identify missing keywords from the CV.
        
        Args:
            cv_keywords: Keywords extracted from CV
            required_keywords: Required keywords from job description
            optional_keywords: Optional keywords from job description
            
        Returns:
            Dictionary with missing_required and missing_optional keywords
        """
        # Convert to lowercase sets for comparison
        cv_keywords_lower = set(kw.lower() for kw in cv_keywords)
        required_lower = set(kw.lower() for kw in required_keywords)
        optional_lower = set(kw.lower() for kw in optional_keywords)
        
        # Find missing keywords with partial matching
        missing_required = []
        missing_optional = []
        
        for req_kw in required_keywords:
            if not MissingKeywordIdentifier._is_present(req_kw.lower(), cv_keywords_lower):
                missing_required.append(req_kw)
        
        for opt_kw in optional_keywords:
            if not MissingKeywordIdentifier._is_present(opt_kw.lower(), cv_keywords_lower):
                missing_optional.append(opt_kw)
        
        return {
            'missing_required': missing_required,
            'missing_optional': missing_optional,
            'missing_required_count': len(missing_required),
            'missing_optional_count': len(missing_optional)
        }
    
    @staticmethod
    def prioritize_missing_keywords(
        missing_required: List[str],
        missing_optional: List[str],
        max_keywords: int = 10
    ) -> List[str]:
        """
        Prioritize which missing keywords to add to CV.
        Prioritizes required keywords over optional.
        
        Args:
            missing_required: Missing required keywords
            missing_optional: Missing optional keywords
            max_keywords: Maximum number of keywords to add
            
        Returns:
            List of prioritized keywords to add
        """
        # Start with all required keywords
        prioritized = list(missing_required)
        
        # Add optional keywords if space allows
        remaining_slots = max_keywords - len(prioritized)
        if remaining_slots > 0:
            prioritized.extend(missing_optional[:remaining_slots])
        
        return prioritized[:max_keywords]
    
    @staticmethod
    def _is_present(keyword: str, cv_keywords_set: Set[str]) -> bool:
        """
        Check if keyword is present in CV with fuzzy matching.
        
        Args:
            keyword: Keyword to check
            cv_keywords_set: Set of CV keywords (lowercase)
            
        Returns:
            True if keyword is present
        """
        # Exact match
        if keyword in cv_keywords_set:
            return True
        
        # Partial match - check if keyword is substring or superstring
        for cv_kw in cv_keywords_set:
            if keyword in cv_kw or cv_kw in keyword:
                return True
            
            # Check word overlap
            kw_words = set(keyword.split())
            cv_words = set(cv_kw.split())
            
            if kw_words and cv_words:
                overlap = kw_words & cv_words
                # If 50% or more words overlap, consider it a match
                if len(overlap) / len(kw_words) >= 0.5:
                    return True
        
        return False
    
    @staticmethod
    def generate_missing_keywords_report(missing_data: Dict) -> str:
        """
        Generate a report of missing keywords.
        
        Args:
            missing_data: Dictionary from identify_missing_keywords
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 60)
        report.append("MISSING KEYWORDS REPORT")
        report.append("=" * 60)
        report.append("")
        
        report.append(f"Missing Required Keywords: {missing_data['missing_required_count']}")
        if missing_data['missing_required']:
            for kw in missing_data['missing_required']:
                report.append(f"  ❌ {kw}")
        else:
            report.append("  ✅ All required keywords present!")
        report.append("")
        
        report.append(f"Missing Optional Keywords: {missing_data['missing_optional_count']}")
        if missing_data['missing_optional']:
            for kw in missing_data['missing_optional'][:10]:  # Show first 10
                report.append(f"  ⚠️  {kw}")
            if len(missing_data['missing_optional']) > 10:
                report.append(f"  ... and {len(missing_data['missing_optional']) - 10} more")
        else:
            report.append("  ✅ All optional keywords present!")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)


if __name__ == '__main__':
    # Test the identifier
    cv_keywords = ['python', 'javascript', 'react', 'django', 'postgresql']
    required_keywords = ['Python', 'JavaScript', 'SQL', 'Docker', 'Git']
    optional_keywords = ['React', 'AWS', 'Kubernetes', 'TypeScript']
    
    identifier = MissingKeywordIdentifier()
    missing = identifier.identify_missing_keywords(
        cv_keywords, required_keywords, optional_keywords
    )
    
    print(identifier.generate_missing_keywords_report(missing))
    
    print("\nPrioritized keywords to add:")
    prioritized = identifier.prioritize_missing_keywords(
        missing['missing_required'],
        missing['missing_optional'],
        max_keywords=5
    )
    for kw in prioritized:
        print(f"  • {kw}")
