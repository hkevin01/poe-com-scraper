import asyncio
import json
import logging
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import aiohttp
from bs4 import BeautifulSoup

from .config import Config
from .exporters import DataExporter
from .utils import rate_limiter, retry_on_failure


@dataclass
class Conversation:
    """Data class for storing conversation information"""
    id: str
    bot_name: str
    title: str
    messages: List[Dict[str, Any]]
    timestamp: str
    metadata: Dict[str, Any]

class PoeScraper:
    """Main scraper class for Poe.com"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = Config(config_path)
        self.session = None
        self.logger = logging.getLogger(__name__)
        self.conversations = []
        self.is_running = False
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_session()
        
    async def start_session(self):
        """Initialize aiohttp session with proper headers"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        connector = aiohttp.TCPConnector(limit=10)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            headers=headers,
            connector=connector,
            timeout=timeout
        )
        
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            
    @rate_limiter
    @retry_on_failure(max_retries=3)
    async def fetch_page(self, url: str) -> str:
        """Fetch a single page with rate limiting and retry logic"""
        if not self.session:
            await self.start_session()
            
        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.text()
            else:
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status
                )
                
    def parse_conversation_list(self, html: str) -> List[Dict[str, str]]:
        """Parse conversation list from main page"""
        soup = BeautifulSoup(html, 'html.parser')
        conversations = []
        
        # Find conversation elements (this would need to be updated based on actual DOM structure)
        conversation_elements = soup.find_all('div', class_='conversation-item')
        
        for element in conversation_elements:
            try:
                conv_data = {
                    'id': element.get('data-conversation-id', ''),
                    'title': element.find('h3', class_='conversation-title').text.strip(),
                    'bot_name': element.find('span', class_='bot-name').text.strip(),
                    'url': element.find('a')['href'],
                    'preview': element.find('p', class_='message-preview').text.strip()
                }
                conversations.append(conv_data)
            except (AttributeError, KeyError) as e:
                self.logger.warning(f"Failed to parse conversation element: {e}")
                continue
                
        return conversations
        
    def parse_conversation_detail(self, html: str, conv_id: str) -> Conversation:
        """Parse detailed conversation data"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract conversation metadata
        title_elem = soup.find('h1', class_='conversation-title')
        title = title_elem.text.strip() if title_elem else f"Conversation {conv_id}"
        
        bot_elem = soup.find('span', class_='bot-indicator')
        bot_name = bot_elem.text.strip() if bot_elem else "Unknown"
        
        # Extract messages
        messages = []
        message_elements = soup.find_all('div', class_='message')
        
        for msg_elem in message_elements:
            try:
                message = {
                    'role': 'user' if 'user-message' in msg_elem.get('class', []) else 'assistant',
                    'content': msg_elem.find('div', class_='message-content').text.strip(),
                    'timestamp': msg_elem.get('data-timestamp', ''),
                    'id': msg_elem.get('data-message-id', '')
                }
                messages.append(message)
            except AttributeError as e:
                self.logger.warning(f"Failed to parse message: {e}")
                continue
                
        # Extract metadata
        metadata = {
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'message_count': len(messages),
            'url': f"https://poe.com/chat/{conv_id}"
        }
        
        return Conversation(
            id=conv_id,
            bot_name=bot_name,
            title=title,
            messages=messages,
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
            metadata=metadata
        )
        
    async def scrape_conversations(self, max_conversations: Optional[int] = None) -> List[Conversation]:
        """Main scraping method"""
        self.is_running = True
        max_conv = max_conversations or self.config.scraping.max_conversations
        
        try:
            # Fetch conversation list
            self.logger.info("Fetching conversation list...")
            main_page_html = await self.fetch_page("https://poe.com/")
            conversation_links = self.parse_conversation_list(main_page_html)
            
            self.logger.info(f"Found {len(conversation_links)} conversations")
            
            # Limit conversations if specified
            if max_conv and max_conv < len(conversation_links):
                conversation_links = conversation_links[:max_conv]
                
            # Scrape individual conversations
            conversations = []
            for i, conv_link in enumerate(conversation_links):
                if not self.is_running:
                    break
                    
                self.logger.info(f"Scraping conversation {i+1}/{len(conversation_links)}: {conv_link['title']}")
                
                try:
                    conv_html = await self.fetch_page(conv_link['url'])
                    conversation = self.parse_conversation_detail(conv_html, conv_link['id'])
                    conversations.append(conversation)
                    
                except Exception as e:
                    self.logger.error(f"Failed to scrape conversation {conv_link['id']}: {e}")
                    continue
                    
            self.conversations = conversations
            self.logger.info(f"Successfully scraped {len(conversations)} conversations")
            return conversations
            
        except Exception as e:
            self.logger.error(f"Scraping failed: {e}")
            raise
        finally:
            self.is_running = False
            
    def stop_scraping(self):
        """Stop the scraping process"""
        self.is_running = False
        self.logger.info("Scraping stopped by user")
        
    def export_data(self, conversations: List[Conversation], format: str = 'json', filename: Optional[str] = None):
        """Export scraped data using DataExporter"""
        exporter = DataExporter(self.config)
        return exporter.export(conversations, format, filename)
        
    def get_stats(self) -> Dict[str, Any]:
        """Get scraping statistics"""
        if not self.conversations:
            return {}
            
        total_messages = sum(len(conv.messages) for conv in self.conversations)
        bot_counts = {}
        
        for conv in self.conversations:
            bot_name = conv.bot_name
            bot_counts[bot_name] = bot_counts.get(bot_name, 0) + 1
            
        return {
            'total_conversations': len(self.conversations),
            'total_messages': total_messages,
            'average_messages_per_conversation': total_messages / len(self.conversations),
            'bot_distribution': bot_counts,
            'last_scraped': time.strftime('%Y-%m-%d %H:%M:%S')
        }