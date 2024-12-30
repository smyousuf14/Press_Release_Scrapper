# Press Release Scraper

This repository contains a Python-based scraper that **collects and categorizes** press releases from two major pharmaceutical websites:

- **Pfizer** (using direct HTTP requests and [BeautifulSoup](https://pypi.org/project/beautifulsoup4/))
- **Merck** (using [Selenium](https://pypi.org/project/selenium/) to handle JavaScript rendering, then BeautifulSoup for parsing)

Each press release (title, date, URL, etc.) is categorized into one of several “high-level” buckets:

- Regulatory Approval  
- Clinical Trial Update  
- Commercialized Drug Update  
- Financial News  
- Management Update  
- Other  

Finally, the scraper consolidates all entries and stores them in a single Excel file called **`combined_press_releases.xlsx`**.

---

## Table of Contents

1. [Why Categorize Press Releases?](#why-categorize-press-releases)
2. [Project Structure](#project-structure)
3. [Installation & Setup](#installation--setup)
4. [Usage](#usage)
5. [Notes & Troubleshooting](#notes--troubleshooting)
6. [License](#license)

---

## Why Categorize Press Releases?

Pharmaceutical companies release numerous announcements—like new trial data, pipeline updates, and corporate leadership changes—on a regular basis. Manually sifting through all of this can be time-consuming. By sorting them into broader “general categories,” it becomes easier to quickly identify the nature of each press release (e.g., **Financial News** vs. **Regulatory Approval**).


