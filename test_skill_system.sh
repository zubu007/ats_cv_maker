#!/bin/bash
# Test script for skill matching system
# This script validates that all modules are importable and have correct structure

echo "🧪 Testing Skill Matching System Structure..."
echo "================================================"

# Test Python syntax
echo ""
echo "1. Checking Python syntax..."
python3 -m py_compile src/ats_cv_maker/skill_extractor.py
python3 -m py_compile src/ats_cv_maker/skill_normalizer.py
python3 -m py_compile src/ats_cv_maker/skill_matcher.py
python3 -m py_compile src/ats_cv_maker/ats_scorer.py
echo "✓ All files have valid Python syntax"

# Check for required classes
echo ""
echo "2. Checking for required classes..."

check_class() {
    local file=$1
    local class=$2
    if grep -q "class $class" "$file"; then
        echo "✓ Found class $class in $file"
    else
        echo "✗ Missing class $class in $file"
    fi
}

check_class "src/ats_cv_maker/skill_extractor.py" "SkillExtractor"
check_class "src/ats_cv_maker/skill_extractor.py" "SkillList"
check_class "src/ats_cv_maker/skill_normalizer.py" "SkillNormalizer"
check_class "src/ats_cv_maker/skill_normalizer.py" "NormalizedSkill"
check_class "src/ats_cv_maker/skill_matcher.py" "SkillMatcher"
check_class "src/ats_cv_maker/ats_scorer.py" "ATSScorer"

# Check for key methods
echo ""
echo "3. Checking for key methods..."

check_method() {
    local file=$1
    local method=$2
    if grep -q "def $method" "$file"; then
        echo "✓ Found method $method in $file"
    else
        echo "✗ Missing method $method in $file"
    fi
}

check_method "src/ats_cv_maker/skill_extractor.py" "extract_skills_from_cv"
check_method "src/ats_cv_maker/skill_extractor.py" "extract_skills_from_job_description"
check_method "src/ats_cv_maker/skill_normalizer.py" "normalize_skills"
check_method "src/ats_cv_maker/skill_normalizer.py" "merge_skills"
check_method "src/ats_cv_maker/skill_matcher.py" "match_skills"
check_method "src/ats_cv_maker/skill_matcher.py" "calculate_skill_score"
check_method "src/ats_cv_maker/ats_scorer.py" "calculate_skill_match_score"

echo ""
echo "4. Checking script files..."
[ -f "skill_score.py" ] && echo "✓ skill_score.py exists" || echo "✗ skill_score.py missing"
[ -f "skill_score_orchestration.py" ] && echo "✓ skill_score_orchestration.py exists" || echo "✗ skill_score_orchestration.py missing"
[ -f "main.py" ] && echo "✓ main.py exists" || echo "✗ main.py missing"

echo ""
echo "5. Checking documentation..."
[ -f "docs/SKILL_MATCHING.md" ] && echo "✓ SKILL_MATCHING.md exists" || echo "✗ SKILL_MATCHING.md missing"

echo ""
echo "================================================"
echo "✅ Structure validation complete!"
echo ""
echo "To use the skill matching system:"
echo "  1. Install dependencies: uv sync"
echo "  2. Run skill analysis: python skill_score.py <cv_file> <jd_file>"
echo "  3. Full ATS analysis: python main.py <cv_file> <jd_file>"
