# Project Structure

This document describes the organized folder structure of the ATS CV Maker project.

## Directory Layout

```
ats_cv_maker/
├── 📁 src/
│   └── ats_cv_maker/           # Main Python package
│       ├── __init__.py          # Package initialization
│       ├── ats_scorer.py        # ATS score calculation
│       ├── config.py            # Configuration management
│       ├── cost_estimator.py    # API cost estimation
│       ├── cv_extractor.py      # Text extraction from CVs
│       ├── cv_section_parser.py # AI-powered section parsing
│       ├── experience_relevance_scorer.py  # Experience relevance scoring ⭐
│       ├── job_title_normalizer.py        # Job title normalization ⭐
│       ├── keyword_extractor.py # Keyword extraction (TF-IDF + spaCy)
│       ├── keyword_placement_agent.py   # LangChain keyword placement
│       ├── keyword_rating_agent.py      # AI keyword rating
│       ├── latex_cv_generator.py        # LaTeX CV generation
│       ├── missing_keyword_identifier.py # Missing keyword identification
│       ├── skill_extractor.py           # Skill extraction
│       ├── skill_normalizer.py          # Skill normalization
│       ├── skill_matcher.py             # Skill matching
│       ├── pdf_generator.py             # PDF compilation
│       ├── output_manager.py            # Output management
│       ├── keyword_placement_agent.py   # Keyword placement
│       └── pipeline_finalizer.py        # Pipeline finalization
│
├── 📁 docs/                     # Documentation
│   ├── README.md               # Documentation index
│   ├── GETTING_STARTED.md      # Quick start guide
│   ├── SETUP.md                # Installation guide
│   ├── WORKFLOW_GUIDE.md       # Workflow tutorial
│   ├── COMPARISON.md           # Analysis vs Improvement modes
│   ├── QUICK_REFERENCE.md      # Command reference
│   ├── LATEX_INSTALL.md        # LaTeX setup
│   ├── PROJECT_SUMMARY.md      # Technical overview
│   ├── EXPERIENCE_RELEVANCE.md # Experience relevance scoring ⭐
│   ├── SKILL_MATCHING.md       # Skill matching system
│   ├── SKILL_SYSTEM_INDEX.md   # Skill system documentation
│   ├── SKILL_MATCHING_QUICKSTART.md # Quick start for skills
│   └── OUTPUT_MANAGEMENT.md    # Output management guide
│
├── 📁 scripts/                  # Utility scripts
│   ├── demo.sh                 # Interactive demo
│   └── quickstart.sh           # Quick setup script
│
├── 📁 examples/                # Sample files
│   ├── sample_cv.txt           # Example CV
│   └── sample_job_description.txt # Example job description
│
├── 📄 main.py                  # Analysis-only entry point
├── 📄 improve_cv.py            # Full improvement workflow
│
├── ⚙️ Configuration Files
│   ├── pyproject.toml          # Python project configuration
│   ├── requirements.txt        # Alternative dependency list
│   ├── uv.lock                 # Dependency lock file
│   ├── .env.example            # Environment variables template
│   └── .gitignore              # Git ignore rules
│
└── 📄 README.md               # Main project documentation
```

## Folder Descriptions

### `src/ats_cv_maker/`
**Main Python package containing all analysis and improvement modules.**

Core modules:
- **cv_extractor.py** - Extracts text from PDF/TXT files
- **keyword_extractor.py** - TF-IDF and spaCy-based keyword extraction
- **keyword_rating_agent.py** - AI-powered keyword categorization
- **ats_scorer.py** - ATS score calculation and reporting
- **experience_relevance_scorer.py** ⭐ - Experience relevance scoring
- **job_title_normalizer.py** ⭐ - Job title normalization with AI support

Improvement modules:
- **cv_section_parser.py** - LangChain CV section parsing
- **missing_keyword_identifier.py** - Missing keyword identification
- **keyword_placement_agent.py** - LangChain keyword placement
- **latex_cv_generator.py** - Professional CV generation in LaTeX
- **pdf_generator.py** - PDF compilation from LaTeX

