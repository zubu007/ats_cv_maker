"""
ATS CV Maker - Intelligent CV scoring and improvement system.

This package provides tools to analyze CVs against job descriptions,
identify missing keywords, and automatically generate improved CVs.
"""

__version__ = "0.2.0"

from src.ats_cv_maker.cv_extractor import CVExtractor
from src.ats_cv_maker.keyword_extractor import KeywordExtractor
from src.ats_cv_maker.keyword_rating_agent import KeywordRatingAgent
from src.ats_cv_maker.ats_scorer import ATSScorer
from src.ats_cv_maker.cv_section_parser import CVSectionParser
from src.ats_cv_maker.missing_keyword_identifier import MissingKeywordIdentifier
from src.ats_cv_maker.keyword_placement_agent import KeywordPlacementAgent
from src.ats_cv_maker.latex_cv_generator import LaTeXCVGenerator
from src.ats_cv_maker.pdf_generator import PDFGenerator

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
]
