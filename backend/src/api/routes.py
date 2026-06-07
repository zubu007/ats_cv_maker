"""
API Routes
REST API endpoints for ATS CV Maker
"""

from fastapi import APIRouter, HTTPException, File, UploadFile
from typing import Optional
import logging

from .models import (
    CVAnalysisRequest,
    CVAnalysisResponse,
    CVImprovementRequest,
    CVImprovementResponse,
    SkillMatchingRequest,
    SkillMatchingResponse,
    AtsScoreResponse,
    KeywordData,
    RatedKeywords,
    SkillData,
    KeywordPlacement,
    SectionComparison,
    CVScoreRequest,
    CVScoreResponse,
    CoverLetterRequest,
    CoverLetterResponse,
    RenderPDFRequest,
    RenderPDFResponse,
)
from .core import ATSCVMakerService
from ..cover_letter_generator import CoverLetterGenerator

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["ATS CV Maker"])

# Initialize service
service = ATSCVMakerService()


@router.post("/analyze", response_model=CVAnalysisResponse)
async def analyze_cv(request: CVAnalysisRequest):
    """
    Analyze CV against job description.
    
    Extracts keywords, rates them, calculates ATS score, and optionally
    performs skill matching and experience relevance analysis.
    
    Args:
        request: CVAnalysisRequest with CV and job description content
        
    Returns:
        CVAnalysisResponse with complete analysis results
    """
    try:
        result = service.analyze_cv(
            cv_content=request.cv_content,
            jd_content=request.job_description,
            use_spacy=request.use_spacy,
            include_skills=request.include_skills,
            include_experience=request.include_experience,
            max_keywords=request.max_keywords
        )
        
        # Format CV keywords
        cv_keywords = [
            KeywordData(
                keyword=kw,
                frequency=result['cv_keywords'].count(kw),
                relevance_score=0.5
            )
            for kw in set(result['cv_keywords'][:20])
        ]
        
        # Format JD keywords
        jd_keywords = [
            KeywordData(
                keyword=kw,
                frequency=result['jd_keywords'].count(kw),
                relevance_score=0.7
            )
            for kw in set(result['jd_keywords'][:20])
        ]
        
        # Format ATS score
        score_data = result['score_data']
        ats_score = AtsScoreResponse(
            score=score_data.get('score', 0),
            percentage=score_data.get('percentage', 0),
            matched_required=score_data.get('matched_required_count', 0),
            total_required=score_data.get('total_required', 0),
            matched_optional=score_data.get('matched_optional_count', 0),
            total_optional=score_data.get('total_optional', 0)
        )
        
        # Format rated keywords
        rated_keywords = RatedKeywords(
            required=result['rated_keywords']['required'][:10],
            optional=result['rated_keywords']['optional'][:10]
        )
        
        # Format experience score if available
        experience_score = None
        if result.get('experience_score'):
            experience_score = result['experience_score']

        # Format section comparisons
        section_comparisons_list = None
        if result.get('section_comparisons'):
            section_comparisons_list = [
                SectionComparison(**comp) for comp in result['section_comparisons']
            ]
        
        # Create summary
        summary = f"CV Analysis Complete: {ats_score.percentage:.1f}% match with {ats_score.matched_required}/{ats_score.total_required} required keywords."
        
        return CVAnalysisResponse(
            cv_keywords=cv_keywords,
            jd_keywords=jd_keywords,
            rated_keywords=rated_keywords,
            ats_score=ats_score,
            skill_score=result['skill_score_data'],
            experience_score=experience_score,
            section_comparisons=section_comparisons_list,
            analysis_summary=summary
        )
        
    except Exception as e:
        logger.error(f"Error analyzing CV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing CV: {str(e)}")


