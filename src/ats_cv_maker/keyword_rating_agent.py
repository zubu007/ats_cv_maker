"""
AI Agent for rating keywords as required or optional.
Uses LLM (OpenAI or Anthropic) to intelligently categorize keywords.
"""

import os
import json
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class KeywordRatingAgent:
    """AI agent that rates keywords as required or optional based on job description."""
    
    def __init__(self):
        """Initialize the keyword rating agent."""
        self.provider = os.getenv('AI_PROVIDER', 'openai').lower()
        self.model = os.getenv('AI_MODEL', 'gpt-4')
        
        if self.provider == 'openai':
            self._init_openai()
        elif self.provider == 'anthropic':
            self._init_anthropic()
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}. Use 'openai' or 'anthropic'")
    
    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
    
    def _init_anthropic(self):
        """Initialize Anthropic client."""
        try:
            from anthropic import Anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
            self.client = Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("Anthropic package not installed. Run: pip install anthropic")
    
    def rate_keywords(self, keywords: List[str], job_description: str) -> Dict[str, List[str]]:
        """
        Rate keywords as required or optional based on job description.
        
        Args:
            keywords: List of keywords extracted from job description
            job_description: Full job description text
            
        Returns:
            Dictionary with 'required' and 'optional' keyword lists
        """
        prompt = self._create_prompt(keywords, job_description)
        
        if self.provider == 'openai':
            response = self._call_openai(prompt)
        else:
            response = self._call_anthropic(prompt)
        
        return self._parse_response(response, keywords)
    
    def _create_prompt(self, keywords: List[str], job_description: str) -> str:
        """
        Create prompt for the LLM.
        
        Args:
            keywords: List of keywords to rate
            job_description: Job description text
            
        Returns:
            Formatted prompt string
        """
        keywords_str = "\n".join([f"- {kw}" for kw in keywords])
        
        prompt = f"""You are an expert ATS (Applicant Tracking System) analyst. Your task is to categorize keywords from a job description into two categories: REQUIRED and OPTIONAL.

REQUIRED keywords are:
- Skills, technologies, or qualifications explicitly marked as "required", "must have", "essential"
- Core competencies central to the role
- Years of experience if specifically mentioned as mandatory
- Critical certifications or degrees

OPTIONAL keywords are:
- Skills marked as "preferred", "nice to have", "bonus"
- Secondary skills or "plus" qualifications
- General industry terms not specifically emphasized

Job Description:
{job_description}

Keywords to categorize:
{keywords_str}

Respond ONLY with a JSON object in this exact format:
{{
  "required": ["keyword1", "keyword2"],
  "optional": ["keyword3", "keyword4"]
}}

Make sure every keyword from the list is categorized into either required or optional."""
        
        return prompt
    
    def _call_openai(self, prompt: str) -> str:
        """
        Call OpenAI API.
        
        Args:
            prompt: The prompt to send
            
        Returns:
            Response text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert ATS analyst. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error calling OpenAI API: {str(e)}")
    
    def _call_anthropic(self, prompt: str) -> str:
        """
        Call Anthropic API.
        
        Args:
            prompt: The prompt to send
            
        Returns:
            Response text
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Error calling Anthropic API: {str(e)}")
    
    def _parse_response(self, response: str, original_keywords: List[str]) -> Dict[str, List[str]]:
        """
        Parse LLM response into structured format.
        
        Args:
            response: Raw response from LLM
            original_keywords: Original keyword list for fallback
            
        Returns:
            Dictionary with required and optional keywords
        """
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                
                # Validate structure
                if 'required' in result and 'optional' in result:
                    return {
                        'required': result['required'],
                        'optional': result['optional']
                    }
        except json.JSONDecodeError:
            pass
        
        # Fallback: treat all keywords as required if parsing fails
        print("Warning: Could not parse LLM response. Treating all keywords as required.")
        return {
            'required': original_keywords,
            'optional': []
        }
