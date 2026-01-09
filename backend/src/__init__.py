"""
ATS CV Maker - Intelligent CV scoring and improvement system.

This package provides tools to analyze CVs against job descriptions,
identify missing keywords, and automatically generate improved CVs.
Includes experience relevance scoring for better candidate evaluation.
"""

__version__ = "0.2.0"

from .cv_extractor import CVExtractor
from .keyword_extractor import KeywordExtractor
from .keyword_rating_agent import KeywordRatingAgent
from .ats_scorer import ATSScorer
from .cv_section_parser import CVSectionParser
from .missing_keyword_identifier import MissingKeywordIdentifier
from .keyword_placement_agent import KeywordPlacementAgent
from .latex_cv_generator import LaTeXCVGenerator
from .pdf_generator import PDFGenerator
from .experience_relevance_scorer import ExperienceRelevanceScorer, JobExperience
from .job_title_normalizer import JobTitleNormalizer

__all__ = [
    "CVExtractor",
    "KeywordExtractor",
    "KeywordRatingAgent",
    "ATSScorer",
    "CVSectionParser",
    "MissingKeywordIdentifier",
    "KeywordPlacementAgent",
    "LaTeXCVGenerator",
    "PDFGenerator",
    "ExperienceRelevanceScorer",
    "JobExperience",
    "JobTitleNormalizer",
]
