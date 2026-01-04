"""
LaTeX CV Generator
Generates a professional single-column, 1-page A4 CV in LaTeX format.
"""

from typing import Optional
from src.ats_cv_maker.keyword_placement_agent import ImprovedCVSections


class LaTeXCVGenerator:
    """Generates professional LaTeX CVs."""
    
    @staticmethod
    def generate_latex(sections: ImprovedCVSections, name: str = None) -> str:
        """
        Generate LaTeX code for a professional CV.
        
        Args:
            sections: Improved CV sections
            name: Candidate name (extracted from personal_info if not provided)
            
        Returns:
            LaTeX code as string
        """
        # Extract name from personal info if not provided
        if not name:
            lines = sections.personal_info.strip().split('\n')
            name = lines[0] if lines else "Your Name"
        
        latex_code = r"""\documentclass[11pt,a4paper,sans]{moderncv}

% Modern CV style and color
\moderncvstyle{banking}
\moderncvcolor{blue}

% Character encoding
\usepackage[utf8]{inputenc}

% Adjust page margins
\usepackage[scale=0.85]{geometry}
\setlength{\hintscolumnwidth}{3cm}

% Reduce spacing
\usepackage{enumitem}
\setlist{noitemsep,topsep=2pt,parsep=2pt,partopsep=2pt}

% Personal data
""" + LaTeXCVGenerator._generate_personal_data(sections.personal_info) + r"""

\begin{document}

\makecvtitle

"""
        
        # Add Professional Summary
        if sections.professional_summary:
            latex_code += LaTeXCVGenerator._generate_summary_section(sections.professional_summary)
        
        # Add Skills
        if sections.skills:
            latex_code += LaTeXCVGenerator._generate_skills_section(sections.skills)
        
        # Add Work Experience
        if sections.work_experience:
            latex_code += LaTeXCVGenerator._generate_experience_section(sections.work_experience)
        
        # Add Education
        if sections.education:
            latex_code += LaTeXCVGenerator._generate_education_section(sections.education)
        
        # Add Projects
        if sections.projects:
            latex_code += LaTeXCVGenerator._generate_projects_section(sections.projects)
        
        # Add Certifications
        if sections.certifications:
            latex_code += LaTeXCVGenerator._generate_certifications_section(sections.certifications)
        
        latex_code += r"""
\end{document}
"""
        
        return latex_code
    
    @staticmethod
    def _generate_personal_data(personal_info: str) -> str:
        """Extract and format personal data from personal_info section."""
        lines = personal_info.strip().split('\n')
        
        name = lines[0] if len(lines) > 0 else "Your Name"
        
        # Extract email, phone, location
        email = ""
        phone = ""
        location = ""
        
        for line in lines[1:]:
            line_lower = line.lower()
            if 'email' in line_lower or '@' in line:
                email = line.split(':')[-1].strip() if ':' in line else line.strip()
                email = email.replace('Email:', '').strip()
            elif 'phone' in line_lower or '(' in line or ')' in line:
                phone = line.split(':')[-1].strip() if ':' in line else line.strip()
                phone = phone.replace('Phone:', '').strip()
            elif 'location' in line_lower or 'address' in line_lower:
                location = line.split(':')[-1].strip() if ':' in line else line.strip()
        
        latex = f"\\name{{{name.split()[0] if name else 'First'}}}{{{' '.join(name.split()[1:]) if len(name.split()) > 1 else 'Last'}}}\n"
        
        if email:
            latex += f"\\email{{{email}}}\n"
        if phone:
            latex += f"\\phone[mobile]{{{phone}}}\n"
        if location:
            latex += f"\\address{{{location}}}\n"
        
        return latex
    
    @staticmethod
    def _generate_summary_section(summary: str) -> str:
        """Generate professional summary section."""
        # Clean and escape LaTeX special characters
        summary_clean = LaTeXCVGenerator._escape_latex(summary.strip())
        
        return f"""\\section{{Professional Summary}}
{summary_clean}

"""
    
    @staticmethod
    def _generate_skills_section(skills: str) -> str:
        """Generate skills section."""
        skills_clean = LaTeXCVGenerator._escape_latex(skills.strip())
        
        # Try to parse structured skills
        lines = skills_clean.split('\n')
        
        latex = "\\section{Technical Skills}\n"
        
        for line in lines:
            if line.strip():
                # Check if it's a category (e.g., "Languages: Python, Java")
                if ':' in line:
                    parts = line.split(':', 1)
                    category = parts[0].strip()
                    items = parts[1].strip()
                    latex += f"\\cvitem{{{category}}}{{{items}}}\n"
                else:
                    latex += f"\\cvitem{{}}{{• {line.strip()}}}\n"
        
        latex += "\n"
        return latex
    
    @staticmethod
    def _generate_experience_section(experience: str) -> str:
        """Generate work experience section."""
        experience_clean = LaTeXCVGenerator._escape_latex(experience.strip())
        
        latex = "\\section{Work Experience}\n"
        
        # Parse experience entries (simplified parsing)
        lines = experience_clean.split('\n')
        current_entry = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_entry:
                    latex += LaTeXCVGenerator._format_experience_entry(current_entry)
                    current_entry = []
            else:
                current_entry.append(line)
        
        # Add last entry
        if current_entry:
            latex += LaTeXCVGenerator._format_experience_entry(current_entry)
        
        latex += "\n"
        return latex
    
    @staticmethod
    def _format_experience_entry(entry_lines: list) -> str:
        """Format a single experience entry."""
        if not entry_lines:
            return ""
        
        # First line is typically job title
        job_title = entry_lines[0]
        company = ""
        dates = ""
        description = []
        
        # Parse company and dates from second line
        if len(entry_lines) > 1:
            second_line = entry_lines[1]
            if '|' in second_line:
                parts = second_line.split('|')
                company = parts[0].strip()
                dates = parts[1].strip() if len(parts) > 1 else ""
            else:
                company = second_line
        
        # Rest are description points
        description = [line for line in entry_lines[2:] if line]
        
        latex = f"\\cventry{{{dates}}}{{{job_title}}}{{{company}}}{{}}{{}}{{%\n"
        
        if description:
            latex += "\\begin{itemize}\n"
            for point in description:
                point_clean = point.lstrip('•-').strip()
                latex += f"  \\item {point_clean}\n"
            latex += "\\end{itemize}}\n"
        else:
            latex += "}\n"
        
        return latex
    
    @staticmethod
    def _generate_education_section(education: str) -> str:
        """Generate education section."""
        education_clean = LaTeXCVGenerator._escape_latex(education.strip())
        
        latex = "\\section{Education}\n"
        
        lines = education_clean.split('\n')
        current_entry = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_entry:
                    latex += LaTeXCVGenerator._format_education_entry(current_entry)
                    current_entry = []
            else:
                current_entry.append(line)
        
        if current_entry:
            latex += LaTeXCVGenerator._format_education_entry(current_entry)
        
        latex += "\n"
        return latex
    
    @staticmethod
    def _format_education_entry(entry_lines: list) -> str:
        """Format a single education entry."""
        if not entry_lines:
            return ""
        
        degree = entry_lines[0]
        institution = entry_lines[1] if len(entry_lines) > 1 else ""
        dates = entry_lines[2] if len(entry_lines) > 2 else ""
        
        # Try to extract dates from institution line
        if '|' in institution:
            parts = institution.split('|')
            institution = parts[0].strip()
            dates = parts[1].strip() if len(parts) > 1 else dates
        
        return f"\\cventry{{{dates}}}{{{degree}}}{{{institution}}}{{}}{{}}{{}}\\n"
    
    @staticmethod
    def _generate_projects_section(projects: str) -> str:
        """Generate projects section."""
        projects_clean = LaTeXCVGenerator._escape_latex(projects.strip())
        
        latex = "\\section{Projects}\n"
        
        lines = projects_clean.split('\n')
        for line in lines:
            if line.strip():
                if line.strip().startswith(('-', '•')):
                    project_text = line.strip().lstrip('-•').strip()
                    if ':' in project_text:
                        parts = project_text.split(':', 1)
                        latex += f"\\cvitem{{{parts[0].strip()}}}{{{parts[1].strip()}}}\n"
                    else:
                        latex += f"\\cvitem{{}}{{• {project_text}}}\n"
                else:
                    latex += f"\\cvitem{{}}{{• {line.strip()}}}\n"
        
        latex += "\n"
        return latex
    
    @staticmethod
    def _generate_certifications_section(certifications: str) -> str:
        """Generate certifications section."""
        certifications_clean = LaTeXCVGenerator._escape_latex(certifications.strip())
        
        latex = "\\section{Certifications}\n"
        
        lines = certifications_clean.split('\n')
        for line in lines:
            if line.strip():
                cert_text = line.strip().lstrip('-•').strip()
                latex += f"\\cvitem{{}}{{• {cert_text}}}\n"
        
        latex += "\n"
        return latex
    
    @staticmethod
    def _escape_latex(text: str) -> str:
        """Escape special LaTeX characters."""
        # Common LaTeX special characters
        replacements = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\^{}',
            '\\': r'\textbackslash{}',
        }
        
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        return text
    
    @staticmethod
    def save_latex(latex_code: str, output_path: str = "improved_cv.tex"):
        """
        Save LaTeX code to file.
        
        Args:
            latex_code: LaTeX code string
            output_path: Output file path
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(latex_code)


if __name__ == '__main__':
    # Test the generator
    import sys
    import json
    from src.ats_cv_maker.keyword_placement_agent import ImprovedCVSections
    
    if len(sys.argv) < 2:
        print("Usage: python latex_cv_generator.py <improved_sections_json>")
        sys.exit(1)
    
    # Load improved sections
    with open(sys.argv[1], 'r') as f:
        sections_data = json.load(f)
    
    sections = ImprovedCVSections(**sections_data)
    
    print("📝 Generating LaTeX CV...")
    generator = LaTeXCVGenerator()
    latex_code = generator.generate_latex(sections)
    
    output_file = "improved_cv.tex"
    generator.save_latex(latex_code, output_file)
    
    print(f"✅ LaTeX CV generated: {output_file}")
    print("\nTo compile to PDF, run:")
    print(f"  pdflatex {output_file}")
