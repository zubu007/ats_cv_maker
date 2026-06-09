"""
LaTeX CV Generator
Generates a professional single-column, 1-page A4 CV in LaTeX format.
"""

import re
from typing import Optional
from .keyword_placement_agent import ImprovedCVSections


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
        parsed_name, parsed_email, parsed_phone, parsed_location = LaTeXCVGenerator._parse_personal_data(
            sections.personal_info
        )

        # Extract name from personal info if not provided
        if not name:
            name = parsed_name or "Your Name"
        
        latex_code = r"""\PassOptionsToPackage{expansion=false}{microtype}
\documentclass[11pt,a4paper,sans]{moderncv}

% Modern CV style and color
\moderncvstyle{banking}
\moderncvcolor{blue}

% Character encoding
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}

% Adjust page margins
\usepackage[scale=0.85]{geometry}
\setlength{\hintscolumnwidth}{4cm}
\setlength{\emergencystretch}{2em}

% Reduce spacing
\usepackage{enumitem}
\setlist{noitemsep,topsep=2pt,parsep=2pt,partopsep=2pt}

""" + LaTeXCVGenerator._generate_moderncv_metadata(
            name=name,
            email=parsed_email,
            phone=parsed_phone,
            location=parsed_location,
        ) + r"""
\begin{document}

""" + LaTeXCVGenerator._generate_left_aligned_header(
            name=name,
            email=parsed_email,
            phone=parsed_phone,
            location=parsed_location,
        ) + "\n"
        
        # Add Professional Summary
        if sections.professional_summary:
            latex_code += LaTeXCVGenerator._generate_summary_section(sections.professional_summary)
        
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

        # Skills should appear near the end
        if sections.skills:
            latex_code += LaTeXCVGenerator._generate_skills_section(sections.skills)

        # Additional section appears after skills
        if sections.additional:
            latex_code += LaTeXCVGenerator._generate_additional_section(sections.additional)
        
        latex_code += r"""
\end{document}
"""
        
        return latex_code
    
    @staticmethod
    def _parse_personal_data(personal_info: str) -> tuple[str, str, str, str]:
        """Extract personal data from personal_info section."""
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

        return name.strip(), email.strip(), phone.strip(), location.strip()

    @staticmethod
    def _generate_left_aligned_header(name: str, email: str, phone: str, location: str) -> str:
        """
        Build a left-aligned header so name/personal data are not centered.
        Keeps full name in one style/color.
        """
        safe_name = LaTeXCVGenerator._escape_latex(name or "Your Name")
        contact_parts = []
        if email:
            contact_parts.append(LaTeXCVGenerator._escape_latex(email))
        if phone:
            contact_parts.append(LaTeXCVGenerator._escape_latex(phone))
        if location:
            contact_parts.append(LaTeXCVGenerator._escape_latex(location))

        latex = f"{{\\Huge\\bfseries\\textcolor{{black}}{{{safe_name}}}}}\n\n"

        if contact_parts:
            latex += " \\enspace|\\enspace ".join(contact_parts) + "\n\n"

        latex += "\\vspace{0.6em}\n"
        return latex

    @staticmethod
    def _generate_moderncv_metadata(name: str, email: str, phone: str, location: str) -> str:
        """
        Define moderncv metadata macros to prevent class-level undefined-command warnings.
        We still render a custom left-aligned header manually.
        """
        parts = (name or "").split()
        first_name = parts[0] if parts else "First"
        last_name = " ".join(parts[1:]) if len(parts) > 1 else "Last"

        metadata_lines = [
            f"\\name{{{LaTeXCVGenerator._escape_latex(first_name)}}}{{{LaTeXCVGenerator._escape_latex(last_name)}}}",
        ]

        if email:
            metadata_lines.append(f"\\email{{{LaTeXCVGenerator._escape_latex(email)}}}")
        if phone:
            metadata_lines.append(f"\\phone[mobile]{{{LaTeXCVGenerator._escape_latex(phone)}}}")
        if location:
            metadata_lines.append(f"\\address{{{LaTeXCVGenerator._escape_latex(location)}}}")

        return "\n".join(metadata_lines) + "\n"
    
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
                    latex += f"\\cvitem{{}}{{\\textbullet{{}} {line.strip()}}}\n"
        
        latex += "\n"
        return latex

    @staticmethod
    def _generate_additional_section(additional: str) -> str:
        """Generate additional section."""
        additional_clean = LaTeXCVGenerator._escape_latex(additional.strip())
        if not additional_clean:
            return ""
        return f"""\\section{{Additional}}
{additional_clean}

"""
    
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
        
        degree = entry_lines[0].strip()
        institution_line = entry_lines[1].strip() if len(entry_lines) > 1 else ""
        dates = ""
        overview_lines: list[str] = []

        institution = institution_line
        if "|" in institution_line:
            parts = institution_line.split("|", 1)
            institution = parts[0].strip()
            dates = parts[1].strip()
            overview_lines = [line.strip() for line in entry_lines[2:] if line.strip()]
        else:
            if len(entry_lines) > 2 and LaTeXCVGenerator._looks_like_date_line(entry_lines[2].strip()):
                dates = entry_lines[2].strip()
                overview_lines = [line.strip() for line in entry_lines[3:] if line.strip()]
            else:
                overview_lines = [line.strip() for line in entry_lines[2:] if line.strip()]

        latex = f"\\cventry{{{dates}}}{{{degree}}}{{{institution}}}{{}}{{}}{{%\n"
        if overview_lines:
            latex += "\\begin{itemize}\n"
            for line in overview_lines:
                latex += f"  \\item {line}\n"
            latex += "\\end{itemize}}\n"
        else:
            latex += "}\n"
        return latex
    
    @staticmethod
    def _generate_projects_section(projects: str) -> str:
        """Generate projects section."""
        projects_raw = projects.strip()
        if not projects_raw:
            return ""

        latex = "\\section{Projects}\n"

        entries = LaTeXCVGenerator._parse_project_entries(projects_raw)
        for title, details in entries:
            safe_title = LaTeXCVGenerator._escape_latex(title or "Project")
            safe_details = LaTeXCVGenerator._escape_latex_with_urls(details)
            latex += f"\\cvitem{{{safe_title}}}{{\\newline {safe_details}}}\n"

        latex += "\n"
        return latex

    @staticmethod
    def _parse_project_entries(projects_raw: str) -> list[tuple[str, str]]:
        """
        Parse project text into (title, details) while collapsing noisy line breaks/bullets.
        """
        entries: list[tuple[str, str]] = []
        current_title = ""
        current_parts: list[str] = []

        def flush_current() -> None:
            nonlocal current_title, current_parts
            if not current_title and not current_parts:
                return
            details = " | ".join(part for part in current_parts if part)
            entries.append((current_title or "Project", details))
            current_title = ""
            current_parts = []

        for raw_line in projects_raw.splitlines():
            stripped = raw_line.strip()
            if not stripped:
                continue
            if stripped in {"•", "*", "-", "•:"}:
                continue

            starts_new = stripped.startswith("-")
            cleaned = stripped.lstrip("-").lstrip("•").strip()
            if not cleaned:
                continue

            if starts_new:
                flush_current()
                if ":" in cleaned:
                    title, details = cleaned.split(":", 1)
                    current_title = title.strip()
                    if details.strip():
                        current_parts.append(details.strip())
                else:
                    current_title = cleaned
            else:
                # Continuation line for current project details.
                if not current_title:
                    current_title = "Project"
                current_parts.append(cleaned)

        flush_current()
        return entries

    @staticmethod
    def _looks_like_date_line(text: str) -> bool:
        lowered = text.lower()
        if any(token in lowered for token in ["present", "current", "-", "to"]):
            return bool(re.search(r"\d{4}", text))
        return bool(re.fullmatch(r"\d{4}", text.strip()))
    
    @staticmethod
    def _generate_certifications_section(certifications: str) -> str:
        """Generate certifications section."""
        certifications_clean = LaTeXCVGenerator._escape_latex(certifications.strip())
        
        latex = "\\section{Certifications}\n"
        
        lines = certifications_clean.split('\n')
        for line in lines:
            if line.strip():
                cert_text = line.strip().lstrip('-•').strip()
                latex += f"\\cvitem{{}}{{\\textbullet{{}} {cert_text}}}\n"
        
        latex += "\n"
        return latex
    
    @staticmethod
    def _escape_latex(text: str) -> str:
        """Escape special LaTeX characters."""
        replacements = {
            '\\': r'\char`\\',
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
            '•': r'\textbullet{}',
        }
        return "".join(replacements.get(char, char) for char in text)

    @staticmethod
    def _escape_latex_with_urls(text: str) -> str:
        """
        Escape LaTeX text while preserving URLs with explicit line-break hints,
        so long links can wrap without overflowing the right margin.
        """
        if not text:
            return ""

        url_pattern = re.compile(r"https?://\S+")
        pieces: list[str] = []
        cursor = 0

        for match in url_pattern.finditer(text):
            start, end = match.span()
            raw_url = match.group(0)

            prefix = text[cursor:start]
            if prefix:
                pieces.append(LaTeXCVGenerator._escape_latex(prefix))

            trailing = ""
            while raw_url and raw_url[-1] in ".,);:!?":
                trailing = raw_url[-1] + trailing
                raw_url = raw_url[:-1]

            pieces.append(LaTeXCVGenerator._format_breakable_url(raw_url))
            if trailing:
                pieces.append(LaTeXCVGenerator._escape_latex(trailing))

            cursor = end

        suffix = text[cursor:]
        if suffix:
            pieces.append(LaTeXCVGenerator._escape_latex(suffix))

        return "".join(pieces)

    @staticmethod
    def _format_breakable_url(raw_url: str) -> str:
        """
        Render URL text with safe LaTeX escaping and explicit break opportunities.
        """
        escaped = LaTeXCVGenerator._escape_latex(raw_url)
        escaped = escaped.replace("://", "://\\allowbreak{}")
        escaped = escaped.replace("/", "/\\allowbreak{}")
        escaped = escaped.replace("-", "-\\allowbreak{}")
        escaped = escaped.replace("\\_", "\\_\\allowbreak{}")
        escaped = escaped.replace("?", "?\\allowbreak{}")
        escaped = escaped.replace("=", "=\\allowbreak{}")
        escaped = escaped.replace("\\&", "\\&\\allowbreak{}")
        return escaped
    
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
    from .keyword_placement_agent import ImprovedCVSections
    
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
