# Analysis vs Improvement Mode

## Two Modes of Operation

### Analysis Mode (`main.py`)
**Purpose**: Evaluate your CV and identify gaps

**What it does**:
- ✅ Extracts keywords from CV and job description
- ✅ Rates keywords as required/optional
- ✅ Calculates ATS score
- ✅ Lists missing keywords
- ✅ Generates report

**What it doesn't do**:
- ❌ Doesn't modify your CV
- ❌ Doesn't generate new files
- ❌ Doesn't add keywords

**Use when**: You want to understand your CV's strengths and weaknesses

### Improvement Mode (`improve_cv.py`)
**Purpose**: Automatically optimize your CV for ATS

**What it does**:
- ✅ Everything from Analysis Mode, PLUS:
- ✅ Parses CV into sections
- ✅ Identifies which keywords to add
- ✅ Intelligently adds keywords to sections
- ✅ Recalculates new score
- ✅ Generates LaTeX CV
- ✅ Creates professional PDF

**Use when**: You want an optimized, ATS-friendly CV automatically

## Feature Comparison

| Feature | Analysis (`main.py`) | Improvement (`improve_cv.py`) |
|---------|---------------------|-------------------------------|
| Extract text from CV | ✅ | ✅ |
| Extract keywords | ✅ | ✅ |
| Rate keywords (AI) | ✅ | ✅ |
| Calculate ATS score | ✅ | ✅ |
| Generate report | ✅ | ✅ |
| Parse CV sections | ❌ | ✅ |
| Identify missing keywords | ✅ (report only) | ✅ (actionable) |
| Add keywords to CV | ❌ | ✅ |
| Generate LaTeX | ❌ | ✅ |
| Create PDF | ❌ | ✅ |
| Recalculate score | ❌ | ✅ |

## Command Comparison

### Analysis Mode
```bash
# Basic analysis
python main.py cv.pdf job_description.txt

# Save report
python main.py cv.pdf job_description.txt --output report.txt

# Without spaCy
python main.py cv.pdf job_description.txt --no-spacy
```

### Improvement Mode
```bash
# Full workflow (analyze + improve + generate PDF)
python improve_cv.py cv.pdf job_description.txt

# Just analyze (same as main.py)
python improve_cv.py cv.pdf job_description.txt --analyze-only

# Custom output
python improve_cv.py cv.pdf job_description.txt --output my_cv

# Limit keywords
python improve_cv.py cv.pdf job_description.txt --max-keywords 5
```

## Output Comparison

### Analysis Mode Output
```
📊 FINAL SCORE: 68.33%

✅ MATCHED REQUIRED KEYWORDS:
  • python
  • javascript
  • react

❌ MISSING REQUIRED KEYWORDS:
  • docker
  • kubernetes
  • ci/cd
```

### Improvement Mode Output
```
📊 INITIAL SCORE: 68.33%

[... analysis output ...]

🔧 IMPROVING CV
📑 Parsing CV into sections...
📝 Will add 6 keywords:
  • docker
  • kubernetes
  • ci/cd

📊 NEW SCORE: 91.67%
Score improvement: +23.34%

📝 Generated: optimized_cv.pdf
```

## When to Use Each Mode

### Use Analysis Mode When:
1. **Initial exploration**: Understanding where you stand
2. **Multiple job applications**: Comparing scores across different JDs
3. **Budget-conscious**: Fewer API calls (1 vs 3)
4. **Manual control**: You want to edit CV yourself
5. **Learning**: Understanding ATS mechanics

### Use Improvement Mode When:
1. **Need quick results**: Want an optimized CV fast
2. **First time optimizing**: Not sure how to add keywords
3. **Professional output needed**: Want a polished PDF
4. **Trust AI placement**: Comfortable with AI suggestions
5. **Time-constrained**: Need results in minutes, not hours

## Workflow Examples

### Conservative Workflow (Analysis First)
```bash
# 1. Analyze first
python main.py my_cv.pdf job_description.txt

# 2. Review results
cat report.txt

# 3. Decide if improvement needed
python improve_cv.py my_cv.pdf job_description.txt --max-keywords 5
```

### Aggressive Workflow (Direct Improvement)
```bash
# Go straight to improvement
python improve_cv.py my_cv.pdf job_description.txt
```

### Iterative Workflow
```bash
# Round 1: Analyze
python main.py my_cv.pdf job1.txt --output job1_analysis.txt

# Round 2: Improve for job 1
python improve_cv.py my_cv.pdf job1.txt --output cv_job1

# Round 3: Use improved CV for job 2
python improve_cv.py cv_job1.pdf job2.txt --output cv_job2
```

## Cost Comparison

### Analysis Mode
- **API Calls**: 1 (keyword rating)
- **Estimated Cost**: 
  - GPT-4: $0.01-0.02
  - GPT-3.5: $0.001-0.002
  - Claude-3-Sonnet: $0.005-0.01

### Improvement Mode
- **API Calls**: 3 (keyword rating + section parsing + keyword placement)
- **Estimated Cost**:
  - GPT-4: $0.04-0.06
  - GPT-3.5: $0.003-0.006
  - Claude-3-Sonnet: $0.015-0.025

**Cost Savings Tip**: Use `--analyze-only` flag with `improve_cv.py` for same cost as analysis mode

## Technical Differences

### Analysis Mode
- **Modules Used**: 5
  - cv_extractor
  - keyword_extractor
  - keyword_rating_agent
  - ats_scorer
  - main

- **Dependencies**: Core only
  - OpenAI or Anthropic
  - scikit-learn
  - spaCy (optional)

### Improvement Mode
- **Modules Used**: 10
  - All from Analysis Mode, PLUS:
  - cv_section_parser
  - missing_keyword_identifier
  - keyword_placement_agent
  - latex_cv_generator
  - pdf_generator

- **Dependencies**: Extended
  - Everything from Analysis Mode, PLUS:
  - LangChain
  - LaTeX distribution (pdflatex)
  - moderncv package

## Recommendation

**For most users**: Start with **Improvement Mode**

Why?
- Does everything Analysis Mode does
- Plus generates actionable improvements
- Creates professional PDF output
- Use `--analyze-only` if you just want analysis
- Marginal cost difference ($0.02-0.04 more)

**Exception**: Use Analysis Mode if:
- You don't have LaTeX installed
- You prefer manual CV editing
- Running bulk analyses (100+ CVs)
- Developing custom workflows

## Quick Decision Guide

```
Do you want a new, improved CV PDF?
│
├─ YES → Use improve_cv.py
│
└─ NO
   │
   Do you just want to see your score?
   │
   ├─ YES → Use improve_cv.py --analyze-only
   │         (or main.py)
   │
   └─ NO
      │
      Are you building custom tools?
      │
      └─ YES → Use main.py and modules separately
```
