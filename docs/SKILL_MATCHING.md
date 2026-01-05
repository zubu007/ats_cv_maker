# Skill Matching & Scoring System

## Overview

The skill matching system is a new addition to the ATS CV Maker that provides intelligent skill analysis and matching between your CV and a job description. It works alongside the keyword matching system to give you a comprehensive view of your fit for a position.

## Components

### 1. Skill Extractor (`skill_extractor.py`)

**Purpose**: Extracts professional skills from text using LLM intelligence.

**Key Features**:
- Extracts all types of skills: technical, tools, frameworks, soft skills
- Structured output using Pydantic models
- Supports both CV and job description analysis
- Can categorize skills by type (optional)

**API**:
```python
from src.ats_cv_maker.skill_extractor import SkillExtractor

extractor = SkillExtractor()

# Extract from CV
cv_skills = extractor.extract_skills_from_cv(cv_text)
# Returns: SkillList with .skills = ["Python", "React", ...]

# Extract from Job Description
jd_skills = extractor.extract_skills_from_job_description(jd_text)
```

### 2. Skill Normalizer (`skill_normalizer.py`)

**Purpose**: Intelligently normalizes and standardizes skill names.

**Key Features**:
- LLM-powered normalization decisions
- Only normalizes when beneficial (not all skills)
- Merges original and normalized skills
- Provides reasoning for each normalization decision

**Normalization Examples**:
- "PyTorch" + "TensorFlow" → Both get mapped to "Deep Learning Framework" (if both exist)
- "React" + "Vue" + "Angular" → All map to "Frontend Framework" (if multiple exist)
- "Java" → Kept as-is (NO normalization for programming languages)
- "AWS" + "Azure" + "GCP" → All map to "Cloud Platform" (if multiple exist)

**Important Rules**:
- Does NOT normalize unique or distinctive skills
- Does NOT normalize programming languages
- Does NOT normalize well-known brand names (unless many competitors)
- Asks: "Does normalizing this skill help with job matching?"

**API**:
```python
from src.ats_cv_maker.skill_normalizer import SkillNormalizer

normalizer = SkillNormalizer()

# Normalize skills
normalized = normalizer.normalize_skills(skill_list, context="cv")
# Returns: NormalizedSkillList with decisions for each skill

# Merge original and normalized
merged_skills, mappings = normalizer.merge_skills(
    original_skills, 
    normalized
)
```

### 3. Skill Matcher (`skill_matcher.py`)

**Purpose**: Matches CV skills with job description skills using fuzzy matching.

**Key Features**:
- Fuzzy string matching with configurable threshold (default 0.8)
- Normalizes skill names for comparison (lowercase, special char removal)
- Detailed matching report with similarity scores
- Calculates skill match score

**Matching Algorithm**:
1. Normalizes both CV and JD skill names for comparison
2. Uses `SequenceMatcher` for fuzzy matching
3. Returns best match if similarity >= threshold
4. Calculates: (matched_skills / total_jd_skills) * 100

**API**:
```python
from src.ats_cv_maker.skill_matcher import SkillMatcher

matcher = SkillMatcher(similarity_threshold=0.8)

# Match skills
results = matcher.match_skills(cv_skills, jd_skills, verbose=True)

# Calculate score
score = matcher.calculate_skill_score(
    matched_skills_count=5,
    jd_skills_count=10
)
# Returns: 50.0 (5/10 * 100)
```

### 4. ATS Scorer Updates (`ats_scorer.py`)

**New Method**: `calculate_skill_match_score()`

```python
from src.ats_cv_maker.ats_scorer import ATSScorer

scorer = ATSScorer()

# Calculate skill score
skill_score_data = scorer.calculate_skill_match_score(
    matched_skills=5,
    total_jd_skills=10
)
# Returns: {
#     'skill_match_score': 50.0,
#     'matched_skills': 5,
#     'total_jd_skills': 10,
#     'match_percentage': 50.0
# }
```

**Updated Report Generation**:
```python
# Generate report with both keyword and skill scores
report = scorer.generate_report(
    score_data=keyword_results,
    skill_score_data=skill_score_results,
    combined_score=72.5
)
```

## Workflows

### Workflow 1: Skill Analysis Only

