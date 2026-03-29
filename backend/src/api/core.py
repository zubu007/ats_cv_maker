"""
Core API service functions
Business logic for API endpoints
"""

from typing import Dict, List, Tuple, Optional, Any
from ..cv_extractor import CVExtractor
from ..keyword_extractor import KeywordExtractor
from ..keyword_rating_agent import KeywordRatingAgent
from ..ats_scorer import ATSScorer
from ..skill_extractor import SkillExtractor
from ..skill_normalizer import SkillNormalizer
from ..skill_matcher import SkillMatcher
from ..cv_section_parser import CVSectionParser
from ..experience_relevance_scorer import ExperienceRelevanceScorer
from ..missing_keyword_identifier import MissingKeywordIdentifier
from ..keyword_placement_agent import KeywordPlacementAgent, ImprovedCVSections
from ..pdf_generator import PDFGenerator
from ..latex_cv_generator import LaTeXCVGenerator
import re
import logging
import tempfile
import os
import base64

logger = logging.getLogger(__name__)

class ATSCVMakerService:
    """Main service class for ATS CV Maker operations"""
    
    def __init__(self):
        """Initialize service components"""
        self.cv_extractor = CVExtractor()
        self.section_parser = CVSectionParser()
    
    def extract_target_job_title(self, jd_text: str, jd_keywords: list) -> str:
        """Extract target job title from job description"""
        patterns = [
            r'(?:Job\s+Title|Position|Role|Title)\s*:\s*([^\n]+)',
            r'^([A-Z][^,\n]+(?:Engineer|Developer|Manager|Analyst|Designer|Architect|Lead|Director))[,\n]',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, jd_text, re.IGNORECASE | re.MULTILINE)
            if match:
                title = match.group(1).strip()
                if len(title) < 100:
                    return title
        
        for kw in jd_keywords:
            if any(word in kw.lower() for word in ['engineer', 'developer', 'manager', 'analyst', 'designer', 'architect']):
                return kw
        
        return jd_keywords[0] if jd_keywords else "Software Engineer"
    
    def analyze_cv(
        self,
        cv_content: str,
        jd_content: str,
        use_spacy: bool = True,
        include_skills: bool = True,
        include_experience: bool = True,
        max_keywords: int = 50
    ) -> Dict[str, Any]:
        """
        Analyze CV against job description.
        
        Args:
            cv_content: CV text content
            jd_content: Job description text content
            use_spacy: Enable spaCy NLP
            include_skills: Include skill matching
            include_experience: Include experience relevance
            max_keywords: Max keywords to extract
            
        Returns:
            Dictionary with analysis results
        """
        # Extract keywords
        keyword_extractor = KeywordExtractor(use_spacy=use_spacy)
        cv_keywords = keyword_extractor.extract_keywords(cv_content, max_keywords=max_keywords)
        jd_keywords = keyword_extractor.extract_keywords(jd_content, max_keywords=max_keywords)
        
        # Rate keywords
        rating_agent = KeywordRatingAgent()
        rated_keywords = rating_agent.rate_keywords(jd_keywords, jd_content)
        
        # Calculate ATS score
        scorer = ATSScorer()
        score_data = scorer.calculate_keyword_match_score(
            cv_keywords=cv_keywords,
            required_keywords=rated_keywords['required'],
            optional_keywords=rated_keywords['optional']
        )
        
        # Skill matching
        skill_score_data = None
        if include_skills:
            try:
                skill_extractor = SkillExtractor()
                cv_skills = skill_extractor.extract_skills_from_cv(cv_content)
                jd_skills = skill_extractor.extract_skills_from_text(jd_content)
                
                skill_normalizer = SkillNormalizer()
                normalized_cv_skills = skill_normalizer.normalize_skills(cv_skills.skills, context="cv")
                normalized_jd_skills = skill_normalizer.normalize_skills(jd_skills.skills, context="jd")
                
                skill_matcher = SkillMatcher()
                skill_score_data = skill_matcher.calculate_skill_match(
                    cv_skills.skills,
                    jd_skills.skills,
                    normalized_cv_skills,
                    normalized_jd_skills
                )
            except Exception:
                skill_score_data = None
        
        # Experience relevance
        experience_score = None
        if include_experience:
            try:
                sections = self.section_parser.parse_cv(cv_content)
                if sections.work_experience:
                    target_job_title = self.extract_target_job_title(jd_content, jd_keywords)
                    
                    scorer_exp = ExperienceRelevanceScorer(use_embeddings=True)
                    cv_experiences = scorer_exp.parse_cv_work_experience(sections.work_experience)
                    
                    if cv_experiences:
                        experience_score = scorer_exp.score_experience(
                            cv_experiences=cv_experiences,
                            target_job_title=target_job_title,
                            target_seniority="Mid"
                        )
            except Exception:
                experience_score = None
        
        return {
            'cv_keywords': cv_keywords,
            'jd_keywords': jd_keywords,
            'rated_keywords': rated_keywords,
            'score_data': score_data,
            'skill_score_data': skill_score_data,
            'experience_score': experience_score,
            'cv_content': cv_content,
            'jd_content': jd_content
        }
    
    def improve_cv(
        self,
        cv_content: str,
        jd_content: str,
        max_keywords_to_add: int = 10,
        use_spacy: bool = True,
        include_experience: bool = True
    ) -> Dict[str, Any]:
        """
        Generate CV improvement recommendations.
        
        Args:
            cv_content: CV text content
            jd_content: Job description text content
            max_keywords_to_add: Max keywords to suggest
            use_spacy: Enable spaCy NLP
            include_experience: Include experience analysis
            
        Returns:
            Dictionary with improvement recommendations
        """
        # First, analyze the CV
        analysis = self.analyze_cv(
            cv_content=cv_content,
            jd_content=jd_content,
            use_spacy=use_spacy,
            include_skills=True,
            include_experience=include_experience,
            max_keywords=50
        )
        
        # Parse CV sections
        sections = self.section_parser.parse_cv(cv_content)
        
        # Identify missing keywords
        identifier = MissingKeywordIdentifier()
        missing_data = identifier.identify_missing_keywords(
            cv_keywords=analysis['cv_keywords'],
            required_keywords=analysis['rated_keywords']['required'],
            optional_keywords=analysis['rated_keywords']['optional']
        )
        
        # Prioritize keywords to add
        keywords_to_add = identifier.prioritize_missing_keywords(
            missing_data['missing_required'],
            missing_data['missing_optional'],
            max_keywords=max_keywords_to_add
        )
        
        # Get placement suggestions using the keyword placement agent
        placement_agent = KeywordPlacementAgent()
        try:
            improved_sections = placement_agent.improve_cv_with_keywords(
                sections=sections,
                keywords_to_add=keywords_to_add,
                job_description=jd_content
            )
            # Create keyword placements from improved sections
            keyword_placements = [
                {
                    'keyword': kw,
                    'suggested_section': 'professional_summary',
                    'suggestion': f'Added to CV',
                    'is_required': kw in analysis['rated_keywords']['required']
                }
                for kw in keywords_to_add
            ]
        except Exception as e:
            # Fallback if improve_cv_with_keywords fails
            keyword_placements = [
                {
                    'keyword': kw,
                    'suggested_section': 'work_experience',
                    'suggestion': f'Consider adding: {kw}',
                    'is_required': kw in analysis['rated_keywords']['required']
                }
                for kw in keywords_to_add
            ]
        
        # Generate improved PDF
        improved_pdf_base64 = None
        try:
            improved_sections_dict = improved_sections if improved_sections else sections
            
            # Convert dict sections to ImprovedCVSections object if needed
            if isinstance(improved_sections_dict, dict):
                improved_sections_obj = ImprovedCVSections(
                    personal_info=improved_sections_dict.get('personal_info', ''),
                    professional_summary=improved_sections_dict.get('professional_summary', ''),
                    skills=improved_sections_dict.get('skills', ''),
                    work_experience=improved_sections_dict.get('work_experience', ''),
                    education=improved_sections_dict.get('education', ''),
                    projects=improved_sections_dict.get('projects', ''),
                    certifications=improved_sections_dict.get('certifications', ''),
                    additional=improved_sections_dict.get('additional', '')
                )
            else:
                improved_sections_obj = improved_sections_dict
            
            # Generate LaTeX from improved sections
            latex_code = LaTeXCVGenerator.generate_latex(improved_sections_obj)
            
            # Create temporary directory for LaTeX compilation
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write LaTeX to file
                tex_path = os.path.join(temp_dir, 'cv.tex')
                with open(tex_path, 'w') as f:
                    f.write(latex_code)
                
                # Compile to PDF
                pdf_path = PDFGenerator.compile_latex_to_pdf(tex_path, temp_dir)
                
                # Convert PDF to base64
                with open(pdf_path, 'rb') as pdf_file:
                    improved_pdf_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error generating improved PDF: {str(e)}")
        
        return {
            'original_analysis': analysis,
            'sections': sections,
            'missing_data': missing_data,
            'keywords_to_add': keywords_to_add,
            'keyword_placements': keyword_placements,
            'improved_pdf_base64': improved_pdf_base64
        }
    
    def match_skills(
        self,
        cv_content: str,
        jd_content: str,
        normalize_skills: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze skill matching between CV and job description.
        
        Args:
            cv_content: CV text content
            jd_content: Job description text content
            normalize_skills: Normalize skills for better matching
            
        Returns:
            Dictionary with skill matching results
        """
        # Extract skills
        skill_extractor = SkillExtractor()
        cv_skills = skill_extractor.extract_skills_from_cv(cv_content)
        jd_skills = skill_extractor.extract_skills_from_job_description(jd_content)
        
        # Normalize if requested
        normalized_cv_skills = None
        normalized_jd_skills = None
        
        if normalize_skills:
            skill_normalizer = SkillNormalizer()
            normalized_cv_skills = skill_normalizer.normalize_skills(cv_skills.skills, context="cv")
            normalized_jd_skills = skill_normalizer.normalize_skills(jd_skills.skills, context="jd")
        
        # Match skills
        skill_matcher = SkillMatcher()
        matched_skills = skill_matcher.calculate_skill_match(
            cv_skills.skills,
            jd_skills.skills,
            normalized_cv_skills,
            normalized_jd_skills
        )
        
        return {
            'cv_skills': cv_skills.skills,
            'jd_skills': jd_skills.skills,
            'normalized_cv_skills': normalized_cv_skills,
            'normalized_jd_skills': normalized_jd_skills,
            'matched_skills': matched_skills
        }