Utilities:
- **config.py** - Configuration management
- **cost_estimator.py** - API cost calculation

### `docs/`
**All documentation files for the project.**

- README.md - Documentation index
- GETTING_STARTED.md - Quick start guide
- SETUP.md - Detailed installation
- WORKFLOW_GUIDE.md - How to improve CVs
- COMPARISON.md - Mode comparison guide
- QUICK_REFERENCE.md - Command cheat sheet
- LATEX_INSTALL.md - LaTeX installation guide
- PROJECT_SUMMARY.md - Technical details

### `scripts/`
**Executable scripts for quick setup and demos.**

- demo.sh - Interactive demo of the full workflow
- quickstart.sh - Automated setup and installation

### `examples/`
**Sample files for testing and demonstration.**

- sample_cv.txt - Example CV for testing
- sample_job_description.txt - Example job description

## Key Configuration Files

### `pyproject.toml`
Project metadata and dependencies. Run `uv sync` to install.

### `.env.example`
Copy to `.env` and add your API keys:
```bash
cp .env.example .env
# Edit with your OpenAI or Anthropic API keys
```

### `main.py` & `improve_cv.py`
Entry points for the application:
- **main.py** - Analysis-only mode (faster, cheaper)
- **improve_cv.py** - Full improvement workflow (generates PDF)

## Import Examples

### Using as a package:
```python
from src.ats_cv_maker import (
    CVExtractor,
    KeywordExtractor,
    ATSScorer,
    CVSectionParser,
    LaTeXCVGenerator,
    ExperienceRelevanceScorer,  # ⭐ New
    JobTitleNormalizer,          # ⭐ New
)

# Extract CV text
extractor = CVExtractor()
cv_text = extractor.extract("resume.pdf")

# Extract keywords
keyword_extractor = KeywordExtractor()
keywords = keyword_extractor.extract_keywords(cv_text)

# Score experience relevance ⭐
exp_scorer = ExperienceRelevanceScorer()
experience_score = exp_scorer.score_experience(
    cv_experiences=experiences,
    target_job_title="Senior Engineer"
)
```

### Running scripts:
```bash
# Quick analysis
python main.py cv.pdf job_description.txt

# Full improvement workflow
python improve_cv.py cv.pdf job_description.txt

# Demo
./scripts/demo.sh

# Quick setup
./scripts/quickstart.sh
```

## Project Statistics

- **Python Modules**: 12 (in src/ats_cv_maker/)
- **Documentation Files**: 8 (in docs/)
- **Scripts**: 2 (in scripts/)
- **Sample Files**: 2 (in examples/)
- **Total Lines of Code**: ~3,500+
- **Documentation**: ~10,000+ lines

## How to Navigate

1. **New to the project?** → Start with [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)
2. **Want to install?** → See [docs/SETUP.md](docs/SETUP.md)
3. **Need LaTeX help?** → Check [docs/LATEX_INSTALL.md](docs/LATEX_INSTALL.md)
4. **Using the CLI?** → Reference [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)
5. **Understanding workflows?** → Read [docs/WORKFLOW_GUIDE.md](docs/WORKFLOW_GUIDE.md)

## Development Workflow

```bash
# Install dependencies
uv sync

# Run analysis
python main.py examples/sample_cv.txt examples/sample_job_description.txt

# Run full improvement
python improve_cv.py examples/sample_cv.txt examples/sample_job_description.txt

# Run demo
./scripts/demo.sh
```

## Git Considerations

The following are gitignored:
- Generated CV files (cv_sections/, improved_cv_sections/)
- PDF and LaTeX output files (*.pdf, *.tex, *.aux, *.log)
- Virtual environments (.venv/, venv/)
- Python cache (__pycache__/)

But these are tracked:
- All source code (src/)
- All documentation (docs/)
- Sample files (examples/)
- Configuration files
