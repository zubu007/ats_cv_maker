"""
CV text extraction module for ATS CV Maker.
Extracts text from PDF and plain text CV files.
"""

import PyPDF2
from pathlib import Path
from typing import Optional


class CVExtractor:
    """Extracts text from CV files in various formats."""
    
    @staticmethod
    def extract_from_pdf(pdf_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text from the PDF
        """
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
        
        return text.strip()
    
    @staticmethod
    def extract_from_text(text_path: str) -> str:
        """
        Extract text from a plain text file.
        
        Args:
            text_path: Path to the text file
            
        Returns:
            Content of the text file
        """
        try:
            with open(text_path, 'r', encoding='utf-8') as file:
                text = file.read()
        except Exception as e:
            raise Exception(f"Error reading text file: {str(e)}")
        
        return text.strip()
    
    @staticmethod
    def extract(file_path: str) -> str:
        """
        Automatically detect file type and extract text.
        
        Args:
            file_path: Path to the CV file
            
        Returns:
            Extracted text from the CV
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = path.suffix.lower()
        
        if file_extension == '.pdf':
            return CVExtractor.extract_from_pdf(file_path)
        elif file_extension in ['.txt', '.text']:
            return CVExtractor.extract_from_text(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}. Supported formats: .pdf, .txt")
