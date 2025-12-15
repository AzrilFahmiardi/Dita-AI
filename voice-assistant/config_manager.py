import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ConfigManager:    
    def __init__(self, config_path: str = "config.yaml", environment: str = None):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to YAML configuration file
            environment: Environment name (development, production, etc.)
        """
        self.config_path = Path(config_path)
        self.environment = environment or os.getenv('DITA_ENV', 'development')
        self._config = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file with environment variable substitution"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_text = f.read()
            
            # Replace environment variables
            config_text = self._substitute_env_vars(config_text)
            
            # Parse YAML
            self._config = yaml.safe_load(config_text)
            
            # Apply environment-specific overrides
            self._apply_environment_overrides()
            
            print(f"Configuration loaded from {self.config_path} (env: {self.environment})")
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")
    
    def _substitute_env_vars(self, text: str) -> str:
        """Replace ${VAR_NAME} with environment variable values"""
        import re
        
        def replace_var(match):
            var_name = match.group(1)
            var_value = os.getenv(var_name)
            if var_value is None:
                raise ValueError(f"Environment variable {var_name} not found")
            return var_value
        
        return re.sub(r'\$\{([^}]+)\}', replace_var, text)
    
    def _apply_environment_overrides(self) -> None:
        """Apply environment-specific configuration overrides"""
        if 'environments' in self._config and self.environment in self._config['environments']:
            overrides = self._config['environments'][self.environment]
            self._deep_update(self._config, overrides)
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict) -> None:
        """Deep update dictionary with nested values"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key_path: Dot-separated path (e.g., 'llm.primary.model_name')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self.get(section, {})
    
    # Convenience methods for common configurations
    
    def get_api_key(self, key_name: str) -> str:
        """Get API key directly from environment using key name - ABSTRACTED"""
        api_key = os.getenv(key_name)
        if not api_key:
            raise ValueError(f"Environment variable {key_name} not found")
        return api_key
    
    def get_model_config(self, model_type: str = 'primary') -> Dict[str, Any]:
        """Get LLM model configuration"""
        return self.get_section(f'llm.{model_type}')
    
    def get_stt_config(self) -> Dict[str, Any]:
        """Get speech-to-text configuration"""
        return self.get_section('stt')
    
    def get_wakeword_config(self) -> Dict[str, Any]:
        """Get wake word configuration"""
        return self.get_section('wakeword')
    
    def get_rag_config(self) -> Dict[str, Any]:
        """Get RAG system configuration"""
        return self.get_section('rag')
    
    def get_audio_config(self) -> Dict[str, Any]:
        """Get audio processing configuration"""
        return self.get_section('audio')
    
    def get_vad_config(self) -> Dict[str, Any]:
        """Get Voice Activity Detection configuration"""
        return self.get_section('vad')
    
    def get_tts_config(self) -> Dict[str, Any]:
        """Get Text-to-Speech configuration"""
        return self.get_section('tts')


# Global configuration instance
_config_manager = None

def get_config() -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def reload_config() -> ConfigManager:
    """Reload configuration (useful for development)"""
    global _config_manager
    _config_manager = ConfigManager()
    return _config_manager


# Export convenience functions
def get_api_key(key_name: str) -> str:
    """Get API key directly from environment - ABSTRACTED for any provider"""
    return get_config().get_api_key(key_name)

def get_model_config(model_type: str = 'primary') -> Dict[str, Any]:
    """Get model configuration"""
    return get_config().get_model_config(model_type)

def get_stt_config() -> Dict[str, Any]:
    """Get STT configuration"""
    return get_config().get_stt_config()

def get_wakeword_config() -> Dict[str, Any]:
    """Get wake word configuration"""
    return get_config().get_wakeword_config()

def get_rag_config() -> Dict[str, Any]:
    """Get RAG configuration"""
    return get_config().get_rag_config()

def get_elasticsearch_config() -> Dict[str, Any]:
    """Get Elasticsearch configuration"""
    return get_config().get('elasticsearch', {})

def get_news_config() -> Dict[str, Any]:
    """Get news search configuration"""
    return get_config().get('news_search', {})

def get_vad_config() -> Dict[str, Any]:
    """Get Voice Activity Detection configuration"""
    return get_config().get_vad_config()

def get_tts_config() -> Dict[str, Any]:
    """Get Text-to-Speech configuration"""
    return get_config().get('tts', {})
