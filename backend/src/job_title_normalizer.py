"""
Job Title Normalizer Agent
Normalizes job titles to standard forms for comparison.
"""

import os
import re
from typing import List, Dict
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

load_dotenv()


class NormalizedTitle(BaseModel):
    """Normalized job title."""
    original_title: str = Field(description="Original job title")
    normalized_title: str = Field(description="Standardized job title (e.g., 'Software Engineer')")
    seniority_level: str = Field(
        description="Seniority level: 'Junior', 'Mid', 'Senior', or 'Lead'",
        default="Mid"
    )


class JobTitleNormalizer:
    """Normalizes job titles to standard forms using AI."""
    
    def __init__(self):
        """Initialize the job title normalizer."""
        self.provider = os.getenv('AI_PROVIDER', 'openai').lower()
        self.model_name = os.getenv('AI_MODEL', 'gpt-4-turbo')
        
        if self.provider == 'openai':
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=0.1,
                api_key=os.getenv('OPENAI_API_KEY')
            )
        elif self.provider == 'anthropic':
            self.llm = ChatAnthropic(
                model=self.model_name,
                temperature=0.1,
                api_key=os.getenv('ANTHROPIC_API_KEY')
            )
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")
    
    def normalize_title(self, job_title: str) -> NormalizedTitle:
        """
        Normalize a single job title.
        
        Args:
            job_title: Original job title
            
        Returns:
            NormalizedTitle with normalized title and seniority level
        """
        prompt = f"""You are an expert at normalizing job titles. Analyze the following job title and:
1. Extract the core role/title (e.g., 'Software Engineer', 'Product Manager', 'Data Scientist')
2. Determine the seniority level: 'Junior', 'Mid', 'Senior', or 'Lead'

Examples:
- "Junior Software Developer" → normalized: "Software Engineer", seniority: "Junior"
- "SWE II" → normalized: "Software Engineer", seniority: "Mid"
- "Senior Backend Engineer" → normalized: "Backend Engineer", seniority: "Senior"
- "Engineering Lead" → normalized: "Software Engineer", seniority: "Lead"
- "Staff Engineer" → normalized: "Software Engineer", seniority: "Lead"

Job Title: {job_title}

Provide the normalized title and seniority level."""

        response = self.llm.invoke(prompt)
        
        # Extract normalized title and seniority from response
        text = response.content.lower()
        
        # Parse response to extract normalized title and seniority
        normalized_title = self._extract_normalized_title(job_title, text)
        seniority_level = self._extract_seniority_level(text)
        
        return NormalizedTitle(
            original_title=job_title,
            normalized_title=normalized_title,
            seniority_level=seniority_level
        )
    
    def normalize_titles(self, job_titles: List[str]) -> List[NormalizedTitle]:
        """
        Normalize multiple job titles.
        
        Args:
            job_titles: List of original job titles
            
        Returns:
            List of NormalizedTitle objects
        """
        return [self.normalize_title(title) for title in job_titles]
    
    @staticmethod
    def _extract_normalized_title(original: str, response_text: str) -> str:
        """
        Extract normalized title from response text.
        
        Args:
            original: Original job title
            response_text: Response text from LLM
            
        Returns:
            Normalized job title
        """
        # Try to find common engineering roles
        engineering_roles = [
            'software engineer', 'backend engineer', 'frontend engineer', 'full stack engineer',
            'product manager', 'data scientist', 'data engineer', 'devops engineer',
            'systems engineer', 'qa engineer', 'solutions architect', 'security engineer',
            'machine learning engineer', 'platform engineer', 'infrastructure engineer',
            'cloud engineer', 'database administrator', 'business analyst', 'project manager',
            'technical lead', 'engineering manager'
        ]
        
        # Check if any role is mentioned in response
        for role in engineering_roles:
            if role in response_text:
                return role.title()
        
        # Fallback: clean up original title
        return JobTitleNormalizer._simple_normalize(original)
    
    @staticmethod
    def _extract_seniority_level(response_text: str) -> str:
        """
        Extract seniority level from response text.
        
        Args:
            response_text: Response text from LLM
            
        Returns:
            Seniority level: 'Junior', 'Mid', 'Senior', or 'Lead'
        """
        if any(word in response_text for word in ['lead', 'staff', 'principal', 'director']):
            return 'Lead'
        elif any(word in response_text for word in ['senior', 'sr', 'sr.']):
            return 'Senior'
        elif any(word in response_text for word in ['junior', 'jr', 'jr.', 'entry']):
            return 'Junior'
        else:
            return 'Mid'
    
    @staticmethod
    def _simple_normalize(job_title: str) -> str:
        """
        Simple normalization without AI (fallback).
        
        Args:
            job_title: Original job title
            
        Returns:
            Normalized job title
        """
        # Remove seniority markers
        title = job_title.lower()
        
        # Remove level indicators
        title = re.sub(r'\b(junior|jr|jr\.|senior|sr|sr\.|lead|staff|principal|i|ii|iii|iv|v|1|2|3|4|5)\b', '', title)
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Capitalize first letter of each word
        return title.title()
    
    def calculate_title_similarity(self, title1: str, title2: str) -> float:
        """
        Calculate similarity between two job titles (0-1).
        
        Args:
            title1: First job title
            title2: Second job title
            
        Returns:
            Similarity score (0-1)
        """
        from difflib import SequenceMatcher
        
        # Normalize both titles
        norm1 = self._simple_normalize(title1).lower()
        norm2 = self._simple_normalize(title2).lower()
        
        # Calculate sequence similarity
        similarity = SequenceMatcher(None, norm1, norm2).ratio()
        
        return similarity
