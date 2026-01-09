"""
Experience Relevance Scorer
Measures how relevant a candidate's past roles are to the target role.
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import re
from difflib import SequenceMatcher

try:
    from sentence_transformers import SentenceTransformer, util
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False


@dataclass
class JobExperience:
    """Job experience entry."""
    job_title: str
    company: str
    duration_years: float
    seniority_level: str = "Mid"  # Junior, Mid, Senior, Lead
    description: str = ""


class ExperienceRelevanceScorer:
    """Scores how relevant past experience is to a target job."""
    
    # Seniority level weights
    SENIORITY_WEIGHTS = {
        'Junior': 0.6,
        'Mid': 0.8,
        'Senior': 1.0,
        'Lead': 1.1
    }
    
    def __init__(self, use_embeddings: bool = True):
        """
        Initialize the experience relevance scorer.
        
        Args:
            use_embeddings: Whether to use sentence embeddings for title similarity
        """
        self.use_embeddings = use_embeddings and EMBEDDINGS_AVAILABLE
        if self.use_embeddings:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"Warning: Could not load embedding model: {e}")
                print("Falling back to simple similarity matching")
                self.use_embeddings = False
    
    def score_experience(
        self,
        cv_experiences: List[JobExperience],
        target_job_title: str,
        target_seniority: str = "Mid"
    ) -> Dict:
        """
        Score how relevant CV experience is to target job.
        
        Formula:
        experience_score = (title_similarity * 0.5) + (seniority_match * 0.3) + (duration_factor * 0.2)
        
        Args:
            cv_experiences: List of job experiences from CV
            target_job_title: Target job title from job description
            target_seniority: Target seniority level
            
        Returns:
            Dictionary with score breakdown
        """
        if not cv_experiences:
            return {
                'experience_relevance_score': 0.0,
                'title_similarity_score': 0.0,
                'seniority_match_score': 0.0,
                'duration_factor_score': 0.0,
                'relevant_experience': [],
                'total_relevant_years': 0.0,
                'matching_positions': 0,
                'details': "No work experience found in CV"
            }
        
        # Calculate title similarity for each position
        title_similarities = []
        seniority_matches = []
        relevant_experiences = []
        
        for exp in cv_experiences:
            title_sim = self._calculate_title_similarity(exp.job_title, target_job_title)
            title_similarities.append(title_sim)
            
            # Only consider positions with >30% title similarity as relevant
            if title_sim > 0.3:
                seniority_match = self._calculate_seniority_match(
                    exp.seniority_level,
                    target_seniority
                )
                seniority_matches.append(seniority_match)
                relevant_experiences.append({
                    'job_title': exp.job_title,
                    'company': exp.company,
                    'duration_years': exp.duration_years,
                    'title_similarity': round(title_sim, 3),
                    'seniority_match': round(seniority_match, 3)
                })
        
        # Calculate aggregate scores
        if not relevant_experiences:
            # No relevant experience found
            return {
                'experience_relevance_score': 0.0,
                'title_similarity_score': 0.0,
                'seniority_match_score': 0.0,
                'duration_factor_score': 0.0,
                'relevant_experience': [],
                'total_relevant_years': 0.0,
                'matching_positions': 0,
                'details': f"No positions similar to '{target_job_title}' found in CV"
            }
        
        # Average title similarity of relevant positions
        title_similarity_score = sum(exp['title_similarity'] for exp in relevant_experiences) / len(relevant_experiences)
        
        # Average seniority match
        seniority_match_score = sum(seniority_matches) / len(seniority_matches)
        
        # Duration factor: years in relevant roles
        total_relevant_years = sum(exp['duration_years'] for exp in relevant_experiences)
        duration_factor_score = self._calculate_duration_factor(total_relevant_years)
        
        # Calculate weighted final score
        final_score = (
            title_similarity_score * 0.5 +
            seniority_match_score * 0.3 +
            duration_factor_score * 0.2
        )
        
        return {
            'experience_relevance_score': round(final_score * 100, 2),
            'title_similarity_score': round(title_similarity_score * 100, 2),
            'seniority_match_score': round(seniority_match_score * 100, 2),
            'duration_factor_score': round(duration_factor_score * 100, 2),
            'relevant_experience': relevant_experiences,
            'total_relevant_years': round(total_relevant_years, 1),
            'matching_positions': len(relevant_experiences),
            'details': f"Found {len(relevant_experiences)} relevant position(s) with {total_relevant_years:.1f} years experience"
        }
    
    def _calculate_title_similarity(self, cv_title: str, target_title: str) -> float:
        """
        Calculate similarity between CV job title and target job title.
        Returns score 0-1.
        
        Args:
            cv_title: Job title from CV
            target_title: Target job title from job description
            
        Returns:
            Similarity score (0-1)
        """
        if self.use_embeddings:
            try:
                # Use sentence embeddings for semantic similarity
                cv_embedding = self.embedding_model.encode(cv_title, convert_to_tensor=True)
                target_embedding = self.embedding_model.encode(target_title, convert_to_tensor=True)
                similarity = util.pytorch_cos_sim(cv_embedding, target_embedding)[0][0].item()
                return float(similarity)
            except Exception as e:
                print(f"Warning: Embedding similarity failed: {e}")
                return self._calculate_simple_title_similarity(cv_title, target_title)
        else:
            return self._calculate_simple_title_similarity(cv_title, target_title)
    
    @staticmethod
    def _calculate_simple_title_similarity(title1: str, title2: str) -> float:
        """
        Calculate simple string similarity between titles.
        
        Args:
            title1: First job title
            title2: Second job title
            
        Returns:
            Similarity score (0-1)
        """
        # Normalize titles
        norm1 = ExperienceRelevanceScorer._normalize_title(title1).lower()
        norm2 = ExperienceRelevanceScorer._normalize_title(title2).lower()
        
        # Calculate sequence similarity
        similarity = SequenceMatcher(None, norm1, norm2).ratio()
        
        # Check for keyword matches (higher weight for exact role matches)
        keywords1 = set(norm1.split())
        keywords2 = set(norm2.split())
        if keywords1 and keywords2:
            intersection = len(keywords1 & keywords2)
            union = len(keywords1 | keywords2)
            keyword_similarity = intersection / union
            # Weight keyword match higher
            similarity = (similarity * 0.4) + (keyword_similarity * 0.6)
        
        return min(similarity, 1.0)
    
    @staticmethod
    def _normalize_title(title: str) -> str:
        """
        Normalize job title by removing seniority levels and extra words.
        
        Args:
            title: Original job title
            
        Returns:
            Normalized title
        """
        # Convert to lowercase
        normalized = title.lower()
        
        # Remove common seniority indicators
        seniority_patterns = [
            r'\b(junior|jr|jr\.|jnr|entry.?level)\b',
            r'\b(senior|sr|sr\.|snr)\b',
            r'\b(lead|staff|principal|director|head|chief)\b',
            r'\b(level\s+)?[i]{1,3}v?\b',  # Roman numerals
            r'\b[0-9]+\b',  # Numbers
        ]
        
        for pattern in seniority_patterns:
            normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)
        
        # Remove extra spaces
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    @staticmethod
    def _calculate_seniority_match(cv_seniority: str, target_seniority: str) -> float:
        """
        Calculate seniority level match score (0-1).
        
        Args:
            cv_seniority: Candidate's seniority level
            target_seniority: Target job seniority level
            
        Returns:
            Match score (0-1)
        """
        seniority_levels = ['Junior', 'Mid', 'Senior', 'Lead']
        
        # Normalize inputs
        cv_level = ExperienceRelevanceScorer._normalize_seniority(cv_seniority)
        target_level = ExperienceRelevanceScorer._normalize_seniority(target_seniority)
        
        # If not found, default to Mid
        cv_idx = seniority_levels.index(cv_level) if cv_level in seniority_levels else 1
        target_idx = seniority_levels.index(target_level) if target_level in seniority_levels else 1
        
        # Calculate difference (closer levels = higher score)
        level_diff = abs(cv_idx - target_idx)
        
        # Map difference to score
        # 0 difference = 1.0, 1 difference = 0.85, 2 = 0.6, 3 = 0.3
        score_map = {0: 1.0, 1: 0.85, 2: 0.6, 3: 0.3}
        return score_map.get(level_diff, 0.2)
    
    @staticmethod
    def _normalize_seniority(seniority: str) -> str:
        """
        Normalize seniority level string.
        
        Args:
            seniority: Seniority level string
            
        Returns:
            Normalized seniority ('Junior', 'Mid', 'Senior', or 'Lead')
        """
        s = seniority.lower().strip()
        
        if any(word in s for word in ['junior', 'jr', 'entry', 'graduate']):
            return 'Junior'
        elif any(word in s for word in ['senior', 'sr', 'snr']):
            return 'Senior'
        elif any(word in s for word in ['lead', 'staff', 'principal', 'director', 'head', 'chief']):
            return 'Lead'
        else:
            return 'Mid'
    
    @staticmethod
    def _calculate_duration_factor(total_years: float) -> float:
        """
        Calculate duration factor score based on years of relevant experience.
        
        More years = higher score, with diminishing returns.
        
        Args:
            total_years: Total years of relevant experience
            
        Returns:
            Duration factor score (0-1)
        """
        # 0 years: 0.0
        # 1 year: 0.2
        # 2 years: 0.4
        # 3 years: 0.6
        # 4+ years: approaching 1.0
        # Uses logarithmic scaling for diminishing returns
        
        if total_years <= 0:
            return 0.0
        elif total_years >= 8:
            return 1.0
        else:
            # Logarithmic scaling: score = (ln(years + 1) / ln(9)) * 1.0
            import math
            return min(math.log(total_years + 1) / math.log(9), 1.0)
    
    def parse_cv_work_experience(self, work_experience_text: str) -> List[JobExperience]:
        """
        Parse work experience text to extract job entries.
        
        Args:
            work_experience_text: Raw work experience text from CV
            
        Returns:
            List of JobExperience objects
        """
        experiences = []
        
        # Split by common section separators (newlines with capital letters or patterns)
        entries = re.split(r'\n(?=[A-Z])', work_experience_text)
        
        for entry in entries:
            if not entry.strip():
                continue
            
            lines = entry.strip().split('\n')
            if not lines:
                continue
            
            # First line usually contains job title
            job_title = lines[0].strip()
            
            # Extract company and duration
            company = ""
            duration_years = 1.0  # Default
            
            for line in lines[1:]:
                line = line.strip()
                
                # Look for date ranges or duration
                date_match = re.search(r'(\d{4})\s*[-–]\s*(?:(\d{4})|present|now)', line, re.IGNORECASE)
                if date_match:
                    start_year = int(date_match.group(1))
                    if date_match.group(2):
                        end_year = int(date_match.group(2))
                    else:
                        # Assume present = current year
                        from datetime import datetime
                        end_year = datetime.now().year
                    
                    duration_years = max(end_year - start_year, 0.5)
                
                # Look for company name (often after job title or in specific patterns)
                if 'company' in line.lower() or any(
                    line.lower().startswith(comp) for comp in ['at ', 'company:', 'employer:']
                ):
                    company = line.split(':', 1)[-1].strip()
            
            # Infer seniority from title
            seniority = self._infer_seniority_from_title(job_title)
            
            experiences.append(JobExperience(
                job_title=job_title,
                company=company,
                duration_years=duration_years,
                seniority_level=seniority,
                description='\n'.join(lines[1:])
            ))
        
        return experiences
    
    @staticmethod
    def _infer_seniority_from_title(job_title: str) -> str:
        """
        Infer seniority level from job title.
        
        Args:
            job_title: Job title string
            
        Returns:
            Seniority level ('Junior', 'Mid', 'Senior', or 'Lead')
        """
        title_lower = job_title.lower()
        
        if any(word in title_lower for word in ['junior', 'jr', 'entry', 'graduate']):
            return 'Junior'
        elif any(word in title_lower for word in ['senior', 'sr', 'snr']):
            return 'Senior'
        elif any(word in title_lower for word in ['lead', 'staff', 'principal', 'director', 'head', 'chief', 'manager', 'architect']):
            return 'Lead'
        else:
            return 'Mid'
