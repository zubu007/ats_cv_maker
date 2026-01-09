"""
API Request and Response Models
Pydantic models for type validation and documentation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class CVAnalysisRequest(BaseModel):
    """Request model for CV analysis endpoint"""
    cv_content: str = Field(..., description="CV content as text")
    job_description: str = Field(..., description="Job description content as text")
    use_spacy: bool = Field(True, description="Enable spaCy NLP processing")
    include_skills: bool = Field(True, description="Include skill matching analysis")
    include_experience: bool = Field(True, description="Include experience relevance analysis")
    max_keywords: int = Field(50, description="Maximum keywords to extract")


class KeywordData(BaseModel):
    """Model for keyword information"""
    keyword: str
    frequency: int
    relevance_score: float


class RatedKeywords(BaseModel):
    """Model for rated keywords"""
    required: List[str]
    optional: List[str]


class AtsScoreResponse(BaseModel):
    """Response model for ATS score"""
    score: float
    percentage: float
    matched_required: int
    total_required: int
    matched_optional: int
    total_optional: int


class SkillData(BaseModel):
    """Model for skill information"""
    skill: str
    normalized_skill: Optional[str] = None
    is_technical: bool


class ExperienceRelevanceScore(BaseModel):
    """Model for experience relevance scoring"""
    experience_relevance_score: float
    experience_count: int
    relevant_experiences: List[str]


class CVAnalysisResponse(BaseModel):
    """Complete response model for CV analysis"""
    cv_keywords: List[KeywordData]
    jd_keywords: List[KeywordData]
    rated_keywords: RatedKeywords
    ats_score: AtsScoreResponse
    skill_score: Optional[Dict[str, Any]] = None
    experience_score: Optional[ExperienceRelevanceScore] = None
    analysis_summary: str


class CVImprovementRequest(BaseModel):
    """Request model for CV improvement endpoint"""
    cv_content: str = Field(..., description="CV content as text")
    job_description: str = Field(..., description="Job description content as text")
    max_keywords_to_add: int = Field(10, description="Maximum keywords to add")
    use_spacy: bool = Field(True, description="Enable spaCy NLP processing")
    include_experience: bool = Field(True, description="Include experience relevance analysis")


class KeywordPlacement(BaseModel):
    """Model for keyword placement suggestion"""
    keyword: str
    section: str
    suggestion: str
    priority: str


class CVImprovementResponse(BaseModel):
    """Response model for CV improvement"""
    original_score: AtsScoreResponse
    keywords_to_add: List[str]
    keyword_placements: List[KeywordPlacement]
    improvement_summary: str
    estimated_new_score: AtsScoreResponse


class SkillMatchingRequest(BaseModel):
    """Request model for skill matching endpoint"""
    cv_content: str = Field(..., description="CV content as text")
    job_description: str = Field(..., description="Job description content as text")
    normalize_skills: bool = Field(True, description="Normalize skills")


class SkillMatchingResponse(BaseModel):
    """Response model for skill matching"""
    cv_skills: List[SkillData]
    jd_skills: List[SkillData]
    matched_skills: List[Dict[str, Any]]
    missing_skills: List[str]
    skill_match_percentage: float
    summary: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    api_ready: bool
