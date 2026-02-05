import os
import hashlib
import json
import logging
from typing import Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

CACHE_DIR = "data/cache"
CACHE_EXPIRY_HOURS = 24

class CacheManager:
    def __init__(self, cache_dir: str = CACHE_DIR, expiry_hours: int = CACHE_EXPIRY_HOURS):
        self.cache_dir = cache_dir
        self.expiry_hours = expiry_hours
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_cache_key(self, prompt: str, model: str = "default") -> str:
        cache_str = f"{model}:{prompt}"
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def _is_expired(self, cache_data: dict) -> bool:
        if "timestamp" not in cache_data:
            return True
        
        cache_time = datetime.fromisoformat(cache_data["timestamp"])
        expiry_time = cache_time + timedelta(hours=self.expiry_hours)
        return datetime.now() > expiry_time
    
    def get(self, prompt: str, model: str = "default") -> Optional[str]:
        cache_key = self._get_cache_key(prompt, model)
        cache_path = self._get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            logger.debug(f"Cache miss for key: {cache_key[:8]}...")
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            if self._is_expired(cache_data):
                logger.debug(f"Cache expired for key: {cache_key[:8]}...")
                os.remove(cache_path)
                return None
            
            logger.debug(f"Cache hit for key: {cache_key[:8]}...")
            return cache_data.get("response")
        
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to read cache: {e}")
            return None
    
    def set(self, prompt: str, response: str, model: str = "default", metadata: Optional[dict] = None):
        cache_key = self._get_cache_key(prompt, model)
        cache_path = self._get_cache_path(cache_key)
        
        cache_data = {
            "prompt": prompt,
            "response": response,
            "model": model,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Cached response for key: {cache_key[:8]}...")
        
        except IOError as e:
            logger.warning(f"Failed to write cache: {e}")
    
    def clear_expired(self):
        cleared = 0
        for filename in os.listdir(self.cache_dir):
            if not filename.endswith('.json'):
                continue
            
            cache_path = os.path.join(self.cache_dir, filename)
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                if self._is_expired(cache_data):
                    os.remove(cache_path)
                    cleared += 1
            
            except (json.JSONDecodeError, IOError):
                continue
        
        logger.info(f"Cleared {cleared} expired cache entries")
        return cleared
    
    def clear_all(self):
        cleared = 0
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                os.remove(os.path.join(self.cache_dir, filename))
                cleared += 1
        
        logger.info(f"Cleared all {cleared} cache entries")
        return cleared
    
    def get_stats(self) -> dict:
        total = 0
        expired = 0
        size_bytes = 0
        
        for filename in os.listdir(self.cache_dir):
            if not filename.endswith('.json'):
                continue
            
            cache_path = os.path.join(self.cache_dir, filename)
            total += 1
            size_bytes += os.path.getsize(cache_path)
            
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                if self._is_expired(cache_data):
                    expired += 1
            
            except (json.JSONDecodeError, IOError):
                continue
        
        return {
            "total_entries": total,
            "expired_entries": expired,
            "active_entries": total - expired,
            "size_mb": round(size_bytes / (1024 * 1024), 2)
        }

_global_cache = None

def get_cache() -> CacheManager:
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheManager()
    return _global_cache
