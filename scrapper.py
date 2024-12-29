import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

# -------------------------- Helper / Common Code --------------------------

def is_within_last_5_years(date_obj):
    five_years_ago = datetime.now() - timedelta(days=5*365)
    return date_obj >= five_years_ago

def categorize_press_release(title, body=""):
    t_lower = title.lower()
    if any(word in t_lower for word in ["approval", "approve", "authorized", "fda"]):
        return "Regulatory Approval"
    elif any(word in t_lower for word in ["clinical trial", "phase", "study"]):
        return "Clinical Trial Update"
    elif any(word in t_lower for word in ["financial", "dividend", "finance", "earnings", "q1", "q2"]):
        return "Financial News"
    elif any(word in t_lower for word in ["appoint", "ceo", "executive", "board of directors"]):
        return "Management Update"
    elif any(word in t_lower for word in ["launch", "commercial"]):
        return "Commercialized Drug Update"
    else:
        return "Other"

def extract_categories(text_div):
    """
    This was originally for Pfizer's <ul class="filter-list__list"> categories.
    For Merck or other sites, it likely won't apply, but we'll keep it in the code.
    """
    categories = []
    cat_list = text_div.find("ul", class_="filter-list__list")
    if not cat_list:
        return categories
    cat_items = cat_list.find_all("li")
    for cat in cat_items:
        cat_a = cat.find("a", class_="tag")
        if cat_a:
            cat_text = cat_a.get_text(strip=True)
            categories.append(cat_text)
    return categories

# -------------------------- Pfizer Scraper --------------------------

def scrape_pfizer_press_page(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve page: {url}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    press_data = []
    result_lists = soup.find_all("ul", class_="result-list")

    for rlist in result_lists:
        releases = rlist.find_all("li", class_="grid-x")
        for item in releases:
            date_div = item.find("div", class_="cell small-12 medium-12 lmedium-2")
            if not date_div:
                continue
            date_tag = date_div.find("p", class_="date")
            if not date_tag:
                continue

            raw_date = date_tag.get_text(strip=True)  # e.g. "12.19.2024"
            try:
                date_obj = datetime.strptime(raw_date, "%m.%d.%Y")
            except ValueError:
                continue

            # Filter out older than 5 years
            if not is_within_last_5_years(date_obj):
                continue

            text_div = item.find("div", class_="cell small-12 medium-12 lmedium-10")
            if not text_div:
                continue

            title_h5 = text_div.find("h5")
            if not title_h5:
                continue
            link_a = title_h5.find("a")
            if not link_a:
                continue

            title = link_a.get_text(strip=True)
            link = link_a.get("href")
            
            # Attempt to find any categories
            cats = extract_categories(text_div)
            category = categorize_press_release(title)

            press_data.append({
                "Date": date_obj.strftime("%Y-%m-%d"),
                "Company": "Pfizer",
                "Title": title,
                "URL": "https://www.pfizer.com" + link,
                "Tags": ", ".join(cats),
                "Category": category
            })
    return press_data

def scrape_pfizer():
    """
    Example function that scrapes multiple pages from Pfizer's site.
    """
    all_press = []
    base_url = ("https://www.pfizer.com/newsroom/press-releases"
                "?field_tags_target_id%5B22256%5D=22256&page=")

    for page_num in range(0, 10):  # Adjust how many pages you want
        url = base_url + str(page_num)
        page_results = scrape_pfizer_press_page(url)
        if not page_results:
            break
        all_press.extend(page_results)

    return all_press

# -------------------------- Merck Scraper using Selenium --------------------------

def scrape_merck_selenium():
    """
    Use Selenium to load Merck's press release page, wait for the content to render,
    then parse the final DOM with BeautifulSoup.
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    import time

    url = "https://www.merck.com/media/news/"

    # Configure Selenium for headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")         # Run in headless mode
    chrome_options.add_argument("--no-sandbox")       
    chrome_options.add_argument("--disable-dev-shm-usage")

    # You need to have "chromedriver" installed & on your PATH
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    # Wait a bit for JS to load. Could be replaced with an explicit wait or condition
    time.sleep(5)

    # Now get the final rendered HTML
    page_html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(page_html, "html.parser")
    press_data = []

    # Based on the actual HTML for Merck's "News releases" 
    # the dynamic block might appear within <div class="d8-results-container">
    # or <div class="d8-search-container">, etc.

    # We can attempt to find them. Right now, the site shows them in JavaScript calls,
    # so let's attempt a hypothetical parse:

    # Hypothetical example: maybe the rendered DOM places each release in something like:
    # <div class="d8-results-item"> or similar. Let's just guess "d8-results-container"
    results_div = soup.find("div", class_="d8-results-container")
    if not results_div:
        print("Merck: Could not find any 'd8-results-container' in the page.")
        return press_data

    # We might see each item in <div class="some-article-class"> or so. 
    # Let's search for repeated patterns. For demonstration, let's see if we find <h3>:
    article_divs = results_div.find_all("div", class_="some-article-class")  # <--- hypothetical
    # The code below is just a placeholder. In reality, you'd look carefully at
    # the final Selenium-rendered HTML and adapt your selectors accordingly.

    for article in article_divs:
        # Example attempt to find date
        date_span = article.find("span", class_="release-date")
        if not date_span:
            continue
        raw_date = date_span.get_text(strip=True)  # e.g. "December 20, 2024"
        try:
            date_obj = datetime.strptime(raw_date, "%B %d, %Y")
        except ValueError:
            # fallback date parse attempts, or skip
            continue
        if not is_within_last_5_years(date_obj):
            continue

        title_tag = article.find("h3")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)

        # link
        link_tag = title_tag.find("a")
        if not link_tag:
            continue
        link = link_tag.get("href", "").strip()
        if link.startswith("/"):
            link = "https://www.merck.com" + link

        # Use our categorizer
        category = categorize_press_release(title)

        # Tag or body might be extracted from something else
        # placeholder:
        tags_text = ""

        press_data.append({
            "Date": date_obj.strftime("%Y-%m-%d"),
            "Company": "Merck",
            "Title": title,
            "URL": link,
            "Tags": tags_text,
            "Category": category
        })

    return press_data


# -------------------------- Main --------------------------

def main():
    # Pfizer
    pfizer_data = scrape_pfizer()

    # Merck with Selenium
    merck_data = scrape_merck_selenium()

    # Combine
    combined_df = pd.DataFrame(pfizer_data + merck_data)
    # Sort descending
    combined_df.sort_values("Date", ascending=False, inplace=True)

    # Save to Excel
    combined_df.to_excel("combined_press_releases.xlsx", index=False)

    print(f"Scraped {len(pfizer_data)} Pfizer press releases.")
    print(f"Scraped {len(merck_data)} Merck press releases.")
    print("Saved combined_press_releases.xlsx")


if __name__ == "__main__":
    main()

