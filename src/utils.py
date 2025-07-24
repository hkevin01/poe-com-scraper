import asyncio
import functools
import hashlib
import logging
import os
import time
from typing import Any, Callable, Optional

import aiohttp


def rate_limiter(func: Callable) -> Callable:
    """Decorator for rate limiting API calls"""
    last_call_time = 0
    min_interval = 2.0  # Minimum seconds between calls
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        nonlocal last_call_time
        
        current_time = time.time()
        time_since_last_call = current_time - last_call_time
        
        if time_since_last_call < min_interval:
            sleep_time = min_interval - time_since_last_call
            await asyncio.sleep(sleep_time)
            
        last_call_time = time.time()
        return await func(*args, **kwargs)
    
    return wrapper

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator for retrying failed operations with exponential backoff"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        raise last_exception
                        
                    wait_time = delay * (backoff ** attempt)
                    logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time:.2f}s...")
                    await asyncio.sleep(wait_time)
                    
            raise last_exception
        
        return wrapper
    return decorator

class ProgressTracker:
    """Track and report progress of long-running operations"""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
        self.callbacks = []
        
    def add_callback(self, callback: Callable[[int, int, float], None]):
        """Add progress callback function"""
        self.callbacks.append(callback)
        
    def update(self, increment: int = 1):
        """Update progress"""
        self.current += increment
        
        if self.current > self.total:
            self.current = self.total
            
        # Calculate progress percentage
        percentage = (self.current / self.total) * 100 if self.total > 0 else 0
        
        # Calculate ETA
        elapsed_time = time.time() - self.start_time
        if self.current > 0:
            eta = (elapsed_time / self.current) * (self.total - self.current)
        else:
            eta = 0
            
        # Call progress callbacks
        for callback in self.callbacks:
            try:
                callback(self.current, self.total, percentage)
            except Exception as e:
                logging.warning(f"Progress callback failed: {e}")
                
    def reset(self):
        """Reset progress tracker"""
        self.current = 0
        self.start_time = time.time()
        
    def is_complete(self) -> bool:
        """Check if progress is complete"""
        return self.current >= self.total

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
        
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
        
    return filename

def create_file_hash(filepath: str) -> str:
    """Create SHA-256 hash of file contents"""
    hasher = hashlib.sha256()
    
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except FileNotFoundError:
        return ""

def ensure_directory(directory: str) -> str:
    """Ensure directory exists, create if necessary"""
    os.makedirs(directory, exist_ok=True)
    return directory

def format_bytes(bytes_value: int) -> str:
    """Format bytes into human-readable string"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} TB"

def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string"""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

class Logger:
    """Enhanced logging utility"""
    
    def __init__(self, name: str, level: str = 'INFO', file_path: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (if specified)
        if file_path:
            ensure_directory(os.path.dirname(file_path))
            file_handler = logging.FileHandler(file_path)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
            
    def get_logger(self):
        """Get the configured logger instance"""
        return self.logger

async def test_connection(url: str, timeout: int = 10) -> bool:
    """Test if a URL is accessible"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                return response.status == 200
    except Exception:
        return False

def validate_url(url: str) -> bool:
    """Validate URL format"""
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None