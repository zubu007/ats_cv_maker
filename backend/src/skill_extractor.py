"""
Skill Extractor Agent
Uses LLM to intelligently extract and structure skills from text.
"""

import os
import re
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

load_dotenv()


class SkillList(BaseModel):
    """Structured list of skills extracted from text."""
    skills: List[str] = Field(
        description="List of professional skills, technologies, tools, and competencies extracted from the text"
    )
    skill_categories: dict = Field(
        default_factory=dict,
        description="Optional categorization of skills (e.g., 'programming_languages', 'frameworks', 'tools')"
    )


class JDTargetExtraction(BaseModel):
    """Structured job target data extracted from a job description."""

    company_name: str = Field(default="", description="Company name if explicitly found in JD text")
    position: str = Field(default="", description="Job title/position if explicitly found in JD text")
    skills: List[str] = Field(default_factory=list, description="Concise hard-skill keywords for CV skills section")


class SkillExtractor:
    """Extracts skills from CV or job description text using LLM."""
    
    def __init__(self):
        """Initialize the skill extractor."""
        self.provider = os.getenv('AI_PROVIDER', 'openai').lower()
        self.model_name = os.getenv('AI_MODEL', 'gpt-4-turbo')
        
        if self.provider == 'openai':
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=0.2,
                api_key=os.getenv('OPENAI_API_KEY')
            )
        elif self.provider == 'anthropic':
            self.llm = ChatAnthropic(
                model=self.model_name,
                temperature=0.2,
                api_key=os.getenv('ANTHROPIC_API_KEY')
            )
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")
        
        # Create structured output parsers
        self.structured_llm = self.llm.with_structured_output(SkillList)
        self.jd_target_structured_llm = self.llm.with_structured_output(JDTargetExtraction)

    @staticmethod
    def _sanitize_for_cv_skills(raw_skills: List[str], max_words: int = 3) -> List[str]:
        """
        Keep only concise, CV-skills-friendly values.
        Removes perks/benefits, generic employment conditions, and long phrases.
        """
        blocked_terms = {
            "flexible working",
            "working hours",
            "hybrid",
            "remote",
            "on-site",
            "onsite",
            "benefit",
            "wellpass",
            "company event",
            "visa",
            "sponsorship",
            "salary",
            "compensation",
            "culture",
            "english proficiency",
            "language proficiency",
            "collaboration",
            "team player",
            "communication",
            "physical hardware",
            "full-stack development",
            "software development",
            "infrastructure management",
            "clean code",
        }

        def canonicalize(skill: str) -> str:
            lowered = skill.lower()
            if "ci/cd" in lowered:
                return "CI/CD"
            if "github action" in lowered:
                return "GitHub Actions"
            if "version control" in lowered:
                return "Version Control"
            if "linux" in lowered and ("system" in lowered or "infrastructure" in lowered):
                return "Linux"
            return skill

        cleaned_skills: list[str] = []
        seen: set[str] = set()

        for skill in raw_skills:
            cleaned = re.sub(r"\s+", " ", str(skill or "").strip(" -•,.;")).strip()
            if not cleaned:
                continue

            cleaned = canonicalize(cleaned)

            if len(cleaned.split()) > max_words:
                continue

            lowered = cleaned.lower()
            if any(term in lowered for term in blocked_terms):
                continue

            normalized_key = re.sub(r"[^a-z0-9]+", "", lowered)
            if not normalized_key or normalized_key in seen:
                continue

            seen.add(normalized_key)
            cleaned_skills.append(cleaned)

        return cleaned_skills
    
    def extract_skills_from_cv(self, cv_text: str) -> SkillList:
        """
        Extract skills from CV text.
        
        Args:
            cv_text: Full CV text
            
        Returns:
            SkillList with extracted skills
        """
        # Truncate CV text if too long
        max_chars = 8000
        if len(cv_text) > max_chars:
            cv_text = cv_text[:max_chars] + "..."
        
        prompt = f"""Extract ALL skills from this CV: programming languages, frameworks, tools, databases, methodologies, soft skills.

CV:
{cv_text}

Be comprehensive, no duplicates."""
        
        try:
            result = self.structured_llm.invoke(prompt)
            return result
        except Exception as e:
            raise Exception(f"Error extracting skills from CV: {str(e)}")
    
    def extract_skills_from_job_description(self, jd_text: str) -> SkillList:
        """
        Extract skills from job description text.
        
        Args:
            jd_text: Job description text
            
        Returns:
            SkillList with extracted skills
        """
        # Truncate job description if too long
        max_chars = 6000
        if len(jd_text) > max_chars:
            jd_text = jd_text[:max_chars] + "..."
        
        prompt = f"""Extract ALL skills and requirements from this job description: required & preferred skills, technologies, tools, methodologies, soft skills.

Job Description:
{jd_text}

Be comprehensive, no duplicates."""
        
        try:
            result = self.structured_llm.invoke(prompt)
            return result
        except Exception as e:
            raise Exception(f"Error extracting skills from job description: {str(e)}")

    def extract_target_cv_skills_from_job_description(self, jd_text: str) -> SkillList:
        """
        Extract only concise skill keywords suitable for a CV skills section.
        """
        extraction = self.extract_target_cv_data_from_job_description(jd_text)
        return SkillList(skills=extraction.skills, skill_categories={})

    def extract_target_cv_data_from_job_description(self, jd_text: str) -> JDTargetExtraction:
        """
        Extract company, position, and concise skill keywords for CV enhancement flow.
        """
        max_chars = 6000
        if len(jd_text) > max_chars:
            jd_text = jd_text[:max_chars] + "..."

        prompt = f"""Extract structured data for CV tailoring from this job description.

INCLUDE ONLY:
- Technologies, tools, frameworks, languages, databases, platforms, protocols, methodologies
- Explicit hard skills (not duties/benefits)

EXCLUDE:
- Benefits/perks (salary, hybrid/remote policy, wellpass, company events, flexible hours)
- Responsibilities, company culture, role descriptions
- Generic traits and language proficiency

OUTPUT RULES:
- Return:
  1) company_name (empty if not explicitly stated)
  2) position (empty if not explicitly stated)
  3) skills list
- Each skill must be 1 to 3 words
- Use concise canonical skill names (e.g., Python, GitHub Actions, CI/CD)
- No extra explanations

Job Description:
{jd_text}
"""

        try:
            result = self.jd_target_structured_llm.invoke(prompt)
            sanitized = self._sanitize_for_cv_skills(result.skills)
            return JDTargetExtraction(
                company_name=str(result.company_name or "").strip(),
                position=str(result.position or "").strip(),
                skills=sanitized,
            )
        except Exception as e:
            raise Exception(f"Error extracting CV-target data from job description: {str(e)}")
    
    @staticmethod
    def generate_skills_report(skills_list: SkillList, title: str = "Skills Report") -> str:
        """
        Generate a formatted report of extracted skills.
        
        Args:
            skills_list: SkillList object
            title: Report title
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 60)
        report.append(f"📋 {title}")
        report.append("=" * 60)
        report.append("")
        
        report.append(f"Total Skills Found: {len(skills_list.skills)}")
        report.append("")
        
        report.append("Skills:")
        for i, skill in enumerate(skills_list.skills, 1):
            report.append(f"  {i}. {skill}")
        
        if skills_list.skill_categories:
            report.append("")
            report.append("Categorized Skills:")
            for category, category_skills in skills_list.skill_categories.items():
                report.append(f"  {category}:")
                for skill in category_skills:
                    report.append(f"    • {skill}")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)


if __name__ == '__main__':
    # Test the skill extractor
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python skill_extractor.py <cv_file>")
        sys.exit(1)
    
    from .cv_extractor import CVExtractor
    
    cv_file = sys.argv[1]
    extractor = CVExtractor()
    cv_text = extractor.extract(cv_file)
    
    print("🔍 Extracting skills from CV...")
    skill_extractor = SkillExtractor()
    skills = skill_extractor.extract_skills_from_cv(cv_text)
    
    print(skill_extractor.generate_skills_report(skills, "CV Skills"))
    print(f"\nExtracted {len(skills.skills)} unique skills")
