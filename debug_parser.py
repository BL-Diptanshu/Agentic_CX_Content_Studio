from src.processing.document_parser import CampaignDocumentParser
import json
import logging

# Configure logging to see parser internals
logging.basicConfig(level=logging.DEBUG)

def debug_parsing():
    parser = CampaignDocumentParser()
    file_path = "FitNow Official Brand Guidelines Document.docx"
    
    print(f"Parsing {file_path}...")
    try:
        # 1. Parse full document
        result = parser.parse_document(file_path, 'docx')
        
        # 2. Check internal extraction state
        text = parser._extract_from_docx(file_path)
        
        # Manually normalize
        from src.processing.document_parser import normalize_whitespace, remove_extra_newlines
        normalized = normalize_whitespace(remove_extra_newlines(text))
        
        print("\n--- Normalized Text (First 1000 chars) ---")
        print(normalized[:1000])
        print("------------------------------------------")
        
        # Check Heading Extraction
        sections = parser._extract_all_sections_by_headings(normalized)
        print(f"\n--- Detected Sections via Headings ({len(sections)}) ---")
        for k in sections.keys():
            print(f"Section Key: '{k}' -> Length: {len(sections[k])}")
            
        print("\n--- Final Extracted Result Keys ---")
        print(list(result.keys()))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_parsing()
