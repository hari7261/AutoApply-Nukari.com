# 🚀 Naukri AutoApply - Smart Job Application Bot

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Selenium](https://img.shields.io/badge/Selenium-4.0+-orange.svg)](https://selenium.dev)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An intelligent automation tool that applies to recent job postings on Naukri.com based on your preferences, saving hours of manual work.

**Why I Built This:** After applying to 100+ jobs manually during my own job search, I created this solution to handle the repetitive tasks while I focused on interview preparation.

## 🌟 Features

- **Smart Filtering** - Applies only to jobs matching your exact criteria
- **Fresh Listings** - Prioritizes postings from last 24 hours
- **Human-like Interaction** - Mimics real user behavior
- **Secure Login** - Uses Google OAuth authentication
- **Configurable** - Easy setup via config file
- **Error Resilient** - Multiple recovery mechanisms

## ⚙️ Tech Stack

- Python 3.8+
- Selenium WebDriver
- ChromeDriver
- ConfigParser

## 📦 Installation

### Prerequisites
- Google Chrome installed
- Python 3.8+

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/naukri-autoapply.git
   cd naukri-autoapply
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Download ChromeDriver matching your Chrome version from [here](https://chromedriver.chromium.org/downloads) and place it in project root

## 🛠 Configuration

1. Edit `config.ini`:
   ```ini
   [NAUKRI]
   email = your@email.com
   
   [JOB_SEARCH]
   keywords = Python,Java
   locations = Bangalore,Remote
   experience = 3-6
   salary = 5-10
   
   [DEFAULT]
   headless = False  # Set True to run in background
   chrome_driver_path = chromedriver.exe  # Path if not in root
   ```

## 🚀 Usage

Run the automation:
```bash
python main.py
```

The bot will:
1. Open Naukri.com and login via Google
2. Search jobs matching your criteria
3. Apply to relevant positions automatically

**Note:** You'll need to manually enter your Google password when prompted for security reasons.

## 🛡️ Safety Features

- Built-in delays between actions
- Multiple element detection strategies
- Session recovery mechanisms
- Smart error handling

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

## ⚠️ Disclaimer

Use at your own risk. This is for educational purposes only. Respect Naukri.com's Terms of Service.

## 📜 License

[MIT](LICENSE)
```

---

### Additional Files to Include:

1. **requirements.txt**
```text
selenium>=4.0.0
configparser
```

2. **.gitignore**
```text
*.ini
*.log
/chromedriver*
/venv/
__pycache__/
```

3. **Sample config.ini**
```ini
[NAUKRI]
email = your@email.com

[JOB_SEARCH]
keywords = Python,Java
locations = Bangalore,Remote
experience = 3-6
salary = 5-10

[DEFAULT]
headless = False
chrome_driver_path = chromedriver.exe
```
---
