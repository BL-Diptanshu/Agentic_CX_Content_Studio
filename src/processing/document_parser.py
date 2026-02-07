"""
Document Parser Utility
Extracts campaign information from uploaded documents (DOCX, PDF, TXT)
"""
import logging
from typing import Dict, Any, Optional
from docx import Document
import PyPDF2
import re


logger = logging.getLogger(__name__)

# Helper functions migrated from deleted processing modules
def normalize_whitespace(text: str) -> str:
    """Normalize horizontal whitespace to single spaces, preserving newlines"""
    # Replace multiple spaces/tabs with single space
    return re.sub(r'[ \t]+', ' ', text).strip()

def remove_extra_newlines(text: str) -> str:
    """Remove multiple consecutive newlines"""
    return re.sub(r'\n+', '\n', text).strip()

def get_token_info(text: str) -> Dict[str, Any]:
    """Get token count approximation or exact if tiktoken available"""
    try:
        import tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")
        token_count = len(encoding.encode(text))
    except ImportError:
        # Fallback approximation (avg 4 chars per token or 0.75 words)
        token_count = len(text.split()) * 1.3
        
    return {
        "token_count": int(token_count),
        "character_count": len(text)
    }


class CampaignDocumentParser:
    """Parse campaign briefs from various document formats"""
    
    def __init__(self):
        self.keywords = {
            # Basic campaign info
            'campaign_name': ['campaign name', 'campaign:', 'project name', 'project:', 'campaign title'],
            'brand': ['brand name', 'brand:', 'company:', 'organization:', 'brand overview'],
            'objective': ['objective', 'goal', 'purpose', 'aim:', 'description:', 'campaign objective'],
            'target_audience': ['target audience', 'audience:', 'demographics:', 'who:', 'customer segments'],
            
            # Section 1-2: Brand Overview, Mission & Vision
            'brand_overview': ['brand overview', 'about', 'company overview', 'introduction'],
            'mission': ['mission:', 'mission statement', 'our mission'],
            'vision': ['vision:', 'vision statement', 'our vision'],
            
            # Section 3: Brand Values
            'brand_values': ['brand values', 'core values', 'values:', 'guiding principles'],
            
            # Section 4: Tone & Voice Guidelines
            'tone_required': ['required tone', 'preferred tone', 'tone guidelines', 'brand tone'],
            'tone_prohibited': ['prohibited tone', 'avoid tone', 'disallowed tone', 'tone to avoid'],
            'voice_characteristics': ['voice characteristics', 'brand voice', 'communication style'],
            
            # Section 5: Language & Messaging Rules
            'allowed_language': ['allowed language', 'approved messaging', 'acceptable terms', 'use these words'],
            'forbidden_language': ['forbidden language', 'prohibited words', 'banned terms', 'never use', 'avoid these words'],
            
            # Section 6: Customer Promise
            'customer_promise': ['customer promise', 'brand promise', 'commitment', 'we promise'],
            
            # Section 7: Compliance & Regulatory
            'compliance': ['compliance', 'regulatory', 'legal requirements', 'regulations'],
            
            # Section 8: Visual Identity
            'visual_themes': ['visual identity', 'visual themes', 'imagery guidelines', 'allowed visuals'],
            'visual_prohibited': ['disallowed visuals', 'prohibited imagery', 'visual restrictions'],
            
            # Section 9-10: Content & AI Usage
            'content_applicability': ['content applicability', 'where to use', 'usage context'],
            'ai_usage': ['ai systems', 'ai usage', 'automation guidelines']
        }
    
    def parse_document(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Parse document and extract campaign information
        
        Args:
            file_path: Path to the uploaded file
            file_type: File extension (docx, pdf, txt)
            
        Returns:
            Dictionary with extracted campaign fields
        """
        logger.info(f"Parsing document: {file_path} (type: {file_type})")
        
        try:
            if file_type == 'docx':
                text = self._extract_from_docx(file_path)
            elif file_type == 'pdf':
                text = self._extract_from_pdf(file_path)
            elif file_type == 'txt':
                text = self._extract_from_txt(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            # Extract fields from text
            extracted = self._extract_fields(text)
            logger.info(f"Successfully extracted {len(extracted)} fields from document")
            return extracted
            
        except Exception as e:
            logger.error(f"Error parsing document: {e}", exc_info=True)
            return {'error': str(e)}
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        doc = Document(file_path)
        text = "\n\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        return text
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
        return text
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _extract_fields(self, text: str) -> Dict[str, Any]:
        """
        Extract campaign fields using keyword matching and pattern recognition.
        Also intelligently detects ALL sections using headings for flexibility.
        """
        # Preprocess text
        # Preprocess text (using local helpers)
        # Imports removed as functions are now inlined
        
        text = normalize_whitespace(remove_extra_newlines(text))
        text_lower = text.lower()
        extracted = {}
        
        # Add metadata
        extracted['metadata'] = get_token_info(text)
        
        # Extract predefined fields using keywords
        for field, patterns in self.keywords.items():
            value = self._find_field_value(text, text_lower, patterns)
            if value:
                extracted[field] = value
        
        # ENHANCED: Extract ALL sections by heading detection
        # This captures sections even if not in predefined keywords
        all_sections = self._extract_all_sections_by_headings(text)
        
        # Add sections that weren't caught by keyword matching
        for section_name, section_content in all_sections.items():
            # Clean up section name: remove numbering (e.g., "1. Brand Overview" → "brand_overview")
            clean_name = re.sub(r'^\d+\.?\s*', '', section_name)  # Remove leading numbers
            clean_name = clean_name.replace('_', ' ')  # Temporarily convert underscores to spaces
            
            # Create a sanitized field name
            field_name = clean_name.lower().replace(' ', '_').replace('&', 'and').replace('(', '').replace(')', '').replace(':', '')
            # Remove any remaining non-alphanumeric characters except underscores
            field_name = re.sub(r'[^a-z0-9_]', '', field_name)
            
            # Only add if not already extracted by keyword matching
            if field_name not in extracted and section_content.strip():
                extracted[field_name] = section_content.strip()
        
        # If no explicit campaign name, try to extract from document header
        if 'campaign_name' not in extracted:
            lines = text.split('\n')
            # First non-empty line often contains title
            for line in lines[:5]:
                if line.strip() and len(line.strip()) > 5:
                    extracted['campaign_name'] = line.strip()
                    break
        
        # Combine objectives and description
        if 'objective' in extracted and 'description' in extracted:
            extracted['objective'] = f"{extracted['objective']}\n\n{extracted.pop('description')}"
        
        logger.info(f"Extracted {len(extracted)} total fields from document")
        return extracted
    
    def _extract_all_sections_by_headings(self, text: str) -> Dict[str, str]:
        """
        Intelligently extract ALL sections from document using heading detection.
        Works with ANY brand guideline structure, not just predefined keywords.
        
        This enables the parser to adapt to ANY brand document format.
        """
        sections = {}
        lines = text.split('\n')
        
        current_section = None
        current_content = []
        
        for line in lines:
            stripped = line.strip()
            
            # Detect headings (various patterns)
            is_heading = False
            
            # Pattern 1: Numbered headings (e.g., "1. Brand Overview", "2.1 Mission")
            if re.match(r'^\d+\.?\s+[A-Z]', stripped):
                is_heading = True
            
            # Pattern 2: All caps or title case with minimal punctuation
            elif stripped.isupper() and len(stripped.split()) <= 6:
                is_heading = True
            
            # Pattern 3: Title case with colon or ending
            elif stripped and stripped[0].isupper() and len(stripped.split()) <= 8:
                # Check if it's actually a title (short, few punctuation)
                if stripped.count('.') <= 1 and stripped.count(',') == 0:
                    is_heading = True
            
            if is_heading and len(stripped) > 3:
                # Save previous section
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = stripped
                current_content = []
            elif current_section:
                # Add to current section content
                if stripped:
                    current_content.append(stripped)
        
        # Save last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        logger.debug(f"Detected {len(sections)} sections by heading analysis")
        return sections
    
    def _find_field_value(self, text: str, text_lower: str, patterns: list) -> Optional[str]:
        """
        Find value for a field using keyword patterns
        """
        for pattern in patterns:
            # Find position of keyword
            idx = text_lower.find(pattern)
            if idx != -1:
                # Extract text after keyword
                start = idx + len(pattern)
                # Get rest of line and possibly next few lines
                remaining = text[start:start+3000]  # Look ahead 3000 chars
                
                # Clean up the value
                lines = remaining.split('\n')
                value_lines = []
                
                for line in lines[:30]:  # Take up to 30 lines
                    line = line.strip()
                    if not line:
                        break  # Stop at empty line
                    # Stop if we hit another field keyword
                    if any(kw in line.lower() for kwlist in self.keywords.values() for kw in kwlist):
                        if value_lines:  # Only stop if we've already collected something
                            break
                    value_lines.append(line)
                
                if value_lines:
                    value = " ".join(value_lines)
                    # Clean up
                    value = re.sub(r'^[:;\-\s]+', '', value)  # Remove leading punctuation
                    value = re.sub(r'\s+', ' ', value)  # Normalize whitespace
                    return value.strip()
        
        return None

def parse_uploaded_document(uploaded_file) -> Dict[str, Any]:
    """
    Streamlit wrapper for parsing uploaded files
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        Dictionary with extracted campaign info
    """
    import tempfile
    import os
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{uploaded_file.name.split(".")[-1]}') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name
    
    try:
        # Determine file type
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        # Parse document
        parser = CampaignDocumentParser()
        result = parser.parse_document(tmp_path, file_extension)
        
        return result
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
