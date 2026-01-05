#!/usr/bin/env python3
"""
Example: Using the Experience Relevance Scorer

This example demonstrates how to use the ExperienceRelevanceScorer
to evaluate how relevant a candidate's past roles are to a target job.
"""

from src.ats_cv_maker.experience_relevance_scorer import ExperienceRelevanceScorer, JobExperience


def example_1_direct_scoring():
    """Example 1: Direct scoring with JobExperience objects."""
    print("=" * 60)
    print("EXAMPLE 1: Direct Experience Scoring")
    print("=" * 60)
    
    # Create a scorer
    scorer = ExperienceRelevanceScorer(use_embeddings=True)
    
    # Define candidate's past experiences
    experiences = [
        JobExperience(
            job_title="Senior Backend Engineer",
            company="Tech Corp",
            duration_years=3.0,
            seniority_level="Senior",
            description="Led backend architecture and system design"
        ),
        JobExperience(
            job_title="Backend Developer",
            company="Startup Inc",
            duration_years=2.5,
            seniority_level="Mid",
            description="Developed REST APIs and database optimization"
        ),
        JobExperience(
            job_title="Junior Python Developer",
            company="Learning Labs",
            duration_years=1.0,
            seniority_level="Junior",
            description="Learned Python and web development fundamentals"
        )
    ]
    
    # Score against target job
    target_job = "Lead Backend Engineer"
    target_seniority = "Senior"
    
    result = scorer.score_experience(
        cv_experiences=experiences,
        target_job_title=target_job,
        target_seniority=target_seniority
    )
    
    # Print results
    print(f"\nTarget Job: {target_job}")
    print(f"Target Seniority: {target_seniority}\n")
    
    print(f"OVERALL SCORE: {result['experience_relevance_score']:.2f}%\n")
    
    print("Component Breakdown:")
    print(f"  • Title Similarity: {result['title_similarity_score']:.2f}%")
    print(f"  • Seniority Match: {result['seniority_match_score']:.2f}%")
    print(f"  • Duration Factor: {result['duration_factor_score']:.2f}%\n")
    
    print(f"Summary: {result['details']}")
    
    if result['relevant_experience']:
        print("\nRelevant Positions Found:")
        for i, exp in enumerate(result['relevant_experience'], 1):
            print(f"\n  {i}. {exp['job_title']} at {exp['company']}")
            print(f"     Duration: {exp['duration_years']} years")
            print(f"     Title Similarity: {exp['title_similarity']*100:.1f}%")
            print(f"     Seniority Match: {exp['seniority_match']*100:.1f}%")


def example_2_parsing_cv_text():
    """Example 2: Parse work experience from CV text."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Parsing CV Work Experience")
    print("=" * 60)
    
    # Sample CV work experience text
    cv_text = """
    Senior Backend Engineer
    Tech Corp, San Francisco, CA
    Jan 2021 – Present (3 years)
    - Led architecture and design of microservices platform
    - Managed team of 5 backend developers
    
    Backend Developer
    Startup Inc, Mountain View, CA
    Jun 2018 – Dec 2020 (2.5 years)
    - Developed REST APIs serving 10M+ daily requests
    - Optimized database queries improving performance by 40%
    
    Junior Python Developer
    Learning Labs, Online
    Jan 2017 – May 2018 (1.5 years)
    - Completed Python bootcamp and built first production application
    """
    
    # Create scorer
    scorer = ExperienceRelevanceScorer(use_embeddings=False)
    
    # Parse CV text
    experiences = scorer.parse_cv_work_experience(cv_text)
    
    print(f"\nParsed {len(experiences)} job positions:\n")
    for i, exp in enumerate(experiences, 1):
        print(f"{i}. {exp.job_title}")
        print(f"   Company: {exp.company}")
        print(f"   Duration: {exp.duration_years} years")
        print(f"   Seniority: {exp.seniority_level}\n")
    
    # Score the parsed experience
    result = scorer.score_experience(
        cv_experiences=experiences,
        target_job_title="Principal Engineer",
        target_seniority="Lead"
    )
    
    print(f"\nScore against 'Principal Engineer' role:")
    print(f"Experience Relevance Score: {result['experience_relevance_score']:.2f}%")


def example_3_title_similarity():
    """Example 3: Compare job titles."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Job Title Similarity Comparison")
    print("=" * 60)
    
    scorer = ExperienceRelevanceScorer(use_embeddings=False)
    
    # Test various title comparisons
    comparisons = [
        ("Backend Engineer", "Senior Backend Engineer"),
        ("Software Developer", "Backend Engineer"),
        ("DevOps Engineer", "Infrastructure Engineer"),
        ("Data Scientist", "Software Engineer"),
        ("Project Manager", "Senior Backend Engineer"),
    ]
    
    print("\nTitle Similarity Scores (0-1 scale):\n")
    for title1, title2 in comparisons:
        similarity = scorer._calculate_simple_title_similarity(title1, title2)
        print(f"  {title1:25} vs {title2:25} → {similarity:.3f}")


