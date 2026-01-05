# Experience Relevance Score - Quick Reference

## What It Does

Measures how relevant a candidate's past work roles are to a target job position on a 0-100% scale.

## Formula

```
experience_score = (title_similarity × 0.5) + (seniority_match × 0.3) + (duration_factor × 0.2)
```

## Three Components

| Component | Weight | Measures | Range |
|-----------|--------|----------|-------|
| **Title Similarity** | 50% | How similar past titles are to target title | 0-100% |
| **Seniority Match** | 30% | How well seniority levels align | 0-100% |
| **Duration Factor** | 20% | Years spent in relevant roles | 0-100% |

## Score Interpretation

| Score | Meaning |
|-------|---------|
| 80-100% | ⭐⭐⭐⭐⭐ Excellent - Highly relevant experience |
| 60-80% | ⭐⭐⭐⭐ Good - Relevant with some gaps |
| 40-60% | ⭐⭐⭐ Fair - Some relevant experience |
| 20-40% | ⭐⭐ Limited - Minimal relevant experience |
| 0-20% | ⭐ Poor - Little to no relevant experience |

## Using in CLI

### With Analysis
```bash
python main.py cv.pdf job.txt
# Shows experience relevance score in report
```

### Skip Experience Scoring
```bash
python main.py cv.pdf job.txt --no-experience
```

### During CV Improvement
```bash
python improve_cv.py cv.pdf job.txt
# Shows experience relevance in analysis phase
```

## Using in Code

### Direct Scoring
```python
from src.ats_cv_maker import ExperienceRelevanceScorer, JobExperience

scorer = ExperienceRelevanceScorer()

result = scorer.score_experience(
    cv_experiences=[
        JobExperience(
            job_title="Senior Backend Engineer",
            company="Tech Corp",
            duration_years=3.0,
            seniority_level="Senior"
        )
    ],
    target_job_title="Lead Backend Engineer"
)

print(f"{result['experience_relevance_score']:.1f}%")  # 72.5%
```

### Parse CV Text
```python
scorer = ExperienceRelevanceScorer()

# Parse work experience from CV text
experiences = scorer.parse_cv_work_experience(cv_text)

# Score against target
result = scorer.score_experience(
    cv_experiences=experiences,
    target_job_title="Senior Engineer"
)
```

## Seniority Levels

### Classification
- **Junior** - 0-2 years, entry-level roles
- **Mid** - 2-5 years, standard roles (default)
- **Senior** - 5-8+ years, advanced roles
- **Lead** - 8+ years, leadership/staff roles

### Matching Scores
- Exact match: 100%
- 1 level difference: 85% (e.g., Mid→Senior)
- 2 level difference: 60% (e.g., Junior→Senior)  
- 3 level difference: 30% (e.g., Junior→Lead)

## Duration Scoring

Years in relevant roles:
| Years | Score |
|-------|-------|
| 0 | 0% |
| 1 | 20% |
| 2 | 40% |
| 3 | 60% |
| 4 | 73% |
| 5 | 83% |
| 8+ | 100% |

## Title Similarity

### How It Works
- Uses AI embeddings (if available) for semantic understanding
- Falls back to string similarity (keyword matching)
- Compares CV titles against target job title

### Examples
| CV Title | Target Title | Similarity |
|----------|--------------|-----------|
| Backend Engineer | Senior Backend Engineer | 90% |
| Backend Developer | Backend Engineer | 85% |
| Software Developer | DevOps Engineer | 50% |
| Accountant | Software Engineer | 10% |

## Report Output

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

## Environment Setup

### Optional: Enhanced Title Normalization
```bash
# Install for AI-powered job title normalization
pip install sentence-transformers

# Or rely on string-based fallback (no additional install needed)
```

### Configure AI Provider (Optional)
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env with your keys:
OPENAI_API_KEY=sk-...
# or
ANTHROPIC_API_KEY=...
```

## Common Use Cases

### 1. Quick CV Analysis
```bash
python main.py resume.pdf target_job.txt
# Shows all three scores: keyword, skill (if enabled), and experience
```

### 2. Focus on Experience Fit
```python
from src.ats_cv_maker import ExperienceRelevanceScorer

scorer = ExperienceRelevanceScorer()
result = scorer.score_experience(experiences, "Senior Engineer")

print(f"Experience Fit: {result['experience_relevance_score']}%")
for exp in result['relevant_experience']:
    print(f"  - {exp['job_title']}: {exp['title_similarity']*100:.0f}% match")
```

### 3. Identify Experience Gaps
```python
result = scorer.score_experience(experiences, "Cloud Architect")

if result['experience_relevance_score'] < 50:
    print("⚠️ Limited relevant experience")
    print(f"Need more: {result['details']}")
```

## Troubleshooting

### Low score with high keywords?
→ CV has right **skills** but **inexperienced** in role
→ Add more work experience descriptions

### High score with low keywords?
→ CV has **relevant experience** but lacks **terminology**
→ Add keywords to job descriptions/achievements

### "Could not load embedding model"?
→ System using fallback string similarity
→ Optional: `pip install sentence-transformers`

## Key Features

✅ Semantic job title matching (with AI option)
✅ Seniority level alignment scoring
✅ Years of relevant experience weighting
✅ Automatic CV work experience parsing
✅ AI-powered title normalization (optional)
✅ Graceful fallbacks if AI unavailable
✅ Detailed reporting with position breakdown
✅ Zero breaking changes to existing code

## Files Reference

| File | Purpose |
|------|---------|
| `experience_relevance_scorer.py` | Main scoring engine |
| `job_title_normalizer.py` | Title normalization (optional AI) |
| `docs/EXPERIENCE_RELEVANCE.md` | Full documentation |
| `example_experience_scorer.py` | Code examples |

## API Summary

### ExperienceRelevanceScorer
```python
scorer = ExperienceRelevanceScorer(use_embeddings=True)

# Main method
result = scorer.score_experience(
    cv_experiences: List[JobExperience],
    target_job_title: str,
    target_seniority: str = "Mid"
) -> Dict

# Parse CV text
experiences = scorer.parse_cv_work_experience(cv_text: str) -> List[JobExperience]
```

### JobTitleNormalizer
```python
normalizer = JobTitleNormalizer()

# Normalize single title
result = normalizer.normalize_title(job_title: str) -> NormalizedTitle

# Calculate similarity
similarity = normalizer.calculate_title_similarity(title1: str, title2: str) -> float
```

## More Information

- **Full Docs**: See `docs/EXPERIENCE_RELEVANCE.md`
- **Examples**: Run `python example_experience_scorer.py`
- **Implementation**: See `EXPERIENCE_RELEVANCE_IMPLEMENTATION.md`
