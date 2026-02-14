import logging
import time
from flask import current_app

# Masking helper for logs
def mask_key(key):
    if not key: return "None"
    return f"{key[:6]}...{key[-4:]}"

class APIKeyManager:
    _instance = None
    
    # Status constants
    ACTIVE = "active"
    COOLING_DOWN = "cooling_down"
    DISABLED = "disabled"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(APIKeyManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized: return
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("APIKeyManager")

        self.keys = [] # List of dicts: {key, status, cooldown_until}
        self.current_index = 0
        self.cooldown_duration = 300 # 5 minutes default
        
        self._initialize_keys()
        self._initialized = True

    def _initialize_keys(self):
        config_keys = current_app.config.get("GOOGLE_API_KEYS", [])
        for k in config_keys:
            self.keys.append({
                "key": k,
                "status": self.ACTIVE,
                "cooldown_until": 0
            })
        self.logger.info(f"Initialized with {len(self.keys)} API keys.")

    def get_key(self):
        """Returns the next available healthy key using Round-Robin."""
        if not self.keys:
            self.logger.error("No API keys available.")
            return None

        # Check all keys starting from current index
        num_keys = len(self.keys)
        for i in range(num_keys):
            idx = (self.current_index + i) % num_keys
            key_info = self.keys[idx]
            
            # Check if key is out of cooldown
            if key_info["status"] == self.COOLING_DOWN:
                if time.time() >= key_info["cooldown_until"]:
                    key_info["status"] = self.ACTIVE
                    self.logger.info(f"Key {mask_key(key_info['key'])} is back from cooldown.")

            if key_info["status"] == self.ACTIVE:
                self.current_index = (idx + 1) % num_keys # Update for next call
                return key_info["key"]

        self.logger.warning("All keys are currently in cooldown or disabled.")
        return None

    def mark_failed(self, key, error_type="rate_limit"):
        """Marks a key as cooling down due to failure."""
        for key_info in self.keys:
            if key_info["key"] == key:
                key_info["status"] = self.COOLING_DOWN
                key_info["cooldown_until"] = time.time() + self.cooldown_duration
                self.logger.warning(
                    f"Key {mask_key(key)} failed ({error_type}). cooldown for {self.cooldown_duration}s."
                )
                break

    def mark_success(self, key):
        """Optionally reset status or update metrics on success."""
        for key_info in self.keys:
            if key_info["key"] == key:
                if key_info["status"] == self.COOLING_DOWN:
                    key_info["status"] = self.ACTIVE
                    key_info["cooldown_until"] = 0
                break

# Helper function to get instance
def get_key_manager():
    return APIKeyManager()
