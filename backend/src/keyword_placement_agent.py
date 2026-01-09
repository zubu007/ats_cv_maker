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
        self.model_name = os.getenv('AI_MODEL', 'gpt-4')
        
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
        keywords_str = "\n".join([f"- {kw}" for kw in keywords_to_add])
        
        jd_context = f"\n\nJob Description Context:\n{job_description}" if job_description else ""
        
        prompt = f"""You are an expert CV writer and ATS optimization specialist. Your task is to naturally integrate missing keywords into a CV to improve its ATS score while maintaining authenticity and readability.

CRITICAL RULES:
1. Add keywords ONLY where they make sense contextually
2. Maintain the original tone and style of the CV
3. Be truthful - don't fabricate experience or skills
4. Integrate keywords naturally into existing content
5. Prefer adding to Skills, Professional Summary, and Work Experience sections
6. For technical skills, add them to the Skills section
7. For soft skills or methodologies, weave into experience descriptions
8. Keep the content honest and verifiable
9. Maintain professional language and formatting
10. Preserve all original contact information exactly

ORIGINAL CV SECTIONS:

Personal Info:
{sections.personal_info}

Professional Summary:
{sections.professional_summary}

Skills:
{sections.skills}

Work Experience:
{sections.work_experience}

Education:
{sections.education}

Projects:
{sections.projects or "N/A"}

Certifications:
{sections.certifications or "N/A"}

Additional:
{sections.additional or "N/A"}

KEYWORDS TO ADD (prioritize these):
{keywords_str}
{jd_context}

PLACEMENT STRATEGIES:
1. **Skills Section**: Add technical skills, tools, technologies directly
2. **Professional Summary**: Incorporate key skills and methodologies naturally
3. **Work Experience**: Add relevant tools/technologies to existing job descriptions
4. **Projects**: Mention technologies used in projects
5. **Education**: Add relevant coursework or specializations if applicable

OUTPUT REQUIREMENTS:
- Return all sections even if unchanged
- Add keywords naturally without being obvious
- Maintain original formatting and structure
- Don't remove any existing content
- Provide placement_notes explaining what was added and where

Improve the CV by adding these keywords appropriately."""
        
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
