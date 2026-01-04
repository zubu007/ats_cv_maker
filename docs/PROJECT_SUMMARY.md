# ATS CV Maker - Project Summary

## Overview

An intelligent ATS (Applicant Tracking System) scoring tool that uses AI to analyze CVs against job descriptions. The system extracts keywords, rates them as required/optional, and calculates a comprehensive match score.

## Project Structure

```
ats_cv_maker/
├── main.py                      # Main orchestration script
├── cv_extractor.py             # CV text extraction (PDF, TXT)
├── keyword_extractor.py        # Keyword extraction (TF-IDF + spaCy)
├── keyword_rating_agent.py     # AI agent for rating keywords
├── ats_scorer.py              # Score calculation and reporting
├── cost_estimator.py          # API cost estimation tool
├── pyproject.toml             # Project dependencies
├── requirements.txt           # Alternative dependency list
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── README.md                 # Main documentation
├── SETUP.md                  # Detailed setup guide
├── quickstart.sh             # Automated setup script
├── sample_cv.txt             # Sample CV for testing
└── sample_job_description.txt # Sample job description
```

## Key Features

### 1. CV Text Extraction (`cv_extractor.py`)
- Supports PDF and plain text files
- Automatic format detection
- Error handling for corrupted files

### 2. Keyword Extraction (`keyword_extractor.py`)
- **TF-IDF vectorization**: Identifies important terms based on frequency
- **spaCy NLP**: Extracts noun phrases and named entities
- **Customizable**: Adjustable n-grams (1-3 words) and keyword counts
- **Smart preprocessing**: Handles technical terms (C++, C#, etc.)

### 3. AI-Powered Keyword Rating (`keyword_rating_agent.py`)
- **Multi-provider support**: OpenAI (GPT) or Anthropic (Claude)
- **Intelligent categorization**: Rates keywords as required or optional
- **Context-aware**: Analyzes full job description for context
- **Fallback handling**: Graceful degradation if AI call fails

### 4. ATS Scoring (`ats_scorer.py`)
- **Weighted scoring**: 70% required, 30% optional keywords
- **Partial matching**: Fuzzy keyword matching algorithm
- **Detailed reports**: Shows matched and missing keywords
- **Actionable insights**: Clear breakdown of score components

### 5. Cost Estimation (`cost_estimator.py`)
- **Price comparison**: Compare costs across different AI models
- **Usage projection**: Estimate costs for multiple analyses
- **Budget planning**: Helps users choose cost-effective models

## Scoring Algorithm

```python
Score = (matched_required / total_required) × 0.7 + (matched_optional / total_optional) × 0.3
```

### Components:
- **Required Keywords** (70% weight): Must-have skills from job description
- **Optional Keywords** (30% weight): Preferred/nice-to-have skills
- **Matching Logic**: Exact and partial matches supported

### Keyword Rating Logic:
The AI agent analyzes job descriptions to identify:
- **Required**: Terms with "required", "must have", "essential"
- **Optional**: Terms with "preferred", "nice to have", "bonus"
- **Context-aware**: Considers emphasis and position in text

## Usage Examples

### Basic Analysis
```bash
python main.py my_cv.pdf job_description.txt
```

### With Report Output
```bash
python main.py my_cv.pdf job_description.txt --output report.txt
```

### Without spaCy (TF-IDF only)
```bash
python main.py my_cv.pdf job_description.txt --no-spacy
```

### Estimate Costs
```bash
# Single analysis
python cost_estimator.py gpt-4 1

# Compare models
python cost_estimator.py compare 10
```

## Sample Output

```
🚀 Starting ATS CV Analysis...
============================================================

📄 Extracting text from CV...
✓ Extracted 1542 characters from CV

📋 Extracting text from job description...
✓ Extracted 892 characters from job description

🔍 Extracting keywords using TF-IDF and NLP...
✓ Extracted 45 keywords from CV
✓ Extracted 38 keywords from job description

🤖 Rating keywords as required/optional using AI agent...
✓ Identified 15 required keywords
✓ Identified 12 optional keywords

📊 Calculating ATS keyword match score...

============================================================
ATS KEYWORD MATCH SCORE REPORT
============================================================

📊 FINAL SCORE: 78.50%

Required Keywords Score: 73.33% (11/15)
Optional Keywords Score: 91.67% (11/12)

✅ MATCHED REQUIRED KEYWORDS:
  • agile
  • javascript
  • node.js
  • postgresql
  • python
  • react
  • restful api
  • scrum
  • software development
  • sql
  • version control

❌ MISSING REQUIRED KEYWORDS:
  • bachelor degree computer science
  • git
  • mysql
  • problem solving

...
```

## Technology Stack

- **Python 3.11+**: Core language
- **PyPDF2**: PDF text extraction
- **scikit-learn**: TF-IDF vectorization
- **spaCy**: NLP and noun phrase extraction
- **OpenAI/Anthropic**: AI-powered keyword rating
- **python-dotenv**: Environment variable management

## API Requirements

You need ONE of the following:
- **OpenAI API key**: For GPT models
- **Anthropic API key**: For Claude models

### Recommended Models:
- **Budget-friendly**: `gpt-3.5-turbo` or `claude-3-haiku`
- **Balanced**: `claude-3-sonnet` (recommended)
- **High-quality**: `gpt-4` or `claude-3-opus`

## Installation

### Quick Start (Linux/Mac)
```bash
./quickstart.sh
```

### Manual Setup
```bash
# Install dependencies
pip install -e .

# Download spaCy model
python -m spacy download en_core_web_sm

# Configure API keys
cp .env.example .env
# Edit .env with your API keys

# Run sample
python main.py sample_cv.txt sample_job_description.txt
```

## Extensibility

The modular design allows easy extension:

1. **Add new extractors**: Extend `CVExtractor` for DOCX, HTML, etc.
2. **Custom scoring**: Modify `ATSScorer` for different formulas
3. **Additional metrics**: Add skill match, experience match, etc.
4. **Alternative AI providers**: Add new providers to `KeywordRatingAgent`

## Future Enhancements

Planned features (as per original design):
- ✅ Keyword match score (COMPLETED)
- ⏳ Skill match score
- ⏳ Experience match score
- ⏳ Recency score
- ⏳ Education match score
- ⏳ Semantic relevance score

## Performance Considerations

- **Token usage**: ~800-1000 tokens per analysis
- **API cost**: $0.001-0.03 per analysis (model-dependent)
- **Processing time**: 2-5 seconds per analysis
- **Batch processing**: Can analyze multiple CVs sequentially

## Security & Privacy

- **Local processing**: CV text extracted locally
- **API calls**: Only keywords and job description sent to AI
- **No storage**: No data stored on external servers
- **.env file**: Keep API keys secure and private

## Troubleshooting

Common issues and solutions documented in [SETUP.md](SETUP.md):
- Missing API keys
- spaCy model not found
- PDF extraction errors
- Rate limiting

## License

MIT License - Free for personal and commercial use.

## Contributing

Contributions welcome! Areas for improvement:
- Additional file format support
- More sophisticated matching algorithms
- Batch processing capabilities
- Web interface
- Additional scoring metrics

## Credits

Created as an ATS-friendly CV scoring system to help job seekers optimize their resumes for Applicant Tracking Systems.
