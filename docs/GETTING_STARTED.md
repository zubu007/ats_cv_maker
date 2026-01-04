# 🎉 ATS CV Maker v2.0 - Complete CV Improvement System

## What's New?

Your ATS CV Maker now has a **complete CV improvement workflow** that not only analyzes your CV but automatically optimizes it and generates a professional PDF!

## 📁 Project Structure

```
ats_cv_maker/
├── 📊 ANALYSIS MODULES
│   ├── cv_extractor.py              # Extract text from PDF/TXT
│   ├── keyword_extractor.py         # TF-IDF + spaCy keyword extraction
│   ├── keyword_rating_agent.py      # AI keyword rating (required/optional)
│   ├── ats_scorer.py               # Score calculation & reporting
│   └── main.py                      # Analysis-only workflow
│
├── ✨ IMPROVEMENT MODULES (NEW!)
│   ├── cv_section_parser.py         # AI-powered section parsing
│   ├── missing_keyword_identifier.py # Identify keywords to add
│   ├── keyword_placement_agent.py   # LangChain keyword placement
│   ├── latex_cv_generator.py        # Professional LaTeX generation
│   ├── pdf_generator.py            # PDF compilation
│   └── improve_cv.py                # Full improvement workflow
│
├── 🛠️ UTILITIES
│   ├── config.py                    # Configuration management
│   └── cost_estimator.py           # API cost estimation
│
├── 📚 DOCUMENTATION
│   ├── README.md                    # Main documentation
│   ├── SETUP.md                     # Installation guide
│   ├── WORKFLOW_GUIDE.md           # Improvement workflow guide
│   ├── COMPARISON.md               # Analysis vs Improvement modes
│   ├── QUICK_REFERENCE.md          # Command cheat sheet
│   └── PROJECT_SUMMARY.md          # Technical overview
│
├── 🚀 SCRIPTS
│   ├── quickstart.sh               # Automated setup
│   └── demo.sh                      # Demo workflow
│
├── 📄 SAMPLES
│   ├── sample_cv.txt               # Sample CV for testing
│   └── sample_job_description.txt  # Sample job description
│
└── ⚙️ CONFIGURATION
    ├── pyproject.toml              # Python dependencies
    ├── requirements.txt            # Alternative dependency list
    ├── .env.example               # Environment variables template
    └── .gitignore                 # Git ignore rules
```

## 🎯 Two Modes of Operation

### 1. Analysis Mode (`main.py`)
**Quick CV scoring and gap analysis**

```bash
python main.py cv.pdf job_description.txt
```

- Extracts keywords
- Rates as required/optional
- Calculates ATS score
- Reports missing keywords

### 2. Improvement Mode (`improve_cv.py`) ⭐ NEW!
**Complete CV optimization with PDF generation**

```bash
python improve_cv.py cv.pdf job_description.txt
```

Does everything Analysis Mode does, PLUS:
- ✨ Parses CV into sections
- ✨ Identifies keywords to add
- ✨ Intelligently places keywords
- ✨ Recalculates score
- ✨ Generates LaTeX CV
- ✨ Creates professional PDF

## 🚀 Quick Start

### Installation

```bash
# 1. Install Python dependencies
pip install -e .

# 2. Download spaCy model
python -m spacy download en_core_web_sm

# 3. Install LaTeX (for PDF generation)
# macOS:
brew install --cask mactex-no-gui
sudo tlmgr install moderncv

# Ubuntu:
sudo apt-get install texlive-latex-base texlive-latex-extra

# 4. Configure API keys
cp .env.example .env
# Edit .env with your OpenAI or Anthropic API key
```

### Try It Out

```bash
# Option 1: Run the demo
./demo.sh

# Option 2: Quick improvement
python improve_cv.py sample_cv.txt sample_job_description.txt

# Option 3: With your own CV
python improve_cv.py my_cv.pdf job_description.txt --output optimized_cv
```

## 📊 What You Get

After running the improvement workflow:

```
📁 Output Files:
├── cv_sections/                    # Original CV sections
│   ├── personal_info.txt
│   ├── skills.txt
│   ├── work_experience.txt
│   ├── education.txt
│   └── sections.json
│
├── improved_cv_sections/           # Enhanced sections
│   ├── professional_summary.txt    # With keywords added
│   ├── skills.txt                  # Updated skills
│   ├── work_experience.txt         # Enhanced descriptions
│   ├── placement_notes.txt         # What was changed
│   └── improved_sections.json
│
├── optimized_cv.tex               # LaTeX source (editable)
└── optimized_cv.pdf               # Final PDF! ✨
```

## 🎨 Key Features

### Intelligent Keyword Placement
- **LangChain Structured Outputs**: Ensures proper JSON parsing
- **Context-Aware**: Adds keywords where they make sense
- **Natural Integration**: Maintains readability and authenticity
- **Placement Notes**: Explains what was added and where

### Professional PDF Generation
- **ModernCV Template**: Clean, professional LaTeX template
- **Single Column**: ATS-friendly format
- **A4 Size**: Standard professional sizing
- **Automatic Compilation**: From LaTeX to PDF in seconds

