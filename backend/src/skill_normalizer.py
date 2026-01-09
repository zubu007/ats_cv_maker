"""
Skill Normalizer Agent
Uses LLM to intelligently normalize and categorize skills.
"""

import os
from typing import List, Dict, Set
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

load_dotenv()


class NormalizedSkill(BaseModel):
    """Represents a normalized skill."""
    original_skill: str = Field(description="Original skill name from the source")
    normalized_name: str = Field(description="Normalized/standardized skill name")
    category: str = Field(description="Skill category (e.g., 'Programming Language', 'Framework', 'Tool')")
    should_normalize: bool = Field(
        description="Whether this skill should be normalized or kept as-is"
    )
    reasoning: str = Field(
        description="Brief explanation of why this skill was normalized or not"
    )


class NormalizedSkillList(BaseModel):
    """Structured list of normalized skills."""
    normalized_skills: List[NormalizedSkill] = Field(
        description="List of skills with normalization decisions"
    )


class SkillNormalizer:
    """Normalizes and standardizes skill names using LLM intelligence."""
    
    def __init__(self):
        """Initialize the skill normalizer."""
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
        self.structured_llm = self.llm.with_structured_output(NormalizedSkillList)
    
    def normalize_skills(self, skills: List[str], context: str = "general") -> NormalizedSkillList:
        """
        Normalize and standardize skill names.
        
        Args:
            skills: List of skills to normalize
            context: Context for normalization (e.g., 'cv', 'job_description')
            
        Returns:
            NormalizedSkillList with normalized skills and decisions
        """
        skills_str = "\n".join(f"- {skill}" for skill in skills)
        
        prompt = f"""You are an expert skill standardization and taxonomy specialist. Your task is to intelligently 
normalize and standardize skills while deciding which ones truly benefit from normalization.

IMPORTANT GUIDELINES:
1. ONLY normalize skills when it makes sense (e.g., similar technologies, frameworks, or related tools)
2. Examples of good normalization:
   - "PyTorch" and "TensorFlow" → "Deep Learning Framework" (if both appear)
   - "React", "Vue", "Angular" → "Frontend Framework" (if multiple appear)
   - "Java", "Python", "C++" → Keep as-is (NO normalization for languages)
   - "AWS", "Azure", "GCP" → "Cloud Platform" (if multiple appear)
3. DO NOT normalize unique or distinctive skills
4. DO NOT normalize programming languages (keep Java, Python, C++ as-is)
5. DO NOT normalize well-known brand names unless there are many similar competitors
6. Ask yourself: "Does normalizing this skill help match with job requirements?"
7. For each skill, decide: normalize or keep as-is based on presence of similar alternatives

Skills to normalize:
{skills_str}

For each skill:
1. Analyze if there are similar alternatives in the list
2. Decide whether normalization is beneficial (yes/no)
3. If normalizing, provide a meaningful normalized name
4. Categorize each skill
5. Provide brief reasoning

Context: {context}

Normalize these skills intelligently. Remember: normalize only when it truly helps with skill matching."""
        
        try:
            result = self.structured_llm.invoke(prompt)
            return result
        except Exception as e:
            raise Exception(f"Error normalizing skills: {str(e)}")
    
    @staticmethod
    def merge_skills(
        original_skills: List[str],
        normalized_skills: NormalizedSkillList
    ) -> tuple[List[str], Dict[str, str]]:
        """
        Merge original and normalized skills.
        
        Args:
            original_skills: Original list of skills
            normalized_skills: NormalizedSkillList from normalizer
            
        Returns:
            Tuple of (merged_skills_list, skill_mappings)
        """
        # Track which normalized skills we've added to avoid duplicates
        merged_skills = set(original_skills)
        skill_mappings = {}  # original -> normalized mapping
        
        for norm_skill in normalized_skills.normalized_skills:
            if norm_skill.should_normalize:
                # Add the normalized skill to the set
                merged_skills.add(norm_skill.normalized_name)
                # Track the mapping
                skill_mappings[norm_skill.original_skill] = norm_skill.normalized_name
            else:
                # Keep original skill as-is (it's already in merged_skills)
                skill_mappings[norm_skill.original_skill] = norm_skill.original_skill
        
        return sorted(list(merged_skills)), skill_mappings
    
    @staticmethod
    def generate_normalization_report(
        normalized_skills: NormalizedSkillList,
        original_count: int
    ) -> str:
        """
        Generate a report of normalization decisions.
        
        Args:
            normalized_skills: NormalizedSkillList from normalizer
            original_count: Original count of skills
            
        Returns:
            Formatted report string
        """
        normalized_count = sum(
            1 for s in normalized_skills.normalized_skills if s.should_normalize
        )
        
        report = []
        report.append("=" * 80)
        report.append("📊 Skill Normalization Report")
        report.append("=" * 80)
        report.append(f"\nOriginal Skills: {original_count}")
        report.append(f"Normalized: {normalized_count}")
        report.append(f"Kept As-Is: {original_count - normalized_count}")
        report.append(f"New Merged List Size: {original_count + (normalized_count)}")  # Max possible with new normalized skills
        report.append("\n" + "-" * 80)
        report.append("Normalization Details:")
        report.append("-" * 80)
        
        for norm_skill in normalized_skills.normalized_skills:
            status = "✓ NORMALIZED" if norm_skill.should_normalize else "- KEPT"
            report.append(f"\n{status}")
            report.append(f"  Original: {norm_skill.original_skill}")
            if norm_skill.should_normalize:
                report.append(f"  → Normalized To: {norm_skill.normalized_name}")
            report.append(f"  Category: {norm_skill.category}")
            report.append(f"  Reasoning: {norm_skill.reasoning}")
        
        report.append("\n" + "=" * 80)
        return "\n".join(report)


if __name__ == '__main__':
    # Test the skill normalizer
    test_skills = [
        "Python",
        "Java",
        "React",
        "Vue.js",
        "Angular",
        "PyTorch",
        "TensorFlow",
        "AWS",
        "Azure",
        "Git",
        "Docker",
        "Kubernetes"
    ]
    
    normalizer = SkillNormalizer()
    print("🔄 Normalizing skills...")
    
    normalized = normalizer.normalize_skills(test_skills, context="job_description")
    print(normalizer.generate_normalization_report(normalized, len(test_skills)))
    
    merged, mappings = normalizer.merge_skills(test_skills, normalized)
    print(f"\n✅ Merged Skills List ({len(merged)} total):")
    for skill in merged:
        print(f"  • {skill}")
