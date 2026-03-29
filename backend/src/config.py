"""
Configuration module for ATS CV Maker.
Centralizes all configurable parameters.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration settings for ATS CV Maker."""
    
    # AI Provider Settings
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'openai').lower()
    AI_MODEL = os.getenv('AI_MODEL', 'gpt-4o-mini')  # Using mini for cost and speed
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    
    # Keyword Extraction Settings
    MAX_KEYWORDS_CV = 50  # Maximum keywords to extract from CV
    MAX_KEYWORDS_JD = 50  # Maximum keywords to extract from job description
    NGRAM_RANGE = (1, 3)  # N-gram range for TF-IDF (1-3 words)
    USE_SPACY = True      # Whether to use spaCy for noun phrase extraction
    
    # Scoring Settings
    REQUIRED_WEIGHT = 0.7   # Weight for required keywords (70%)
    OPTIONAL_WEIGHT = 0.3   # Weight for optional keywords (30%)
    SIMILARITY_THRESHOLD = 0.8  # Threshold for fuzzy matching
    
    # AI Agent Settings
    AI_TEMPERATURE = 0.3    # Temperature for AI responses (lower = more consistent)
    AI_MAX_TOKENS = 4000    # Maximum tokens for AI responses
    
    # Score Interpretation Thresholds
    EXCELLENT_THRESHOLD = 80  # Score >= 80% is excellent
    GOOD_THRESHOLD = 70       # Score >= 70% is good
    MODERATE_THRESHOLD = 50   # Score >= 50% is moderate
    
    @classmethod
    def validate(cls):
        """
        Validate configuration settings.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate AI provider
        if cls.AI_PROVIDER not in ['openai', 'anthropic']:
            errors.append(f"Invalid AI_PROVIDER: {cls.AI_PROVIDER}. Must be 'openai' or 'anthropic'")
        
        # Validate API keys
        if cls.AI_PROVIDER == 'openai' and not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY not set but AI_PROVIDER is 'openai'")
        
        if cls.AI_PROVIDER == 'anthropic' and not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY not set but AI_PROVIDER is 'anthropic'")
        
        # Validate weights
        if not 0 <= cls.REQUIRED_WEIGHT <= 1:
            errors.append(f"REQUIRED_WEIGHT must be between 0 and 1, got {cls.REQUIRED_WEIGHT}")
        
        if not 0 <= cls.OPTIONAL_WEIGHT <= 1:
            errors.append(f"OPTIONAL_WEIGHT must be between 0 and 1, got {cls.OPTIONAL_WEIGHT}")
        
        total_weight = cls.REQUIRED_WEIGHT + cls.OPTIONAL_WEIGHT
        if abs(total_weight - 1.0) > 0.01:
            errors.append(f"Weights must sum to 1.0, got {total_weight}")
        
        return errors
    
    @classmethod
    def get_score_interpretation(cls, score: float) -> str:
        """
        Get interpretation of a score.
        
        Args:
            score: Score percentage (0-100)
            
        Returns:
            Human-readable interpretation
        """
        if score >= cls.EXCELLENT_THRESHOLD:
            return "Excellent match! 🌟"
        elif score >= cls.GOOD_THRESHOLD:
            return "Good match! ✅"
        elif score >= cls.MODERATE_THRESHOLD:
            return "Moderate match ⚠️"
        else:
            return "Low match ❌"
    
    @classmethod
    def print_config(cls):
        """Print current configuration."""
        print("=" * 60)
        print("ATS CV Maker Configuration")
        print("=" * 60)
        print(f"AI Provider:          {cls.AI_PROVIDER}")
        print(f"AI Model:             {cls.AI_MODEL}")
        print(f"Max CV Keywords:      {cls.MAX_KEYWORDS_CV}")
        print(f"Max JD Keywords:      {cls.MAX_KEYWORDS_JD}")
        print(f"N-gram Range:         {cls.NGRAM_RANGE}")
        print(f"Use spaCy:            {cls.USE_SPACY}")
        print(f"Required Weight:      {cls.REQUIRED_WEIGHT * 100}%")
        print(f"Optional Weight:      {cls.OPTIONAL_WEIGHT * 100}%")
        print(f"AI Temperature:       {cls.AI_TEMPERATURE}")
        print(f"AI Max Tokens:        {cls.AI_MAX_TOKENS}")
        print("=" * 60)
        
        # Validate and show errors if any
        errors = cls.validate()
        if errors:
            print("\n⚠️  Configuration Errors:")
            for error in errors:
                print(f"  - {error}")
                print("=" * 60)
        else:
            print("✅ Configuration is valid")
            print("=" * 60)


# Create a singleton instance
config = Config()


if __name__ == '__main__':
    # Print configuration when run directly
    Config.print_config()
