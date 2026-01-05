# Experience Relevance Score

## Overview

The **Experience Relevance Score** measures how relevant a candidate's past work roles are to the target job position. It evaluates the match between a candidate's professional background and the requirements of a specific job opening.

## Purpose

- Assess whether candidates have worked in roles that translate to the target position
- Evaluate seniority progression and alignment
- Measure total time spent in relevant experience
- Provide a comprehensive view of career fit beyond just skills and keywords

## Components

The experience relevance score is calculated using three weighted components:

### 1. Title Similarity (50% weight)

**Description:** Measures how semantically similar past job titles are to the target job title.

**Algorithm:**
- Uses sentence embeddings (SentenceTransformers) for semantic similarity
- Compares each CV job title against the target job title
- Calculates cosine similarity (0-1 scale)
- Falls back to string similarity if embeddings are unavailable

**Examples:**
- "Backend Engineer" vs "Backend Developer" → High similarity (0.85+)
- "Software Developer" vs "DevOps Engineer" → Moderate similarity (0.50-0.70)
- "Accountant" vs "Software Engineer" → Low similarity (0.10-0.30)

### 2. Seniority Match (30% weight)

**Description:** Evaluates how well the candidate's seniority levels align with the target role's requirements.

**Seniority Levels:**
- **Junior:** Early-career roles, typically 0-2 years in field
- **Mid:** Standard full-time roles, typically 2-5 years experience
- **Senior:** Advanced roles, typically 5+ years experience  
- **Lead:** Leadership/staff roles, typically 8+ years experience

**Scoring:**
- Exact match: 1.0 (100%)
- 1 level difference: 0.85 (85%) - e.g., Mid to Senior
- 2 levels difference: 0.6 (60%) - e.g., Junior to Senior
- 3 levels difference: 0.3 (30%) - e.g., Junior to Lead

**Examples:**
- CV has "Senior Developer", target is "Senior Engineer" → 1.0 match
- CV has "Mid-level Engineer", target is "Senior Engineer" → 0.85 match
- CV has "Junior Developer", target is "Senior Engineer" → 0.3 match

### 3. Duration Factor (20% weight)

**Description:** Rewards candidates with more years of experience in relevant roles, using logarithmic scaling to diminish returns beyond 8 years.

**Formula:**
```
score = ln(years + 1) / ln(9)  [capped at 1.0]
```

**Duration Mapping:**
- 0 years: 0.0
- 1 year: 0.2
- 2 years: 0.4
- 3 years: 0.6
- 4 years: 0.73
- 5 years: 0.83
- 8+ years: 1.0

**Examples:**
- Candidate with 2 years as "Backend Engineer" → 0.4 duration score
- Candidate with 5 years as "Backend Engineer" → 0.83 duration score
- Candidate with 10 years as "Backend Engineer" → 1.0 duration score (capped)

## Final Score Formula

```
experience_relevance_score = (title_similarity * 0.5) + (seniority_match * 0.3) + (duration_factor * 0.2)
```

**Result Range:** 0-100%

### Score Interpretation

| Score | Interpretation | Recommendation |
|-------|-----------------|-----------------|
| 80-100% | Excellent fit | Strong candidate with highly relevant experience |
| 60-80% | Good fit | Candidate has relevant experience with some gaps |
| 40-60% | Moderate fit | Candidate has some relevant experience |
| 20-40% | Limited fit | Candidate has minimal relevant experience |
| 0-20% | Poor fit | Little to no relevant experience for this role |

## Job Title Normalization

To ensure consistent comparison, job titles are normalized using the `JobTitleNormalizer` agent:

### Normalization Process

1. **Extract Core Role:** Remove seniority indicators and extra words
   - "Senior Backend Developer" → "Backend Developer"
   - "SWE II" → "Software Engineer"
   - "Staff Engineer" → "Software Engineer"

2. **Standardize Common Terms:**
   - "Backend Engineer" and "Backend Developer" are treated as equivalent
   - "Frontend Engineer" and "Frontend Developer" are treated as equivalent
   - Variations are mapped to standard role names

3. **Extract Seniority:** Automatically detect and classify seniority level
   - Keywords: "junior", "jr", "entry-level" → Junior
   - Keywords: "senior", "sr", "snr" → Senior
   - Keywords: "lead", "staff", "principal", "director" → Lead
   - Default: Mid (if no clear seniority indicator)

### AI-Enhanced Normalization

When the AI provider is configured (OpenAI/Anthropic), the `JobTitleNormalizer` uses an LLM to:
- Understand job title variations and context
- Map non-standard titles to industry-standard roles
- Accurately infer seniority levels

