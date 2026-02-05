"""
Brand Knowledge Base Loader
Loads brand validation rules from JSON files in brand_kb/ directory
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class BrandKBLoader:
    """Loads brand knowledge base rules from JSON files"""
    
    def __init__(self, kb_path: str = "brand_kb"):
        self.kb_path = Path(kb_path)
        self._cache: Dict[str, any] = {}
        logger.info(f"Initialized BrandKBLoader with path: {self.kb_path}")
    
    def load_forbidden_language(self) -> Dict[str, List[str]]:
        """
        Load forbidden language by category.
        
        Returns:
            Dict with categories as keys and forbidden terms as values
            Example: {"absolute_claims": ["guaranteed", "100% success"], ...}
        """
        path = self.kb_path / "policy" / "forbidden_language.json"
        data = self._load_json(path, "forbidden_language")
        logger.debug(f"Loaded {len(data)} forbidden language categories")
        return data
    
    def load_allowed_language(self) -> Dict[str, List[str]]:
        """
        Load encouraged/allowed language by category.
        
        Returns:
            Dict with categories as keys and encouraged phrases as values
        """
        path = self.kb_path / "policy" / "allowed_language.json"
        data = self._load_json(path, "allowed_language")
        logger.debug(f"Loaded {len(data)} allowed language categories")
        return data
    
    def load_tone_profile(self) -> Dict[str, List[str]]:
        """
        Load tone profile with required and disallowed tones.
        
        Returns:
            Dict with keys: required_tone, disallowed_tone, writing_style
        """
        path = self.kb_path / "tone" / "tone_profile.json"
        data = self._load_json(path, "tone_profile")
        logger.debug(f"Loaded tone profile with {len(data)} sections")
        return data
    
    def load_context_rules(self) -> Dict[str, List[str]]:
        """
        Load context rules for allowed/restricted sections.
        
        Returns:
            Dict with allowed_sections and restricted_sections
        """
        path = self.kb_path / "context_rules" / "allowed_context_types.json"
        data = self._load_json(path, "context_rules")
        logger.debug(f"Loaded context rules")
        return data
    
    def get_all_forbidden_terms(self) -> List[str]:
        """
        Get a flat list of all forbidden terms across all categories.
        
        Returns:
            List of all forbidden terms/phrases
        """
        forbidden_data = self.load_forbidden_language()
        all_terms = []
        
        for category, terms in forbidden_data.items():
            all_terms.extend(terms)
        
        logger.debug(f"Total forbidden terms: {len(all_terms)}")
        return all_terms
    
    def get_forbidden_by_category(self) -> Dict[str, List[str]]:
        """
        Get forbidden terms organized by category for detailed reporting.
        
        Returns:
            Dict mapping category names to lists of forbidden terms
        """
        return self.load_forbidden_language()
    
    def get_all_allowed_phrases(self) -> List[str]:
        """
        Get a flat list of all encouraged phrases.
        
        Returns:
            List of all allowed/encouraged phrases
        """
        allowed_data = self.load_allowed_language()
        all_phrases = []
        
        for category, phrases in allowed_data.items():
            all_phrases.extend(phrases)
        
        return all_phrases
    
    def _load_json(self, path: Path, cache_key: str) -> Dict:
        """
        Load JSON file with caching.
        
        Args:
            path: Path to JSON file
            cache_key: Key for caching
            
        Returns:
            Parsed JSON data
        """
        # Check cache first
        if cache_key in self._cache:
            logger.debug(f"Using cached data for: {cache_key}")
            return self._cache[cache_key]
        
        # Load from file
        try:
            if not path.exists():
                logger.warning(f"KB file not found: {path}")
                return {}
            
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Cache the data
            self._cache[cache_key] = data
            logger.info(f"Loaded KB file: {path}")
            return data
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from {path}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading {path}: {e}")
            return {}
    
    def reload_all(self):
        """Clear cache and reload all KB files"""
        self._cache.clear()
        logger.info("Cleared KB cache, files will be reloaded on next access")


# Global instance
_kb_loader: Optional[BrandKBLoader] = None


def get_kb_loader(kb_path: str = "brand_kb") -> BrandKBLoader:
    """
    Get or create global BrandKBLoader instance.
    
    Args:
        kb_path: Path to brand knowledge base directory
        
    Returns:
        BrandKBLoader instance
    """
    global _kb_loader
    if _kb_loader is None:
        _kb_loader = BrandKBLoader(kb_path)
    return _kb_loader
