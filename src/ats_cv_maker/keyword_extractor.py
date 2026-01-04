"""
Keyword extraction module using TF-IDF and noun-phrase extraction.
"""

import re
from typing import List, Dict, Set
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
from collections import Counter


class KeywordExtractor:
    """Extracts keywords from text using TF-IDF and NLP techniques."""
    
    def __init__(self, use_spacy: bool = True):
        """
        Initialize the keyword extractor.
        
        Args:
            use_spacy: Whether to use spaCy for noun phrase extraction
        """
        self.use_spacy = use_spacy
        self.nlp = None
        
        if use_spacy:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("Warning: spaCy model 'en_core_web_sm' not found. Using TF-IDF only.")
                print("To install: python -m spacy download en_core_web_sm")
                self.use_spacy = False
    
    def extract_with_tfidf(self, text: str, max_keywords: int = 30, ngram_range: tuple = (1, 3)) -> List[tuple]:
        """
        Extract keywords using TF-IDF.
        
        Args:
            text: Input text
            max_keywords: Maximum number of keywords to extract
            ngram_range: Range of n-grams to consider
            
        Returns:
            List of (keyword, score) tuples sorted by score
        """
        # Preprocess text
        text = self._preprocess_text(text)
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=max_keywords,
            ngram_range=ngram_range,
            stop_words='english',
            lowercase=True,
            token_pattern=r'\b[a-zA-Z][a-zA-Z+#\.]*\b'  # Include +, #, . for terms like C++, C#, etc.
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform([text])
            feature_names = vectorizer.get_feature_names_out()
            
            # Get scores for each keyword
            scores = tfidf_matrix.toarray()[0]
            keyword_scores = list(zip(feature_names, scores))
            
            # Sort by score descending
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            return keyword_scores
        except ValueError:
            # Handle case when text is too short
            return []
    
    def extract_noun_phrases(self, text: str) -> List[str]:
        """
        Extract noun phrases using spaCy.
        
        Args:
            text: Input text
            
        Returns:
            List of noun phrases
        """
        if not self.use_spacy or self.nlp is None:
            return []
        
        doc = self.nlp(text)
        noun_phrases = []
        
        # Extract noun chunks
        for chunk in doc.noun_chunks:
            phrase = chunk.text.lower().strip()
            if len(phrase) > 2:  # Filter out very short phrases
                noun_phrases.append(phrase)
        
        # Extract named entities
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG', 'PRODUCT', 'SKILL', 'LANGUAGE']:
                noun_phrases.append(ent.text.lower().strip())
        
        return list(set(noun_phrases))
    
    def extract_keywords(self, text: str, max_keywords: int = 30) -> List[str]:
        """
        Extract keywords combining TF-IDF and noun phrases.
        
        Args:
            text: Input text
            max_keywords: Maximum number of keywords to extract
            
        Returns:
            List of extracted keywords
        """
        keywords = set()
        
        # Extract using TF-IDF
        tfidf_keywords = self.extract_with_tfidf(text, max_keywords=max_keywords)
        for keyword, _ in tfidf_keywords:
            keywords.add(keyword)
        
        # Extract noun phrases if spaCy is available
        if self.use_spacy:
            noun_phrases = self.extract_noun_phrases(text)
            keywords.update(noun_phrases[:max_keywords])
        
        return list(keywords)[:max_keywords]
    
    def compare_keywords(self, cv_text: str, job_description: str) -> Dict[str, any]:
        """
        Compare keywords between CV and job description.
        
        Args:
            cv_text: CV text content
            job_description: Job description text
            
        Returns:
            Dictionary with CV keywords, JD keywords, and matched keywords
        """
        cv_keywords = set(self.extract_keywords(cv_text, max_keywords=50))
        jd_keywords = set(self.extract_keywords(job_description, max_keywords=50))
        
        # Find matched keywords (exact match or partial match)
        matched = set()
        for cv_kw in cv_keywords:
            for jd_kw in jd_keywords:
                if cv_kw == jd_kw or cv_kw in jd_kw or jd_kw in cv_kw:
                    matched.add(jd_kw)
                    break
        
        return {
            'cv_keywords': list(cv_keywords),
            'jd_keywords': list(jd_keywords),
            'matched_keywords': list(matched),
            'match_count': len(matched),
            'total_jd_keywords': len(jd_keywords)
        }
    
    @staticmethod
    def _preprocess_text(text: str) -> str:
        """
        Preprocess text for keyword extraction.
        
        Args:
            text: Input text
            
        Returns:
            Preprocessed text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep important ones like +, #
        text = re.sub(r'[^\w\s+#\.]', ' ', text)
        
        return text.strip()
