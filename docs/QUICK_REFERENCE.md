# Quick Reference Guide

## Common Commands

### Installation & Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -e .

# Download spaCy model
python -m spacy download en_core_web_sm

# Setup environment file
cp .env.example .env
# Then edit .env with your API keys

# Quick automated setup (Linux/Mac only)
./quickstart.sh
```

### Running Analysis

```bash
# Basic analysis
python main.py cv.pdf job_description.txt

# Save report to file
python main.py cv.pdf job_description.txt --output report.txt

# Without spaCy (TF-IDF only)
python main.py cv.pdf job_description.txt --no-spacy

# With sample files
python main.py sample_cv.txt sample_job_description.txt
```

### Configuration & Testing

```bash
# View current configuration
python config.py

# Estimate costs for single analysis
python cost_estimator.py gpt-4 1
python cost_estimator.py claude-3-sonnet 1

# Compare model costs for 10 analyses
python cost_estimator.py compare 10

# Test individual modules (Python REPL)
python -c "from cv_extractor import CVExtractor; print(CVExtractor.extract('sample_cv.txt')[:100])"
```

### Help & Documentation

```bash
# View command-line help
python main.py --help

# View available options
python main.py -h
```

## Module Usage Examples

### Using CV Extractor

```python
from cv_extractor import CVExtractor

# Extract from PDF
text = CVExtractor.extract_from_pdf('resume.pdf')

# Extract from text file
text = CVExtractor.extract_from_text('resume.txt')

# Auto-detect format
text = CVExtractor.extract('resume.pdf')
```

### Using Keyword Extractor

```python
from keyword_extractor import KeywordExtractor

# Initialize
extractor = KeywordExtractor(use_spacy=True)

# Extract keywords
keywords = extractor.extract_keywords(text, max_keywords=30)

# Compare CV and JD keywords
result = extractor.compare_keywords(cv_text, jd_text)
print(f"Matched: {result['match_count']}/{result['total_jd_keywords']}")
```

### Using Keyword Rating Agent

```python
from keyword_rating_agent import KeywordRatingAgent

# Initialize (requires .env file with API keys)
agent = KeywordRatingAgent()

# Rate keywords
keywords = ['python', 'javascript', 'docker', 'aws']
rated = agent.rate_keywords(keywords, job_description_text)

print(f"Required: {rated['required']}")
print(f"Optional: {rated['optional']}")
```

### Using ATS Scorer

```python
from ats_scorer import ATSScorer

# Calculate score
score = ATSScorer.calculate_keyword_match_score(
    cv_keywords=['python', 'javascript', 'react'],
    required_keywords=['python', 'javascript', 'sql'],
    optional_keywords=['react', 'docker']
)

print(f"Final Score: {score['final_score']}%")

# Generate report
report = ATSScorer.generate_report(score)
print(report)
```

## Environment Variables

Edit `.env` file with these variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
AI_PROVIDER=openai
AI_MODEL=gpt-4

# OR Anthropic Configuration
ANTHROPIC_API_KEY=your-key-here
AI_PROVIDER=anthropic
AI_MODEL=claude-3-sonnet-20240229
```

## Supported File Formats

- **CV Files**: `.pdf`, `.txt`
- **Job Description**: `.txt` (recommended)

## Model Options

### OpenAI Models
- `gpt-4` - Highest quality, most expensive
- `gpt-4-turbo` - Fast and capable
- `gpt-3.5-turbo` - Budget-friendly option

### Anthropic Models
- `claude-3-opus-20240229` - Highest quality
- `claude-3-sonnet-20240229` - Balanced (recommended)
- `claude-3-haiku-20240307` - Fastest and cheapest

## Troubleshooting Commands

```bash
# Check if Python is installed
python --version

# Check if pip is installed
pip --version

# List installed packages
pip list

# Check if spaCy model is installed
python -c "import spacy; spacy.load('en_core_web_sm')"

# Verify environment file
cat .env

# Test PDF extraction
python -c "from cv_extractor import CVExtractor; print('PDF extraction works!')"

# Test API connection (OpenAI)
python -c "from openai import OpenAI; client = OpenAI(); print('OpenAI connected!')"

# Test API connection (Anthropic)
python -c "from anthropic import Anthropic; client = Anthropic(); print('Anthropic connected!')"
```

## File Structure

```
Your working directory:
├── my_cv.pdf              # Your CV file
├── job_description.txt    # Job description
└── reports/              # Optional: output directory
    └── analysis.txt      # Generated report
```

## Exit Codes

- `0` - Success (score >= 50%)
- `1` - Error or low score (< 50%)

## Performance Tips

1. **Use cheaper models for bulk analysis**: `gpt-3.5-turbo` or `claude-3-haiku`
2. **Disable spaCy if not needed**: Use `--no-spacy` flag
3. **Batch similar jobs**: Reuse extracted CV text
4. **Monitor API costs**: Use `cost_estimator.py` first

## Getting Help

1. Check [README.md](README.md) for overview
2. Check [SETUP.md](SETUP.md) for installation help
3. Check [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for technical details
4. Run `python main.py --help` for command-line options

## Example Workflow

```bash
# 1. Setup (one time)
cp .env.example .env
# Edit .env with API key
pip install -e .
python -m spacy download en_core_web_sm

# 2. Estimate costs
python cost_estimator.py compare 5

# 3. Run analysis
python main.py my_cv.pdf job_description.txt --output report.txt

# 4. Review report
cat report.txt

# 5. Update CV based on missing keywords
# Edit your CV...

# 6. Re-analyze
python main.py my_cv_v2.pdf job_description.txt --output report_v2.txt
```

## Advanced Usage

### Batch Processing Multiple Jobs

```bash
#!/bin/bash
for jd in job_descriptions/*.txt; do
    output="reports/$(basename "$jd" .txt)_report.txt"
    python main.py my_cv.pdf "$jd" --output "$output"
done
```

### Custom Scoring Weights

Edit `config.py`:
```python
REQUIRED_WEIGHT = 0.8  # 80% for required
OPTIONAL_WEIGHT = 0.2  # 20% for optional
```

### Different AI Models for Testing

```bash
# Test with GPT-3.5 (cheaper)
AI_MODEL=gpt-3.5-turbo python main.py cv.pdf jd.txt

# Test with Claude Haiku (cheapest)
AI_PROVIDER=anthropic AI_MODEL=claude-3-haiku-20240307 python main.py cv.pdf jd.txt
```
