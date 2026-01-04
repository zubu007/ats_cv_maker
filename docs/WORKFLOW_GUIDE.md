# CV Improvement Workflow Guide

## Overview

The ATS CV Maker now includes a complete workflow to automatically improve your CV by:
1. Parsing your CV into sections
2. Identifying missing keywords
3. Intelligently adding keywords to appropriate sections
4. Recalculating the ATS score
5. Generating a professional LaTeX PDF

## Complete Workflow

### Step 1: Analyze Your CV

First, analyze your CV to see the initial score:

```bash
python improve_cv.py my_cv.pdf job_description.txt --analyze-only
```

This shows you:
- Initial ATS score
- Matched required/optional keywords
- Missing required/optional keywords

### Step 2: Improve Your CV

Run the full improvement workflow:

```bash
python improve_cv.py my_cv.pdf job_description.txt --output optimized_cv
```

This will:
1. **Parse CV Sections** - AI extracts:
   - Personal Info
   - Professional Summary
   - Skills
   - Work Experience
   - Education
   - Projects
   - Certifications
   
2. **Identify Missing Keywords**:
   - Lists missing required keywords (priority)
   - Lists missing optional keywords
   - Prioritizes top keywords to add

3. **Smart Keyword Placement**:
   - Uses LangChain with structured outputs
   - Adds keywords naturally to appropriate sections
   - Maintains authenticity and readability
   - Provides placement notes

4. **Recalculate Score**:
   - Extracts keywords from improved CV
   - Calculates new ATS score
   - Shows improvement percentage

5. **Generate LaTeX & PDF**:
   - Creates professional single-column A4 CV
   - Uses moderncv LaTeX template
   - Compiles to PDF automatically

## Output Files

After running the improvement workflow, you'll find:

```
project/
├── cv_sections/              # Original CV sections
│   ├── personal_info.txt
│   ├── skills.txt
│   ├── work_experience.txt
│   ├── education.txt
│   └── sections.json
├── improved_cv_sections/     # Improved sections with keywords
│   ├── personal_info.txt
│   ├── professional_summary.txt
│   ├── skills.txt
│   ├── work_experience.txt
│   ├── education.txt
│   ├── placement_notes.txt
│   └── improved_sections.json
├── optimized_cv.tex          # LaTeX source
└── optimized_cv.pdf          # Final PDF! ✨
```

## Command-Line Options

```bash
# Full improvement with defaults
python improve_cv.py cv.pdf jd.txt

# Custom output name
python improve_cv.py cv.pdf jd.txt --output my_new_cv

# Limit keywords to add (default: 10)
python improve_cv.py cv.pdf jd.txt --max-keywords 5

# Analysis only (no improvement)
python improve_cv.py cv.pdf jd.txt --analyze-only

# Without spaCy
python improve_cv.py cv.pdf jd.txt --no-spacy
```

## Example Session

```
🚀 Starting ATS CV Analysis...
============================================================

📄 Extracting text from CV...
✓ Extracted 1542 characters from CV

📋 Extracting text from job description...
✓ Extracted 892 characters from job description

🔍 Extracting keywords...
✓ Extracted 45 keywords from CV
✓ Extracted 38 keywords from job description

🤖 Rating keywords as required/optional...
✓ Identified 15 required keywords
✓ Identified 12 optional keywords

📊 Calculating initial ATS score...

============================================================
ATS KEYWORD MATCH SCORE REPORT
============================================================

📊 INITIAL SCORE: 68.33%

Required Keywords Score: 60.00% (9/15)
Optional Keywords Score: 83.33% (10/12)

❌ MISSING REQUIRED KEYWORDS:
  • docker
  • kubernetes
  • ci/cd
  • git
  • microservices
  • unit testing

============================================================
🔧 IMPROVING CV
============================================================

📑 Parsing CV into sections...
✓ Parsed and saved 7 sections

🔍 Identifying missing keywords...
✓ Found 6 missing required keywords
✓ Found 2 missing optional keywords

📝 Will add 8 keywords:
  • docker
  • kubernetes
  • ci/cd
  • git
  • microservices
  • unit testing
  • graphql
  • redis

🤖 Using AI to intelligently place keywords...
✓ Improved sections saved to: improved_cv_sections/

📋 Placement notes:
Added Docker and Kubernetes to Skills section.
Integrated CI/CD pipeline experience into current role description.
Added Git to version control tools in Skills.
Mentioned microservices architecture in Senior Developer role.
Added unit testing to development practices.
Included GraphQL and Redis in technical skills.

============================================================
📊 CALCULATING NEW SCORE
============================================================

🔍 Extracting keywords from improved CV...
✓ Extracted 53 keywords from improved CV

📊 Calculating new ATS score...

============================================================
📈 SCORE IMPROVEMENT
============================================================
Initial Score: 68.33%
New Score:     91.67%
Improvement:   +23.34%

============================================================
ATS KEYWORD MATCH SCORE REPORT
============================================================

📊 NEW SCORE: 91.67%

Required Keywords Score: 93.33% (14/15)
Optional Keywords Score: 91.67% (11/12)

✅ MATCHED REQUIRED KEYWORDS:
  • python
  • javascript
  • react
  • node.js
  • docker
  • kubernetes
  • ci/cd
  • git
  • microservices
  • unit testing
  • ...

============================================================
📝 GENERATING LATEX AND PDF
============================================================

📝 Generating LaTeX code...
✓ LaTeX file saved: optimized_cv.tex

🔨 Compiling to PDF...
   Run 1/2...
   Run 2/2...
✅ PDF generated: /path/to/optimized_cv.pdf

============================================================
✅ CV IMPROVEMENT COMPLETE!
============================================================
Keywords added: 8
Score improvement: +23.34%
Output: /path/to/optimized_cv.pdf
============================================================
```