```bash
python skill_score.py examples/sample_cv.txt examples/sample_job_description.txt
```

**Output**:
- Step-by-step extraction and normalization
- Skill matching results with similarity scores
- Final skill match score (0-100)
- Matched and unmatched skills

**Options**:
```bash
# Skip normalization (faster, less API calls)
python skill_score.py ... --no-normalize

# Verbose output with detailed matching info
python skill_score.py ... --verbose

# Save report to file
python skill_score.py ... --output report.txt
```

### Workflow 2: Complete ATS Analysis (Keyword + Skill)

```bash
python main.py examples/sample_cv.txt examples/sample_job_description.txt
```

**Output**:
- Keyword match score (0-100)
- Skill match score (0-100)
- Combined score (average of both)
- Detailed matching details for both

**Options**:
```bash
# Skip skill analysis
python main.py ... --no-skills

# Skip skill normalization (faster)
python main.py ... --no-normalize-skills

# No spaCy for keyword extraction
python main.py ... --no-spacy

# Save full report
python main.py ... --output full_report.txt
```

### Workflow 3: Full Score Orchestration

For programmatic use:

```python
from skill_score_orchestration import analyze_skills

results = analyze_skills(
    cv_file='examples/sample_cv.txt',
    jd_file='examples/sample_job_description.txt',
    verbose=True,
    normalize=True
)

print(f"CV Skills: {len(results['cv_skills'])}")
print(f"Skill Match Score: {results['skill_match_score']:.1f}/100")
print(f"Matched Skills: {results['total_matched']}/{results['total_jd_skills']}")
```

## Scoring Formula

### Skill Match Score

$$\text{Skill Match Score} = \frac{\text{Matched Skills}}{\text{Total JD Skills}} \times 100$$

**Example**:
- Job description requires: 10 unique skills
- Your CV matches: 7 of those skills
- Score: (7 / 10) * 100 = **70.0/100**

### Combined Score (Keyword + Skill)

When both scores are available:

$$\text{Combined Score} = \frac{\text{Keyword Score} + \text{Skill Score}}{2}$$

**Example**:
- Keyword Match Score: 75
- Skill Match Score: 65
- Combined: (75 + 65) / 2 = **70.0/100**

## Score Interpretation

| Score | Interpretation | Recommendation |
|-------|----------------|-----------------|
| 80-100 | Excellent match | Strong fit, apply with confidence |
| 60-79 | Good match | Good fit, consider minor improvements |
| 40-59 | Moderate match | Some gaps, consider skill development |
| 0-39 | Low match | Significant gaps, may need major prep |

## Key Differences from Keyword Matching

| Aspect | Keyword Matching | Skill Matching |
|--------|-----------------|-----------------|
| **What's Matched** | Specific keywords/terms | Skills, tools, frameworks, languages |
| **Matching Type** | Exact + partial | Fuzzy (with similarity threshold) |
| **Weighting** | Required (70%) / Optional (30%) | Uniform (all job skills equal) |
| **Normalization** | None | Intelligent (LLM-powered) |
| **Use Case** | Keyword density for ATS systems | Actual skill fit assessment |
| **Score** | 0-100 (weighted) | 0-100 (proportional match) |

## Implementation Details

### Skill Extraction Process

1. **Input**: Raw CV or job description text
2. **LLM Analysis**: Comprehensive extraction of all skills
3. **Output**: Structured list of skills with categories

**Extracted Skill Types**:
- Programming languages
- Frameworks and libraries
- Tools and platforms
- Databases
- Cloud services
- Methodologies
- Soft skills
- Domain expertise

### Normalization Logic

**Decision Tree**:
1. Are there similar alternatives in the list?
   - YES: Consider normalization
   - NO: Keep as-is

2. Would normalizing help with job matching?
   - YES: Create normalized category
   - NO: Keep original skill name

3. Is this a unique or well-known brand?
   - YES: Keep as-is (unless many competitors exist)
   - NO: May normalize

### Matching Algorithm

1. **Normalization**: Both skill lists normalized for comparison
   - Convert to lowercase
   - Remove special characters
   - Remove extra whitespace

