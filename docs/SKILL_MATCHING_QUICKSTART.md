# Quick Start: Skill Matching System

## Overview

The ATS CV Maker now includes an intelligent **Skill Matching System** that analyzes the skills in your CV and matches them against the job description. This works alongside the keyword matching system to give you a complete assessment of your fit.

## What's New

### New Modules
- **`skill_extractor.py`**: LLM-powered skill extraction
- **`skill_normalizer.py`**: Intelligent skill normalization and standardization
- **`skill_matcher.py`**: Fuzzy matching and skill score calculation
- **`ats_scorer.py`** (updated): Now includes skill score calculation

### New Scripts
- **`skill_score.py`**: Standalone skill analysis tool
- **`skill_score_orchestration.py`**: Programmatic skill analysis workflow

## Quick Usage

### Option 1: Skill Analysis Only

```bash
python skill_score.py examples/sample_cv.txt examples/sample_job_description.txt
```

**Output**: Skill match score (0-100) based on how many job description skills are in your CV.

### Option 2: Complete ATS Analysis (Keyword + Skill)

```bash
python main.py examples/sample_cv.txt examples/sample_job_description.txt
```

**Output**:
- Keyword match score
- Skill match score
- Combined score (average of both)

### Option 3: Programmatic Access

```python
from skill_score_orchestration import analyze_skills

results = analyze_skills(
    cv_file='examples/sample_cv.txt',
    jd_file='examples/sample_job_description.txt',
    normalize=True
)

print(f"Skill Match Score: {results['skill_match_score']:.1f}/100")
```

## How It Works

### 1. Skill Extraction
Your CV and job description are analyzed by an LLM to extract:
- Programming languages
- Frameworks and libraries
- Tools and platforms
- Methodologies
- Soft skills
- Domain expertise

### 2. Skill Normalization
The extracted skills are intelligently normalized:
- "PyTorch" + "TensorFlow" → "Deep Learning Framework"
- "React" + "Vue" + "Angular" → "Frontend Framework"
- Unique skills (like "Java") remain unchanged

**Key Rule**: Only skills that benefit from normalization are normalized.

### 3. Skill Matching
CV skills are matched against job description skills using fuzzy matching:
- Handles typos and variations
- Normalizes for comparison
- Returns similarity scores

### 4. Score Calculation
$$\text{Skill Match Score} = \frac{\text{Matched Skills}}{\text{Total JD Skills}} \times 100$$

**Example**: If the job requires 10 skills and your CV has 7 of them:
- Score = (7 / 10) × 100 = **70/100**

## Common Commands

```bash
# Skill analysis with details
python skill_score.py cv.pdf jd.txt --verbose

# Skip normalization (faster, fewer API calls)
python skill_score.py cv.pdf jd.txt --no-normalize

# Save detailed report
python skill_score.py cv.pdf jd.txt --output skill_report.txt

# Full ATS analysis
python main.py cv.pdf jd.txt

# Full analysis without skill component
python main.py cv.pdf jd.txt --no-skills

# Full analysis with skill report
python main.py cv.pdf jd.txt --output ats_report.txt
```

## Score Interpretation

| Score | Meaning | Action |
|-------|---------|--------|
| 80-100 | Excellent skill match | Strong candidate |
| 60-79 | Good skill match | Competitive candidate |
| 40-59 | Moderate skill match | Consider upskilling |
| 0-39 | Low skill match | May need training |

## API Costs

Each skill analysis costs approximately:
- **GPT-4**: $0.08-0.12 per analysis
- **GPT-3.5-turbo**: $0.01-0.02 per analysis
- **Claude 3**: $0.02-0.04 per analysis

**Tip**: Use `--no-normalize` to skip 2 API calls and save ~50% cost.

## Configuration

Set in `.env`:

```bash
# AI Provider (openai or anthropic)
AI_PROVIDER=openai

# Model (gpt-4, gpt-3.5-turbo, claude-3-sonnet-20240229)
AI_MODEL=gpt-4

# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

## Examples

### Example 1: Check Skill Fit
```bash
python skill_score.py my_cv.pdf data_engineer_jd.txt
```

Output shows:
- 15 skills extracted from CV
- 12 skills in job description
- 9 matches found
- **Skill Score: 75/100** ✅

### Example 2: Full Assessment
```bash
python main.py my_cv.pdf senior_dev_jd.txt
```

Output shows:
- Keyword Match Score: 68/100
- Skill Match Score: 75/100
- Combined Score: 71.5/100 ✅

### Example 3: Detailed Analysis with Report
```bash
python skill_score.py my_cv.pdf jd.txt --verbose --output detailed_report.txt
```

Produces:
- Console: Step-by-step analysis with all details
- File: Saved report for review

## Troubleshooting

**Q: Getting low skill scores?**
A: Use `--verbose` to see which skills matched and which didn't. The fuzzy matcher might be missing close matches (try adjusting similarity threshold in code).

**Q: Skills not being extracted?**
A: Ensure skills are explicitly mentioned in your CV (not just implied). Use standard names (e.g., "Python" not "py").

**Q: Too many API calls costing money?**
A: Use `--no-normalize` to skip normalization and save 50% of API calls.

**Q: Different results each time?**
A: LLM responses vary slightly. Results should be similar but not identical each run.

## Next Steps

1. **Install Dependencies**: `uv sync`
2. **Run Your First Analysis**: `python skill_score.py examples/sample_cv.txt examples/sample_job_description.txt`
3. **Review Results**: Check the skill match score and matched/unmatched skills
4. **Improve CV**: Add missing skills from job description to your CV
5. **Retrace**: Run again to verify improvements

## Documentation

See [SKILL_MATCHING.md](SKILL_MATCHING.md) for detailed documentation including:
- API reference
- Advanced usage
- Customization options
- Performance tuning
- Future enhancements

## Support

For issues or questions:
1. Check [SKILL_MATCHING.md](SKILL_MATCHING.md) troubleshooting section
2. Review the verbose output: `--verbose`
3. Check your `.env` configuration
4. Ensure all dependencies are installed: `uv sync`
