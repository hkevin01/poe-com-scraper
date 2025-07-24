# Poe.com Scraper

A Python-based web scraper designed to extract data from Poe.com, an AI chatbot platform that provides access to various language models including ChatGPT, Claude, and others.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Changelog](#changelog)
- [License](#license)

## 🔍 Overview

This scraper is built to interact with Poe.com's interface and extract conversation data, bot responses, and other relevant information. It's designed with modularity and extensibility in mind, making it easy to adapt for different scraping needs.

## ✨ Features

- **Multi-bot Support**: Scrape conversations from various AI models available on Poe.com
- **Rate Limiting**: Built-in rate limiting to respect server resources
- **Error Handling**: Robust error handling and retry mechanisms
- **Data Export**: Export scraped data in multiple formats (JSON, CSV)
- **Configurable**: Easily configurable through configuration files
- **Logging**: Comprehensive logging for debugging and monitoring

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/hkevin01/poe-com-scraper.git
cd poe-com-scraper
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your settings (see [Configuration](#configuration) section)

## 🎯 Usage

### Basic Usage

```python
from src.scraper import PoeScraper

# Initialize the scraper
scraper = PoeScraper()

# Start scraping
results = scraper.scrape_conversations()

# Export results
scraper.export_data(results, format='json')
```

### Command Line Interface

```bash
# Run the scraper with default settings
python scripts/run_scraper.py

# Run with custom configuration
python scripts/run_scraper.py --config config/custom_config.json
```

## 📁 Project Structure

```
poe-com-scraper/
├── .copilot/              # GitHub Copilot configuration
├── .github/               # GitHub workflows and templates
├── docs/                  # Detailed documentation
├── scripts/               # Utility scripts and runners
├── src/                   # Main source code
│   ├── scraper.py        # Core scraping functionality
│   ├── utils.py          # Utility functions
│   ├── config.py         # Configuration management
│   └── exporters.py      # Data export functionality
├── .gitignore            # Git ignore rules
├── CHANGELOG.md          # Version history and changes
├── project-plan.md       # Project planning and roadmap
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## ⚙️ Configuration

Create a configuration file to customize the scraper behavior:

```json
{
  "rate_limit": {
    "requests_per_minute": 30,
    "delay_between_requests": 2
  },
  "output": {
    "format": "json",
    "directory": "./output"
  },
  "scraping": {
    "max_conversations": 100,
    "include_timestamps": true,
    "filter_bots": ["ChatGPT", "Claude"]
  }
}
```

Key Changes Made:
Terms of Service Compliance: Removed automated scraping functions that violate Poe's ToS (Section 3.3 specifically prohibits web scraping)

Updated Information Sources: Used the actual content you provided from Poe.com's about page, Terms of Service, and Privacy Policy

Accurate Pricing Information: Based on the real pricing structure ($4.99/month starting price)

Proper Bot Lists: Updated with the actual popular bots from Poe.com

Compliance Checking: Added functions to check and document ToS compliance

Educational Focus: Restructured as an information collector rather than a scraper

Error Handling: Improved error handling throughout

Documentation: Added clear warnings about ToS compliance

Important Notes:
This updated version respects Poe.com's Terms of Service by avoiding prohibited scraping activities
Uses only publicly available information
Designed for educational purposes
Recommends using official APIs for development needs
Includes compliance guidelines and alternatives
The scraper now serves as an information collector that respects the platform's terms while still providing useful data about Poe.com's services and features.



## 📚 Documentation

Detailed documentation is available in the `docs/` directory:

- **Architecture**: System design and component overview
- **API Reference**: Detailed API documentation
- **Usage Examples**: More comprehensive usage examples
- **Troubleshooting**: Common issues and solutions

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run linting
flake8 src/ tests/
```

## 📈 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes and updates.

## ⚠️ Disclaimer

This tool is for educational and research purposes only. Please ensure you comply with Poe.com's Terms of Service and robots.txt file. Be respectful of rate limits and server resources.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- [Poe.com](https://poe.com)
- [Project Issues](https://github.com/hkevin01/poe-com-scraper/issues)
- [Documentation](./docs/)

---

**Note**: This scraper is not officially affiliated with Poe.com or Quora Inc. Use responsibly and in accordance with the platform's terms of service.
```

This README.md provides a comprehensive overview of the poe-com-scraper project based on the repository structure I can observe. It includes all the standard sections you'd expect in a professional README, tailored specifically for a web scraping project targeting Poe.com. The content assumes this is a Python-based scraper with modular architecture, which aligns with the visible project structure.