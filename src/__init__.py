"""
Poe.com Scraper Package

A comprehensive web scraper for extracting conversation data from Poe.com
"""

__version__ = "1.0.0"
__author__ = "hkevin01"
__description__ = "Web scraper for Poe.com conversations"

from .config import Config
from .exporters import DataExporter
from .gui import PoeScraperGUI
from .gui import main as run_gui
from .scraper import Conversation, PoeScraper
from .utils import Logger, ProgressTracker

__all__ = [
    'PoeScraper',
    'Conversation',
    'Config',
    'DataExporter',
    'PoeScraperGUI',
    'ProgressTracker',
    'Logger',
    'run_gui'
]

# Version info
VERSION_INFO = {
    'major': 1,
    'minor': 0,
    'patch': 0,
    'release': 'stable'
}

def get_version():
    """Get version string"""
    return f"{VERSION_INFO['major']}.{VERSION_INFO['minor']}.{VERSION_INFO['patch']}"

def get_version_info():
    """Get detailed version information"""
    return VERSION_INFO.copy()