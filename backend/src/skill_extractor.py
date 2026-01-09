"""
Skill Extractor Agent
Uses LLM to intelligently extract and structure skills from text.
"""

import os
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


class SkillExtractor:
    """Extracts skills from CV or job description text using LLM."""
    
    def __init__(self):
        """Initialize the skill extractor."""
        self.provider = os.getenv('AI_PROVIDER', 'openai').lower()
        self.model_name = os.getenv('AI_MODEL', 'gpt-4')
        
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
        
        # Create structured output parser
        self.structured_llm = self.llm.with_structured_output(SkillList)
    
    def extract_skills_from_cv(self, cv_text: str) -> SkillList:
        """
        Extract skills from CV text.
        
        Args:
            cv_text: Full CV text
            
        Returns:
            SkillList with extracted skills
        """
        prompt = f"""You are an expert CV analyst. Extract ALL professional skills, technologies, tools, 
programming languages, frameworks, methodologies, and competencies mentioned in this CV.

IMPORTANT:
1. Extract every skill mentioned, including soft skills
2. Include programming languages, frameworks, tools, databases, platforms
3. Include professional methodologies (Agile, Scrum, etc.)
4. Include soft skills (leadership, communication, problem-solving)
5. Be comprehensive - don't filter or limit
6. Keep skill names exactly as written in the CV (preserve original names)
7. No duplicates

CV Text:
{cv_text}

Extract all skills found in this CV."""
        
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
        prompt = f"""You are an expert recruiter. Extract ALL skills, technologies, tools, 
programming languages, frameworks, and requirements mentioned in this job description.

IMPORTANT:
1. Extract every skill requirement mentioned
2. Include both required and preferred skills
3. Include programming languages, frameworks, databases, tools, platforms
4. Include professional methodologies and processes
5. Include soft skills and competencies
6. Be comprehensive - capture all requirements
7. Keep skill names exactly as written in the JD (preserve original names)
8. No duplicates

Job Description:
{jd_text}

Extract all skills and requirements from this job description."""
        
        try:
            result = self.structured_llm.invoke(prompt)
            return result
        except Exception as e:
            raise Exception(f"Error extracting skills from job description: {str(e)}")
    
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
