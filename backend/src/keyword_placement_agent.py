"""
Keyword Placement Agent
Uses LangChain structured outputs to intelligently place missing keywords into CV sections.
"""

import os
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from .cv_section_parser import CVSections

load_dotenv()


class ImprovedCVSections(BaseModel):
    """Improved CV sections with keywords added."""
    personal_info: str = Field(description="Name, contact information - typically unchanged")
    professional_summary: str = Field(description="Enhanced professional summary with relevant keywords naturally integrated")
    skills: str = Field(description="Skills section with missing keywords added appropriately")
    work_experience: str = Field(description="Work experience with keywords integrated into relevant job descriptions")
    education: str = Field(description="Education section, potentially enhanced with relevant coursework or certifications")
    projects: str = Field(description="Projects section with keywords added to project descriptions if appropriate")
    certifications: str = Field(description="Certifications section with any relevant additions")
    additional: str = Field(description="Additional sections with keywords if appropriate")
    placement_notes: str = Field(description="Brief notes on where and how keywords were added")


class KeywordPlacementAgent:
    """AI agent that intelligently places missing keywords into appropriate CV sections."""
    
    def __init__(self):
        """Initialize the keyword placement agent."""
        self.provider = os.getenv('AI_PROVIDER', 'openai').lower()
        self.model_name = os.getenv('AI_MODEL', 'gpt-4-turbo')
        
        if self.provider == 'openai':
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=0.3,  # Slightly higher for creative placement
                api_key=os.getenv('OPENAI_API_KEY')
            )
        elif self.provider == 'anthropic':
            self.llm = ChatAnthropic(
                model=self.model_name,
                temperature=0.3,
                api_key=os.getenv('ANTHROPIC_API_KEY')
            )
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")
        
        # Create structured output parser
        self.structured_llm = self.llm.with_structured_output(ImprovedCVSections)
    
    def improve_cv_with_keywords(
        self,
        sections: CVSections,
        keywords_to_add: List[str],
        job_description: str = ""
    ) -> ImprovedCVSections:
        """
        Improve CV by intelligently adding missing keywords to appropriate sections.
        
        Args:
            sections: Original CV sections
            keywords_to_add: List of keywords to add
            job_description: Optional job description for context
            
        Returns:
            ImprovedCVSections with keywords added
        """
        # Truncate sections to prevent token overflow
        def truncate(text: str, max_chars: int = 2000) -> str:
            if len(text) > max_chars:
                return text[:max_chars] + "..."
            return text
        
        keywords_str = ", ".join(keywords_to_add[:15])  # Limit to 15 keywords
        
        # Truncate job description context
        jd_snippet = ""
        if job_description:
            jd_snippet = f"\nJob: {truncate(job_description, 500)}"
        
        prompt = f"""Add these keywords naturally to the CV sections. Keep original content, only enhance.

Keywords to add: {keywords_str}{jd_snippet}

SECTIONS (keep formatting):

Personal: {truncate(sections.personal_info, 500)}

Summary: {truncate(sections.professional_summary, 1000)}

Skills: {truncate(sections.skills, 1500)}

Experience: {truncate(sections.work_experience, 3000)}

Education: {truncate(sections.education, 1000)}

Projects: {truncate(sections.projects or "", 1000)}

Certs: {truncate(sections.certifications or "", 500)}

Other: {truncate(sections.additional or "", 500)}

RULES:
- Add keywords naturally to Skills, Summary, or Experience
- Don't fabricate experience
- Keep original content intact
- Note where you added keywords in placement_notes"""
        
        try:
            result = self.structured_llm.invoke(prompt)
            return result
        except Exception as e:
            raise Exception(f"Error improving CV: {str(e)}")
    
    def save_improved_sections(
        self,
        improved_sections: ImprovedCVSections,
        output_dir: str = "improved_cv_sections"
    ) -> dict:
        """
        Save improved sections to files.
        
        Args:
            improved_sections: Improved CV sections
            output_dir: Directory to save improved sections
            
        Returns:
            Dictionary of saved file paths
        """
        import os
        import json
        
        os.makedirs(output_dir, exist_ok=True)
        
        saved_files = {}
        
        # Save each section
        section_mapping = {
            'personal_info': 'personal_info.txt',
            'professional_summary': 'professional_summary.txt',
            'skills': 'skills.txt',
            'work_experience': 'work_experience.txt',
            'education': 'education.txt',
            'projects': 'projects.txt',
            'certifications': 'certifications.txt',
            'additional': 'additional.txt',
            'placement_notes': 'placement_notes.txt'
        }
        
        for field_name, filename in section_mapping.items():
            content = getattr(improved_sections, field_name, "")
            if content:
                filepath = os.path.join(output_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                saved_files[field_name] = filepath
        
        # Save as JSON
        json_path = os.path.join(output_dir, 'improved_sections.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(improved_sections.model_dump(), f, indent=2)
        saved_files['json'] = json_path
        
        return saved_files


if __name__ == '__main__':
    # Test the placement agent
    import sys
    import json
    
    if len(sys.argv) < 3:
        print("Usage: python keyword_placement_agent.py <sections_json> <keywords_file>")
        sys.exit(1)
    
    # Load sections
    with open(sys.argv[1], 'r') as f:
        sections_data = json.load(f)
    sections = CVSections(**sections_data)
    
    # Load keywords
    with open(sys.argv[2], 'r') as f:
        keywords = [line.strip() for line in f if line.strip()]
    
    print(f"🔍 Improving CV with {len(keywords)} keywords...")
    
    agent = KeywordPlacementAgent()
    improved = agent.improve_cv_with_keywords(sections, keywords)
    
    print("\n💾 Saving improved sections...")
    saved_files = agent.save_improved_sections(improved)
    
    print("\n✅ Improved CV sections saved:")
    for section, filepath in saved_files.items():
        print(f"  • {section}: {filepath}")
    
    print(f"\n📝 Placement Notes:\n{improved.placement_notes}")
