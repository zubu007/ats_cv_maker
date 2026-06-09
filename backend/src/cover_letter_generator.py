"""
AI Agent for generating a cover letter.
"""
import os
from typing import List
from dotenv import load_dotenv
from .keyword_extractor import KeywordExtractor
from .cv_extractor import CVExtractor
from .pdf_generator import PDFGenerator
from .latex_cv_generator import LaTeXCVGenerator
import base64
import tempfile


load_dotenv()

class CoverLetterGenerator:
    """
    AI agent that generates a personalized cover letter based on a CV and job description.
    """

    def __init__(self):
        self.provider = os.getenv('AI_PROVIDER', 'openai').lower()
        self.model = os.getenv('AI_MODEL', 'gpt-4o-mini')
        self.openai_api_key = os.getenv('FAU_API_KEY') or os.getenv('OPENAI_API_KEY')
        self.openai_base_url = os.getenv('OPENAI_BASE_URL', 'https://hub.nhr.fau.de/api/llmgw/v1')
        
        if self.provider == 'openai':
            from openai import OpenAI
            self.client = OpenAI(api_key=self.openai_api_key, base_url=self.openai_base_url)
        elif self.provider == 'anthropic':
            from anthropic import Anthropic
            self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

    def generate(
        self,
        cv_content: str,
        job_description: str,
        company_name: str = "",
        position: str = "",
    ) -> dict:
        """
        Generates a cover letter.

        Args:
            cv_content: The base64 encoded CV content.
            job_description: The job description text.
            company_name: Optional company override from UI.
            position: Optional position/title override from UI.

        Returns:
            A dictionary containing the cover letter text and the PDF as a base64 string.
        """
        cv_extractor = CVExtractor()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_cv:
            temp_cv.write(base64.b64decode(cv_content))
            temp_cv_path = temp_cv.name
        
        cv_text = cv_extractor.extract_from_pdf(temp_cv_path)
        os.remove(temp_cv_path)

        return self.generate_from_text(
            cv_text=cv_text,
            job_description=job_description,
            company_name=company_name,
            position=position,
        )

    def generate_from_text(
        self,
        cv_text: str,
        job_description: str,
        company_name: str = "",
        position: str = "",
    ) -> dict:
        """
        Generates a cover letter from plain CV text and job description.
        """
        cover_letter_text = self._generate_cover_letter_text(
            cv_text=cv_text,
            job_description=job_description,
            company_name=company_name,
            position=position,
        )
        pdf_base64 = self._generate_pdf(cover_letter_text)

        return {
            "cover_letter_text": cover_letter_text,
            "cover_letter_pdf": pdf_base64,
        }

    def _generate_cover_letter_text(
        self,
        cv_text: str,
        job_description: str,
        company_name: str = "",
        position: str = "",
    ) -> str:
        """Generate cover letter text using the configured LLM provider."""

        keyword_extractor = KeywordExtractor(use_spacy=False)
        jd_keywords = keyword_extractor.extract_keywords(job_description, max_keywords=15)

        prompt = self._create_prompt(
            cv_text=cv_text,
            job_description=job_description,
            jd_keywords=jd_keywords,
            company_name=company_name,
            position=position,
        )

        if self.provider == 'openai':
            cover_letter_text = self._call_openai(prompt)
        else:
            cover_letter_text = self._call_anthropic(prompt)

        return cover_letter_text

    def _create_prompt(
        self,
        cv_text: str,
        job_description: str,
        jd_keywords: List[str],
        company_name: str = "",
        position: str = "",
    ) -> str:
        company = str(company_name or "").strip()
        role = str(position or "").strip()
        target_context_lines: list[str] = []
        if company:
            target_context_lines.append(f"- Company Name: {company}")
        if role:
            target_context_lines.append(f"- Position Name: {role}")

        provided_target_context = (
            "\n".join(target_context_lines)
            if target_context_lines
            else "- No explicit company/position overrides provided by the user."
        )

        return f"""
        Based on the following CV and job description, write a complete, professional, and personalized cover letter.

        CRITICAL REQUIREMENTS:
        1. Extract the candidate's ACTUAL NAME, contact information, and details from the CV provided below
        2. Use the REAL information from the CV - DO NOT use placeholders like [Your Name], [Company Name], [Position], etc.
        3. If explicit company/position values are provided below, treat them as the source of truth and use those exact values
        4. If you cannot find specific information in the CV (like hiring manager), simply omit that detail rather than using a placeholder
        5. Write a complete, ready-to-send cover letter with proper salutation and closing
        6. The letter should be enthusiastic and highlight the candidate's most relevant skills and experiences that match the job description
        7. Naturally incorporate the provided keywords throughout the letter
        8. Use a professional but personable tone
        9. Structure: introduction paragraph, 2-3 body paragraphs highlighting relevant experience, and conclusion paragraph
        10. Generate a concise subject line for the cover letter email. E.g. "Application for Software Engineer Position - John Doe"

        User-provided target details:
        {provided_target_context}

        CV Details:
        ---
        {cv_text[:3000]}
        ---

        Job Description:
        ---
        {job_description[:3000]}
        ---

        Keywords to naturally incorporate:
        - {", ".join(jd_keywords)}

        Generate the output in the following format:
        
        Subject: [Write the subject line here]
        
        [Then provide the complete cover letter text with NO placeholders. The letter should be immediately usable without any edits needed.]
        """

    def _call_openai(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional cover letter writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        return response.choices[0].message.content

    def _call_anthropic(self, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters in text."""
        # Backslash must be escaped first to avoid double-escaping
        text = text.replace('\\', r'\textbackslash{}')
        
        # Now escape other special characters
        replacements = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
        }
        
        # Apply replacements
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        return text
    
    def _generate_pdf(self, cover_letter_text: str) -> str:
        """Generates a PDF from the cover letter text."""
        # Escape LaTeX special characters
        escaped_text = self._escape_latex(cover_letter_text)
        
        # Replace newlines: single newline -> space, double newline -> paragraph break
        # Split into paragraphs first
        paragraphs = escaped_text.split('\n\n')
        processed_paragraphs = []
        
        for para in paragraphs:
            # Replace single newlines with spaces within paragraphs
            para = para.replace('\n', ' ')
            # Clean up multiple spaces
            para = ' '.join(para.split())
            if para.strip():  # Only add non-empty paragraphs
                processed_paragraphs.append(para.strip())
        
        # Join paragraphs with double newlines (LaTeX will handle paragraph breaks)
        processed_text = '\n\n'.join(processed_paragraphs)
        
        latex_template = f"""\\documentclass[a4paper,12pt]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{geometry}}
\\usepackage{{parskip}}
\\geometry{{a4paper, margin=1in, top=1in, bottom=1in, left=1in, right=1in}}
\\begin{{document}}
\\sffamily
{processed_text}
\\end{{document}}
"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            tex_path = os.path.join(temp_dir, 'cover_letter.tex')
            with open(tex_path, 'w', encoding='utf-8') as f:
                f.write(latex_template)
            
            pdf_path = PDFGenerator.compile_latex_to_pdf(tex_path, temp_dir)
            
            with open(pdf_path, 'rb') as pdf_file:
                return base64.b64encode(pdf_file.read()).decode('utf-8')
