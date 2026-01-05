This software project is licensed under the MIT License.

# ATS CV Maker

An intelligent ATS (Applicant Tracking System) tool that scores your CV through keyword matching AND skill matching, then automatically improves it by adding missing keywords and generating a professional LaTeX PDF.

## Features

### Analysis Features
- 📄 **CV Text Extraction**: Supports PDF and TXT formats
- 🔍 **Keyword Extraction**: Uses TF-IDF and spaCy for intelligent keyword extraction
- 🤖 **AI-Powered Rating**: Uses OpenAI or Anthropic to categorize keywords as required/optional
- 📊 **Keyword Scoring**: Calculates keyword match scores with detailed breakdowns
- 🎯 **Skill Extraction & Matching** (NEW!): LLM-powered skill extraction, intelligent normalization, and matching
- 🎯 **Skill Scoring** (NEW!): Calculates skill match score based on job requirements
- 📝 **Detailed Reports**: Generates comprehensive reports with matched/missing keywords and skills

### Improvement Features
- 🤖 **AI Section Parser**: Intelligently parses CV into structured sections
- 🎯 **Missing Keyword Identification**: Identifies which keywords to add
- ✨ **Smart Keyword Placement**: Uses LangChain to naturally add keywords to appropriate sections
- 📄 **LaTeX Generation**: Creates professional single-column A4 CV in LaTeX
- 🎨 **PDF Generation**: Automatically compiles to a polished PDF

## Installation

1. **Clone the repository**:
```bash
cd /Users/zhade/project/youtube_projects/ats_cv_maker
```