@router.post("/improve", response_model=CVImprovementResponse)
async def improve_cv(request: CVImprovementRequest):
    """
    Generate CV improvement recommendations.
    
    Identifies missing keywords, suggests placements, and estimates
    the improved ATS score.
    
    Args:
        request: CVImprovementRequest with CV and job description content
        
    Returns:
        CVImprovementResponse with improvement recommendations
    """
    try:
        result = service.improve_cv(
            cv_content=request.cv_content,
            jd_content=request.job_description,
            max_keywords_to_add=request.max_keywords_to_add,
            use_spacy=request.use_spacy,
            include_experience=request.include_experience
        )
        
        # Format original score
        score_data = result['original_analysis']['score_data']
        original_score = AtsScoreResponse(
            score=score_data.get('score', 0),
            percentage=score_data.get('percentage', 0),
            matched_required=score_data.get('matched_required_count', 0),
            total_required=score_data.get('total_required', 0),
            matched_optional=score_data.get('matched_optional_count', 0),
            total_optional=score_data.get('total_optional', 0)
        )
        
        # Estimate new score (assuming all keywords would be added)
        estimated_new_score = AtsScoreResponse(
            score=min(100, score_data.get('score', 0) + len(result['keywords_to_add']) * 2),
            percentage=min(100, score_data.get('percentage', 0) + len(result['keywords_to_add']) * 2),
            matched_required=min(
                score_data.get('total_required', 0),
                score_data.get('matched_required_count', 0) + len([k for k in result['keywords_to_add']])
            ),
            total_required=score_data.get('total_required', 0),
            matched_optional=score_data.get('matched_optional_count', 0),
            total_optional=score_data.get('total_optional', 0)
        )
        
        # Format keyword placements
        keyword_placements = [
            KeywordPlacement(
                keyword=placement.get('keyword', ''),
                section=placement.get('suggested_section', 'unknown'),
                suggestion=placement.get('suggestion', ''),
                priority='high' if placement.get('is_required', False) else 'medium'
            )
            for placement in result['keyword_placements'][:10]
        ]
        
        summary = f"Found {len(result['keywords_to_add'])} keywords to add that could improve your score to {estimated_new_score.percentage:.1f}%"
        
        return CVImprovementResponse(
            original_score=original_score,
            keywords_to_add=result['keywords_to_add'][:10],
            keyword_placements=keyword_placements,
            improvement_summary=summary,
            estimated_new_score=estimated_new_score,
            improved_pdf_base64=result.get('improved_pdf_base64')
        )
        
    except Exception as e:
        logger.error(f"Error improving CV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error improving CV: {str(e)}")


@router.post("/match-skills", response_model=SkillMatchingResponse)
async def match_skills(request: SkillMatchingRequest):
    """
    Analyze skill matching between CV and job description.
    
    Extracts and matches technical and soft skills with optional
    normalization for better matching accuracy.
    
    Args:
        request: SkillMatchingRequest with CV and job description content
        
    Returns:
        SkillMatchingResponse with skill matching results
    """
    try:
        result = service.match_skills(
            cv_content=request.cv_content,
            jd_content=request.job_description,
            normalize_skills=request.normalize_skills
        )
        
        # Format CV skills
        cv_skills = [
            SkillData(
                skill=skill,
                normalized_skill=result['normalized_cv_skills'].get(skill) if result['normalized_cv_skills'] else None,
                is_technical=True
            )
            for skill in result['cv_skills'][:20]
        ]
        
        # Format JD skills
        jd_skills = [
            SkillData(
                skill=skill,
                normalized_skill=result['normalized_jd_skills'].get(skill) if result['normalized_jd_skills'] else None,
                is_technical=True
            )
            for skill in result['jd_skills'][:20]
        ]
        
        # Calculate match percentage
        matched_count = len(cv_skills) if result['matched_skills'] else 0
        total_jd_skills = len(jd_skills)
        match_percentage = (matched_count / total_jd_skills * 100) if total_jd_skills > 0 else 0
        
        # Get missing skills
        cv_skill_set = set(result['cv_skills'])
        missing_skills = [s for s in result['jd_skills'] if s not in cv_skill_set]
        
        summary = f"Skill Match: {match_percentage:.1f}%. You have {matched_count}/{total_jd_skills} of the required skills."
        
        return SkillMatchingResponse(
            cv_skills=cv_skills,
            jd_skills=jd_skills,
            matched_skills=result['matched_skills'] if isinstance(result['matched_skills'], list) else [],
            missing_skills=missing_skills[:10],
            skill_match_percentage=match_percentage,
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"Error matching skills: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error matching skills: {str(e)}")


@router.post("/score", response_model=CVScoreResponse)
async def score_cv_route(request: CVScoreRequest):
    """
    Summarizes the job description and scores the CV against it.
    """
    try:
        result = service.score_cv(
            cv_content=request.cv_content,
            job_description=request.job_description,
        )
        return CVScoreResponse(
            jd_summary=result["jd_summary"],
            score=result["score"]
        )
    except Exception as e:
        logger.error(f"Error in /score endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/generate-cover-letter", response_model=CoverLetterResponse)
async def generate_cover_letter(request: CoverLetterRequest):
    """
    Generates a cover letter based on the CV and job description.
    """
    try:
        generator = CoverLetterGenerator()
        result = generator.generate(
            cv_content=request.cv_content,
            job_description=request.job_description,
        )
        return CoverLetterResponse(
            cover_letter_text=result["cover_letter_text"],
            cover_letter_pdf=result["cover_letter_pdf"]
        )
    except Exception as e:
        logger.error(f"Error in /generate-cover-letter endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/render-pdf", response_model=RenderPDFResponse)
async def render_pdf(request: RenderPDFRequest):
    """
    Renders text to PDF.
    """
    try:
        generator = CoverLetterGenerator()
        pdf_base64 = generator._generate_pdf(request.text)
        return RenderPDFResponse(pdf=pdf_base64)
    except Exception as e:
        logger.error(f"Error in /render-pdf endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
