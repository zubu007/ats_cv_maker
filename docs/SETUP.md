# Setup Guide for ATS CV Maker

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- An API key from either OpenAI or Anthropic

## Step-by-Step Setup

### 1. Install Python Dependencies

```bash
# Option A: Using pip directly
pip install -e .

# Option B: Using a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### 2. Download spaCy Language Model

For better keyword extraction, install the spaCy English model:

```bash
python -m spacy download en_core_web_sm
```

Note: You can skip this step and use `--no-spacy` flag if you want to use TF-IDF only.

### 3. Configure API Keys

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API credentials:

#### For OpenAI (GPT models):
```bash
OPENAI_API_KEY=sk-your-actual-key-here
AI_PROVIDER=openai
AI_MODEL=gpt-4  # or gpt-3.5-turbo for lower cost
```

#### For Anthropic (Claude models):
```bash
ANTHROPIC_API_KEY=your-actual-key-here
AI_PROVIDER=anthropic
AI_MODEL=claude-3-sonnet-20240229
```

### 4. Verify Installation

Test the installation with sample files:

```bash
python main.py sample_cv.txt sample_job_description.txt
```

You should see output similar to:
```
🚀 Starting ATS CV Analysis...
============================================================

📄 Extracting text from CV...
✓ Extracted 1542 characters from CV

📋 Extracting text from job description...
✓ Extracted 892 characters from job description

...

📊 FINAL SCORE: 78.50%
```

## Troubleshooting

### Issue: "OPENAI_API_KEY not found in environment variables"

**Solution**: Make sure you've created a `.env` file and added your API key. The `.env` file should be in the same directory as `main.py`.

### Issue: "spaCy model 'en_core_web_sm' not found"

**Solution**: 
```bash
python -m spacy download en_core_web_sm
```

Or run with `--no-spacy` flag:
```bash
python main.py cv.pdf job_description.txt --no-spacy
```

### Issue: "Error extracting text from PDF"

**Solution**: Make sure your PDF is not encrypted or password-protected. Try converting it to a text file first.

### Issue: Rate limiting or API errors

**Solution**: 
- Check your API key is valid and has available credits
- For OpenAI: You may need to add payment method to your account
- Try using a different model (e.g., `gpt-3.5-turbo` instead of `gpt-4`)

## Getting API Keys

### OpenAI
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API keys section
4. Create a new API key
5. Add payment method (required for API access)

### Anthropic
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API keys section
4. Create a new API key

## Using the Quick Start Script (Linux/Mac)

For a fully automated setup, run:

```bash
./quickstart.sh
```

This script will:
- Create virtual environment
- Install all dependencies
- Download spaCy model
- Run a sample analysis

## Next Steps

After setup, try:
1. Analyze your own CV against a real job description
2. Experiment with different AI models
3. Save reports for comparison
4. Adjust keyword extraction parameters

For more information, see the main [README.md](README.md).