## How Keywords Are Added

The AI agent follows these strategies:

### 1. Skills Section
Technical skills, tools, and technologies are added directly:
```
Before: Languages: Python, JavaScript
After:  Languages: Python, JavaScript, TypeScript
        Tools: Git, Docker, Kubernetes
```

### 2. Professional Summary
Key methodologies and approaches are woven in naturally:
```
Before: Experienced software developer...
After:  Experienced software developer with expertise in 
        microservices architecture and CI/CD pipelines...
```

### 3. Work Experience
Relevant technologies are added to existing job descriptions:
```
Before: - Developed web applications using Python
After:  - Developed web applications using Python and Docker,
          implementing CI/CD pipelines with Jenkins
```

### 4. Projects Section
Technologies are mentioned in project descriptions:
```
Before: E-commerce Platform: Built using React and Node.js
After:  E-commerce Platform: Built using React, Node.js, Redis
        for caching, with Docker containerization
```

## Best Practices

### 1. Be Honest
- Only add keywords for skills you actually have
- The AI tries to place keywords honestly, but review the output
- Don't add technologies you've never used

### 2. Review Before Submitting
- Always review the generated PDF
- Ensure all additions are accurate
- Verify the placement makes sense

### 3. Customize Further
- The LaTeX file is editable
- Adjust formatting as needed
- Add or remove sections

### 4. Iterate
- Run analysis multiple times
- Try different job descriptions
- Refine your keyword strategy

## Troubleshooting

### LaTeX Compilation Fails

**Issue**: `moderncv.cls not found`

**Solution**:
```bash
# macOS
sudo tlmgr install moderncv

# Ubuntu
sudo apt-get install texlive-latex-extra

# Windows
# Install via MiKTeX Console
```

### Keywords Not Added

**Issue**: New score is the same as old score

**Possible causes**:
1. All keywords already present
2. AI couldn't find appropriate places
3. Keywords too generic

**Solution**: Review placement_notes.txt for details

### PDF Not Generated

**Issue**: LaTeX compilation errors

**Solution**:
1. Check the .tex file for special characters
2. Compile manually: `pdflatex optimized_cv.tex`
3. Check latex_error.log for details

## Advanced Usage

### Custom LaTeX Template

Edit `latex_cv_generator.py` to customize:
- Page margins
- Font sizes
- Colors
- Section styles

### Modify Keyword Placement Logic

Edit `keyword_placement_agent.py` to:
- Change placement strategies
- Adjust AI temperature
- Modify the prompt

### Change Scoring Weights

Edit `config.py`:
```python
REQUIRED_WEIGHT = 0.8  # 80% for required
OPTIONAL_WEIGHT = 0.2  # 20% for optional
```

## Tips for Best Results

1. **Use detailed job descriptions**: More context = better keyword placement
2. **Limit keywords**: Start with 5-10, not 20+
3. **Review AI suggestions**: The placement_notes.txt explains what was added
4. **Iterate**: Run multiple times with adjustments
5. **Customize output**: Edit the LaTeX file for final touches

## API Costs

Improvement workflow uses ~2-3 API calls:
1. Keyword rating (same as analysis)
2. CV section parsing
3. Keyword placement

**Estimated cost per improvement**:
- GPT-4: $0.03-0.05
- GPT-3.5-turbo: $0.002-0.005
- Claude-3-Sonnet: $0.01-0.02

Use `cost_estimator.py` for accurate estimates.