def example_4_seniority_evaluation():
    """Example 4: Evaluate seniority alignment."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Seniority Level Alignment")
    print("=" * 60)
    
    scorer = ExperienceRelevanceScorer()
    
    cv_levels = ["Junior", "Mid", "Senior", "Lead"]
    target_level = "Senior"
    
    print(f"\nTarget Seniority: {target_level}\n")
    print("CV Seniority → Match Score:")
    
    for cv_level in cv_levels:
        match = scorer._calculate_seniority_match(cv_level, target_level)
        print(f"  {cv_level:10} → {match*100:5.0f}%")


def example_5_duration_scoring():
    """Example 5: Duration factor calculation."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Duration Factor Scoring")
    print("=" * 60)
    
    scorer = ExperienceRelevanceScorer()
    
    durations = [0, 1, 2, 3, 4, 5, 6, 8, 10, 15]
    
    print("\nYears of Experience → Duration Score:\n")
    for years in durations:
        factor = scorer._calculate_duration_factor(years)
        print(f"  {years:2} years → {factor*100:5.1f}%")


def example_6_complete_workflow():
    """Example 6: Complete workflow from CV text to score."""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Complete Workflow")
    print("=" * 60)
    
    # Sample CV
    cv_text = """
    EXPERIENCE
    
    Senior Data Engineer
    DataCorp Analytics, New York, NY
    March 2020 – Present
    - Designed and implemented distributed data pipeline processing 1TB daily
    - Led team of 3 engineers implementing real-time analytics
    - Reduced query latency by 60% through optimization
    
    Data Engineer
    Analytics Startup, Boston, MA
    June 2018 – February 2020
    - Built ETL pipelines for data warehouse
    - Developed SQL optimization strategies
    
    Junior Software Developer
    Tech Training Academy, Online
    January 2017 – May 2018
    - Completed bootcamp and worked on various Python projects
    """
    
    # Job description
    target_job_title = "Senior Data Engineer"
    
    # Create and run scorer
    scorer = ExperienceRelevanceScorer(use_embeddings=True)
    
    # Parse CV
    print("\nParsing CV work experience...")
    experiences = scorer.parse_cv_work_experience(cv_text)
    print(f"Found {len(experiences)} positions")
    
    # Score
    print(f"\nScoring against '{target_job_title}' role...")
    result = scorer.score_experience(
        cv_experiences=experiences,
        target_job_title=target_job_title,
        target_seniority="Senior"
    )
    
    # Display results
    print("\n" + "=" * 40)
    print("RESULTS")
    print("=" * 40)
    print(f"\nExperience Relevance Score: {result['experience_relevance_score']:.2f}%")
    print(f"\nComponent Scores:")
    print(f"  Title Similarity:  {result['title_similarity_score']:.2f}%")
    print(f"  Seniority Match:   {result['seniority_match_score']:.2f}%")
    print(f"  Duration Factor:   {result['duration_factor_score']:.2f}%")
    
    print(f"\nExperience Summary:")
    print(f"  Matching Positions: {result['matching_positions']}")
    print(f"  Total Relevant Years: {result['total_relevant_years']}")
    
    if result['relevant_experience']:
        print(f"\nMatching Positions:")
        for exp in result['relevant_experience']:
            print(f"  • {exp['job_title']} ({exp['duration_years']} years)")
            print(f"    Match: {exp['title_similarity']*100:.0f}% | Seniority: {exp['seniority_match']*100:.0f}%")


if __name__ == "__main__":
    # Run all examples
    example_1_direct_scoring()
    example_2_parsing_cv_text()
    example_3_title_similarity()
    example_4_seniority_evaluation()
    example_5_duration_scoring()
    example_6_complete_workflow()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)
