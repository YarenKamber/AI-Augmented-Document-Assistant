import os
import re
import uuid
from dataclasses import dataclass
from pypdf import PdfReader
from typing import List

@dataclass
class Document:
    """
    Data class to hold document metadata and content.
    """
    doc_id: str
    filename: str
    text: str

class DocumentProcessor:
    def __init__(self):
        """
        Initialize the DocumentProcessor.
        """
        pass

    def build_document(self, file_path: str) -> Document:
        """
        Processes a file (extracts & cleans) and returns a Document object.
        
        Args:
            file_path (str): Absolute path to the file.
            
        Returns:
            Document: A dataclass containing metadata and processed text.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        filename = os.path.basename(file_path)
        
        # Extract and clean text
        raw_text = self.extract_text(file_path)
        cleaned_text = self.clean_text(raw_text)
        
        # Create a unique ID for this document instance
        doc_id = str(uuid.uuid4())
        
        return Document(
            doc_id=doc_id,
            filename=filename,
            text=cleaned_text
        )

    def extract_text(self, file_path: str) -> str:
        """
        Determines file type and extracts text accordingly.
        
        Args:
            file_path (str): Abs path to the file.
            
        Returns:
            str: Extracted raw text.
        """
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        try:
            if ext == '.pdf':
                return self._extract_pdf_text(file_path)
            elif ext == '.txt':
                return self._extract_txt_text(file_path)
            else:
                raise ValueError(f"Unsupported file type: {ext}. Only .pdf and .txt are supported.")
        except Exception as e:
            # Re-raise nicely formatted errors
            raise ValueError(f"Error extracting text from {os.path.basename(file_path)}: {str(e)}")

    def clean_text(self, text: str) -> str:
        """
        Minimal text cleaning: normalize whitespace and newlines.
        
        Steps:
        1. Replace multiple spaces/tabs with single space.
        2. Normalize line breaks: replace 3+ newlines with 2 (paragraph break).
        3. Strip leading/trailing whitespace.
        """
        if not text:
            return ""
            
        # Pattern: [ \t]+ -> " " (Collapse horizontal whitespace)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Basic normalization of varied newline chars
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Replace 3+ empty lines with 2 newlines (preserve paragraphs clearly)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()

    def chunk_text(self, text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
        """
        Splits text into chunks of `chunk_size` characters with `overlap`.
        Simple sliding window approach.
        
        Args:
            text (str): The cleaned text.
            chunk_size (int): Max characters per chunk.
            overlap (int): Number of overlapping characters.
            
        Returns:
            List[str]: list of chunk strings.
        """
        if not text:
            return []
            
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = min(start + chunk_size, text_len)
            
            # Simple cut
            chunk = text[start:end]
            
            # Optional: Try not to cut words in half if possible (minor improvement)
            # If we are not at end of text, try to pull back to the last space
            if end < text_len:
                last_space = chunk.rfind(' ')
                if last_space != -1 and len(chunk) - last_space < 50: 
                    # Only pull back if we don't lose too much characters (e.g. < 50 chars)
                    end = start + last_space + 1
                    chunk = text[start:end]

            chunks.append(chunk.strip())
            
            # If we reached the end, break
            if end >= text_len:
                break
                
            # Move start forward, subtracting overlap
            # Ensure we always move forward at least 1 char to avoid infinite loop
            step = max(1, len(chunk) - overlap)
            start += step
            
        return chunks

    def _extract_pdf_text(self, file_path: str) -> str:
        """
        Helper to safely extract text from PDF using pypdf.
        """
        text_content = []
        reader = PdfReader(file_path)
        
        if reader.is_encrypted:
            try:
                # Try empty password
                reader.decrypt("")
            except:
                 raise ValueError("PDF is encrypted and cannot be read.")

        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)
        
        full_text = "\n".join(text_content)
        
        if not full_text.strip():
            # Warn but don't crash, might be OCR needed which is out of scope
            return "" 

        return full_text

    def _extract_txt_text(self, file_path: str) -> str:
        """
        Helper to extract text from TXT with encoding fallback.
        """
        # Try UTF-8 first
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Fallback to Latin-1
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