### Fallback Behavior

If the AI provider is unavailable or encounters an error, the system falls back to:
- Pattern-based seniority detection
- String similarity matching
- Default mid-level classification

## Integration Points

### CV Analysis (main.py)

The experience relevance score is calculated as part of the initial CV analysis:

```bash
python main.py cv.pdf job_description.txt
```

Command-line flag to skip analysis:
```bash
python main.py cv.pdf job_description.txt --no-experience
```

### CV Improvement (improve_cv.py)

The experience relevance score is displayed in the analysis phase:

```bash
python improve_cv.py cv.pdf job_description.txt
```

The report shows how the score factors into the overall assessment and identifies which experiences are most relevant to the target role.

## Implementation Details

### Key Classes

1. **ExperienceRelevanceScorer**
   - Main class for calculating experience relevance scores
   - Methods:
     - `score_experience()` - Calculate overall relevance score
     - `parse_cv_work_experience()` - Parse CV text to extract job entries
     - `_calculate_title_similarity()` - Compare job titles using embeddings
     - `_calculate_seniority_match()` - Evaluate seniority alignment
     - `_calculate_duration_factor()` - Score years of relevant experience

2. **JobTitleNormalizer**
   - Normalizes job titles to standard forms
   - Uses AI agents (optional) for semantic understanding
   - Methods:
     - `normalize_title()` - Normalize a single job title
     - `normalize_titles()` - Normalize multiple titles
     - `calculate_title_similarity()` - Compare two raw titles

### Data Structures

```python
@dataclass
class JobExperience:
    job_title: str          # e.g., "Senior Backend Engineer"
    company: str            # e.g., "Tech Company Inc"
    duration_years: float   # e.g., 3.5
    seniority_level: str    # "Junior", "Mid", "Senior", "Lead"
    description: str        # Job description text
```

## Report Output

The experience relevance score appears in ATS reports with detailed breakdown:

```
💼 EXPERIENCE RELEVANCE SCORE
------------------------------------------------------------
SCORE: 72.50%
Title Similarity: 85.00%
Seniority Match: 80.00%
Duration Factor: 60.00%
Relevant Experience: 2 positions, 5.0 years

  Matching Positions:
    • Senior Backend Engineer at Tech Corp
      Duration: 3.0 years | Title Match: 90.0% | Seniority Match: 100.0%
    • Backend Developer at Startup Inc
      Duration: 2.0 years | Title Match: 80.0% | Seniority Match: 60.0%
```

## Configuration

### Environment Variables

- `AI_PROVIDER` - "openai" or "anthropic" (default: "openai")
- `AI_MODEL` - Model name (default: "gpt-4")
- `OPENAI_API_KEY` - OpenAI API key (for AI-enhanced normalization)
- `ANTHROPIC_API_KEY` - Anthropic API key (for AI-enhanced normalization)

### Threshold Behavior

- Titles with <30% similarity are excluded from relevance calculation
- Only positions matching the target role are counted as "relevant"
- At least one relevant position is needed to generate a non-zero score

## Future Enhancements

Potential improvements for this feature:

1. **Soft Skills Matching:** Evaluate transferable soft skills (leadership, communication, etc.)
2. **Industry Alignment:** Weight industry experience (finance, healthcare, tech, etc.)
3. **Company Prestige:** Factor in caliber/size of previous employers
4. **Trend Analysis:** Identify career progression patterns
5. **Skill Overlap:** Cross-reference skills mentioned in experience section
6. **Custom Weights:** Allow customization of component weights per role

## Troubleshooting

### Low Experience Score with High Keyword Score

This typically means:
- Candidate has relevant **skills** but **inexperienced** in the role
- Title similarity is low despite strong technical skills
- **Recommendation:** Highlight transferable skills and successful projects

### High Experience Score with Low Keyword Score

This typically means:
- Candidate has **years of relevant experience** but doesn't mention key **terms/tools**
- Job titles match well but CV lacks specific keyword terminology
- **Recommendation:** Add relevant keywords/tools to work experience descriptions

### Embedding Model Not Loading

If you see this warning: "Warning: Could not load embedding model"
- The system falls back to string similarity matching
- Install transformer models: `pip install sentence-transformers`
- Or ensure sufficient disk space for model cache

## See Also

- [SKILL_MATCHING.md](SKILL_MATCHING.md) - Skill matching system
- [README.md](../README.md) - Project overview
- [src/ats_cv_maker/experience_relevance_scorer.py](../src/ats_cv_maker/experience_relevance_scorer.py) - Implementation