2. **Create a virtual environment** (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -e .
# Or alternatively:
pip install -r requirements.txt
```

4. **Download spaCy language model** (optional but recommended):
```bash
python -m spacy download en_core_web_sm
```

5. **Install LaTeX** (required for PDF generation):
```bash
# macOS
brew install --cask mactex-no-gui

# Ubuntu/Debian
sudo apt-get install texlive-latex-base texlive-latex-extra

# Windows
# Download and install MiKTeX from https://miktex.org/
```

6. **Set up environment variables**:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```bash
# For OpenAI
OPENAI_API_KEY=your_openai_api_key_here
AI_PROVIDER=openai
AI_MODEL=gpt-4

# ### Analyze Only (Original Functionality)

```bash
# Basic analysis (keyword matching)
python main.py cv.pdf job_description.txt

# With output report
python main.py cv.pdf job_description.txt --output report.txt

# Skip skill analysis
python main.py cv.pdf job_description.txt --no-skills

# Skip skill normalization (faster, cheaper)
python main.py cv.pdf job_description.txt --no-normalize-skills
```

### Skill Match Analysis (NEW!)

```bash
# Skill match score only
python skill_score.py cv.pdf job_description.txt

# With detailed matching information
python skill_score.py cv.pdf job_description.txt --verbose

# Skip normalization (saves API calls)
python skill_score.py cv.pdf job_description.txt --no-normalize

# Save skill report
python skill_score.py cv.pdf job_description.txt --output skill_report.txt
```

### Improve CV (Full Workflow)

```bash
# Analyze, improve, and generate PDF
python improve_cv.py cv.pdf job_description.txt

# Specify output name
python improve_cv.py cv.pdf job_description.txt --output my_improved_cv

# Limit keywords to add
python improve_cv.py cv.pdf job_description.txt --max-keywords 5

# Analyze only without improvement
python improve_cv.py cv.pdf job_description.txt --analyze-only
```

### Complete Example

```bash
# This will:
# 1. Extract and analyze CV + JD
# 2. Calculate keyword and skill scores
# 3. Parse CV into sections
# 4. Identify missing keywords
# 5. Add keywords intelligently
# 6. Recalculate score
# 7. Generate LaTeX file
# 8. Create PDF

python improve_cv.py my_resume.pdf software_engineer_jd.txt --output optimized_resume
```

## Analysis Mode

### Keyword Matching (main.py)

1. **Extract Text**: Extracts text from your CV (PDF/TXT)
2. **Extract Keywords**: Uses TF-IDF and noun-phrase extraction to identify key terms
3. **Rate Keywords**: AI agent analyzes job description to categorize keywords
4. **Calculate Score**: Matches CV keywords against rated job description keywords
5. **Generate Report**: Creates detailed report with matched/missing keywords

Where:
- **Required keywords**: Skills and qualifications marked as "required", "must have", or "essential"
- **Optional keywords**: Skills marked as "preferred", "nice to have", or "bonus"
- **Weights**: Required keywords count for 70%, optional for 30%

**Formula**: $(matched\_required / total) × 0.7 + (matched\_optional / total) × 0.3$

### Skill Matching (skill_score.py) - NEW!

1. **Extract Skills**: LLM extracts professional skills from CV and job description
2. **Normalize Skills**: Intelligently groups similar skills (e.g., PyTorch + TensorFlow → "Deep Learning Framework")
3. **Merge Skills**: Combines original and normalized skills
4. **Match Skills**: Uses fuzzy matching to find similarities between CV and JD skills
5. **Calculate Score**: Computes skill match percentage

**Formula**: $(matched\_skills / total\_jd\_skills) × 100$

**Example**: 7 matched skills out of 10 required = (7/10) × 100 = **70/100**

**Key Difference**: Skill matching focuses on actual skill fit, not keyword density.

### Improvement Mode (improve_cv.py)

1. **Parse Sections**: AI agent separates CV into structured sections (skills, experience, etc.)
2. **Identify Missing**: Compares CV keywords with job requirements
3. **Smart Placement**: LangChain-powered agent adds keywords naturally to appropriate sections
4. **Recalculate Score**: Computes new ATS score after improvements
5. **Generate LaTeX**: Creates professional single-column A4 CV
6. **Create PDF**: Compiles LaTeX to final PDF

## Modules

### Analysis Modules
- **cv_extractor.py**: Extracts text from CV files (PDF, TXT)
- **keyword_extractor.py**: Extracts keywords using TF-IDF and spaCy
- **keyword_rating_agent.py**: AI agent for rating keywords as required/optional
- **ats_scorer.py**: Calculates ATS scores (keyword and skill) and generates reports
- **skill_extractor.py** (NEW!): Extracts professional skills from text using LLM
- **skill_normalizer.py** (NEW!): Intelligently normalizes and standardizes skill names
- **skill_matcher.py** (NEW!): Matches skills between CV and job description
- **main.py**: Integrated keyword and skill analysis workflow

### Improvement Modules
- **cv_section_parser.py**: AI agent to parse CV into structured sections using LangChain
- **missing_keyword_identifier.py**: Identifies missing keywords to add
- **keyword_placement_agent.py**: Intelligently places keywords using LangChain
- **latex_cv_generator.py**: Generates professional LaTeX CV (single-column, A4)
- **pdf_generator.py**: Compiles LaTeX to PDF
- **improve_cv.py**: Full improvement workflow orchestration

### Entry Point Scripts
- **main.py**: Integrated keyword + skill analysis
- **skill_score.py** (NEW!): Standalone skill matching analysis
- **skill_score_orchestration.py** (NEW!): Programmatic interface for skill analysis
- **improve_cv.py**: Full CV improvement and PDF generation workflow

## Requirements

- Python >= 3.11
- OpenAI API key OR Anthropic API key
- Dependencies listed in pyproject.toml

## Requirements

- Python >= 3.11
- OpenAI API key OR Anthropic API key
- Dependencies listed in pyproject.toml
- LaTeX distribution (for PDF generation in improve_cv.py)

## Future Enhancements

Planned features:
1. ✅ Skill match score (IMPLEMENTED!)
2. Experience match score
3. Recency score
4. Education match score
5. Semantic relevance score
6. Skill proficiency levels (beginner, intermediate, expert)
7. Learning path recommendations
8. Market trend analysis

## License

MIT License

## Documentation

For detailed information about skill matching, see:
- [Skill Matching Quick Start](docs/SKILL_MATCHING_QUICKSTART.md) - Quick usage guide
- [Skill Matching System](docs/SKILL_MATCHING.md) - Comprehensive documentation
- [Skill System Index](docs/SKILL_SYSTEM_INDEX.md) - Complete feature index
- [Implementation Details](docs/SKILL_MATCHING_IMPLEMENTATION.md) - Technical details

For other documentation:
- [Setup Guide](docs/SETUP.md) - Detailed installation
- [Workflow Guide](docs/WORKFLOW_GUIDE.md) - Complete workflows
- [Getting Started](docs/GETTING_STARTED.md) - Quick start tutorial