2. **Comparison**: SequenceMatcher calculates similarity ratio
   - Compares each CV skill with all JD skills
   - Selects best match if similarity >= threshold (0.8)

3. **Scoring**: Calculate percentage based on JD skills
   - Only JD skills count for total (you need to match what they're looking for)

## API Examples

### Complete Skill Analysis

```python
from src.ats_cv_maker.cv_extractor import CVExtractor
from src.ats_cv_maker.skill_extractor import SkillExtractor
from src.ats_cv_maker.skill_normalizer import SkillNormalizer
from src.ats_cv_maker.skill_matcher import SkillMatcher

# Extract text
extractor = CVExtractor()
cv_text = extractor.extract('cv.pdf')
jd_text = extractor.extract_from_text('jd.txt')

# Extract skills
skill_extractor = SkillExtractor()
cv_skills = skill_extractor.extract_skills_from_cv(cv_text).skills
jd_skills = skill_extractor.extract_skills_from_job_description(jd_text).skills

# Normalize
normalizer = SkillNormalizer()
norm_cv = normalizer.normalize_skills(cv_skills)
norm_jd = normalizer.normalize_skills(jd_skills)

cv_merged, _ = normalizer.merge_skills(cv_skills, norm_cv)
jd_merged, _ = normalizer.merge_skills(jd_skills, norm_jd)

# Match
matcher = SkillMatcher()
results = matcher.match_skills(cv_merged, jd_merged)

score = matcher.calculate_skill_score(
    results['total_matched'],
    results['total_jd_skills']
)

print(f"Skill Match Score: {score:.1f}/100")
```

## Performance Considerations

### API Calls

- **Skill Extraction**: 2 API calls (CV + JD)
- **Skill Normalization**: 2 API calls (CV + JD)
- **Total for Full Workflow**: 4 API calls

**Cost Estimation** (using GPT-4):
- Per analysis: ~$0.08-0.12
- Per 100 analyses: ~$8-12

### Speed

- **Extraction**: ~5-10 seconds per document
- **Normalization**: ~5-10 seconds per document
- **Matching**: <1 second (local processing)
- **Total**: ~20-40 seconds per analysis

### Optimizations

```bash
# Skip normalization (saves 2 API calls)
python skill_score.py ... --no-normalize

# Use faster model
# Set in .env: AI_MODEL=gpt-3.5-turbo
```

## Troubleshooting

### Issue: Skill extraction missing skills

**Solution**: Skills are based on LLM understanding. Try:
- Providing more context in CV (full job titles, detailed descriptions)
- Ensure skills are explicitly mentioned (not just implied)
- Check if skill format is standard (e.g., "Python" not "py")

### Issue: Normalization not working as expected

**Solution**: Normalization only happens when beneficial:
- Ensure there are multiple similar skills to trigger normalization
- Check if skills are unique/distinctive (won't normalize)
- Verify skills aren't programming languages (kept as-is)

### Issue: Low skill match score

**Solutions**:
- Use `--verbose` flag to see which skills matched
- Check job description for required skills you're missing
- Verify skill names match (fuzzy matching with 0.8 threshold)
- Try --no-normalize to use original skill names

## Future Enhancements

1. **Skill Proficiency Levels**: Extract skill proficiency (beginner, intermediate, expert)
2. **Experience Weighting**: Weight skills by years of experience
3. **Skill Relationships**: Map related skills (e.g., Python → Data Science ecosystem)
4. **Learning Paths**: Suggest skills to learn for better fit
5. **Historical Matching**: Track how skills evolve in job market over time

## Configuration

Set in `.env` file:

```bash
# AI Provider
AI_PROVIDER=openai
# AI_PROVIDER=anthropic

# Model selection
AI_MODEL=gpt-4
# AI_MODEL=gpt-3.5-turbo
# AI_MODEL=claude-3-sonnet-20240229

# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

## References

- [Skill Extractor Source](src/ats_cv_maker/skill_extractor.py)
- [Skill Normalizer Source](src/ats_cv_maker/skill_normalizer.py)
- [Skill Matcher Source](src/ats_cv_maker/skill_matcher.py)
- [Skill Score Script](skill_score.py)
- [ATS Scorer Updates](src/ats_cv_maker/ats_scorer.py)
