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


---

## Why Categorize Press Releases?

Pharmaceutical companies release numerous announcements—like new trial data, pipeline updates, and corporate leadership changes—on a regular basis. Manually sifting through all of this can be time-consuming. By sorting them into broader “general categories,” it becomes easier to quickly identify the nature of each press release (e.g., **Financial News** vs. **Regulatory Approval**).

## Project Structure
- **`scrapper.py`**  
  - **`scrape_pfizer()`**: Pulls Pfizer press releases using `requests` + BeautifulSoup.  
  - **`scrape_merck()`**: Uses Selenium to load Merck’s JS-driven page, then extracts press releases with BeautifulSoup.  
  - **`categorize_press_release()`**: Assigns each release to a high-level category (Regulatory Approval, Financial News, etc.) based on text-matching.  
  - Combines all results into one DataFrame and writes them to **`combined_press_releases.xlsx`**.

- **`requirements.txt`**  
  - Python dependencies such as `requests`, `selenium`, `beautifulsoup4`, `pandas`.

- **`README.md`**  
  - Explains project usage and structure.

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/press-release-scraper.git
2. **Install Python packages:**
   ```bash
   pip install -r requirements.txt
3. **Set up Selenium (for Merck scraping):**
   -Download a WebDriver (e.g., ChromeDriver or GeckoDriver).
   -Update any driver paths in scrapper.py if needed.

## Usage
1. **Run the scraper**:
2. **Check the output:**
