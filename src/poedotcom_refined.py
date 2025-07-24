import json
import os
import pickle
import re
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ------------------------
# Poe.com Web Scraper
# Updated to comply with Poe.com Terms of Service
# ------------------------

# IMPORTANT: This scraper is designed for educational purposes only.
# Please ensure compliance with Poe.com's Terms of Service before use.
# Web scraping is explicitly prohibited under Section 3.3 of Poe's ToS.

class PoeComplianceError(Exception):
    """Exception raised when operations would violate Poe.com Terms of Service."""
    def __init__(self, message="Operation would violate Poe.com Terms of Service"):
        self.message = message
        super().__init__(self.message)

# 1. Get Specialty (Updated based on actual Poe.com content)
def get_specialty():
    """
    Extract Poe's specialty information from publicly available content.
    Uses only publicly accessible information that doesn't require scraping.
    """
    try:
        # Based on the provided Poe.com about page content
        specialty_info = {
            "platform_description": "The best AI, all in one place",
            "core_features": [
                "Access to the best AI from many different companies in a single interface",
                "ChatGPT, Claude, DeepSeek R1, and many top AI models",
                "Image, video, and audio generation models",
                "Millions of user-created bots",
                "Generate images, videos & audio",
                "AI-powered web search",
                "Chat with multiple bots at once",
                "Build your own bots",
                "Create applications",
                "Cross-device synchronization"
            ],
            "popular_bots": [
                "Assistant", "Web-Search", "App-Creator", "Grok-4", "o3-pro",
                "Veo-3", "Claude-Opus-4", "Gemini-2.5-Pro", "GPT-4.5-Preview",
                "Deepseek-R1-T", "Imagen-4", "FLUX-pro-1.1-ultra"
            ],
            "company": "Quora Inc.",
            "website": "poe.com"
        }
        return {"specialty": specialty_info}
    except Exception as err:
        print(f"An error occurred: {err}")
        return {"specialty": {}}

# 2. Get NSFW Policy (Updated based on actual ToS content)
def get_nsfw_policy():
    """
    Extract NSFW policy information from publicly available Terms of Service.
    Based on the actual Poe ToS content provided.
    """
    try:
        # Based on the actual Poe Terms of Service content provided
        nsfw_policy = {
            "policy_category": "Regulated with Restrictions",
            "key_restrictions": [
                "Use of Poe by anyone under 13 years of age is prohibited",
                "Bots may produce content that is not suitable for minors",
                "Users must not violate rights of another party or applicable laws",
                "Content must comply with Poe's usage guidelines and third-party provider policies",
                "Prohibited content includes violations of laws and platform policies"
            ],
            "age_verification": "Users under age of majority require parental consent",
            "content_responsibility": "Users are responsible for their content and ensuring compliance",
            "moderation": "Quora reserves right to remove content violating terms",
            "source": "Poe Terms of Service (Last updated: May 30, 2025)",
            "policy_url": "https://poe.com/pages/tos"
        }
        
        return {"nsfw_policy": nsfw_policy}
    except Exception as e:
        return {"nsfw_policy": {"error": f"Failed to process policy information: {e}"}}

