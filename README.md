# Poe.com Scraper

A Python-based tool to collect and analyze publicly available data from Poe.com, an AI chatbot platform featuring models like ChatGPT, Claude, and more.

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
This tool interacts with Poe.com's public interface to collect information about available bots, features, and policies. It is designed for modularity, extensibility, and educational use.

## ✨ Features
- Multi-bot support: Collect info on various AI models
- Rate limiting: Respects server resources
- Error handling: Robust and informative
- Data export: JSON, CSV formats
- Configurable: Easy to adjust via config files
- Logging: Detailed logs for debugging and monitoring
- Compliance: Avoids prohibited scraping, focuses on public info

## 🚀 Installation
### Prerequisites
- Python 3.7 or higher
- pip package manager

### Setup
```bash
git clone https://github.com/hkevin01/poe-com-scraper.git
cd poe-com-scraper
pip install -r requirements.txt
```

## 🎯 Usage
### Basic Usage
```python
from src.scraper import PoeScraper
scraper = PoeScraper()
results = scraper.scrape_conversations()
scraper.export_data(results, format='json')
```
### CLI Usage
```bash
python scripts/run_scraper.py
python scripts/run_scraper.py --config config/custom_config.json
```

## 📁 Project Structure
```
poe-com-scraper/
├── .copilot/              # Copilot config
├── .github/               # Workflows & templates
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── src/                   # Source code
│   ├── scraper.py         # Core scraping logic
│   ├── utils.py           # Utilities
│   ├── config.py          # Config management
│   └── exporters.py       # Data export
├── .gitignore             # Ignore rules
├── CHANGELOG.md           # Changelog
├── project-plan.md        # Roadmap
├── requirements.txt       # Dependencies
└── README.md              # This file
```

## ⚙️ Configuration
Create a config file to customize behavior:
```json
{
  "rate_limit": {"requests_per_minute": 30, "delay_between_requests": 2},
  "output": {"format": "json", "directory": "./output"},
  "scraping": {"max_conversations": 100, "include_timestamps": true, "filter_bots": ["ChatGPT", "Claude"]}
}
```

## 📚 Documentation
See the `docs/` directory for:
- Architecture
- API Reference
- Usage Examples
- Troubleshooting

## 🤝 Contributing
1. Fork the repo
2. Create a feature branch
3. Commit changes
4. Push to your branch
5. Open a Pull Request

### Development Setup
```bash
pip install -r requirements-dev.txt
python -m pytest tests/
flake8 src/ tests/
```

## 📈 Changelog
See [CHANGELOG.md](CHANGELOG.md) for history.

## ⚠️ Disclaimer
This tool is for educational and research purposes only. It does not violate Poe.com's Terms of Service and only collects public information. Please respect rate limits and server resources.

## 📄 License
MIT License - see LICENSE for details.

## 🔗 Links
- [Poe.com](https://poe.com)
- [Project Issues](https://github.com/hkevin01/poe-com-scraper/issues)
- [Documentation](./docs/)

---
**Note**: This project is not affiliated with Poe.com or Quora Inc. Use responsibly and in accordance with the platform's terms of service.