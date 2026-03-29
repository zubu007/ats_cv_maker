"""
CV Section Parser Agent
Parses CV text into structured sections using AI.
"""

import os
import json
from typing import Dict, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

load_dotenv()


class CVSections(BaseModel):
    """Structured CV sections."""
    personal_info: str = Field(description="Name, contact information, email, phone, location")
    professional_summary: str = Field(default="", description="Professional summary or objective statement")
    skills: str = Field(default="", description="Technical skills, programming languages, tools, technologies")
    work_experience: str = Field(description="Work experience, job history, professional experience")
    education: str = Field(description="Education, degrees, certifications, academic background")
    projects: str = Field(default="", description="Personal or professional projects")
    certifications: str = Field(default="", description="Professional certifications and licenses")
    additional: str = Field(default="", description="Any additional sections like awards, publications, volunteer work")


class CVSectionParser:
    """Parses CV text into structured sections using LangChain."""
    
    def __init__(self):
        """Initialize the CV section parser."""
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
        
        # Create structured output parser
        self.structured_llm = self.llm.with_structured_output(CVSections)
    
    def parse_cv(self, cv_text: str) -> CVSections:
        """
        Parse CV text into structured sections.
        
        Args:
            cv_text: Full CV text
            
        Returns:
            CVSections object with parsed sections
        """
        # Truncate CV text if too long (keep first 15000 chars ~3750 tokens)
        max_chars = 15000
        if len(cv_text) > max_chars:
            cv_text = cv_text[:max_chars] + "\n...[CV truncated for processing]"
        
        prompt = f"""Extract this CV into sections. Keep text AS-IS, don't modify.

CV:
{cv_text}

Sections: personal_info, professional_summary, skills, work_experience, education, projects, certifications, additional."""
        
        try:
            result = self.structured_llm.invoke(prompt)
            return result
        except Exception as e:
            raise Exception(f"Error parsing CV: {str(e)}")
    
    def save_sections(self, sections: CVSections, output_dir: str = "cv_sections") -> Dict[str, str]:
        """
        Save each section to a separate file.
        
        Args:
            sections: CVSections object
            output_dir: Directory to save sections
            
        Returns:
            Dictionary mapping section names to file paths
        """
        import os
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
            'additional': 'additional.txt'
        }
        
        for field_name, filename in section_mapping.items():
            content = getattr(sections, field_name, "")
            if content:  # Only save non-empty sections
                filepath = os.path.join(output_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                saved_files[field_name] = filepath
        
        # Also save as JSON
        json_path = os.path.join(output_dir, 'sections.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(sections.model_dump(), f, indent=2)
        saved_files['json'] = json_path
        
        return saved_files
    
    def load_sections(self, section_dir: str = "cv_sections") -> CVSections:
        """
        Load sections from saved files.
        
        Args:
            section_dir: Directory containing saved sections
            
        Returns:
            CVSections object
        """
        json_path = os.path.join(section_dir, 'sections.json')
        
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return CVSections(**data)
        else:
            raise FileNotFoundError(f"Sections file not found: {json_path}")


if __name__ == '__main__':
    # Test the parser
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python cv_section_parser.py <cv_file>")
        sys.exit(1)
    
    from .cv_extractor import CVExtractor
    
    # Extract CV text
    cv_file = sys.argv[1]
    extractor = CVExtractor()
    cv_text = extractor.extract(cv_file)
    
    # Parse sections
    print("🔍 Parsing CV sections...")
    parser = CVSectionParser()
    sections = parser.parse_cv(cv_text)
    
    # Save sections
    print("💾 Saving sections...")
    saved_files = parser.save_sections(sections)
    
    print("\n✅ Sections extracted and saved:")
    for section, filepath in saved_files.items():
        if section != 'json':
            print(f"  • {section}: {filepath}")
    print(f"  • Full JSON: {saved_files['json']}")