### Smart Analysis
- **TF-IDF**: Statistical keyword importance
- **spaCy NLP**: Noun phrase and entity extraction
- **AI Rating**: GPT-4 or Claude categorizes keywords
- **Weighted Scoring**: 70% required, 30% optional

## 📈 Example Results

```
📊 INITIAL SCORE: 68.33%
   Missing 6 required keywords

🔧 IMPROVING CV...
   Adding: docker, kubernetes, ci/cd, git, microservices, unit testing

📊 NEW SCORE: 91.67%
   Improvement: +23.34% 🚀

✅ PDF GENERATED: optimized_cv.pdf
```

## 💰 Cost Estimates

### Per Improvement Session
- **GPT-4**: $0.04-0.06
- **GPT-3.5-Turbo**: $0.003-0.006  
- **Claude-3-Sonnet**: $0.015-0.025 (recommended)
- **Claude-3-Haiku**: $0.002-0.004 (budget option)

Use `python cost_estimator.py compare` to see full comparison.

## 🔧 Command Reference

```bash
# Full improvement workflow
python improve_cv.py cv.pdf jd.txt

# Analysis only
python improve_cv.py cv.pdf jd.txt --analyze-only

# Custom output name
python improve_cv.py cv.pdf jd.txt --output my_cv

# Limit keywords to add
python improve_cv.py cv.pdf jd.txt --max-keywords 5

# Without spaCy
python improve_cv.py cv.pdf jd.txt --no-spacy

# View configuration
python config.py

# Estimate costs
python cost_estimator.py compare 10
```

## 📖 Documentation Guide

1. **Start Here**: [README.md](README.md) - Overview and quick start
2. **Setup**: [SETUP.md](SETUP.md) - Detailed installation
3. **Usage**: [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) - Complete workflow guide
4. **Commands**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Command cheat sheet
5. **Comparison**: [COMPARISON.md](COMPARISON.md) - Analysis vs Improvement modes
6. **Technical**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Architecture details

## 🎓 How It Works

### The 6-Step Improvement Process

1. **Parse Sections** (LangChain)
   - Extracts: Skills, Experience, Education, etc.
   - Saves each section separately

2. **Identify Missing Keywords**
   - Compares CV keywords with job requirements
   - Prioritizes required over optional

3. **Smart Placement** (LangChain Structured Outputs)
   - Adds keywords to appropriate sections
   - Maintains natural language
   - Provides placement notes

4. **Recalculate Score**
   - Extracts keywords from improved CV
   - Calculates new ATS score
   - Shows improvement

5. **Generate LaTeX**
   - Creates professional single-column CV
   - Uses moderncv template
   - Properly formatted sections

6. **Compile PDF**
   - Runs pdflatex automatically
   - Cleans up auxiliary files
   - Outputs polished PDF

## 🌟 Best Practices

### Before Running
1. ✅ Review your original CV for accuracy
2. ✅ Have a detailed job description ready
3. ✅ Ensure API keys are configured
4. ✅ Install LaTeX for PDF generation

### After Running
1. ✅ Read placement_notes.txt
2. ✅ Review the improved PDF
3. ✅ Verify all added keywords are truthful
4. ✅ Customize LaTeX file if needed
5. ✅ Test ATS score on real ATS systems

### Tips
- Start with `--max-keywords 5` for subtle improvements
- Use `--analyze-only` first to see what needs work
- Review and edit the .tex file before final submission
- Run multiple times with different job descriptions
- Keep original CV as baseline

## 🐛 Troubleshooting

### Common Issues

**1. "moderncv.cls not found"**
```bash
sudo tlmgr install moderncv  # macOS/Linux
# Windows: Install via MiKTeX Console
```

**2. "API key not found"**
```bash
cp .env.example .env
# Edit .env and add your API key
```

**3. "PDF not generated"**
```bash
# Check if pdflatex is installed
pdflatex --version

# Compile manually
pdflatex optimized_cv.tex
```

**4. "No keywords added"**
- Your CV may already be well-optimized!
- Check placement_notes.txt for details
- Try increasing --max-keywords

## 🔮 Future Enhancements

Planned features:
- ✅ Keyword match score (COMPLETED)
- ⏳ Skill match score
- ⏳ Experience match score  
- ⏳ Multi-page CV support
- ⏳ Multiple CV templates
- ⏳ Batch processing
- ⏳ Web interface

## 📝 License

MIT License - Free for personal and commercial use.

## 🙏 Credits

Built with:
- **LangChain**: For structured AI outputs
- **OpenAI/Anthropic**: For AI-powered analysis
- **spaCy**: For NLP and keyword extraction
- **ModernCV**: For LaTeX CV template
- **scikit-learn**: For TF-IDF vectorization

---

## 🚀 Ready to Get Started?

```bash
# Quick demo
./demo.sh

# Or dive right in
python improve_cv.py your_cv.pdf job_description.txt
```

**Questions?** Check the documentation files or open an issue!

**Happy job hunting! 🎯**
