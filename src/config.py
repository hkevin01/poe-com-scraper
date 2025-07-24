import json
import os
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    requests_per_minute: int = 30
    delay_between_requests: float = 2.0
    max_concurrent_requests: int = 5

@dataclass
class OutputConfig:
    """Output configuration"""
    format: str = 'json'
    directory: str = './output'
    filename_template: str = 'poe_scrape_{timestamp}'
    include_metadata: bool = True

@dataclass
class ScrapingConfig:
    """Scraping behavior configuration"""
    max_conversations: int = 100
    include_timestamps: bool = True
    filter_bots: List[str] = None
    skip_empty_conversations: bool = True
    max_retries: int = 3
    timeout_seconds: int = 30

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = 'INFO'
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    file: Optional[str] = None
    console: bool = True

class Config:
    """Main configuration class"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.rate_limit = RateLimitConfig()
        self.output = OutputConfig()
        self.scraping = ScrapingConfig()
        self.logging = LoggingConfig()
        
        if config_path and os.path.exists(config_path):
            self.load_from_file(config_path)
        else:
            self.load_defaults()
            
    def load_from_file(self, config_path: str):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                
            # Update rate limit config
            if 'rate_limit' in config_data:
                for key, value in config_data['rate_limit'].items():
                    if hasattr(self.rate_limit, key):
                        setattr(self.rate_limit, key, value)
                        
            # Update output config
            if 'output' in config_data:
                for key, value in config_data['output'].items():
                    if hasattr(self.output, key):
                        setattr(self.output, key, value)
                        
            # Update scraping config
            if 'scraping' in config_data:
                for key, value in config_data['scraping'].items():
                    if hasattr(self.scraping, key):
                        setattr(self.scraping, key, value)
                        
            # Update logging config
            if 'logging' in config_data:
                for key, value in config_data['logging'].items():
                    if hasattr(self.logging, key):
                        setattr(self.logging, key, value)
                        
        except Exception as e:
            print(f"Error loading config file: {e}")
            self.load_defaults()
            
    def load_defaults(self):
        """Load default configuration"""
        # Defaults are already set in dataclass definitions
        pass
        
    def save_to_file(self, config_path: str):
        """Save current configuration to JSON file"""
        config_dict = {
            'rate_limit': asdict(self.rate_limit),
            'output': asdict(self.output),
            'scraping': asdict(self.scraping),
            'logging': asdict(self.logging)
        }
        
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'rate_limit': asdict(self.rate_limit),
            'output': asdict(self.output),
            'scraping': asdict(self.scraping),
            'logging': asdict(self.logging)
        }
        
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        # Validate rate limit config
        if self.rate_limit.requests_per_minute <= 0:
            errors.append("Rate limit requests_per_minute must be positive")
            
        if self.rate_limit.delay_between_requests < 0:
            errors.append("Rate limit delay_between_requests cannot be negative")
            
        # Validate output config
        if not self.output.directory:
            errors.append("Output directory cannot be empty")
            
        if self.output.format not in ['json', 'csv', 'xlsx']:
            errors.append("Output format must be one of: json, csv, xlsx")
            
        # Validate scraping config
        if self.scraping.max_conversations <= 0:
            errors.append("Max conversations must be positive")
            
        if self.scraping.max_retries < 0:
            errors.append("Max retries cannot be negative")
            
        return errors