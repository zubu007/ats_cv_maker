"""
ATS scoring module for calculating keyword match scores.
"""

from typing import Dict, List, Set


class ATSScorer:
    """Calculates ATS scores based on keyword matching."""
    
    @staticmethod
    def calculate_keyword_match_score(
        cv_keywords: List[str],
        required_keywords: List[str],
        optional_keywords: List[str]
    ) -> Dict[str, any]:
        """
        Calculate keyword match score using the formula:
        Score = (matched_required / total_required) * 0.7 + (matched_optional / total_optional) * 0.3
        
        Args:
            cv_keywords: Keywords extracted from CV
            required_keywords: Required keywords from job description
            optional_keywords: Optional keywords from job description
            
        Returns:
            Dictionary containing score details and breakdown
        """
        # Convert to sets for easier matching
        cv_keywords_set = set(kw.lower() for kw in cv_keywords)
        required_set = set(kw.lower() for kw in required_keywords)
        optional_set = set(kw.lower() for kw in optional_keywords)
        
        # Find matches (including partial matches)
        matched_required = ATSScorer._find_matches(cv_keywords_set, required_set)
        matched_optional = ATSScorer._find_matches(cv_keywords_set, optional_set)
        
        # Calculate scores
        total_required = len(required_set)
        total_optional = len(optional_set)
        
        required_score = 0.0
        optional_score = 0.0
        
        if total_required > 0:
            required_score = len(matched_required) / total_required
        
        if total_optional > 0:
            optional_score = len(matched_optional) / total_optional
        
        # Final weighted score
        final_score = (required_score * 0.7) + (optional_score * 0.3)
        
        # Calculate missing keywords
        missing_required = required_set - matched_required
        missing_optional = optional_set - matched_optional
        
        return {
            'final_score': round(final_score * 100, 2),  # As percentage
            'required_score': round(required_score * 100, 2),
            'optional_score': round(optional_score * 100, 2),
            'matched_required': list(matched_required),
            'matched_optional': list(matched_optional),
            'missing_required': list(missing_required),
            'missing_optional': list(missing_optional),
            'total_required': total_required,
            'total_optional': total_optional,
            'matched_required_count': len(matched_required),
            'matched_optional_count': len(matched_optional)
        }
    
    @staticmethod
    def _find_matches(cv_keywords: Set[str], target_keywords: Set[str]) -> Set[str]:
        """
        Find matching keywords between CV and target keywords.
        Supports exact matches and partial matches.
        
        Args:
            cv_keywords: Set of CV keywords
            target_keywords: Set of target keywords to match
            
        Returns:
            Set of matched keywords from target_keywords
        """
        matched = set()
        
        for target_kw in target_keywords:
            # Exact match
            if target_kw in cv_keywords:
                matched.add(target_kw)
                continue
            
            # Partial match: check if target keyword is in any CV keyword
            for cv_kw in cv_keywords:
                if ATSScorer._is_similar(cv_kw, target_kw):
                    matched.add(target_kw)
                    break
        
        return matched
    
    @staticmethod
    def _is_similar(kw1: str, kw2: str, threshold: float = 0.8) -> bool:
        """
        Check if two keywords are similar enough to be considered a match.
        
        Args:
            kw1: First keyword
            kw2: Second keyword
            threshold: Similarity threshold (not used in basic implementation)
            
        Returns:
            True if keywords are similar enough
        """
        # Simple substring matching
        if kw1 in kw2 or kw2 in kw1:
            return True
        
        # Check if words from one keyword appear in the other
        words1 = set(kw1.split())
        words2 = set(kw2.split())
        
        # If significant overlap in words, consider it a match
        if words1 and words2:
            intersection = words1 & words2
            union = words1 | words2
            if len(intersection) / len(union) >= 0.5:
                return True
        
        return False
    
    @staticmethod
    def generate_report(score_data: Dict) -> str:
        """
        Generate a human-readable report from score data.
        
        Args:
            score_data: Score data dictionary from calculate_keyword_match_score
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 60)
        report.append("ATS KEYWORD MATCH SCORE REPORT")
        report.append("=" * 60)
        report.append("")
        
        report.append(f"📊 FINAL SCORE: {score_data['final_score']}%")
        report.append("")
        
        report.append(f"Required Keywords Score: {score_data['required_score']}% "
                     f"({score_data['matched_required_count']}/{score_data['total_required']})")
        report.append(f"Optional Keywords Score: {score_data['optional_score']}% "
                     f"({score_data['matched_optional_count']}/{score_data['total_optional']})")
        report.append("")
        
        report.append("✅ MATCHED REQUIRED KEYWORDS:")
        if score_data['matched_required']:
            for kw in sorted(score_data['matched_required']):
                report.append(f"  • {kw}")
        else:
            report.append("  (none)")
        report.append("")
        
        report.append("✅ MATCHED OPTIONAL KEYWORDS:")
        if score_data['matched_optional']:
            for kw in sorted(score_data['matched_optional']):
                report.append(f"  • {kw}")
        else:
            report.append("  (none)")
        report.append("")
        
        report.append("❌ MISSING REQUIRED KEYWORDS:")
        if score_data['missing_required']:
            for kw in sorted(score_data['missing_required']):
                report.append(f"  • {kw}")
        else:
            report.append("  (none)")
        report.append("")
        
        report.append("⚠️  MISSING OPTIONAL KEYWORDS:")
        if score_data['missing_optional']:
            for kw in sorted(score_data['missing_optional']):
                report.append(f"  • {kw}")
        else:
            report.append("  (none)")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
