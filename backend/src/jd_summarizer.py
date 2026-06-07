"""
AI Agent for summarizing a job description into key sections.
"""
import os
from typing import Dict, List
import json
from dotenv import load_dotenv

load_dotenv()

class JDSummarizer:
    """AI agent to summarize a job description into tasks and requirements."""

    def __init__(self):
        self.provider = os.getenv('AI_PROVIDER', 'openai').lower()
        self.model = os.getenv('AI_MODEL', 'gpt-4o-mini')
        
        if self.provider == 'openai':
            from openai import OpenAI
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        elif self.provider == 'anthropic':
            from anthropic import Anthropic
            self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

    def summarize(self, job_description: str) -> Dict[str, List[str]]:
        """
        Summarizes the job description into task description and candidate requirements.

        Args:
            job_description: The full text of the job description.

        Returns:
            A dictionary with 'task_description' and 'candidate_requirements'.
        """
        prompt = self._create_prompt(job_description)
        
        if self.provider == 'openai':
            response_text = self._call_openai(prompt)
        else:
            response_text = self._call_anthropic(prompt)
            
        return self._parse_response(response_text)

    def _create_prompt(self, job_description: str) -> str:
        # Truncate for performance
        max_jd_chars = 4000
        if len(job_description) > max_jd_chars:
            job_description = job_description[:max_jd_chars] + "..."

        return f"""
Analyze the following job description and extract the key task descriptions and candidate requirements.
Focus on actionable responsibilities and essential qualifications.

Job Description:
---
{job_description}
---

Extract the information into a JSON object with two keys:
1. "task_description": A list of strings, where each string is a primary task or responsibility.
2. "candidate_requirements": A list of strings, where each string is a required skill, qualification, or experience.

Example JSON output:
{{
  "task_description": [
    "Develop and maintain web applications using React and Node.js.",
    "Collaborate with cross-functional teams to define and ship new features."
  ],
  "candidate_requirements": [
    "3+ years of experience in software development.",
    "Proficiency in JavaScript, HTML, and CSS.",
    "Bachelor's degree in Computer Science or related field."
  ]
}}

Provide only the JSON object in your response.
"""

    def _call_openai(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a job description analyst. Your output is only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content

    def _call_anthropic(self, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
        
    def _parse_response(self, response_text: str) -> Dict[str, List[str]]:
        try:
            # Handle potential markdown code blocks from LLM
            json_str = response_text.strip().replace('```json', '').replace('```', '').strip()
            data = json.loads(json_str)
            return {
                "task_description": data.get("task_description", []),
                "candidate_requirements": data.get("candidate_requirements", [])
            }
        except (json.JSONDecodeError, AttributeError):
            # Fallback for non-JSON or malformed responses
            return {
                "task_description": [],
                "candidate_requirements": []
            }

