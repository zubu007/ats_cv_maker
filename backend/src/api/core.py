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
from ..section_comparator import SectionComparator
from ..jd_summarizer import JDSummarizer
from ..cover_letter_generator import CoverLetterGenerator
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
                jd_skills = skill_extractor.extract_skills_from_job_description(jd_content)
                
                skill_matcher = SkillMatcher()
                match_results = skill_matcher.match_skills(
                    cv_skills.skills,
                    jd_skills.skills
                )
                
                # Calculate skill score
                skill_score_data = {
                    'cv_skills': cv_skills.skills,
                    'jd_skills': jd_skills.skills,
                    'matched_skills': [m['cv_skill'] for m in match_results['matched_skills']],
                    'missing_skills': [s for s in jd_skills.skills if not any(m['jd_skill'] == s for m in match_results['matched_skills'])],
                    'skill_match_percentage': SkillMatcher.calculate_skill_score(
                        match_results['total_matched'],
                        match_results['total_jd_skills']
                    )
                }
            except Exception as e:
                logger.error(f"Error in skill matching: {str(e)}")
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

        # Section-by-section comparisons
        section_comparisons = []
        try:
            comparator = SectionComparator()
            
            # Parse CV sections for comparison
            try:
                cv_sections = self.section_parser.parse_cv(cv_content)
            except:
                cv_sections = None
            
            # Compare Skills
            if skill_score_data and 'cv_skills' in skill_score_data and 'jd_skills' in skill_score_data:
                skills_comparison = comparator.compare_skills(
                    skill_score_data['cv_skills'][:15],
                    skill_score_data['jd_skills'][:15]
                )
                section_comparisons.append(skills_comparison)
            
            # Compare Keywords
            keywords_comparison = comparator.compare_keywords(
                cv_keywords[:15],
                rated_keywords['required'][:10],
                rated_keywords['optional'][:10]
            )
            section_comparisons.append(keywords_comparison)
            
            # Compare Education
            if cv_sections and cv_sections.education:
                education_comparison = comparator.compare_education(
                    cv_sections.education,
                    jd_content
                )
                section_comparisons.append(education_comparison)
            
            # Compare Experience
            if experience_score:
                experience_comparison = comparator.compare_experience(
                    experience_score.get('experience_count', 0),
                    jd_content
                )
                section_comparisons.append(experience_comparison)
                
        except Exception as e:
            logger.error(f"Error creating section comparisons: {str(e)}")
            section_comparisons = []
        
        return {
            'cv_keywords': cv_keywords,
            'jd_keywords': jd_keywords,
            'rated_keywords': rated_keywords,
            'score_data': score_data,
            'skill_score_data': skill_score_data,
            'experience_score': experience_score,
            'section_comparisons': section_comparisons,
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
        improved_sections = None
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
            logger.error(f"Error improving CV with keywords: {str(e)}")
            improved_sections = None
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
            # Use improved sections if available, otherwise use original sections
            if improved_sections:
                # improved_sections is already an ImprovedCVSections object
                sections_for_pdf = improved_sections
            else:
                # Convert CVSections to ImprovedCVSections
                sections_for_pdf = ImprovedCVSections(
                    personal_info=sections.personal_info,
                    professional_summary=sections.professional_summary,
                    skills=sections.skills,
                    work_experience=sections.work_experience,
                    education=sections.education,
                    projects=sections.projects or '',
                    certifications=sections.certifications or '',
                    additional=sections.additional or '',
                    placement_notes='No improvements applied - using original CV sections.'
                )
            
            # Generate LaTeX from sections
            latex_code = LaTeXCVGenerator.generate_latex(sections_for_pdf)
            
            # Create temporary directory for LaTeX compilation
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write LaTeX to file
                tex_path = os.path.join(temp_dir, 'cv.tex')
                with open(tex_path, 'w', encoding='utf-8') as f:
                    f.write(latex_code)
                
                # Compile to PDF
                pdf_path = PDFGenerator.compile_latex_to_pdf(tex_path, temp_dir)
                
                # Convert PDF to base64
                with open(pdf_path, 'rb') as pdf_file:
                    improved_pdf_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error generating improved PDF: {str(e)}")
            # Don't raise, just log - PDF generation is optional
        
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
        match_results = skill_matcher.match_skills(
            cv_skills.skills,
            jd_skills.skills
        )
        
        # Calculate missing skills
        missing_skills = [
            s for s in jd_skills.skills 
            if not any(m['jd_skill'] == s for m in match_results['matched_skills'])
        ]
        
        return {
            'cv_skills': cv_skills.skills,
            'jd_skills': jd_skills.skills,
            'normalized_cv_skills': normalized_cv_skills,
            'normalized_jd_skills': normalized_jd_skills,
            'matched_skills': match_results['matched_skills'],
            'missing_skills': missing_skills,
            'skill_match_percentage': SkillMatcher.calculate_skill_score(
                match_results['total_matched'],
                match_results['total_jd_skills']
            )
        }

    def score_cv(self, cv_content: str, job_description: str) -> Dict[str, Any]:
        """
        Summarizes the JD and scores the CV against it.
        """
        # Step 1: Summarize the Job Description
        jd_summarizer = JDSummarizer()
        jd_summary = jd_summarizer.summarize(job_description)
        
        # Step 2: Extract keywords from the CV
        keyword_extractor = KeywordExtractor(use_spacy=False) # Keep it fast
        cv_keywords = keyword_extractor.extract_keywords(cv_content, max_keywords=100)

        # Step 3: Score CV against the summarized JD
        score = self._calculate_score(cv_keywords, jd_summary)

        return {
            "jd_summary": jd_summary,
            "cv_keywords": cv_keywords,
            "score": score,
        }

    def _calculate_score(self, cv_keywords: List[str], jd_summary: Dict[str, List[str]]) -> float:
        """
        Calculates a score based on keyword matches.
        """
        if not jd_summary["task_description"] and not jd_summary["candidate_requirements"]:
            return 0.0

        # Combine JD points into a single string for matching
        jd_text = " ".join(jd_summary["task_description"] + jd_summary["candidate_requirements"])
        
        if not jd_text:
            return 0.0

        matched_keywords = 0
        for keyword in cv_keywords:
            if keyword.lower() in jd_text.lower():
                matched_keywords += 1
        
        # Simple scoring: percentage of CV keywords that appear in the JD summary
        # This can be improved with more advanced scoring logic
        score = (matched_keywords / len(cv_keywords)) * 100 if cv_keywords else 0.0
        
        return min(score, 100.0)

    def generate_cover_letter(self, cv_content: str, job_description: str) -> Dict[str, str]:
        """
        Generates a cover letter.
        """
        generator = CoverLetterGenerator()
        result = generator.generate(
            cv_content=cv_content,
            job_description=job_description,
        )
        return result