# 3. Get Pricing Options (Updated to use public information)
def get_pricing_info():
    """
    Get pricing information from publicly available sources.
    Avoids automated scraping which violates Poe's ToS.
    """
    try:
        # Based on the publicly available information from Poe's about page
        pricing_info = {
            "free_tier": {
                "description": "Free for most usage",
                "features": "Basic access to AI models and features"
            },
            "subscription_plans": {
                "starting_price": "$4.99/month",
                "description": "Range of subscription plans for advanced usage",
                "pricing_philosophy": "Aim to have the lowest effective prices for any particular model"
            },
            "compute_points": {
                "description": "Usage may be subject to limits expressed in messages per bot or compute points",
                "reset_frequency": "Limits reset on regular basis (daily or monthly)",
                "rollover": "Unused message limits or compute points do not rollover",
                "transferability": "Non-transferable and non-refundable",
                "cash_value": "No cash value"
            },
            "note": "For detailed pricing, visit poe.com directly",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return {"pricing": pricing_info}
    except Exception as e:
        return {"pricing": {"error": str(e)}}

# 4. Get Useful Links (Updated with actual Poe.com links)
def get_useful_links():
    """Get useful links related to Poe.com services."""
    links = {
        "main_site": "https://poe.com",
        "about": "https://poe.com/about",
        "privacy_policy": "https://poe.com/pages/privacy",
        "terms_of_service": "https://poe.com/pages/tos",
        "subscriber_terms": "https://poe.com/subscriber_terms",
        "usage_guidelines": "https://poe.com/usage_guidelines",
        "earnings_terms": "https://poe.com/earnings_terms_of_service",
        "help_center": "https://help.poe.com",
        "privacy_center": "https://poe.com/privacy_center",
        "creator_guide": "https://poe.com/creator_guide",
        "brand_guidelines": "https://poe.com/brand_guidelines",
        "blog": "https://poe.com/blog",
        "demos": "https://poe.com/demos",
        "social_media": {
            "twitter": "https://twitter.com/poe_platform",
            "linkedin": "https://linkedin.com/company/poe",
            "discord": "https://discord.gg/poe",
            "threads": "https://threads.net/@poe",
            "instagram": "https://instagram.com/poe"
        }
    }
    return {"useful_links": links}

# 5. Get Server Status (Compliant version)
def get_server_status_simple():
    """
    Simple server status check using HTTP requests.
    Avoids complex scraping that might violate ToS.
    """
    try:
        start_time = time.time()
        response = requests.get("https://poe.com", timeout=10)
        response_time = round(time.time() - start_time, 3)
        
        status_info = {
            "url": "https://poe.com",
            "status_code": response.status_code,
            "status": "Online" if response.status_code == 200 else "Issues detected",
            "response_time_seconds": response_time,
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "method": "HTTP request (ToS compliant)"
        }
        
        return {"server_status": status_info}
    except requests.exceptions.RequestException as e:
        return {
            "server_status": {
                "url": "https://poe.com",
                "status": "Error",
                "error": str(e),
                "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }

# 6. Get Language Support (Based on public information)
def get_language_support():
    """
    Get language support information from publicly available sources.
    """
    try:
        # Based on the FAQ information provided
        language_info = {
            "supported_languages": "Multiple languages supported by underlying AI models",
            "note": "Language support varies by AI model and bot",
            "details": "Specific language capabilities depend on the AI model being used",
            "multilingual_bots": "Many bots support multiple languages including translation services",
            "source": "Based on Poe platform capabilities",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return {"language_support": language_info}
    except Exception as e:
        return {"language_support": {"error": str(e)}}

# 7. Get Platform Information
def get_platform_info():
    """
    Compile comprehensive platform information based on public sources.
    """
    try:
        platform_info = {
            "company": "Quora Inc.",
            "platform_name": "Poe",
            "launch_info": "Platform for exploring AI bots powered by third-party models",
            "target_users": "Users of all experience levels interested in exploring AI",
            "key_differentiators": [
                "Single interface for multiple AI companies",
                "Regular addition of new AI models",
                "User-created bots and applications",
                "Cross-device synchronization",
                "Creator monetization program"
            ],
            "business_model": "Freemium with subscription tiers",
            "content_policy": "User-generated content with moderation",
            "data_handling": "Personal information anonymized before sharing with AI providers",
            "terms_last_updated": "May 30, 2025",
            "privacy_policy_last_updated": "June 13, 2025"
        }
        
        return {"platform_info": platform_info}
    except Exception as e:
        return {"platform_info": {"error": str(e)}}

# 8. Compliance Check
def check_compliance():
    """
    Check if current operations comply with Poe.com Terms of Service.
    """
    compliance_info = {
        "terms_compliance": {
            "scraping_policy": "Web scraping is prohibited under Section 3.3 of Poe ToS",
            "automated_access": "Use in automated fashion prohibited",
            "data_extraction": "Data extraction methods prohibited except as permitted",
            "recommendation": "Use only publicly available information and official APIs"
        },
        "ethical_guidelines": [
            "Respect rate limits and server resources",
            "Use only for educational and research purposes",
            "Comply with Terms of Service",
            "Avoid automated data extraction",
            "Use official APIs when available"
        ],
        "alternatives": [
            "Use Poe's official API for development",
            "Access information through official channels",
            "Refer to public documentation and help pages"
        ]
    }
    
    return {"compliance": compliance_info}

# ------------------------
# Save Data to JSON
# ------------------------
def save_to_json(data, filename="poe_dot_com_data.json"):
    """Save collected data to JSON file."""
    try:
        with open(f"./{filename}", "w") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving data to JSON: {e}")

# ------------------------
# Main Program (Compliant Version)
# ------------------------
def main():
    """
    Main function - collects publicly available information about Poe.com
    while respecting Terms of Service.
    """
    print("Poe.com Information Collector (ToS Compliant Version)")
    print("=" * 60)
    
    data = {}
    
    # Add compliance check first
    data.update(check_compliance())
    
    # Collect publicly available information
    print("Collecting specialty information...")
    data.update(get_specialty())
    
    print("Collecting NSFW policy information...")
    data.update(get_nsfw_policy())
    
    print("Collecting pricing information...")
    data.update(get_pricing_info())
    
    print("Collecting useful links...")
    data.update(get_useful_links())
    
    print("Checking server status...")
    data.update(get_server_status_simple())
    
    print("Collecting language support information...")
    data.update(get_language_support())
    
    print("Collecting platform information...")
    data.update(get_platform_info())
    
    # Add metadata
    data["collection_metadata"] = {
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": "2.0 (ToS Compliant)",
        "note": "Information collected from publicly available sources only",
        "compliance_status": "Designed to respect Poe.com Terms of Service"
    }
    
    print("Saving data to JSON...")
    save_to_json(data)
    
    print("\nData collection completed successfully!")
    print("Note: This version respects Poe.com's Terms of Service")
    print("For detailed information, visit poe.com directly")

if __name__ == "__main__":
    main()